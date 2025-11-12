# Training Security Model on Google Colab

## Why Colab?

**GPU Requirements:**
- Fine-tuning 7B model requires **16GB+ GPU RAM**
- Local training: RTX 3090/4090 (~$1500+) or A100 rental ($2-3/hour)
- **Colab Free tier:** T4 GPU (16GB) - **FREE**
- **Colab Pro:** A100 GPU (40GB) - $10/month (faster training)

**Training Time:**
- Colab T4 (free): ~6-8 hours
- Colab A100 (Pro): ~2-3 hours
- Local RTX 4090: ~4-5 hours

**Cost Comparison:**
| Option | GPU | Cost | Time |
|--------|-----|------|------|
| **Colab Free** | T4 | $0 | 6-8h |
| **Colab Pro** | A100 | $10/month | 2-3h |
| Local GPU | RTX 4090 | $1500+ | 4-5h |
| Cloud GPU Rental | A100 | $2-3/hour | 3h = $6-9 |

**Recommendation:** Use **Colab Pro** ($10) for fastest training with A100.

---

## Setup Instructions

### 1. Open Notebook in Colab

**Option A: Upload from local**
1. Go to https://colab.research.google.com
2. File → Upload notebook
3. Select `training/DeepSeek_Security_Training_Colab.ipynb`

**Option B: Open from GitHub**
1. Go to https://colab.research.google.com
2. File → Open notebook → GitHub tab
3. Enter: `your-repo-url/training/DeepSeek_Security_Training_Colab.ipynb`

### 2. Enable GPU

1. Runtime → Change runtime type
2. Hardware accelerator: **GPU**
3. GPU type:
   - Free tier: **T4** (auto-selected)
   - Colab Pro: **A100** (recommended)
4. Click Save

**Verify GPU:**
```python
!nvidia-smi
```
Should show T4 or A100.

### 3. Set API Keys

**Method 1: Colab Secrets (Recommended)**

1. Click 🔑 icon in left sidebar (Secrets)
2. Add two secrets:
   - Name: `OPENAI_API_KEY`, Value: `sk-...` (required)
   - Name: `WANDB_API_KEY`, Value: `...` (optional - for tracking)
3. Enable notebook access for both

**Method 2: Manual (Less Secure)**

In the notebook, uncomment and edit:
```python
os.environ["OPENAI_API_KEY"] = "sk-..."
os.environ["WANDB_API_KEY"] = "..."  # optional
```

### 4. Mount Google Drive

The notebook will prompt you to authorize Google Drive access. This saves your trained model to Drive so you can download it later.

Your model will be saved to: `MyDrive/deepseek-security-model/`

---

## Running the Training

### Step-by-Step Execution

**Run cells in order:**

1. **Setup Environment** (~3 min)
   - Installs dependencies
   - Checks GPU
   - Loads API keys

2. **Download Datasets** (~5 min)
   - Downloads HuggingFace datasets
   - ~500MB total

3. **Generate Synthetic Data** (~30-45 min)
   - Generates 5,000 examples (reduced from 20K for Colab)
   - Uses GPT-4o-mini
   - Cost: ~$2-3 in OpenAI credits

4. **Prepare Training Data** (~2 min)
   - Formats to ChatML
   - Creates train/val/test splits

5. **Fine-tune Model** (~2-8 hours depending on GPU)
   - **T4 (free):** 6-8 hours
   - **A100 (Pro):** 2-3 hours
   - Uses 4-bit quantization + LoRA
   - Saves checkpoints every epoch

6. **Save & Download** (~5 min)
   - Merges LoRA weights
   - Copies to Google Drive
   - ~4GB total

### Monitor Training

**In Notebook:**
- Watch loss decrease in output
- Check validation metrics every epoch

**WandB (Optional):**
- View training curves at https://wandb.ai
- Track experiments
- Compare runs

---

## Colab-Specific Optimizations

### Reduced Dataset Size

To fit within Colab's time limits, the notebook generates:
- **1,000 examples per category** (vs 3,750 in full version)
- **Total: 5,000 examples** (vs 20,000)
- **Training time: 2-8 hours** (vs 4-5 hours full)

**For production:** Use full dataset on local GPU or cloud instance.

### Memory Optimization

```python
# Smaller batch size for Colab
BATCH_SIZE = 2  # vs 4 on local
GRADIENT_ACCUMULATION = 8  # Effective batch = 16

# 4-bit quantization (uses ~6GB VRAM)
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4"
)
```

### Session Management

**Colab disconnects after 12 hours (free) or 24 hours (Pro)**

**To avoid losing progress:**
1. Training saves checkpoints every epoch to Drive
2. If disconnected, resume from last checkpoint:
   ```python
   trainer.train(resume_from_checkpoint=True)
   ```

**Keep session alive:**
- Press Ctrl+Shift+I → Console → Paste:
  ```javascript
  function KeepClicking(){
    console.log("Clicking");
    document.querySelector("colab-connect-button").click()
  }
  setInterval(KeepClicking,60000)
  ```

