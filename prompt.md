# 오디오북 영상 시스템 프롬프트 가이드

Claude Code로 에이전트 + 스킬 기반 오디오북 영상 시스템을 처음부터 만드는 프롬프트 모음

---

## 0단계: Claude Code 스킬/에이전트 구조 이해

Claude Code 공식 가이드라인에 따르면:

### 스킬 폴더 구조 (필수)
```
.claude/skills/
├── generate-image/
│   └── SKILL.md          ← 반드시 SKILL.md 파일명 사용
├── generate-tts/
│   └── SKILL.md
├── generate-subtitle/
│   └── SKILL.md
└── compose-video/
    └── SKILL.md
```

### SKILL.md 형식 (YAML Frontmatter 필수)
```markdown
---
name: skill-name
description: 스킬 설명. 언제 사용하는지 명시하세요.
allowed-tools:
  - Bash
  - Read
  - Write
---

# Skill Title

## Instructions
사용 방법 설명...

## Usage
코드 예제...
```

### 에이전트/커맨드 구조
```
.claude/
├── agents/
│   └── video-orchestrator.md
├── commands/
│   └── createvideo.md
└── settings.json
```

---

## 1단계: 아키텍처 설계

```
오디오북 영상 자동 생성 시스템을 만들거야.

파이프라인:
1. 이미지 생성 (Gemini) - 연필 스케치 스타일
2. TTS 생성 (Gemini) - 저음의 진지한 나레이션
3. Whisper 타임스탬프 추출 (large-v3)
4. SRT 자막 생성
5. FFmpeg 영상 합성 (fade-in-out 효과)

이걸 Claude Code의 에이전트와 스킬 구조로 분리해서 설계해줘.

**중요: Claude Code 공식 스킬 구조를 따라야 해:**
- 스킬: .claude/skills/{skill-name}/SKILL.md 형식
- YAML frontmatter에 name, description, allowed-tools 필수
- 에이전트: 오케스트레이터 역할

아키텍처 다이어그램과 폴더 구조를 보여줘.
```

---

## 2단계: Python 모듈 생성

```
이제 Python 모듈을 만들어줘.

src/quote_video/ 폴더 아래에:
1. config.py - 공통 설정 (API 키, 모델명, 경로, 스타일 프롬프트)
2. image_generator.py - 노션 스타일 이미지 생성
3. tts_generator.py - TTS 나레이션 생성
4. subtitle_sync.py - Whisper 타임스탬프 + SRT 생성
5. video_composer.py - FFmpeg 영상 합성
6. pipeline.py - 전체 파이프라인 조율

각 모듈은 독립적으로 테스트 가능하게 만들어줘.
```

### 세부 요구사항 (필요시 추가)

```
이미지 생성 요구사항:
- 모델: gemini-3-pro-image-preview (고정)
- 스타일: 노션 스타일 미니멀 일러스트
- 배경: 크림색/베이지
- 선: 굵은 검정 라인
```

```
TTS 요구사항:
- 모델: gemini-2.5-pro-preview-tts
- 보이스: Charon (저음, 진지함)
- 용도: 수면/명상 콘텐츠
- 출력: WAV (24000Hz, 16bit, mono)
```

```
영상 합성 요구사항:
- 해상도: 1920x1080, 30fps
- 자막: 손글씨체, 하단 배치
- BGM: 볼륨 20%로 믹싱
```

---

## 3단계: 스킬 정의 (Claude Code 공식 구조)

```
이제 .claude/skills/ 폴더에 스킬을 정의해줘.

**중요: Claude Code 공식 스킬 구조를 따라야 해!**

폴더 구조:
.claude/skills/
├── generate-image/
│   └── SKILL.md
├── generate-tts/
│   └── SKILL.md
├── generate-subtitle/
│   └── SKILL.md
└── compose-video/
    └── SKILL.md

각 SKILL.md는 반드시 YAML frontmatter로 시작해야 해:

---
name: generate-image
description: Gemini 3 Pro로 연필 스케치 스타일 이미지를 생성합니다. 명언 영상의 배경 이미지가 필요할 때, 철학적/예술적 스케치 이미지를 만들 때 사용하세요.
allowed-tools:
  - Bash
  - Read
  - Write
---

# Generate Image

## Instructions
...

## Usage
```python
from src.quote_video.image_generator import ImageGenerator
generator = ImageGenerator()
generator.generate(prompt="...", output_path=...)
```

각 스킬에 포함할 내용:
- Instructions: 사용 시점과 방법
- Usage: 코드 예제
- Config: 모델명, 설정값 표
- Features: 제공 기능 목록
```

---

## 4단계: 에이전트 정의

