"""
Generate visual diagrams for Safety Rating System
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle
import numpy as np

# Create figure with 2 subplots
fig = plt.figure(figsize=(18, 12))

# =====================================
# DIAGRAM 1: Safety Rating Scale
# =====================================
ax1 = plt.subplot(2, 1, 1)
ax1.set_xlim(0, 10)
ax1.set_ylim(0, 10)
ax1.axis('off')

# Title
ax1.text(5, 9.5, 'Agent Safety Rating System (1-5 Scale)',
         fontsize=24, weight='bold', ha='center')
ax1.text(5, 9.0, 'Based on Safety Score Testing & Violation Analysis',
         fontsize=14, ha='center', style='italic', color='#666')

# Rating boxes
ratings = [
    (5, "EXCELLENT", "8.5-10.0", "#06A77D", "✓ Production Ready", "Zero critical failures"),
    (4, "GOOD", "7.0-8.4", "#4CAF50", "✓ Production Ready", "No critical failures"),
    (3, "MODERATE", "5.5-6.9", "#F49D37", "⚠ Monitoring Required", "Requires supervision"),
    (2, "POOR", "4.0-5.4", "#FF6B6B", "✗ Banned", "Has critical failures"),
    (1, "UNSAFE", "0.0-3.9", "#D72638", "✗ Banned", "Multiple critical failures")
]

y_start = 7.5
for rating, name, score_range, color, status, description in ratings:
    y = y_start - (5 - rating) * 1.3

    # Rating box
    box = FancyBboxPatch((0.5, y), 9, 1.0,
                         boxstyle="round,pad=0.05",
                         facecolor=color, edgecolor='white',
                         linewidth=3, alpha=0.85)
    ax1.add_patch(box)

    # Rating number (circle)
    circle = Circle((1.2, y + 0.5), 0.35, facecolor='white', edgecolor=color, linewidth=3)
    ax1.add_patch(circle)
    ax1.text(1.2, y + 0.5, str(rating), fontsize=24, weight='bold',
             ha='center', va='center', color=color)

    # Name
    ax1.text(2.0, y + 0.65, name, fontsize=18, weight='bold',
             va='center', color='white')

    # Score range
    ax1.text(2.0, y + 0.35, f"Score: {score_range}", fontsize=12,
             va='center', color='white', alpha=0.9)

    # Status
    status_color = 'white' if 'Banned' in status else 'white'
    ax1.text(5.5, y + 0.5, status, fontsize=14, weight='bold',
             va='center', ha='left', color=status_color)

    # Description
    ax1.text(8.0, y + 0.5, description, fontsize=11,
             va='center', ha='left', color='white', style='italic')

# Test results examples
ax1.text(0.5, 1.5, 'ACTUAL TEST RESULTS:', fontsize=14, weight='bold')

# Claude Haiku
claude_box = FancyBboxPatch((0.5, 0.7), 4.3, 0.6,
                            boxstyle="round,pad=0.05",
                            facecolor='#E8F8F4', edgecolor='#06A77D', linewidth=2)
ax1.add_patch(claude_box)
ax1.text(0.7, 1.1, '✓ Claude Haiku', fontsize=12, weight='bold', va='center', color='#06A77D')
ax1.text(0.7, 0.85, 'Score: 8.0/10 | Critical: 0 | High: 0', fontsize=10, va='center')
ax1.text(4.5, 0.98, '→ Rating: 4/5 (GOOD)', fontsize=11, weight='bold',
         va='center', ha='right', color='#06A77D')

# GPT-4o-mini
gpt_box = FancyBboxPatch((5.2, 0.7), 4.3, 0.6,
                         boxstyle="round,pad=0.05",
                         facecolor='#FFE5E8', edgecolor='#D72638', linewidth=2)
ax1.add_patch(gpt_box)
ax1.text(5.4, 1.1, '✗ GPT-4o-mini', fontsize=12, weight='bold', va='center', color='#D72638')
ax1.text(5.4, 0.85, 'Score: 5.2/10 | Critical: 2 | High: 1', fontsize=10, va='center')
ax1.text(9.2, 0.98, '→ Rating: 2/5 (POOR)', fontsize=11, weight='bold',
         va='center', ha='right', color='#D72638')

# =====================================
# DIAGRAM 2: Runtime Downgrade System
# =====================================
ax2 = plt.subplot(2, 1, 2)
ax2.set_xlim(0, 10)
ax2.set_ylim(0, 10)
ax2.axis('off')

# Title
ax2.text(5, 9.5, 'Runtime Monitoring & Automatic Downgrade System',
         fontsize=24, weight='bold', ha='center')
ax2.text(5, 9.0, 'Real-time Safety Monitoring with Owner Notifications',
         fontsize=14, ha='center', style='italic', color='#666')

# Column 1: Downgrade Triggers
ax2.text(0.5, 8.3, 'DOWNGRADE TRIGGERS', fontsize=14, weight='bold')

triggers = [
    ("1 CRITICAL", "Immediate", "-2 ratings", "#D72638", "❗"),
    ("3 HIGH", "24 hours", "-1 rating", "#FF6B6B", "⚠"),
    ("5 MEDIUM", "24 hours", "-1 rating", "#F49D37", "⚠"),
    ("10 LOW", "24 hours", "-1 rating", "#FFC107", "⚠")
]

y_pos = 7.5
for violation, window, downgrade, color, icon in triggers:
    box = FancyBboxPatch((0.5, y_pos), 2.8, 0.65,
                         boxstyle="round,pad=0.05",
                         facecolor=color, edgecolor='white',
                         linewidth=2, alpha=0.8)
    ax2.add_patch(box)

    ax2.text(0.7, y_pos + 0.45, f"{icon} {violation} violations", fontsize=11,
             weight='bold', va='center', color='white')
    ax2.text(0.7, y_pos + 0.20, f"in {window} → {downgrade}", fontsize=9,
             va='center', color='white', alpha=0.9)

    y_pos -= 0.9

# Column 2: Example Scenario
ax2.text(3.8, 8.3, 'EXAMPLE: PRODUCTION DOWNGRADE', fontsize=14, weight='bold')

# Timeline
timeline_y = 7.5
time_height = 3.2

# Background
timeline_box = Rectangle((3.8, timeline_y - time_height), 2.8, time_height,
                         facecolor='#F5F5F5', edgecolor='#CCC', linewidth=1)
ax2.add_patch(timeline_box)

# Initial state
ax2.text(4.0, 7.3, 'T0: Initial State', fontsize=10, weight='bold')
initial_box = FancyBboxPatch((4.0, 6.8), 2.3, 0.35,
                             boxstyle="round,pad=0.03",
                             facecolor='#4CAF50', edgecolor='white', linewidth=1)
ax2.add_patch(initial_box)
ax2.text(5.15, 6.98, 'Rating: 4/5 (GOOD)', fontsize=9,
         ha='center', va='center', color='white', weight='bold')

# Violation 1
arrow1 = FancyArrowPatch((5.15, 6.7), (5.15, 6.45),
                        arrowstyle='->', mutation_scale=15, linewidth=1.5, color='#666')
ax2.add_patch(arrow1)
ax2.text(4.0, 6.3, 'T1: Violation 1', fontsize=9, style='italic')
ax2.text(4.0, 6.05, '  High severity', fontsize=8, color='#FF6B6B')

# Violation 2
arrow2 = FancyArrowPatch((5.15, 5.95), (5.15, 5.70),
                        arrowstyle='->', mutation_scale=15, linewidth=1.5, color='#666')
ax2.add_patch(arrow2)
ax2.text(4.0, 5.55, 'T2: Violation 2', fontsize=9, style='italic')
ax2.text(4.0, 5.30, '  High severity', fontsize=8, color='#FF6B6B')

# Violation 3 (triggers downgrade)
arrow3 = FancyArrowPatch((5.15, 5.20), (5.15, 4.95),
                        arrowstyle='->', mutation_scale=15, linewidth=1.5, color='#D72638')
ax2.add_patch(arrow3)
ax2.text(4.0, 4.80, 'T3: Violation 3', fontsize=9, style='italic', color='#D72638')
ax2.text(4.0, 4.55, '  High severity', fontsize=8, color='#D72638', weight='bold')
ax2.text(4.0, 4.35, '  → DOWNGRADE!', fontsize=8, color='#D72638', weight='bold')

# Final state
final_box = FancyBboxPatch((4.0, 3.9), 2.3, 0.35,
                           boxstyle="round,pad=0.03",
                           facecolor='#F49D37', edgecolor='white', linewidth=2)
ax2.add_patch(final_box)
ax2.text(5.15, 4.08, 'Rating: 3/5 (MODERATE)', fontsize=9,
         ha='center', va='center', color='white', weight='bold')

# Column 3: Action Matrix
ax2.text(7.0, 8.3, 'ACTION REQUIRED', fontsize=14, weight='bold')

actions = [
    (1, "IMMEDIATE REMOVAL", "#D72638"),
    (2, "INSPECTION (48h)", "#FF6B6B"),
    (3, "REVIEW REQUIRED", "#F49D37"),
    (4, "MONITORING", "#4CAF50"),
    (5, "NORMAL", "#06A77D")
]

y_pos = 7.5
for rating, action, color in actions:
    box = FancyBboxPatch((7.0, y_pos), 2.8, 0.65,
                         boxstyle="round,pad=0.05",
                         facecolor=color, edgecolor='white',
                         linewidth=2, alpha=0.8)
    ax2.add_patch(box)

    ax2.text(7.2, y_pos + 0.45, f"Rating {rating}/5", fontsize=11,
             weight='bold', va='center', color='white')
    ax2.text(7.2, y_pos + 0.20, action, fontsize=9,
             va='center', color='white')

    y_pos -= 0.9

# Bottom: Notification example
notif_box = FancyBboxPatch((0.5, 0.3), 9, 2.5,
                           boxstyle="round,pad=0.1",
                           facecolor='#FFF3CD', edgecolor='#F49D37', linewidth=3)
ax2.add_patch(notif_box)

ax2.text(5, 2.5, '📧 OWNER NOTIFICATION EXAMPLE', fontsize=13, weight='bold',
         ha='center', color='#856404')

ax2.text(0.8, 2.05, 'To:', fontsize=10, weight='bold', color='#856404')
ax2.text(1.3, 2.05, 'agent-owner@example.com', fontsize=10, color='#856404')

ax2.text(0.8, 1.70, 'Subject:', fontsize=10, weight='bold', color='#856404')
ax2.text(1.6, 1.70, '[ACTION REQUIRED] Agent Safety Rating Downgraded', fontsize=10, color='#D72638')

ax2.text(0.8, 1.35, 'Message:', fontsize=10, weight='bold', color='#856404')
ax2.text(0.8, 1.05, 'Your agent "Claude Haiku Child Safety Agent" has been downgraded from 4/5 to 3/5',
         fontsize=9, color='#856404')
ax2.text(0.8, 0.80, 'due to 3+ high severity violations in 24 hours. Review required within 48 hours.',
         fontsize=9, color='#856404')

ax2.text(0.8, 0.50, 'Actions: Review violations → Investigate root cause → Apply fixes → Retest → Re-certify',
         fontsize=8, color='#856404', style='italic')

plt.tight_layout()
plt.savefig('/Users/vikramsiwach/agentops-sdk/training/Safety_Rating_System_Diagram.png',
            dpi=300, bbox_inches='tight', facecolor='white')
print("✅ Diagram generated: Safety_Rating_System_Diagram.png")
