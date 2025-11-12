"""
Step 7: Download agent security datasets from HuggingFace, GitHub, and other sources

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
DATA_DIR = Path("./data/security/raw")
DATA_DIR.mkdir(parents=True, exist_ok=True)

print("🔒 Downloading Agent Security Datasets\n")
print("="*70)

# ============================================================================
# 1. HUGGINGFACE DATASETS
# ============================================================================

print("\n## HUGGINGFACE DATASETS ##\n")

huggingface_datasets = [
    {
        "name": "prompt-injection-safeguard",
        "id": "xTRam1/safe-guard-prompt-injection",
        "priority": "HIGH",
        "description": "Prompt injection defense examples"
    },
    {
        "name": "prompt-injection-chatbot",
        "id": "reshabhs/SPML_Chatbot_Prompt_Injection",
        "priority": "HIGH",
        "description": "Chatbot-specific prompt injection attacks"
    },
    {
        "name": "jailbreak-behaviors",
        "id": "JailbreakBench/JBB-Behaviors",
        "priority": "MEDIUM",
        "description": "100 misuse behaviors for jailbreak detection"
    },
    {
        "name": "adversarial-samples",
        "id": "MBZUAI-LLM/M-Attack_AdvSamples",
        "priority": "MEDIUM",
        "description": "Adversarial attack samples"
    },
]

def download_huggingface_dataset(dataset_id, output_name):
    """Download dataset from HuggingFace."""
    output_path = DATA_DIR / output_name

    try:
        print(f"\n📥 Downloading: {dataset_id}")

        # Try loading with datasets library
        try:
            dataset = load_dataset(dataset_id)
            output_path.mkdir(parents=True, exist_ok=True)
            dataset.save_to_disk(str(output_path))
            print(f"✅ Downloaded to: {output_path}")
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
    download_huggingface_dataset(ds["id"], ds["name"])

# ============================================================================
# 2. GITHUB REPOSITORIES
# ============================================================================

print("\n\n## GITHUB REPOSITORIES ##\n")

github_repos = [
    {
        "name": "ai-agent-privacy",
        "url": "https://github.com/facebookresearch/ai-agent-privacy",
        "priority": "HIGH",
        "description": "AgentDAM privacy leakage benchmark"
    },
    {
        "name": "llm-attacks",
        "url": "https://github.com/llm-attacks/llm-attacks",
        "priority": "HIGH",
        "description": "Universal adversarial attacks on LLMs"
    },
    {
        "name": "llmart",
        "url": "https://github.com/IntelLabs/LLMart",
        "priority": "MEDIUM",
        "description": "LLM Adversarial Robustness Toolkit"
    },
]

def download_github_repo(repo_url, output_name):
    """Clone GitHub repository."""
    output_path = DATA_DIR / output_name

    try:
        print(f"\n📥 Cloning: {repo_url}")

        # Remove if exists
        if output_path.exists():
            shutil.rmtree(output_path)

        # Clone with depth 1 (shallow clone for speed)
        cmd = f"git clone --depth 1 {repo_url} {output_path}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✅ Cloned to: {output_path}")
            return True
        else:
            print(f"❌ Error: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

for repo in github_repos:
    print(f"\n[{repo['priority']}] {repo['description']}")
    download_github_repo(repo["url"], repo["name"])

# ============================================================================
# 3. PROCESS AND ORGANIZE DATA
# ============================================================================

print("\n\n## ORGANIZING DATASETS ##\n")

# Create category directories
categories = ["prompt_injection", "adversarial_attacks", "privacy_leakage", "tool_poisoning"]
for category in categories:
    category_dir = DATA_DIR / category
    category_dir.mkdir(parents=True, exist_ok=True)

# Move datasets to appropriate categories
moves = [
    ("prompt-injection-safeguard", "prompt_injection"),
    ("prompt-injection-chatbot", "prompt_injection"),
    ("jailbreak-behaviors", "prompt_injection"),
    ("adversarial-samples", "adversarial_attacks"),
    ("llm-attacks", "adversarial_attacks"),
    ("llmart", "adversarial_attacks"),
    ("ai-agent-privacy", "privacy_leakage"),
]

for source, category in moves:
    source_path = DATA_DIR / source
    dest_path = DATA_DIR / category / source

    if source_path.exists() and not dest_path.exists():
        try:
            shutil.move(str(source_path), str(dest_path))
            print(f"✅ Moved {source} → {category}/")
        except Exception as e:
            print(f"⚠️  Could not move {source}: {e}")

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

for category in categories:
    category_dir = DATA_DIR / category
    if category_dir.exists():
        size_mb = get_dir_size(category_dir)
        num_subdirs = len([d for d in category_dir.iterdir() if d.is_dir()])
        print(f"\n{category}:")
        print(f"  Datasets: {num_subdirs}")
        print(f"  Size: {size_mb:.2f} MB")

print("\n\n✅ Dataset download complete!")
print("\n⚠️  NOTE: Some datasets may require manual download or access tokens")
print("\nNext steps:")
print("  1. Review downloaded datasets in data/security/raw/")
print("  2. Run: python 8_generate_security_synthetic.py")
print("  3. Then: python 9_prepare_security_training_data.py")
