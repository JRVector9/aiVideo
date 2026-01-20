---
name: compose-video
description: FFmpeg으로 이미지, 오디오, 자막을 합성하여 전문가급 영상을 만듭니다. 씬을 영상으로 합성할 때, 페이드 효과와 BGM이 필요할 때 사용하세요.
allowed-tools:
  - Bash
  - Read
  - Write
---

# Compose Video with FFmpeg

FFmpeg을 사용하여 이미지, 오디오, 자막, BGM을 하나의 영상으로 합성하는 스킬입니다.

## Instructions

### 단일 씬 합성

1. **이미지 준비**: 1920x1080 PNG
2. **오디오 준비**: WAV 나레이션
3. **자막 준비**: SRT 파일 (선택)
4. **페이드 효과**: 자동 적용
5. **영상 출력**: MP4 (H.264)

### 최종 영상 합성

1. **씬 연결**: 여러 씬 MP4 연결
2. **BGM 믹싱**: 15% 볼륨으로 믹싱
3. **최종 출력**: 고품질 MP4

## Usage

```python
from src.quote_video.video_composer import VideoComposer

composer = VideoComposer()

# 씬 합성
scene_video = composer.compose_scene(
    image_path="output/scene_001.png",
    audio_path="output/narration_001.wav",
    output_path="output/scene_001.mp4",
    subtitle_path="output/subtitle_001.srt",
    fade_in=True,
    fade_out=True
)

# 최종 영상 합성
final_video = composer.compose_video(
    scenes=[scene1, scene2, scene3],
    output_path="output/final_video.mp4",
    bgm_path="assets/bgm/gymnopedie.mp3",
    bgm_volume=0.15
)
```

## Config

| 항목 | 값 | 설명 |
|------|-----|------|
| 해상도 | 1920x1080 | Full HD |
| FPS | 30 | 초당 프레임 |
| 코덱 | H.264 (libx264) | 호환성 최고 |
| 오디오 | AAC 192kbps | 고품질 오디오 |
| 페이드 | 0.5초 | In/Out 효과 |
| BGM 볼륨 | 15% | 나레이션 방해 없음 |

## Features

1. **자동 페이드**: 부드러운 씬 전환
2. **자막 임베딩**: 폰트, 색상, 위치 자동 설정
3. **BGM 믹싱**: 나레이션과 자연스러운 믹싱
4. **고품질 출력**: 전문가급 인코딩 설정

## Subtitle Styling

```
폰트: KOTRA_SONGEULSSI (손글씨체)
크기: 48pt
색상: White
외곽선: Black, 2px
위치: 하단 중앙
```

## Performance

- **1분 씬**: 약 10-15초 합성
- **10분 영상**: 약 2-3분 처리
- **GPU 가속**: NVIDIA/AMD 지원

## FFmpeg Requirements

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows
choco install ffmpeg
```

## Output Quality

- **비트레이트**: 자동 (해상도 기준)
- **프로필**: High (최고 호환성)
- **키프레임**: 2초 간격
- **픽셀 포맷**: yuv420p (유튜브 최적화)

## Configuration Details

```python
# src/quote_video/config.py

# 영상 설정
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
VIDEO_FPS = 30
VIDEO_FADE_DURATION = 0.5  # 초

# 자막 설정
SUBTITLE_FONT = "KOTRA_SONGEULSSI"
SUBTITLE_FONT_SIZE = 48
SUBTITLE_FONT_COLOR = "white"
SUBTITLE_OUTLINE_COLOR = "black"
SUBTITLE_OUTLINE_WIDTH = 2

# 오디오 설정
BGM_VOLUME = 0.15  # 15%
AUDIO_CODEC = "aac"
AUDIO_BITRATE = "192k"

