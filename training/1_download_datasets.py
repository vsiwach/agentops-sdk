"""
Step 1: Download retail/CPG datasets from Kaggle and HuggingFace

Prerequisites:
    pip install kaggle datasets huggingface_hub

    # Set up Kaggle API credentials
    # Download kaggle.json from https://www.kaggle.com/settings
    # Place in ~/.kaggle/kaggle.json
    chmod 600 ~/.kaggle/kaggle.json
"""

import os
import subprocess
from pathlib import Path
from datasets import load_dataset

# Create data directory
DATA_DIR = Path("./data/raw")
DATA_DIR.mkdir(parents=True, exist_ok=True)

print("📦 Downloading Retail/CPG Datasets\n")
print("="*70)

# ============================================================================
# 1. KAGGLE DATASETS
# ============================================================================

kaggle_datasets = [
    {
        "name": "fraud-grocery-retail",
        "id": "oscarm524/fraud-detection-in-grocery-shopping-transactions",
        "priority": "HIGH",
        "description": "Retail self-checkout fraud detection"
    },
    {
        "name": "ecommerce-fraud-2024",
        "id": "shriyashjagtap/fraudulent-e-commerce-transactions",
        "priority": "HIGH",
        "description": "1.4M+ e-commerce transactions with fraud labels"
    },
    {
        "name": "fmcg-sales-2024",
        "id": "krishanukalita/fmcg-sales-demand-forecasting-and-optimization",
        "priority": "HIGH",
        "description": "Recent FMCG sales data"
    },
    {
        "name": "online-retail-transactions",
        "id": "abhishekrp1517/online-retail-transactions-dataset",
        "priority": "MEDIUM",
        "description": "Online retail customer behavior"
    },
    {
        "name": "category-brand-sales",
        "id": "jagatsaikia/category-brand-sales-dataset",
        "priority": "MEDIUM",
        "description": "Weekly sales by brand and category"
    }
]

def download_kaggle_dataset(dataset_id, output_name):
    """Download dataset from Kaggle."""
    output_path = DATA_DIR / output_name

    try:
        print(f"\n📥 Downloading: {dataset_id}")
        cmd = f"kaggle datasets download -d {dataset_id} -p {output_path} --unzip"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✅ Downloaded to: {output_path}")
            return True
        else:
            print(f"❌ Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

print("\n## KAGGLE DATASETS ##\n")
for ds in kaggle_datasets:
    print(f"\n[{ds['priority']}] {ds['description']}")
    download_kaggle_dataset(ds["id"], ds["name"])

# ============================================================================
# 2. HUGGINGFACE DATASETS
# ============================================================================

print("\n\n## HUGGINGFACE DATASETS ##\n")

huggingface_datasets = [
    {
        "name": "financial-fraud",
        "id": "amitkedia/Financial-Fraud-Dataset",
        "priority": "MEDIUM",
        "description": "Financial fraud patterns"
    }
]

def download_huggingface_dataset(dataset_id, output_name):
    """Download dataset from HuggingFace."""
    output_path = DATA_DIR / output_name

    try:
        print(f"\n📥 Downloading: {dataset_id}")
        dataset = load_dataset(dataset_id)

        # Save to disk
        output_path.mkdir(parents=True, exist_ok=True)
        dataset.save_to_disk(str(output_path))

        print(f"✅ Downloaded to: {output_path}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

for ds in huggingface_datasets:
    print(f"\n[{ds['priority']}] {ds['description']}")
    download_huggingface_dataset(ds["id"], ds["name"])

# ============================================================================
# 3. SUMMARY
# ============================================================================

print("\n\n" + "="*70)
print("📊 DOWNLOAD SUMMARY")
print("="*70)

downloaded = list(DATA_DIR.glob("*"))
print(f"\nTotal datasets downloaded: {len(downloaded)}")
print("\nDatasets:")
for ds in downloaded:
    size_mb = sum(f.stat().st_size for f in ds.rglob('*') if f.is_file()) / 1024 / 1024
    print(f"  - {ds.name}: {size_mb:.2f} MB")

print("\n✅ Dataset download complete!")
print("\nNext step: python 2_generate_synthetic_data.py")
