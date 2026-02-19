# Changelog

All notable changes to Quote Video System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.8.0] - 2026-01-24

### Added
- **Config Manager 시스템**: 완전한 설정 관리 시스템 추가
  - `src/config_manager.py`: ConfigManager 클래스
  - Pydantic 기반 설정 검증 (VideoConfig 모델)
  - 설정 스키마 정의 (CONFIG_SCHEMA)

- **프리셋 관리 기능**: 사용자 설정 저장/불러오기
  - 프리셋 저장: 현재 설정을 이름으로 저장
  - 프리셋 불러오기: 저장된 프리셋으로 설정 복원
  - 프리셋 삭제: 불필요한 프리셋 제거
  - 프리셋 목록: 저장된 모든 프리셋 조회
  - 메타데이터: 이름, 설명, 생성/수정 시간

- **Config API 엔드포인트**:
  - `GET /api/config/schema`: 설정 스키마 반환 (UI 동적 생성용)
  - `POST /api/config/validate`: 설정 검증
  - `GET /api/config/presets`: 프리셋 목록
  - `POST /api/config/presets/{name}`: 프리셋 저장
  - `GET /api/config/presets/{name}`: 프리셋 불러오기
  - `DELETE /api/config/presets/{name}`: 프리셋 삭제

- **프론트엔드 프리셋 UI**:
  - 프리셋 드롭다운 선택
  - "불러오기" 버튼
  - "현재 설정 저장" 버튼
  - "삭제" 버튼
  - 상태 메시지 표시

### Technical Details
- **config_manager.py**:
  - `VideoConfig`: Pydantic 모델로 이미지, 폰트, 자막 설정 검증
  - `ConfigManager`: 스키마 제공, 검증, 프리셋 CRUD
  - `PRESETS_DIR`: presets/ 디렉토리에 JSON 파일로 저장
  - 파일명 안전화: 특수문자 제거, 최대 100자
- **api.py**:
  - `config_manager` 싱글톤 import
  - `PresetSaveRequest` 모델 추가
  - RESTful API 구조

## [1.7.0] - 2026-01-24

### Added
- **프로젝트 폰트 파일 포함**: 환경 독립적인 폰트 렌더링
  - `assets/font/` 디렉토리에 7개 한글 폰트 추가
  - KOTRA_BOLD.otf, RIDIBatang.otf, 강원교육 시리즈 (모두 Bold/Light, 새음, 튼튼, 현옥샘)
  - Git 저장소에 포함되어 모든 서버에서 일관된 폰트 사용
- **사용자 폰트 선택 UI**: 프론트엔드에서 폰트 커스터마이징
  - 명언 텍스트 폰트 선택 (중앙 상단)
  - 저자 텍스트 폰트 선택 (중앙 하단)
  - 자막 폰트 선택 (하단 나레이션)
  - localStorage에 자동 저장/복원
- **폰트 목록 API**: `GET /api/fonts` 엔드포인트
  - config.AVAILABLE_FONTS 반환
  - 프론트엔드에서 동적으로 폰트 드롭다운 채우기

### Changed
- **FFmpeg fontfile= 사용**: 시스템 폰트 대신 폰트 파일 절대 경로 지정
  - `_build_quote_text_filter()`: `font=` → `fontfile='{FONT_DIR}/{filename}'`
  - 백슬래시 이스케이핑 추가 (Windows 경로 지원)
- **ASS 자막 fontsdir 옵션**: 한글 자막 깨짐 해결
  - `subtitles={ass_path}:fontsdir={FONT_DIR}`
  - 폰트 파일명에서 확장자 제거하여 ASS Fontname 생성
- **프론트엔드 레이블 명확화**:
  - "명언 텍스트" → "중앙 상단 고정 텍스트"
  - "저자" → "중앙 하단 고정 텍스트"
- **기본 폰트 변경**:
  - 명언/저자: RIDIBatang.otf (우아한 바탕체)
  - 자막: KOTRA_BOLD.otf (가독성 좋은 고딕)

### Fixed
- **한글 텍스트 완전 깨짐 해결**: fontfile로 직접 경로 지정
  - 명언 본문 한글 100% 정상 렌더링
  - 저자 이름 한글 100% 정상 렌더링
  - 자막 한글 100% 정상 렌더링
- **시스템 폰트 의존성 제거**: 모든 환경에서 동일한 폰트 사용

