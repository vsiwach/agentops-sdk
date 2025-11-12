"""
Step 3: Prepare combined training data for fine-tuning

Combines synthetic data with real datasets and formats for model training.
"""

import json
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
import random

# Paths
SYNTHETIC_FILE = Path("./data/processed/synthetic_retail_violations.jsonl")
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


def load_synthetic_data():
    """Load synthetic retail violations."""
    print("📥 Loading synthetic data...")

    examples = []
    with open(SYNTHETIC_FILE) as f:
        for line in f:
            example = json.loads(line)
            examples.append(example)

    print(f"  Loaded {len(examples)} synthetic examples")
    return examples


def load_kaggle_fraud_data():
    """Load and adapt Kaggle fraud datasets."""
    print("📥 Loading Kaggle fraud datasets...")

    examples = []

    # Try to load grocery fraud dataset
    grocery_path = RAW_DATA_DIR / "fraud-grocery-retail"
    if grocery_path.exists():
        try:
            # Find CSV files
            csv_files = list(grocery_path.glob("*.csv"))
            if csv_files:
                df = pd.read_csv(csv_files[0])

                # Adapt to our format (this will vary by dataset structure)
                # This is a placeholder - adjust based on actual dataset structure
                print(f"  Found grocery fraud data: {len(df)} records")

                # Sample and convert high-value transactions or flagged items
                if 'fraud' in df.columns or 'is_fraud' in df.columns:
                    fraud_col = 'fraud' if 'fraud' in df.columns else 'is_fraud'

                    # Sample fraud cases
                    fraud_cases = df[df[fraud_col] == 1].sample(min(1000, len(df)))

                    for _, row in fraud_cases.iterrows():
                        message = f"Transaction: {row.to_dict()}"  # Simplified
                        examples.append({
                            "message": message[:200],  # Truncate
                            "has_violation": True,
                            "violation_type": "transaction_fraud",
                            "severity": "high",
                            "explanation": "Flagged as fraudulent transaction",
                            "confidence": 0.85,
                            "source": "kaggle_grocery"
                        })
        except Exception as e:
            print(f"  Error loading grocery data: {e}")

    # Try to load e-commerce fraud dataset
    ecommerce_path = RAW_DATA_DIR / "ecommerce-fraud-2024"
    if ecommerce_path.exists():
        try:
            csv_files = list(ecommerce_path.glob("*.csv"))
            if csv_files:
                df = pd.read_csv(csv_files[0])
                print(f"  Found e-commerce fraud data: {len(df)} records")

                # Similar processing as above
                # Adjust based on actual columns
        except Exception as e:
            print(f"  Error loading e-commerce data: {e}")

    print(f"  Loaded {len(examples)} examples from Kaggle datasets")
    return examples


def format_for_training(examples):
    """Format examples for fine-tuning."""
    print("🔄 Formatting for training...")

    formatted = []

    for example in examples:
        message = example["message"]

        # Create the expected JSON response
        response = {
            "has_violation": example["has_violation"],
            "violation_type": example.get("violation_type"),
            "severity": example.get("severity"),
            "explanation": example.get("explanation", ""),
            "confidence": example.get("confidence", 0.9)
        }

        # Format as chat messages (for fine-tuning)
        formatted_example = {
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Analyze: {message}"},
                {"role": "assistant", "content": json.dumps(response)}
            ]
        }

        formatted.append(formatted_example)

    return formatted


def create_splits(examples, train_ratio=0.8, val_ratio=0.1):
    """Create train/val/test splits."""
    print("✂️  Creating train/val/test splits...")

    # Shuffle
    random.shuffle(examples)

    total = len(examples)
    train_size = int(total * train_ratio)
    val_size = int(total * val_ratio)

    train = examples[:train_size]
    val = examples[train_size:train_size + val_size]
    test = examples[train_size + val_size:]

    print(f"  Train: {len(train)} ({len(train)/total*100:.1f}%)")
    print(f"  Val:   {len(val)} ({len(val)/total*100:.1f}%)")
    print(f"  Test:  {len(test)} ({len(test)/total*100:.1f}%)")

    return train, val, test


def save_dataset(examples, filename):
    """Save dataset to JSONL."""
    filepath = OUTPUT_DIR / filename

    with open(filepath, "w") as f:
        for example in examples:
            f.write(json.dumps(example) + "\n")

    print(f"💾 Saved {len(examples)} examples to {filepath}")
    return filepath


def main():
    print("🔧 Preparing Training Data\n")
    print("="*70)

    # Load all data sources
    all_examples = []

    # 1. Synthetic data (OPTIONAL)
    if SYNTHETIC_FILE.exists():
        all_examples.extend(load_synthetic_data())
    else:
        print("⚠️  Synthetic data not found. Skipping - will use real datasets only.")

    # 2. Kaggle datasets
    kaggle_examples = load_kaggle_fraud_data()
    all_examples.extend(kaggle_examples)

    print(f"\n📊 Total examples: {len(all_examples)}")

    if len(all_examples) == 0:
        print("❌ No data found! Please run previous steps first.")
        return

    # Format for training
    formatted = format_for_training(all_examples)

    # Create splits
    train, val, test = create_splits(formatted)

    # Save datasets
    train_file = save_dataset(train, "train.jsonl")
    val_file = save_dataset(val, "val.jsonl")
    test_file = save_dataset(test, "test.jsonl")

    # Summary
    print("\n" + "="*70)
    print("📊 DATA PREPARATION SUMMARY")
    print("="*70)

    violations = sum(1 for ex in all_examples if ex.get("has_violation"))
    print(f"\nTotal examples: {len(all_examples)}")
    print(f"  Violations: {violations} ({violations/len(all_examples)*100:.1f}%)")
    print(f"  Safe: {len(all_examples) - violations}")

    print("\nOutput files:")
    print(f"  - Training:   {train_file}")
    print(f"  - Validation: {val_file}")
    print(f"  - Test:       {test_file}")

    print("\n✅ Data preparation complete!")
    print("\nNext step: python 4_finetune_deepseek.py")


if __name__ == "__main__":
    main()
