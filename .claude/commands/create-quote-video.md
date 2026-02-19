# /createvideo Command

명언 영상 자동 생성 커맨드

## Usage

```bash
/createvideo
```

실행하면 quote-video-agent가 활성화되어 대화형으로 영상을 생성합니다.

## Workflow

1. **주제 확인**: 어떤 명언/철학자를 다룰지 질문
2. **씬 구성**: quote-writer-agent가 씬 데이터 생성
3. **사용자 승인**: 씬 데이터 확인 및 수정
4. **영상 생성**: quote-video-agent가 파이프라인 실행
   - 이미지 생성 (FLUX)
   - TTS 생성 (Gemini)
   - 자막 생성 (Whisper)
   - 영상 합성 (FFmpeg)
5. **결과 출력**: 최종 MP4 파일 경로 제공

## Options

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--theme` | 주제 | 대화형 입력 |
| `--count` | 씬 개수 | 10 |
| `--bgm` | BGM 파일 경로 | None |
| `--output` | 출력 파일명 | auto |
| `--no-subtitle` | 자막 생략 | False |

## Example Sessions

### Session 1: 쇼펜하우어 명언

```
User: /createvideo

Agent: 어떤 주제로 영상을 만들까요?
1. 쇼펜하우어 고통과 의지
2. 니체 초인 사상
3. 스토아 철학
4. 직접 입력

User: 1

Agent: 몇 개의 씬으로 구성할까요? (권장: 5-15개)

User: 12

Agent: 씬 데이터를 생성했습니다:
[씬 데이터 미리보기...]

계속 진행할까요? (y/n)

User: y

Agent: [진행 상황 출력]
✅ Scene 1/12 completed
✅ Scene 2/12 completed
...

최종 영상이 생성되었습니다:
📁 output/schopenhauer_quotes_2026_01_21.mp4
```

### Session 2: 커스텀 명언

```
User: /createvideo --theme "삶의 지혜" --count 8 --bgm "assets/bgm/calm_piano.mp3"

Agent: "삶의 지혜" 주제로 8개 씬을 생성합니다.
BGM: calm_piano.mp3

씬 데이터 생성 중...
[씬 데이터 출력]

User: 3번째 씬을 수정하고 싶어

Agent: 3번째 씬:
"작은 것에 감사하라"
→ Simple objects arranged beautifully

어떻게 수정할까요?

User: 이미지를 "A person writing in a gratitude journal"로 변경

Agent: 수정 완료. 영상 생성을 시작할까요?

User: yes

[생성 진행...]
```

## Pipeline Steps Detail

### 1. Image Generation (FLUX)
```
[1/4] 이미지 생성 중...
- Prompt: A wise philosopher contemplating life...
- Style: Notion minimalist sketch
- Resolution: 1920x1080
⏱️  약 15-30초
```

### 2. TTS Generation (Gemini)
```
[2/4] 나레이션 생성 중...
- Text: 인생은 고통이다.
- Voice: Enceladus (deep male)
- Format: WAV 24kHz
⏱️  약 3-5초
```

### 3. Subtitle Sync (Whisper)
```
[3/4] 자막 생성 중...
- Model: large-v3
- Language: Korean
- Format: SRT
⏱️  약 5-10초
```

### 4. Video Composition (FFmpeg)
```
[4/4] 영상 합성 중...
- Video: H.264 1920x1080 30fps
- Audio: AAC 192kbps
- Effects: Fade in/out 0.5s
⏱️  약 10-15초
```

## Output Structure

```
output/
└── {project_name}_2026_01_21.mp4

temp/ (자동 삭제)
├── scene_001_image.png
├── scene_001_audio.wav
├── scene_001_subtitle.srt
├── scene_001_video.mp4
└── ...
```

## Error Recovery

### ComfyUI 연결 실패
```
❌ ComfyUI 서버에 연결할 수 없습니다.
확인: http://localhost:8188 가 실행 중인지 확인하세요.
```

### Gemini API 키 없음
```
❌ GEMINI_API_KEY가 설정되지 않았습니다.
.env 파일에 API 키를 추가하세요:
GEMINI_API_KEY=your_key_here
```

### FFmpeg 없음
```
❌ FFmpeg이 설치되지 않았습니다.
설치: brew install ffmpeg (macOS)
```

## Performance

| 영상 길이 | 씬 개수 | 예상 시간 |
|----------|--------|----------|
| 2분 | 5 | 5-8분 |
| 5분 | 12 | 12-18분 |
| 10분 | 25 | 25-40분 |

## Tips

1. **씬 길이**: 15-25초가 이상적
2. **BGM 선택**: 차분한 클래식/앰비언트 추천
3. **프롬프트 품질**: 구체적이고 시각적인 설명 사용
4. **병렬 처리**: 현재 미지원, 순차 처리
5. **재시도**: 실패한 씬만 개별 재생성 가능

## Requirements

- Python 3.10+
- FFmpeg
- ComfyUI 서버 (localhost:8188)
- Gemini API 키
- 10GB+ 디스크 공간 (Whisper 모델)
- GPU 권장 (선택)