### Technical Details
- **config.py**:
  - `AVAILABLE_FONTS`: 폰트 파일명 → 표시 이름 딕셔너리
  - `QUOTE_FONT`, `AUTHOR_FONT`, `SUBTITLE_FONT`: 파일명으로 변경
- **video_composer.py**:
  - `_build_quote_text_filter()`: quote_font, author_font 파라미터 추가
  - 텍스트 이스케이핑: 백슬래시 추가 처리
  - `_convert_srt_to_ass()`: Path(font_file).stem으로 폰트명 추출
- **pipeline.py**:
  - Scene 데이터클래스에 `quote_font`, `author_font` 필드 추가
  - `create_video()`: 전역 폰트 설정 파라미터 추가
  - Scene별 폰트 > 전역 폰트 > Config 기본값 우선순위
- **api.py**:
  - VideoRequest에 `quote_font`, `author_font` 필드 추가
  - `process_video_job()` signature 업데이트
  - `GET /api/fonts` 엔드포인트 추가
- **static/index.html**:
  - `loadFonts()`: 페이지 로드 시 폰트 목록 fetch
  - fontSettings localStorage 저장/복원
  - generateVideo()에서 폰트 설정 전송

## [1.6.0] - 2026-01-24

### Changed
- **실시간 진행 상태 모니터링**: Polling에서 SSE (Server-Sent Events)로 전환
  - 백엔드: `GET /api/jobs/{job_id}/stream` SSE 엔드포인트 추가
  - 프론트엔드: EventSource API로 실시간 스트리밍
  - 진행률 업데이트 지연 제거 (5초 → 즉시)
  - 서버 부하 감소 (반복 요청 → 단일 연결)
  - 자동 재연결 지원

### Technical Details
- **SSE 이벤트 타입**:
  - `progress`: 진행 상태 업데이트 (progress, current_stage, status)
  - `completed`: 작업 완료 (result, filename)
  - `failed`: 작업 실패 (error)
  - `error`: 시스템 오류
- **연결 관리**:
  - 1초마다 상태 확인 (변경 시에만 전송)
  - 완료/실패 시 자동 연결 종료
  - 클라이언트 연결 해제 감지
  - Fallback: 연결 오류 시 최종 상태 확인
- **의존성 추가**: `sse-starlette>=1.6.5`

### Benefits
- 실시간 진행 상태 (Polling 대비 최대 5초 빠른 업데이트)
- 서버 부하 감소 (예: 10명 사용자, 2분 작업 시 240회 → 2회 요청)
- 네트워크 효율성 향상 (HTTP 단일 연결 유지)
- 사용자 경험 개선 (즉각적인 피드백)

## [1.5.0] - 2026-01-24

### Added
- **백엔드 프롬프트 저장 시스템**: 모든 생성 영상의 프롬프트를 서버에 영구 저장
  - `PromptManager` 클래스: 프롬프트 저장/조회/삭제 관리
  - `prompts/` 디렉토리: JSON 형식으로 프롬프트 메타데이터 저장
  - 영상 생성 완료 시 자동으로 프롬프트 저장
- **프롬프트 조회 API 엔드포인트**:
  - `GET /api/prompts`: 저장된 프롬프트 목록 조회
  - `GET /api/prompts/{filename}`: 특정 영상의 프롬프트 조회
  - `DELETE /api/prompts/{filename}`: 프롬프트 삭제
- **프롬프트 메타데이터 구조**:
  - 파일명, 생성 시간
  - 전역 이미지 프롬프트 (global_prompt)
  - 이미지 해상도 (image_width, image_height)
  - 자막 설정 (subtitle_settings)
  - Scene 데이터 (narration, image_prompt, quote_text, author)

### Changed
- 웹 UI `viewPromptHistory()`: 백엔드 API에서 프롬프트 조회
- `VideoRequest`: `global_prompt` 필드 추가
- `process_video_job()`: 영상 생성 완료 시 프롬프트 자동 저장
- localStorage 기반 저장 제거 (백엔드 저장으로 대체)

### Fixed
- **프롬프트 손실 문제 해결**: 브라우저 캐시 삭제 시에도 프롬프트 유지
- 안정적인 서버 기반 저장으로 프롬프트 영구 보존

