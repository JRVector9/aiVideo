"""
Korean to English Translator using DeepL API
이미지 생성 프롬프트를 위한 한영 번역 모듈
"""

import re
import requests
from typing import Optional
from .config import DEEPL_API_KEY, DEEPL_API_URL


class Translator:
    """DeepL API를 사용한 한영 번역기"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: DeepL API 키 (기본값: config에서 로드)
        """
        self.api_key = api_key or DEEPL_API_KEY
        self.api_url = DEEPL_API_URL

        if not self.api_key:
            print("[Translator] Warning: DEEPL_API_KEY not found. Translation will be skipped.")

    def is_korean(self, text: str) -> bool:
        """
        텍스트에 한글이 포함되어 있는지 확인

        Args:
            text: 확인할 텍스트

        Returns:
            한글이 포함되어 있으면 True
        """
        # 한글 유니코드 범위: AC00-D7A3 (가-힣)
        korean_pattern = re.compile(r'[\uAC00-\uD7A3]')
        return bool(korean_pattern.search(text))

    def translate_to_english(self, text: str) -> str:
        """
        한글 텍스트를 영어로 번역

        Args:
            text: 번역할 텍스트

        Returns:
            번역된 영어 텍스트 (실패 시 원본 반환)
        """
        # API 키가 없으면 원본 반환
        if not self.api_key:
            print("[Translator] Skipping translation (no API key)")
            return text

        # 한글이 없으면 원본 반환
        if not self.is_korean(text):
            print("[Translator] No Korean detected, using original text")
            return text

        try:
            print(f"[Translator] Translating: {text[:50]}...")

            # DeepL API 호출
            headers = {
                "Authorization": f"DeepL-Auth-Key {self.api_key}",
                "Content-Type": "application/x-www-form-urlencoded"
            }

            data = {
                "text": text,
                "target_lang": "EN-US",  # 미국 영어
                "source_lang": "KO"       # 한국어
            }

            response = requests.post(
                self.api_url,
                headers=headers,
                data=data,
                timeout=10
            )

            response.raise_for_status()

            result = response.json()
            translated_text = result["translations"][0]["text"]

            print(f"[Translator] Translated: {translated_text[:50]}...")
            return translated_text

        except requests.exceptions.RequestException as e:
            print(f"[Translator] API Error: {e}")
            print(f"[Translator] Using original text as fallback")
            return text

        except (KeyError, IndexError) as e:
            print(f"[Translator] Response parsing error: {e}")
            print(f"[Translator] Using original text as fallback")
            return text

        except Exception as e:
            print(f"[Translator] Unexpected error: {e}")
            print(f"[Translator] Using original text as fallback")
            return text


# 테스트용 코드
if __name__ == "__main__":
    translator = Translator()

    # 테스트 케이스
    test_cases = [
        "고요한 아침의 평화로운 산 풍경",
        "A peaceful mountain landscape at dawn",
        "지혜로운 철학자가 나무 아래에서 명상하는 모습",
        "Mixed text with 한글 and English"
    ]

    for test_text in test_cases:
        print(f"\n{'='*60}")
        print(f"Input: {test_text}")
        print(f"Korean detected: {translator.is_korean(test_text)}")
        result = translator.translate_to_english(test_text)
        print(f"Output: {result}")
