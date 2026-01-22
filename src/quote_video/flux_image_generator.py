"""
FLUX Image Generator using ComfyUI API
ComfyUI 서버를 통한 FLUX 모델 이미지 생성
"""

import json
import time
import uuid
import requests
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
    """ComfyUI FLUX 모델을 사용한 이미지 생성기"""

    def __init__(self, server_url: Optional[str] = None):
        """
        Args:
            server_url: ComfyUI 서버 URL (기본값: config에서 로드)
        """
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
        timeout: int = 300
    ) -> Path:
        """
        FLUX 모델로 이미지 생성

        Args:
            prompt: 이미지 생성 프롬프트 (한글/영어 모두 가능)
            output_path: 저장할 이미지 경로
            style_prompt: 스타일 프롬프트 (기본값: config의 IMAGE_STYLE_PROMPT)
            seed: 시드값 (-1이면 랜덤)
            timeout: 타임아웃 (초)

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
        print(f"[FluxImageGenerator] Final prompt: {full_prompt[:100]}...")

        # 워크플로우 준비
        workflow = self._prepare_workflow(full_prompt, seed)

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

    def _prepare_workflow(self, prompt: str, seed: int) -> Dict[str, Any]:
        """워크플로우 준비"""
        workflow = json.loads(json.dumps(DEFAULT_FLUX_WORKFLOW))

        # 프롬프트 설정 (Node 7: CLIPTextEncode)
        workflow["7"]["inputs"]["text"] = prompt

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

    def _wait_for_completion(self, prompt_id: str, timeout: int) -> bytes:
        """생성 완료 대기 및 이미지 다운로드"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            # 히스토리 확인
            history_url = f"{self.history_endpoint}/{prompt_id}"
            response = requests.get(history_url)

            if response.status_code == 200:
                history = response.json()

                if prompt_id in history:
                    outputs = history[prompt_id].get("outputs", {})

                    # SaveImage 노드의 출력 확인 (노드 ID "9")
                    if "9" in outputs:
                        images = outputs["9"].get("images", [])
                        if images:
                            image_info = images[0]
                            filename = image_info["filename"]
                            subfolder = image_info.get("subfolder", "")

                            # 이미지 다운로드
                            return self._download_image(filename, subfolder)

            # 대기
            time.sleep(2)

        raise TimeoutError(f"Image generation timed out after {timeout} seconds")

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
