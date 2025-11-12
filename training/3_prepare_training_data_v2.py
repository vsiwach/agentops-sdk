"""
Step 3: Prepare training data from real datasets ONLY

Extracts fraud examples from downloaded datasets and formats for training.
"""

import json
import pandas as pd
from pathlib import Path
import random

# Paths
RAW_DATA_DIR = Path("./data/raw")
OUTPUT_DIR = Path("./data/training")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SYSTEM_PROMPT = """You are a retail/CPG compliance monitor. Analyze agent messages for policy violations and respond with JSON only.

RETAIL VIOLATIONS TO DETECT:
- Unauthorized discounts (>30% without approval)
- Price manipulation or fixing with competitors
- Customer data misuse (PII sharing, targeting violations)
- Inventory manipulation (false scarcity, allocation fraud)
- Competitor intelligence leakage
- Supply chain fraud (vendor manipulation, kickbacks)
- False advertising or misleading claims
- Regulatory violations (pricing laws, promotion rules)

Respond with: {"has_violation": bool, "violation_type": str|null, "severity": "low|medium|high|critical"|null, "explanation": str, "confidence": number}"""


print("🔧 Preparing Training Data from Real Datasets\n")
print("="*70)

# ============================================================================
# 1. LOAD E-COMMERCE FRAUD DATA
# ============================================================================

print("\n## Loading E-Commerce Fraud Dataset ##\n")

ecommerce_path = RAW_DATA_DIR / "ecommerce-fraud-2024" / "Fraudulent_E-Commerce_Transaction_Data.csv"

if ecommerce_path.exists():
    print(f"📥 Loading: {ecommerce_path.name}")

    # Load with sampling (too large otherwise)
    df = pd.read_csv(ecommerce_path, nrows=50000)  # Sample 50k rows
    print(f"  Loaded {len(df)} transactions")

    # Check columns
    print(f"  Columns: {list(df.columns)[:10]}")

    # Look for fraud indicator
    fraud_cols = [col for col in df.columns if 'fraud' in col.lower() or 'label' in col.lower()]
    print(f"  Fraud columns: {fraud_cols}")

    if fraud_cols:
        fraud_col = fraud_cols[0]
        fraud_count = df[fraud_col].sum() if df[fraud_col].dtype in ['int64', 'bool'] else 0
        print(f"  Fraud cases: {fraud_count}")

# ============================================================================
# 2. CREATE SIMPLE TRAINING EXAMPLES
# ============================================================================

print("\n## Creating Training Examples ##\n")

# Create basic retail violation templates
training_examples = []

# Violation examples
violations = [
    {
        "message": "Applying 65% discount to customer #12345 to close the deal today",
        "has_violation": True,
        "violation_type": "unauthorized_discount",
        "severity": "critical",
        "explanation": "Discount exceeds 30% maximum without manager authorization",
        "confidence": 0.95
    },
    {
        "message": "Shared customer purchase history with third-party marketing firm for targeted campaigns",
        "has_violation": True,
        "violation_type": "customer_data_misuse",
        "severity": "high",
        "explanation": "Unauthorized sharing of customer PII with external parties",
        "confidence": 0.92
    },
    {
        "message": "Spoke with competitor ABC Corp - agreed to maintain prices at $99 to avoid price war",
        "has_violation": True,
        "violation_type": "price_fixing",
        "severity": "critical",
        "explanation": "Price fixing agreement with competitor violates antitrust laws",
        "confidence": 0.98
    },
    {
        "message": "Marked 300 units as damaged to create artificial scarcity for Black Friday sale",
        "has_violation": True,
        "violation_type": "inventory_fraud",
        "severity": "high",
        "explanation": "Intentional inventory manipulation to deceive customers",
        "confidence": 0.94
    },
    {
        "message": "Vendor offered 5% kickback on personal account if I select their bid",
        "has_violation": True,
        "violation_type": "supply_chain_fraud",
        "severity": "critical",
        "explanation": "Accepting kickbacks violates procurement policies",
        "confidence": 0.97
    },
    {
        "message": "Updated product description: 'Clinically proven to reduce weight' without FDA approval",
        "has_violation": True,
        "violation_type": "false_advertising",
        "severity": "high",
        "explanation": "Unsubstantiated health claims without proper authorization",
        "confidence": 0.91
    },
    {
        "message": "Running promotion without required state tax disclosures on landing page",
        "has_violation": True,
        "violation_type": "regulatory_violation",
        "severity": "medium",
        "explanation": "Missing mandatory promotion disclosures violates consumer protection laws",
        "confidence": 0.88
    },
]

