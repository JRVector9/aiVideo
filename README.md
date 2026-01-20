# 🎬 Quote Video System

ComfyUI FLUX + ElevenLabs 기반 오디오북 영상 자동 생성 시스템

![License](https://img.shields.io/badge/License-MIT-green.svg)
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FLUX](https://img.shields.io/badge/FLUX-Schnell-purple.svg)
![ElevenLabs](https://img.shields.io/badge/ElevenLabs-TTS-orange.svg)

---

## ✨ Features

| 기능 | 설명 | 기술 스택 |
|------|------|----------|
| 🎨 **이미지 생성** | Notion 스타일 미니멀 일러스트 | FLUX Schnell (ComfyUI) |
| 🎙️ **TTS 나레이션** | 고품질 한국어 음성 생성 | ElevenLabs multilingual-v2 |
| 📝 **자막 동기화** | 정확한 타임스탬프 자막 | Whisper large-v3 |
| 🎬 **영상 합성** | 전문가급 영상 제작 | FFmpeg |

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone <repository-url>
cd quote-video-prompt

# 가상환경 생성
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 편집
COMFYUI_URL=https://comfyui.jrai.space
ELEVENLABS_API_KEY=your_api_key_here
```

**API 키 발급**:
- ElevenLabs: https://elevenlabs.io/app/settings/api-keys
- 무료: 10,000 글자/월

### 3. 테스트 실행

```bash
# 이미지 생성 테스트
python test_flux_image.py

# TTS 테스트
python -m src.quote_video.tts_generator

# 자막 테스트
python test_subtitle.py
```

---

## 📋 Requirements

### 필수 요구사항

- **Python**: 3.10 이상
- **FFmpeg**: 영상 합성용
  ```bash
  # macOS
  brew install ffmpeg

  # Ubuntu/Debian
  sudo apt install ffmpeg
  ```

### API 요구사항

- **ComfyUI 서버**: https://comfyui.jrai.space (FLUX Schnell 모델)
- **ElevenLabs API**: 무료 10,000 글자/월

### 디스크 공간

- Whisper 모델: ~3GB (첫 실행 시 자동 다운로드)
- 출력 영상: 씬당 ~10-50MB

---

## 🏗️ Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Scenes    │────▶│   FLUX      │────▶│ ElevenLabs  │────▶│  Whisper    │
│   (Input)   │     │   Image     │     │    TTS      │     │  Subtitle   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                          │                   │                    │
                          ▼                   ▼                    ▼
                    ┌─────────────────────────────────────────────────┐
                    │              FFmpeg Video Composer              │
                    │    • 이미지 + 오디오 + 자막 합성                 │
                    │    • Fade In/Out 효과                          │
                    │    • BGM 믹싱                                   │
                    └─────────────────────────────────────────────────┘
                                          │
                                          ▼
                                   ┌─────────────┐
                                   │ Final MP4   │
                                   │ (1920x1080) │
                                   └─────────────┘
```

---

## 📂 Project Structure

```
quote-video-prompt/
├── src/quote_video/              # Python 모듈
│   ├── config.py                 # 설정
│   ├── flux_image_generator.py   # FLUX 이미지 생성
│   ├── tts_generator.py          # ElevenLabs TTS
│   ├── subtitle_sync.py          # Whisper 자막
│   ├── video_composer.py         # FFmpeg 합성
│   └── pipeline.py               # 전체 파이프라인
│
├── .claude/                      # Claude Code 스킬/에이전트
│   ├── skills/                   # 4개 스킬
│   ├── agents/                   # 2개 에이전트
│   └── commands/                 # 커맨드
│
├── assets/
│   ├── font/                     # 자막 폰트
│   └── bgm/                      # 배경음악
│
├── output/                       # 최종 영상
├── temp/                         # 임시 파일
└── tests/                        # 테스트 스크립트
```

---

## 🎯 Usage

### Python API

```python
from src.quote_video.pipeline import QuoteVideoPipeline, Scene

# 파이프라인 초기화
pipeline = QuoteVideoPipeline()

# 씬 데이터
scenes = [
    Scene(
        narration="인생은 고통이다.",
        image_prompt="A wise philosopher contemplating life, pencil sketch"
    ),
    Scene(
        narration="그러나 우리는 이 고통을 받아들이고 초월해야 한다.",
        image_prompt="A person meditating peacefully, minimalist illustration"
    )
]

# 영상 생성
pipeline.create_video(
    scenes=scenes,
    output_name="my_quote_video",
    bgm_path=None  # 선택: BGM 파일 경로
)
```

### Claude Code 커맨드

```bash
/createvideo
```

---

## ⚙️ Configuration

### FLUX 이미지 설정

```python
# src/quote_video/config.py

IMAGE_WIDTH = 1920
IMAGE_HEIGHT = 1080
IMAGE_STEPS = 4              # FLUX Schnell: 4-8 steps
IMAGE_CFG_SCALE = 1.0        # FLUX uses CFG 1.0
IMAGE_SAMPLER = "euler"
IMAGE_SCHEDULER = "simple"
```

### ElevenLabs 음성 설정

```python
# 음성 ID (config.py에서 변경 가능)
ELEVENLABS_VOICE_ID = "pNInz6obpgDQGcFmaJgB"  # Adam (영어)

# 한국어 지원 모델
ELEVENLABS_MODEL = "eleven_multilingual_v2"

# 음성 품질 조정
ELEVENLABS_VOICE_STABILITY = 0.5      # 0-1: 낮을수록 다양한 표현
ELEVENLABS_VOICE_SIMILARITY = 0.75    # 0-1: 높을수록 원본 음색 유지
```

### 영상 설정

```python
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
VIDEO_FPS = 30
VIDEO_FADE_DURATION = 0.5    # 초

BGM_VOLUME = 0.15            # 15%

SUBTITLE_FONT = "KOTRA_SONGEULSSI"
SUBTITLE_FONT_SIZE = 48
```

---

## 🧪 Testing

모든 테스트 스크립트는 `tests/` 폴더에 있습니다.

### 개별 모듈 테스트

```bash
# ComfyUI 연결 확인
python tests/test_comfyui.py

# FLUX 모델 확인
python tests/find_flux.py

# FLUX 이미지 생성
python tests/test_flux_image.py

# ElevenLabs TTS
python -m src.quote_video.tts_generator

# Whisper 자막
python tests/test_subtitle.py
```

### 전체 파이프라인 테스트

```bash
python -m src.quote_video.pipeline
```

자세한 테스트 가이드는 `tests/README.md`를 참고하세요.

---

## 📊 Performance

| 작업 | 예상 시간 | 비고 |
|------|----------|------|
| 이미지 생성 | 15-30초 | FLUX Schnell (4 steps) |
| TTS 생성 | 3-5초 | ElevenLabs API |
| 자막 생성 | 5-10초 | Whisper large-v3 |
| 영상 합성 | 10-15초 | 1분 영상 기준 |
| **총 1씬** | **~45초** | |
| **총 10씬 영상** | **~8분** | 순차 처리 |

---

## 💰 Cost Estimation

### ElevenLabs (TTS)

- **무료**: 10,000 글자/월
- **씬당 평균**: 50-100 글자
- **월 제작 가능**: 100-200 씬 (10-20개 영상)

### ComfyUI (이미지)

- **사용**: 무료 (자체 서버 사용 시)
- **API**: 서버 설정에 따름

---

## 🎨 Style Customization

### 이미지 스타일

```python
# config.py에서 수정
IMAGE_STYLE_PROMPT = """
Minimalist Notion-style illustration, pencil sketch aesthetic,
vintage paper background, thick black outlines, clean composition,
philosophical and artistic mood, hand-drawn feel
"""
```

### 음성 스타일

다른 음성으로 변경:
```python
# Rachel (여성, 차분)
ELEVENLABS_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"

# Domi (여성, 강인)
ELEVENLABS_VOICE_ID = "AZnzlk1XvdvUeBnXmlld"

# Bella (여성, 부드러움)
ELEVENLABS_VOICE_ID = "EXAVITQu4vr4xnSDxMaL"
```

---

## 🔧 Troubleshooting

### ComfyUI 연결 실패

```bash
# 서버 상태 확인
curl https://comfyui.jrai.space/

# 모델 확인
python find_flux.py
```

### ElevenLabs API 오류

```bash
# API 키 확인
cat .env | grep ELEVENLABS

# 무료 사용량 확인
# https://elevenlabs.io/app/usage
```

### Whisper 메모리 부족

```python
# config.py에서 더 작은 모델 사용
WHISPER_MODEL = "medium"  # 또는 "small", "base"
```

---

## 📝 License

MIT License

---

## 🤝 Contributing

이슈와 PR을 환영합니다!

---

## 📚 Resources

- [FLUX Documentation](https://github.com/black-forest-labs/flux)
- [ElevenLabs API Docs](https://elevenlabs.io/docs)
- [Whisper Documentation](https://github.com/openai/whisper)
- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)

---

## ✅ Tested Environment

- macOS 14.x (Apple Silicon)
- Python 3.14
- FLUX Schnell (ComfyUI)
- ElevenLabs API v2.31.0
- Whisper large-v3
- FFmpeg 6.x
