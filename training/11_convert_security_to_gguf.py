"""
Step 11: Convert security model to GGUF format

Converts the fine-tuned security model to GGUF for Ollama deployment.
"""

import subprocess
from pathlib import Path

MERGED_MODEL_DIR = Path("./models/deepseek-security-lora/merged")
OUTPUT_DIR = Path("./models/gguf")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL_NAME = "deepseek-security"

print("🔄 Converting Security Model to GGUF\n")
print("="*70)

# Q8 quantization for security model (balance of speed and accuracy)
GGUF_FILE = OUTPUT_DIR / f"{MODEL_NAME}-q8.gguf"

print(f"\n## Converting to Q8_0 (8-bit quantization) ##\n")
print(f"Input: {MERGED_MODEL_DIR}")
print(f"Output: {GGUF_FILE}")

cmd = f"python llama.cpp/convert_hf_to_gguf.py {MERGED_MODEL_DIR} --outfile {GGUF_FILE} --outtype q8_0"

print(f"\nRunning: {cmd}\n")
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

if result.returncode == 0:
    print(f"✅ Q8 model saved: {GGUF_FILE}")
    # Print file size
    size_mb = GGUF_FILE.stat().st_size / 1024 / 1024
    print(f"   Size: {size_mb:.2f} MB")
else:
    print(f"❌ Error: {result.stderr}")
    exit(1)

print("\n" + "="*70)
print("✅ CONVERSION COMPLETE!")
print("="*70)
print(f"\nGGUF model: {GGUF_FILE}")
print("\nNext step: python 12_deploy_security_to_ollama.py")
