#!/usr/bin/env python3
"""
Dequantize the 4-bit model to FP16 for GGUF conversion
"""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import json

MODEL_DIR = "/Users/vikramsiwach/agentops-sdk/training/models/"
OUTPUT_DIR = "/Users/vikramsiwach/agentops-sdk/training/models_fp16/"

print("Loading 4-bit model...")
# Load the model with bitsandbytes quantization first
model = AutoModelForCausalLM.from_pretrained(
    MODEL_DIR,
    device_map="auto",
    torch_dtype=torch.float16,
    trust_remote_code=True,
)

tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR, trust_remote_code=True)

print("Saving dequantized model...")
model.save_pretrained(OUTPUT_DIR, max_shard_size="5GB")
tokenizer.save_pretrained(OUTPUT_DIR)

# Remove quantization config
config_path = f"{OUTPUT_DIR}/config.json"
with open(config_path, 'r') as f:
    config = json.load(f)

if 'quantization_config' in config:
    del config['quantization_config']

with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)

print(f"✅ Dequantized model saved to: {OUTPUT_DIR}")
