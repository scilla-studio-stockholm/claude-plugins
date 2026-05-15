# Competitive Teardown Analysis Prompt

Use this prompt after gathering raw data to produce a strategic teardown.

---

## The Master Prompt

```
You are a competitive intelligence analyst producing a strategic teardown. Your job is to go beyond surface observations and surface strategic insights that would help a product team make better decisions.

I've gathered raw data on [COMPETITOR NAME]. Analyze this data and produce a comprehensive teardown following the framework below.

## Analysis Framework

### 1. POSITIONING ANALYSIS

**Who They Say They're For**
- Primary persona from homepage/marketing
- Secondary audiences mentioned
- Who they explicitly exclude or ignore

**The Problem They Lead With**
- Primary pain point in hero messaging
- How they frame the problem (technical? business? emotional?)
- What enemy/status quo they position against

**What They Avoid Talking About**
- Topics conspicuously absent
- Competitors they don't mention
- Limitations they don't address
- This reveals strategic weaknesses

**Positioning Shifts Over Time** (if Wayback data available)
- How has messaging changed?
- What did they used to emphasize that they don't now?
- What's new in their positioning?

### 2. PRODUCT ANALYSIS

**Core Capabilities**
- What can users actually DO with this product?
- What's the core workflow?
- What's table stakes vs. differentiated?

**Shipping Velocity & Patterns**
- How often do they ship? (from changelog)
- Big bets vs. incremental improvements ratio
- Areas getting most attention
- Technical debt signals (lots of bug fixes? stability updates?)

**Technical Architecture Signals**
- Tech stack (from job postings)
- Infrastructure choices (cloud, on-prem options)
- Integration architecture (API-first? embedded? standalone?)
- Scale indicators

**Product Maturity Indicators**
- Documentation depth and quality
- Edge case handling (from reviews)
- Error message sophistication
- Admin/enterprise features

### 3. MARKET STRATEGY

**Content/SEO Focus**
- What keywords are they targeting?
- What topics do they write about?
- Content format preferences (blog, video, webinars)
- This reveals what market they want to own

**Customer Proof Points**
- Who do they showcase in case studies?
- What outcomes do they highlight?
- What industries/segments featured?
- Customer size patterns (SMB? Enterprise? Mixed?)

**Partnership & Integration Ecosystem**
- Key integration partners
- What ecosystem are they betting on?
- Who do they think their customer uses?
- Partnership depth (marketing vs. deep product)

**Pricing Intelligence**
- Pricing model (seats, usage, flat, hybrid)
- Price points and tiers
- What's gated at each tier?
- Value metric (what do they charge for?)
- Enterprise/custom pricing signals
- Changes over time (if Wayback available)
- Discounting signals from reviews

### 4. VOICE OF CUSTOMER

**What Users Love** (from reviews)
- Consistent praise themes
- "Can't live without" features
- Emotional language patterns
- Recommendation likelihood

**Consistent Complaints**
- Repeated pain points across reviews
- Patterns by segment (SMB vs enterprise)
- Recency of complaints (old issues vs. new)
- Severity indicators

**Unmet Needs**
- Feature requests in reviews
- Workarounds users mention
- "I wish it could..." patterns
- Gaps users accept but resent

**Churn Signals**
- Why do people leave? (from negative reviews)
- Competitor mentions in reviews
- Deal-breaker patterns
- Implementation failure stories

### 5. STRATEGIC SIGNALS

**Investment Areas** (from job postings)
- Where are they hiring most?
- New roles that didn't exist before
- Seniority patterns (building vs. scaling)
- Geographic expansion signals
- Technical bets (AI, mobile, platform)

**Likely Roadmap**
Synthesize from:
- Job postings (what they're building capacity for)
- Changelog patterns (what's getting velocity)
- Content/marketing (what they're teasing)
- Partnership announcements
- Executive statements/interviews

**Strategic Bets They're Making**
- Platform vs. point solution
- Horizontal vs. vertical
- Self-serve vs. sales-led
- Build vs. buy vs. partner

### 6. VULNERABILITY MAP

**Positioning Gaps**
- Segments they ignore
- Use cases they don't address
- Problems they don't solve
- Messages they can't credibly claim

**Product Weaknesses**
- Consistent complaints
- Missing table-stakes features
- Technical limitations
- Integration gaps

**Segment Blindspots**
- Customer types underserved
- Industries not featured
- Company sizes ignored
- Use cases not supported

**Operational Risks**
- Hiring struggles (roles open too long)
- Technical debt signals
- Support quality issues
- Leadership/stability concerns

### 7. IMPLICATIONS FOR US

**Where We Can Win**
- Positioning opportunities
- Feature gaps we can fill
- Segments we can own
- Messages we can claim

**Where We Should Avoid**
- Their strengths we can't match
- Battles not worth fighting
- Segments they own

**Messaging Opportunities**
- Weaknesses we can highlight
- Contrast positioning options
- Proof points we need

**Feature Priorities**
- Table stakes we must have
- Differentiators to build
- Nice-to-haves to skip

---

## Output Format

Produce the teardown as a structured document with:
1. Executive Summary (3-4 sentences: who they are, their bet, their vulnerability, our opportunity)
2. Each section above with findings
3. Evidence quotes/data points supporting key claims
4. Confidence levels for inferences (high/medium/low based on data quality)

Be specific. Cite evidence. Distinguish between facts and inferences.

---

## Raw Data to Analyze

[PASTE RAW DATA FILES HERE]
```

---

## Quick Version (for faster analysis)

```
Analyze this competitor data and tell me:

1. **In one sentence each:**
   - Who they're for
   - Their main bet
   - Their biggest weakness
   - Our best opportunity against them

2. **Top 3 vulnerabilities** we could exploit (with evidence)

3. **Top 3 strengths** we shouldn't try to compete on directly

4. **What they're probably building next** (based on job postings + changelog + content)

5. **Recommended positioning against them** (one paragraph)

[PASTE DATA]
```

---

## Section-by-Section Deep Dives

If you want to go deeper on specific areas:

### Pricing Deep Dive
```
Analyze their pricing strategy:
- What's the value metric?
- How do tiers differ?
- What's gated at enterprise?
- Any discounting signals in reviews?
- How does this compare to market?
- Pricing power indicators?
- Recommendations for our pricing vs. theirs?

[PASTE PRICING PAGE + REVIEWS]
```

### Job Postings Deep Dive
```
Analyze these job postings to infer:
- Where are they investing most?
- What technical bets are they making?
- What organizational gaps do they have?
- What does seniority mix tell us?
- What's their likely 12-month roadmap based on hiring?

[PASTE JOB LISTINGS]
```

### Review Sentiment Deep Dive
```
Analyze these reviews to find:
- Top 5 things users love (with frequency)
- Top 5 consistent complaints (with frequency)
- Churn reasons mentioned
- Competitor comparisons made
- Feature requests/unmet needs
- Segment-specific patterns (enterprise vs SMB)
- Severity assessment for each issue

[PASTE REVIEWS]
```

---

## Tips for Best Analysis

1. **Look for patterns, not anecdotes** - One complaint isn't signal, five similar complaints is

2. **Note what's missing** - Absence of enterprise features, certain integrations, or market segments is signal

3. **Date everything** - Recent reviews matter more than old ones; recent job postings signal current priorities

4. **Cross-reference sources** - Job postings + changelog + content should tell a consistent story. Inconsistency is interesting.

5. **Distinguish facts from inferences** - "They have 500 employees" is fact. "They're struggling with scale" is inference. Label accordingly.
