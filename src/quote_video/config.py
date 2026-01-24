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
# FLUX.1 Schnell - Fast and stable on MPS (Apple Silicon)
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
IMAGE_STEPS = 4  # FLUX.1 Schnell: 4-8 steps recommended (fast)
IMAGE_CFG_SCALE = 1.0  # FLUX uses CFG 1.0
IMAGE_SAMPLER = "euler"
IMAGE_SCHEDULER = "simple"
IMAGE_SEED = -1

# ===========================
# TTS Configuration (ElevenLabs)
# ===========================
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

# 다국어 음성 (multilingual-v2 모델)
ELEVENLABS_VOICE_ID = "uyVNoMrnUku1dZyVEXwD"  # 사용자 선택 음성
# 다른 음성 옵션:
# - Rachel: "21m00Tcm4TlvDq8ikWAM" (여성, 차분)
# - Domi: "AZnzlk1XvdvUeBnXmlld" (여성, 강인)
# - Bella: "EXAVITQu4vr4xnSDxMaL" (여성, 부드러움)

ELEVENLABS_MODEL = "eleven_multilingual_v2"  # 다국어 지원
ELEVENLABS_VOICE_STABILITY = 0.2  # 0-1: 낮을수록 다양한 표현
ELEVENLABS_VOICE_SIMILARITY = 0.75  # 0-1: 높을수록 원본 음색 유지
ELEVENLABS_STYLE = 0.0  # 0-1: 스타일 강도 (v2 only)
ELEVENLABS_USE_SPEAKER_BOOST = True  # 명료도 향상

TTS_SAMPLE_RATE = 44100  # ElevenLabs default
TTS_CHANNELS = 1
TTS_BIT_DEPTH = 16

# 지원 언어
SUPPORTED_LANGUAGES = {
    "ko": "한국어 (Korean)",
    "en": "영어 (English)",
    "ja": "일본어 (Japanese)",
    "zh": "중국어 (Chinese)",
    "es": "스페인어 (Spanish)",
    "fr": "프랑스어 (French)",
    "de": "독일어 (German)",
    "it": "이탈리아어 (Italian)",
    "pt": "포르투갈어 (Portuguese)",
    "pl": "폴란드어 (Polish)",
    "tr": "터키어 (Turkish)",
    "ru": "러시아어 (Russian)",
    "nl": "네덜란드어 (Dutch)",
    "cs": "체코어 (Czech)",
    "ar": "아랍어 (Arabic)",
    "hi": "힌디어 (Hindi)",
    "auto": "자동 감지 (Auto-detect)"
}

DEFAULT_LANGUAGE = "ko"  # 기본 언어

# ===========================
# DeepL Translation Configuration
# ===========================
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY", "")
DEEPL_API_URL = "https://api-free.deepl.com/v2/translate"  # Free tier endpoint
# For Pro tier use: "https://api.deepl.com/v2/translate"

# ===========================
# Whisper Configuration
# ===========================
WHISPER_MODEL = "large-v3"
WHISPER_LANGUAGE = "ko"  # 기본 언어 (None=자동 감지)

# ===========================
# Video Composition Settings
# ===========================
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
VIDEO_FPS = 30
VIDEO_FADE_DURATION = 0.5

BGM_VOLUME = 0.15

# Font Settings (폰트 설정)
# 사용 가능한 폰트 목록
AVAILABLE_FONTS = {
    "KOTRA_BOLD.otf": "KOTRA Bold",
    "RIDIBatang.otf": "리디바탕",
    "강원교육모두 Bold.otf": "강원교육모두 Bold",
    "강원교육모두 Light.otf": "강원교육모두 Light",
    "강원교육새음.otf": "강원교육새음",
    "강원교육튼튼.otf": "강원교육튼튼",
    "강원교육현옥샘.otf": "강원교육현옥샘"
}

# Subtitle Settings (자막)
SUBTITLE_FONT = "KOTRA_BOLD.otf"  # 기본 자막 폰트
SUBTITLE_FONT_SIZE = 48
SUBTITLE_FONT_COLOR = "white"
SUBTITLE_OUTLINE_COLOR = "black"
SUBTITLE_OUTLINE_WIDTH = 2
SUBTITLE_POSITION = "bottom"

# Quote Text Overlay Settings (명언 텍스트 오버레이)
QUOTE_FONT = "RIDIBatang.otf"  # 기본 명언 폰트 (우아한 느낌)
QUOTE_FONT_SIZE = 72
QUOTE_FONT_COLOR = "white"
QUOTE_OUTLINE_COLOR = "black"
QUOTE_OUTLINE_WIDTH = 3
QUOTE_SHADOW_OFFSET = 2  # 그림자 오프셋

# Author Text Settings (저자 텍스트)
AUTHOR_FONT = "RIDIBatang.otf"  # 기본 저자 폰트
AUTHOR_FONT_SIZE = 52  # 저자 이름은 명언보다 작게
AUTHOR_OUTLINE_WIDTH = 2

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