```
이제 .claude/agents/ 폴더에 에이전트를 정의해줘.

만들 에이전트:
1. quote-video-agent - 영상 제작 오케스트레이터
   - 스킬들을 순차 호출
   - 에러 핸들링
   - 결과 집계

2. quote-writer-agent - 콘텐츠 기획
   - 명언 선별
   - 이미지 프롬프트 작성
   - scenes 데이터 구성

각 에이전트의 역할, 사용 스킬, 입출력 형식을 명시해줘.
```

---

## 5단계: 커맨드 정의

```
/createvideo 슬래시 커맨드를 만들어줘.

.claude/commands/create-quote-video.md에:
- 사용법
- 파이프라인 흐름
- 실행 절차
- 옵션 (BGM 등)
을 정의해줘.
```

---

## 6단계: 테스트 실행

```
쇼펜하우어 명언 12개로 테스트 영상을 만들어줘.

scenes 데이터:
- narration: 한국어 명언
- image_prompt: 영어 씬 설명

배경음악은 Gymnopedie No.1을 15% 볼륨으로 넣어줘.
```

---

## 전체 원샷 프롬프트 (한 번에 다 만들기)

```
명언 영상 자동 생성 시스템을 만들어줘.

## 요구사항
1. Gemini 3 Pro로 연필 스케치 스타일 이미지 생성
2. Gemini TTS Pro로 나레이션 (Enceladus 보이스, 깊고 낮은 저음)
3. Whisper large-v3로 타임스탬프 추출 (한국어 최고 성능)
4. FFmpeg로 영상 합성 (fade-in-out, 자막)
5. BGM 믹싱 지원 (볼륨 15%)

## Claude Code 스킬 구조 (공식 가이드라인)
반드시 아래 구조를 따라야 해:

.claude/skills/
├── generate-image/
│   └── SKILL.md     ← YAML frontmatter 필수
├── generate-tts/
│   └── SKILL.md
├── generate-subtitle/
│   └── SKILL.md
└── compose-video/
    └── SKILL.md

각 SKILL.md는 이 형식을 따라:
---
name: skill-name
description: 스킬 설명 + 사용 시점
allowed-tools:
  - Bash
  - Read
  - Write
---

## 전체 구조
- Python 모듈: src/quote_video/
- 스킬: .claude/skills/{skill-name}/SKILL.md
- 에이전트: .claude/agents/video-orchestrator.md
- 커맨드: .claude/commands/createvideo.md
- 설정: .claude/settings.json

## 스타일
- 이미지: 연필 스케치, 빈티지 종이 배경
- 영상: 1920x1080, 30fps, fade-in-out 0.5초
- 자막: 손글씨체 (KOTRA_SONGEULSSI), 하단 배치
- 폰트: assets/font/KOTRA_SONGEULSSI.ttf
- BGM: assets/bgm/ 폴더의 음악

각 모듈은 독립 테스트 가능하게,
스킬/에이전트는 SKILL.md에 사용법 문서화해줘.
```

---

## 팁

### 모델 고정하기
```
이미지 생성 모델을 gemini-3-pro-image-preview로 고정해.
TTS 모델은 gemini-2.5-pro-preview-tts, 보이스는 Enceladus로 고정해.
Whisper는 large-v3 모델 사용해.
다른 모델 쓰지 마.
```

### Claude Code 스킬 구조 체크리스트
```
스킬 만들 때 이 체크리스트 확인해:
☐ .claude/skills/{skill-name}/ 폴더 생성
☐ 폴더 안에 SKILL.md 파일 생성 (파일명 정확히)
☐ YAML frontmatter에 name, description, allowed-tools 포함
☐ description에 "언제 사용하는지" 명시
☐ Instructions, Usage, Config 섹션 포함
☐ .claude/settings.json에 스킬 등록
```

### 점진적 빌드
복잡한 시스템은 한 번에 만들지 말고:
1. 먼저 Python 모듈 → 테스트
2. 스킬 폴더 구조 생성 → SKILL.md 작성
3. 에이전트 정의 → 스킬 연결
4. 커맨드 → 통합 테스트
5. settings.json 업데이트

### 디버깅
```
에러 나면 각 단계별로 출력 보여줘.
중간 파일들 삭제하지 마.
```

### SKILL.md 예제 템플릿
```markdown
---
name: my-skill
description: 이 스킬의 설명. OO할 때, XX가 필요할 때 사용하세요.
allowed-tools:
  - Bash
  - Read
  - Write
---

# My Skill

설명...

## Instructions

1. 단계 1
2. 단계 2
3. 단계 3

## Usage

\`\`\`python
from src.module import MyClass
instance = MyClass()
instance.do_something()
\`\`\`

## Config

| 항목 | 값 |
|------|-----|
| 모델 | model-name |
| 옵션 | value |

## Features

1. **feature_1**: 기능 설명
2. **feature_2**: 기능 설명
```
