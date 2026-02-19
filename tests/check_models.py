"""
ComfyUI 서버의 사용 가능한 모델 확인
"""

import requests
import json

COMFYUI_URL = "http://localhost:8188"

def check_checkpoints():
    """사용 가능한 Checkpoint 모델 확인"""
    print("="*60)
    print("Available Checkpoint Models")
    print("="*60)

    try:
        response = requests.get(f"{COMFYUI_URL}/object_info/CheckpointLoaderSimple", timeout=10)

        if response.status_code == 200:
            info = response.json()
            checkpoints = info.get("CheckpointLoaderSimple", {}).get("input", {}).get("required", {}).get("ckpt_name", [])

            if isinstance(checkpoints, list) and len(checkpoints) > 0:
                models = checkpoints[0] if isinstance(checkpoints[0], list) else checkpoints

                print(f"Total models: {len(models)}")
                print("\nFLUX models:")
                flux_models = [m for m in models if 'flux' in m.lower()]
                for model in flux_models:
                    print(f"  ✅ {model}")

                print("\nOther models:")
                other_models = [m for m in models if 'flux' not in m.lower()][:10]
                for model in other_models:
                    print(f"  - {model}")

                if len(other_models) > 10:
                    print(f"  ... and {len(other_models) - 10} more")

                return models
            else:
                print("⚠️  No checkpoint info found")
        else:
            print(f"⚠️  Status: {response.status_code}")

    except Exception as e:
        print(f"❌ Error: {e}")

    return []


def get_samplers():
    """사용 가능한 샘플러 확인"""
    print("\n" + "="*60)
    print("Available Samplers")
    print("="*60)

    try:
        response = requests.get(f"{COMFYUI_URL}/object_info/KSampler", timeout=10)

        if response.status_code == 200:
            info = response.json()
            sampler_info = info.get("KSampler", {}).get("input", {}).get("required", {})

            samplers = sampler_info.get("sampler_name", [[]])[0]
            schedulers = sampler_info.get("scheduler", [[]])[0]

            print(f"Samplers: {', '.join(samplers[:10])}")
            if len(samplers) > 10:
                print(f"  ... and {len(samplers) - 10} more")

            print(f"\nSchedulers: {', '.join(schedulers)}")

            return samplers, schedulers
    except Exception as e:
        print(f"❌ Error: {e}")

    return [], []


def main():
    print("\n╔════════════════════════════════════════════════════════╗")
    print("║   ComfyUI Model & Config Check                        ║")
    print("╚════════════════════════════════════════════════════════╝\n")

    models = check_checkpoints()
    samplers, schedulers = get_samplers()

    print("\n" + "="*60)
    print("Recommendation")
    print("="*60)

    flux_models = [m for m in models if 'flux' in m.lower()]

    if flux_models:
        print(f"✅ Use FLUX model: {flux_models[0]}")
    else:
        print("⚠️  No FLUX models found")
        if models:
            print(f"💡 Available model: {models[0]}")

    if samplers:
        print(f"✅ Use sampler: {samplers[0]}")

    if schedulers:
        print(f"✅ Use scheduler: {schedulers[0]}")


if __name__ == "__main__":
    main()