# 비디오 코덱
VIDEO_CODEC = "libx264"
VIDEO_PRESET = "medium"  # ultrafast/fast/medium/slow/veryslow
VIDEO_CRF = 23  # 0-51, 낮을수록 고품질 (18-28 권장)
```

## FFmpeg Command Examples

### 씬 합성 명령어

```bash
ffmpeg -loop 1 -framerate 30 -i scene.png \
  -i narration.wav \
  -vf "fade=t=in:st=0:d=0.5,fade=t=out:st=3.5:d=0.5,\
       subtitles=subtitle.srt:force_style='FontName=KOTRA_SONGEULSSI,FontSize=48'" \
  -c:v libx264 -preset medium -crf 23 \
  -c:a aac -b:a 192k \
  -pix_fmt yuv420p \
  -t 4.0 \
  scene_001.mp4
```

### 씬 연결 명령어

```bash
# concat.txt 파일 생성
file 'scene_001.mp4'
file 'scene_002.mp4'
file 'scene_003.mp4'

# FFmpeg 연결
ffmpeg -f concat -safe 0 -i concat.txt \
  -c copy intermediate.mp4
```

### BGM 믹싱 명령어

```bash
ffmpeg -i intermediate.mp4 \
  -i bgm.mp3 \
  -filter_complex "[1:a]volume=0.15[bgm];[0:a][bgm]amerge=inputs=2[a]" \
  -map 0:v -map "[a]" \
  -c:v copy -c:a aac -b:a 192k \
  -shortest \
  final_video.mp4
```

## Advanced Features

### 커스텀 자막 스타일

```python
# 자막 스타일 커스터마이징
composer.compose_scene(
    # ...
    subtitle_style={
        "FontName": "Arial",
        "FontSize": 52,
        "PrimaryColour": "&H00FFFFFF",  # White
        "OutlineColour": "&H00000000",  # Black
        "Outline": 3,
        "Shadow": 2,
        "MarginV": 80  # 하단 여백
    }
)
```

### 페이드 효과 커스터마이징

```python
# 페이드 시간 조정
composer.compose_scene(
    # ...
    fade_in_duration=1.0,   # 1초 페이드인
    fade_out_duration=0.8,  # 0.8초 페이드아웃
    fade_color="black"      # 검은색 페이드
)
```

### BGM 페이드 아웃

```python
# BGM이 영상 끝에서 페이드아웃
composer.compose_video(
    # ...
    bgm_path="bgm.mp3",
    bgm_volume=0.15,
    bgm_fade_out=True,      # 마지막 3초 페이드아웃
    bgm_fade_duration=3.0
)
```

## File Size Estimates

| 영상 길이 | 예상 파일 크기 | 비고 |
|----------|---------------|------|
| 5초 씬 | 5-10MB | 1920x1080, CRF 23 |
| 30초 씬 | 15-30MB | 고정 이미지 |
| 1분 영상 | 30-60MB | 10 씬 기준 |
| 5분 영상 | 150-250MB | 자막 + BGM 포함 |

**압축 옵션**:
```python
# config.py에서 CRF 조정
VIDEO_CRF = 28  # 더 작은 파일 (품질 약간 저하)
VIDEO_CRF = 18  # 더 큰 파일 (매우 높은 품질)
```

## Troubleshooting

### FFmpeg 없음 에러

```
FileNotFoundError: ffmpeg not found
```

**해결**:
```bash
# FFmpeg 설치 확인
ffmpeg -version

# 설치 (macOS)
brew install ffmpeg

# PATH 확인
which ffmpeg
```

### 폰트 없음 경고

```
Fontconfig warning: Cannot load font KOTRA_SONGEULSSI
```

**해결**:
```bash
# 1. 폰트 다운로드
# assets/font/ 폴더에 .ttf 파일 저장

# 2. 폰트 경로 명시 (macOS/Linux)
SUBTITLE_FONT = "/Users/username/Desktop/Project/quote-video-prompt/assets/font/KOTRA_SONGEULSSI.ttf"

# 3. 또는 시스템 폰트 사용
SUBTITLE_FONT = "Arial"
```

### 자막이 안 보임

**원인**:
1. SRT 파일 인코딩 문제 (UTF-8 필요)
2. 타임스탬프 범위 초과
3. 폰트 색상이 배경과 동일

**해결**:
```python
# SRT 파일 UTF-8 확인
with open("subtitle.srt", "r", encoding="utf-8") as f:
    print(f.read())

