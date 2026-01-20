# Quote Video Agent

명언 영상 자동 생성 오케스트레이터 에이전트

## Role

명언 영상 제작 파이프라인을 총괄하며, 4개의 스킬을 순차적으로 호출하여 최종 영상을 생성합니다.

## Skills Used

1. **generate-image**: FLUX로 배경 이미지 생성
2. **generate-tts**: Gemini TTS로 나레이션 생성
3. **generate-subtitle**: Whisper로 자막 생성
4. **compose-video**: FFmpeg로 영상 합성

## Workflow

```
Input: scenes 데이터 (narration + image_prompt 리스트)
  ↓
For each scene:
  1. generate-image → 배경 이미지
  2. generate-tts → 나레이션 음성
  3. generate-subtitle → SRT 자막
  4. compose-video → 씬 영상
  ↓
compose-video (final) → 최종 영상 + BGM
  ↓
Output: MP4 영상 파일
```

## Input Format

```python
scenes = [
    {
        "narration": "인생은 고통이다.",
        "image_prompt": "A wise philosopher contemplating life"
    },
    {
        "narration": "그러나 우리는 이 고통을 받아들이고 초월해야 한다.",
        "image_prompt": "A person meditating peacefully"
    }
]
```

## Output

```
output/
├── {project_name}.mp4        # 최종 영상
└── temp/
    ├── scene_001_image.png
    ├── scene_001_audio.wav
    ├── scene_001_subtitle.srt
    ├── scene_001_video.mp4
    └── ... (각 씬별 파일들)
```

## Error Handling

- **이미지 생성 실패**: 재시도 (최대 3회)
- **TTS 실패**: API 키 확인 안내
- **Whisper 실패**: 오디오 파일 검증
- **FFmpeg 실패**: 의존성 설치 확인

## Usage Example

```bash
# 에이전트 호출
python -m src.quote_video.pipeline

# 또는 커맨드 사용
/createvideo
```

## Dependencies

- ComfyUI 서버 실행 중
- Gemini API 키 설정
- FFmpeg 설치
- Python 3.10+

## Performance

- **1분 영상 (3-4 씬)**: 약 5-10분
- **10분 영상 (30-40 씬)**: 약 30-60분
- 병렬 처리 미지원 (순차 처리)

## Configuration

모든 설정은 `src/quote_video/config.py`에서 관리됩니다.
