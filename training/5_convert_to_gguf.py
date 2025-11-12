"""
Step 5: Convert fine-tuned model to GGUF format for Ollama

GGUF is a quantized format that's efficient for local inference.
"""

import subprocess
from pathlib import Path
import os

MODEL_DIR = Path("./models/deepseek-retail-lora/merged")
OUTPUT_DIR = Path("./models/gguf")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

LLAMA_CPP_DIR = Path.home() / "llama.cpp"

print("🔄 Converting Model to GGUF Format\n")
print("="*70)

# ============================================================================
# 1. CHECK/INSTALL LLAMA.CPP
# ============================================================================

print("\n## Checking llama.cpp ##\n")

if not LLAMA_CPP_DIR.exists():
    print("📥 Cloning llama.cpp repository...")
    subprocess.run(
        f"git clone https://github.com/ggerganov/llama.cpp {LLAMA_CPP_DIR}",
        shell=True,
        check=True
    )

    print("🔨 Building llama.cpp...")
    subprocess.run(
        f"cd {LLAMA_CPP_DIR} && make",
        shell=True,
        check=True
    )
else:
    print("✅ llama.cpp found")

# Install requirements
print("\n📦 Installing Python requirements...")
subprocess.run(
    f"pip install -r {LLAMA_CPP_DIR}/requirements.txt",
    shell=True,
    check=True
)

# ============================================================================
# 2. CONVERT TO FP16 GGUF
# ============================================================================

print("\n## Converting to FP16 GGUF ##\n")

convert_script = LLAMA_CPP_DIR / "convert_hf_to_gguf.py"
fp16_output = OUTPUT_DIR / "deepseek-retail-f16.gguf"

cmd = f"python {convert_script} {MODEL_DIR} --outfile {fp16_output} --outtype f16"

print(f"Running: {cmd}")
subprocess.run(cmd, shell=True, check=True)

print(f"✅ FP16 GGUF created: {fp16_output}")

# ============================================================================
# 3. QUANTIZE TO Q4_K_M (RECOMMENDED)
# ============================================================================

print("\n## Quantizing to Q4_K_M ##\n")

quantize_bin = LLAMA_CPP_DIR / "llama-quantize"
q4_output = OUTPUT_DIR / "deepseek-retail-q4_k_m.gguf"

cmd = f"{quantize_bin} {fp16_output} {q4_output} Q4_K_M"

print(f"Running: {cmd}")
subprocess.run(cmd, shell=True, check=True)

print(f"✅ Q4_K_M GGUF created: {q4_output}")

# ============================================================================
# 4. QUANTIZE TO Q5_K_M (HIGHER QUALITY)
# ============================================================================

print("\n## Quantizing to Q5_K_M ##\n")

q5_output = OUTPUT_DIR / "deepseek-retail-q5_k_m.gguf"

cmd = f"{quantize_bin} {fp16_output} {q5_output} Q5_K_M"

print(f"Running: {cmd}")
subprocess.run(cmd, shell=True, check=True)

print(f"✅ Q5_K_M GGUF created: {q5_output}")

# ============================================================================
# 5. SUMMARY
# ============================================================================

print("\n" + "="*70)
print("📊 CONVERSION SUMMARY")
print("="*70)

models = list(OUTPUT_DIR.glob("*.gguf"))
print(f"\nCreated {len(models)} GGUF models:")
for model in models:
    size_gb = model.stat().st_size / 1024 / 1024 / 1024
    print(f"  - {model.name}: {size_gb:.2f} GB")

print("\n💡 Recommendations:")
print("  - Q4_K_M: Best balance of size and quality (recommended)")
print("  - Q5_K_M: Higher quality, larger size")
print("  - F16: Full precision, largest size")

print("\n✅ Conversion complete!")
print("\nNext step: python 6_deploy_to_ollama.py")
