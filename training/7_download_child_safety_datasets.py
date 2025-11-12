"""
Step 7: Download child safety datasets from HuggingFace and research sources

Prerequisites:
    pip install huggingface_hub datasets gitpython

    # Optionally set HF token for private datasets
    export HF_TOKEN=your_token_here
"""

import os
import subprocess
from pathlib import Path
from datasets import load_dataset
import shutil

# Create directory structure
DATA_DIR = Path("./data/child_safety/raw")
DATA_DIR.mkdir(parents=True, exist_ok=True)

print("🛡️  Downloading Child Safety Datasets\n")
print("="*70)

# ============================================================================
# 1. HUGGINGFACE DATASETS
# ============================================================================

print("\n## HUGGINGFACE DATASETS ##\n")

huggingface_datasets = [
    {
        "name": "jigsaw-toxicity",
        "id": "google/jigsaw_toxicity_pred",
        "priority": "CRITICAL",
        "description": "159K Wikipedia comments with 6 toxicity labels"
    },
    {
        "name": "x-sensitive",
        "id": "cardiffnlp/x_sensitive",
        "priority": "HIGH",
        "description": "Social media content: profanity, sexual, drugs, self-harm"
    },
    {
        "name": "oig-moderation",
        "id": "ontocord/OIG-moderation",
        "priority": "HIGH",
        "description": "NSFW, anthropic-redteam, toxic comments"
    },
    {
        "name": "content-moderation",
        "id": "GuardrailsAI/content-moderation",
        "priority": "MEDIUM",
        "description": "Jigsaw evaluation subset for moderation"
    },
    {
        "name": "toxic-bert-dataset",
        "id": "unitary/toxic-bert",
        "priority": "MEDIUM",
        "description": "Toxic content detection model training data",
        "type": "model",  # This is a model, we'll try to get its dataset
    },
]

def download_huggingface_dataset(dataset_id, output_name, dataset_type="dataset"):
    """Download dataset from HuggingFace."""
    output_path = DATA_DIR / output_name

    try:
        print(f"\n📥 Downloading: {dataset_id}")

        if dataset_type == "model":
            print(f"   Note: {dataset_id} is a model, not a dataset. Skipping...")
            return False

        # Try loading with datasets library
        try:
            dataset = load_dataset(dataset_id)
            output_path.mkdir(parents=True, exist_ok=True)
            dataset.save_to_disk(str(output_path))
            print(f"✅ Downloaded to: {output_path}")

            # Print dataset info
            if hasattr(dataset, 'num_rows'):
                print(f"   Rows: {dataset.num_rows:,}")
            elif 'train' in dataset:
                print(f"   Train rows: {len(dataset['train']):,}")

            return True
        except Exception as e:
            # Fallback to CLI download
            print(f"   Trying CLI download method...")
            cmd = f"huggingface-cli download {dataset_id} --repo-type dataset --local-dir {output_path}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"✅ Downloaded to: {output_path}")
                return True
            else:
                print(f"⚠️  Partial or failed: {str(e)[:100]}")
                return False

    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

for ds in huggingface_datasets:
    print(f"\n[{ds['priority']}] {ds['description']}")
    ds_type = ds.get("type", "dataset")
    download_huggingface_dataset(ds["id"], ds["name"], ds_type)

# ============================================================================
# 2. RESEARCH DATASETS (LIMITED PUBLIC AVAILABILITY)
# ============================================================================

print("\n\n## RESEARCH DATASETS ##\n")

print("""
⚠️  IMPORTANT: Grooming Detection Datasets

The following datasets contain sensitive material and have limited public availability:

1. PAN12 Dataset (Perverted Justice Archives)
   - Real chat logs from convicted groomers
   - Requires special access/ethics approval
   - URL: https://pan.webis.de/clef12/pan12-web/sexual-predator-identification.html
   - Status: NOT publicly downloadable

2. Protectbot Training Data
   - Based on PAN12 dataset
   - Published in research papers only
   - Status: NOT publicly available

3. SERI Dataset (NSF-funded project)
   - Synthetic grooming conversations
   - Under active development (2024)
   - Status: NOT yet released

RECOMMENDATION: Generate synthetic grooming examples using GPT-4o-mini with
human review rather than attempting to access these restricted datasets.
""")

