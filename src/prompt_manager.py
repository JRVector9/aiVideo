"""
Prompt History Manager
영상 생성 시 사용된 프롬프트를 저장하고 조회하는 관리자
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class PromptManager:
    """프롬프트 히스토리 관리"""

    def __init__(self, prompts_dir: Path):
        """
        Args:
            prompts_dir: 프롬프트 저장 디렉토리
        """
        self.prompts_dir = prompts_dir
        self.prompts_dir.mkdir(exist_ok=True, parents=True)

    def save_prompt(
        self,
        filename: str,
        scenes: List[Dict],
        global_prompt: Optional[str] = None,
        subtitle_settings: Optional[Dict] = None,
        image_width: int = 1920,
        image_height: int = 1080
    ):
        """
        프롬프트 히스토리 저장

        Args:
            filename: 영상 파일명 (확장자 포함)
            scenes: Scene 데이터 리스트
            global_prompt: 전역 이미지 프롬프트
            subtitle_settings: 자막 설정 딕셔너리
            image_width: 이미지 가로 해상도
            image_height: 이미지 세로 해상도
        """
        # 파일명에서 확장자 제거
        base_name = filename.replace('.mp4', '')
        prompt_file = self.prompts_dir / f"{base_name}.json"

        prompt_data = {
            "filename": filename,
            "timestamp": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "global_prompt": global_prompt,
            "image_width": image_width,
            "image_height": image_height,
            "subtitle_settings": subtitle_settings or {},
            "scenes_count": len(scenes),
            "scenes": scenes
        }

        with open(prompt_file, 'w', encoding='utf-8') as f:
            json.dump(prompt_data, f, ensure_ascii=False, indent=2)

        print(f"[PromptManager] Saved prompt history: {prompt_file}")

    def get_prompt(self, filename: str) -> Optional[Dict]:
        """
        프롬프트 히스토리 조회

        Args:
            filename: 영상 파일명 (확장자 포함)

        Returns:
            프롬프트 데이터 딕셔너리 또는 None
        """
        base_name = filename.replace('.mp4', '')
        prompt_file = self.prompts_dir / f"{base_name}.json"

        if not prompt_file.exists():
            return None

        with open(prompt_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def list_prompts(self, limit: int = 50) -> List[Dict]:
        """
        저장된 프롬프트 목록 조회

        Args:
            limit: 최대 조회 개수

        Returns:
            프롬프트 데이터 리스트 (최신순)
        """
        prompt_files = sorted(
            self.prompts_dir.glob("*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )

        prompts = []
        for prompt_file in prompt_files[:limit]:
            try:
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    prompt_data = json.load(f)
                    prompts.append(prompt_data)
            except Exception as e:
                print(f"[PromptManager] Error loading {prompt_file}: {e}")

        return prompts

    def delete_prompt(self, filename: str) -> bool:
        """
        프롬프트 히스토리 삭제

        Args:
            filename: 영상 파일명 (확장자 포함)

        Returns:
            삭제 성공 여부
        """
        base_name = filename.replace('.mp4', '')
        prompt_file = self.prompts_dir / f"{base_name}.json"

        if prompt_file.exists():
            prompt_file.unlink()
            print(f"[PromptManager] Deleted prompt history: {prompt_file}")
            return True

        return False
