---
name: jtbd-interview-planner
description: Plan rigorous, JTBD-focused interview guides for customer research. Use when someone needs to create a discussion guide for user interviews, customer discovery, or jobs-to-be-done research. Accepts research questions, hypotheses, briefs, or problem statements as input (manual text or file paths). Produces a complete semi-structured guide with intro scripts, JTBD-arc questions, conditional follow-ups, and a separate coverage checklist. Auto-validates for leading questions, double-barrels, hypotheticals, and other anti-patterns.
user_invocable: true
---

# JTBD Interview Planner

Plan professional, JTBD-focused interview guides that surface causal mechanisms behind customer behavior. Built to the standards of a senior researcher—rigorous, unbiased, and structured for reliable analysis.

## Workflow

### Step 1: Gather Input

Ask for research context. Accept manual input, file paths, or both:

```
I'll help you plan a JTBD-focused interview guide. I need some context:

**Option A - Describe your research:**
- What's the core question you're trying to answer?
- What decision will this research inform?
- Any hypotheses you want to explore?

**Option B - Point me to existing docs:**
- File paths to research briefs, PRDs, strategy docs, or Knowledge Finder outputs

**Option C - Both:**
- Share files AND tell me what to focus on

Also tell me: Who are you interviewing? (e.g., current users, churned users, prospects, power users)
```

### Step 2: Clarify if Needed

Only ask clarifying questions if critical information is missing:
- **If no research question:** "What decision will this research inform?"
- **If no participant type:** "Who are you interviewing—current users, churned users, prospects, or someone else?"
- **If unclear scope:** "Is there a specific part of the experience you want to focus on, or the full journey?"

Do not ask unnecessary questions. Make reasonable assumptions and flag them.

### Step 3: Generate Guide

Use the JTBD framework in `references/jtbd_framework.md` to structure the guide:

1. **Study Context** - Objectives, research questions, hypotheses, participant criteria
2. **Interview Setup** - Duration, intro script with consent re-check
3. **Warm-Up** - Role/context questions (3-5 min)
4. **Core Exploration** - JTBD timeline arc (25-30 min):
   - First thought / Struggling moment
   - Passive → Active looking / Trigger event
   - Deciding / Tradeoffs
   - Consuming / Outcomes
5. **Deep Dive** - Customized section based on research objectives (5-7 min)
6. **Closing** - Final questions, outro script
7. **Researcher Notes** - What to listen for, analysis hooks

Use the template in `assets/guide_template.md` as the structure.

### Step 4: Build Conditional Follow-Ups

Every core question needs 2-4 conditional follow-ups:

```
Q: Walk me through the last time you [did X].

Follow-ups:
→ If they mention frustration: "What made that frustrating?"
→ If they mention a workaround: "How did you come up with that approach?"
→ If they mention other people: "What was [person's] role in this?"
→ If vague on timeline: "How long ago was this? What else was happening then?"
→ If they skip to solution: "Back up—what was happening right before that?"
```

**Follow-up triggers to always include:**
- Emotional language → Probe deeper ("Tell me more about that feeling")
- Other people mentioned → Explore their role
- Vague timeline → Anchor to specifics
- Jumped ahead → Back up to context
- Surface answer → Ask "why" or "what made you..."

### Step 5: Validate Questions

Run validation against anti-patterns in `references/question_patterns.md`:

| Anti-Pattern | Detection | Action |
|--------------|-----------|--------|
| **Leading** | "Would you say...", "How frustrating was..." | 🔴 Must fix |
| **Double-barrel** | Two questions joined with "and" | 🟡 Split |
| **Hypothetical** | "Would you...", "Will you..." | 🟡 Reframe to past |
| **Closed yes/no** | "Did you...", "Is it..." | 🟡 Make open |
| **Jargon** | Technical terms, product names | 🟢 Flag for review |
| **Confirmation bias** | "Since X is difficult...", "We believe..." | 🔴 Must fix |

Use `scripts/validate_guide.py` to check the generated guide:

