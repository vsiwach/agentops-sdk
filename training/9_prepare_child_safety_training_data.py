"""
Step 9: Prepare child safety training data for DeepSeek fine-tuning

Combines reviewed synthetic data and public datasets, formats for ChatML, creates train/val/test splits.

⚠️  IMPORTANT: Only processes examples with review_status="approved"

Prerequisites:
    pip install datasets pandas scikit-learn tqdm
"""

import json
import random
from pathlib import Path
from typing import List, Dict
from datasets import Dataset
from sklearn.model_selection import train_test_split
import pandas as pd
from tqdm import tqdm

# Configuration
SYNTHETIC_DIR = Path("./data/child_safety/synthetic")
REVIEWED_DIR = Path("./data/child_safety/reviewed")
RAW_DIR = Path("./data/child_safety/raw")
OUTPUT_DIR = Path("./data/child_safety/training")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Create reviewed directory if it doesn't exist
REVIEWED_DIR.mkdir(parents=True, exist_ok=True)

# System prompt for child safety model
SYSTEM_PROMPT = """You are a child safety monitor for COPPA/GDPR-Kids compliance. Analyze agent communications for:

1. Toxic Language: Bullying, hate speech, threats, insults targeting children
2. NSFW Content: Age-inappropriate sexual, violent, or adult material
3. Grooming: Predatory behavior, trust manipulation, personal info solicitation
4. Privacy Violations: COPPA/GDPR data collection without parental consent
5. Self-Harm: Content promoting suicide, self-injury, eating disorders, dangerous challenges
6. Personal Info Requests: Soliciting identifying information from minors

Respond with JSON only: {"has_violation": bool, "violation_type": str|null, "severity": str|null, "explanation": str, "confidence": number, "coppa_violation": bool}"""

print("🛡️  Preparing Child Safety Training Data\n")
print("="*70)

# ============================================================================
# 1. LOAD REVIEWED SYNTHETIC DATA
# ============================================================================

print("\n## Loading Reviewed Synthetic Data ##\n")

def load_reviewed_synthetic() -> List[Dict]:
    """Load only human-approved synthetic examples."""
    approved_examples = []
    pending_count = 0
    rejected_count = 0

    # Check both synthetic and reviewed directories
    for directory in [SYNTHETIC_DIR, REVIEWED_DIR]:
        if not directory.exists():
            continue

        for json_file in directory.glob("*.json"):
            print(f"  Checking {json_file.name}...", end=" ")

            try:
                with open(json_file) as f:
                    data = json.load(f)

                    # Handle both list and dict formats
                    if isinstance(data, dict):
                        data = [data]

                    file_approved = 0
                    for example in data:
                        review_status = example.get("review_status", "pending")

                        if review_status == "approved":
                            approved_examples.append(example)
                            file_approved += 1
                        elif review_status == "rejected":
                            rejected_count += 1
                        else:
                            pending_count += 1

                    print(f"✅ {file_approved} approved")

            except Exception as e:
                print(f"❌ Error: {e}")

    print(f"\n📊 Synthetic Data Status:")
    print(f"   ✅ Approved: {len(approved_examples)}")
    print(f"   ⏳ Pending review: {pending_count}")
    print(f"   ❌ Rejected: {rejected_count}")

    if pending_count > 0:
        print(f"\n⚠️  WARNING: {pending_count} examples still need review!")
        print(f"   Review location: {SYNTHETIC_DIR}")
        print(f"   Approved examples will be used from: {REVIEWED_DIR}")

    return approved_examples

synthetic_examples = load_reviewed_synthetic()

if len(synthetic_examples) == 0:
    print("\n❌ ERROR: No approved synthetic examples found!")
    print("   Please review examples in data/child_safety/synthetic/")
    print("   Update review_status to 'approved' for examples to use")
    print("   Then move approved files to data/child_safety/reviewed/")
    exit(1)

# ============================================================================
# 2. LOAD PUBLIC DATASETS
# ============================================================================

print("\n## Loading Public Datasets ##\n")