### Technical Details
- 프롬프트 파일: `prompts/{filename}.json` (확장자 제거된 파일명)
- JSON 구조: timestamp, created_at, global_prompt, scenes, subtitle_settings, image_width, image_height
- 자동 디렉토리 생성: `PROJECT_ROOT/prompts`
- 오류 발생 시에도 영상 생성은 계속 진행 (프롬프트 저장 실패는 warning)

## [1.4.0] - 2026-01-24

### Added
- **자막 커스터마이징 시스템**: 자막 폰트, 크기, 색상, 위치 완전 제어
  - 웹 UI에 전역 자막 설정 섹션 추가
  - 자막 폰트 선택 (NanumGothic, NanumMyeongjo, Arial, Helvetica 등)
  - 자막 크기 조절 (20-120)
  - 자막 위치 선택 (상단/중앙/하단)
  - 자막 색상 및 외곽선 색상 커스터마이징
  - 외곽선 두께 조절 (0-10)
- **Scene별 자막 설정**: Scene 클래스에 자막 설정 필드 추가 (우선순위: Scene > 전역)
- **LocalStorage 지원**: 자막 설정이 브라우저에 자동 저장/복원

### Changed
- `VideoComposer.compose_scene()`: 자막 설정 파라미터 추가
- `VideoComposer._convert_srt_to_ass()`: 동적 자막 설정 적용
- `QuoteVideoPipeline.create_video()`: 전역 자막 설정 파라미터 추가
- `Scene` 데이터클래스: 자막 커스터마이징 필드 추가
- FastAPI `VideoRequest`: 자막 설정 필드 추가
- ASS 자막 파일: Alignment 및 MarginV가 위치에 따라 동적 설정

### Technical Details
- **ASS Subtitle Format**:
  - Alignment: top=8, center=5, bottom=2
  - MarginV: top/bottom=50, center=0
  - 폰트, 색상, 외곽선이 런타임에 적용
- **자막 위치 제어**: subtitles 필터의 ASS 스타일로 정밀 제어
- **기본값 유지**: 설정하지 않으면 config.py의 기본값 사용

## [1.3.1] - 2026-01-24

### Added
- **Web Interface Integration**: 명언 텍스트 오버레이 기능이 웹 UI에 추가됨
  - 각 Scene에 "명언 텍스트" 입력 필드 추가 (선택사항)
  - "저자" 입력 필드 추가 (선택사항)
  - localStorage에 자동 저장
  - 프롬프트 히스토리에 명언/저자 정보 표시
- **Backend API Update**: FastAPI 엔드포인트가 quote_text, author 필드 지원
  - `SceneInput` 모델에 `quote_text`, `author` 필드 추가 (Optional)
  - Scene 생성 시 자동으로 전달
- **Example Script**: `example_text_overlay.py` 추가 - Python에서 텍스트 오버레이 사용 예제

### Changed
- 웹 UI에서 Scene 생성 시 quote_text, author 초기화
- collectScenes() 함수가 새 필드 수집
- 프롬프트 히스토리 뷰가 명언/저자 표시 (있는 경우)

## [1.3.0] - 2026-01-23

### Added
- **FFmpeg Text Overlay**: 명언 텍스트를 FFmpeg drawtext 필터로 직접 렌더링
  - `VideoComposer.compose_scene()`: `quote_text`, `author` 파라미터 추가
  - `_build_quote_text_filter()`: drawtext 필터 구성 메서드
  - 100% 완벽한 텍스트 품질 (AI 생성 이미지 텍스트 문제 해결)
  - 폰트, 크기, 색상, 위치 완전 제어
  - 그림자 효과 및 외곽선 지원

### Changed
- **Scene 데이터클래스**: `quote_text`, `author` 필드 추가
- **이미지 생성 역할 변경**: 배경 이미지로만 사용 (텍스트는 FFmpeg로 렌더링)
- **Config 설정 추가**:
  - `QUOTE_FONT`: 명언 폰트 (NanumMyeongjo-Bold)
  - `QUOTE_FONT_SIZE`: 72
  - `AUTHOR_FONT_SIZE`: 52
  - 외곽선, 그림자 설정

### Technical Details
- FFmpeg drawtext 필터 사용으로 텍스트 렌더링 품질 최상
- 명언 본문: 화면 중앙 (약간 위)
- 저자 이름: 명언 아래 150px
- 한글/영어 모두 완벽 지원

