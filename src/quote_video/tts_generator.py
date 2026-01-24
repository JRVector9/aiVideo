"""
TTS Generator using ElevenLabs API
ElevenLabs를 사용한 고품질 나레이션 생성
"""

import os
from pathlib import Path
from typing import Optional
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from .config import (
    ELEVENLABS_API_KEY,
    ELEVENLABS_VOICE_ID,
    ELEVENLABS_MODEL,
    ELEVENLABS_VOICE_STABILITY,
    ELEVENLABS_VOICE_SIMILARITY,
    ELEVENLABS_STYLE,
    ELEVENLABS_USE_SPEAKER_BOOST,
    TEMP_DIR
)


class TTSGenerator:
    """ElevenLabs를 사용한 음성 생성기"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: ElevenLabs API 키 (기본값: config에서 로드)
        """
        self.api_key = api_key or ELEVENLABS_API_KEY

        if not self.api_key:
            raise ValueError(
                "ELEVENLABS_API_KEY is required. "
                "Set it in .env file or pass it to constructor.\n"
                "Get your API key from: https://elevenlabs.io/app/settings/api-keys"
            )

        self.client = ElevenLabs(api_key=self.api_key)
        self.voice_id = ELEVENLABS_VOICE_ID
        self.model = ELEVENLABS_MODEL

        print(f"[TTSGenerator] Initialized with ElevenLabs")
        print(f"[TTSGenerator] Model: {self.model}")
        print(f"[TTSGenerator] Voice ID: {self.voice_id}")

    def generate(
        self,
        text: str,
        output_path: Path,
        voice_id: Optional[str] = None,
        stability: Optional[float] = None,
        similarity: Optional[float] = None,
        language: Optional[str] = None
    ) -> Path:
        """
        텍스트를 음성으로 변환

        Args:
            text: 변환할 텍스트
            output_path: 저장할 MP3 파일 경로
            voice_id: 사용할 음성 ID (기본값: config의 ELEVENLABS_VOICE_ID)
            stability: 음성 안정성 0-1 (기본값: config 값)
            similarity: 음성 유사성 0-1 (기본값: config 값)
            language: 언어 코드 (예: 'ko', 'en', 'ja', 'zh', None=자동 감지)

        Returns:
            저장된 오디오 파일 경로
        """
        voice = voice_id or self.voice_id
        stab = stability if stability is not None else ELEVENLABS_VOICE_STABILITY
        sim = similarity if similarity is not None else ELEVENLABS_VOICE_SIMILARITY

        print(f"[TTSGenerator] Generating TTS...")
        print(f"[TTSGenerator] Text length: {len(text)} characters")
        print(f"[TTSGenerator] Text: {text[:100]}...")
        print(f"[TTSGenerator] Voice: {voice}")
        print(f"[TTSGenerator] Language: {language or 'auto-detect'}")

        try:
            # 음성 설정
            voice_settings = VoiceSettings(
                stability=stab,
                similarity_boost=sim,
                style=ELEVENLABS_STYLE,
                use_speaker_boost=ELEVENLABS_USE_SPEAKER_BOOST
            )

            # TTS 생성
            audio_generator = self.client.text_to_speech.convert(
                voice_id=voice,
                text=text,
                model_id=self.model,
                voice_settings=voice_settings
            )

            # 출력 경로 준비
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # 오디오 저장
            with open(output_path, 'wb') as f:
                for chunk in audio_generator:
                    f.write(chunk)

            print(f"[TTSGenerator] Audio saved: {output_path}")
            print(f"[TTSGenerator] File size: {output_path.stat().st_size / 1024:.2f} KB")

            return output_path

        except Exception as e:
            print(f"[TTSGenerator] Error: {e}")
            raise

    def list_voices(self):
        """사용 가능한 음성 목록 조회"""
        print("[TTSGenerator] Fetching available voices...")

        try:
            voices = self.client.voices.get_all()

            print(f"\nAvailable voices ({len(voices.voices)}):\n")

            for voice in voices.voices[:10]:  # 처음 10개만 표시
                print(f"  🎤 {voice.name}")
                print(f"     ID: {voice.voice_id}")
                print(f"     Labels: {', '.join(voice.labels.values()) if voice.labels else 'N/A'}")
                print()

            return voices.voices

        except Exception as e:
            print(f"[TTSGenerator] Error fetching voices: {e}")
            return []


# 테스트용 코드
if __name__ == "__main__":
    try:
        generator = TTSGenerator()

        # 음성 목록 확인
        print("="*60)
        print("Available Voices")
        print("="*60)
        generator.list_voices()

        # 테스트 TTS 생성
        print("\n" + "="*60)
        print("TTS Generation Test")
        print("="*60)

        test_text = "인생은 고통이다. 그러나 우리는 이 고통을 받아들이고 초월해야 한다."
        output_path = TEMP_DIR / "test_elevenlabs_tts.mp3"

        result = generator.generate(test_text, output_path)
        print(f"\n✅ TTS generated successfully: {result}")
        print(f"\nPlay audio:")
        print(f"  open {result}")

    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
