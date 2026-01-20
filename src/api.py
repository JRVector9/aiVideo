"""
FastAPI Server for Quote Video Generation
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import uvicorn

from quote_video.pipeline import QuoteVideoPipeline, Scene
from quote_video.config import OUTPUT_DIR

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

@app.on_event("startup")
async def startup_event():
    global pipeline
    print("[API] Initializing pipeline...")
    pipeline = QuoteVideoPipeline()
    print("[API] Pipeline ready!")

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

class VideoRequest(BaseModel):
    scenes: List[SceneInput]
    output_name: Optional[str] = "generated_video"
    clean_temp: Optional[bool] = True

@app.post("/api/create-video")
async def create_video(request: VideoRequest):
    """
    명언 영상 생성

    Request Body:
    {
        "scenes": [
            {
                "narration": "인생은 고통이다.",
                "image_prompt": "A wise philosopher contemplating life"
            }
        ],
        "output_name": "my_video",
        "clean_temp": true
    }
    """
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")

    try:
        # Scene 객체로 변환
        scenes = [
            Scene(narration=s.narration, image_prompt=s.image_prompt)
            for s in request.scenes
        ]

        # 영상 생성
        result_path = pipeline.create_video(
            scenes=scenes,
            output_name=request.output_name,
            clean_temp=request.clean_temp
        )

        return {
            "status": "success",
            "video_path": str(result_path),
            "filename": result_path.name,
            "scenes_count": len(scenes)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")

@app.get("/api/videos")
async def list_videos():
    """생성된 영상 목록"""
    OUTPUT_DIR.mkdir(exist_ok=True)
    videos = list(OUTPUT_DIR.glob("*.mp4"))

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
