"""
Step 8: Generate synthetic child safety violation examples using GPT-4o-mini

⚠️  CRITICAL ETHICAL REQUIREMENTS:
    1. ALL generated examples MUST be manually reviewed by humans
    2. Generated data is for DEFENSIVE purposes only (protecting children)
    3. Secure storage with encryption and access controls
    4. Follow institutional review board (IRB) guidelines
    5. No real child exploitation material

Prerequisites:
    pip install openai tqdm

    export OPENAI_API_KEY=your_api_key_here
"""

import os
import json
import openai
from pathlib import Path
from tqdm import tqdm
from datetime import datetime
import hashlib

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set")

openai.api_key = OPENAI_API_KEY

OUTPUT_DIR = Path("./data/child_safety/synthetic")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Number of examples per category
EXAMPLES_PER_CATEGORY = 2000
BATCH_SIZE = 10  # Generate in batches

print("🛡️  Generating Synthetic Child Safety Training Data\n")
print("="*70)
print("\n⚠️  ETHICAL NOTICE:")
print("   - All generated data is for DEFENSIVE AI training only")
print("   - Content will be reviewed by humans before use")
print("   - Purpose: Train models to PROTECT children from harm")
print("="*70 + "\n")

# ============================================================================
# 1. SYSTEM PROMPTS AND GENERATION TEMPLATES
# ============================================================================

SYSTEM_PROMPT = """You are generating training examples for a child safety AI system.

CRITICAL CONTEXT:
- Purpose: Train AI to DETECT and PREVENT harm to children
- Audience: AI researchers building PROTECTIVE systems
- Use case: DEFENSIVE security, not offensive

Your task is to generate realistic examples of violations that a child safety model needs to learn to detect and block.

ETHICAL GUIDELINES:
1. Generate examples that are realistic but not gratuitously detailed
2. Focus on detection signals (patterns, language, tactics)
3. Never include actual graphic content or real cases
4. All examples will be human-reviewed before use

You must generate examples that help train AI to protect children from:
1. Toxic Language (bullying, threats, hate speech)
2. NSFW Content (age-inappropriate sexual/violent material)
3. Grooming (predatory trust-building, manipulation)
4. Privacy Violations (COPPA/GDPR data collection)
5. Self-Harm Content (suicide, self-injury, eating disorders)
6. Personal Info Requests (soliciting identifying information)

Output format: JSON array with objects containing:
{
  "content": "the example message/communication",
  "violation_type": "category",
  "severity": "low|medium|high|critical",
  "explanation": "why this violates child safety",
  "user_age": 8-13,
  "context": "brief scenario description",
  "coppa_violation": true/false
}
"""

CATEGORY_PROMPTS = {
    "toxic_language": {
        "description": "Bullying, threats, hate speech, insults targeting children",
        "examples_needed": EXAMPLES_PER_CATEGORY,
        "prompt": """Generate {count} examples of TOXIC LANGUAGE violations for child safety training.

Include mix of:
- 70% clear violations (bullying, threats, insults)
- 20% moderate violations (mean comments, exclusion)
- 10% edge cases (harsh but not clearly bullying)

Age context: Messages to/from children ages 8-13

Focus on:
- School-related bullying
- Identity-based harassment
- Threats and intimidation
- Insults and name-calling

Output JSON array with all {count} examples."""
    },

    "nsfw_content": {
        "description": "Age-inappropriate sexual, violent, or adult content",
        "examples_needed": EXAMPLES_PER_CATEGORY,
        "prompt": """Generate {count} examples of AGE-INAPPROPRIATE CONTENT violations.

Include mix of:
- 60% sexual content references (keep clinical, not graphic)
- 20% violence/gore descriptions
- 10% drug/alcohol promotion
- 10% gambling/adult themes

Age context: Content shown to children under 13

IMPORTANT: Use clinical language, avoid graphic details. Focus on detection signals like:
- Inappropriate terminology
- Adult themes in child contexts
- Violation of age ratings

Output JSON array with all {count} examples."""
    },

    "grooming": {
        "description": "Predatory trust-building and manipulation tactics",
        "examples_needed": EXAMPLES_PER_CATEGORY,
        "prompt": """Generate {count} examples of GROOMING behavior for child safety training.

Include mix of:
- 40% trust-building phase (compliments, special attention)
- 30% information gathering (personal details, photos)
- 20% boundary testing (inappropriate requests)
- 10% meeting solicitation (offline contact)

Age context: Adult/stranger communicating with child (8-13)

Detection signals to include:
- Excessive flattery ("you're so mature")
- Secrecy requests ("don't tell your parents")
- Gift offers or promises
- Personal info requests (address, school, photos)
- Meeting proposals
- Isolation tactics

IMPORTANT: Focus on predatory PATTERNS, not graphic content.

Output JSON array with all {count} examples."""
    },

    "privacy_violation": {
        "description": "COPPA/GDPR violations - unauthorized data collection",
        "examples_needed": EXAMPLES_PER_CATEGORY,
        "prompt": """Generate {count} examples of PRIVACY VIOLATIONS (COPPA/GDPR compliance).

Include mix of:
- 30% biometric data requests (fingerprint, face scan, voice)
- 25% location tracking without consent
- 25% personal information collection (name, address, phone)
- 20% third-party data sharing

Age context: Data collection from children under 13

COPPA violations to include:
- Collecting personal info without parental consent
- Biometric data (fingerprints, facial recognition)
- Location tracking
- Sharing data with third parties
- Using child data for AI training
- No data deletion policy

Output JSON array with all {count} examples. Set coppa_violation: true for all."""
    },

    "self_harm": {
        "description": "Content promoting suicide, self-injury, eating disorders",
        "examples_needed": EXAMPLES_PER_CATEGORY,
        "prompt": """Generate {count} examples of SELF-HARM content for child safety training.

Include mix of:
- 35% self-injury discussion/methods
- 30% eating disorder promotion
- 25% suicide ideation
- 10% dangerous challenges

Age context: Content accessible to children 8-13

IMPORTANT: Clinical language only. Focus on detection signals:
- Self-harm terminology
- Pro-ana/pro-mia language
- Suicide planning language
- Dangerous challenge instructions
- "Tips and tricks" for harmful behaviors

Avoid: Graphic details, specific methods

Output JSON array with all {count} examples."""
    },

    "personal_info_request": {
        "description": "Soliciting identifying information from children",
        "examples_needed": EXAMPLES_PER_CATEGORY,
        "prompt": """Generate {count} examples of PERSONAL INFORMATION REQUESTS from children.

Include mix of:
- 25% name and surname requests
- 25% address/location requests
- 20% phone number requests
- 15% school information requests
- 15% photo/video requests

Age context: Requests directed at children under 13

Request types:
- Direct: "What's your address?"
- Indirect: "Where do you live? I might know the area"
- Progressive: Building profile over multiple questions
- Disguised: Surveys, games, "friend" requests

Severity levels:
- Low: First name, age, general interests
- Medium: Full name, city, school district
- High: Address, phone, school name, schedule
- Critical: Requests combined with meeting proposals

Output JSON array with all {count} examples."""
    },
}

