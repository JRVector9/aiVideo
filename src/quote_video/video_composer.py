"""
Video Composer using FFmpeg
FFmpeg을 사용한 영상 합성 (이미지 + 오디오 + 자막 + BGM)
"""

import subprocess
from pathlib import Path
from typing import Optional, List
from .config import (
    VIDEO_WIDTH,
    VIDEO_HEIGHT,
    VIDEO_FPS,
    VIDEO_FADE_DURATION,
    BGM_VOLUME,
    SUBTITLE_FONT,
    SUBTITLE_FONT_SIZE,
    SUBTITLE_FONT_COLOR,
    SUBTITLE_OUTLINE_COLOR,
    SUBTITLE_OUTLINE_WIDTH,
    FONT_DIR,
    TEMP_DIR,
    OUTPUT_DIR
)


class VideoComposer:
    """FFmpeg을 사용한 영상 합성기"""

    def __init__(self):
        """FFmpeg 사용 가능 여부 확인"""
        try:
            subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                check=True
            )
            print("[VideoComposer] FFmpeg is available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("FFmpeg is not installed or not in PATH")

    def compose_scene(
        self,
        image_path: Path,
        audio_path: Path,
        output_path: Path,
        subtitle_path: Optional[Path] = None,
        fade_in: bool = True,
        fade_out: bool = True
    ) -> Path:
        """
        단일 씬 합성 (이미지 + 오디오 + 자막)

        Args:
            image_path: 배경 이미지 경로
            audio_path: 오디오 파일 경로
            output_path: 출력 영상 경로
            subtitle_path: SRT 자막 파일 경로 (선택)
            fade_in: 페이드인 효과 적용 여부
            fade_out: 페이드아웃 효과 적용 여부

        Returns:
            생성된 영상 파일 경로
        """
        print(f"[VideoComposer] Composing scene...")
        print(f"[VideoComposer] Image: {image_path}")
        print(f"[VideoComposer] Audio: {audio_path}")

        # 오디오 길이 확인
        duration = self._get_audio_duration(audio_path)
        print(f"[VideoComposer] Duration: {duration:.2f}s")

        # FFmpeg 필터 구성
        video_filter = self._build_video_filter(
            duration, fade_in, fade_out, subtitle_path
        )

        # FFmpeg 명령 구성
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", str(image_path),
            "-i", str(audio_path),
            "-c:v", "libx264",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            "-vf", video_filter,
            "-r", str(VIDEO_FPS),
            str(output_path)
        ]

        # 실행
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        subprocess.run(cmd, check=True, capture_output=True)

        print(f"[VideoComposer] Scene composed: {output_path}")
        return output_path

    def compose_video(
        self,
        scenes: List[Path],
        output_path: Path,
        bgm_path: Optional[Path] = None,
        bgm_volume: float = BGM_VOLUME
    ) -> Path:
        """
        여러 씬을 하나의 영상으로 합성 (+ BGM)

        Args:
            scenes: 씬 영상 파일 경로 리스트
            output_path: 최종 출력 영상 경로
            bgm_path: 배경음악 파일 경로 (선택)
            bgm_volume: BGM 볼륨 (0.0 ~ 1.0)

        Returns:
            최종 영상 파일 경로
        """
        print(f"[VideoComposer] Composing final video...")
        print(f"[VideoComposer] Scenes: {len(scenes)}")

        # concat 리스트 파일 생성
        concat_file = TEMP_DIR / "concat_list.txt"
        with open(concat_file, 'w') as f:
            for scene in scenes:
                f.write(f"file '{scene.absolute()}'\n")

        # 씬 연결
        temp_output = TEMP_DIR / "temp_concatenated.mp4"
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",
            str(temp_output)
        ]

        subprocess.run(cmd, check=True, capture_output=True)

        # BGM 믹싱
        if bgm_path and bgm_path.exists():
            print(f"[VideoComposer] Adding BGM: {bgm_path}")
            final_output = self._add_bgm(temp_output, bgm_path, output_path, bgm_volume)
        else:
            final_output = output_path
            temp_output.rename(final_output)

        print(f"[VideoComposer] Final video: {final_output}")
        return final_output

    def _get_audio_duration(self, audio_path: Path) -> float:
        """오디오 길이 추출"""
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(audio_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())

    def _build_video_filter(
        self,
        duration: float,
        fade_in: bool,
        fade_out: bool,
        subtitle_path: Optional[Path]
    ) -> str:
        """비디오 필터 문자열 구성"""
        filters = []

        # 리사이즈
        filters.append(f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=decrease")
        filters.append(f"pad={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2")

        # 페이드 효과
        if fade_in:
            filters.append(f"fade=t=in:st=0:d={VIDEO_FADE_DURATION}")

        if fade_out:
            fade_start = max(0, duration - VIDEO_FADE_DURATION)
            filters.append(f"fade=t=out:st={fade_start}:d={VIDEO_FADE_DURATION}")

        # 자막
        if subtitle_path and subtitle_path.exists():
            # .ttf 또는 .otf 폰트 찾기
            font_path = FONT_DIR / f"{SUBTITLE_FONT}.ttf"
            if not font_path.exists():
                font_path = FONT_DIR / f"{SUBTITLE_FONT}.otf"

            # ASS 자막으로 변환하여 폰트 직접 지정
            ass_path = self._convert_srt_to_ass(subtitle_path, font_path if font_path.exists() else None)
            if ass_path:
                # subtitles 필터 사용 (ASS 파일 지원)
                # 경로의 특수 문자 이스케이프
                escaped_path = str(ass_path).replace('\\', '/').replace(':', '\\:')
                subtitle_filter = f"subtitles={escaped_path}"
                filters.append(subtitle_filter)

        return ",".join(filters)

    def _add_bgm(
        self,
        video_path: Path,
        bgm_path: Path,
        output_path: Path,
        volume: float
    ) -> Path:
        """배경음악 믹싱"""
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-stream_loop", "-1",
            "-i", str(bgm_path),
            "-filter_complex",
            f"[1:a]volume={volume}[bgm];[0:a][bgm]amix=inputs=2:duration=first[aout]",
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            str(output_path)
        ]

        subprocess.run(cmd, check=True, capture_output=True)
        return Path(output_path)

    def _color_to_hex(self, color: str) -> str:
        """색상명을 FFmpeg용 16진수로 변환"""
        color_map = {
            "white": "FFFFFF",
            "black": "000000",
            "red": "FF0000",
            "green": "00FF00",
            "blue": "0000FF",
        }
        return color_map.get(color.lower(), "FFFFFF")

    def _convert_srt_to_ass(self, srt_path: Path, font_path: Optional[Path]) -> Optional[Path]:
        """SRT 자막을 ASS 형식으로 변환 (폰트 경로 포함)"""
        try:
            # SRT 파일 읽기
            with open(srt_path, 'r', encoding='utf-8') as f:
                srt_content = f.read()

            # SRT 파싱
            dialogues = []
            blocks = srt_content.strip().split('\n\n')

            for block in blocks:
                lines = block.strip().split('\n')
                if len(lines) >= 3:
                    # 타임스탬프 파싱 (SRT 형식: HH:MM:SS,mmm)
                    timestamp_line = lines[1]
                    start_str, end_str = timestamp_line.split(' --> ')

                    # SRT 시간을 ASS 시간으로 변환
                    start_ass = self._srt_time_to_ass(start_str)
                    end_ass = self._srt_time_to_ass(end_str)

                    # 텍스트
                    text = '\n'.join(lines[2:])

                    dialogues.append((start_ass, end_ass, text))

            # ASS 파일 생성
            ass_path = srt_path.with_suffix('.ass')

            # 폰트 경로 설정
            fontname = str(font_path.absolute()) if font_path and font_path.exists() else "Arial"

            # ASS 헤더
            ass_content = f"""[Script Info]
Title: Quote Video Subtitle
ScriptType: v4.00+
WrapStyle: 0
PlayResX: {VIDEO_WIDTH}
PlayResY: {VIDEO_HEIGHT}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{fontname},{SUBTITLE_FONT_SIZE},&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,{SUBTITLE_OUTLINE_WIDTH},0,2,10,10,50,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

            # 대화 추가
            for start, end, text in dialogues:
                ass_content += f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}\n"

            # ASS 파일 저장
            with open(ass_path, 'w', encoding='utf-8') as f:
                f.write(ass_content)

            return ass_path

        except Exception as e:
            print(f"[VideoComposer] Warning: Failed to convert SRT to ASS: {e}")
            return None

    def _srt_time_to_ass(self, srt_time: str) -> str:
        """SRT 타임스탬프를 ASS 형식으로 변환
        SRT: HH:MM:SS,mmm
        ASS: H:MM:SS.cc (centiseconds)
        """
        # SRT 형식 파싱
        time_part, millis = srt_time.strip().split(',')
        h, m, s = time_part.split(':')

        # ASS 형식으로 변환 (centiseconds)
        centiseconds = int(millis) // 10

        return f"{int(h)}:{m}:{s}.{centiseconds:02d}"


# 테스트용 코드
if __name__ == "__main__":
    composer = VideoComposer()

    # 테스트할 파일들이 필요합니다
    test_image = TEMP_DIR / "test_flux_image.png"
    test_audio = TEMP_DIR / "test_tts.wav"
    test_subtitle = TEMP_DIR / "test_subtitle.srt"
    output_video = OUTPUT_DIR / "test_scene.mp4"

    if test_image.exists() and test_audio.exists():
        try:
            result = composer.compose_scene(
                test_image,
                test_audio,
                output_video,
                test_subtitle if test_subtitle.exists() else None
            )
            print(f"✅ Video composed successfully: {result}")
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print(f"❌ Test files not found")
