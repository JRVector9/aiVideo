"""
명언 영상 생성 예시 - 텍스트 오버레이 활용
"""

from pathlib import Path
from src.quote_video.pipeline import QuoteVideoPipeline, Scene

# 파이프라인 초기화
pipeline = QuoteVideoPipeline()

# 씬 생성 - quote_text와 author 추가!
scenes = [
    Scene(
        narration="인생은 고통이다. 그러나 이 고통을 받아들이고 초월할 때 우리는 진정한 평화를 얻는다.",
        image_prompt="A serene Buddha statue under a bodhi tree, golden sunset, peaceful atmosphere, minimalist illustration",
        quote_text="인생은 고통이다",  # 화면에 표시될 명언
        author="붓다"                   # 저자
    ),
    Scene(
        narration="어둠은 어둠으로 몰아낼 수 없다. 오직 빛만이 그것을 할 수 있다.",
        image_prompt="A candle lighting the darkness, warm glow, hope and peace, minimalist sketch",
        quote_text="어둠은 빛으로만\n몰아낼 수 있다",  # 줄바꿈도 가능!
        author="마틴 루터 킹"
    ),
    Scene(
        narration="살아있는 것들 중 가장 강한 것은 가장 부드러운 것이다.",
        image_prompt="Water flowing around rocks, gentle stream, nature's wisdom, pencil sketch style",
        quote_text="부드러움이\n가장 강하다",
        author="노자"
    )
]

# 영상 생성
print("🎬 명언 영상 생성 시작...")

video = pipeline.create_video(
    scenes=scenes,
    output_name="philosophy_quotes_with_text",
    bgm_path=Path("assets/bgm/peaceful.mp3") if Path("assets/bgm/peaceful.mp3").exists() else None,
    clean_temp=False  # 디버깅을 위해 임시 파일 유지
)

print(f"\n✅ 영상 생성 완료: {video}")
print(f"\n재생: open {video}")