# ============================================================================
# 2. SAFE EXAMPLES GENERATION
# ============================================================================

SAFE_EXAMPLES_PROMPT = """Generate {count} examples of SAFE, APPROPRIATE interactions with children for training.

These are NEGATIVE examples (no violations) that the model should learn to ALLOW.

Include:
- Educational content appropriate for ages 8-13
- Friendly, respectful conversations
- Homework help, learning support
- Age-appropriate entertainment discussions
- Positive social interactions
- Parent-authorized information collection (with proper consent language)

Each example should:
- Be clearly safe and appropriate
- Serve as contrast to violation examples
- Cover diverse scenarios (education, entertainment, social)

Output JSON array with format:
{{
  "content": "the safe message",
  "violation_type": null,
  "severity": null,
  "explanation": "why this is safe",
  "user_age": 8-13,
  "context": "scenario",
  "coppa_violation": false
}}

Generate {count} safe examples."""

# ============================================================================
# 3. GENERATION FUNCTIONS
# ============================================================================

def generate_batch(category, batch_num, batch_size):
    """Generate a batch of examples for a category."""

    if category == "safe":
        prompt = SAFE_EXAMPLES_PROMPT.format(count=batch_size)
    else:
        category_config = CATEGORY_PROMPTS[category]
        prompt = category_config["prompt"].format(count=batch_size)

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,  # Higher for diversity
            response_format={"type": "json_object"},
            max_tokens=4000
        )

        result = json.loads(response.choices[0].message.content)

        # Handle different response formats
        if "examples" in result:
            examples = result["examples"]
        elif isinstance(result, list):
            examples = result
        else:
            # Try to extract array from any key
            for key, value in result.items():
                if isinstance(value, list):
                    examples = value
                    break
            else:
                print(f"⚠️  Unexpected response format: {result}")
                return []

        # Add metadata
        for example in examples:
            example["category"] = category
            example["generated_at"] = datetime.now().isoformat()
            example["batch_num"] = batch_num
            example["review_status"] = "pending"  # Must be reviewed
            example["example_id"] = hashlib.md5(
                f"{category}_{batch_num}_{example.get('content', '')}".encode()
            ).hexdigest()[:12]

        return examples

    except Exception as e:
        print(f"❌ Error generating batch {batch_num} for {category}: {e}")
        return []


def generate_category(category, num_examples):
    """Generate all examples for a category."""

    print(f"\n{'='*70}")
    print(f"Generating: {category.upper()}")
    print(f"Target: {num_examples} examples")
    print(f"{'='*70}\n")

    all_examples = []
    num_batches = (num_examples + BATCH_SIZE - 1) // BATCH_SIZE

    with tqdm(total=num_examples, desc=f"{category}") as pbar:
        for batch_num in range(num_batches):
            batch_size = min(BATCH_SIZE, num_examples - len(all_examples))

            examples = generate_batch(category, batch_num, batch_size)

            if examples:
                all_examples.extend(examples)
                pbar.update(len(examples))

                # Save incrementally
                output_file = OUTPUT_DIR / f"{category}_batch_{batch_num}.json"
                with open(output_file, 'w') as f:
                    json.dump(examples, f, indent=2)

            # Stop if we have enough
            if len(all_examples) >= num_examples:
                break

    print(f"\n✅ Generated {len(all_examples)} examples for {category}")

    # Save combined file
    combined_file = OUTPUT_DIR / f"{category}_all.json"
    with open(combined_file, 'w') as f:
        json.dump(all_examples, f, indent=2)

    return all_examples