# 자막 강제 표시 테스트
SUBTITLE_FONT_COLOR = "yellow"  # 눈에 띄는 색
SUBTITLE_OUTLINE_WIDTH = 4      # 두꺼운 외곽선
```

### 오디오 동기화 문제

**증상**: 자막이 오디오보다 빠르거나 느림

**해결**:
```python
# subtitle_sync.py에서 오프셋 조정
def generate_srt(self, audio_path, output_path, offset=0.0):
    # offset: 초 단위 (양수=자막 지연, 음수=자막 앞당김)
    # ...
```

### 영상이 너무 큼

**해결**:
```python
# config.py
VIDEO_CRF = 28           # 23 → 28 (파일 크기 ~40% 감소)
VIDEO_PRESET = "fast"    # medium → fast (약간 더 큰 파일)

# 또는 해상도 조정
VIDEO_WIDTH = 1280       # 1920 → 1280
VIDEO_HEIGHT = 720       # 1080 → 720 (HD)
```

### GPU 가속 사용

**NVIDIA GPU**:
```bash
# config.py
VIDEO_CODEC = "h264_nvenc"  # libx264 → h264_nvenc

# 약 3-5배 빠른 인코딩
```

**macOS (Apple Silicon)**:
```bash
# config.py
VIDEO_CODEC = "h264_videotoolbox"  # libx264 → h264_videotoolbox

# M1/M2 칩 하드웨어 가속
```

### 오디오가 잘림

**원인**: 이미지 길이 < 오디오 길이

**해결**:
```python
# video_composer.py
# 자동으로 오디오 길이에 맞춤
duration = max(audio_duration, min_duration)
```

## Platform Compatibility

### 유튜브

✅ **최적 설정** (이미 적용됨):
- H.264 (libx264)
- AAC 오디오
- yuv420p 픽셀 포맷
- 1920x1080 해상도

### 인스타그램

**추가 설정 필요**:
```python
VIDEO_WIDTH = 1080   # 정사각형
VIDEO_HEIGHT = 1080
VIDEO_FPS = 30
```

### TikTok

**추가 설정 필요**:
```python
VIDEO_WIDTH = 1080   # 세로 영상
VIDEO_HEIGHT = 1920
VIDEO_FPS = 30
```

## Example: Batch Composition

```python
from pathlib import Path
from src.quote_video.video_composer import VideoComposer

composer = VideoComposer()

# 여러 씬 일괄 처리
scenes = []
for i in range(1, 11):  # 10개 씬
    scene_mp4 = composer.compose_scene(
        image_path=f"output/scene_{i:03d}.png",
        audio_path=f"output/narration_{i:03d}.wav",
        subtitle_path=f"output/subtitle_{i:03d}.srt",
        output_path=f"temp/scene_{i:03d}.mp4"
    )
    scenes.append(scene_mp4)
    print(f"✅ Scene {i}/10 composed")

# 최종 영상 합성
final = composer.compose_video(
    scenes=scenes,
    output_path="output/final_video.mp4",
    bgm_path="assets/bgm/meditation.mp3",
    bgm_volume=0.12
)

print(f"🎬 Final video: {final}")
```

## Testing

```bash
# FFmpeg 설치 확인
ffmpeg -version

# 간단한 테스트
ffmpeg -f lavfi -i testsrc=duration=5:size=1920x1080:rate=30 \
  -c:v libx264 -pix_fmt yuv420p test.mp4
```

## Resources

- **FFmpeg Documentation**: https://ffmpeg.org/documentation.html
- **H.264 Guide**: https://trac.ffmpeg.org/wiki/Encode/H.264
- **Subtitle Filters**: https://ffmpeg.org/ffmpeg-filters.html#subtitles
- **Audio Filters**: https://ffmpeg.org/ffmpeg-filters.html#audio-filters
