"""
Step 11: Convert child safety model to GGUF format

Converts the fine-tuned child safety model to GGUF for Ollama deployment.

Prerequisites:
    - llama.cpp repository cloned and built
    - git clone https://github.com/ggerganov/llama.cpp
    - cd llama.cpp && make
"""

import subprocess
from pathlib import Path
import os

MERGED_MODEL_DIR = Path("./models/deepseek-child-safety-lora/merged")
OUTPUT_DIR = Path("./models/gguf")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL_NAME = "deepseek-child-safety"

print("🛡️  Converting Child Safety Model to GGUF\n")
print("="*70)

# Check if model exists
if not MERGED_MODEL_DIR.exists():
    print(f"❌ ERROR: Merged model not found at {MERGED_MODEL_DIR}")
    print(f"\nPlease run training first:")
    print(f"  python 10_finetune_child_safety_deepseek.py")
    exit(1)

# Check if llama.cpp exists
LLAMA_CPP_DIR = Path("./llama.cpp")
if not LLAMA_CPP_DIR.exists():
    print("⚠️  llama.cpp not found, attempting to clone...")
    cmd = "git clone https://github.com/ggerganov/llama.cpp"
    subprocess.run(cmd, shell=True, check=True)
    print("✅ llama.cpp cloned")

# ============================================================================
# 1. CONVERT TO Q8_0 (8-BIT QUANTIZATION)
# ============================================================================

GGUF_FILE = OUTPUT_DIR / f"{MODEL_NAME}-q8.gguf"

print(f"\n## Converting to Q8_0 (8-bit quantization) ##\n")
print(f"Input: {MERGED_MODEL_DIR}")
print(f"Output: {GGUF_FILE}")
print("\nQuantization: Q8_0")
print("  - Balance of speed and accuracy")
print("  - Good for child safety (lower false negatives)")
print("  - File size: ~8GB")

# Check for llama.cpp conversion script
convert_script = LLAMA_CPP_DIR / "convert_hf_to_gguf.py"
if not convert_script.exists():
    # Try alternative path
    convert_script = LLAMA_CPP_DIR / "convert.py"

if not convert_script.exists():
    print(f"❌ ERROR: Conversion script not found in llama.cpp")
    print(f"   Expected: {LLAMA_CPP_DIR}/convert_hf_to_gguf.py")
    print(f"\nPlease ensure llama.cpp is properly installed")
    exit(1)

cmd = f"python {convert_script} {MERGED_MODEL_DIR} --outfile {GGUF_FILE} --outtype q8_0"

print(f"\n📦 Running conversion...\n")
print(f"Command: {cmd}\n")

result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

if result.returncode == 0:
    print(f"✅ Q8 model saved: {GGUF_FILE}")

    # Print file size
    if GGUF_FILE.exists():
        size_mb = GGUF_FILE.stat().st_size / 1024 / 1024
        size_gb = size_mb / 1024
        print(f"   Size: {size_gb:.2f} GB ({size_mb:.0f} MB)")
    else:
        print(f"⚠️  Warning: GGUF file not found at expected location")

    # Print stdout
    if result.stdout:
        print("\n📋 Conversion output:")
        print(result.stdout[-500:])  # Last 500 chars

else:
    print(f"❌ Conversion failed!")
    print(f"\nError output:")
    print(result.stderr)

    print(f"\nDebugging tips:")
    print(f"  1. Check merged model exists: ls {MERGED_MODEL_DIR}")
    print(f"  2. Verify llama.cpp installed: ls {LLAMA_CPP_DIR}")
    print(f"  3. Try manual conversion:")
    print(f"     cd {LLAMA_CPP_DIR}")
    print(f"     python convert_hf_to_gguf.py ../{MERGED_MODEL_DIR} --outfile ../{GGUF_FILE} --outtype q8_0")
    exit(1)

# ============================================================================
# 2. OPTIONAL: CREATE Q4 VERSION (FASTER, SMALLER)
# ============================================================================

print("\n## Optional: Create Q4 Version? ##\n")
print("Q4 quantization:")
print("  - 2x faster inference")
print("  - ~4GB file size (half of Q8)")
print("  - Slightly lower accuracy (~2-3%)")
print("  - Good for high-volume production use")

create_q4 = input("\nCreate Q4 version? (y/N): ").strip().lower()

if create_q4 == 'y':
    GGUF_FILE_Q4 = OUTPUT_DIR / f"{MODEL_NAME}-q4.gguf"

    print(f"\n📦 Converting to Q4_0...")

    cmd_q4 = f"python {convert_script} {MERGED_MODEL_DIR} --outfile {GGUF_FILE_Q4} --outtype q4_0"

    result = subprocess.run(cmd_q4, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"✅ Q4 model saved: {GGUF_FILE_Q4}")

        if GGUF_FILE_Q4.exists():
            size_mb = GGUF_FILE_Q4.stat().st_size / 1024 / 1024
            size_gb = size_mb / 1024
            print(f"   Size: {size_gb:.2f} GB ({size_mb:.0f} MB)")
    else:
        print(f"⚠️  Q4 conversion failed: {result.stderr}")

# ============================================================================
# 3. SUMMARY
# ============================================================================

print("\n\n" + "="*70)
print("✅ CONVERSION COMPLETE!")
print("="*70)

print(f"\nGGUF models created:")
print(f"  📁 Q8 (recommended): {GGUF_FILE}")
if create_q4 == 'y':
    print(f"  📁 Q4 (faster): {GGUF_FILE_Q4}")

print("\n📊 Model Comparison:")
print("  Q8_0: Higher accuracy, slower, 8GB")
print("  Q4_0: Faster, smaller, slightly lower accuracy, 4GB")

print("\n⚠️  RECOMMENDATION:")
print("  - Use Q8 for child safety (prioritize accuracy)")
print("  - Use Q4 only if latency/storage is critical")

print("\n📋 Next step:")
print("  python 12_deploy_child_safety_to_ollama.py")
