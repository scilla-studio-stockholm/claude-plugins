---
name: competitive-teardown
description: Generate deep, strategic competitive analysis that goes far beyond surface-level feature comparisons. Use when a PM needs to understand a competitor's positioning, roadmap signals, vulnerabilities, and strategic direction. Analyzes website, changelog, job postings, reviews, pricing history, content strategy, and community sentiment to surface hidden insights.
user_invocable: true
---

# Competitive Teardown Generator

Produces strategic competitive intelligence by analyzing multiple public data sources and synthesizing patterns most competitors miss.

## Quick Start

1. Run data gathering: `python scripts/gather_intel.py "CompanyName" --url https://competitor.com --output /tmp/teardown/company_name`
2. Read the raw data files (homepage, pricing, about, etc.)
3. Search the web for reviews (AppSumo, G2, Trustpilot, Reddit) and competitor comparisons
4. Synthesize into a structured teardown document
5. Save to `output/company_name/analysis/teardown.md`

## What Makes This Different

Most competitive analysis is shallow - homepage copy, pricing, feature lists. This skill digs into **signals that reveal strategy**:

| Source | Surface Read | Strategic Signal |
|--------|--------------|------------------|
| Job postings | "They're hiring" | Where they're investing, what they can't build internally, tech stack bets |
| Changelog | "They shipped X" | Shipping velocity, priorities, technical debt patterns |
| App reviews | "Users complain about Y" | Vulnerabilities you can exploit, unmet needs |
| Pricing history | "They cost $X" | Positioning shifts, market pressure, discounting desperation |
| Content/SEO | "They blog about Z" | Market they're chasing, keywords they want to own |
| Support docs | "They document W" | Product complexity, edge cases, maturity |

## Data Sources Analyzed

### Primary Sources (Script Gathers)
- **Website**: Homepage, pricing, about, customers, careers pages
- **Changelog/Release notes**: Shipping patterns, feature velocity
- **Job postings**: Roles, tech stack, growth areas, organizational gaps
- **App Store/Play Store reviews**: User sentiment, pain points, praise patterns
- **G2/Capterra reviews**: Enterprise buyer perspective, implementation issues

### Secondary Sources (Web Search)
Use `WebSearch` and `WebFetch` to gather:
- **AppSumo reviews**: Often has detailed user feedback, complaints, and ratings
- **G2/Capterra/Trustpilot**: Enterprise buyer perspective, verified reviews
- **Reddit/Communities**: Unfiltered user sentiment, workarounds, complaints
- **Competitor comparisons**: "[Company] vs [Competitor]" articles reveal positioning
- **Industry reviews**: "[Company] review 2024 2025" surfaces recent coverage

Example searches:
```
"Company Name" reviews reddit 2024 2025
"Company Name" vs competitors alternatives
"Company Name" complaints problems issues
```

### Derived Analysis (LLM Synthesis)
- **Positioning gaps**: Where they're weak or silent
- **Roadmap signals**: What they're likely building next
- **Vulnerability map**: Where you can win
- **Pricing strategy**: How they capture value
- **Content strategy**: What market they want

## Usage

### Basic Teardown
```bash
python scripts/gather_intel.py "Competitor" --url https://competitor.com
```

### Full Analysis with All Sources
```bash
python scripts/gather_intel.py "Competitor" \
  --url https://competitor.com \
  --changelog https://competitor.com/changelog \
  --careers https://competitor.com/careers \
  --g2 https://g2.com/products/competitor/reviews \
  --appstore https://apps.apple.com/app/competitor
```

### Output Structure
```
output/competitor_name/
├── raw/
│   ├── homepage.md
│   ├── pricing.md
│   ├── careers.md
│   ├── changelog.md
│   ├── reviews_appstore.md
│   ├── reviews_g2.md
│   └── metadata.json
├── analysis/
│   └── teardown.md (after LLM analysis)
└── summary.md
```

## Two-Stage Workflow

### Stage 1: Data Gathering (Script)

The script crawls and structures raw data from public sources.

**What it captures:**
- Full text from key pages
- Job posting titles and descriptions
- Review text and ratings
- Changelog entries with dates
- Metadata (last updated, page structure)

**Limitations:**
- Some sites block automated access (Notion, some enterprise sites)
- Cannot access gated content
- Rate-limited on some sites

**JavaScript-Rendered Pages:**
The script uses Playwright (headless browser) to capture JS-rendered pages like signup flows, checkout pages, and app interfaces. Install with:
```bash
pip install playwright && playwright install chromium
```