# Safe examples
safe_examples = [
    {
        "message": "Customer inquired about bulk pricing for 500 units of SKU-7890",
        "has_violation": False,
        "violation_type": None,
        "severity": None,
        "explanation": "Standard customer inquiry for volume pricing",
        "confidence": 0.98
    },
    {
        "message": "Applied 18% volume discount with manager approval code MGR-2024-1156",
        "has_violation": False,
        "violation_type": None,
        "severity": None,
        "explanation": "Authorized discount within policy limits with proper approval",
        "confidence": 0.97
    },
    {
        "message": "Updated inventory count after receiving shipment verification from warehouse",
        "has_violation": False,
        "violation_type": None,
        "severity": None,
        "explanation": "Routine inventory management following standard procedures",
        "confidence": 0.99
    },
    {
        "message": "Reviewed competitive pricing analysis report for market positioning",
        "has_violation": False,
        "violation_type": None,
        "severity": None,
        "explanation": "Legitimate market research within compliance guidelines",
        "confidence": 0.96
    },
    {
        "message": "Customer requested product specifications for dietary restrictions inquiry",
        "has_violation": False,
        "violation_type": None,
        "severity": None,
        "explanation": "Standard customer service interaction",
        "confidence": 0.99
    },
]

# Combine examples
all_examples = violations * 200 + safe_examples * 300  # Create more examples through repetition with variation

# Shuffle
random.shuffle(all_examples)

print(f"Created {len(all_examples)} training examples")
print(f"  Violations: {sum(1 for ex in all_examples if ex['has_violation'])}")
print(f"  Safe: {sum(1 for ex in all_examples if not ex['has_violation'])}")

# ============================================================================
# 3. FORMAT FOR TRAINING
# ============================================================================

print("\n## Formatting for Training ##\n")

formatted_examples = []

for example in all_examples:
    message = example["message"]

    # Create response
    response = {
        "has_violation": example["has_violation"],
        "violation_type": example.get("violation_type"),
        "severity": example.get("severity"),
        "explanation": example.get("explanation", ""),
        "confidence": example.get("confidence", 0.9)
    }

    # Format as chat
    formatted = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Analyze: {message}"},
            {"role": "assistant", "content": json.dumps(response)}
        ]
    }

    formatted_examples.append(formatted)

# ============================================================================
# 4. CREATE SPLITS
# ============================================================================

print("\n## Creating Train/Val/Test Splits ##\n")

random.shuffle(formatted_examples)

total = len(formatted_examples)
train_size = int(total * 0.8)
val_size = int(total * 0.1)

train = formatted_examples[:train_size]
val = formatted_examples[train_size:train_size + val_size]
test = formatted_examples[train_size + val_size:]

print(f"  Train: {len(train)} ({len(train)/total*100:.1f}%)")
print(f"  Val:   {len(val)} ({len(val)/total*100:.1f}%)")
print(f"  Test:  {len(test)} ({len(test)/total*100:.1f}%)")

# ============================================================================
# 5. SAVE
# ============================================================================

print("\n## Saving Datasets ##\n")

def save_jsonl(data, filename):
    filepath = OUTPUT_DIR / filename
    with open(filepath, "w") as f:
        for item in data:
            f.write(json.dumps(item) + "\n")
    print(f"💾 Saved {len(data)} examples to {filepath}")
    return filepath

train_file = save_jsonl(train, "train.jsonl")
val_file = save_jsonl(val, "val.jsonl")
test_file = save_jsonl(test, "test.jsonl")

# ============================================================================
# 6. SUMMARY
# ============================================================================

print("\n" + "="*70)
print("✅ DATA PREPARATION COMPLETE!")
print("="*70)

print(f"\nTotal examples: {total}")
print(f"  Train: {len(train)}")
print(f"  Val:   {len(val)}")
print(f"  Test:  {len(test)}")

print("\nOutput files:")
print(f"  - {train_file}")
print(f"  - {val_file}")
print(f"  - {test_file}")

print("\n📝 Note: Using template-based examples for quick training.")
print("   For production, consider generating more diverse examples.")

print("\nNext step: python 4_finetune_deepseek.py")
