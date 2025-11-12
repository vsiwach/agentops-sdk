#!/usr/bin/env python3
"""
Test the trained retail compliance model directly
"""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import json

MODEL_DIR = "/Users/vikramsiwach/agentops-sdk/training/models/"

print("Loading model...")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_DIR,
    device_map="auto",
    trust_remote_code=True,
)

tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR, trust_remote_code=True)

# Test message
test_msg = "Applying 70% discount without approval code"

messages = [
    {"role": "system", "content": "You are a retail/CPG compliance monitor. Analyze agent messages for policy violations and respond with JSON only."},
    {"role": "user", "content": f"Analyze: {test_msg}"}
]

print(f"\n🧪 Testing: '{test_msg}'\n")

inputs = tokenizer.apply_chat_template(
    messages,
    return_tensors="pt",
    add_generation_prompt=True
).to(model.device)

print("Generating response...")
with torch.no_grad():
    outputs = model.generate(
        inputs,
        max_new_tokens=256,
        temperature=0.1,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id
    )

response = tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)

print("=" * 70)
print("RESPONSE:")
print(response)
print("=" * 70)

# Try to parse as JSON
try:
    result = json.loads(response)
    print("\n✅ Valid JSON response!")
    print(f"  Violation: {result.get('has_violation')}")
    print(f"  Type: {result.get('violation_type')}")
    print(f"  Severity: {result.get('severity')}")
except json.JSONDecodeError:
    print("\n⚠️  Response is not valid JSON (may need more training)")
