"""
FLUX Image Generator using ComfyUI API or Flux2C API
ComfyUI 서버 또는 Flux2C API를 통한 FLUX 모델 이미지 생성
"""

import json
import time
import uuid
import requests
import base64
import websocket
from pathlib import Path
from typing import Optional, Dict, Any
from .config import (
    COMFYUI_API_ENDPOINT,
    COMFYUI_WS_ENDPOINT,
    COMFYUI_VIEW_ENDPOINT,
    COMFYUI_HISTORY_ENDPOINT,
    DEFAULT_FLUX_WORKFLOW,
    IMAGE_STYLE_PROMPT,
    TEMP_DIR
)
from .translator import Translator


class FluxImageGenerator:
    """ComfyUI 또는 Flux2C API를 사용한 이미지 생성기"""

    def __init__(
        self,
        server_url: Optional[str] = None,
        backend: str = "comfyui",
        flux2c_api_url: Optional[str] = None,
        flux2c_timeout: int = 120
    ):
        """
        Args:
            server_url: ComfyUI 서버 URL (기본값: config에서 로드)
            backend: 이미지 생성 백엔드 ("comfyui" 또는 "flux2c-api")
            flux2c_api_url: Flux2C API URL (backend="flux2c-api"인 경우 필수)
            flux2c_timeout: Flux2C API 타임아웃 (초)
        """
        self.backend = backend
        self.flux2c_api_url = flux2c_api_url.rstrip("/") if flux2c_api_url else None
        self.flux2c_timeout = flux2c_timeout

        # ComfyUI 설정
        self.api_endpoint = COMFYUI_API_ENDPOINT
        self.ws_endpoint = COMFYUI_WS_ENDPOINT
        self.view_endpoint = COMFYUI_VIEW_ENDPOINT
        self.history_endpoint = COMFYUI_HISTORY_ENDPOINT
        self.translator = Translator()

        if server_url:
            self.api_endpoint = f"{server_url}/prompt"
            self.view_endpoint = f"{server_url}/view"
            self.history_endpoint = f"{server_url}/history"

    def generate(
        self,
        prompt: str,
        output_path: Path,
        style_prompt: Optional[str] = None,
        seed: int = -1,
        timeout: Optional[int] = None,
        width: int = 1920,
        height: int = 1080
    ) -> Path:
        """
        FLUX 모델로 이미지 생성

        Args:
            prompt: 이미지 생성 프롬프트 (한글/영어 모두 가능)
            output_path: 저장할 이미지 경로
            style_prompt: 스타일 프롬프트 (기본값: config의 IMAGE_STYLE_PROMPT)
            seed: 시드값 (-1이면 랜덤)
            timeout: 타임아웃 (초). None이면 무제한 대기 (비동기 모드, 기본값)
            width: 이미지 가로 해상도 (기본값: 1920)
            height: 이미지 세로 해상도 (기본값: 1080)

        Returns:
            저장된 이미지 파일 경로
        """
        # 한글 프롬프트 자동 번역
        original_prompt = prompt
        prompt = self.translator.translate_to_english(prompt)

        if original_prompt != prompt:
            print(f"[FluxImageGenerator] Original (KR): {original_prompt}")
            print(f"[FluxImageGenerator] Translated (EN): {prompt}")

        # 프롬프트 결합
        full_prompt = prompt
        if style_prompt:
            full_prompt = f"{prompt}, {style_prompt}"
        else:
            full_prompt = f"{prompt}, {IMAGE_STYLE_PROMPT}"

        print(f"[FluxImageGenerator] Generating image...")
        print(f"[FluxImageGenerator] Backend: {self.backend}")
        print(f"[FluxImageGenerator] Resolution: {width}x{height}")
        print(f"[FluxImageGenerator] Final prompt: {full_prompt[:100]}...")

        # 백엔드 선택
        image_data = None

        # Flux2C API 시도
        if self.backend == "flux2c-api":
            try:
                image_data = self._generate_flux2c_api(full_prompt, width, height, seed)
            except Exception as e:
                print(f"[FluxImageGenerator] Flux2C API failed, falling back to ComfyUI: {e}")
                self.backend = "comfyui"  # Fallback

        # ComfyUI 사용
        if self.backend == "comfyui" or image_data is None:
            # 워크플로우 준비
            workflow = self._prepare_workflow(full_prompt, seed, width, height)

            # 이미지 생성 요청
            prompt_id = self._queue_prompt(workflow)

            # 생성 완료 대기
            image_data = self._wait_for_completion(prompt_id, timeout)

        # 이미지 저장
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'wb') as f:
            f.write(image_data)

        print(f"[FluxImageGenerator] Image saved: {output_path}")
        return output_path

    def _prepare_workflow(self, prompt: str, seed: int, width: int = 1920, height: int = 1080) -> Dict[str, Any]:
        """워크플로우 준비"""
        workflow = json.loads(json.dumps(DEFAULT_FLUX_WORKFLOW))

        # 프롬프트 설정 (Node 7: CLIPTextEncode)
        workflow["7"]["inputs"]["text"] = prompt

        # 해상도 설정 (Node 6: EmptyLatentImage)
        workflow["6"]["inputs"]["width"] = width
        workflow["6"]["inputs"]["height"] = height

        # 시드 설정
        if seed != -1:
            workflow["3"]["inputs"]["seed"] = seed
        else:
            workflow["3"]["inputs"]["seed"] = int(time.time() * 1000) % (2**32)

        return workflow

    def _queue_prompt(self, workflow: Dict[str, Any]) -> str:
        """프롬프트 큐에 추가"""
        client_id = str(uuid.uuid4())

        payload = {
            "prompt": workflow,
            "client_id": client_id
        }

        response = requests.post(self.api_endpoint, json=payload)
        response.raise_for_status()

        result = response.json()
        prompt_id = result.get("prompt_id")

        if not prompt_id:
            raise RuntimeError(f"Failed to queue prompt: {result}")

        print(f"[FluxImageGenerator] Prompt queued: {prompt_id}")
        return prompt_id

    def _wait_for_completion(self, prompt_id: str, timeout: Optional[int] = None) -> bytes:
        """
        생성 완료 대기 및 이미지 다운로드 (비동기 처리)

        Args:
            prompt_id: ComfyUI 프롬프트 ID
            timeout: 타임아웃 (초). None이면 무제한 대기 (비동기 모드)
        """
        start_time = time.time()
        poll_count = 0

        while True:
            # 타임아웃 체크 (timeout이 설정된 경우에만)
            if timeout is not None and time.time() - start_time > timeout:
                raise TimeoutError(f"Image generation timed out after {timeout} seconds")

            poll_count += 1

            # 히스토리 확인
            history_url = f"{self.history_endpoint}/{prompt_id}"
            response = requests.get(history_url)

            if response.status_code == 200:
                history = response.json()

                if prompt_id in history:
                    # 에러 체크
                    status = history[prompt_id].get("status", {})
                    if status.get("status_str") == "error":
                        error_msg = status.get("messages", [["Unknown error"]])
                        raise RuntimeError(f"Image generation failed: {error_msg}")

                    outputs = history[prompt_id].get("outputs", {})

                    # SaveImage 노드의 출력 확인 (노드 ID "9")
                    if "9" in outputs:
                        images = outputs["9"].get("images", [])
                        if images:
                            image_info = images[0]
                            filename = image_info["filename"]
                            subfolder = image_info.get("subfolder", "")

                            elapsed = time.time() - start_time
                            print(f"[FluxImageGenerator] Completed in {elapsed:.1f}s (polls: {poll_count})")

                            # 이미지 다운로드
                            return self._download_image(filename, subfolder)

            # 진행 상황 로깅 (10회마다)
            if poll_count % 10 == 0:
                elapsed = time.time() - start_time
                print(f"[FluxImageGenerator] Still generating... ({elapsed:.0f}s elapsed)")

            # 대기 (서버 부하 방지)
            time.sleep(2)

    def _download_image(self, filename: str, subfolder: str = "") -> bytes:
        """이미지 다운로드"""
        params = {
            "filename": filename,
            "subfolder": subfolder,
            "type": "output"
        }

        response = requests.get(self.view_endpoint, params=params)
        response.raise_for_status()

        print(f"[FluxImageGenerator] Downloaded: {filename}")
        return response.content

    def _generate_flux2c_api(
        self,
        prompt: str,
        width: int,
        height: int,
        seed: int = -1,
        steps: int = 4
    ) -> bytes:
        """
        Flux2C API를 사용하여 이미지 생성

        Args:
            prompt: 이미지 프롬프트 (영어)
            width: 이미지 가로 해상도
            height: 이미지 세로 해상도
            seed: 시드값 (-1이면 랜덤)
            steps: 샘플링 스텝 수 (기본값: 4)

        Returns:
            이미지 데이터 (bytes)
        """
        if not self.flux2c_api_url:
            raise ValueError("Flux2C API URL is not configured")

        print(f"[FluxImageGenerator] Calling Flux2C API: {self.flux2c_api_url}")

        payload = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "steps": steps,
            "seed": seed
        }

        response = requests.post(
            f"{self.flux2c_api_url}/generate",
            json=payload,
            timeout=self.flux2c_timeout
        )
        response.raise_for_status()

        data = response.json()
        image_bytes = base64.b64decode(data["image_base64"])

        print(f"[FluxImageGenerator] Flux2C API completed in {data.get('generation_time', 0):.1f}s")
        return image_bytes


# 테스트용 코드
if __name__ == "__main__":
    generator = FluxImageGenerator()

    test_prompt = "A wise old philosopher sitting under a tree, contemplating life"
    output_path = TEMP_DIR / "test_flux_image.png"

    try:
        result = generator.generate(test_prompt, output_path)
        print(f"✅ Image generated successfully: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")
