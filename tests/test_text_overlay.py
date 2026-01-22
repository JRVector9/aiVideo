"""
Test Text Overlay Feature
명언 텍스트 오버레이 기능 테스트
"""

from pathlib import Path
import sys

# 프로젝트 루트를 파이썬 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.quote_video.video_composer import VideoComposer
from src.quote_video.config import TEMP_DIR, OUTPUT_DIR

def test_text_overlay():
    """FFmpeg drawtext 필터 테스트"""

    # 테스트용 임시 이미지 생성 (단색 배경)
    # FFmpeg로 간단한 테스트 이미지 생성
    import subprocess

    test_image = TEMP_DIR / "test_text_overlay_bg.png"
    test_audio = TEMP_DIR / "test_text_overlay_audio.wav"

    # 1. 테스트 이미지 생성 (1920x1080 검은색 배경)
    print("[Test] Creating test background image...")
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", "color=c=black:s=1920x1080:d=3",
        "-frames:v", "1",
        str(test_image)
    ]
    subprocess.run(cmd, check=True, capture_output=True)

    # 2. 테스트 오디오 생성 (3초 무음)
    print("[Test] Creating test audio...")
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", "anullsrc=r=44100:cl=stereo",
        "-t", "3",
        str(test_audio)
    ]
    subprocess.run(cmd, check=True, capture_output=True)

    # 3. VideoComposer로 텍스트 오버레이 테스트
    print("[Test] Testing text overlay...")
    composer = VideoComposer()

    output_video = OUTPUT_DIR / "test_text_overlay.mp4"

    result = composer.compose_scene(
        image_path=test_image,
        audio_path=test_audio,
        output_path=output_video,
        quote_text="인생은 고통이다",
        author="붓다",
        fade_in=False,
        fade_out=False
    )

    print(f"\n✅ Test completed successfully!")
    print(f"Output video: {result}")
    print(f"\nYou can play it with:")
    print(f"  ffplay {result}")
    print(f"  open {result}")

    return result


if __name__ == "__main__":
    try:
        test_text_overlay()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