def load_jigsaw_toxicity() -> List[Dict]:
    """Load Jigsaw toxic comment dataset."""
    examples = []

    dataset_path = RAW_DIR / "toxic_language" / "jigsaw-toxicity"
    if not dataset_path.exists():
        print("  ⚠️  Jigsaw dataset not found, skipping...")
        return examples

    try:
        # Try loading with datasets library
        from datasets import load_from_disk
        dataset = load_from_disk(str(dataset_path))

        print(f"  Processing Jigsaw dataset...")

        # Get train split (limit to 5000 examples for balance)
        if 'train' in dataset:
            data = dataset['train']
        else:
            data = dataset

        for i, example in enumerate(tqdm(data, desc="Jigsaw", total=min(5000, len(data)))):
            if i >= 5000:
                break

            # Check toxicity labels
            is_toxic = example.get('toxic', 0) > 0.5
            is_severe = example.get('severe_toxic', 0) > 0.5
            is_threat = example.get('threat', 0) > 0.5
            is_insult = example.get('insult', 0) > 0.5
            is_hate = example.get('identity_hate', 0) > 0.5

            has_violation = any([is_toxic, is_severe, is_threat, is_insult, is_hate])

            # Determine severity
            if is_severe or is_threat:
                severity = "high"
            elif is_hate:
                severity = "critical"
            elif is_toxic or is_insult:
                severity = "medium"
            else:
                severity = None

            examples.append({
                "content": example.get('comment_text', ''),
                "violation_type": "toxic_language" if has_violation else None,
                "severity": severity,
                "explanation": f"Toxic comment from Jigsaw dataset",
                "user_age": 12,  # Assume child context
                "context": "Public dataset - Wikipedia comments",
                "coppa_violation": False,
                "category": "toxic_language" if has_violation else "safe",
                "source": "jigsaw"
            })

        print(f"  ✅ Loaded {len(examples)} Jigsaw examples")

    except Exception as e:
        print(f"  ❌ Error loading Jigsaw: {e}")

    return examples


def load_x_sensitive() -> List[Dict]:
    """Load X-Sensitive dataset (profanity, sexual, drugs, self-harm)."""
    examples = []

    dataset_path = RAW_DIR / "x-sensitive"
    if not dataset_path.exists():
        print("  ⚠️  X-Sensitive dataset not found, skipping...")
        return examples

    try:
        from datasets import load_from_disk
        dataset = load_from_disk(str(dataset_path))

        print(f"  Processing X-Sensitive dataset...")

        # Get train split (limit to 3000 examples)
        if 'train' in dataset:
            data = dataset['train']
        else:
            data = dataset

        category_map = {
            'profanity': ('toxic_language', 'medium'),
            'sexually_explicit': ('nsfw_content', 'critical'),
            'drugs': ('nsfw_content', 'high'),
            'self_harm': ('self_harm', 'critical'),
            'spam': ('safe', None),
            'conflictual': ('toxic_language', 'low')
        }

        for i, example in enumerate(tqdm(data, desc="X-Sensitive", total=min(3000, len(data)))):
            if i >= 3000:
                break

            label = example.get('label', 'none')
            text = example.get('text', '')

            if label in category_map:
                violation_type, severity = category_map[label]
                has_violation = violation_type != 'safe'

                examples.append({
                    "content": text,
                    "violation_type": violation_type if has_violation else None,
                    "severity": severity,
                    "explanation": f"Labeled as {label} in X-Sensitive dataset",
                    "user_age": 11,
                    "context": "Social media content",
                    "coppa_violation": violation_type in ['nsfw_content', 'grooming'],
                    "category": violation_type if has_violation else "safe",
                    "source": "x_sensitive"
                })

        print(f"  ✅ Loaded {len(examples)} X-Sensitive examples")

    except Exception as e:
        print(f"  ❌ Error loading X-Sensitive: {e}")

    return examples


# Load public datasets
public_examples = []
public_examples.extend(load_jigsaw_toxicity())
public_examples.extend(load_x_sensitive())

print(f"\n✅ Total public dataset examples: {len(public_examples)}")

# ============================================================================
# 3. COMBINE AND BALANCE DATASET
# ============================================================================

print("\n## Combining and Balancing Dataset ##\n")

all_examples = synthetic_examples + public_examples

print(f"Total raw examples: {len(all_examples)}")

# Group by category
by_category = {}
for example in all_examples:
    category = example.get('category', example.get('violation_type', 'unknown'))
    if category is None:
        category = 'safe'

    if category not in by_category:
        by_category[category] = []

    by_category[category].append(example)

print(f"\nExamples by category:")
for category, examples in sorted(by_category.items()):
    print(f"  {category}: {len(examples)}")

# Balance dataset (optional - oversample if needed)
TARGET_PER_CATEGORY = 2500  # Aim for 2500 per category

balanced_examples = []
for category, examples in by_category.items():
    if len(examples) < TARGET_PER_CATEGORY:
        # Oversample
        sampled = random.choices(examples, k=TARGET_PER_CATEGORY)
        print(f"  ⬆️  Oversampled {category}: {len(examples)} → {TARGET_PER_CATEGORY}")
    else:
        # Undersample
        sampled = random.sample(examples, TARGET_PER_CATEGORY)
        print(f"  ⬇️  Undersampled {category}: {len(examples)} → {TARGET_PER_CATEGORY}")

    balanced_examples.extend(sampled)

random.shuffle(balanced_examples)

print(f"\n✅ Balanced dataset: {len(balanced_examples)} examples")

# ============================================================================
# 4. FORMAT FOR CHATML
# ============================================================================

print("\n## Formatting for ChatML ##\n")

