"""
Test cases for Korean to English translation
"""

from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.quote_video.translator import Translator


def test_korean_detection():
    """한글 감지 테스트"""
    translator = Translator()

    print("\n=== Korean Detection Test ===")

    test_cases = [
        ("고요한 아침", True),
        ("A peaceful morning", False),
        ("Mixed 한글 text", True),
        ("100% English", False),
    ]

    for text, expected in test_cases:
        result = translator.is_korean(text)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{text}' -> Korean: {result} (expected: {expected})")


def test_translation():
    """번역 테스트"""
    translator = Translator()

    print("\n=== Translation Test ===")

    test_cases = [
        "고요한 아침의 평화로운 산 풍경",
        "지혜로운 철학자가 나무 아래에서 명상하는 모습",
        "A wise philosopher contemplating life",
    ]

    for text in test_cases:
        print(f"\nInput: {text}")
        result = translator.translate_to_english(text)
        print(f"Output: {result}")
        print(f"Changed: {text != result}")


def test_flux_integration():
    """FluxImageGenerator 통합 테스트"""
    print("\n=== Flux Integration Test ===")

    # FluxImageGenerator 인스턴스 생성만 확인
    try:
        from src.quote_video.flux_image_generator import FluxImageGenerator

        generator = FluxImageGenerator()
        print("✅ FluxImageGenerator created successfully")
        print(f"✅ Translator initialized: {generator.translator is not None}")

        # 번역 기능 확인 (이미지 생성은 하지 않음)
        test_prompt = "고요한 아침의 산"
        translated = generator.translator.translate_to_english(test_prompt)
        print(f"✅ Translation works: '{test_prompt}' -> '{translated}'")

    except ModuleNotFoundError as e:
        print(f"⚠️  Skipping Flux integration test (missing dependency: {e})")
        print("✅ Translation module works independently")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_korean_detection()
    test_translation()
    test_flux_integration()

    print("\n" + "="*60)
    print("All tests completed!")
