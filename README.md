# 🎬 오디오북 영상 시스템 프롬프트 가이드

Claude Code로 **에이전트 + 스킬 기반 오디오북 영상 시스템**을 처음부터 만드는 프롬프트 모음입니다.

![Claude Code](https://img.shields.io/badge/Claude_Code-Agent_&_Skill-blueviolet.svg)
![Gemini](https://img.shields.io/badge/Gemini_3.0-Required-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## ⚠️ 필수 요구사항

> **🔴 Gemini 3.0 API Key가 반드시 필요합니다!**  
> [Google AI Studio](https://aistudio.google.com/)에서 API Key를 발급받으세요.

---

## 📋 이 프롬프트로 만들 수 있는 것

| 기능 | 설명 | 사용 모델 |
|------|------|----------|
| 🎨 이미지 생성 | Notion 스타일 미니멀 일러스트 | Gemini 3 Pro |
| 🎙️ TTS 나레이션 | 저음의 진지한 음성 생성 | Gemini TTS Pro |
| 📝 자막 동기화 | Whisper로 정확한 타임스탬프 추출 | Whisper large-v3 |
| 🎬 영상 합성 | FFmpeg로 전문가급 영상 제작 | FFmpeg |

---

## 🚀 사용법

### 1. Claude Code에서 `prompt.md` 열기

### 2. 원하는 단계의 프롬프트 복사 & 실행

- **0단계**: Claude Code 스킬/에이전트 구조 이해
- **1단계**: 아키텍처 설계
- **2단계**: Python 모듈 생성
- **3단계**: 스킬 정의
- **4단계**: 에이전트 정의
- **5단계**: 커맨드 정의
- **6단계**: 테스트 실행

### 3. 또는 "전체 원샷 프롬프트"로 한 번에 생성

---

## 🏗️ 생성되는 아키텍처

```
project/
├── .claude/
│   ├── skills/                    # Claude Code 스킬
│   │   ├── generate-image/SKILL.md
│   │   ├── generate-tts/SKILL.md
│   │   ├── generate-subtitle/SKILL.md
│   │   └── compose-video/SKILL.md
│   ├── agents/                    # 에이전트
│   │   ├── quote-video-agent.md
│   │   └── quote-writer-agent.md
│   └── commands/
│       └── create-quote-video.md
├── src/quote_video/               # Python 모듈
│   ├── config.py
│   ├── image_generator.py
│   ├── tts_generator.py
│   ├── subtitle_sync.py
│   ├── video_composer.py
│   └── pipeline.py
└── assets/
    ├── font/
    └── bgm/
```

---

## 🎨 파이프라인 플로우

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Scenes    │────▶│   Gemini    │────▶│   Gemini    │────▶│  Whisper    │
│   (Input)   │     │   Image     │     │    TTS      │     │  Timestamp  │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                          │                   │                    │
                          ▼                   ▼                    ▼
                    ┌─────────────────────────────────────────────────┐
                    │              FFmpeg Video Composer               │
                    │    • 이미지 + 오디오 + 자막 합성                  │
                    │    • Fade In/Out 효과                           │
                    │    • BGM 믹싱                                    │
                    └─────────────────────────────────────────────────┘
                                          │
                                          ▼
                                   ┌─────────────┐
                                   │ Final MP4   │
                                   │ (1920x1080) │
                                   └─────────────┘
```

---

## 📝 프롬프트 구성

| 프롬프트 | 설명 |
|----------|------|
| 0단계 | Claude Code 스킬/에이전트 구조 이해 |
| 1단계 | 아키텍처 설계 |
| 2단계 | Python 모듈 생성 |
| 3단계 | 스킬 정의 (SKILL.md) |
| 4단계 | 에이전트 정의 |
| 5단계 | 커맨드 정의 |
| 6단계 | 테스트 실행 |
| 원샷 | 한 번에 전체 시스템 생성 |
| 팁 | 모델 고정, 체크리스트, 디버깅 |

---

## ⚙️ 설정값 (고정)

### API 모델

| 컴포넌트 | 모델 | 비고 |
|----------|------|------|
| 이미지 | `gemini-3-pro-image-preview` | Notion 스타일 일러스트 |
| TTS | `gemini-2.5-pro-preview-tts` | Voice: Enceladus (깊은 저음) |
| Whisper | `large-v3` | 한국어 최고 성능 |

### 영상 스펙

| 항목 | 값 |
|------|-----|
| 해상도 | 1920x1080 |
| FPS | 30 |
| 페이드 | 0.5초 |
| BGM 볼륨 | 15% |
| 자막 폰트 | KOTRA_SONGEULSSI (손글씨체) |

---

## 📁 파일 목록

- `prompt.md` - 전체 프롬프트 가이드

---

## 📝 License

MIT License

---

## 🤝 Contributing

이슈와 PR 환영합니다!
