"""
Config Manager
설정 스키마, 검증, 프리셋 관리 시스템
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, field_validator, ValidationError


# 프로젝트 경로
PROJECT_ROOT = Path(__file__).parent.parent
PRESETS_DIR = PROJECT_ROOT / "presets"
PRESETS_DIR.mkdir(exist_ok=True)


# ===========================
# 사용 가능한 옵션들
# ===========================
AVAILABLE_FONTS = {
    "KOTRA_BOLD.otf": "KOTRA Bold",
    "RIDIBatang.otf": "리디바탕",
    "강원교육모두 Bold.otf": "강원교육모두 Bold",
    "강원교육모두 Light.otf": "강원교육모두 Light",
    "강원교육새음.otf": "강원교육새음",
    "강원교육튼튼.otf": "강원교육튼튼",
    "강원교육현옥샘.otf": "강원교육현옥샘"
}

AVAILABLE_POSITIONS = {
    "top": "상단",
    "center": "중앙",
    "bottom": "하단"
}

AVAILABLE_BACKENDS = {
    "comfyui": "ComfyUI (기본)",
    "flux2c-api": "Flux2C API (Mac Metal 가속)"
}


# ===========================
# Pydantic 검증 모델
# ===========================
class VideoConfig(BaseModel):
    """영상 생성 설정 검증 모델"""

    # 이미지 설정 (기본값: 세로 영상 9:16)
    image_width: int = 1080
    image_height: int = 1920

    # 이미지 생성 백엔드
    image_backend: str = "comfyui"
    flux2c_api_url: Optional[str] = None

    # 전역 프롬프트
    global_prompt: Optional[str] = None

    # 명언 폰트 (중앙 상단)
    quote_font: Optional[str] = None

    # 저자 폰트 (중앙 하단)
    author_font: Optional[str] = None

    # 자막 설정
    subtitle_font: Optional[str] = None
    subtitle_font_size: int = 48
    subtitle_font_color: str = "#FFFFFF"
    subtitle_outline_color: str = "#000000"
    subtitle_outline_width: int = 2
    subtitle_position: str = "bottom"

    @field_validator('image_width', 'image_height')
    @classmethod
    def validate_dimensions(cls, v: int) -> int:
        if not 512 <= v <= 2048:
            raise ValueError('크기는 512-2048 사이여야 합니다')
        return v

    @field_validator('subtitle_font_size')
    @classmethod
    def validate_font_size(cls, v: int) -> int:
        if not 20 <= v <= 120:
            raise ValueError('폰트 크기는 20-120 사이여야 합니다')
        return v

    @field_validator('subtitle_outline_width')
    @classmethod
    def validate_outline_width(cls, v: int) -> int:
        if not 0 <= v <= 10:
            raise ValueError('외곽선 두께는 0-10 사이여야 합니다')
        return v

    @field_validator('quote_font', 'author_font', 'subtitle_font')
    @classmethod
    def validate_font(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v != "" and v not in AVAILABLE_FONTS:
            raise ValueError(f'사용 가능한 폰트가 아닙니다: {v}')
        return v if v != "" else None

    @field_validator('subtitle_position')
    @classmethod
    def validate_position(cls, v: str) -> str:
        if v not in AVAILABLE_POSITIONS:
            raise ValueError(f'사용 가능한 위치가 아닙니다: {v}')
        return v

    @field_validator('image_backend')
    @classmethod
    def validate_backend(cls, v: str) -> str:
        if v not in AVAILABLE_BACKENDS:
            raise ValueError(f'사용 가능한 백엔드가 아닙니다: {v}')
        return v


class PresetMetadata(BaseModel):
    """프리셋 메타데이터"""
    name: str
    description: Optional[str] = None
    created_at: str
    updated_at: str


class Preset(BaseModel):
    """프리셋 전체 구조"""
    metadata: PresetMetadata
    config: VideoConfig


# ===========================
# 설정 스키마 정의
# ===========================
CONFIG_SCHEMA = {
    "image": {
        "title": "이미지 설정",
        "fields": {
            "image_backend": {
                "type": "select",
                "label": "생성 백엔드",
                "options": AVAILABLE_BACKENDS,
                "default": "comfyui",
                "hint": "이미지 생성에 사용할 백엔드 엔진"
            },
            "flux2c_api_url": {
                "type": "text",
                "label": "Flux2C API URL",
                "default": "",
                "hint": "Flux2C API 사용 시 필수 (예: https://your-ngrok-url.ngrok-free.dev)",
                "show_if": {"image_backend": "flux2c-api"}
            },
            "image_width": {
                "type": "number",
                "label": "가로 크기",
                "min": 512,
                "max": 2048,
                "step": 64,
                "default": 1080,
                "hint": "이미지 가로 해상도 (픽셀)"
            },
            "image_height": {
                "type": "number",
                "label": "세로 크기",
                "min": 512,
                "max": 2048,
                "step": 64,
                "default": 1920,
                "hint": "이미지 세로 해상도 (픽셀)"
            }
        }
    },
    "fonts": {
        "title": "폰트 설정",
        "fields": {
            "quote_font": {
                "type": "select",
                "label": "중앙 상단",
                "options": AVAILABLE_FONTS,
                "default": "RIDIBatang.otf",
                "hint": "화면 중앙 상단에 표시될 명언 텍스트 폰트"
            },
            "author_font": {
                "type": "select",
                "label": "중앙 하단",
                "options": AVAILABLE_FONTS,
                "default": "RIDIBatang.otf",
                "hint": "화면 중앙 하단에 표시될 저자 텍스트 폰트"
            },
            "subtitle_font": {
                "type": "select",
                "label": "자막 폰트",
                "options": AVAILABLE_FONTS,
                "default": "KOTRA_BOLD.otf",
                "hint": "화면 하단 나레이션 자막 폰트"
            }
        }
    },
    "subtitle": {
        "title": "자막 스타일",
        "fields": {
            "subtitle_font_size": {
                "type": "number",
                "label": "폰트 크기",
                "min": 20,
                "max": 120,
                "step": 2,
                "default": 48,
                "hint": "자막 텍스트 크기"
            },
            "subtitle_font_color": {
                "type": "color",
                "label": "폰트 색상",
                "default": "#FFFFFF",
                "hint": "자막 텍스트 색상"
            },
            "subtitle_outline_color": {
                "type": "color",
                "label": "외곽선 색상",
                "default": "#000000",
                "hint": "자막 외곽선 색상"
            },
            "subtitle_outline_width": {
                "type": "number",
                "label": "외곽선 두께",
                "min": 0,
                "max": 10,
                "step": 1,
                "default": 2,
                "hint": "자막 외곽선 두께 (0: 없음)"
            },
            "subtitle_position": {
                "type": "select",
                "label": "위치",
                "options": AVAILABLE_POSITIONS,
                "default": "bottom",
                "hint": "자막 표시 위치"
            }
        }
    },
    "prompt": {
        "title": "프롬프트 설정",
        "fields": {
            "global_prompt": {
                "type": "textarea",
                "label": "전역 이미지 프롬프트",
                "default": "",
                "hint": "모든 Scene의 이미지 프롬프트에 자동으로 추가됩니다"
            }
        }
    }
}


# ===========================
# ConfigManager 클래스
# ===========================
class ConfigManager:
    """설정 관리 시스템"""

    def __init__(self):
        self.presets_dir = PRESETS_DIR
        self.presets_dir.mkdir(exist_ok=True)

    def get_schema(self) -> Dict[str, Any]:
        """
        프론트엔드용 설정 스키마 반환
        """
        return {
            "schema": CONFIG_SCHEMA,
            "fonts": AVAILABLE_FONTS,
            "positions": AVAILABLE_POSITIONS,
            "backends": AVAILABLE_BACKENDS,
            "defaults": self.get_defaults()
        }

    def get_defaults(self) -> Dict[str, Any]:
        """
        기본 설정값 반환
        """
        defaults = {}
        for section in CONFIG_SCHEMA.values():
            for field_name, field_info in section.get("fields", {}).items():
                defaults[field_name] = field_info.get("default")
        return defaults

    def validate(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        설정 검증

        Returns:
            {"valid": True, "config": validated_config} 또는
            {"valid": False, "errors": [...]}
        """
        try:
            validated = VideoConfig(**config)
            return {
                "valid": True,
                "config": validated.model_dump()
            }
        except ValidationError as e:
            errors = []
            for error in e.errors():
                field = ".".join(str(x) for x in error["loc"])
                errors.append({
                    "field": field,
                    "message": error["msg"]
                })
            return {
                "valid": False,
                "errors": errors
            }

    def save_preset(
        self,
        name: str,
        config: Dict[str, Any],
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        프리셋 저장

        Args:
            name: 프리셋 이름 (파일명으로 사용)
            config: 설정 값
            description: 프리셋 설명

        Returns:
            {"success": True, "preset": {...}} 또는
            {"success": False, "error": "..."}
        """
        # 설정 검증
        validation = self.validate(config)
        if not validation["valid"]:
            return {
                "success": False,
                "error": "설정 검증 실패",
                "details": validation["errors"]
            }

        # 파일명 안전하게 변환
        safe_name = self._sanitize_filename(name)
        if not safe_name:
            return {
                "success": False,
                "error": "유효하지 않은 프리셋 이름입니다"
            }

        preset_path = self.presets_dir / f"{safe_name}.json"
        now = datetime.now().isoformat()

        # 기존 프리셋이 있으면 updated_at만 갱신
        if preset_path.exists():
            existing = json.loads(preset_path.read_text(encoding="utf-8"))
            created_at = existing.get("metadata", {}).get("created_at", now)
        else:
            created_at = now

        preset = Preset(
            metadata=PresetMetadata(
                name=name,
                description=description,
                created_at=created_at,
                updated_at=now
            ),
            config=VideoConfig(**config)
        )

        preset_path.write_text(
            preset.model_dump_json(indent=2),
            encoding="utf-8"
        )

        return {
            "success": True,
            "preset": preset.model_dump()
        }

    def load_preset(self, name: str) -> Dict[str, Any]:
        """
        프리셋 불러오기

        Args:
            name: 프리셋 이름

        Returns:
            {"success": True, "preset": {...}} 또는
            {"success": False, "error": "..."}
        """
        safe_name = self._sanitize_filename(name)
        preset_path = self.presets_dir / f"{safe_name}.json"

        if not preset_path.exists():
            return {
                "success": False,
                "error": f"프리셋을 찾을 수 없습니다: {name}"
            }

        try:
            data = json.loads(preset_path.read_text(encoding="utf-8"))
            preset = Preset(**data)
            return {
                "success": True,
                "preset": preset.model_dump()
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"프리셋 로드 실패: {str(e)}"
            }

    def list_presets(self) -> List[Dict[str, Any]]:
        """
        프리셋 목록 반환

        Returns:
            프리셋 메타데이터 목록
        """
        presets = []
        for preset_file in sorted(self.presets_dir.glob("*.json")):
            try:
                data = json.loads(preset_file.read_text(encoding="utf-8"))
                metadata = data.get("metadata", {})
                presets.append({
                    "filename": preset_file.stem,
                    "name": metadata.get("name", preset_file.stem),
                    "description": metadata.get("description"),
                    "created_at": metadata.get("created_at"),
                    "updated_at": metadata.get("updated_at")
                })
            except Exception:
                continue
        return presets

    def delete_preset(self, name: str) -> Dict[str, Any]:
        """
        프리셋 삭제

        Args:
            name: 프리셋 이름

        Returns:
            {"success": True} 또는 {"success": False, "error": "..."}
        """
        safe_name = self._sanitize_filename(name)
        preset_path = self.presets_dir / f"{safe_name}.json"

        if not preset_path.exists():
            return {
                "success": False,
                "error": f"프리셋을 찾을 수 없습니다: {name}"
            }

        try:
            preset_path.unlink()
            return {"success": True}
        except Exception as e:
            return {
                "success": False,
                "error": f"프리셋 삭제 실패: {str(e)}"
            }

    def _sanitize_filename(self, name: str) -> str:
        """파일명에서 위험한 문자 제거"""
        # 공백은 언더스코어로 변환
        safe = name.strip().replace(" ", "_")
        # 위험한 문자 제거
        safe = "".join(c for c in safe if c.isalnum() or c in "_-")
        return safe[:100]  # 최대 100자


# 싱글톤 인스턴스
config_manager = ConfigManager()
