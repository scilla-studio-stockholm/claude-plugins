# Manual Data Sources Guide

Some valuable competitive intelligence requires manual gathering. This guide explains what to look for and how to capture it.

---

## LinkedIn Intelligence

### Company Page
**URL pattern:** `linkedin.com/company/[company-name]`

**What to capture:**
- Employee count and growth (LinkedIn shows "X employees" and sometimes growth %)
- Employee distribution by function (click "People" → filter by department)
- Recent posts from company page
- "People also viewed" competitors

**Save as:** `raw/linkedin_company.md`

### Employee Posts
**How to find:** Search LinkedIn for company name, filter to Posts

**What to look for:**
- What are employees proud of shipping?
- What are they complaining about (carefully)?
- Conference talks, blog posts they share
- Hiring managers talking about what they're building

**What to capture:** Screenshot or copy 5-10 most revealing posts

**Save as:** `raw/linkedin_posts.md`

### Hiring Velocity
**How to check:** Company page → Jobs tab

**What to capture:**
- Total open roles
- Roles by department
- How long jobs have been posted (signals hard-to-fill roles)
- New roles vs. backfills

**Save as:** Include in `raw/linkedin_company.md`

---

## Wayback Machine (Pricing & Positioning History)

### How to Use
1. Go to `web.archive.org`
2. Enter competitor's pricing page URL
3. Look at snapshots from 6mo, 1yr, 2yr ago

### What to Capture
- Pricing changes (amounts, tiers, packaging)
- Messaging changes on homepage
- Feature additions/removals from pricing page
- Target audience shifts

**Save as:** `raw/wayback_analysis.md`

**Format:**
```markdown
# Pricing History: [Company]

## January 2024
- Starter: $X/mo
- Pro: $Y/mo
- Enterprise: Custom

## June 2023
- Starter: $X/mo (was $Z - increased)
- Pro: $Y/mo
- Note: Added "Team" tier between Starter and Pro

## Observations
- Prices increased 20% in past year
- Shifted from per-seat to usage-based for enterprise
- Removed free tier in 2023
```

---

## GitHub Intelligence (if open source)

### Repository Health
**What to check:**
- Stars and growth trend
- Commit frequency
- Issue response time
- PR merge velocity
- Contributor count (employees vs. community)

### Issues & Discussions
**What to look for:**
- Feature requests with most 👍
- Bugs that stay open long
- Community frustrations
- Roadmap hints from maintainers

### Code Signals
**What to look for:**
- Technology choices
- Code quality indicators
- Documentation quality
- Test coverage

**Save as:** `raw/github_analysis.md`

---

## Reddit & Community Sentiment

### How to Find
- Search Reddit for company/product name
- Check relevant subreddits (r/SaaS, r/ProductManagement, industry-specific)
- Search Twitter/X for product mentions
- Check Product Hunt comments
- Look for Hacker News discussions

### What to Capture
- Unfiltered opinions (people are honest on Reddit)
- Alternatives people recommend
- Specific complaints and praise
- Migration stories (switching from/to)

**Save as:** `raw/community_sentiment.md`

**Format:**
```markdown
# Community Sentiment: [Company]

## Reddit Mentions

### r/[subreddit] - [date]
"[Quote about product]"
Context: [Why they said this]
Sentiment: Positive/Negative/Mixed

### r/[subreddit] - [date]
...

## Key Themes
- Users frequently mention [X]
- Common complaint: [Y]
- Often compared to: [Z competitor]
```

---

## Case Studies & Customer Evidence

### What to Capture
- Customer names and logos
- Industries represented
- Company sizes featured
- Outcomes/metrics highlighted
- Implementation timeline mentioned
- Quotes from customers

### Where to Find
- /customers or /case-studies page
- Press releases
- Customer interviews/videos
- Conference presentations
- Logos on homepage (often more than case studies)

**Save as:** `raw/customer_evidence.md`

**Format:**
```markdown
# Customer Evidence: [Company]

## Case Studies

### [Customer Name]
- Industry: [X]
- Size: [employees/revenue if mentioned]
- Outcome highlighted: [metric]
- Quote: "[what they said]"
- What they use it for: [use case]

## Logo Wall Analysis
- Total logos: ~[N]
- Enterprise names: [list recognizable ones]
- Industries represented: [list]
- Notable absences: [what types NOT shown]
```

---

## Integration & Partnership Analysis

### What to Capture
- Featured integrations (homepage vs. integrations page)
- Integration depth (deep vs. surface-level)
- API documentation quality
- Partner program details
- Co-marketing partnerships

### Where to Find
- /integrations page
- API documentation
- Partner directory
- Press releases about partnerships
- App marketplaces (Salesforce AppExchange, etc.)

**Save as:** `raw/integrations.md`

---

## Financial & Funding Intelligence

### What to Capture
- Funding history (Crunchbase)
- Investor names
- Valuation if known
- Revenue estimates (from press, employee count estimates)
- Profitability signals

### Where to Find
- Crunchbase
- PitchBook (if you have access)
- Press releases
- LinkedIn headcount trends
- Job posting volume trends

**Save as:** `raw/financial_intel.md`

---

## Quick Capture Template

When gathering manually, save each source with this header:

```markdown
# [Source Type]: [Company Name]
Captured: [Date]
URL: [source URL]

## Raw Content

[Paste content here]

## Key Observations

- [Your notes on what stands out]
- [Patterns you notice]
- [Questions this raises]
```

---

## Checklist Before Analysis

Before running the LLM analysis, confirm you have:

- [ ] Homepage and key pages (script)
- [ ] Pricing page with tier details
- [ ] Changelog/release notes (past 6 months)
- [ ] Job postings (current)
- [ ] G2 or Capterra reviews (20+ reviews ideal)
- [ ] App store reviews if applicable
- [ ] LinkedIn company data
- [ ] At least one historical Wayback snapshot
- [ ] Community mentions if available
- [ ] Customer evidence summary

More data = better analysis. But even partial data produces useful insights.
