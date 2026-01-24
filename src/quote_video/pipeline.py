"""
Quote Video Pipeline
전체 파이프라인 조율 (이미지 생성 → TTS → 자막 → 영상 합성)
"""

from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from .flux_image_generator import FluxImageGenerator
from .tts_generator import TTSGenerator
from .subtitle_sync import SubtitleSync
from .video_composer import VideoComposer
from .config import TEMP_DIR, OUTPUT_DIR


@dataclass
class Scene:
    """단일 씬 데이터"""
    narration: str  # 한국어 나레이션 텍스트
    image_prompt: str  # 영어 이미지 프롬프트
    quote_text: Optional[str] = None  # 명언 본문 (화면에 표시될 텍스트)
    author: Optional[str] = None  # 명언 저자
    # 자막 커스터마이징 옵션 (씬별 설정, 선택사항)
    subtitle_font: Optional[str] = None
    subtitle_font_size: Optional[int] = None
    subtitle_font_color: Optional[str] = None
    subtitle_outline_color: Optional[str] = None
    subtitle_outline_width: Optional[int] = None
    subtitle_position: Optional[str] = None
    # 명언/저자 텍스트 폰트 옵션 (씬별 설정, 선택사항)
    quote_font: Optional[str] = None
    author_font: Optional[str] = None