# ============================================================================
# 4. GENERATE ALL CATEGORIES
# ============================================================================

def main():
    print("\n📋 Generation Plan:")
    print(f"   - Violation categories: {len(CATEGORY_PROMPTS)}")
    print(f"   - Examples per category: {EXAMPLES_PER_CATEGORY}")
    print(f"   - Safe examples: {EXAMPLES_PER_CATEGORY * 2}")
    print(f"   - Total examples: {EXAMPLES_PER_CATEGORY * (len(CATEGORY_PROMPTS) + 2)}")
    print(f"   - Batch size: {BATCH_SIZE}")

    input("\nPress Enter to start generation (Ctrl+C to cancel)...")

    all_generated = {}

    # Generate violation examples
    for category in CATEGORY_PROMPTS.keys():
        examples = generate_category(category, EXAMPLES_PER_CATEGORY)
        all_generated[category] = examples

    # Generate safe examples (2x the violations for balance)
    safe_examples = generate_category("safe", EXAMPLES_PER_CATEGORY * 2)
    all_generated["safe"] = safe_examples

    # ========================================================================
    # 5. SUMMARY AND REVIEW INSTRUCTIONS
    # ========================================================================

    print("\n\n" + "="*70)
    print("📊 GENERATION SUMMARY")
    print("="*70)

    total_examples = 0
    for category, examples in all_generated.items():
        print(f"\n  {category}:")
        print(f"    Generated: {len(examples)}")
        print(f"    Status: PENDING HUMAN REVIEW")
        total_examples += len(examples)

    print(f"\n  TOTAL: {total_examples} examples")

    print("\n\n" + "="*70)
    print("⚠️  CRITICAL: HUMAN REVIEW REQUIRED")
    print("="*70)

    print("""
ALL generated examples MUST be manually reviewed before training:

1. REVIEW PROCESS:
   - Check each example for appropriateness
   - Verify detection signals are correct
   - Ensure no graphic/gratuitous content
   - Confirm educational value for AI training

2. REVIEW CRITERIA:
   ✅ Accept: Clear detection signals, appropriate for training
   ❌ Reject: Too graphic, not representative, unclear signals
   ⚠️  Edit: Good concept but needs refinement

3. REVIEW TOOLS:
   - Location: data/child_safety/synthetic/
   - Format: JSON files with review_status field
   - Update: Change "review_status" to "approved" or "rejected"

4. SECURITY:
   - Store in encrypted directory
   - Limit access to authorized reviewers only
   - Log all access for auditing

5. NEXT STEPS (after review):
   - Move approved examples to: data/child_safety/reviewed/
   - Run: python 9_prepare_child_safety_training_data.py
   - Only approved examples will be used for training
""")

    print("\n" + "="*70)
    print("✅ Generation complete! Proceed to manual review.")
    print("="*70)

    # Create review template
    review_template = OUTPUT_DIR / "REVIEW_INSTRUCTIONS.md"
    review_template.write_text("""# Child Safety Dataset Review Instructions

## Overview

You are reviewing synthetic training examples for a child safety AI model.

**Purpose:** Train AI to detect and prevent harm to children
**Status:** All examples require human approval before training use

## Review Criteria

### Accept ✅
- Clear detection signals for AI to learn
- Realistic but not gratuitously detailed
- Educational value for model training
- Appropriate for research context

### Reject ❌
- Too graphic or detailed
- Not representative of real violations
- Unclear detection signals
- Potentially harmful if leaked

### Edit ⚠️
- Good concept but needs refinement
- Detection signals could be clearer
- Severity level incorrect

## Review Process

1. Open JSON file in `data/child_safety/synthetic/`
2. For each example:
   - Read content and explanation
   - Assess against criteria above
   - Update `review_status` field:
     - "approved" - Accept for training
     - "rejected" - Exclude from training
     - "needs_edit" - Requires changes
3. Save file with reviews
4. Run validation: `python validate_reviews.py`

## Example Review

```json
{
  "content": "You're so special, what school do you go to?",
  "violation_type": "grooming",
  "severity": "high",
  "explanation": "Excessive flattery + personal info request",
  "review_status": "approved",  // ← UPDATE THIS
  "reviewer_notes": "Clear grooming signal, appropriate",  // ← ADD THIS
  "reviewed_by": "reviewer_id",  // ← ADD THIS
  "reviewed_at": "2025-01-15T10:30:00"  // ← ADD THIS
}
```

## Ethical Guidelines

- All data is for defensive AI training only
- No real child exploitation material
- Secure storage with encryption
- Access limited to authorized personnel
- Regular audits of training data

## Questions or Concerns?

Contact: [Ethics Review Board / Data Protection Officer]
""")

if __name__ == "__main__":
    main()
