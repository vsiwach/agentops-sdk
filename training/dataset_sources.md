# Retail/CPG Training Datasets for Agent Misbehavior Detection

## Found Datasets

### 1. Kaggle Datasets (Most Relevant)

#### ⭐ FMCG Sales Demand Forecasting (Nov 2024)
- **URL**: https://www.kaggle.com/datasets/krishanukalita/fmcg-sales-demand-forecasting-and-optimization
- **Relevance**: High - Recent FMCG sales data
- **Use Case**: Analyze pricing patterns, discount behavior, sales anomalies
- **Download**: `kaggle datasets download -d krishanukalita/fmcg-sales-demand-forecasting-and-optimization`

#### ⭐ Fraud Detection at Self-Checkout in Retail (May 2023)
- **URL**: https://www.kaggle.com/datasets/oscarm524/fraud-detection-in-grocery-shopping-transactions
- **Relevance**: Very High - Direct retail fraud detection
- **Use Case**: Train on actual retail fraud patterns
- **Download**: `kaggle datasets download -d oscarm524/fraud-detection-in-grocery-shopping-transactions`

#### ⭐ E-Commerce Fraud Transactions (2024)
- **URL**: https://www.kaggle.com/datasets/shriyashjagtap/fraudulent-e-commerce-transactions
- **Relevance**: High - 1.4M+ transactions with fraud labels
- **Features**: Transaction amount, payment method, product category, customer behavior
- **Download**: `kaggle datasets download -d shriyashjagtap/fraudulent-e-commerce-transactions`

#### Online Retail Transactions Dataset (March 2023)
- **URL**: https://www.kaggle.com/datasets/abhishekrp1517/online-retail-transactions-dataset
- **Relevance**: Medium - Customer behavior patterns
- **Use Case**: Normal transaction patterns for baseline
- **Download**: `kaggle datasets download -d abhishekrp1517/online-retail-transactions-dataset`

#### Category Brand Sales Dataset (Dec 2021)
- **URL**: https://www.kaggle.com/datasets/jagatsaikia/category-brand-sales-dataset
- **Relevance**: Medium - Weekly sales by brand/category
- **Use Case**: Pricing and promotion analysis
- **Download**: `kaggle datasets download -d jagatsaikia/category-brand-sales-dataset`

#### Coupon Purchase Prediction
- **URL**: https://www.kaggle.com/c/coupon-purchase-prediction/data
- **Relevance**: Medium - Discount/coupon behavior
- **Use Case**: Legitimate vs suspicious discount patterns
- **Download**: Via Kaggle competition API

### 2. HuggingFace Datasets

#### Financial Fraud Dataset
- **URL**: https://huggingface.co/datasets/amitkedia/Financial-Fraud-Dataset
- **Relevance**: Medium - General fraud patterns
- **Use Case**: Cross-domain fraud detection principles
- **Download**: `from datasets import load_dataset; dataset = load_dataset("amitkedia/Financial-Fraud-Dataset")`

### 3. Additional Sources

#### Amazon Fraud Dataset Benchmark (GitHub)
- **URL**: https://github.com/amazon-science/fraud-dataset-benchmark
- **Relevance**: High - E-commerce fraud benchmark
- **Use Case**: State-of-the-art fraud detection patterns

#### FTC Consumer Complaints (Public)
- **URL**: https://www.ftc.gov/enforcement/consumer-sentinel-network/reports
- **Relevance**: Very High - Real-world retail violations
- **Use Case**: Text-based violation descriptions
- **Access**: Public data request

## Dataset Combination Strategy

### Phase 1: Baseline Training (Week 1)
1. **Grocery Self-Checkout Fraud** - Core retail fraud patterns
2. **E-Commerce Fraud Transactions** - Large-scale transaction fraud
3. **Synthetic Generation** - Retail-specific policy violations

### Phase 2: Enhancement (Week 2-3)
4. **FMCG Sales Data** - Pricing and discount anomalies
5. **Online Retail Transactions** - Normal behavior baseline
6. **Financial Fraud** - Cross-domain patterns

### Phase 3: Specialization (Week 4+)
7. **Custom Annotations** - Company-specific policies
8. **Active Learning** - Production feedback loop
9. **Domain Adaptation** - Fine-tune for specific retail verticals

## Data Preparation Pipeline

```python
# Combined dataset structure
{
    "message": "Applied 60% discount without approval",
    "context": "retail_pricing",
    "has_violation": true,
    "violation_type": "unauthorized_discount",
    "severity": "critical",
    "explanation": "Exceeds 30% threshold",
    "confidence": 0.95,
    "source": "synthetic|kaggle|ftc|production"
}
```

## Estimated Dataset Sizes

- **Total Transactions**: ~2M+ records
- **Labeled Violations**: ~200K+ potential violations
- **Text Descriptions**: ~50K+ natural language examples
- **After Filtering**: ~100K high-quality training examples

## Next Steps

1. Set up Kaggle API credentials
2. Download all datasets
3. Run data preparation scripts
4. Generate synthetic violations
5. Combine and deduplicate
6. Create train/val/test splits (80/10/10)
