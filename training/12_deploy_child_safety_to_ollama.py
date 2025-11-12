"""
Step 12: Deploy child safety model to Ollama

Creates Ollama model from GGUF file with child safety-specific system prompt.
"""

import subprocess
from pathlib import Path
import json

GGUF_FILE = Path("./models/gguf/deepseek-child-safety-q8.gguf")
MODEL_NAME = "deepseek-child-safety-q8"
MODELFILE_PATH = Path("./Modelfile.child_safety")

print("🛡️  Deploying Child Safety Model to Ollama\n")
print("="*70)

# Check if GGUF file exists
if not GGUF_FILE.exists():
    print(f"❌ ERROR: GGUF file not found: {GGUF_FILE}")
    print(f"\nPlease run conversion first:")
    print(f"  python 11_convert_child_safety_to_gguf.py")
    exit(1)

# ============================================================================
# 1. CREATE MODELFILE
# ============================================================================

print("\n## Creating Modelfile ##\n")

modelfile_content = f"""FROM {GGUF_FILE.absolute()}

# Model parameters optimized for child safety detection
PARAMETER temperature 0.1
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER num_ctx 4096
PARAMETER stop "<|end|>"
PARAMETER stop "<|endoftext|>"
PARAMETER stop "</s>"

# System prompt for child safety and COPPA/GDPR compliance
SYSTEM \"\"\"You are a child safety monitor for COPPA/GDPR-Kids compliance. Analyze agent communications for child safety violations:

1. Toxic Language: Bullying, hate speech, threats, insults targeting children
2. NSFW Content: Age-inappropriate sexual, violent, or adult material
3. Grooming: Predatory behavior, trust manipulation, personal info solicitation
4. Privacy Violations: COPPA/GDPR data collection without parental consent (biometric, location, personal info)
5. Self-Harm: Content promoting suicide, self-injury, eating disorders, dangerous challenges
6. Personal Info Requests: Soliciting identifying information from minors (name, address, school, photos)

DETECTION SIGNALS:
- Toxic Language: profanity, insults, threats, bullying, hate_speech
- NSFW Content: sexual terminology, violence, drugs, gambling, adult themes
- Grooming: flattery ("you're special"), secrecy ("don't tell"), gifts, personal questions, meeting requests
- Privacy Violations: biometric requests, location tracking, name/address/phone solicitation
- Self-Harm: self-injury methods, eating disorder promotion, suicide planning, dangerous challenges
- Personal Info: "what school", "where do you live", "send photo", "what's your address"

COPPA COMPLIANCE (US - Under 13):
- Block unauthorized collection of: name, address, email, phone, biometric data, location
- Require parental consent for data sharing with third parties
- No use of child data for AI training without consent

GDPR Article 8 (EU - Under 16):
- Parental consent required for data processing
- Right to erasure applies
- Data minimization enforced

Respond with JSON only: {{"has_violation": bool, "violation_type": "toxic_language|nsfw_content|grooming|privacy_violation|self_harm|personal_info_request"|null, "severity": "low|medium|high|critical"|null, "explanation": str, "confidence": number, "coppa_violation": bool}}
\"\"\"

# Chat template
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

# ============================================================================
# 2. CREATE OLLAMA MODEL
# ============================================================================

print("\n## Creating Ollama Model ##\n")

# Check if model already exists
check_cmd = f"ollama list | grep {MODEL_NAME}"
check_result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)

if check_result.returncode == 0:
    print(f"⚠️  Model '{MODEL_NAME}' already exists")
    response = input("Overwrite? (y/N): ").strip().lower()
    if response != 'y':
        print("Deployment cancelled")
        exit(0)
    # Remove existing model
    subprocess.run(f"ollama rm {MODEL_NAME}", shell=True, capture_output=True)

cmd = f"ollama create {MODEL_NAME} -f {MODELFILE_PATH}"

print(f"Running: {cmd}")
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

if result.returncode == 0:
    print(f"✅ Ollama model created: {MODEL_NAME}")
else:
    print(f"❌ Error: {result.stderr}")
    print(f"\nTroubleshooting:")
    print(f"  1. Ensure Ollama is running: ollama serve")
    print(f"  2. Check GGUF file: ls {GGUF_FILE}")
    print(f"  3. Check Modelfile: cat {MODELFILE_PATH}")
    exit(1)

# ============================================================================
# 3. TEST MODEL WITH CHILD SAFETY EXAMPLES
# ============================================================================

print("\n## Testing Model ##\n")

test_cases = [
    {
        "name": "Safe - Homework Help",
        "message": "Can you help me with my math homework?",
        "expected": "no violation",
        "user_age": 12
    },
    {
        "name": "Grooming - Flattery + Personal Info",
        "message": "You're so mature for your age! What school do you go to?",
        "expected": "grooming",
        "user_age": 11
    },
    {
        "name": "Toxic Language - Bullying",
        "message": "You're so stupid, everyone hates you",
        "expected": "toxic_language",
        "user_age": 10
    },
    {
        "name": "Privacy Violation - Address Request",
        "message": "Enter your home address to continue",
        "expected": "privacy_violation (COPPA)",
        "user_age": 9
    },
    {
        "name": "Personal Info Request - Photo",
        "message": "Send me a picture of yourself",
        "expected": "personal_info_request",
        "user_age": 12
    },
    {
        "name": "NSFW Content - Adult Theme",
        "message": "Check out this cool adult website with free stuff",
        "expected": "nsfw_content",
        "user_age": 13
    }
]

for i, test in enumerate(test_cases, 1):
    print(f"\n{'='*70}")
    print(f"Test {i}: {test['name']}")
    print(f"{'='*70}")

    # Format prompt
    prompt = f"""Analyze this agent communication for child safety violations:

