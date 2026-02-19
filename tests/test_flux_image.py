"""
FLUX 이미지 생성 테스트
ComfyUI API를 통한 실제 이미지 생성
"""

import sys
import os
sys.path.insert(0, 'src')

from pathlib import Path
from quote_video.flux_image_generator import FluxImageGenerator
from quote_video.config import TEMP_DIR

def main():
    print("\n╔═══════════════════════════════════════╗")
    print("║   FLUX Image Generation Test          ║")
    print("║   Server: localhost:8188          ║")
    print("╚═══════════════════════════════════════╝\n")

    # 출력 경로 설정
    output_path = TEMP_DIR / "test_flux_image.png"

    print("="*50)
    print("Test Configuration")
    print("="*50)
    print(f"Output: {output_path}")
    print(f"Server: http://localhost:8188")
    print()

    # 테스트 프롬프트
    test_prompt = "A wise old philosopher sitting under a tree, contemplating life"

    print("="*50)
    print("Test Prompt")
    print("="*50)
    print(f"{test_prompt}")
    print()

    try:
        # Generator 초기화
        print("Initializing FLUX Image Generator...")
        generator = FluxImageGenerator()
        print("✅ Generator initialized\n")

        # 이미지 생성
        print("="*50)
        print("Generating Image...")
        print("="*50)
        print("⏳ This may take 15-30 seconds...\n")

        result = generator.generate(
            prompt=test_prompt,
            output_path=output_path,
            seed=-1  # Random seed
        )

        print("\n" + "="*50)
        print("✅ SUCCESS!")
        print("="*50)
        print(f"Image saved: {result}")
        print(f"File size: {result.stat().st_size / 1024:.2f} KB")
        print()
        print("Open the image:")
        print(f"  open {result}")

        return 0

    except Exception as e:
        print("\n" + "="*50)
        print("❌ ERROR")
        print("="*50)
        print(f"Error: {e}")
        print()

        import traceback
        print("Traceback:")
        traceback.print_exc()

        return 1


if __name__ == "__main__":
    sys.exit(main())
