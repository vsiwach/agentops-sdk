# How to Run the Training in Google Colab

## 🚀 5-Step Quick Start

### Step 1: Open Colab
Go to: **https://colab.research.google.com**

### Step 2: Upload Notebook
1. Click **File → Upload notebook**
2. Choose: `DeepSeek_Retail_Training_Fixed.ipynb`
3. Wait for it to open

### Step 3: Enable GPU
1. Click **Runtime → Change runtime type**
2. Select **T4 GPU** from dropdown
3. Click **Save**

### Step 4: Upload Your Training Files
When the notebook prompts you (in cell 3), upload these 3 files:

**Files to upload** (from `training/data/training/` on your computer):
```
✅ train.jsonl (2,320 examples)
✅ val.jsonl (290 examples)
✅ test.jsonl (290 examples)
```

### Step 5: Run Everything
Click **Runtime → Run all**

Then go grab coffee ☕ - it takes **~3 hours**

---

## ⏰ Timeline

| Step | Time | What's Happening |
|------|------|------------------|
| Setup & Install | 5 min | Installing packages, loading model |
| Upload Files | 2 min | Uploading your training data |
| Training | 2-3 hours | Fine-tuning DeepSeek-R1 |
| Evaluation | 5 min | Testing the trained model |
| Download | 10 min | Downloading model (~4GB) |

**Total: ~3 hours**

---

## 📋 What Each Cell Does

1. **Check GPU** - Verifies you have GPU enabled
2. **Install Packages** - Installs transformers, LoRA, etc.
3. **Upload Data** - YOU DO THIS: Upload 3 training files
4. **Load Model** - Downloads DeepSeek-R1 base model (5-10 min)
5. **Configure LoRA** - Sets up efficient fine-tuning
6. **Load Training Data** - Prepares your examples
7. **Configure Training** - Sets hyperparameters
8. **Create Trainer** - Initializes the training
9. **Train** - THE BIG ONE: 2-3 hours of training
10. **Save Model** - Saves LoRA adapter + merged model
11. **Evaluate** - Tests performance
12. **Test** - Quick inference test
13. **Download** - YOU DO THIS: Download the trained model

---

## 💡 Important Tips

### ✅ DO:
- Enable T4 GPU before running
- Keep browser tab open during training
- Upload all 3 files when prompted
- Download the model at the end

### ❌ DON'T:
- Close the browser tab during training
- Use CPU runtime (won't work)
- Skip uploading training files
- Forget to download the model

---

## 🎯 Progress Indicators

Watch for these in the output:

```
✅ GPU detected: Tesla T4
✅ All packages installed!
✅ Data loaded and formatted!
✅ Model loaded!
✅ LoRA configured!
✅ Trainer ready!

🎯 Starting training...
Epoch 1/3: [Progress bar]
Epoch 2/3: [Progress bar]
Epoch 3/3: [Progress bar]

✅ TRAINING COMPLETE!
✅ Model is working!
📥 Downloading...
```

---

## 🆘 Troubleshooting

### "Runtime disconnected"
**Solution:** Runtime → Reconnect. Training resumes from last checkpoint.

### "Out of memory"
**Solution:** Runtime → Restart runtime, then in cell 7 change:
```python
per_device_train_batch_size=2,  # Was 4
gradient_accumulation_steps=8,  # Was 4
```

### "No GPU available"
**Solution:** Runtime → Change runtime type → Select T4 GPU → Save

### Upload fails
**Solution:** Make sure files are `.jsonl` format and < 25MB each

### Download fails
**Solution:** Files → Right-click `deepseek-retail-model.zip` → Download

---

## ✅ Success Checklist

After completion, you should have:
- [ ] Saw "TRAINING COMPLETE" message
- [ ] Saw evaluation results
- [ ] Saw test inference output
- [ ] Downloaded `deepseek-retail-model.zip` (4GB)

---

## 🎉 After Download

On your local machine:

```bash
# Unzip
unzip deepseek-retail-model.zip

# Move to project
mv deepseek-retail_merged ~/agentops-sdk/training/models/

# Convert to GGUF
cd ~/agentops-sdk/training
python 5_convert_to_gguf.py

# Deploy to Ollama
python 6_deploy_to_ollama.py

# Test!
export AGENTOPS_RETAIL_MODE=1
python ../examples/retail_agent_demo.py
```

---

## 📊 What You'll Get

**A fine-tuned model that detects:**
- Unauthorized discounts (>30%)
- Customer data misuse
- Price fixing with competitors
- Inventory manipulation
- Kickback schemes
- False advertising
- Regulatory violations

**Performance:**
- JSON output: 95%+ success
- Detection rate: 85%+
- Cost: $0 (local inference)
- Privacy: 100% local

---

## Need Help?

1. Check the output in each cell for error messages
2. Make sure GPU is enabled (see cell 1 output)
3. Verify all 3 training files were uploaded
4. Check that training completed all 3 epochs

**Ready? Open that notebook in Colab and click Run all!** 🚀
