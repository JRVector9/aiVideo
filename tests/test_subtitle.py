"""
Whisper 자막 생성 테스트
"""

import sys
sys.path.insert(0, 'src')

from pathlib import Path
from quote_video.subtitle_sync import SubtitleSync
from quote_video.config import TEMP_DIR

def main():
    print("\n╔═══════════════════════════════════════╗")
    print("║   Whisper Subtitle Test               ║")
    print("╚═══════════════════════════════════════╝\n")

    # 방금 생성한 TTS 오디오 사용
    audio_path = TEMP_DIR / "test_elevenlabs_tts.mp3"
    output_srt = TEMP_DIR / "test_subtitle.srt"

    if not audio_path.exists():
        print(f"❌ Audio file not found: {audio_path}")
        print("Please run TTS test first:")
        print("  python -m src.quote_video.tts_generator")
        return 1

    print("="*50)
    print("Configuration")
    print("="*50)
    print(f"Audio: {audio_path}")
    print(f"Output: {output_srt}")
    print()

    try:
        print("="*50)
        print("Initializing Whisper...")
        print("="*50)
        print("⏳ First run will download ~3GB model...")
        print()

        sync = SubtitleSync()

        print("\n" + "="*50)
        print("Generating Subtitles...")
        print("="*50)

        result = sync.generate_srt(audio_path, output_srt)

        print("\n" + "="*50)
        print("✅ SUCCESS!")
        print("="*50)
        print(f"SRT file: {result}")

        # SRT 내용 출력
        print("\n" + "="*50)
        print("SRT Content")
        print("="*50)
        with open(result, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content)

        # 타임스탬프 정보
        print("\n" + "="*50)
        print("Timestamps")
        print("="*50)
        timestamps = sync.get_timestamps(audio_path)
        for start, end, text in timestamps:
            print(f"[{start:.2f}s - {end:.2f}s] {text}")

        return 0

    except Exception as e:
        print("\n" + "="*50)
        print("❌ ERROR")
        print("="*50)
        print(f"Error: {e}")

        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