```bash
python scripts/validate_guide.py guide.md
```

Fix all 🔴 Critical issues. Flag 🟡 Warnings for researcher awareness.

### Step 6: Generate Checklist

Create a separate coverage checklist using `assets/checklist_template.md`:
- Section coverage tracking
- JTBD component capture (four forces, timeline)
- Quotable moment logging
- Quality self-check

### Step 7: Output Both Files

Deliver:
1. **Interview Guide** (`[study-name]-guide.md`) - The complete discussion guide
2. **Coverage Checklist** (`[study-name]-checklist.md`) - The tracker for during/after interview

---

## JTBD Framework Reference

The guide follows the Jobs To Be Done interview methodology. See `references/jtbd_framework.md` for:
- The timeline arc (first thought → passive → active → deciding → consuming)
- The four forces of progress (push, pull, anxiety, habit)
- Struggling moment identification
- Red flags during interviews
- What good output looks like

**Key principle:** Customers don't buy products. They hire them to make progress. The interview uncovers the causal story behind that hiring decision.

---

## Quality Standards

### Every Question Must:
- [ ] Be open-ended (not yes/no)
- [ ] Focus on past behavior (not hypothetical future)
- [ ] Be neutral (not leading or assuming)
- [ ] Ask one thing (not double-barreled)
- [ ] Use participant's language (not jargon)
- [ ] Have 2+ conditional follow-ups

### The Guide Must Cover:
- [ ] Struggling moment (specific, emotional, situational)
- [ ] Trigger event (what pushed passive → active)
- [ ] All four forces (push, pull, anxiety, habit)
- [ ] Decision criteria and tradeoffs
- [ ] Outcomes vs expectations
- [ ] Competitive alternatives considered

### Intro Script Must Include:
- [ ] Thank you and time acknowledgment
- [ ] Topic framing (what we'll cover)
- [ ] Time estimate
- [ ] Recording consent re-check
- [ ] "Any questions before we start?"

---

## Participant Type Adjustments

The core JTBD structure stays consistent across participant types (for analysis comparability), but tone and framing adjust:

| Participant Type | Tone Adjustment |
|------------------|-----------------|
| B2B Executive | Concise, respect time pressure, business outcome framing |
| Consumer User | More casual, allow lifestyle context |
| Churned User | Careful framing—focus on "back then" not "why you left us" |
| Power User | Can go deeper on specifics, less warm-up needed |
| New User | More context-setting, explore onboarding thoroughly |
| Prospect | Focus on current state and struggling moment, less on outcomes |

---

## Anti-Pattern Quick Reference

### 🔴 Never Do:
- "Would you say X is good?" → Leading
- "How frustrating was the onboarding?" → Assumes frustration
- "We think users need X—do you agree?" → Confirmation bias

### 🟡 Avoid:
- "Did you find it easy?" → Closed (use "How did you find it?")
- "Would you recommend it?" → Hypothetical (use "Have you recommended it?")
- "What did you think of the pricing and the features?" → Double-barrel (split)

### ✅ Do:
- "How would you describe your experience with..."
- "Walk me through what happened when..."
- "Tell me about a time when..."
- "What was going on in your life/work when..."

---

## File Structure

```
jtbd-interview-planner/
├── SKILL.md (this file)
├── scripts/
│   └── validate_guide.py    # Anti-pattern detection
├── references/
│   ├── jtbd_framework.md    # JTBD methodology
│   └── question_patterns.md # Anti-patterns to detect
└── assets/
    ├── guide_template.md    # Interview guide structure
    └── checklist_template.md # Coverage tracker
```

---

## When to Use This Skill

✅ **Use when:**
- Planning customer discovery interviews
- Creating discussion guides for user research
- Doing jobs-to-be-done research
- Investigating purchase/adoption decisions
- Exploring churn or switching behavior

❌ **Don't use when:**
- Usability testing (use task-based protocol instead)
- Survey design (different methodology)
- Focus groups (different dynamics)
- Quantitative research design
