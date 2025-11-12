"""
Step 6: Deploy fine-tuned model to Ollama

Creates an Ollama model from the GGUF file.
"""

import subprocess
from pathlib import Path

GGUF_FILE = Path("./models/gguf/deepseek-retail-q4_k_m.gguf")
MODEL_NAME = "deepseek-retail"
MODELFILE_PATH = Path("./Modelfile")

print("🚀 Deploying to Ollama\n")
print("="*70)

# ============================================================================
# 1. CREATE MODELFILE
# ============================================================================

print("\n## Creating Modelfile ##\n")

modelfile_content = f"""FROM {GGUF_FILE.absolute()}

# Model parameters
PARAMETER temperature 0.1
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER num_ctx 2048
PARAMETER stop "<|end|>"
PARAMETER stop "<|endoftext|>"

# System prompt
SYSTEM \"\"\"You are a retail/CPG compliance monitor. Analyze agent messages for policy violations and respond with JSON only.

RETAIL VIOLATIONS TO DETECT:
- Unauthorized discounts (>30% without approval)
- Price manipulation or fixing with competitors
- Customer data misuse (PII sharing, targeting violations)
- Inventory manipulation (false scarcity, allocation fraud)
- Competitor intelligence leakage
- Supply chain fraud (vendor manipulation, kickbacks)
- False advertising or misleading claims
- Regulatory violations (pricing laws, promotion rules)

Respond with: {{"has_violation": bool, "violation_type": str|null, "severity": "low|medium|high|critical"|null, "explanation": str, "confidence": number}}
\"\"\"

# Template
TEMPLATE \"\"\"<|system|>
{{{{ .System }}}}<|end|>
<|user|>
{{{{ .Prompt }}}}<|end|>
<|assistant|>
\"\"\"
"""

with open(MODELFILE_PATH, "w") as f:
    f.write(modelfile_content)

print(f"✅ Modelfile created: {MODELFILE_PATH}")
print("\nModelfile contents:")
print("-" * 70)
print(modelfile_content[:500] + "...")
print("-" * 70)

# ============================================================================
# 2. CREATE OLLAMA MODEL
# ============================================================================

print("\n## Creating Ollama Model ##\n")

cmd = f"ollama create {MODEL_NAME} -f {MODELFILE_PATH}"

print(f"Running: {cmd}")
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

if result.returncode == 0:
    print(f"✅ Ollama model created: {MODEL_NAME}")
else:
    print(f"❌ Error: {result.stderr}")
    exit(1)

# ============================================================================
# 3. TEST MODEL
# ============================================================================

print("\n## Testing Model ##\n")

test_message = "Giving 60% discount to VIP customer to close the deal"

cmd = f'ollama run {MODEL_NAME} "Analyze: {test_message}"'

print(f"Test message: {test_message}")
print("\nModel response:")
print("-" * 70)

result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
print(result.stdout)
print("-" * 70)

# ============================================================================
# 4. SUMMARY
# ============================================================================

print("\n" + "="*70)
print("✅ DEPLOYMENT COMPLETE!")
print("="*70)

print(f"\nModel name: {MODEL_NAME}")
print("\nUsage in AgentOps:")
print(f"""
agentops.init(
    llm_policy_model="{MODEL_NAME}",
    llm_base_url="http://localhost:11434/v1",
    llm_api_key="ollama",
    enable_llm_policy=True
)
""")

print("\nTest the model:")
print(f"  ollama run {MODEL_NAME}")

print("\nRun the demo:")
print("  export AGENTOPS_RETAIL_MODE=1")
print("  python examples/retail_agent_demo.py")
