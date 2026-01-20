---
name: generate-tts
description: ElevenLabs API로 고품질 한국어 나레이션 음성을 생성합니다. 명언이나 철학적 텍스트를 음성으로 변환할 때, 오디오북 나레이션이 필요할 때 사용하세요.
allowed-tools:
  - Bash
  - Read
  - Write
---

# Generate TTS Narration with ElevenLabs

ElevenLabs API를 사용하여 전문가급 고품질 나레이션을 생성하는 스킬입니다.

## Instructions

1. **텍스트 준비**: 한국어 나레이션 텍스트 작성
2. **음성 선택**: 기본 Adam 음성 또는 다른 음성 선택
3. **TTS 생성**: ElevenLabs multilingual-v2 모델로 생성
4. **MP3 저장**: 44.1kHz, 고품질 MP3 형식

## Usage

```python
from src.quote_video.tts_generator import TTSGenerator

generator = TTSGenerator()

# TTS 생성
audio_path = generator.generate(
    text="인생은 고통이다. 그러나 우리는 이 고통을 받아들이고 초월해야 한다.",
    output_path="output/narration_001.mp3",
    voice_id=None  # 기본 음성 사용
)

print(f"Audio saved: {audio_path}")
```

## Config

| 항목 | 값 | 설명 |
|------|-----|------|
| API | ElevenLabs | 고품질 TTS API |
| 모델 | multilingual_v2 | 한국어 지원 모델 |
| 기본 음성 | Adam | 남성, 영어 (한국어도 지원) |
| 샘플레이트 | 44100 Hz | 고품질 오디오 |
| 포맷 | MP3 | 표준 오디오 포맷 |
| 생성 시간 | 3-5초 | 평균 4초 |

## Features

1. **고품질 음성**: ElevenLabs의 자연스러운 AI 음성
2. **한국어 지원**: multilingual-v2 모델로 완벽한 한국어 발음
3. **빠른 생성**: 평균 3-5초 내 음성 생성
4. **음성 커스터마이징**: Stability, Similarity, Style 조정 가능
5. **여러 음성**: 남성/여성, 다양한 톤 선택 가능

## Voice Options

### 남성 음성

```python
# Adam (기본) - 영어, 한국어 지원
ELEVENLABS_VOICE_ID = "pNInz6obpgDQGcFmaJgB"
```

### 여성 음성

```python
# Rachel - 차분하고 명료한 톤
ELEVENLABS_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"

# Domi - 강인하고 자신감 있는 톤
ELEVENLABS_VOICE_ID = "AZnzlk1XvdvUeBnXmlld"

# Bella - 부드럽고 따뜻한 톤
ELEVENLABS_VOICE_ID = "EXAVITQu4vr4xnSDxMaL"
```

### 음성 목록 조회

```python
generator = TTSGenerator()
voices = generator.list_voices()
```

## Voice Settings

### Stability (안정성)

```python
# 0.0 - 1.0 범위
ELEVENLABS_VOICE_STABILITY = 0.5

# 낮을수록: 다양한 표현, 감정적
# 높을수록: 일관된 톤, 안정적
```

### Similarity (유사성)

```python
# 0.0 - 1.0 범위
ELEVENLABS_VOICE_SIMILARITY = 0.75

# 낮을수록: 변화가 많은 음색
# 높을수록: 원본 음성 특징 유지
```

### Style (스타일 강도)

```python
# 0.0 - 1.0 범위
ELEVENLABS_STYLE = 0.0

# v2 모델에서만 지원
# 높을수록: 강한 표현력
```

### Speaker Boost (명료도 향상)

```python
ELEVENLABS_USE_SPEAKER_BOOST = True

# 음성 명료도 향상
# 오디오북/나레이션에 권장
```

## Environment Variables

```bash
# .env 파일
ELEVENLABS_API_KEY=your_api_key_here
```

**API 키 발급**:
1. https://elevenlabs.io/ 회원가입
2. https://elevenlabs.io/app/settings/api-keys 에서 발급
3. 무료: 10,000 글자/월

## Cost & Quota

### 무료 플랜

- **월 10,000 글자**
- **단일 생성 제한**: 최대 2,500 글자
- **커스텀 음성**: 최대 3개
- **제약**: 상업적 사용 불가, 크레딧 표기 필요

### 예상 사용량

```
씬당 평균 텍스트: 50-100 글자
10개 씬 영상: 약 500-1,000 글자

월 제작 가능: 10-20개 영상 (무료 플랜)
```

### 사용량 확인

https://elevenlabs.io/app/usage

## Performance

| 텍스트 길이 | 생성 시간 | 파일 크기 |
|------------|----------|----------|
| 50 글자 | ~3초 | ~30KB |
| 100 글자 | ~4초 | ~70KB |
| 200 글자 | ~5초 | ~150KB |

## Example Texts

### 철학적 명언

```python
"인생은 고통이다. 그러나 우리는 이 고통을 받아들이고 초월해야 한다."
"욕망은 끝이 없다. 만족은 욕망을 버릴 때 찾아온다."
"지혜는 고통을 통해 온다."
```

### 길이 권장사항

- **최소**: 10 글자 (너무 짧으면 부자연스러움)
- **최적**: 30-150 글자 (자연스러운 문장)
- **최대**: 2,500 글자 (API 제한)

## Troubleshooting

### Invalid API Key

```bash
# API 키 확인
cat .env | grep ELEVENLABS

# 올바른 형식인지 확인
# 32자 16진수 문자열
```

### Quota Exceeded

```
Error: You've exceeded your character quota
```

**해결**:
- 사용량 확인: https://elevenlabs.io/app/usage
- 월 초기화 대기 또는 유료 플랜 업그레이드

### Missing Permissions

```
Error: API key missing permission 'voices_read'
```

**해결**:
- 음성 목록 조회는 선택사항
- TTS 생성은 정상 작동
- API 키 재발급 시도

### Poor Quality

**한국어 발음이 부자연스러운 경우**:
1. `multilingual_v2` 모델 사용 확인
2. 문장 부호 추가 (쉼표, 마침표)
3. 다른 음성 ID 시도
4. Stability 값 조정 (0.3-0.7)

## Advanced Usage

### 감정 조절

```python
# 차분한 명상 톤
generator.generate(
    text="...",
    stability=0.7,      # 높은 안정성
    similarity=0.8      # 원본 음색 유지
)

# 감정적이고 다이나믹한 톤
generator.generate(
    text="...",
    stability=0.3,      # 낮은 안정성
    similarity=0.6      # 음색 변화 허용
)
```

### 다른 음성 사용

```python
# Rachel 음성으로 생성
generator.generate(
    text="...",
    voice_id="21m00Tcm4TlvDq8ikWAM"
)
```
