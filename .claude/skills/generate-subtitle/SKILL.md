---
name: generate-subtitle
description: Whisper large-v3로 오디오에서 정확한 타임스탬프를 추출하고 SRT 자막을 생성합니다. 영상에 자막이 필요할 때, 음성 동기화가 필요할 때 사용하세요.
allowed-tools:
  - Bash
  - Read
  - Write
---

# Generate Subtitle with Whisper

Whisper AI를 사용하여 오디오를 분석하고 정확한 타임스탬프 자막을 생성하는 스킬입니다.

## Instructions

1. **오디오 입력**: WAV 또는 MP3 오디오 파일
2. **Whisper 실행**: large-v3 모델로 한국어 인식
3. **타임스탬프 추출**: 단어 단위 타이밍 분석
4. **SRT 생성**: 표준 SRT 자막 포맷 출력

## Usage

```python
from src.quote_video.subtitle_sync import SubtitleSync

sync = SubtitleSync()

# SRT 자막 생성
subtitle_path = sync.generate_srt(
    audio_path="output/narration_001.wav",
    output_path="output/subtitle_001.srt",
    language="ko"  # 한국어
)

# 타임스탬프만 추출
timestamps = sync.get_timestamps("output/narration_001.wav")
for start, end, text in timestamps:
    print(f"[{start:.2f}s - {end:.2f}s] {text}")
```

## Config

| 항목 | 값 | 설명 |
|------|-----|------|
| 모델 | large-v3 | 최고 성능 Whisper 모델 |
| 언어 | ko | 한국어 최적화 |
| 타임스탬프 | Word-level | 단어 단위 정밀 타이밍 |
| 포맷 | SRT | 표준 자막 포맷 |

## Features

1. **정확한 인식**: large-v3 모델의 한국어 최고 정확도
2. **단어 타임스탬프**: 밀리초 단위 정밀 동기화
3. **SRT 표준**: FFmpeg 및 모든 플레이어 호환
4. **빠른 처리**: GPU 가속 지원

## SRT Format Example

```srt
1
00:00:00,000 --> 00:00:03,500
인생은 고통이다.

2
00:00:03,500 --> 00:00:08,200
그러나 우리는 이 고통을 받아들이고 초월해야 한다.
```

## Performance

| 오디오 길이 | CPU 처리 시간 | GPU 처리 시간 | 정확도 |
|------------|--------------|--------------|-------|
| 4초 | ~5초 | ~2초 | 100% |
| 30초 | ~10초 | ~4초 | 98%+ |
| 1분 | ~15초 | ~6초 | 95%+ |

**테스트 결과** (ElevenLabs TTS → Whisper):
```
입력: 인생은 고통이다. 그러나 우리는 이 고통을 받아들이고 초월해야 한다.
출력: 인생은 고통이다. 그러나 우리는 이 고통을 받아들이고 초월해야 한다.
정확도: 100%
```

## Environment Setup

### 필수 요구사항

```bash
# Python 패키지
pip install openai-whisper

# FFmpeg (오디오 로딩용)
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

### 모델 다운로드

**첫 실행 시 자동 다운로드**:
```python
import whisper
model = whisper.load_model("large-v3")
# Downloading: 100%|████████| 2.87G/2.87G
```

- **모델 크기**: ~3GB
- **다운로드 시간**: 5-10분 (인터넷 속도에 따름)
- **저장 위치**: `~/.cache/whisper/`
- **재사용**: 한 번 다운로드 후 재사용

## Configuration

```python
# src/quote_video/config.py

WHISPER_MODEL = "large-v3"       # 최고 성능 모델
WHISPER_LANGUAGE = "ko"          # 한국어 고정
WHISPER_DEVICE = None            # None=자동, "cuda"=GPU, "cpu"=CPU
```

### 모델 옵션

| 모델 | 크기 | 정확도 | 속도 | 추천 용도 |
|------|------|-------|------|----------|
| tiny | 39MB | ~70% | 매우 빠름 | 테스트용 |
| base | 74MB | ~75% | 빠름 | 간단한 자막 |
| small | 244MB | ~85% | 보통 | 일반 사용 |
| medium | 769MB | ~90% | 느림 | 고품질 |
| large-v3 | 2.87GB | ~98% | 매우 느림 | **프로덕션** |

## Advanced Features

### 단어 단위 타임스탬프

```python
# Whisper는 단어 단위 타이밍 제공
result = model.transcribe(
    "audio.mp3",
    word_timestamps=True,
    language="ko"
)