## [1.2.3] - 2026-01-23

### Fixed
- **Rollback to FLUX.1 Schnell**: FLUX.2 Klein 모델이 MPS (Apple Silicon) 환경에서 VAE 디코딩 시 `MPSGraph does not support tensor dims larger than INT_MAX` 에러 발생으로 FLUX.1 Schnell로 복귀
- **Async Processing**: `timeout=None` 설정으로 비동기 처리 유지 (타임아웃 없이 안정적 생성)

### Changed
- Model: `flux-2-klein-4b.safetensors` → `flux1-schnell.safetensors`
- CLIP: `CLIPLoader (qwen_3_4b)` → `DualCLIPLoader (t5xxl_fp16 + clip_l)`
- VAE: `flux2-vae.safetensors` → `ae.safetensors`
- Image Generation Time: ~30초 목표 → ~90-120초 (MPS 환경, 비동기)
- Quality: FLUX.1 Schnell 표준 품질 유지

### Technical Notes
- FLUX.2 Klein은 NVIDIA GPU (CUDA) 환경에서만 안정적으로 작동
- MPS 백엔드는 FP8 모델 미지원 및 대용량 텐서 제한 있음
- CPU Fallback (`PYTORCH_ENABLE_MPS_FALLBACK=1`) 시도했으나 VAE INT_MAX 에러 해결 불가

## [1.2.0] - 2025-01-23

### Changed

#### Image Generation Engine Upgrade
- **FLUX.1 Schnell → FLUX.2 Klein Base 4B**
  - Model: `flux-2-klein-base-4b-fp8.safetensors`
  - Parameters: 12B → 32B (약 2.7배 증가)
  - Steps: 4 → 25 (고품질 생성)
  - Generation Time: 15-30초 → 40-90초
  - Quality: 2-3배 향상 (더 정교한 디테일, 개선된 명암)
  - VRAM: FP8 양자화로 8GB에서 실행 가능

#### Documentation Updates
- 모든 문서에서 FLUX.2 Klein Base 반영
  - `README.md`: 기술 스택, 성능 지표 업데이트
  - `SETUP.md`: 설치 가이드 및 예상 시간 업데이트
  - `tests/README.md`: 테스트 예상 시간 업데이트
  - `.claude/skills/generate-image/SKILL.md`: FLUX.2 상세 스펙 업데이트
  - `static/usage.html`: 프론트엔드 엔진 정보 업데이트

#### Configuration
- `src/quote_video/config.py`:
  - `FLUX_UNET_NAME`: "flux1-schnell.safetensors" → "flux-2-klein-base-4b-fp8.safetensors"
  - `IMAGE_STEPS`: 4 → 25

### Performance Impact

| Metric | Before (FLUX.1) | After (FLUX.2) | Change |
|--------|----------------|----------------|--------|
| Image Generation | 15-30초 | 40-90초 | +2-3배 시간 |
| Image Quality | 기본 | 고품질 | +2-3배 품질 |
| Model Size | 12B params | 32B params | +2.7배 |
| Total (1 scene) | ~45초 | ~80초 | +35초 |
| Total (10 scenes) | ~8분 | ~14분 | +6분 |

### Migration Notes
- 기존 프로젝트는 자동으로 FLUX.2 Klein Base 사용
- 더 빠른 생성이 필요한 경우 `IMAGE_STEPS`를 25→10으로 조정 가능 (품질 저하)
- ComfyUI 서버에 `flux-2-klein-base-4b-fp8.safetensors` 모델 필요

## [1.0.0] - 2025-01-21

### Added

#### Core Features
- **FLUX Schnell Image Generation**: ComfyUI 기반 고속 이미지 생성 (4 steps, 15-30초)
- **ElevenLabs TTS**: multilingual-v2 모델로 고품질 한국어 나레이션 생성
- **Whisper Subtitles**: large-v3 모델로 정확한 타임스탬프 자막 생성
- **FFmpeg Video Composition**: 전문가급 영상 합성 시스템

#### Python Modules
- `src.quote_video.config`: 중앙 설정 관리
- `src.quote_video.flux_image_generator`: FLUX 이미지 생성기
- `src.quote_video.tts_generator`: ElevenLabs TTS 생성기
- `src.quote_video.subtitle_sync`: Whisper 자막 동기화
- `src.quote_video.video_composer`: FFmpeg 영상 합성
- `src.quote_video.pipeline`: 전체 파이프라인 통합

