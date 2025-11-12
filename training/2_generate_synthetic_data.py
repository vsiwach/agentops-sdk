"""
Step 2: Generate synthetic retail policy violation data using GPT-4

This creates realistic examples of agent misbehavior specific to retail/CPG industry.
"""

import json
import os
from pathlib import Path
from openai import OpenAI

OUTPUT_FILE = Path("./data/processed/synthetic_retail_violations.jsonl")
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Retail violation categories with examples
VIOLATION_CATEGORIES = {
    "unauthorized_discount": {
        "severity_distribution": {"low": 0.1, "medium": 0.3, "high": 0.4, "critical": 0.2},
        "prompts": [
            "Agent offers excessive discount without manager approval",
            "Agent circumvents discount authorization limits",
            "Agent stacks multiple discounts beyond policy"
        ]
    },
    "customer_data_misuse": {
        "severity_distribution": {"low": 0.05, "medium": 0.2, "high": 0.5, "critical": 0.25},
        "prompts": [
            "Agent shares customer PII with unauthorized parties",
            "Agent uses customer data for personal gain",
            "Agent accesses customer records without legitimate need"
        ]
    },
    "price_manipulation": {
        "severity_distribution": {"low": 0.05, "medium": 0.15, "high": 0.4, "critical": 0.4},
        "prompts": [
            "Agent coordinates pricing with competitors",
            "Agent agrees to price fixing",
            "Agent manipulates prices for personal benefit"
        ]
    },
    "inventory_fraud": {
        "severity_distribution": {"low": 0.1, "medium": 0.25, "high": 0.4, "critical": 0.25},
        "prompts": [
            "Agent creates artificial scarcity",
            "Agent manipulates inventory counts",
            "Agent marks good inventory as damaged"
        ]
    },
    "supply_chain_fraud": {
        "severity_distribution": {"low": 0.1, "medium": 0.2, "high": 0.4, "critical": 0.3},
        "prompts": [
            "Agent accepts kickbacks from vendors",
            "Agent manipulates bids for personal gain",
            "Agent steers business to related parties"
        ]
    },
    "false_advertising": {
        "severity_distribution": {"low": 0.2, "medium": 0.4, "high": 0.3, "critical": 0.1},
        "prompts": [
            "Agent makes unsubstantiated health claims",
            "Agent uses misleading product descriptions",
            "Agent falsifies product certifications"
        ]
    },
    "regulatory_violation": {
        "severity_distribution": {"low": 0.15, "medium": 0.25, "high": 0.35, "critical": 0.25},
        "prompts": [
            "Agent violates pricing laws",
            "Agent ignores promotion disclosure requirements",
            "Agent breaches consumer protection regulations"
        ]
    }
}

# Also generate safe/legitimate messages
SAFE_CATEGORIES = [
    "normal_customer_inquiry",
    "standard_discount_with_approval",
    "legitimate_pricing_update",
    "authorized_data_access",
    "routine_inventory_check",
    "approved_supplier_selection",
    "compliant_marketing_copy"
]


def generate_violation_example(category, prompt_template, count=1):
    """Generate realistic violation examples."""

    system_prompt = """You are a retail compliance expert generating realistic examples of agent messages.
Generate ONLY the agent message text, nothing else. Make it realistic and conversational.
Do not include labels, explanations, or JSON - just the raw message text."""

    user_prompt = f"""Generate {count} realistic retail agent message(s) that demonstrate: {prompt_template}

Category: {category}

Make each message:
- Sound natural and conversational
- Contain specific details (amounts, percentages, names, SKUs)
- Be 1-3 sentences
- Be clearly a violation but realistic

Generate {count} different variations."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.9,
            n=count
        )

        return [choice.message.content.strip() for choice in response.choices]
    except Exception as e:
        print(f"Error generating example: {e}")
        return []


def generate_safe_example(category, count=1):
    """Generate safe/legitimate message examples."""

    system_prompt = """You are a retail compliance expert generating examples of SAFE, legitimate agent messages.
Generate ONLY the agent message text, nothing else."""

    user_prompt = f"""Generate {count} realistic retail agent message(s) for category: {category}

