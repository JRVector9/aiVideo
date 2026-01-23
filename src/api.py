"""
FastAPI Server for Quote Video Generation
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
from datetime import datetime
import uvicorn
import asyncio
import re

from quote_video.pipeline import QuoteVideoPipeline, Scene
from quote_video.config import OUTPUT_DIR, PROJECT_ROOT
from job_manager import JobManager, JobStatus

def generate_video_filename() -> str:
    """
    자동으로 고유한 영상 파일명 생성
    형식: aiVideo_YYYYMMDD_001.mp4
    """
    today = datetime.now().strftime("%Y%m%d")
    pattern = f"aiVideo_{today}_*.mp4"

    # 오늘 날짜의 기존 파일 찾기
    existing_files = list(OUTPUT_DIR.glob(pattern))

    if not existing_files:
        # 첫 번째 파일
        return f"aiVideo_{today}_001"

    # 기존 파일에서 숫자 추출
    numbers = []
    for file in existing_files:
        match = re.search(rf"aiVideo_{today}_(\d+)\.mp4", file.name)
        if match:
            numbers.append(int(match.group(1)))

    # 가장 큰 숫자 + 1
    next_number = max(numbers) + 1 if numbers else 1

    return f"aiVideo_{today}_{next_number:03d}"

app = FastAPI(
    title="AI Video Generator",
    description="FLUX + ElevenLabs + Whisper 기반 명언 영상 자동 생성 API",
    version="1.0.0"
)

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙
STATIC_DIR = Path(__file__).parent.parent / "static"
STATIC_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# 파이프라인 초기화 (서버 시작 시 한 번만)
pipeline = None
job_manager = None

@app.on_event("startup")
async def startup_event():
    global pipeline, job_manager
    print("[API] Initializing pipeline...")
    pipeline = QuoteVideoPipeline()

    # 작업 관리자 초기화
    jobs_dir = PROJECT_ROOT / "jobs"
    job_manager = JobManager(jobs_dir)

    print("[API] Pipeline ready!")
    print(f"[API] Job manager ready! Jobs directory: {jobs_dir}")

@app.get("/", response_class=HTMLResponse)
async def root():
    """프론트엔드 UI 제공"""
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return index_path.read_text()
    return """
    <h1>AI Video Generator API</h1>
    <p>Frontend not found. API endpoints:</p>
    <ul>
        <li>GET /health - Health check</li>
        <li>POST /api/create-video - Create video</li>
        <li>GET /api/videos - List videos</li>
    </ul>
    """

@app.get("/api")
async def api_info():
    """API 정보"""
    return {
        "message": "AI Video Generator API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "create_video": "/api/create-video",
            "list_videos": "/api/videos"
        }
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "pipeline": "ready" if pipeline else "initializing"
    }

class SceneInput(BaseModel):
    narration: str
    image_prompt: str
    quote_text: Optional[str] = None  # 명언 텍스트 (화면 표시용)
    author: Optional[str] = None      # 명언 저자

class VideoRequest(BaseModel):
    scenes: List[SceneInput]
    clean_temp: Optional[bool] = True
    image_width: Optional[int] = 1920
    image_height: Optional[int] = 1080
    # 전역 자막 설정 (선택사항)
    subtitle_font: Optional[str] = None
    subtitle_font_size: Optional[int] = None
    subtitle_font_color: Optional[str] = None
    subtitle_outline_color: Optional[str] = None
    subtitle_outline_width: Optional[int] = None
    subtitle_position: Optional[str] = None

def process_video_job(
    job_id: str,
    scenes: List[Scene],
    output_name: str,
    clean_temp: bool,
    image_width: int = 1920,
    image_height: int = 1080,
    subtitle_font: Optional[str] = None,
    subtitle_font_size: Optional[int] = None,
    subtitle_font_color: Optional[str] = None,
    subtitle_outline_color: Optional[str] = None,
    subtitle_outline_width: Optional[int] = None,
    subtitle_position: Optional[str] = None
):
    """백그라운드에서 영상 생성 처리"""
    import traceback

    def update_progress(stage: str, progress: int):
        """진행 상태 업데이트 콜백"""
        job_manager.update_job(
            job_id,
            current_stage=stage,
            progress=progress
        )

    try:
        print(f"[Job {job_id}] Starting video generation...")
        print(f"[Job {job_id}] Image resolution: {image_width}x{image_height}")

        # 작업 시작
        job_manager.update_job(
            job_id,
            status=JobStatus.PROCESSING,
            started_at=datetime.utcnow().isoformat(),
            current_stage="🚀 영상 생성 시작...",
            progress=5
        )

        print(f"[Job {job_id}] Calling pipeline.create_video...")

        # 영상 생성
        result_path = pipeline.create_video(
            scenes=scenes,
            output_name=output_name,
            clean_temp=clean_temp,
            progress_callback=update_progress,
            image_width=image_width,
            image_height=image_height,
            subtitle_font=subtitle_font,
            subtitle_font_size=subtitle_font_size,
            subtitle_font_color=subtitle_font_color,
            subtitle_outline_color=subtitle_outline_color,
            subtitle_outline_width=subtitle_outline_width,
            subtitle_position=subtitle_position
        )

        print(f"[Job {job_id}] Video created successfully: {result_path}")

        # 작업 완료
        job_manager.update_job(
            job_id,
            status=JobStatus.COMPLETED,
            completed_at=datetime.utcnow().isoformat(),
            current_stage="✅ 완료",
            progress=100,
            result={
                "video_path": str(result_path),
                "filename": result_path.name
            }
        )

    except Exception as e:
        # 상세한 에러 로그
        error_trace = traceback.format_exc()
        print(f"[Job {job_id}] ERROR: {str(e)}")
        print(f"[Job {job_id}] Traceback:\n{error_trace}")

        # 작업 실패
        job_manager.update_job(
            job_id,
            status=JobStatus.FAILED,
            completed_at=datetime.utcnow().isoformat(),
            current_stage="❌ 실패",
            error=f"{str(e)}\n\nTraceback:\n{error_trace}"
        )

@app.post("/api/create-video")
async def create_video(request: VideoRequest, background_tasks: BackgroundTasks):
    """
    명언 영상 생성 (비동기)

    즉시 job_id를 반환하고 백그라운드에서 처리
    /api/jobs/{job_id} 엔드포인트로 진행 상태 확인 가능
    """
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")

    try:
        # Scene 객체로 변환
        scenes = [
            Scene(
                narration=s.narration,
                image_prompt=s.image_prompt,
                quote_text=s.quote_text,
                author=s.author
            )
            for s in request.scenes
        ]

        # 자동으로 고유한 파일명 생성
        auto_filename = generate_video_filename()
        print(f"[API] Auto-generated filename: {auto_filename}")

        # 작업 생성
        job_id = job_manager.create_job(
            scenes_count=len(scenes),
            output_name=auto_filename
        )

        # 백그라운드 작업 추가
        background_tasks.add_task(
            process_video_job,
            job_id,
            scenes,
            auto_filename,
            request.clean_temp,
            request.image_width,
            request.image_height,
            request.subtitle_font,
            request.subtitle_font_size,
            request.subtitle_font_color,
            request.subtitle_outline_color,
            request.subtitle_outline_width,
            request.subtitle_position
        )

        return {
            "status": "accepted",
            "job_id": job_id,
            "filename": f"{auto_filename}.mp4",
            "message": "영상 생성 작업이 시작되었습니다. /api/jobs/{job_id} 엔드포인트로 진행 상태를 확인하세요.",
            "scenes_count": len(scenes)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create job: {str(e)}")

@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str):
    """작업 상태 조회"""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.get("/api/jobs")
async def list_jobs(limit: int = 20):
    """작업 목록 조회"""
    jobs = job_manager.list_jobs(limit=limit)
    return {
        "count": len(jobs),
        "jobs": jobs
    }

@app.get("/api/videos")
async def list_videos():
    """생성된 영상 목록"""
    OUTPUT_DIR.mkdir(exist_ok=True)
    videos = list(OUTPUT_DIR.glob("*.mp4"))

    print(f"[API] Found {len(videos)} videos in {OUTPUT_DIR}")
    for v in videos:
        print(f"[API] - {v.name} ({v.stat().st_size} bytes, created: {v.stat().st_mtime})")

    return {
        "count": len(videos),
        "videos": [
            {
                "filename": v.name,
                "size": v.stat().st_size,
                "created": v.stat().st_mtime
            }
            for v in sorted(videos, key=lambda x: x.stat().st_mtime, reverse=True)
        ]
    }

@app.get("/api/videos/{filename}")
async def download_video(filename: str):
    """영상 다운로드"""
    video_path = OUTPUT_DIR / filename

    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video not found")

    return FileResponse(
        path=video_path,
        media_type="video/mp4",
        filename=filename
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