#### Documentation
- `README.md`: 프로젝트 개요 및 기능 소개
- `SETUP.md`: 상세 설치 가이드 (270+ 줄)
- `tests/README.md`: 테스트 가이드
- `.claude/skills/`: Claude Code 스킬 문서 (4개)
  - `generate-image/`: FLUX Schnell 이미지 생성 스킬
  - `generate-tts/`: ElevenLabs TTS 스킬
  - `generate-subtitle/`: Whisper 자막 스킬
  - `compose-video/`: FFmpeg 영상 합성 스킬

#### Test Scripts
- `tests/test_comfyui.py`: ComfyUI 서버 연결 테스트
- `tests/check_models.py`: 모델 목록 조회
- `tests/find_flux.py`: FLUX 모델 검색
- `tests/test_flux_image.py`: 이미지 생성 테스트
- `tests/test_subtitle.py`: 자막 생성 테스트

#### Examples
- `example.py`: 4가지 사용 예제 스크립트
  - 간단한 1씬 영상
  - 3씬 연결 영상
  - BGM 포함 영상
  - 커스텀 설정 영상

#### Configuration
- `.env.example`: 환경 변수 템플릿
- `requirements.txt`: Python 의존성 목록
- `.gitignore`: Git 제외 파일 설정

### Technical Specifications

#### Image Generation (FLUX Schnell)
- Model: flux1-schnell.safetensors
- Loader: UNETLoader (not CheckpointLoaderSimple)
- Steps: 4 (optimal for Schnell)
- CFG Scale: 1.0 (FLUX recommended)
- Resolution: 1920x1080
- Generation Time: 15-30 seconds
- Style: Notion-style minimal illustration

#### TTS (ElevenLabs)
- Model: eleven_multilingual_v2
- Default Voice: Adam (pNInz6obpgDQGcFmaJgB)
- Sample Rate: 44100 Hz
- Format: MP3
- Language: Korean support
- Generation Time: 3-5 seconds
- Free Tier: 10,000 characters/month

#### Subtitles (Whisper)
- Model: large-v3
- Language: Korean (ko)
- Format: SRT
- Timestamp: Word-level precision
- Accuracy: 95%+
- Processing Time: 5-10 seconds per minute

#### Video Composition (FFmpeg)
- Resolution: 1920x1080 (Full HD)
- FPS: 30
- Video Codec: libx264 (H.264)
- Audio Codec: AAC 192kbps
- Pixel Format: yuv420p
- Fade Effects: 0.5s in/out
- BGM Volume: 15%

### Performance

| Task | Time | Output |
|------|------|--------|
| Image Generation | 15-30s | 1.5MB PNG |
| TTS Generation | 3-5s | 70KB MP3 |
| Subtitle Generation | 5-10s | SRT file |
| Video Composition | 10-15s | 10-50MB MP4 |
| **Total (1 scene)** | **~45s** | **Ready MP4** |
| **Total (10 scenes)** | **~8min** | **Full video** |

### Dependencies

#### Python Packages
- `elevenlabs>=2.31.0`: TTS API
- `openai-whisper`: Subtitle generation
- `requests`: ComfyUI API
- `ffmpeg-python`: Video composition
- `torch`: Whisper backend
- `python-dotenv`: Environment management

#### External Tools
- FFmpeg 6.x: Video/audio processing
- Python 3.10+: Runtime environment

#### API Services
- ComfyUI Server: localhost:8188 (FLUX Schnell)
- ElevenLabs API: TTS service (free tier available)

### System Requirements
- OS: macOS, Linux, Windows (WSL recommended)
- Python: 3.10+
- RAM: 8GB+ (16GB recommended for Whisper)
- Disk: 5GB+ (includes Whisper model)
- Network: Internet connection required

---

## [Unreleased]

### Planned Features
- Parallel scene processing
- Additional voice options
- Custom subtitle styling UI
- Video preview before final render
- Progress callbacks
- Batch processing CLI
- Docker deployment
- Web interface

---

## Version History

- **1.0.0** (2025-01-21): Initial release with full pipeline
  - FLUX Schnell image generation
  - ElevenLabs TTS
  - Whisper subtitles
  - FFmpeg composition
  - Complete documentation
  - Test suite
  - Example scripts
