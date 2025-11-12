# Export Model in FP16 Format for Local Use

## Problem
The current model export includes 4-bit quantization config which causes issues when loading on Mac. We need to export in clean FP16 format.

## Solution: Add This Cell to Your Colab Notebook

**Add this as a NEW cell AFTER the training completes (after Step 10):**

```python
# ============================================
# EXPORT CLEAN FP16 MODEL (Compatible Format)
# ============================================

print("🔄 Creating clean FP16 export...\n")

# Step 1: Load base model in FP16
print("1/4 Loading base model...")
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

base_model = AutoModelForCausalLM.from_pretrained(
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
    torch_dtype=torch.float16,
    device_map="auto",
    trust_remote_code=True
)

# Step 2: Load LoRA adapter
print("2/4 Loading LoRA adapter...")
from peft import PeftModel

model_with_lora = PeftModel.from_pretrained(
    base_model,
    OUTPUT_DIR  # This is "./deepseek-retail"
)

# Step 3: Merge LoRA into base model
print("3/4 Merging LoRA weights...")
merged_model = model_with_lora.merge_and_unload()

# Step 4: Save in clean FP16 format
print("4/4 Saving clean FP16 model...")
output_path = "./deepseek-retail-fp16"

merged_model.save_pretrained(
    output_path,
    max_shard_size="5GB",
    safe_serialization=True
)

tokenizer.save_pretrained(output_path)

print(f"\n✅ Clean FP16 model saved to: {output_path}")
print("\nThis format will work on Mac for GGUF conversion!")

# Optional: Verify no quantization config
import json
config_path = f"{output_path}/config.json"
with open(config_path, 'r') as f:
    config = json.load(f)

if 'quantization_config' in config:
    print("⚠️  Removing quantization config...")
    del config['quantization_config']
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    print("✅ Quantization config removed")
else:
    print("✅ No quantization config found (good!)")
```

## Then Download the FP16 Model

**Add this cell to download:**

```python
# Zip the FP16 model
print("📦 Zipping FP16 model...\n")
!zip -r deepseek-retail-fp16.zip {output_path}

print("📥 Downloading...\n")
from google.colab import files
files.download('deepseek-retail-fp16.zip')

print("\n✅ DONE!")
print("\nNext steps on your Mac:")
print("1. unzip deepseek-retail-fp16.zip")
print("2. mv deepseek-retail-fp16 ~/agentops-sdk/training/models/")
print("3. cd ~/agentops-sdk/training")
print("4. Run conversion script")
```

## What This Does

1. ✅ Loads the base DeepSeek model in FP16 (no quantization)
2. ✅ Loads your trained LoRA adapter from `./deepseek-retail`
3. ✅ Merges LoRA weights into the base model
4. ✅ Saves as clean FP16 safetensors (compatible with Mac)
5. ✅ Removes any quantization config from config.json
6. ✅ Downloads the clean model (~15GB)

## After Download

On your Mac:

```bash
# Unzip
unzip deepseek-retail-fp16.zip

# Move to training directory
mv deepseek-retail-fp16 ~/agentops-sdk/training/models_fp16/

# Convert to GGUF
cd ~/agentops-sdk/training/llama.cpp
python3 convert_hf_to_gguf.py \
  ~/agentops-sdk/training/models_fp16/ \
  --outfile ~/agentops-sdk/training/models/deepseek-retail.gguf \
  --outtype q8_0

# Create Ollama model
cd ~/agentops-sdk/training/models
ollama create deepseek-retail -f Modelfile

# Test!
ollama run deepseek-retail "Analyze: Applying 70% discount without approval"
```

## Why This Works

- **No 4-bit quantization** = No mutex lock issues
- **Clean FP16** = Compatible with llama.cpp conversion
- **Merged weights** = Single model file, easier to work with
- **Proper safetensors format** = Works with all tools

## File Size

- **Download**: ~15GB (FP16 is larger than 4-bit)
- **After GGUF conversion**: ~8GB (q8_0 quantization)
- **In Ollama**: ~8GB

The larger download is worth it for compatibility!