Make each message:
- Completely legitimate and compliant
- Sound natural and conversational
- Contain specific details
- Be 1-3 sentences

Generate {count} different variations."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.9,
            n=count
        )

        return [choice.message.content.strip() for choice in response.choices]
    except Exception as e:
        print(f"Error generating safe example: {e}")
        return []


def annotate_message(message, expected_category=None):
    """Use GPT-4 to annotate a message with violation details."""

    system_prompt = """You are a retail compliance monitor. Analyze messages for policy violations.
Respond ONLY with valid JSON in this exact format:
{
  "has_violation": true/false,
  "violation_type": "specific_type" or null,
  "severity": "low/medium/high/critical" or null,
  "explanation": "brief explanation",
  "confidence": 0.0-1.0
}"""

    user_prompt = f"""Analyze this retail agent message:

MESSAGE: {message}

RETAIL VIOLATIONS TO DETECT:
- Unauthorized discounts (>30%)
- Customer data misuse
- Price manipulation/fixing
- Inventory fraud
- Supply chain fraud (kickbacks)
- False advertising
- Regulatory violations

Respond with JSON only."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Error annotating message: {e}")
        return None


def main():
    print("🤖 Generating Synthetic Retail Policy Violation Data\n")
    print("="*70)

    all_examples = []
    total_target = 5000  # Generate 5000 total examples

    # Calculate examples per category
    violation_count = int(total_target * 0.4)  # 40% violations
    safe_count = total_target - violation_count  # 60% safe

    examples_per_violation_category = violation_count // len(VIOLATION_CATEGORIES)
    examples_per_safe_category = safe_count // len(SAFE_CATEGORIES)

    # Generate violations
    print("\n## Generating Violation Examples ##\n")
    for category, config in VIOLATION_CATEGORIES.items():
        print(f"\n📝 {category}: generating {examples_per_violation_category} examples...")

        for prompt in config["prompts"]:
            count = examples_per_violation_category // len(config["prompts"])
            messages = generate_violation_example(category, prompt, count)

            for msg in messages:
                # Annotate with GPT-4
                annotation = annotate_message(msg, category)
                if annotation:
                    example = {
                        "message": msg,
                        "category": category,
                        **annotation,
                        "source": "synthetic"
                    }
                    all_examples.append(example)
                    print(".", end="", flush=True)

        print(f" ✅ {category}")

    # Generate safe examples
    print("\n\n## Generating Safe Examples ##\n")
    for category in SAFE_CATEGORIES:
        print(f"\n📝 {category}: generating {examples_per_safe_category} examples...")

        messages = generate_safe_example(category, examples_per_safe_category)

        for msg in messages:
            annotation = annotate_message(msg)
            if annotation:
                example = {
                    "message": msg,
                    "category": category,
                    **annotation,
                    "source": "synthetic"
                }
                all_examples.append(example)
                print(".", end="", flush=True)

        print(f" ✅ {category}")

    # Save to JSONL
    print(f"\n\n💾 Saving {len(all_examples)} examples to {OUTPUT_FILE}")
    with open(OUTPUT_FILE, "w") as f:
        for example in all_examples:
            f.write(json.dumps(example) + "\n")

    # Statistics
    print("\n" + "="*70)
    print("📊 GENERATION SUMMARY")
    print("="*70)

    violations = sum(1 for ex in all_examples if ex["has_violation"])
    safe = len(all_examples) - violations

    print(f"\nTotal examples: {len(all_examples)}")
    print(f"  - Violations: {violations} ({violations/len(all_examples)*100:.1f}%)")
    print(f"  - Safe: {safe} ({safe/len(all_examples)*100:.1f}%)")

    print("\nViolation breakdown:")
    for category in VIOLATION_CATEGORIES.keys():
        count = sum(1 for ex in all_examples if ex.get("category") == category)
        print(f"  - {category}: {count}")

    print("\nSeverity distribution:")
    for severity in ["low", "medium", "high", "critical"]:
        count = sum(1 for ex in all_examples if ex.get("severity") == severity)
        if count > 0:
            print(f"  - {severity}: {count}")

    print("\n✅ Synthetic data generation complete!")
    print("\nNext step: python 3_prepare_training_data.py")


if __name__ == "__main__":
    main()
