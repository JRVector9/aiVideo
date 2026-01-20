"""
Quote Video System Configuration
ComfyUI + FLUX 모델 기반 이미지 생성 설정
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# ===========================
# ComfyUI Configuration
# ===========================
COMFYUI_BASE_URL = os.getenv("COMFYUI_URL", "https://comfyui.jrai.space")
COMFYUI_API_ENDPOINT = f"{COMFYUI_BASE_URL}/prompt"
COMFYUI_WS_ENDPOINT = f"{COMFYUI_BASE_URL.replace('https://', 'wss://').replace('http://', 'ws://')}/ws"
COMFYUI_VIEW_ENDPOINT = f"{COMFYUI_BASE_URL}/view"
COMFYUI_HISTORY_ENDPOINT = f"{COMFYUI_BASE_URL}/history"

# FLUX 모델 설정 (UNETLoader 방식)
FLUX_UNET_NAME = "flux1-schnell.safetensors"
FLUX_CLIP_TYPE = "flux"
FLUX_WEIGHT_DTYPE = "default"

# ===========================
# Image Generation Settings
# ===========================
IMAGE_STYLE_PROMPT = """
Minimalist Notion-style illustration, pencil sketch aesthetic,
vintage paper background, thick black outlines, clean composition,
philosophical and artistic mood, hand-drawn feel
"""

IMAGE_NEGATIVE_PROMPT = """
photorealistic, 3D render, blur, noise, distortion,
cluttered, busy, complex background
"""

IMAGE_WIDTH = 1920
IMAGE_HEIGHT = 1080
IMAGE_STEPS = 4  # FLUX Schnell: 4-8 steps recommended
IMAGE_CFG_SCALE = 1.0  # FLUX uses CFG 1.0
IMAGE_SAMPLER = "euler"
IMAGE_SCHEDULER = "simple"
IMAGE_SEED = -1

# ===========================
# TTS Configuration (ElevenLabs)
# ===========================
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

# 한국어 음성 (multilingual-v2 모델)
ELEVENLABS_VOICE_ID = "uyVNoMrnUku1dZyVEXwD"  # 사용자 선택 음성
# 다른 음성 옵션:
# - Rachel: "21m00Tcm4TlvDq8ikWAM" (여성, 차분)
# - Domi: "AZnzlk1XvdvUeBnXmlld" (여성, 강인)
# - Bella: "EXAVITQu4vr4xnSDxMaL" (여성, 부드러움)

ELEVENLABS_MODEL = "eleven_multilingual_v2"  # 한국어 지원
ELEVENLABS_VOICE_STABILITY = 0.2  # 0-1: 낮을수록 다양한 표현
ELEVENLABS_VOICE_SIMILARITY = 0.75  # 0-1: 높을수록 원본 음색 유지
ELEVENLABS_STYLE = 0.0  # 0-1: 스타일 강도 (v2 only)
ELEVENLABS_USE_SPEAKER_BOOST = True  # 명료도 향상

TTS_SAMPLE_RATE = 44100  # ElevenLabs default
TTS_CHANNELS = 1
TTS_BIT_DEPTH = 16

# ===========================
# Whisper Configuration
# ===========================
WHISPER_MODEL = "large-v3"
WHISPER_LANGUAGE = "ko"

# ===========================
# Video Composition Settings
# ===========================
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
VIDEO_FPS = 30
VIDEO_FADE_DURATION = 0.5

BGM_VOLUME = 0.15

SUBTITLE_FONT = "RIDIBatang"
SUBTITLE_FONT_SIZE = 48
SUBTITLE_FONT_COLOR = "white"
SUBTITLE_OUTLINE_COLOR = "black"
SUBTITLE_OUTLINE_WIDTH = 2
SUBTITLE_POSITION = "bottom"

# ===========================
# Paths
# ===========================
PROJECT_ROOT = Path(__file__).parent.parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
FONT_DIR = ASSETS_DIR / "font"
BGM_DIR = ASSETS_DIR / "bgm"
OUTPUT_DIR = PROJECT_ROOT / "output"
TEMP_DIR = PROJECT_ROOT / "temp"

OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

# ===========================
# ComfyUI FLUX Workflow Template
# ===========================
DEFAULT_FLUX_WORKFLOW = {
    "4": {
        "inputs": {
            "unet_name": FLUX_UNET_NAME,
            "weight_dtype": FLUX_WEIGHT_DTYPE
        },
        "class_type": "UNETLoader"
    },
    "5": {
        "inputs": {
            "clip_name1": "t5xxl_fp16.safetensors",
            "clip_name2": "clip_l.safetensors",
            "type": FLUX_CLIP_TYPE
        },
        "class_type": "DualCLIPLoader"
    },
    "6": {
        "inputs": {
            "width": IMAGE_WIDTH,
            "height": IMAGE_HEIGHT,
            "batch_size": 1
        },
        "class_type": "EmptyLatentImage"
    },
    "7": {
        "inputs": {
            "text": "",
            "clip": ["5", 0]
        },
        "class_type": "CLIPTextEncode"
    },
    "10": {
        "inputs": {
            "vae_name": "ae.safetensors"
        },
        "class_type": "VAELoader"
    },
    "3": {
        "inputs": {
            "seed": IMAGE_SEED,
            "steps": IMAGE_STEPS,
            "cfg": IMAGE_CFG_SCALE,
            "sampler_name": IMAGE_SAMPLER,
            "scheduler": IMAGE_SCHEDULER,
            "denoise": 1,
            "model": ["4", 0],
            "positive": ["7", 0],
            "negative": ["7", 0],
            "latent_image": ["6", 0]
        },
        "class_type": "KSampler"
    },
    "8": {
        "inputs": {
            "samples": ["3", 0],
            "vae": ["10", 0]
        },
        "class_type": "VAEDecode"
    },
    "9": {
        "inputs": {
            "filename_prefix": "quote_video",
            "images": ["8", 0]
        },
        "class_type": "SaveImage"
    }
}