class QuoteVideoPipeline:
    """명언 영상 자동 생성 파이프라인"""

    def __init__(
        self,
        comfyui_url: Optional[str] = None,
        gemini_api_key: Optional[str] = None,
        whisper_model: Optional[str] = None
    ):
        """
        Args:
            comfyui_url: ComfyUI 서버 URL
            gemini_api_key: Gemini API 키
            whisper_model: Whisper 모델명
        """
        print("[Pipeline] Initializing components...")

        self.image_generator = FluxImageGenerator(comfyui_url)
        self.tts_generator = TTSGenerator(gemini_api_key)
        self.subtitle_sync = SubtitleSync(whisper_model)
        self.video_composer = VideoComposer()

        print("[Pipeline] All components initialized")

    def create_video(
        self,
        scenes: List[Scene],
        output_name: str,
        bgm_path: Optional[Path] = None,
        clean_temp: bool = True,
        progress_callback: Optional[callable] = None,
        image_width: int = 1920,
        image_height: int = 1080,
        # 전역 자막 설정 (모든 씬에 적용, Scene별 설정이 우선)
        subtitle_font: Optional[str] = None,
        subtitle_font_size: Optional[int] = None,
        subtitle_font_color: Optional[str] = None,
        subtitle_outline_color: Optional[str] = None,
        subtitle_outline_width: Optional[int] = None,
        subtitle_position: Optional[str] = None,
        # 전역 명언/저자 텍스트 폰트 설정 (모든 씬에 적용, Scene별 설정이 우선)
        quote_font: Optional[str] = None,
        author_font: Optional[str] = None
    ) -> Path:
        """
        씬 데이터로부터 최종 영상 생성

        Args:
            scenes: 씬 데이터 리스트
            output_name: 출력 파일명 (확장자 제외)
            bgm_path: 배경음악 파일 경로
            clean_temp: 임시 파일 삭제 여부
            progress_callback: 진행 상태 콜백 함수 (stage, progress)
            image_width: 이미지 가로 해상도 (기본값: 1920)
            image_height: 이미지 세로 해상도 (기본값: 1080)

        Returns:
            최종 영상 파일 경로
        """
        print(f"\n{'='*60}")
        print(f"[Pipeline] Creating video: {output_name}")
        print(f"[Pipeline] Total scenes: {len(scenes)}")
        print(f"{'='*60}\n")

        scene_videos = []
        total_scenes = len(scenes)

        # 각 씬 처리
        for i, scene in enumerate(scenes, 1):
            print(f"\n--- Processing Scene {i}/{total_scenes} ---")

            # 씬 처리 시작
            if progress_callback:
                progress_callback(
                    f"🎬 Scene {i}/{total_scenes} 처리 중...",
                    int(20 + (i-1) * 60 / total_scenes)
                )

            scene_video = self._process_scene(
                scene, i, progress_callback, total_scenes, image_width, image_height,
                subtitle_font, subtitle_font_size, subtitle_font_color,
                subtitle_outline_color, subtitle_outline_width, subtitle_position,
                quote_font, author_font
            )
            scene_videos.append(scene_video)

        # 최종 영상 합성
        print(f"\n--- Composing Final Video ---")
        if progress_callback:
            progress_callback("🎞️ 최종 영상 합성 중...", 85)

        output_path = OUTPUT_DIR / f"{output_name}.mp4"
        final_video = self.video_composer.compose_video(
            scene_videos,
            output_path,
            bgm_path
        )

        # 임시 파일 정리
        if clean_temp:
            print("[Pipeline] Cleaning temporary files...")
            self._clean_temp_files()

        print(f"\n{'='*60}")
        print(f"[Pipeline] ✅ Video created successfully!")
        print(f"[Pipeline] Output: {final_video}")
        print(f"{'='*60}\n")

        return final_video

    def _process_scene(
        self,
        scene: Scene,
        scene_num: int,
        progress_callback: Optional[callable] = None,
        total_scenes: int = 1,
        image_width: int = 1920,
        image_height: int = 1080,
        global_subtitle_font: Optional[str] = None,
        global_subtitle_font_size: Optional[int] = None,
        global_subtitle_font_color: Optional[str] = None,
        global_subtitle_outline_color: Optional[str] = None,
        global_subtitle_outline_width: Optional[int] = None,
        global_subtitle_position: Optional[str] = None,
        global_quote_font: Optional[str] = None,
        global_author_font: Optional[str] = None
    ) -> Path:
        """단일 씬 처리"""
        scene_prefix = f"scene_{scene_num:03d}"
        base_progress = 20 + (scene_num - 1) * 60 / total_scenes

        # 1. 이미지 생성
        print(f"[Scene {scene_num}] Generating image...")
        if progress_callback:
            progress_callback(f"🎨 Scene {scene_num}: 이미지 생성 중...", int(base_progress + 5))

        image_path = TEMP_DIR / f"{scene_prefix}_image.png"
        self.image_generator.generate(
            scene.image_prompt,
            image_path,
            width=image_width,
            height=image_height
        )

        # 2. TTS 생성
        print(f"[Scene {scene_num}] Generating TTS...")
        if progress_callback:
            progress_callback(f"🎙️ Scene {scene_num}: 음성 생성 중...", int(base_progress + 15))

        audio_path = TEMP_DIR / f"{scene_prefix}_audio.wav"
        self.tts_generator.generate(
            scene.narration,
            audio_path
        )

        # 3. 자막 생성
        print(f"[Scene {scene_num}] Generating subtitles...")
        if progress_callback:
            progress_callback(f"📝 Scene {scene_num}: 자막 생성 중...", int(base_progress + 25))

        subtitle_path = TEMP_DIR / f"{scene_prefix}_subtitle.srt"
        self.subtitle_sync.generate_srt(
            audio_path,
            subtitle_path
        )

        # 4. 씬 합성
        print(f"[Scene {scene_num}] Composing scene...")
        if progress_callback:
            progress_callback(f"🎬 Scene {scene_num}: 합성 중...", int(base_progress + 40))

        scene_video_path = TEMP_DIR / f"{scene_prefix}_video.mp4"

        # 자막 설정: Scene별 설정 우선, 없으면 전역 설정 사용
        subtitle_font = scene.subtitle_font or global_subtitle_font
        subtitle_font_size = scene.subtitle_font_size or global_subtitle_font_size
        subtitle_font_color = scene.subtitle_font_color or global_subtitle_font_color
        subtitle_outline_color = scene.subtitle_outline_color or global_subtitle_outline_color
        subtitle_outline_width = scene.subtitle_outline_width or global_subtitle_outline_width
        subtitle_position = scene.subtitle_position or global_subtitle_position

        self.video_composer.compose_scene(
            image_path,
            audio_path,
            scene_video_path,
            subtitle_path,
            quote_text=scene.quote_text,
            author=scene.author,
            width=image_width,
            height=image_height,
            subtitle_font=scene.subtitle_font or subtitle_font,
            subtitle_font_size=scene.subtitle_font_size or subtitle_font_size,
            subtitle_font_color=scene.subtitle_font_color or subtitle_font_color,
            subtitle_outline_color=scene.subtitle_outline_color or subtitle_outline_color,
            subtitle_outline_width=scene.subtitle_outline_width or subtitle_outline_width,
            subtitle_position=scene.subtitle_position or subtitle_position,
            quote_font=scene.quote_font or global_quote_font,
            author_font=scene.author_font or global_author_font
        )

        print(f"[Scene {scene_num}] ✅ Scene completed")
        return scene_video_path

    def _clean_temp_files(self):
        """임시 파일 정리"""
        for file in TEMP_DIR.glob("scene_*"):
            file.unlink()
        print("[Pipeline] Temporary files cleaned")


# 테스트용 코드
if __name__ == "__main__":
    # 테스트 씬 데이터
    test_scenes = [
        Scene(
            narration="인생은 고통이다.",
            image_prompt="A wise philosopher contemplating life, pencil sketch style",
            quote_text="인생은 고통이다",
            author="붓다"
        ),
        Scene(
            narration="그러나 우리는 이 고통을 받아들이고 초월해야 한다.",
            image_prompt="A person meditating under a tree, minimalist illustration",
            quote_text="고통을 받아들이고\n초월하라",
            author="붓다"
        ),
    ]

    # 파이프라인 실행
    try:
        pipeline = QuoteVideoPipeline()
        result = pipeline.create_video(
            scenes=test_scenes,
            output_name="test_quote_video",
            clean_temp=False
        )
        print(f"✅ Final video: {result}")

    except Exception as e:
        print(f"❌ Pipeline error: {e}")
        import traceback
        traceback.print_exc()
