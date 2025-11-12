# Fix for DataCollatorForCompletionOnlyLM Import Error

## Quick Fix Option 1: Install Specific TRL Version

**Add this cell at the beginning of your notebook (before other installations):**

```python
# Install specific TRL version that has the class
!pip install -q trl==0.7.11

# Verify
from trl import DataCollatorForCompletionOnlyLM
print("✅ DataCollatorForCompletionOnlyLM available!")
```

## Option 2: Skip Completion-Only Training

If the above doesn't work, **replace the training configuration cell** with this:

```python
# Training arguments
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    num_train_epochs=3,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    lr_scheduler_type="cosine",
    warmup_ratio=0.1,
    logging_steps=10,
    save_strategy="epoch",
    evaluation_strategy="epoch",
    fp16=True,
    gradient_checkpointing=True,
    max_grad_norm=0.3,
    optim="paged_adamw_32bit",
    report_to="none"
)

print("✅ Training configuration ready (standard training mode)")
```

**And replace the trainer creation cell** with:

```python
from trl import SFTTrainer

trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    tokenizer=tokenizer,
    max_seq_length=512,
    dataset_text_field="text",
    # No data_collator - will train on full sequences
)

print("✅ Trainer initialized")
```

## Option 3: Use Alternative Import

**Replace the import section** with:

```python
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    BitsAndBytesConfig,
    DataCollatorForLanguageModeling  # Alternative
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_dataset
from trl import SFTTrainer
```

**Then in the collator section:**

```python
# Use standard language modeling collator
collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False  # Causal LM, not masked LM
)

print("✅ Using DataCollatorForLanguageModeling")
```

## Recommended: Use Option 1

Option 1 is the cleanest - just pin TRL to version 0.7.11 which definitely has the class.

## Why This Happens

The TRL library has been rapidly evolving. `DataCollatorForCompletionOnlyLM` was added in TRL 0.7.0 but may have been moved or renamed in newer versions.

## Impact on Training

- **With DataCollatorForCompletionOnlyLM**: Only trains on assistant responses (more efficient, better quality)
- **Without it**: Trains on full conversation (slightly less efficient but still works fine)

Both approaches will produce a working model!

## Test After Fix

After applying the fix, test with:

```python
# Verify imports work
from trl import SFTTrainer
print("✅ SFTTrainer imported")

# Try the problematic import
try:
    from trl import DataCollatorForCompletionOnlyLM
    print("✅ DataCollatorForCompletionOnlyLM imported")
except ImportError as e:
    print(f"⚠️  Using alternative: {e}")
```
