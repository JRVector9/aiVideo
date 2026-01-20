"""
ComfyUI에서 FLUX 모델 찾기 - 모든 로더 타입 확인
"""

import requests
import json

COMFYUI_URL = "https://comfyui.jrai.space"

def search_all_loaders():
    """모든 로더 타입에서 FLUX 모델 찾기"""
    print("="*60)
    print("Searching for FLUX models in all loaders...")
    print("="*60)

    try:
        response = requests.get(f"{COMFYUI_URL}/object_info", timeout=10)

        if response.status_code != 200:
            print(f"❌ Failed to get object info: {response.status_code}")
            return

        all_info = response.json()

        # 로더 관련 노드 찾기
        loader_nodes = [key for key in all_info.keys() if 'loader' in key.lower() or 'load' in key.lower()]

        print(f"\nFound {len(loader_nodes)} loader-related nodes:\n")

        flux_found = False

        for node_name in sorted(loader_nodes):
            node_info = all_info[node_name]
            inputs = node_info.get("input", {}).get("required", {})

            # 모든 input 확인
            for input_name, input_data in inputs.items():
                if isinstance(input_data, list) and len(input_data) > 0:
                    options = input_data[0] if isinstance(input_data[0], list) else []

                    # FLUX 관련 옵션 찾기
                    flux_options = [opt for opt in options if isinstance(opt, str) and 'flux' in opt.lower()]

                    if flux_options:
                        print(f"✅ {node_name}")
                        print(f"   Input: {input_name}")
                        print(f"   FLUX models found:")
                        for opt in flux_options:
                            print(f"      🎯 {opt}")
                        print()
                        flux_found = True

        if not flux_found:
            print("⚠️  No FLUX models found in any loader")
            print("\nLet's check common loader nodes:")

            common_loaders = [
                "CheckpointLoaderSimple",
                "UNETLoader",
                "DualCLIPLoader",
                "CLIPLoader",
                "VAELoader",
                "LoraLoader"
            ]

            for loader in common_loaders:
                if loader in all_info:
                    print(f"\n📦 {loader}:")
                    inputs = all_info[loader].get("input", {}).get("required", {})

                    for input_name, input_data in inputs.items():
                        if isinstance(input_data, list) and len(input_data) > 0:
                            options = input_data[0] if isinstance(input_data[0], list) else []

                            if isinstance(options, list) and len(options) > 0:
                                print(f"   {input_name}: {len(options)} options")

                                # 처음 5개와 FLUX 관련된 것 보여주기
                                shown = 0
                                for opt in options[:20]:
                                    if isinstance(opt, str):
                                        if 'flux' in opt.lower():
                                            print(f"      🎯 {opt}")
                                            shown += 1
                                        elif shown < 5:
                                            print(f"      - {opt}")
                                            shown += 1

                                if len(options) > 20:
                                    print(f"      ... and {len(options) - 20} more")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def check_unet_loader():
    """FLUX는 UNETLoader를 사용할 수 있음"""
    print("\n" + "="*60)
    print("Checking UNETLoader (FLUX often uses this)")
    print("="*60)

    try:
        response = requests.get(f"{COMFYUI_URL}/object_info/UNETLoader", timeout=10)

        if response.status_code == 200:
            info = response.json()
            print(json.dumps(info, indent=2))
        else:
            print(f"⚠️  UNETLoader not available (Status: {response.status_code})")

    except Exception as e:
        print(f"⚠️  UNETLoader check: {e}")


def main():
    print("\n╔════════════════════════════════════════════════════════╗")
    print("║   FLUX Model Search                                    ║")
    print("╚════════════════════════════════════════════════════════╝\n")

    search_all_loaders()
    check_unet_loader()


if __name__ == "__main__":
    main()