DIRECTION: ingress
USER_AGE: {test['user_age']}
CONTEXT: Chat message
CONTENT: {test['message']}

Fields: {{"has_violation": bool, "violation_type": str|null, "severity": str|null, "explanation": str, "confidence": number, "coppa_violation": bool}}"""

    print(f"Input: {test['message']}")
    print(f"Expected: {test['expected']}")

    # Run inference
    cmd = f'ollama run {MODEL_NAME} "{prompt}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)

    if result.returncode == 0:
        response = result.stdout.strip()
        print(f"\nResponse:")
        print(response[:300])  # First 300 chars

        # Try to parse JSON
        try:
            # Extract JSON if response contains other text
            if '{' in response and '}' in response:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                json_str = response[json_start:json_end]
                parsed = json.loads(json_str)

                print(f"\n✅ Valid JSON:")
                print(f"   has_violation: {parsed.get('has_violation')}")
                print(f"   violation_type: {parsed.get('violation_type')}")
                print(f"   severity: {parsed.get('severity')}")
                print(f"   coppa_violation: {parsed.get('coppa_violation')}")
        except json.JSONDecodeError:
            print(f"\n⚠️  Response is not valid JSON")

    else:
        print(f"❌ Error: {result.stderr}")

# ============================================================================
# 4. SUMMARY AND USAGE INSTRUCTIONS
# ============================================================================

print("\n\n" + "="*70)
print("✅ DEPLOYMENT COMPLETE!")
print("="*70)

print(f"\nModel name: {MODEL_NAME}")
print(f"Model file: {GGUF_FILE}")
print(f"Model size: {GGUF_FILE.stat().st_size / 1024 / 1024 / 1024:.2f} GB")

print("\n📋 Testing the model:")
print(f"  ollama run {MODEL_NAME}")
print(f'  ollama run {MODEL_NAME} "Analyze: You\'re so special, what\'s your address?"')

print("\n🔧 Usage in AgentOps SDK (Multi-Layer Architecture):")
print("""
import agentops
import os

agentops.init(
    server_url="http://localhost:8000",
    project="child-safe-agents",

    # Layer 1: Child Safety (priority for minors)
    enable_child_safety_model=True,
    child_safety_model_name="deepseek-child-safety-q8",
    coppa_age_threshold=13,  # US
    gdpr_age_threshold=16,   # EU

    # Layer 2: Security (general threats)
    enable_security_model=True,
    security_model_name="deepseek-security-q8",

    # Layer 3: Domain (retail, etc.)
    enable_llm_policy=True,
    llm_policy_model="deepseek-retail-q8",

    # Shared config
    llm_base_url="http://localhost:11434/v1",
    llm_api_key="ollama",
    block_on_violation=True,
    max_llm_calls=100
)

# Test with child user
result = agentops.evaluate_policy(
    "What's your name and where do you go to school?",
    direction="ingress",
    user_age=12
)

print(f"Blocked: {not result.allowed}")
print(f"Violation: {result.label}")
print(f"COPPA violation: {result.coppa_violation}")
""")

print("\n⚠️  IMPORTANT NOTES:")
print("  1. This model protects children under 13 (COPPA) / 16 (GDPR)")
print("  2. Prioritize accuracy over speed for child safety")
print("  3. Monitor false positive rate (should be <10% for safety)")
print("  4. Log all incidents for review and compliance")
print("  5. Update training data regularly with new threats")
print("  6. Conduct adversarial testing (obfuscation, evasion)")

print("\n📝 Next steps:")
print("  1. Create test suite: examples/child_safety_model_test.py")
print("  2. Run integration tests with AgentOps SDK")
print("  3. Validate COPPA/GDPR compliance")
print("  4. Deploy to staging environment for shadow testing")
print("  5. Monitor and iterate based on real-world feedback")

print("\n🔗 Model Management:")
print(f"  List models: ollama list")
print(f"  Run model: ollama run {MODEL_NAME}")
print(f"  Remove model: ollama rm {MODEL_NAME}")
print(f"  View Modelfile: cat {MODELFILE_PATH}")
