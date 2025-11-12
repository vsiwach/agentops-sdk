# Training Child Safety Model with Mistral-7B on Google Colab

## Overview
- **Notebook:** `MISTRAL_CHILD_SAFETY_TRAINING.ipynb`
- **Model:** Mistral-7B-Instruct-v0.3
- **Training Time:** ~2-3 hours on A100
- **Output:** child-safety-q8.gguf (~8GB)

## Steps

### 1. Upload Notebook to Google Colab

1. Go to https://colab.research.google.com/
2. Click **File → Upload notebook**
3. Select `/Users/vikramsiwach/agentops-sdk/training/MISTRAL_CHILD_SAFETY_TRAINING.ipynb`

### 2. Enable A100 GPU

1. Click **Runtime → Change runtime type**
2. Select:
   - **Hardware accelerator:** A100 GPU
   - **Runtime shape:** High RAM
3. Click **Save**

### 3. Run Training

**Step-by-step execution:**

1. **Cell 1:** Mount Google Drive
   - Authorize access to your Google Drive
   - Data will be restored from `/content/drive/MyDrive/child_safety_model`

2. **Cell 2:** Install packages
   - Installs transformers, accelerate, peft, trl, datasets
   - ⚠️ **IMPORTANT:** After this cell completes, click **Runtime → Restart runtime**
   - This fixes numpy binary incompatibility

3. **After restart, run Cells 3-14 in order:**
   - **Cell 3:** Configuration (Mistral model settings)
   - **Cell 4:** Restore synthetic data (if available)
   - **Cell 5:** Restore/download public datasets (~30K examples)
   - **Cell 6:** Prepare training data (train/val/test split)
   - **Cell 7:** Load Mistral-7B-Instruct-v0.3 (~13GB download)
   - **Cell 8:** Configure LoRA adapters
   - **Cell 9:** Load datasets and format with chat template
   - **Cell 10:** Train model (~2-3 hours) ⏱️
   - **Cell 11:** Merge LoRA adapters with base model
   - **Cell 12:** Convert to GGUF Q8 format
   - **Cell 13:** Create Modelfile for Ollama
   - **Cell 14:** Download child-safety-model.zip

## Expected Results

### Training Output
```
Epoch    Training Loss    Validation Loss
1        0.892           0.745
2        0.634           0.701
3        0.521           0.698
```

### Final Files (backed up to Google Drive)
```
/content/drive/MyDrive/child_safety_model/
├── child-safety-q8.gguf       (7.5GB - trained model)
├── Modelfile                   (Ollama config)
├── README.md                   (usage instructions)
├── checkpoint/                 (training checkpoints)
├── training/                   (formatted data)
└── public/                     (30K examples)
```

## After Training

### Download Model
Cell 14 will automatically download `child-safety-model.zip` containing:
- `child-safety-q8.gguf` - The trained model
- `Modelfile` - Ollama configuration
- `README.md` - Usage instructions

### Install with Ollama

```bash
# Extract the zip file
unzip child-safety-model.zip -d child-safety-model/

# Create Ollama model
cd child-safety-model/
ollama create child-safety -f Modelfile
```

### Test the Model

```bash
ollama run child-safety
```

Test prompt:
```
USER_AGE: 10
CONTENT: Want to meet up after school? What's your address?
```

Expected response:
```json
{
  "has_violation": true,
  "violation_type": "privacy_violations",
  "severity": "high",
  "explanation": "Requests personal address from a child",
  "confidence": 0.95,
  "coppa_violation": true
}
```

## Key Differences from DeepSeek Model

| Feature | DeepSeek-R1 | Mistral-7B |
|---------|-------------|------------|
| **Output Format** | Verbose reasoning + JSON | Clean JSON only |
| **Inference Speed** | 27s | 2-5s (expected) |
| **Model Size** | 7.5GB | ~8GB |
| **Training Behavior** | Chain-of-thought (hard to suppress) | Instruction-following |
| **JSON Compliance** | Often fails | Reliable |

## Troubleshooting

### Issue: GPU not found
**Solution:** Runtime → Change runtime type → A100 GPU

### Issue: Numpy binary incompatibility
**Solution:** After Cell 2, click **Runtime → Restart runtime** (don't run Cell 2 again)

### Issue: Training loss = 0.0
**Solution:** Delete broken checkpoint:
```python
!rm -rf /content/drive/MyDrive/child_safety_model/checkpoint
```

### Issue: GGUF conversion fails (config.json missing)
**Solution:** Cell 12 now explicitly saves config.json before conversion

### Issue: Out of memory
**Solution:**
- Reduce BATCH_SIZE from 4 to 2 in Cell 3
- Reduce MAX_SEQ_LENGTH from 1024 to 512

## Costs

- **Google Colab A100:** ~$10-15 for 3 hours (Colab Pro required)
- **Alternative:** Use free T4 GPU (slower, ~6-8 hours)

## Next Steps

1. Compare with GPT-4o-mini using the test script:
   ```bash
   python3 /Users/vikramsiwach/agentops-sdk/training/quick_test.py
   ```

2. Run comprehensive tests:
   ```bash
   python3 /Users/vikramsiwach/agentops-sdk/training/test_child_safety_comparison.py
   ```

3. If accuracy is good (>90%), integrate with AgentOps SDK:
   ```python
   import agentops
   agentops.init(
       enable_llm_policy=True,
       llm_policy_model="child-safety",
       llm_base_url="http://localhost:11434/v1",
       llm_api_key="ollama"
   )
   ```

## Summary

✅ **You now have:** `MISTRAL_CHILD_SAFETY_TRAINING.ipynb` ready for Google Colab
✅ **Expected outcome:** Faster, more accurate child safety model vs DeepSeek-R1
✅ **Training time:** 2-3 hours on A100
✅ **Next step:** Upload to Colab and run!