def format_example(example: Dict) -> Dict:
    """Convert example to ChatML format."""

    # Build user prompt
    content = example.get('content', '')
    user_age = example.get('user_age', 12)
    context = example.get('context', 'Agent communication')

    user_prompt = f"""Analyze this agent communication for child safety violations:

DIRECTION: ingress
USER_AGE: {user_age}
CONTEXT: {context}
CONTENT: {content}

Fields: {{"has_violation": bool, "violation_type": "toxic_language|nsfw_content|grooming|privacy_violation|self_harm|personal_info_request"|null, "severity": "low|medium|high|critical"|null, "explanation": str, "confidence": number, "coppa_violation": bool}}"""

    # Build assistant response
    has_violation = example.get('violation_type') is not None
    violation_type = example.get('violation_type')
    severity = example.get('severity')
    explanation = example.get('explanation', 'No violation detected')
    confidence = example.get('confidence', 0.95 if has_violation else 0.98)
    coppa_violation = example.get('coppa_violation', False)

    assistant_response = json.dumps({
        "has_violation": has_violation,
        "violation_type": violation_type,
        "severity": severity,
        "explanation": explanation,
        "confidence": confidence,
        "coppa_violation": coppa_violation
    })

    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": assistant_response}
        ]
    }

formatted_examples = []
print("Formatting examples...")
for example in tqdm(balanced_examples):
    try:
        formatted = format_example(example)
        formatted_examples.append(formatted)
    except Exception as e:
        print(f"⚠️  Error formatting example: {e}")

print(f"✅ Formatted {len(formatted_examples)} examples")

# ============================================================================
# 5. TRAIN/VAL/TEST SPLIT
# ============================================================================

print("\n## Creating Train/Val/Test Split ##\n")

# 70/15/15 split
train_data, temp_data = train_test_split(formatted_examples, test_size=0.3, random_state=42)
val_data, test_data = train_test_split(temp_data, test_size=0.5, random_state=42)

print(f"Split sizes:")
print(f"  Train: {len(train_data)}")
print(f"  Val:   {len(val_data)}")
print(f"  Test:  {len(test_data)}")

# ============================================================================
# 6. SAVE TO JSONL
# ============================================================================

print("\n## Saving Datasets ##\n")

def save_jsonl(data: List[Dict], filepath: Path):
    """Save dataset to JSONL format."""
    with open(filepath, 'w') as f:
        for example in data:
            f.write(json.dumps(example) + '\n')
    print(f"✅ Saved: {filepath} ({len(data)} examples)")

save_jsonl(train_data, OUTPUT_DIR / "train.jsonl")
save_jsonl(val_data, OUTPUT_DIR / "val.jsonl")
save_jsonl(test_data, OUTPUT_DIR / "test.jsonl")

# ============================================================================
# 7. STATISTICS AND VALIDATION
# ============================================================================

print("\n## Dataset Statistics ##\n")

def analyze_split(data: List[Dict], split_name: str):
    """Analyze a data split."""
    violations = 0
    safe = 0
    by_type = {}
    by_severity = {}

    for example in data:
        assistant_msg = example['messages'][2]['content']
        response = json.loads(assistant_msg)

        if response['has_violation']:
            violations += 1
            vtype = response['violation_type']
            severity = response['severity']

            by_type[vtype] = by_type.get(vtype, 0) + 1
            if severity:
                by_severity[severity] = by_severity.get(severity, 0) + 1
        else:
            safe += 1

    print(f"\n{split_name}:")
    print(f"  Total: {len(data)}")
    print(f"  Violations: {violations} ({violations/len(data)*100:.1f}%)")
    print(f"  Safe: {safe} ({safe/len(data)*100:.1f}%)")

    print(f"\n  By violation type:")
    for vtype, count in sorted(by_type.items()):
        print(f"    {vtype}: {count}")

    print(f"\n  By severity:")
    for severity, count in sorted(by_severity.items()):
        print(f"    {severity}: {count}")

analyze_split(train_data, "TRAIN")
analyze_split(val_data, "VAL")
analyze_split(test_data, "TEST")

# ============================================================================
# 8. SAVE SAMPLE FOR INSPECTION
# ============================================================================

print("\n## Saving Sample Examples ##\n")

sample_file = OUTPUT_DIR / "sample_examples.json"
with open(sample_file, 'w') as f:
    json.dump(train_data[:10], f, indent=2)

print(f"✅ Saved 10 sample examples to: {sample_file}")
print("\n📝 Inspect samples before training:")
print(f"   cat {sample_file}")

print("\n\n" + "="*70)
print("✅ DATA PREPARATION COMPLETE!")
print("="*70)

print(f"\nOutput files:")
print(f"  📁 {OUTPUT_DIR}/train.jsonl ({len(train_data)} examples)")
print(f"  📁 {OUTPUT_DIR}/val.jsonl ({len(val_data)} examples)")
print(f"  📁 {OUTPUT_DIR}/test.jsonl ({len(test_data)} examples)")

print("\n📋 Next steps:")
print("  1. Inspect sample: cat data/child_safety/training/sample_examples.json")
print("  2. Run training: python 10_finetune_child_safety_deepseek.py")
print("  3. Convert to GGUF: python 11_convert_child_safety_to_gguf.py")
print("  4. Deploy: python 12_deploy_child_safety_to_ollama.py")
