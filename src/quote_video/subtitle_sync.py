"""
Subtitle Synchronization using Whisper
Whisper를 사용한 타임스탬프 추출 및 SRT 자막 생성
"""

import whisper
from pathlib import Path
from typing import List, Tuple, Optional
from .config import WHISPER_MODEL, WHISPER_LANGUAGE, TEMP_DIR


class SubtitleSync:
    """Whisper를 사용한 자막 동기화"""

    def __init__(self, model_name: Optional[str] = None):
        """
        Args:
            model_name: Whisper 모델명 (기본값: config의 WHISPER_MODEL)
        """
        self.model_name = model_name or WHISPER_MODEL

        print(f"[SubtitleSync] Loading Whisper model: {self.model_name}")
        self.model = whisper.load_model(self.model_name)
        print(f"[SubtitleSync] Model loaded successfully")

    def generate_srt(
        self,
        audio_path: Path,
        output_path: Path,
        language: Optional[str] = None
    ) -> Path:
        """
        오디오 파일에서 타임스탬프를 추출하고 SRT 자막 생성

        Args:
            audio_path: 오디오 파일 경로
            output_path: SRT 파일 저장 경로
            language: 언어 코드 (기본값: config의 WHISPER_LANGUAGE)

        Returns:
            저장된 SRT 파일 경로
        """
        lang = language or WHISPER_LANGUAGE

        print(f"[SubtitleSync] Transcribing audio...")
        print(f"[SubtitleSync] Audio: {audio_path}")
        print(f"[SubtitleSync] Language: {lang}")

        # Whisper 실행
        result = self.model.transcribe(
            str(audio_path),
            language=lang,
            word_timestamps=True
        )

        # 세그먼트 추출
        segments = result.get("segments", [])

        if not segments:
            raise RuntimeError("No segments found in transcription")

        print(f"[SubtitleSync] Found {len(segments)} segments")

        # SRT 생성
        srt_content = self._create_srt(segments)

        # 저장
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(srt_content)

        print(f"[SubtitleSync] SRT saved: {output_path}")
        return output_path

    def get_timestamps(
        self,
        audio_path: Path,
        language: Optional[str] = None
    ) -> List[Tuple[float, float, str]]:
        """
        오디오에서 타임스탬프만 추출

        Args:
            audio_path: 오디오 파일 경로
            language: 언어 코드

        Returns:
            [(start_time, end_time, text), ...] 리스트
        """
        lang = language or WHISPER_LANGUAGE

        result = self.model.transcribe(
            str(audio_path),
            language=lang,
            word_timestamps=True
        )

        segments = result.get("segments", [])
        timestamps = []

        for seg in segments:
            start = seg["start"]
            end = seg["end"]
            text = seg["text"].strip()
            timestamps.append((start, end, text))

        return timestamps

    def _create_srt(self, segments: List[dict]) -> str:
        """세그먼트를 SRT 형식으로 변환"""
        srt_lines = []

        for i, seg in enumerate(segments, 1):
            start_time = self._format_timestamp(seg["start"])
            end_time = self._format_timestamp(seg["end"])
            text = seg["text"].strip()

            srt_lines.append(f"{i}")
            srt_lines.append(f"{start_time} --> {end_time}")
            srt_lines.append(text)
            srt_lines.append("")  # 빈 줄

        return "\n".join(srt_lines)

    def _format_timestamp(self, seconds: float) -> str:
        """초를 SRT 타임스탬프 형식으로 변환 (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)

        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


# 테스트용 코드
if __name__ == "__main__":
    sync = SubtitleSync()

    # 테스트할 오디오 파일이 필요합니다
    test_audio = TEMP_DIR / "test_tts.wav"
    output_srt = TEMP_DIR / "test_subtitle.srt"

    if test_audio.exists():
        try:
            result = sync.generate_srt(test_audio, output_srt)
            print(f"✅ SRT generated successfully: {result}")

            # 타임스탬프 출력
            timestamps = sync.get_timestamps(test_audio)
            for start, end, text in timestamps:
                print(f"[{start:.2f}s - {end:.2f}s] {text}")

        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print(f"❌ Test audio not found: {test_audio}")
