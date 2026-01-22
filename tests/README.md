# 🧪 Tests Directory

Quote Video System의 모든 테스트 스크립트 모음

---

## 📋 테스트 파일 목록

### 1. ComfyUI 연결 테스트

**파일**: `test_comfyui.py`

ComfyUI 서버 연결 상태 및 API 엔드포인트 테스트

```bash
python tests/test_comfyui.py
```

**테스트 항목**:
- ✅ Server Status (GET /)
- ✅ System Stats (GET /system_stats)
- ✅ Prompt Endpoint (POST /prompt)
- ✅ Queue Status (GET /queue)
- ✅ Object Info (GET /object_info)

**예상 출력**:
```
✅ Server Status        PASS
✅ System Stats         PASS
✅ Prompt Endpoint      PASS
✅ Queue Status         PASS
✅ Object Info          PASS

All tests passed!
```

---

### 2. 모델 확인

**파일**: `check_models.py`

ComfyUI 서버에 설치된 모든 모델 목록 조회

```bash
python tests/check_models.py
```

**출력 예시**:
```
Available loaders:
- CheckpointLoaderSimple
- UNETLoader
- VAELoader
- CLIPLoader
...

Available models:
- flux-2-klein-base-4b-fp8.safetensors
- sdxl_base.safetensors
...
```

---

### 3. FLUX 모델 검색

**파일**: `find_flux.py`

FLUX 관련 모델을 모든 로더 타입에서 검색

```bash
python tests/find_flux.py
```

**출력 예시**:
```
🔍 Searching for FLUX models...

✅ UNETLoader
   Input: unet_name
   FLUX models found:
      🎯 flux-2-klein-base-4b-fp8.safetensors
      🎯 flux-2-klein-distilled-4b-fp8.safetensors

⚠️ CheckpointLoaderSimple
   No FLUX models found
```

**용도**: FLUX 모델이 어느 로더에서 사용 가능한지 확인

---

### 4. FLUX 이미지 생성 테스트

**파일**: `test_flux_image.py`

FLUX.2 Klein Base 모델로 실제 이미지 생성 테스트

```bash
python tests/test_flux_image.py
```

**처리 과정**:
1. ComfyUI 서버 연결
2. FLUX.2 Klein Base 워크플로우 준비
3. 이미지 생성 (약 40-90초)
4. 이미지 저장 및 자동 열기

**출력**:
- 파일: `temp/test_flux_image.png`
- 크기: ~1.5MB (1920x1080)
- 프롬프트: "A beautiful sunset over mountains..."

**예상 시간**: 40-90초 (고품질)

---

### 5. 자막 생성 테스트

**파일**: `test_subtitle.py`

Whisper large-v3로 오디오에서 SRT 자막 생성 테스트

```bash
python tests/test_subtitle.py
```

**처리 과정**:
1. 테스트 오디오 파일 로드 (temp/test_elevenlabs_tts.mp3)
2. Whisper 모델 로드 (첫 실행 시 ~3GB 다운로드)
3. 음성 인식 및 타임스탬프 추출
4. SRT 자막 파일 생성

**출력**:
- 파일: `temp/test_subtitle.srt`
- 포맷: 표준 SRT (타임스탬프 + 텍스트)

**예상 시간**: 5-10초 (모델 다운로드 제외)

**첫 실행 시**:
```
Downloading Whisper model: large-v3
Download size: ~3GB
Time: 5-10 minutes
```

---

## 🚀 전체 테스트 실행 순서

시스템 설치 후 아래 순서대로 테스트를 실행하세요:

```bash
# 1. ComfyUI 연결 확인
python tests/test_comfyui.py

# 2. FLUX 모델 확인
python tests/find_flux.py

# 3. 이미지 생성 테스트
python tests/test_flux_image.py

# 4. 자막 생성 테스트
python tests/test_subtitle.py
```

모든 테스트가 통과하면 시스템이 정상 작동합니다.

---

## 🐛 문제 해결

### ComfyUI 연결 실패

```bash
# 서버 상태 확인
curl https://comfyui.jrai.space/

# 네트워크 확인
ping comfyui.jrai.space
```

### FLUX 모델 없음

`find_flux.py` 실행 시 FLUX 모델이 없다면:
- ComfyUI 서버에 FLUX 모델 설치 필요
- 또는 다른 ComfyUI 서버 URL 사용

### Whisper 다운로드 실패

```bash
# 수동 다운로드
python -c "import whisper; whisper.load_model('large-v3')"

# 캐시 위치 확인
ls ~/.cache/whisper/
```

### 메모리 부족 (Whisper)

```python
# config.py에서 더 작은 모델 사용
WHISPER_MODEL = "medium"  # 또는 "small"
```

---

## 📊 테스트 결과 예상 시간

| 테스트 | 예상 시간 | 비고 |
|--------|----------|------|
| test_comfyui.py | 3-5초 | API 호출만 |
| check_models.py | 2-3초 | 모델 목록 조회 |
| find_flux.py | 2-3초 | 모델 검색 |
| test_flux_image.py | 40-90초 | FLUX.2 Klein Base 고품질 생성 |
| test_subtitle.py | 5-10초 | 모델 다운로드 제외 |
| **전체** | **~2분** | 모든 테스트 순차 실행 |

---

## 🔧 테스트 환경

- **Python**: 3.10+
- **ComfyUI**: comfyui.jrai.space
- **FLUX Model**: flux-2-klein-base-4b-fp8.safetensors (32B 파라미터, FP8 양자화)
- **Whisper Model**: large-v3 (~3GB)
- **네트워크**: 인터넷 연결 필요

---

## 📝 추가 정보

### TTS 테스트

TTS 테스트는 메인 모듈에서 직접 실행:

```bash
python -m src.quote_video.tts_generator
```

**출력**: `temp/test_elevenlabs_tts.mp3`

### 파이프라인 테스트

전체 파이프라인 테스트:

```bash
python -m src.quote_video.pipeline
```

**출력**: 1씬 테스트 영상 (temp/test_pipeline.mp4)

---

## ✅ 테스트 체크리스트

시스템 설치 확인용:

- [ ] ComfyUI 서버 연결 (test_comfyui.py)
- [ ] FLUX 모델 존재 확인 (find_flux.py)
- [ ] 이미지 생성 성공 (test_flux_image.py)
- [ ] Whisper 모델 다운로드 완료
- [ ] 자막 생성 성공 (test_subtitle.py)
- [ ] ElevenLabs TTS 생성 성공
- [ ] 전체 파이프라인 작동 확인

모든 체크리스트가 완료되면 Quote Video System을 프로덕션에서 사용할 준비가 된 것입니다!
