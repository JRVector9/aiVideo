"""
Video Composer using FFmpeg
FFmpeg을 사용한 영상 합성 (이미지 + 오디오 + 자막 + BGM)
"""

import subprocess
import shutil
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
    QUOTE_FONT,
    QUOTE_FONT_SIZE,
    QUOTE_FONT_COLOR,
    QUOTE_OUTLINE_COLOR,
    QUOTE_OUTLINE_WIDTH,
    QUOTE_SHADOW_OFFSET,
    AUTHOR_FONT,
    AUTHOR_FONT_SIZE,
    AUTHOR_OUTLINE_WIDTH,
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
        quote_text: Optional[str] = None,
        author: Optional[str] = None,
        fade_in: bool = True,
        fade_out: bool = True,
        width: int = VIDEO_WIDTH,
        height: int = VIDEO_HEIGHT,
        # 자막 커스터마이징 옵션
        subtitle_font: Optional[str] = None,
        subtitle_font_size: Optional[int] = None,
        subtitle_font_color: Optional[str] = None,
        subtitle_outline_color: Optional[str] = None,
        subtitle_outline_width: Optional[int] = None,
        subtitle_position: Optional[str] = None,
        # 명언/저자 텍스트 폰트 옵션
        quote_font: Optional[str] = None,
        author_font: Optional[str] = None
    ) -> Path:
        """
        단일 씬 합성 (이미지 + 오디오 + 자막 + 명언 텍스트)

        Args:
            image_path: 배경 이미지 경로
            audio_path: 오디오 파일 경로
            output_path: 출력 영상 경로
            subtitle_path: SRT 자막 파일 경로 (선택)
            quote_text: 명언 텍스트 (선택) - FFmpeg drawtext로 오버레이
            author: 명언 저자 (선택) - quote_text와 함께 표시
            fade_in: 페이드인 효과 적용 여부
            fade_out: 페이드아웃 효과 적용 여부
            width: 영상 가로 해상도 (기본값: config의 VIDEO_WIDTH)
            height: 영상 세로 해상도 (기본값: config의 VIDEO_HEIGHT)
            subtitle_font: 자막 폰트 (선택, 기본값: config.SUBTITLE_FONT)
            subtitle_font_size: 자막 크기 (선택, 기본값: config.SUBTITLE_FONT_SIZE)
            subtitle_font_color: 자막 색상 (선택, 기본값: config.SUBTITLE_FONT_COLOR)
            subtitle_outline_color: 자막 외곽선 색상 (선택, 기본값: config.SUBTITLE_OUTLINE_COLOR)
            subtitle_outline_width: 자막 외곽선 두께 (선택, 기본값: config.SUBTITLE_OUTLINE_WIDTH)
            subtitle_position: 자막 위치 - "top"/"center"/"bottom" (선택, 기본값: config.SUBTITLE_POSITION)

        Returns:
            생성된 영상 파일 경로
        """
        print(f"[VideoComposer] Composing scene...")
        print(f"[VideoComposer] Image: {image_path}")
        print(f"[VideoComposer] Audio: {audio_path}")
        print(f"[VideoComposer] Resolution: {width}x{height}")

        # 오디오 길이 확인
        duration = self._get_audio_duration(audio_path)
        print(f"[VideoComposer] Duration: {duration:.2f}s")

        # FFmpeg 필터 구성
        video_filter = self._build_video_filter(
            duration, fade_in, fade_out, subtitle_path, quote_text, author, width, height,
            subtitle_font, subtitle_font_size, subtitle_font_color,
            subtitle_outline_color, subtitle_outline_width, subtitle_position,
            quote_font, author_font
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
            # Copy across volumes instead of rename (fixes cross-device link error)
            shutil.copy(temp_output, final_output)
            temp_output.unlink()

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
        subtitle_path: Optional[Path],
        quote_text: Optional[str],
        author: Optional[str],
        width: int = VIDEO_WIDTH,
        height: int = VIDEO_HEIGHT,
        subtitle_font: Optional[str] = None,
        subtitle_font_size: Optional[int] = None,
        subtitle_font_color: Optional[str] = None,
        subtitle_outline_color: Optional[str] = None,
        subtitle_outline_width: Optional[int] = None,
        subtitle_position: Optional[str] = None,
        quote_font: Optional[str] = None,
        author_font: Optional[str] = None
    ) -> str:
        """비디오 필터 문자열 구성"""
        filters = []

        # 리사이즈
        filters.append(f"scale={width}:{height}:force_original_aspect_ratio=decrease")
        filters.append(f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2")

        # 페이드 효과
        if fade_in:
            filters.append(f"fade=t=in:st=0:d={VIDEO_FADE_DURATION}")

        if fade_out:
            fade_start = max(0, duration - VIDEO_FADE_DURATION)
            filters.append(f"fade=t=out:st={fade_start}:d={VIDEO_FADE_DURATION}")

        # 명언 텍스트 오버레이 (drawtext 필터)
        if quote_text:
            quote_filter = self._build_quote_text_filter(
                quote_text, author, width, height, quote_font, author_font
            )
            if quote_filter:
                filters.append(quote_filter)

        # 자막 (Whisper 생성 자막 - 나레이션용)
        if subtitle_path and subtitle_path.exists():
            # ASS 자막으로 변환하여 폰트 직접 지정
            ass_path = self._convert_srt_to_ass(
                subtitle_path, width, height,
                subtitle_font, subtitle_font_size, subtitle_font_color,
                subtitle_outline_color, subtitle_outline_width, subtitle_position
            )
            if ass_path:
                # subtitles 필터 사용 (ASS 파일 지원)
                # 경로의 특수 문자 이스케이프
                escaped_path = str(ass_path).replace('\\', '/').replace(':', '\\:')
                escaped_font_dir = str(FONT_DIR).replace('\\', '/').replace(':', '\\:')
                # fontsdir 옵션 추가 (한글 폰트 경로 지정)
                subtitle_filter = f"subtitles={escaped_path}:fontsdir={escaped_font_dir}"
                filters.append(subtitle_filter)

        return ",".join(filters)

    def _build_quote_text_filter(
        self,
        quote_text: str,
        author: Optional[str],
        width: int,
        height: int,
        quote_font: Optional[str] = None,
        author_font: Optional[str] = None
    ) -> str:
        """명언 텍스트 drawtext 필터 구성

        Args:
            quote_text: 명언 본문
            author: 저자 이름 (선택)
            width: 영상 가로 해상도
            height: 영상 세로 해상도
            quote_font: 명언 텍스트 폰트 파일명 (선택)
            author_font: 저자 텍스트 폰트 파일명 (선택)

        Returns:
            drawtext 필터 문자열
        """
        # 폰트 파일 절대 경로
        quote_font_file = FONT_DIR / (quote_font or QUOTE_FONT)
        author_font_file = FONT_DIR / (author_font or AUTHOR_FONT)

        # 텍스트 이스케이프 (FFmpeg 특수 문자 처리)
        escaped_quote = quote_text.replace("'", "'\\\\\\''").replace(":", "\\:").replace("\\", "\\\\\\\\")

        # 명언 본문 필터
        # x=(w-text_w)/2: 가로 중앙
        # y=(h-text_h)/2-100: 세로 중앙에서 약간 위
        quote_filter = (
            f"drawtext="
            f"text='{escaped_quote}':"
            f"fontfile='{quote_font_file}':"
            f"fontsize={QUOTE_FONT_SIZE}:"
            f"fontcolor={QUOTE_FONT_COLOR}:"
            f"borderw={QUOTE_OUTLINE_WIDTH}:"
            f"bordercolor={QUOTE_OUTLINE_COLOR}:"
            f"shadowx={QUOTE_SHADOW_OFFSET}:"
            f"shadowy={QUOTE_SHADOW_OFFSET}:"
            f"shadowcolor=black@0.5:"
            f"x=(w-text_w)/2:"
            f"y=(h-text_h)/2-100"
        )

        # 저자 이름 필터 (있는 경우)
        if author:
            escaped_author = f"- {author}".replace("'", "'\\\\\\''").replace(":", "\\:").replace("\\", "\\\\\\\\")

            author_filter = (
                f"drawtext="
                f"text='{escaped_author}':"
                f"fontfile='{author_font_file}':"
                f"fontsize={AUTHOR_FONT_SIZE}:"
                f"fontcolor={QUOTE_FONT_COLOR}:"
                f"borderw={AUTHOR_OUTLINE_WIDTH}:"
                f"bordercolor={QUOTE_OUTLINE_COLOR}:"
                f"shadowx={QUOTE_SHADOW_OFFSET}:"
                f"shadowy={QUOTE_SHADOW_OFFSET}:"
                f"shadowcolor=black@0.5:"
                f"x=(w-text_w)/2:"
                f"y=(h-text_h)/2+150"
            )

            return f"{quote_filter},{author_filter}"

        return quote_filter

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

    def _color_to_ass(self, color: str) -> str:
        """색상명을 ASS 형식으로 변환 (&HAABBGGRR)"""
        color_map = {
            "white": "&H00FFFFFF",
            "black": "&H00000000",
            "red": "&H000000FF",
            "green": "&H0000FF00",
            "blue": "&H00FF0000",
        }
        return color_map.get(color.lower(), "&H00FFFFFF")

    def _convert_srt_to_ass(
        self,
        srt_path: Path,
        width: int = VIDEO_WIDTH,
        height: int = VIDEO_HEIGHT,
        subtitle_font: Optional[str] = None,
        subtitle_font_size: Optional[int] = None,
        subtitle_font_color: Optional[str] = None,
        subtitle_outline_color: Optional[str] = None,
        subtitle_outline_width: Optional[int] = None,
        subtitle_position: Optional[str] = None
    ) -> Optional[Path]:
        """SRT 자막을 ASS 형식으로 변환 (시스템 폰트 사용)"""
        try:
            # 기본값 설정 (config 값 사용)
            font_file = subtitle_font or SUBTITLE_FONT
            # 폰트 파일명에서 확장자 제거 (ASS Fontname용)
            fontname = Path(font_file).stem
            fontsize = subtitle_font_size or SUBTITLE_FONT_SIZE
            font_color = subtitle_font_color or SUBTITLE_FONT_COLOR
            outline_color_value = subtitle_outline_color or SUBTITLE_OUTLINE_COLOR
            outline_width = subtitle_outline_width or SUBTITLE_OUTLINE_WIDTH
            position = subtitle_position or SUBTITLE_POSITION

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

            # ASS 색상 설정
            primary_color = self._color_to_ass(font_color)
            outline_color_ass = self._color_to_ass(outline_color_value)

            # 자막 위치 설정 (ASS Alignment)
            # bottom: 2 (중앙 하단), center: 5 (중앙), top: 8 (중앙 상단)
            if position == "top":
                alignment = 8
                margin_v = 50
            elif position == "center":
                alignment = 5
                margin_v = 0
            else:  # bottom (기본값)
                alignment = 2
                margin_v = 50

            # ASS 헤더
            ass_content = f"""[Script Info]
Title: Quote Video Subtitle
ScriptType: v4.00+
WrapStyle: 0
PlayResX: {width}
PlayResY: {height}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{fontname},{fontsize},{primary_color},&H000000FF,{outline_color_ass},&H00000000,0,0,0,0,100,100,0,0,1,{outline_width},0,{alignment},10,10,{margin_v},1

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
