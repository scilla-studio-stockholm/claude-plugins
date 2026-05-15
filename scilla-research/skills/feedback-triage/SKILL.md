---
name: feedback-triage
description: Categorize and prioritize customer feedback at scale. Use when a PM or researcher has feedback exports from Intercom, Zendesk, app store reviews, NPS surveys, support tickets, or spreadsheets that need organizing by theme, urgency, and relevance to current focus areas. Handles batch processing and outputs structured summaries.
user_invocable: true
---

# Feedback Triage

Transforms raw customer feedback into categorized, prioritized insights ready for action.

## Quick Start

1. Export feedback from your source (CSV, JSON, or paste text)
2. Run: `python scripts/triage_feedback.py feedback.csv -o triaged.md`
3. Review categorized output and adjust priorities as needed

## What It Does

**Categorizes feedback by theme:**
- Auto-detects common themes (usability, performance, pricing, feature requests, bugs)
- Groups similar feedback together
- Identifies emerging patterns across entries

**Prioritizes by signals:**
- Urgency markers (frustration language, churn risk, severity)
- Frequency (how often this theme appears)
- Customer segment (if data available: enterprise vs. free, new vs. long-term)

**Flags focus area matches:**
- Configure your current priorities in `config.yaml`
- Skill highlights feedback relevant to what you're working on now
- Surfaces unexpected opportunities outside your focus

**Outputs actionable summary:**
- Executive overview (top themes, urgent items, opportunities)
- Detailed breakdown by category
- Raw quotes for evidence

## Usage Options

```bash
# Basic triage
python scripts/triage_feedback.py feedback.csv

# Specify focus areas inline
python scripts/triage_feedback.py feedback.csv --focus "onboarding,pricing,mobile"

# Use config file for focus areas
python scripts/triage_feedback.py feedback.csv --config config.yaml

# Output formats
python scripts/triage_feedback.py feedback.csv --format md|json|csv

# Set minimum entries per theme
python scripts/triage_feedback.py feedback.csv --min-cluster 3
```

## Supported Input Formats

The script auto-detects format. See `references/input_formats.md` for details on:
- Intercom exports (CSV)
- Zendesk exports (CSV)
- App Store / Play Store reviews (CSV)
- NPS survey exports
- Generic CSV with feedback column
- Plain text (one entry per line)
- JSON arrays

## Configuration

Create a `config.yaml` to set persistent focus areas:

```yaml
focus_areas:
  - onboarding
  - checkout flow
  - mobile experience

segments_to_prioritize:
  - enterprise
  - trial users

urgency_keywords:
  - cancel
  - frustrated
  - broken
  - urgent
  - unacceptable
```

## Two-Stage Workflow

### Stage 1: Automated Categorization (Script)

The script handles:
- Parsing input formats
- Basic theme detection via keyword matching
- Urgency flagging
- Grouping and counting

### Stage 2: LLM Review (Claude)

After running the script, paste the output and ask Claude to:
- Refine categories (merge similar, split overloaded)
- Identify nuanced themes the script missed
- Write executive summary
- Recommend actions

See `references/llm_review_prompt.md` for the structured prompt.

## Output Structure

```markdown
# Feedback Triage Report
Generated: [date]
Total entries: [n]

## Executive Summary
[Top 3 themes, urgent items, key opportunities]

## Focus Area Matches
[Feedback relevant to your configured priorities]

## By Category

### Usability (23 entries)
**Urgency: Medium**
Representative quotes:
- "I couldn't figure out how to..."
- "The button was hidden..."

### Feature Requests (18 entries)
...

## Urgent Items (Requires Immediate Attention)
[High-frustration entries, churn signals]

## Opportunities
[Positive feedback, expansion signals, unexpected patterns]
```

## When to Use

- Weekly/monthly feedback review
- Before roadmap planning
- After launches (monitor response)
- When inheriting a new product area
- Preparing for stakeholder updates
