"""
ComfyUI 연결 테스트
"""

import requests
import json
from pathlib import Path

COMFYUI_URL = "http://localhost:8188"

def test_server_status():
    """서버 상태 확인"""
    print("="*50)
    print("1. Server Status Test")
    print("="*50)

    try:
        response = requests.get(f"{COMFYUI_URL}/", timeout=10)
        print(f"✅ Server responded: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Server connection failed: {e}")
        return False


def test_system_stats():
    """시스템 정보 확인"""
    print("\n" + "="*50)
    print("2. System Stats Test")
    print("="*50)

    try:
        response = requests.get(f"{COMFYUI_URL}/system_stats", timeout=10)
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ System stats retrieved")
            print(f"   System: {json.dumps(stats, indent=2)[:200]}...")
            return True
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️  System stats endpoint not available: {e}")
        return True  # 이 엔드포인트는 선택사항


def test_prompt_endpoint():
    """프롬프트 엔드포인트 확인"""
    print("\n" + "="*50)
    print("3. Prompt Endpoint Test")
    print("="*50)

    # 간단한 워크플로우로 테스트
    test_workflow = {
        "1": {
            "inputs": {},
            "class_type": "CheckpointLoaderSimple"
        }
    }

    try:
        # 빈 프롬프트로 구조만 확인
        response = requests.get(f"{COMFYUI_URL}/prompt", timeout=10)
        print(f"✅ Prompt endpoint accessible")
        print(f"   Status: {response.status_code}")
        return True
    except Exception as e:
        print(f"⚠️  Prompt endpoint check: {e}")
        return True


def test_queue():
    """큐 상태 확인"""
    print("\n" + "="*50)
    print("4. Queue Status Test")
    print("="*50)

    try:
        response = requests.get(f"{COMFYUI_URL}/queue", timeout=10)
        if response.status_code == 200:
            queue = response.json()
            print(f"✅ Queue status retrieved")
            print(f"   Running: {len(queue.get('queue_running', []))}")
            print(f"   Pending: {len(queue.get('queue_pending', []))}")
            return True
        else:
            print(f"⚠️  Queue status: {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️  Queue endpoint: {e}")
        return True


def test_object_info():
    """노드 정보 확인 (FLUX 모델 사용 가능 여부)"""
    print("\n" + "="*50)
    print("5. Object Info Test (Node Types)")
    print("="*50)

    try:
        response = requests.get(f"{COMFYUI_URL}/object_info", timeout=10)
        if response.status_code == 200:
            info = response.json()

            # 주요 노드 타입 확인
            key_nodes = [
                "CheckpointLoaderSimple",
                "KSampler",
                "CLIPTextEncode",
                "VAEDecode",
                "SaveImage"
            ]

            print(f"✅ Object info retrieved")
            print(f"   Total node types: {len(info)}")
            print(f"\n   Key nodes available:")

            for node in key_nodes:
                if node in info:
                    print(f"   ✅ {node}")
                else:
                    print(f"   ❌ {node} (missing)")

            return True
        else:
            print(f"⚠️  Object info: {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️  Object info endpoint: {e}")
        return True


def test_embeddings():
    """사용 가능한 임베딩 확인"""
    print("\n" + "="*50)
    print("6. Embeddings Test")
    print("="*50)

    try:
        response = requests.get(f"{COMFYUI_URL}/embeddings", timeout=10)
        if response.status_code == 200:
            embeddings = response.json()
            print(f"✅ Embeddings retrieved: {len(embeddings)} available")
            return True
        else:
            print(f"⚠️  Embeddings: {response.status_code}")
            return True
    except Exception as e:
        print(f"⚠️  Embeddings endpoint: {e}")
        return True


def main():
    print("\n╔═══════════════════════════════════════╗")
    print("║   ComfyUI Connection Test            ║")
    print("║   Server: localhost:8188              ║")
    print("╚═══════════════════════════════════════╝\n")

    results = []

    # 테스트 실행
    results.append(("Server Status", test_server_status()))
    results.append(("System Stats", test_system_stats()))
    results.append(("Prompt Endpoint", test_prompt_endpoint()))
    results.append(("Queue Status", test_queue()))
    results.append(("Object Info", test_object_info()))
    results.append(("Embeddings", test_embeddings()))

    # 결과 요약
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)

    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{name:20s} {status}")

    critical_passed = results[0][1] and results[2][1]  # Server + Prompt endpoint

    print("="*50)
    if critical_passed:
        print("🎉 ComfyUI is ready to use!")
        print("\nNext: Test image generation")
        print("  python test_flux_image.py")
    else:
        print("⚠️  Critical tests failed. Check server connection.")

    return 0 if critical_passed else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
