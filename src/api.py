"""
FastAPI Server for Quote Video Generation
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
from pathlib import Path
from datetime import datetime
import uvicorn
import asyncio
import json
import re

from quote_video.pipeline import QuoteVideoPipeline, Scene
from quote_video.config import OUTPUT_DIR, PROJECT_ROOT, AVAILABLE_FONTS
from job_manager import JobManager, JobStatus
from prompt_manager import PromptManager
from config_manager import config_manager

def generate_video_filename() -> str:
    """
    자동으로 고유한 영상 파일명 생성
    형식: aiVideo_YYYYMMDD_HHMMSS_UUID8.mp4
    UUID 사용으로 동시 요청 시 파일명 충돌 방지
    """
    import uuid
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    return f"aiVideo_{timestamp}_{unique_id}"

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
prompt_manager = None

@app.on_event("startup")
async def startup_event():
    global pipeline, job_manager, prompt_manager
    print("[API] Initializing pipeline...")
    pipeline = QuoteVideoPipeline()

    # 작업 관리자 초기화
    jobs_dir = PROJECT_ROOT / "jobs"
    job_manager = JobManager(jobs_dir)

    # 프롬프트 관리자 초기화
    prompts_dir = PROJECT_ROOT / "prompts"
    prompt_manager = PromptManager(prompts_dir)

    print("[API] Pipeline ready!")
    print(f"[API] Job manager ready! Jobs directory: {jobs_dir}")
    print(f"[API] Prompt manager ready! Prompts directory: {prompts_dir}")

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
    language: Optional[str] = None    # 언어 코드 (ko, en, ja, zh 등)

class VideoRequest(BaseModel):
    scenes: List[SceneInput]
    clean_temp: Optional[bool] = True
    image_width: Optional[int] = 1920
    image_height: Optional[int] = 1080
    # 이미지 생성 백엔드 (선택사항)
    image_backend: Optional[str] = "comfyui"
    flux2c_api_url: Optional[str] = None
    # 전역 이미지 프롬프트 (선택사항)
    global_prompt: Optional[str] = None
    # 전역 언어 설정 (선택사항)
    global_language: Optional[str] = None
    # 전역 자막 설정 (선택사항)
    subtitle_font: Optional[str] = None
    subtitle_font_size: Optional[int] = None
    subtitle_font_color: Optional[str] = None
    subtitle_outline_color: Optional[str] = None
    subtitle_outline_width: Optional[int] = None
    subtitle_position: Optional[str] = None
    # 전역 명언/저자 텍스트 폰트 설정 (선택사항)
    quote_font: Optional[str] = None
    author_font: Optional[str] = None

def process_video_job(
    job_id: str,
    scenes: List[Scene],
    output_name: str,
    clean_temp: bool,
    image_width: int = 1920,
    image_height: int = 1080,
    global_language: Optional[str] = None,
    subtitle_font: Optional[str] = None,
    subtitle_font_size: Optional[int] = None,
    subtitle_font_color: Optional[str] = None,
    subtitle_outline_color: Optional[str] = None,
    subtitle_outline_width: Optional[int] = None,
    subtitle_position: Optional[str] = None,
    quote_font: Optional[str] = None,
    author_font: Optional[str] = None,
    # 이미지 생성 백엔드
    image_backend: str = "comfyui",
    flux2c_api_url: Optional[str] = None,
    # 프롬프트 저장용 원본 데이터
    original_scenes: Optional[List[Dict]] = None,
    global_prompt: Optional[str] = None
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
        print(f"[Job {job_id}] Image backend: {image_backend}")
        print(f"[Job {job_id}] Image resolution: {image_width}x{image_height}")

        # 작업 시작
        job_manager.update_job(
            job_id,
            status=JobStatus.PROCESSING,
            started_at=datetime.utcnow().isoformat(),
            current_stage="🚀 영상 생성 시작...",
            progress=5
        )

        # 요청별 pipeline 생성 (backend 설정 적용)
        print(f"[Job {job_id}] Creating pipeline with backend: {image_backend}")
        request_pipeline = QuoteVideoPipeline(
            image_backend=image_backend,
            flux2c_api_url=flux2c_api_url
        )

        print(f"[Job {job_id}] Calling pipeline.create_video...")

        # 영상 생성
        result_path = request_pipeline.create_video(
            scenes=scenes,
            output_name=output_name,
            clean_temp=clean_temp,
            progress_callback=update_progress,
            image_width=image_width,
            image_height=image_height,
            global_language=global_language,
            subtitle_font=subtitle_font,
            subtitle_font_size=subtitle_font_size,
            subtitle_font_color=subtitle_font_color,
            subtitle_outline_color=subtitle_outline_color,
            subtitle_outline_width=subtitle_outline_width,
            subtitle_position=subtitle_position,
            quote_font=quote_font,
            author_font=author_font
        )

        print(f"[Job {job_id}] Video created successfully: {result_path}")

        # 프롬프트 히스토리 저장
        try:
            subtitle_settings = {}
            if subtitle_font:
                subtitle_settings["font"] = subtitle_font
            if subtitle_font_size:
                subtitle_settings["font_size"] = subtitle_font_size
            if subtitle_font_color:
                subtitle_settings["font_color"] = subtitle_font_color
            if subtitle_outline_color:
                subtitle_settings["outline_color"] = subtitle_outline_color
            if subtitle_outline_width:
                subtitle_settings["outline_width"] = subtitle_outline_width
            if subtitle_position:
                subtitle_settings["position"] = subtitle_position

            prompt_manager.save_prompt(
                filename=result_path.name,
                scenes=original_scenes or [],
                global_prompt=global_prompt,
                subtitle_settings=subtitle_settings,
                image_width=image_width,
                image_height=image_height
            )
            print(f"[Job {job_id}] Prompt history saved")
        except Exception as e:
            print(f"[Job {job_id}] Warning: Failed to save prompt history: {e}")

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
        # 원본 scene 데이터를 dict로 저장 (프롬프트 히스토리용)
        original_scenes = [
            {
                "narration": s.narration,
                "image_prompt": s.image_prompt,
                "quote_text": s.quote_text,
                "author": s.author,
                "language": s.language
            }
            for s in request.scenes
        ]

        # Scene 객체로 변환 (파이프라인용)
        scenes = [
            Scene(
                narration=s.narration,
                image_prompt=s.image_prompt,
                quote_text=s.quote_text,
                author=s.author,
                language=s.language
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
            request.global_language,  # 전역 언어 설정
            request.subtitle_font,
            request.subtitle_font_size,
            request.subtitle_font_color,
            request.subtitle_outline_color,
            request.subtitle_outline_width,
            request.subtitle_position,
            request.quote_font,
            request.author_font,
            request.image_backend,  # 이미지 생성 백엔드
            request.flux2c_api_url,  # Flux2C API URL
            original_scenes,  # 프롬프트 저장용
            request.global_prompt  # 전역 프롬프트
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
    """작업 상태 조회 (Polling용)"""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.get("/api/jobs/{job_id}/stream")
async def stream_job_progress(job_id: str, request: Request):
    """
    작업 진행 상태를 실시간으로 스트리밍 (SSE)

    EventSource로 연결하면 작업 진행률을 실시간으로 받을 수 있습니다.
    """
    # 작업 존재 확인
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    async def event_generator():
        """SSE 이벤트 생성기"""
        last_progress = -1
        last_status = None

        while True:
            # 클라이언트 연결 확인
            if await request.is_disconnected():
                print(f"[SSE] Client disconnected from job {job_id}")
                break

            # 작업 상태 조회
            job = job_manager.get_job(job_id)
            if not job:
                yield {
                    "event": "error",
                    "data": json.dumps({"error": "Job not found"})
                }
                break

            # 진행률 또는 상태 변경 시에만 전송 (중복 방지)
            if job["progress"] != last_progress or job["status"] != last_status:
                yield {
                    "event": "progress",
                    "data": json.dumps({
                        "job_id": job_id,
                        "status": job["status"],
                        "progress": job["progress"],
                        "current_stage": job["current_stage"],
                        "scenes_count": job["scenes_count"]
                    })
                }

                last_progress = job["progress"]
                last_status = job["status"]

                print(f"[SSE] Sent progress update for job {job_id}: {job['progress']}% - {job['current_stage']}")

            # 완료 또는 실패 시 종료
            if job["status"] in ["completed", "failed"]:
                yield {
                    "event": job["status"],
                    "data": json.dumps({
                        "job_id": job_id,
                        "status": job["status"],
                        "result": job.get("result"),
                        "error": job.get("error")
                    })
                }
                print(f"[SSE] Job {job_id} finished with status: {job['status']}")
                break

            # 1초마다 확인 (Polling보다 훨씬 효율적)
            await asyncio.sleep(1)

    return EventSourceResponse(event_generator())

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
async def download_video(filename: str, request: Request):
    """영상 다운로드 및 스트리밍 (Range Request 지원)"""
    video_path = OUTPUT_DIR / filename

    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video not found")

    # 파일 크기 확인
    file_size = video_path.stat().st_size

    # Range 헤더 확인
    range_header = request.headers.get("range")

    if range_header:
        # Range 헤더 파싱 (예: "bytes=0-1023")
        try:
            byte_range = range_header.replace("bytes=", "").split("-")
            start = int(byte_range[0]) if byte_range[0] else 0
            end = int(byte_range[1]) if byte_range[1] else file_size - 1

            # 범위 검증
            if start >= file_size or end >= file_size or start > end:
                raise HTTPException(status_code=416, detail="Range not satisfiable")

            # 파일에서 해당 범위만 읽기
            with open(video_path, "rb") as f:
                f.seek(start)
                data = f.read(end - start + 1)

            # 206 Partial Content 응답
            from fastapi.responses import Response
            return Response(
                content=data,
                status_code=206,
                headers={
                    "Content-Range": f"bytes {start}-{end}/{file_size}",
                    "Accept-Ranges": "bytes",
                    "Content-Length": str(len(data)),
                    "Content-Type": "video/mp4",
                },
                media_type="video/mp4"
            )
        except (ValueError, IndexError) as e:
            # Range 헤더 파싱 실패 시 전체 파일 반환
            print(f"[API] Range header parse error: {e}")
            pass

    # Range 헤더가 없거나 파싱 실패 시 전체 파일 반환
    return FileResponse(
        path=video_path,
        media_type="video/mp4",
        filename=filename,
        headers={
            "Accept-Ranges": "bytes"
        }
    )

@app.get("/api/fonts")
async def list_fonts():
    """사용 가능한 폰트 목록"""
    return {
        "fonts": AVAILABLE_FONTS
    }


# ===========================
# Config Management API
# ===========================

@app.get("/api/config/schema")
async def get_config_schema():
    """
    설정 스키마 반환

    프론트엔드에서 동적으로 설정 UI를 생성하는데 사용
    """
    return config_manager.get_schema()


@app.post("/api/config/validate")
async def validate_config(config: Dict):
    """
    설정 검증

    영상 생성 전 설정 값이 유효한지 확인
    """
    return config_manager.validate(config)


class PresetSaveRequest(BaseModel):
    config: Dict
    description: Optional[str] = None


@app.get("/api/config/presets")
async def list_presets():
    """
    저장된 프리셋 목록

    사용자가 저장한 모든 프리셋의 메타데이터 반환
    """
    presets = config_manager.list_presets()
    return {
        "count": len(presets),
        "presets": presets
    }


@app.post("/api/config/presets/{name}")
async def save_preset(name: str, request: PresetSaveRequest):
    """
    프리셋 저장

    현재 설정을 지정한 이름으로 저장
    """
    result = config_manager.save_preset(
        name=name,
        config=request.config,
        description=request.description
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to save preset"))
    return result


@app.get("/api/config/presets/{name}")
async def load_preset(name: str):
    """
    프리셋 불러오기

    저장된 프리셋의 설정 값 반환
    """
    result = config_manager.load_preset(name)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result.get("error", "Preset not found"))
    return result


@app.delete("/api/config/presets/{name}")
async def delete_preset(name: str):
    """
    프리셋 삭제
    """
    result = config_manager.delete_preset(name)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result.get("error", "Preset not found"))
    return {"message": "Preset deleted successfully"}


@app.get("/api/prompts")
async def list_prompts(limit: int = 50):
    """저장된 프롬프트 히스토리 목록"""
    prompts = prompt_manager.list_prompts(limit=limit)
    return {
        "count": len(prompts),
        "prompts": prompts
    }

@app.get("/api/prompts/{filename}")
async def get_prompt(filename: str):
    """특정 영상의 프롬프트 히스토리 조회"""
    prompt = prompt_manager.get_prompt(filename)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt history not found")
    return prompt

@app.delete("/api/prompts/{filename}")
async def delete_prompt(filename: str):
    """프롬프트 히스토리 삭제"""
    success = prompt_manager.delete_prompt(filename)
    if not success:
        raise HTTPException(status_code=404, detail="Prompt history not found")
    return {"message": "Prompt history deleted successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
