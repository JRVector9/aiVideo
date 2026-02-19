"""
동시 영상 생성 요청 테스트
"""
import asyncio
import aiohttp
import json
from datetime import datetime

API_URL = "https://aivideo.brut.bot"  # Dokploy 배포 주소

# 테스트용 간단한 Scene 데이터
REQUEST_1 = {
    "scenes": [
        {
            "narration": "인생은 짧다.",
            "image_prompt": "A minimalist illustration of a clock with flowing time",
            "quote_text": "인생은 짧다",
            "author": "테스트1"
        }
    ],
    "clean_temp": True,
    "image_width": 1280,
    "image_height": 720,
    "global_prompt": "Minimalist Notion-style illustration"
}

REQUEST_2 = {
    "scenes": [
        {
            "narration": "지혜는 힘이다.",
            "image_prompt": "A minimalist illustration of a glowing brain",
            "quote_text": "지혜는 힘이다",
            "author": "테스트2"
        }
    ],
    "clean_temp": True,
    "image_width": 1280,
    "image_height": 720,
    "global_prompt": "Minimalist Notion-style illustration"
}

async def create_video(session, request_data, request_num):
    """영상 생성 요청"""
    print(f"\n[요청 {request_num}] 영상 생성 시작 - {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")

    try:
        async with session.post(
            f"{API_URL}/api/create-video",
            json=request_data,
            timeout=aiohttp.ClientTimeout(total=30)
        ) as response:
            if response.status == 200:
                data = await response.json()
                print(f"[요청 {request_num}] ✅ 작업 생성 성공!")
                print(f"  - Job ID: {data['job_id']}")
                print(f"  - 파일명: {data['filename']}")
                return data['job_id'], request_num
            else:
                text = await response.text()
                print(f"[요청 {request_num}] ❌ 실패 ({response.status}): {text}")
                return None, request_num
    except Exception as e:
        print(f"[요청 {request_num}] ❌ 예외 발생: {e}")
        return None, request_num

async def monitor_job(session, job_id, request_num):
    """작업 진행 상태 모니터링"""
    if not job_id:
        return

    print(f"\n[요청 {request_num}] 작업 모니터링 시작 (Job ID: {job_id})")

    last_progress = -1
    last_stage = ""

    while True:
        try:
            async with session.get(f"{API_URL}/api/jobs/{job_id}") as response:
                if response.status == 200:
                    job = await response.json()

                    # 진행 상태가 변경되었을 때만 출력
                    if job['progress'] != last_progress or job['current_stage'] != last_stage:
                        timestamp = datetime.now().strftime('%H:%M:%S')
                        print(f"[{timestamp}] 요청{request_num}: {job['progress']}% - {job['current_stage']}")
                        last_progress = job['progress']
                        last_stage = job['current_stage']

                    # 완료 또는 실패 시 종료
                    if job['status'] in ['completed', 'failed']:
                        print(f"\n[요청 {request_num}] 최종 상태: {job['status']}")
                        if job['status'] == 'completed':
                            print(f"  ✅ 성공: {job['result']['filename']}")
                        else:
                            print(f"  ❌ 실패: {job.get('error', 'Unknown error')}")
                        break

                    # 2초마다 체크
                    await asyncio.sleep(2)
                else:
                    print(f"[요청 {request_num}] 작업 조회 실패: {response.status}")
                    break
        except Exception as e:
            print(f"[요청 {request_num}] 모니터링 에러: {e}")
            await asyncio.sleep(2)

async def main():
    """메인 테스트 함수"""
    print("=" * 80)
    print("동시 영상 생성 요청 테스트")
    print("=" * 80)
    print(f"API URL: {API_URL}")
    print(f"테스트 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    async with aiohttp.ClientSession() as session:
        # 1. 두 요청을 동시에 보내기
        print("\n📤 2개의 영상 생성 요청을 동시에 전송합니다...")
        tasks = [
            create_video(session, REQUEST_1, 1),
            create_video(session, REQUEST_2, 2)
        ]

        results = await asyncio.gather(*tasks)

        print("\n" + "=" * 80)
        print("요청 결과:")
        for job_id, req_num in results:
            if job_id:
                print(f"  요청 {req_num}: Job ID = {job_id}")
            else:
                print(f"  요청 {req_num}: 실패")
        print("=" * 80)

        # 2. 두 작업의 진행 상태를 동시에 모니터링
        print("\n📊 두 작업의 진행 상태를 동시에 모니터링합니다...\n")

        monitor_tasks = [
            monitor_job(session, job_id, req_num)
            for job_id, req_num in results
            if job_id
        ]

        if monitor_tasks:
            await asyncio.gather(*monitor_tasks)

        print("\n" + "=" * 80)
        print("테스트 완료!")
        print(f"종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
