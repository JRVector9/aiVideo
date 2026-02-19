# 🔧 Setup Guide

Quote Video System 설치 및 설정 가이드

---

## 📋 시작하기 전에

### 시스템 요구사항

- **OS**: macOS, Linux, Windows (WSL 권장)
- **Python**: 3.10 이상
- **디스크 공간**: 최소 5GB (Whisper 모델 포함)
- **메모리**: 최소 8GB RAM 권장

### 필요한 계정

- **ElevenLabs**: 무료 계정 (10,000 글자/월)
  - 가입: https://elevenlabs.io/
  - API 키 발급: https://elevenlabs.io/app/settings/api-keys

---

## 📥 Step 1: 프로젝트 클론

```bash
git clone <repository-url>
cd quote-video-prompt
```

---

## 🐍 Step 2: Python 가상환경 설정

### macOS / Linux

```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate

# 업그레이드 (권장)
pip install --upgrade pip
```

### Windows

```powershell
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
venv\Scripts\activate

# 업그레이드 (권장)
python -m pip install --upgrade pip
```

---

## 📦 Step 3: 의존성 설치

```bash
# requirements.txt로부터 설치
pip install -r requirements.txt
```

설치되는 주요 패키지:
- `elevenlabs` - TTS API
- `openai-whisper` - 자막 생성
- `requests` - ComfyUI API
- `ffmpeg-python` - 영상 합성
- `torch` - Whisper 백엔드

---

## 🎬 Step 4: FFmpeg 설치

### macOS (Homebrew)

```bash
brew install ffmpeg
```

### Ubuntu / Debian

```bash
sudo apt update
sudo apt install ffmpeg
```

### Windows (Chocolatey)

```powershell
choco install ffmpeg
```

### 설치 확인

```bash
ffmpeg -version
```

---

## 🔑 Step 5: API 키 설정

### 1. ElevenLabs API 키 발급

1. https://elevenlabs.io/ 회원가입
2. https://elevenlabs.io/app/settings/api-keys 접속
3. "Create API Key" 클릭
4. API 키 복사

### 2. .env 파일 생성

```bash
cp .env.example .env
```

### 3. .env 파일 편집

```bash
# .env
# Image Generation Backend (ComfyUI - 기본값)
COMFYUI_URL=http://localhost:8188

# Flux2C API (선택사항 - Mac Metal 가속 사용 시)
# FLUX2C_API_URL=https://your-ngrok-url.ngrok-free.dev
# FLUX2C_API_TIMEOUT=120

# ElevenLabs API Key
ELEVENLABS_API_KEY=your_api_key_here  # 발급받은 API 키로 교체

# DeepL API Key (선택사항 - 한글 번역 사용 시)
DEEPL_API_KEY=your_deepl_api_key_here
```

**중요**: `.env` 파일은 절대 Git에 커밋하지 마세요!

### 4. Flux2C API 설정 (선택사항)

**Flux2C API**는 Mac Metal 가속을 사용하여 더 빠른 이미지 생성을 제공합니다.

#### 사용 시나리오
- **ComfyUI (기본)**: 안정적이고 범용적인 이미지 생성
- **Flux2C API**: Mac M1/M2/M3에서 Metal 가속 활용 시 더 빠른 생성 속도 (약 36-39초)

#### 설정 방법

1. **Admin 페이지 접속**: `http://localhost:8000/static/admin.html`
2. **Image Generation Backend** 섹션에서:
   - Backend 선택: `Flux2C API (Mac Metal 가속)`
   - Flux2C API URL 입력: `https://your-ngrok-url.ngrok-free.dev`
3. **Save Settings** 클릭

**참고**: Flux2C API 서버 설정은 logo_minimal 프로젝트의 DEPLOYMENT.md를 참고하세요.

---

## 🧪 Step 6: 설치 확인

### 6.1 ComfyUI 연결 테스트

```bash
python test_comfyui.py
```

**예상 출력**:
```
✅ Server Status        PASS
✅ System Stats         PASS
✅ Prompt Endpoint      PASS
✅ Queue Status         PASS
✅ Object Info          PASS
```

### 6.2 FLUX 모델 확인

```bash
python find_flux.py
```

**예상 출력**:
```
✅ UNETLoader
   Input: unet_name
   FLUX models found:
      🎯 flux1-schnell.safetensors
```

### 6.3 FLUX 이미지 생성 테스트

```bash
python test_flux_image.py
```

**예상 결과**:
- `temp/test_flux_image.png` 생성 (~1.5MB)
- 이미지 자동으로 열림

### 6.4 ElevenLabs TTS 테스트

```bash
python -m src.quote_video.tts_generator
```

**예상 결과**:
- `temp/test_elevenlabs_tts.mp3` 생성 (~70KB)
- 음성 파일 자동으로 재생

### 6.5 Whisper 자막 테스트

```bash
python test_subtitle.py
```

**첫 실행 시**:
- Whisper large-v3 모델 다운로드 (~3GB, 5-10분 소요)
- 다운로드는 한 번만 필요

**예상 결과**:
- `temp/test_subtitle.srt` 생성
- 타임스탬프와 텍스트 표시

