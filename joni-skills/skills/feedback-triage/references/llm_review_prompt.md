# LLM Review Prompt for Feedback Triage

After running the automated triage, use Claude to refine and deepen the analysis.

---

## The Prompt

```
I've run automated triage on customer feedback. Review this output and help me:

1. **Refine categories**: Are any themes too broad and should be split? Are any too similar and should be merged?

2. **Find what I missed**: What patterns or themes might the keyword-based triage have overlooked? Look for:
   - Subtle frustrations not using obvious keywords
   - Feature requests disguised as complaints
   - Underlying needs behind surface requests

3. **Prioritize**: Given the themes and urgent items, what should I focus on first? Consider:
   - Volume (how many people mentioned it)
   - Severity (how much does it hurt when it happens)
   - Solvability (can we actually fix this)

4. **Write executive summary**: 3-4 sentences I can share with leadership covering the most important findings.

5. **Recommend actions**: For the top 3 themes, suggest a concrete next step.

Here's the triaged feedback:

[PASTE TRIAGE OUTPUT HERE]
```

---

## Example Usage

**Automated triage output (excerpt):**
```
### Usability (23 entries)
- "I couldn't figure out how to export my data"
- "Where is the settings page? I've been looking for 10 minutes"
- "The button to save is too small on mobile"
...

### Feature Requests (18 entries)
- "I wish there was a dark mode"
- "Please add keyboard shortcuts"
...
```

**Claude's refined analysis:**
```
## Refined Categories

I'd suggest splitting "Usability" into:
- **Navigation/Findability** (12 entries) - people can't find features
- **Mobile Experience** (7 entries) - touch targets, responsive issues  
- **Data Management** (4 entries) - export, import, backup concerns

The "dark mode" requests should move to **Visual Preferences** since they're distinct from functional feature requests.

## Missed Patterns

Looking deeper, I notice:
- 5 entries mention "team" or "collaborate" - there's latent demand for multi-user features not captured in your categories
- Several "feature requests" are actually workarounds for poor discoverability ("I wish there was a shortcut to X" often means "I can't find X")

## Priority Recommendation

1. **Navigation/Findability** - High volume, relatively easy fix (better labeling, search)
2. **Mobile Experience** - Growing segment, competitive table stakes
3. **Team Features** - Expansion opportunity, could drive upgrades

## Executive Summary

Users are struggling to find existing features, with 23 usability complaints primarily around navigation. Mobile experience is a growing pain point. There's latent demand for team collaboration features that could drive account expansion. Recommend prioritizing in-app search/navigation improvements as quick win.
```

---

## Quick Version (for smaller datasets)

```
Review this customer feedback and tell me:
1. Top 3 themes and how many mentions each
2. Most urgent items needing immediate attention
3. Any opportunities (expansion signals, high praise)
4. One sentence summary for stakeholders

[PASTE FEEDBACK]
```

---

## Tips for Best Results

1. **Include the full triage output** - Claude needs context on volume and distribution

2. **Add your current priorities** - "We're focused on mobile this quarter" helps Claude prioritize relevant findings

3. **Ask follow-up questions** - "Tell me more about the navigation issues" or "What specific mobile problems are mentioned?"

4. **Request evidence** - "Which quotes best support the team features opportunity?"
