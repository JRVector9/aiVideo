---
name: generate-image
description: ComfyUI FLUX.2 Klein Base 모델로 Notion 스타일 미니멀 일러스트 이미지를 생성합니다. 명언 영상의 배경 이미지가 필요할 때, 철학적/예술적 스케치 이미지를 만들 때 사용하세요.
allowed-tools:
  - Bash
  - Read
  - Write
---

# Generate Image with FLUX.2 Klein Base

ComfyUI 서버에 연결하여 FLUX.2 Klein Base 4B 모델로 고품질 이미지를 생성하는 스킬입니다.

## Instructions

1. **프롬프트 준비**: 영어로 씬 설명 작성
2. **스타일 적용**: Notion 스타일 미니멀 일러스트 자동 적용
3. **이미지 생성**: ComfyUI API를 통해 FLUX.2 Klein Base 모델 실행 (25 steps)
4. **결과 저장**: PNG 형식으로 저장

## Usage

```python
from src.quote_video.flux_image_generator import FluxImageGenerator

generator = FluxImageGenerator()

# 이미지 생성 (기본 해상도: 1920x1080)
image_path = generator.generate(
    prompt="A wise philosopher contemplating life under a tree",
    output_path="output/scene_001.png",
    seed=-1  # -1이면 랜덤
)

# 커스텀 해상도로 생성
image_path = generator.generate(
    prompt="A wise philosopher contemplating life under a tree",
    output_path="output/scene_001.png",
    width=1280,
    height=720,
    seed=-1
)

print(f"Image saved: {image_path}")
```

## Config

| 항목 | 값 | 설명 |
|------|-----|------|
| 서버 | comfyui.jrai.space | ComfyUI 서버 URL |
| 모델 | FLUX.2 Klein Base 4B | 고품질 이미지 생성 모델 (32B 파라미터) |
| 로더 | UNETLoader | FLUX 전용 로더 |
| 해상도 | 설정 가능 (기본: 1920x1080) | 커스텀 해상도 지원 |
| Steps | 25 | FLUX.2 Klein Base 권장값 (25-50) |
| CFG Scale | 1.0 | FLUX 권장값 |
| Sampler | euler | 안정적인 샘플러 |
| Scheduler | simple | 기본 스케줄러 |
| 생성 시간 | 40-90초 | 평균 60초 (고품질) |

## Features

1. **고품질 생성**: FLUX.2 Klein Base는 32B 파라미터로 정교한 고품질 이미지 생성
2. **자동 스타일**: Notion 스타일 미니멀 프롬프트 자동 추가
3. **비동기 처리**: ComfyUI 큐 시스템으로 안정적 생성
4. **에러 핸들링**: 타임아웃 및 실패 자동 처리
5. **시드 제어**: 재현 가능한 이미지 생성 지원
6. **한글 프롬프트 지원**: DeepL API를 통한 한글→영어 자동 번역
7. **해상도 설정**: 커스텀 해상도 지원 (Full HD, HD, 4K, 세로형, 정사각형 등)
8. **FP8 최적화**: 8GB VRAM에서도 실행 가능한 효율적 모델

## Example Prompts

철학적/명상적 이미지:
```
"A serene mountain landscape at dawn, minimalist pencil sketch"
"An old library with books and wisdom, vintage paper aesthetic"
"A lonely tree in vast field, philosophical mood"
"A person meditating under the moonlight, hand-drawn feel"
```

## Technical Details

### FLUX.2 Klein Base 워크플로우

```
UNETLoader (flux-2-klein-base-4b-fp8.safetensors)
    ↓
DualCLIPLoader (t5xxl + clip_l)
    ↓
CLIPTextEncode (프롬프트)
    ↓
KSampler (25 steps, CFG 1.0)
    ↓
VAEDecode (ae.safetensors)
    ↓
SaveImage (PNG)
```

### 스타일 프롬프트

자동으로 추가되는 스타일:
```
Minimalist Notion-style illustration, pencil sketch aesthetic,
vintage paper background, thick black outlines, clean composition,
philosophical and artistic mood, hand-drawn feel
```

## Environment Variables

```bash
COMFYUI_URL=https://comfyui.jrai.space
```

## Performance

- **평균 생성 시간**: 60초
- **최소**: 40초 (서버 idle 상태)
- **최대**: 90초 (서버 busy 상태)
- **품질**: FLUX.1 대비 2-3배 향상 (32B 파라미터)
- **이미지 크기**: 해상도에 따라 변동
  - 1920x1080 (Full HD): 1-2MB
  - 1280x720 (HD): 0.5-1MB
  - 3840x2160 (4K): 3-5MB
  - 1080x1920 (세로형): 1-2MB
  - 1080x1080 (정사각형): 0.7-1.2MB

## Troubleshooting

### 400 Bad Request
- 워크플로우 노드 구조 확인
- 모델명 확인: `flux-2-klein-base-4b-fp8.safetensors`

### Timeout
- 서버 상태 확인: `python test_comfyui.py`
- 타임아웃 증가: `generate(..., timeout=600)` (FLUX.2는 더 긴 시간 필요)

### 모델 없음
- FLUX.2 모델 확인: `python find_flux.py`
- UNETLoader 사용 가능 여부 확인