---

## Download Trained Model

### After Training Completes

1. **In Colab:** Model is saved to `/content/drive/MyDrive/deepseek-security-model/`

2. **In Google Drive:**
   - Open https://drive.google.com
   - Navigate to `My Drive/deepseek-security-model/`
   - Right-click folder → Download
   - Will download as ZIP (~4GB)

3. **On Local Machine:**
   ```bash
   # Extract download
   unzip deepseek-security-model.zip

   # Copy to training directory
   cp -r deepseek-security-model ~/agentops-sdk/training/models/deepseek-security-lora/

   # Convert to GGUF
   cd ~/agentops-sdk/training
   python 11_convert_security_to_gguf.py

   # Deploy to Ollama
   python 12_deploy_security_to_ollama.py
   ```

---

## Troubleshooting

### "CUDA out of memory"

**Solution 1: Reduce batch size**
```python
BATCH_SIZE = 1  # Smallest possible
GRADIENT_ACCUMULATION = 16  # Maintain effective batch
```

**Solution 2: Reduce sequence length**
```python
MAX_SEQ_LENGTH = 512  # vs 1024
```

**Solution 3: Use Colab Pro** (A100 has 40GB vs T4's 16GB)

### "Colab disconnected"

**If mid-training:**
1. Re-run notebook
2. Skip data generation cells (already in Drive)
3. Resume training:
   ```python
   trainer.train(resume_from_checkpoint=True)
   ```

**Prevention:**
- Use Colab Pro (longer sessions)
- Run JavaScript keep-alive (see above)

### "OpenAI API rate limit"

**During synthetic generation:**
```python
# Already included: time.sleep(1) between batches
# If still hitting limits, increase delay:
time.sleep(2)  # or 3
```

**Or reduce examples:**
```python
EXAMPLES_PER_CATEGORY = 500  # vs 1000
```

### "Model not saved to Drive"

**Check mount:**
```python
from google.colab import drive
drive.mount('/content/drive', force_remount=True)
```

**Manual copy:**
```python
!cp -r /content/deepseek-security-lora /content/drive/MyDrive/
```

---

## Cost Breakdown

### Total Costs

| Item | Cost |
|------|------|
| **Colab Pro** (optional) | $10/month |
| **OpenAI API** (synthetic data) | $2-3 |
| **WandB** (optional tracking) | Free tier |
| **Total minimum** | **$2-3** |
| **Total with Pro** | **$12-13** |

**Compare to:**
- Cloud GPU rental (3 hours): $6-9
- Local GPU purchase: $1500+

---

## Alternative: Local Training

If you have a GPU (16GB+ VRAM), run locally instead:

```bash
cd ~/agentops-sdk/training

# Download datasets
python 7_download_security_datasets.py

# Generate synthetic data
export OPENAI_API_KEY=sk-...
python 8_generate_security_synthetic.py

# Prepare data
python 9_prepare_security_training_data.py

# Train (4-5 hours on RTX 4090)
python 10_finetune_security_deepseek.py

# Convert & deploy
python 11_convert_security_to_gguf.py
python 12_deploy_security_to_ollama.py
```

**Pros:**
- No time limits
- Full dataset (20K examples)
- No Colab disconnects

**Cons:**
- Requires expensive GPU
- Uses local disk space
- Ties up machine for hours

---

## Next Steps After Training

Once you have the trained model:

1. **Convert to GGUF** (on local machine with `llama.cpp`)
2. **Deploy to Ollama** (`deepseek-security-q8`)
3. **Test security model:** `python examples/security_model_test.py`
4. **Compare performance:** Run comparison against GPT-4o-mini
5. **Integrate multi-layer:** Enable both security + retail models
6. **Deploy to production:** Shadow mode → full rollout

---

## FAQ

**Q: Can I use Colab free tier?**
A: Yes, but training takes 6-8 hours. Colab Pro (A100) is recommended for 2-3 hour training.

**Q: Will Colab disconnect during training?**
A: Free tier disconnects after 12 hours of inactivity. Training should complete in 6-8 hours. Use JavaScript keep-alive script to prevent early disconnect.

**Q: What if I run out of OpenAI credits?**
A: Synthetic data generation costs ~$2-3. Add $5-10 to your OpenAI account before starting.

**Q: Can I train with fewer examples?**
A: Yes, reduce `EXAMPLES_PER_CATEGORY` to 500 or 250. Training will be faster but accuracy may drop.

**Q: How do I resume if Colab crashes?**
A: Re-run notebook, skip data generation, use `trainer.train(resume_from_checkpoint=True)`.

**Q: Can I use this for the retail model too?**
A: Yes! Adapt the notebook for retail by changing dataset generation prompts to retail violations instead of security violations.

---

**Ready to train?** Open `DeepSeek_Security_Training_Colab.ipynb` in Colab and follow the steps!
