"""
한글 프롬프트로 이미지 생성 테스트
"""

from pathlib import Path
from src.quote_video.flux_image_generator import FluxImageGenerator

def test_korean_prompt():
    """한글 프롬프트 테스트"""
    generator = FluxImageGenerator()

    print("="*60)
    print("한글 프롬프트 이미지 생성 테스트")
    print("="*60)

    # 테스트 프롬프트 (한글)
    korean_prompt = "고요한 아침의 평화로운 산 풍경"
    output_path = Path("temp/test_korean_prompt.png")

    print(f"\n입력 프롬프트: {korean_prompt}")
    print(f"저장 경로: {output_path}")
    print("\n이미지 생성 시작... (약 20초 소요)")
    print("-"*60)

    try:
        result = generator.generate(
            prompt=korean_prompt,
            output_path=output_path,
            seed=-1
        )

        print("-"*60)
        print(f"✅ 성공! 이미지 생성 완료")
        print(f"📁 저장 위치: {result}")
        print(f"📏 파일 크기: {result.stat().st_size / 1024 / 1024:.2f} MB")

    except Exception as e:
        print("-"*60)
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_korean_prompt()