**Pricing Verification:**
The script automatically captures accurate pricing by:
1. Using Playwright (headless browser) for the /pricing page - many sites render pricing via JavaScript
2. **Clicking the "Monthly" toggle** - most SaaS sites default to showing discounted annual pricing; the script clicks "Monthly" to capture true monthly rates
3. Trying common signup URLs (app.company.com/signup, etc.) to verify checkout pricing
4. Saving as `pricing.md` with a note about which billing toggle was selected
5. Flagging a warning if actual checkout pricing couldn't be verified

**Common pricing gotchas:**
- Marketing page shows annual pricing by default (e.g., "$199/mo" is actually annual, monthly is "$249/mo")
- Different pricing shown to different visitor segments (A/B testing)
- Legacy pricing pages still indexed but not available at checkout

### Stage 2: Strategic Analysis (LLM)

After gathering raw data, Claude synthesizes the teardown by:
1. Reading all raw data files from the script
2. Running web searches for reviews, complaints, and competitor comparisons
3. Fetching and analyzing review pages (AppSumo, G2, etc.)
4. Writing a structured teardown document

**Analysis Framework:**

1. **Positioning Analysis**
   - Who do they say they're for?
   - What problem do they lead with?
   - What do they NOT talk about?

2. **Product Maturity Signals**
   - Changelog velocity and patterns
   - Documentation depth
   - Edge case handling in reviews

3. **Strategic Direction**
   - Job postings → investment areas
   - Content strategy → market aspirations
   - Partnership/integration bets

4. **Vulnerability Mapping**
   - Consistent complaints in reviews
   - Gaps in positioning
   - Segments they ignore
   - Technical debt signals

5. **Pricing Intelligence**
   - Model (seats, usage, flat)
   - Changes over time
   - Discounting signals
   - Value metric alignment

6. **Roadmap Prediction**
   - Job postings + changelog + content = likely next moves

## Output: The Teardown Document

```markdown
# Competitive Teardown: [Company]
Generated: [date]

## Executive Summary
[3-4 sentences: Who they are, their bet, their vulnerability, your opportunity]

## Company Snapshot
- Founded: 
- Funding: 
- Headcount (LinkedIn):
- Tech stack (from job posts):

## Positioning Analysis
### Who They Say They're For
### The Problem They Lead With
### What They Avoid Talking About
### Positioning Shifts Over Time

## Product Analysis
### Core Capabilities
### Recent Shipping Patterns
### Technical Architecture Signals
### Maturity Indicators

## Market Strategy
### Content/SEO Focus
### Customer Proof Points
### Partnership Ecosystem
### Pricing Model & Changes

## Voice of Customer
### What Users Love
### Consistent Complaints
### Unmet Needs
### Churn Signals

## Strategic Signals
### Where They're Investing (Job Postings)
### Likely Roadmap
### Bets They're Making

## Vulnerability Map
### Positioning Gaps
### Product Weaknesses
### Segment Blindspots
### Operational Risks

## Implications For Us
### Where We Can Win
### Where We Should Avoid
### Messaging Opportunities
### Feature Priorities

## Evidence Appendix
[Key quotes and data points backing each section]

## Confidence Assessment
| Section | Confidence | Notes |
|---------|------------|-------|
| Positioning | High/Medium/Low | Source quality |
| Pricing | High/Medium/Low | Verified at checkout? |
| Voice of Customer | High/Medium/Low | Review volume and recency |
```

## TL;DR Output

After the full teardown, provide a short summary:

```markdown
## TL;DR

**Who they are:** [One sentence description and positioning]

**Their bet:** [Key strategic bet they're making]

**Their vulnerability:** [Top 3-4 weaknesses you can exploit]

**Your opportunity:** [Where to compete against them]
```

## When to Use

- Entering a new market
- Preparing for sales battlecards
- Roadmap prioritization
- Pricing strategy
- Positioning refresh
- Board/investor updates
- Win/loss analysis context

## Tips for Best Results

1. **Always verify pricing with Monthly toggle** - Most sites default to annual; click Monthly to get true rates

2. **Search for complaints specifically** - "[Company] complaints problems issues" surfaces real pain points

3. **Check AppSumo reviews** - Often more candid than G2/Capterra due to lifetime deal buyers

4. **Look for what's missing** - Silence is signal (segments not mentioned, features not highlighted, enterprise not addressed)

5. **Note team/seat limits** - Many tools cap seats on lower tiers, revealing enterprise gaps

6. **Include confidence levels** - Be honest about what you verified vs inferred
