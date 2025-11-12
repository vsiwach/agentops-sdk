"""
Step 4: Fine-tune DeepSeek-R1-Distill-Qwen-7B for Retail Policy Enforcement

Uses LoRA (Low-Rank Adaptation) for efficient fine-tuning.

Prerequisites:
    pip install transformers datasets peft accelerate bitsandbytes wandb trl torch
"""

import json
import torch
from pathlib import Path
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    BitsAndBytesConfig
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer, DataCollatorForCompletionOnlyLM
import wandb

# Configuration
MODEL_NAME = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"  # HuggingFace model ID
TRAIN_FILE = "./data/training/train.jsonl"
VAL_FILE = "./data/training/val.jsonl"
OUTPUT_DIR = "./models/deepseek-retail-lora"
WANDB_PROJECT = "deepseek-retail-compliance"

# Training hyperparameters
BATCH_SIZE = 4
GRADIENT_ACCUMULATION_STEPS = 4
LEARNING_RATE = 2e-4
NUM_EPOCHS = 3
MAX_SEQ_LENGTH = 512
LORA_R = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0.05

print("🚀 Fine-tuning DeepSeek-R1-Distill-Qwen-7B for Retail Compliance\n")
print("="*70)

# Initialize wandb for experiment tracking
wandb.init(
    project=WANDB_PROJECT,
    config={
        "model": MODEL_NAME,
        "batch_size": BATCH_SIZE,
        "gradient_accumulation": GRADIENT_ACCUMULATION_STEPS,
        "learning_rate": LEARNING_RATE,
        "epochs": NUM_EPOCHS,
        "lora_r": LORA_R,
        "lora_alpha": LORA_ALPHA,
    }
)

# ============================================================================
# 1. LOAD MODEL AND TOKENIZER
# ============================================================================

print("\n## Loading Model ##\n")

# Quantization config for efficient training
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)

print(f"📦 Loading model: {MODEL_NAME}")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True
)

print(f"📦 Loading tokenizer")
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True
)

# Set padding token
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.pad_token_id = tokenizer.eos_token_id

model.config.pad_token_id = tokenizer.pad_token_id

# ============================================================================
# 2. PREPARE MODEL FOR LORA
# ============================================================================

print("\n## Configuring LoRA ##\n")

# Prepare model for k-bit training
model = prepare_model_for_kbit_training(model)

# LoRA configuration
lora_config = LoraConfig(
    r=LORA_R,
    lora_alpha=LORA_ALPHA,
    target_modules=[
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        "gate_proj",
        "up_proj",
        "down_proj"
    ],
    lora_dropout=LORA_DROPOUT,
    bias="none",
    task_type="CAUSAL_LM"
)

# Apply LoRA
model = get_peft_model(model, lora_config)

# Print trainable parameters
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
all_params = sum(p.numel() for p in model.parameters())
print(f"Trainable params: {trainable_params:,} ({100 * trainable_params / all_params:.2f}%)")
print(f"All params: {all_params:,}")

# ============================================================================
# 3. LOAD AND PREPARE DATASET
# ============================================================================

print("\n## Loading Dataset ##\n")

train_dataset = load_dataset("json", data_files=TRAIN_FILE, split="train")
val_dataset = load_dataset("json", data_files=VAL_FILE, split="train")

print(f"Training examples: {len(train_dataset)}")
print(f"Validation examples: {len(val_dataset)}")


def format_chat_template(example):
    """Format examples using chat template."""
    messages = example["messages"]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=False
    )
    return {"text": text}


# Apply formatting
train_dataset = train_dataset.map(format_chat_template)
val_dataset = val_dataset.map(format_chat_template)

# Sample example
print("\n📝 Sample training example:")
print("-" * 70)
print(train_dataset[0]["text"][:500])
print("-" * 70)

# ============================================================================
# 4. TRAINING CONFIGURATION
# ============================================================================

print("\n## Training Configuration ##\n")

training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    num_train_epochs=NUM_EPOCHS,
    per_device_train_batch_size=BATCH_SIZE,
    per_device_eval_batch_size=BATCH_SIZE,
    gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
    learning_rate=LEARNING_RATE,
    lr_scheduler_type="cosine",
    warmup_ratio=0.1,
    logging_steps=10,
    save_strategy="epoch",
    evaluation_strategy="epoch",
    fp16=True,
    push_to_hub=False,
    report_to="wandb",
    gradient_checkpointing=True,
    max_grad_norm=0.3,
    optim="paged_adamw_32bit",
)

# Data collator for completion-only training (only train on assistant responses)
response_template = "<|assistant|>"
collator = DataCollatorForCompletionOnlyLM(
    response_template=response_template,
    tokenizer=tokenizer
)

# ============================================================================
# 5. CREATE TRAINER
# ============================================================================

print("\n## Initializing Trainer ##\n")

trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    tokenizer=tokenizer,
    max_seq_length=MAX_SEQ_LENGTH,
    dataset_text_field="text",
    data_collator=collator,
)

# ============================================================================
# 6. TRAIN
# ============================================================================

print("\n" + "="*70)
print("🎯 Starting Training")
print("="*70 + "\n")

trainer.train()

# ============================================================================
# 7. SAVE MODEL
# ============================================================================

print("\n## Saving Model ##\n")

# Save LoRA adapter
output_path = Path(OUTPUT_DIR)
trainer.model.save_pretrained(output_path)
tokenizer.save_pretrained(output_path)

print(f"✅ Model saved to: {output_path}")

# Also save merged model (optional - takes more space)
print("\n💾 Merging LoRA weights with base model...")
merged_model = model.merge_and_unload()
merged_path = output_path / "merged"
merged_model.save_pretrained(merged_path)
tokenizer.save_pretrained(merged_path)
print(f"✅ Merged model saved to: {merged_path}")

# ============================================================================
# 8. EVALUATION
# ============================================================================

print("\n## Running Evaluation ##\n")

eval_results = trainer.evaluate()
print("📊 Evaluation Results:")
for key, value in eval_results.items():
    print(f"  {key}: {value:.4f}")

wandb.finish()

print("\n" + "="*70)
print("✅ TRAINING COMPLETE!")
print("="*70)
print(f"\nModel saved to: {OUTPUT_DIR}")
print("\nNext steps:")
print("  1. Convert to GGUF: python 5_convert_to_gguf.py")
print("  2. Deploy to Ollama: python 6_deploy_to_ollama.py")
print("  3. Test: python ../examples/retail_agent_demo.py")