---

## 📂 Step 7: 에셋 준비 (선택사항)

### 자막 폰트

한국어 손글씨체 폰트 다운로드:

```bash
# 폰트 폴더 생성
mkdir -p assets/font

# 폰트 다운로드 (예: KOTRA 손글씨체)
# https://www.kotra.or.kr/kh/about/KHMISC010M.html
# 다운로드 후 assets/font/ 폴더에 저장
```

### 배경음악 (BGM)

```bash
# BGM 폴더 생성
mkdir -p assets/bgm

# 무료 음악 다운로드
# 예: Gymnopedie No.1, Clair de Lune 등
# assets/bgm/ 폴더에 MP3 파일 저장
```

---

## 🎯 Step 8: 첫 영상 만들기

### 예제 스크립트 작성

`example.py` 파일 생성:

```python
from src.quote_video.pipeline import QuoteVideoPipeline, Scene

# 파이프라인 초기화
pipeline = QuoteVideoPipeline()

# 씬 정의
scenes = [
    Scene(
        narration="인생은 고통이다.",
        image_prompt="A wise philosopher sitting under a tree, contemplating life"
    )
]

# 영상 생성
pipeline.create_video(
    scenes=scenes,
    output_name="my_first_video",
    clean_temp=False  # 디버깅용으로 임시 파일 보존
)
```

### 실행

```bash
python example.py
```

**예상 시간**: 약 20초 ~ 40초 (FLUX.1 Schnell 빠른 생성)

**출력**: `output/my_first_video.mp4`

---

## ⚙️ 고급 설정

### 이미지 품질 조정

`src/quote_video/config.py`:

```python
# FLUX.1 Schnell 설정
IMAGE_STEPS = 4        # 4-8 (빠른 생성)
IMAGE_WIDTH = 1920     # 해상도
IMAGE_HEIGHT = 1080
```

### 음성 설정

`src/quote_video/config.py`:

```python
# ElevenLabs 설정
ELEVENLABS_VOICE_ID = "pNInz6obpgDQGcFmaJgB"  # Adam
ELEVENLABS_VOICE_STABILITY = 0.5               # 0-1
ELEVENLABS_VOICE_SIMILARITY = 0.75             # 0-1
```

다른 음성으로 변경:
```python
# Rachel (여성, 차분)
ELEVENLABS_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"
```

### 자막 폰트

폰트 파일을 `assets/font/` 에 추가 후:

```python
# config.py
SUBTITLE_FONT = "YOUR_FONT_NAME"  # .ttf 제외
SUBTITLE_FONT_SIZE = 48
```

---

## 🐛 문제 해결

### ComfyUI 연결 실패

```bash
# 1. 서버 상태 확인
curl http://localhost:8188/

# 2. 네트워크 확인
ping localhost:8188

# 3. 방화벽 확인
```

### ElevenLabs API 오류

**"Invalid API Key"**:
```bash
# API 키 확인
cat .env | grep ELEVENLABS

# .env 파일이 로드되는지 확인
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('ELEVENLABS_API_KEY'))"
```

**"Quota Exceeded"**:
- https://elevenlabs.io/app/usage 에서 사용량 확인
- 10,000 글자/월 초과 시 대기 또는 업그레이드

### Whisper 다운로드 실패

```bash
# 수동 다운로드
python -c "import whisper; whisper.load_model('large-v3')"
```

### FFmpeg 오류

```bash
# FFmpeg 버전 확인
ffmpeg -version

# 재설치 (macOS)
brew reinstall ffmpeg
```

### Python 버전 오류

```bash
# Python 버전 확인
python --version

# 3.10 이상이어야 함
```

---

## 📊 성능 최적화

### GPU 가속 (Whisper)

CUDA GPU가 있는 경우:

```bash
# PyTorch with CUDA 재설치
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 더 빠른 Whisper 모델

```python
# config.py
WHISPER_MODEL = "medium"  # large-v3 대신 (약 2배 빠름)
```

### 병렬 처리 (향후 지원)

현재는 순차 처리만 지원합니다.

---

## 🔄 업데이트

```bash
# 최신 버전으로 업데이트
git pull origin main

# 의존성 재설치
pip install -r requirements.txt --upgrade
```

---

## 📞 지원

문제가 발생하면:

1. **로그 확인**: 에러 메시지 전체 복사
2. **테스트 재실행**: 개별 모듈 테스트
3. **이슈 등록**: GitHub Issues에 상세 내용 포함

---

## ✅ 설정 완료 체크리스트

- [ ] Python 3.10+ 설치
- [ ] 가상환경 생성 및 활성화
- [ ] requirements.txt 설치
- [ ] FFmpeg 설치
- [ ] ElevenLabs API 키 발급
- [ ] .env 파일 설정
- [ ] ComfyUI 연결 테스트 통과
- [ ] FLUX 이미지 생성 테스트 통과
- [ ] ElevenLabs TTS 테스트 통과
- [ ] Whisper 자막 테스트 통과
- [ ] 첫 영상 제작 성공

---

**축하합니다! 🎉 이제 Quote Video System을 사용할 준비가 되었습니다!**