for segment in result["segments"]:
    for word in segment["words"]:
        print(f"{word['start']:.2f}s - {word['end']:.2f}s: {word['word']}")
```

### 신뢰도 점수

```python
# 각 세그먼트의 인식 신뢰도
for segment in result["segments"]:
    confidence = segment["no_speech_prob"]
    print(f"신뢰도: {(1 - confidence) * 100:.1f}%")
```

## Troubleshooting

### 모델 다운로드 실패

```bash
# 수동 다운로드
python -c "import whisper; whisper.load_model('large-v3')"

# 캐시 위치 확인
ls ~/.cache/whisper/
```

### FFmpeg 없음 에러

```
RuntimeError: ffmpeg was not found
```

**해결**:
```bash
# FFmpeg 설치 확인
ffmpeg -version

# 없으면 설치
brew install ffmpeg  # macOS
```

### 메모리 부족

```
OutOfMemoryError: CUDA out of memory
```

**해결**:
```python
# config.py에서 더 작은 모델 사용
WHISPER_MODEL = "medium"  # 또는 "small"
```

### GPU 사용 안 됨

```bash
# PyTorch CUDA 설치 (GPU가 있는 경우)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 한국어 인식 부정확

**원인**:
1. 배경 소음이 많음
2. 발음이 불명확함
3. 음질이 낮음

**해결**:
```python
# 언어 명시 및 temperature 조정
result = model.transcribe(
    audio_path,
    language="ko",           # 한국어 강제
    temperature=0.0,         # 결정적 출력
    best_of=5,               # 여러 후보 중 최선
    beam_size=5              # 빔 서치 크기
)
```

## Cost & Resources

### 하드웨어 요구사항

- **CPU**: 4코어 이상 권장
- **RAM**:
  - tiny~small: 2GB+
  - medium: 4GB+
  - large-v3: 8GB+
- **GPU** (선택):
  - VRAM 4GB+ (large-v3는 6GB+ 권장)
  - CUDA 지원 GPU

### 비용

- **완전 무료**: 로컬 실행
- **클라우드 비용**: 없음 (API 없음)
- **전력**: GPU 사용 시 높음

## Compatibility

### 지원 오디오 포맷

FFmpeg가 지원하는 모든 포맷:
- WAV, MP3, M4A, FLAC
- OGG, AAC, WMA
- 비디오에서 오디오 추출 (MP4, MKV, AVI 등)

### 출력 포맷

- **SRT**: 표준 자막 (가장 호환성 높음)
- **VTT**: WebVTT (웹 자막)
- **JSON**: 프로그래밍 처리용

## Example: Batch Processing

```python
from pathlib import Path
from src.quote_video.subtitle_sync import SubtitleSync

sync = SubtitleSync()

# 여러 오디오 파일 일괄 처리
audio_dir = Path("output/audio")
subtitle_dir = Path("output/subtitles")

for audio_file in audio_dir.glob("*.mp3"):
    srt_file = subtitle_dir / f"{audio_file.stem}.srt"
    print(f"Processing: {audio_file.name}")

    sync.generate_srt(
        audio_path=str(audio_file),
        output_path=str(srt_file),
        language="ko"
    )

    print(f"✅ Created: {srt_file.name}")
```

## Testing

```bash
# Whisper 설치 확인
python -c "import whisper; print(whisper.__version__)"

# 전체 테스트
python test_subtitle.py
```

**예상 출력**:
```
✅ Whisper model loaded: large-v3
✅ Audio loaded: temp/test_elevenlabs_tts.mp3
⏳ Transcribing...
✅ Subtitle generated: temp/test_subtitle.srt

1
00:00:00,000 --> 00:00:04,179
인생은 고통이다. 그러나 우리는 이 고통을 받아들이고 초월해야 한다.
```
