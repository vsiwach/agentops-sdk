"""
Generate visual summary of AgentOps Demo Results
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle
import numpy as np

fig, axes = plt.subplots(2, 2, figsize=(18, 14))
fig.suptitle('AgentOps SDK: 2-Agent Safety Demo Results (20 Samples)',
             fontsize=24, weight='bold', y=0.98)

# ================================
# SUBPLOT 1: Demo Overview
# ================================
ax1 = axes[0, 0]
ax1.set_xlim(0, 10)
ax1.set_ylim(0, 10)
ax1.axis('off')

ax1.text(5, 9.2, 'Demo Configuration', fontsize=18, weight='bold', ha='center')

# Agent 1 box
agent1_box = FancyBboxPatch((0.5, 6.5), 9, 2.3,
                            boxstyle="round,pad=0.1",
                            facecolor='#E8F8F4', edgecolor='#06A77D', linewidth=3)
ax1.add_patch(agent1_box)
ax1.text(5, 8.4, 'AGENT 1: Child Safety Agent', fontsize=14, weight='bold', ha='center', color='#06A77D')
ax1.text(1, 7.9, '• Model: Claude Haiku (claude-3-5-haiku-20241022)', fontsize=11)
ax1.text(1, 7.5, '• Role: Respond to child messages safely', fontsize=11)
ax1.text(1, 7.1, '• Safety Rating: 4/5 (GOOD)', fontsize=11, color='#06A77D', weight='bold')
ax1.text(1, 6.7, '• Certified Valid Until: 2026-02-10', fontsize=11)

# Agent 2 box
agent2_box = FancyBboxPatch((0.5, 3.5), 9, 2.3,
                            boxstyle="round,pad=0.1",
                            facecolor='#E8F4F8', edgecolor='#2E86AB', linewidth=3)
ax1.add_patch(agent2_box)
ax1.text(5, 5.4, 'AGENT 2: Safety Auditor', fontsize=14, weight='bold', ha='center', color='#2E86AB')
ax1.text(1, 4.9, '• Model: GPT-4o', fontsize=11)
ax1.text(1, 4.5, '• Role: Audit Agent 1 responses in real-time', fontsize=11)
ax1.text(1, 4.1, '• Validation: 100% accuracy on ground truth', fontsize=11, color='#2E86AB', weight='bold')
ax1.text(1, 3.7, '• Certified Independent Auditor', fontsize=11)

# Test info
test_box = FancyBboxPatch((0.5, 0.5), 9, 2.5,
                          boxstyle="round,pad=0.1",
                          facecolor='#F9F9F9', edgecolor='#666', linewidth=2)
ax1.add_patch(test_box)
ax1.text(5, 2.7, 'Test Configuration', fontsize=14, weight='bold', ha='center')
ax1.text(1, 2.2, '• Total Samples: 20 (12 ground truth + 8 additional)', fontsize=11)
ax1.text(1, 1.8, '• Violation Types: Toxic, NSFW, Self-harm, Privacy, Grooming, Safe', fontsize=11)
ax1.text(1, 1.4, '• User Ages: 8-14 years old', fontsize=11)
ax1.text(1, 1.0, '• Integration: AgentOps SDK + Safety Rating System', fontsize=11)
ax1.text(1, 0.6, '• Runtime Monitoring: Enabled with auto-downgrade', fontsize=11)

# ================================
# SUBPLOT 2: Test Results
# ================================
ax2 = axes[0, 1]
ax2.set_xlim(0, 10)
ax2.set_ylim(0, 10)
ax2.axis('off')

ax2.text(5, 9.2, 'Test Results Summary', fontsize=18, weight='bold', ha='center')

# Results box
results_box = FancyBboxPatch((0.5, 4.0), 9, 4.8,
                             boxstyle="round,pad=0.1",
                             facecolor='white', edgecolor='#06A77D', linewidth=3)
ax2.add_patch(results_box)

# Perfect score indicator
circle = plt.Circle((5, 7.5), 0.8, color='#06A77D', alpha=0.9)
ax2.add_patch(circle)
ax2.text(5, 7.5, '0', fontsize=48, weight='bold', ha='center', va='center', color='white')
ax2.text(5, 6.3, 'Violations Detected', fontsize=12, ha='center', weight='bold')

# Metrics
metrics = [
    ("Total Samples Tested", "20", "#666"),
    ("Agent Violations", "0", "#06A77D"),
    ("Rating Downgrades", "0", "#06A77D"),
    ("Final Safety Rating", "4/5", "#06A77D"),
    ("Average Safety Score", "9.7/10", "#06A77D"),
]

y_pos = 5.2
for label, value, color in metrics:
    ax2.text(1.5, y_pos, f"{label}:", fontsize=11, weight='bold')
    ax2.text(8.5, y_pos, value, fontsize=11, ha='right', color=color, weight='bold')
    y_pos -= 0.5

# Status box
status_box = FancyBboxPatch((0.5, 0.5), 9, 3.0,
                            boxstyle="round,pad=0.1",
                            facecolor='#E8F8F4', edgecolor='#06A77D', linewidth=3)
ax2.add_patch(status_box)
ax2.text(5, 3.1, '✓ EXCELLENT PERFORMANCE', fontsize=16, weight='bold', ha='center', color='#06A77D')
ax2.text(5, 2.5, 'Claude Haiku maintained 4/5 rating across all 20 samples', fontsize=11, ha='center')
ax2.text(5, 2.1, 'Zero violations detected in agent responses', fontsize=11, ha='center')
ax2.text(5, 1.7, 'Perfect handling of toxic, NSFW, self-harm, and grooming attempts', fontsize=11, ha='center')
ax2.text(5, 1.3, 'Provided 988 crisis hotline for self-harm scenario', fontsize=11, ha='center', color='#06A77D', weight='bold')
ax2.text(5, 0.9, 'Status: MONITORING - Continue normal operation', fontsize=11, ha='center', style='italic')

# ================================
# SUBPLOT 3: Sample Breakdown
# ================================
ax3 = axes[1, 0]
ax3.set_xlim(0, 10)
ax3.set_ylim(0, 10)
ax3.axis('off')

ax3.text(5, 9.2, 'Sample Breakdown by Category', fontsize=18, weight='bold', ha='center')

# Categories
categories = [
    ("Toxic Language", 5, "#FF6B6B", "✓"),
    ("NSFW Content", 2, "#FF6B6B", "✓"),
    ("Self-Harm", 1, "#D72638", "✓"),
    ("Privacy Violations", 2, "#F49D37", "✓"),
    ("Grooming", 2, "#D72638", "✓"),
    ("Harmful Instructions", 2, "#F49D37", "✓"),
    ("Safe/Educational", 6, "#06A77D", "✓"),
]

y_pos = 8.0
for category, count, color, status in categories:
    # Category box
    cat_box = FancyBboxPatch((0.5, y_pos-0.4), 9, 0.5,
                             boxstyle="round,pad=0.03",
                             facecolor=color, edgecolor='white', linewidth=2, alpha=0.3)
    ax3.add_patch(cat_box)

    ax3.text(1, y_pos, category, fontsize=11, weight='bold', va='center')
    ax3.text(6, y_pos, f"{count} samples", fontsize=10, va='center')
    ax3.text(8.5, y_pos, f"{status} All handled safely", fontsize=10, va='center', color='#06A77D', weight='bold')

    y_pos -= 0.8

# Key findings
findings_box = FancyBboxPatch((0.5, 0.5), 9, 2.0,
                              boxstyle="round,pad=0.1",
                              facecolor='#FFF3CD', edgecolor='#F49D37', linewidth=2)
ax3.add_patch(findings_box)
ax3.text(5, 2.2, 'KEY FINDING', fontsize=14, weight='bold', ha='center', color='#856404')
ax3.text(5, 1.7, 'Claude Haiku correctly refused all inappropriate requests', fontsize=11, ha='center')
ax3.text(5, 1.3, 'and provided age-appropriate, safe responses in every case.', fontsize=11, ha='center')
ax3.text(5, 0.9, 'Zero violations = Production-ready performance confirmed.', fontsize=11, ha='center', weight='bold', color='#06A77D')

# ================================
# SUBPLOT 4: Agent Comparison
# ================================
ax4 = axes[1, 1]
ax4.set_xlim(0, 10)
ax4.set_ylim(0, 10)
ax4.axis('off')

ax4.text(5, 9.2, 'Comparison: This Demo vs Previous Tests', fontsize=18, weight='bold', ha='center')

# Comparison table
table_data = [
    ("Metric", "Claude Haiku", "GPT-4o-mini", "Winner"),
    ("Safety Score", "9.7/10", "5.2/10", "Claude"),
    ("Violations (20 samples)", "0", "N/A", "Claude"),
    ("Crisis Hotline (988)", "✓ Provided", "✗ Missing", "Claude"),
    ("NSFW Refusal", "✓ Firm", "✗ Validates", "Claude"),
    ("Stranger Danger", "✓ Clear", "✗ Permissive", "Claude"),
    ("Rating", "4/5 (GOOD)", "2/5 (POOR)", "Claude"),
]

y_pos = 8.2
for i, (metric, claude, gpt, winner) in enumerate(table_data):
    if i == 0:
        # Header
        ax4.text(1, y_pos, metric, fontsize=10, weight='bold')
        ax4.text(3.5, y_pos, claude, fontsize=10, weight='bold', ha='center')
        ax4.text(6, y_pos, gpt, fontsize=10, weight='bold', ha='center')
        ax4.text(8.5, y_pos, winner, fontsize=10, weight='bold', ha='center')
        # Line under header
        ax4.plot([0.5, 9.5], [y_pos-0.2, y_pos-0.2], 'k-', linewidth=1)
    else:
        # Data rows
        if i % 2 == 0:
            row_box = Rectangle((0.5, y_pos-0.25), 9, 0.4, facecolor='#F5F5F5', edgecolor='none', alpha=0.5)
            ax4.add_patch(row_box)

        ax4.text(1, y_pos, metric, fontsize=10)

        # Claude value (green if contains checkmark)
        claude_color = '#06A77D' if '✓' in claude else '#666'
        ax4.text(3.5, y_pos, claude, fontsize=10, ha='center', color=claude_color, weight='bold' if '✓' in claude else 'normal')

        # GPT value (red if contains X)
        gpt_color = '#D72638' if '✗' in gpt else '#666'
        ax4.text(6, y_pos, gpt, fontsize=10, ha='center', color=gpt_color, weight='bold' if '✗' in gpt else 'normal')

        # Winner
        ax4.text(8.5, y_pos, winner, fontsize=10, ha='center', color='#06A77D', weight='bold')

    y_pos -= 0.6

# Recommendation
rec_box = FancyBboxPatch((0.5, 0.5), 9, 2.5,
                         boxstyle="round,pad=0.1",
                         facecolor='#06A77D', edgecolor='white', linewidth=3)
ax4.add_patch(rec_box)
ax4.text(5, 2.6, 'PRODUCTION RECOMMENDATION', fontsize=14, weight='bold', ha='center', color='white')
ax4.text(5, 2.1, 'Deploy Claude Haiku as primary child safety agent', fontsize=12, ha='center', color='white')
ax4.text(5, 1.7, 'Maintain GPT-4o as independent auditor', fontsize=12, ha='center', color='white')
ax4.text(5, 1.3, 'Continue runtime monitoring with automatic downgrade system', fontsize=12, ha='center', color='white')
ax4.text(5, 0.9, 'Rating: 4/5 maintained - No action required', fontsize=11, ha='center', color='white', style='italic')

plt.tight_layout()
plt.savefig('/Users/vikramsiwach/agentops-sdk/training/AgentOps_Demo_Summary.png',
            dpi=300, bbox_inches='tight', facecolor='white')
print("✅ Demo summary visualization generated: AgentOps_Demo_Summary.png")
