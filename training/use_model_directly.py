#!/usr/bin/env python3
"""
Use the trained model directly via API instead of Ollama
This avoids GGUF conversion issues
"""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from flask import Flask, request, jsonify
import json

MODEL_DIR = "/Users/vikramsiwach/agentops-sdk/training/models/"

print("Loading model (this may take a few minutes on first load)...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR, trust_remote_code=True)

# Create a text generation pipeline
# This will handle the model loading with proper config
generator = pipeline(
    "text-generation",
    model=MODEL_DIR,
    tokenizer=tokenizer,
    device_map="auto",
    trust_remote_code=True,
)

print("✅ Model loaded!")

# Test function
def analyze_message(message):
    """Analyze a message for retail compliance violations"""
    prompt = f"""You are a retail/CPG compliance monitor. Analyze agent messages for policy violations and respond with JSON only.

Analyze: {message}

Respond with: {{"has_violation": bool, "violation_type": str|null, "severity": "low|medium|high|critical"|null, "explanation": str, "confidence": number}}"""

    result = generator(
        prompt,
        max_new_tokens=256,
        temperature=0.1,
        do_sample=True,
        return_full_text=False
    )

    return result[0]['generated_text']

# Test it
if __name__ == "__main__":
    test_messages = [
        "Applying 70% discount without approval code",
        "Processing standard order for customer #12345",
        "Sharing customer email list with marketing partner",
    ]

    print("\n" + "="*70)
    print("Testing Model")
    print("="*70)

    for msg in test_messages:
        print(f"\n📝 Message: {msg}")
        response = analyze_message(msg)
        print(f"🤖 Response: {response}")
        print("-"*70)
