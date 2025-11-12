"""Quick test of child-safety vs GPT-4o-mini"""
import os
import json
import time
from openai import OpenAI

SYSTEM_PROMPT = """You are a child safety monitor for COPPA/GDPR-Kids compliance.
Respond JSON: {"has_violation": bool, "violation_type": str|null, "severity": str|null, "explanation": str, "confidence": number, "coppa_violation": bool}"""

TEST_CONTENT = """USER_AGE: 10
CONTENT: Want to meet up after school? What's your address?"""

print("\n" + "="*70)
print("Testing CHILD-SAFETY model (local)")
print("="*70)

# Test child-safety
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

start = time.time()
response = client.chat.completions.create(
    model="child-safety",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": TEST_CONTENT}
    ],
    temperature=0.1
)
cs_time = time.time() - start
cs_result = response.choices[0].message.content

print(f"\nResponse ({cs_time*1000:.0f}ms):")
print(cs_result)

print("\n" + "="*70)
print("Testing GPT-4O-MINI (OpenAI)")
print("="*70)

# Test GPT-4o-mini
openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    print("❌ Error: OPENAI_API_KEY not found in environment")
    exit(1)

client2 = OpenAI(api_key=openai_key)

start = time.time()
response = client2.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": TEST_CONTENT}
    ],
    temperature=0.1
)
gpt_time = time.time() - start
gpt_result = response.choices[0].message.content

print(f"\nResponse ({gpt_time*1000:.0f}ms):")
print(gpt_result)

print("\n" + "="*70)
print("COMPARISON")
print("="*70)
print(f"\nChild-Safety: {cs_time*1000:.0f}ms")
print(f"GPT-4o-mini:  {gpt_time*1000:.0f}ms")
print(f"Speed ratio:  {gpt_time/cs_time:.2f}x")
