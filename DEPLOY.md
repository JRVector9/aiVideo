# Dokploy 배포 가이드

## 배포 준비

### 1. 환경 변수 설정
Dokploy 프로젝트에서 다음 환경 변수를 설정하세요:

```
COMFYUI_URL=https://comfyui.jrai.space
ELEVENLABS_API_KEY=your_api_key_here
```

### 2. GitHub 연동
- Repository: https://github.com/lollol-jr/aiVideo
- Branch: main
- Private 저장소 (Personal Access Token 필요)

### 3. 빌드 설정
- Build Type: Dockerfile
- Dockerfile Path: ./Dockerfile
- Port: 8000

### 4. 리소스 설정 (권장)
- Memory: 8GB (Whisper 모델 로딩)
- CPU: 2 cores
- Storage: 20GB

## API 엔드포인트

### 기본
- `GET /` - API 정보
- `GET /health` - 헬스 체크

### 영상 생성
- `POST /api/create-video` - 영상 생성
  ```json
  {
    "scenes": [
      {
        "narration": "인생은 고통이다.",
        "image_prompt": "A wise philosopher contemplating life"
      }
    ],
    "output_name": "my_video"
  }
  ```

### 영상 관리
- `GET /api/videos` - 생성된 영상 목록
- `GET /api/videos/{filename}` - 영상 다운로드

## 주의사항

1. **메모리**: Whisper large-v3 모델이 약 3GB 메모리 사용
2. **디스크**: 영상 파일이 누적되므로 주기적 정리 필요
3. **API 키**: ElevenLabs API 키는 반드시 환경 변수로 설정
4. **ComfyUI**: 외부 ComfyUI 서버 필요 (https://comfyui.jrai.space)

## 테스트

배포 후 다음 명령어로 테스트:

```bash
curl https://your-domain.com/health
```

## 사용 예시

```bash
curl -X POST https://your-domain.com/api/create-video \
  -H "Content-Type: application/json" \
  -d '{
    "scenes": [
      {
        "narration": "인생은 아름답다",
        "image_prompt": "Beautiful sunset over mountains"
      }
    ]
  }'
```
