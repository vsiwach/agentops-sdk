# Google Colab Training Guide

## Quick Start (3 steps)

### Step 1: Open the Notebook in Colab

1. Go to https://colab.research.google.com
2. Click **File → Upload notebook**
3. Upload `DeepSeek_Retail_Training_Colab.ipynb` from this directory

**OR** use this direct link (after uploading to GitHub/Drive):
```
https://colab.research.google.com/github/your-repo/agentops-sdk/blob/main/training/DeepSeek_Retail_Training_Colab.ipynb
```

### Step 2: Enable GPU

1. Click **Runtime → Change runtime type**
2. Select **T4 GPU** (free tier) or **L4 GPU** (if you have Colab Pro)
3. Click **Save**

### Step 3: Upload Training Files

When prompted in the notebook, upload these 3 files:
- `data/training/train.jsonl` (2,320 examples)
- `data/training/val.jsonl` (290 examples)
- `data/training/test.jsonl` (290 examples)

Then **Run All Cells** (Runtime → Run all)

---

## Timeline

| Step | Time | What's Happening |
|------|------|------------------|
| Setup | 5 min | Installing packages, loading model |
| Upload | 2 min | Uploading training data |
| Training | 2-3 hours | Fine-tuning with LoRA |
| Evaluation | 5 min | Testing the model |
| Download | 10 min | Downloading fine-tuned model (~4GB) |

**Total:** ~3 hours

---

## What You'll Get

After training completes, you'll download:
- `deepseek-retail-lora.zip` (~4GB)

This contains:
- LoRA adapter (~50MB)
- Merged model (~4GB)
- Tokenizer files

---

## After Download

Once you've downloaded the model from Colab:

```bash
# 1. Unzip the model
unzip deepseek-retail-lora.zip

# 2. Move to training directory
mv deepseek-retail-lora models/

# 3. Convert to GGUF (for Ollama)
python 5_convert_to_gguf.py

# 4. Deploy to Ollama
python 6_deploy_to_ollama.py

# 5. Test it!
export AGENTOPS_RETAIL_MODE=1
cd ..
python examples/retail_agent_demo.py
```

---

## Colab Tips

### Free vs Pro

| Feature | Free | Pro ($10/mo) |
|---------|------|--------------|
| GPU | T4 (16GB) | L4/A100 (24-40GB) |
| Training Time | 3 hours | 1.5 hours |
| Session Limit | 12 hours | 24 hours |
| Recommended | ✅ Yes | Better if available |

**Free tier is perfectly fine for this!**

### Keeping Session Alive

Colab disconnects after ~90 minutes of inactivity. To prevent this:

1. **Option 1**: Keep browser tab active
2. **Option 2**: Use this console trick:
   ```javascript
   // Paste in browser console (F12)
   function KeepAlive(){
       fetch('/session/id').then(r => console.log('Kept alive'));
   }
   setInterval(KeepAlive, 60000);
   ```

### Monitoring Progress

Watch for these checkpoints in the output:
- ✅ Model loaded
- ✅ Training epoch 1/3 complete (save checkpoint)
- ✅ Training epoch 2/3 complete (save checkpoint)
- ✅ Training epoch 3/3 complete (save checkpoint)
- ✅ Evaluation complete
- ✅ Model merged and saved

---

## Troubleshooting

### "Out of Memory" Error

Reduce batch size in the notebook:
```python
per_device_train_batch_size=2,  # Instead of 4
gradient_accumulation_steps=8,  # Instead of 4
```

### "Runtime Disconnected"

Colab sessions have limits. If disconnected:
1. Reconnect (Runtime → Reconnect)
2. Resume from last checkpoint (automatically loaded)

### Slow Upload

Training files are small (~5MB total). If upload is slow:
1. Use wired connection
2. Or mount Google Drive and copy files there first

---

## FAQ

**Q: Can I use Colab free tier?**
A: Yes! T4 GPU is perfect for this. Training takes ~3 hours.

**Q: Do I need to pay for anything?**
A: No, completely free with Colab free tier.

**Q: What if my session times out?**
A: Training saves checkpoints every epoch. You can resume from the last checkpoint.

**Q: Can I close my laptop during training?**
A: No, keep browser tab open or use the keep-alive script above.

**Q: How much does Colab Pro help?**
A: Pro gives L4 GPU (~2x faster) and longer sessions. Not required but nice to have.

**Q: Can I train multiple models?**
A: Yes, but one at a time. Run the notebook multiple times with different data.

---

## Next Steps After Training

1. **Test locally** with the retail demo
2. **Compare** with GPT-4o-mini performance
3. **Deploy to production** via Ollama
4. **Iterate** - collect feedback and retrain with more examples

---

## Support

- Colab Issues: https://research.google.com/colaboratory/faq.html
- Training Issues: Check the notebook outputs and error messages
- Model Issues: See `training/README.md` troubleshooting section

---

## Success Checklist

- [ ] Opened notebook in Colab
- [ ] Enabled T4 GPU runtime
- [ ] Uploaded 3 training files
- [ ] Ran all cells
- [ ] Training completed (3 epochs)
- [ ] Downloaded model zip file (~4GB)
- [ ] Converted to GGUF format
- [ ] Deployed to Ollama
- [ ] Tested with retail demo

**Happy Training! 🚀**