# ============================================================================
# 3. ORGANIZE DATA BY CATEGORY
# ============================================================================

print("\n\n## ORGANIZING DATASETS ##\n")

# Create category directories
categories = [
    "toxic_language",
    "nsfw_content",
    "grooming",
    "privacy_violation",
    "self_harm",
    "personal_info_request"
]

for category in categories:
    category_dir = DATA_DIR / category
    category_dir.mkdir(parents=True, exist_ok=True)

# Map datasets to categories
dataset_category_map = [
    ("jigsaw-toxicity", ["toxic_language"]),
    ("x-sensitive", ["toxic_language", "nsfw_content", "self_harm"]),
    ("oig-moderation", ["toxic_language", "nsfw_content"]),
    ("content-moderation", ["toxic_language"]),
]

print("📁 Creating symbolic links to organize by category...")

for source, target_categories in dataset_category_map:
    source_path = DATA_DIR / source

    if source_path.exists():
        for category in target_categories:
            dest_path = DATA_DIR / category / source

            # Create symlink if it doesn't exist
            if not dest_path.exists():
                try:
                    # For cross-platform compatibility, copy instead of symlink
                    if dest_path.parent.exists():
                        print(f"✅ Linked {source} → {category}/")
                        # Just create a marker file instead of copying large dataset
                        marker_file = dest_path.parent / f"{source}.txt"
                        marker_file.write_text(f"Source: {source_path}")
                except Exception as e:
                    print(f"⚠️  Could not link {source}: {e}")

# ============================================================================
# 4. SUMMARY
# ============================================================================

print("\n\n" + "="*70)
print("📊 DOWNLOAD SUMMARY")
print("="*70)

def get_dir_size(path):
    """Calculate directory size in MB."""
    try:
        total = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
        return total / 1024 / 1024
    except:
        return 0

def count_examples(path):
    """Try to count examples in dataset."""
    try:
        if (path / "dataset_info.json").exists():
            import json
            with open(path / "dataset_info.json") as f:
                info = json.load(f)
                return info.get("splits", {}).get("train", {}).get("num_examples", "?")
        return "?"
    except:
        return "?"

# Summary of downloaded datasets
print("\nDownloaded Datasets:")
for ds in huggingface_datasets:
    ds_path = DATA_DIR / ds["name"]
    if ds_path.exists():
        size_mb = get_dir_size(ds_path)
        num_examples = count_examples(ds_path)
        print(f"\n  ✅ {ds['name']}")
        print(f"     Priority: {ds['priority']}")
        print(f"     Size: {size_mb:.2f} MB")
        print(f"     Examples: {num_examples}")
    else:
        print(f"\n  ❌ {ds['name']} - Download failed or skipped")

# Category summary
print("\n\nDatasets by Category:")
for category in categories:
    category_dir = DATA_DIR / category
    if category_dir.exists():
        num_sources = len(list(category_dir.glob("*.txt")))
        print(f"\n  {category}:")
        print(f"    Data sources: {num_sources}")

print("\n\n" + "="*70)
print("✅ Dataset download complete!")
print("="*70)

print("\n⚠️  IMPORTANT NOTES:")
print("  1. Grooming datasets (PAN12) require special access")
print("  2. All synthetic data must undergo human review")
print("  3. Follow ethical guidelines for child safety research")
print("  4. Ensure secure storage with encryption and access controls")

print("\n📋 Next steps:")
print("  1. Review downloaded datasets in data/child_safety/raw/")
print("  2. Set up human review process for synthetic data")
print("  3. Run: python 8_generate_child_safety_synthetic.py")
print("  4. CRITICAL: Manually review all generated examples")
print("  5. Then: python 9_prepare_child_safety_training_data.py")
