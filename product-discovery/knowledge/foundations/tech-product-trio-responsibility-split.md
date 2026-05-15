---
title: Tech, Product, and the Trio — Who Owns What
date: 2026-04-14
tags: [frameworks, product-operating-model, tech-organization, product-trio, responsibility, cagan, cutler, torres]
purpose: Framework reference describing how responsibilities distribute between the tech organization, the product organization, the product trio, and the extended delivery team. Used to make visible what each group still owns independently once discovery becomes a shared activity, and how collaboration extends into day-to-day delivery.

---

# Tech, Product, and the Trio — Who Owns What

When an organization works in a product operating model, discovery becomes a genuinely shared activity between product, design, and engineering. That shift is well described by Cagan, Torres, and others. Less often described is what remains distinct: the tech organization keeps a substantial scope of its own, the product organization keeps a substantial scope of its own, and delivery inside the extended team is itself a collaborative activity rather than a handoff from the trio to engineering.

This document is a reference map of those scopes, written as observation rather than prescription. Real organizations vary; the boundaries sketched here are starting points for conversation, not rules.

## Five scopes in the product operating model

| Scope | Who carries it | Character of the work |
|---|---|---|
| **Tech organization** | Engineering leadership, platform teams, tech leads | Architecture, platform, engineering practice, technical health |
| **Product organization** | Product leadership, portfolio owners, marketing, commercial | Portfolio, pricing, positioning, product strategy |
| **Product trio** | PM + designer + tech lead | Discovery: opportunities, assumptions, solution shaping |
| **Extended product team** | Trio + engineers + sometimes QA, data, ops | Delivery: backlog, sprint work, day-to-day operation |
| **Product leadership together** | CPO and CTO (or equivalents) | Cross-cutting tradeoffs, funding, organizational design |

The trio is the standing cross-functional unit for discovery (Cagan; Torres). The extended team is where discovery outputs become running software. Neither replaces the organizations they come from.

## What the tech organization tends to own on its own

Across the literature, these areas remain with engineering even in mature product-model companies:

- System and platform architecture. The trio consumes architectural capability; the tech organization sets the direction.
- Engineering practices — CI/CD, testing, code review, branching, observability, deployment infrastructure. Cagan's delivery principles (13–16) point here, but the specifics are engineering's to define.
- Technical standards — language choices, framework selection, API standards, data schemas at the infrastructure level.
- Technical hiring and engineering career development.
- Tech debt strategy. Which debt matters, which is tolerable, how much capacity remediation gets. Trios flag debt that blocks their work; engineering owns the strategy.
- Security, privacy, and compliance baseline.
- Platform roadmap at the capability level. Informed by product strategy, but shaped by the platform organization.

Cagan's framing in *Empowered*: technical health is the tech organization's accountability. Product empowerment does not remove that accountability — it changes the interface through which product and tech meet.

## What the product organization tends to own on its own

- Product portfolio. Which products exist, which are retired, which are acquired or partnered.
- Pricing and packaging. Commercial models, tiers, SKUs.
- Market segmentation and ICP.
- Go-to-market. Positioning, launch, sales enablement, marketing narrative.
- Product vision and product strategy. The longer-horizon direction trios work inside of (Cagan, principles 5–8).
- Portfolio-level prioritization. Which problems matter most across the company. Teams receive problems; leadership decides which problems.

Trios operate inside this strategic context. The trio does not set portfolio, pricing, or which problem the company should care about most.

## What the trio owns together in discovery

This is the space that did not exist in the IT or feature-team model. Discovery work requires three perspectives at once — value and viability (PM), usability (designer), feasibility (tech lead) — and splitting it across handoffs tends to degrade it (Torres).

The trio's joint work:

- Maintaining an opportunity-solution tree or equivalent visual artifact.
- Weekly customer interviews with all three roles present.
- Designing and running assumption tests.
- Solution shaping: prototypes, narrowing toward what to build.
- Defining team-level outcomes from the strategic problem.
- Deciding what to pursue, park, or kill — with equal say.

What the trio does not decide alone: architecture for the chosen solution (involves the rest of engineering), portfolio-level tradeoffs (product leadership), commercial terms (product leadership).

## Delivery and the extended product team

Discovery is shared work between three people. Delivery is shared work between the trio and the rest of the engineering team — plus anyone else the product depends on (data, QA, ops, sometimes designers from adjacent teams). Treating delivery as a handoff from the trio to engineering tends to reintroduce the failure modes the product model was meant to address.

Several activities sit in this extended-team space:

### Backlog and roadmap

The product manager owns the roadmap and the backlog, and owns them *in collaboration* with the trio and the extended team.

- The PM typically carries the most context on customer insight, commercial implications, and strategic fit, and that context is needed in backlog prioritization — not only in discovery.
- The trio shapes what enters the backlog through discovery outputs: validated opportunities, assumption test results, prototype findings.
- The extended engineering team brings feasibility detail, sequencing, risk, and dependency context that changes what prioritization is realistic.
- Leaving prioritization to engineering alone risks losing the value-and-viability signal the PM carries. Leaving it to the PM alone risks decisions that ignore technical reality. The ongoing conversation between them is the point.

### Sprint planning and day-to-day delivery

- Discovery outputs (OST, assumption test results, prototype findings) are shared with the full team continuously, not revealed at sprint planning (Torres; multiple cases in *Empowered*).
- The trio brings the "what and why." The full team co-owns the "how and when."
- The PM stays present during delivery — answering questions, making tradeoffs on scope, catching drift from the intended outcome. The PM's input during sprint execution is often where risk shows up first.
- The tech lead acts as the bridge into the wider engineering team for architectural review, feasibility spikes, and sequencing.
- Designers continue to be involved during build, not only during shaping.

### Assumption tests that require engineering work

- The trio designs the test; the engineering team runs it as a sprint story (Torres, Orion Labs case).
- Research spikes and technical proofs of concept are engineering-executed, trio-scoped.

### Incidents, production operation, and feedback loops

- On-call, incident response, and operational fixes sit with the engineering team.
- Technical signals from production — uptime, performance, error rates — sit with engineering.
- Behavioural and outcome signals from production — how customers actually use the product, where they drop off, which segments behave differently, whether the intended outcome is moving — are analysed by the PM and designer, often with a dedicated product analyst or data partner when one exists. This analysis serves two purposes at once: measuring the effect of what was delivered, and informing the next round of discovery.
- Instrumentation and monitoring (Cagan, principles 14–15) are shared: engineering builds the observability, the trio and its analytics support read the signal.

### Why the extended team matters for risk

Handoffs between discovery and delivery are where outcome risk tends to accumulate: scope creep, quiet de-scoping, misinterpreted acceptance criteria, missed edge cases that were never surfaced because the PM was not in the room. Keeping the PM, designer, and engineers in continuous contact during delivery is one of the most frequently reported practices in well-functioning product teams (Torres, 2024 CDH Benchmark). The cost of the PM being absent during delivery is often invisible until it is not.

## Grey zones worth naming explicitly

Every organization has areas where the boundaries are ambiguous. Naming them tends to be more useful than resolving them.

| Grey zone | What typically has to be worked out |
|---|---|
| Platform roadmap | Platform team shapes it, but shared or inherited objectives tie it to experience teams (Cagan). Not decided by a single product trio. |
| Tech debt prioritization | Engineering owns the strategy; trios flag blockers; product leadership influences capacity allocation. |
| Developer experience investments | Platform team decides, with end-user value as the primary justification — not developer convenience (Cagan's three-constituency rule). |
| Technical hiring priorities | Engineering owns, informed by what the next 12 months of product work will need. |
| Architectural shifts that change product possibilities | Can be initiated by either side; the decision usually lives at the leadership level. |
| Third-party vendors and SaaS | Scope-dependent. If it shapes customer experience, the trio is involved; if it is pure infrastructure, engineering decides. |
| Internal tooling | Treated as platform-as-a-product when the investment is large enough that multiple teams depend on it and it needs its own roadmap; otherwise owned by the team that uses it most. |
| Scope changes during delivery | The trio together, with the extended engineering team's sequencing and feasibility input. Not something the engineering team decides on its own, and not something the PM decides on their own. |

## Two scenarios

Short walkthroughs. Bold labels match the five scopes. Each bullet ends with the section it illustrates.

### Scenario 1 — A B2B SaaS company adds self-service onboarding

Sales-assisted onboarding takes weeks. 90-day churn is high. Segment X needs a self-serve path.

- **Product organization** sets the strategic problem: cut time-to-first-value for segment X without sales assistance. → *Product organization*
- **Product trio** runs discovery — interviews, experience map, three opportunities, assumption tests on prototypes. → *Trio in discovery*
- **Tech lead bridges to engineering**: identity service can't handle self-serve at target volume. Spike scoped as a sprint story. → *Sprint planning*; *Assumption tests requiring engineering*
- **Product leadership together**: the identity fix would slow two other teams. CPO and CTO choose a lightweight workaround now, platform change next quarter. → *Product leadership together*
- **Extended team** co-owns backlog and sprint work. PM keeps prioritizing during build and makes scope calls on edge cases (e.g. existing SSO customers). Designer iterates as staging data surfaces. → *Backlog and roadmap*; *Sprint planning*
- **Product organization** sets pricing tier and sales positioning. → *Product organization*
- **Tech organization** ensures feature flags, observability, rollback, security baseline. → *Tech organization*
- **After launch**: engineering owns on-call and technical signals. PM, designer, product analyst read activation, time-to-first-value, retention — feeding next discovery cycle. → *Feedback loops*

**Connects to:** [Product Trio — Operational Practices](product-trio-operational-practices.md); [Product Operating Model — Marty Cagan / SVPG](product-operating-model-marty-cagan.md).

### Scenario 2 — A geodata company consolidates product APIs onto a shared platform

Several products, each with its own API, auth, metering, docs. Customers integrate against inconsistent patterns; teams maintain duplicate infrastructure. A platform team is set up to build a shared API platform over 18 months.

- **Tech organization** proposes the consolidation and owns technical direction — gateway, identity model, metering, deprecation path. → *Tech organization*
- **Product leadership together** work the tradeoff: which product work slows, what packaging and pricing opportunities open up, in what sequence teams migrate. → *Product leadership together*; grey zone *Architectural shifts*
- **Experience-team trios** contribute input on commitments in flight and discovery bets that depend on the new platform. → *Trio in discovery*
- **The platform team is itself a product team** with its own trio — platform PM + platform tech lead, designer when user-facing surfaces are involved (developer portal, admin tooling). Platform-as-a-product: discovery with its users, platform roadmap, value/feasibility tradeoffs, backlog run like any product team. → [Empowered Platform Teams](empowered-platform-teams-cagan.md)
- **Three-constituency prioritization**: end users first, experience teams second, developer convenience last. → [Empowered Platform Teams](empowered-platform-teams-cagan.md)
- **Shared or inherited objectives** tie the platform trio to the experience teams — accountable for experience teams' customers continuing to get value, not only for shipping on time. → [Empowered Platform Teams](empowered-platform-teams-cagan.md)
- **Product organization** decides pricing, packaging, commercial narrative for the consolidated platform. → *Product organization*
- **No experience-team trio owns the consolidation.** The platform trio owns it, coordinated through shared objectives and commercial framing from product leadership.

**Connects to:** [Empowered Platform Teams — Marty Cagan / SVPG](empowered-platform-teams-cagan.md) throughout; [Product Operating Model — Marty Cagan / SVPG](product-operating-model-marty-cagan.md).

## Observations that hold across the split

- Tech does not dissolve into product. Expanding the shared space (the trio, the extended team) does not remove tech's independent scope.
- Product does not absorb tech's decisions. Architecture, platform, and engineering practices remain with the tech organization.
- Discovery and delivery are both shared spaces, but with different shapes — three people around an OST versus the whole team around a backlog.
- PM involvement does not end when discovery ends. Value and viability continue to need a voice during build.
- Leadership collaborates at the top. When CPO and CTO disagree in public, the teams below them tend to fracture along the same line.
- Grey zones are normal. They are worth naming, not pretending away.

## Related knowledge

- [Product Operating Model — Marty Cagan / SVPG](product-operating-model-marty-cagan.md)
- [Empowered Platform Teams — Marty Cagan / SVPG](empowered-platform-teams-cagan.md)
- [Product Trio — Operational Practices](product-trio-operational-practices.md)

## Sources

- Cagan, Marty. *Inspired* (2nd ed., 2017). Wiley.
- Cagan, Marty. *Empowered* (2020). Wiley. Especially Chapter 43: "Empowering Platform Teams."
- Cagan, Marty. *Transformed* (2024). Wiley.
- [The Product Operating Model — SVPG](https://www.svpg.com/the-product-operating-model/)
- [Platform Product Management — SVPG](https://www.svpg.com/platform-product-management/)
- [Factors in Structuring a Product Organization — SVPG](https://www.svpg.com/factors-in-structuring-a-product-organization/)
- Torres, Teresa. *Continuous Discovery Habits* (2021). Product Talk LLC.
- [Core Concept: The Product Trio — Product Talk](https://www.producttalk.org/product-trio/)
- [Ask Teresa: Does the Engineer in the Product Trio Need to be the Tech Lead? — Product Talk (2024)](https://www.producttalk.org/2024/10/engineer-lead-product-trio/)
- [Product in Practice: Assumption Testing with Engineers at Orion Labs — Product Talk](https://www.producttalk.org/2022/02/assumption-testing-engineers/)
- Cutler, John. *The Beautiful Mess* (Substack). Writing on feature factory, work shape, internal customer, output vs. outcome.
- [12 Signs You're Working in a Feature Factory — John Cutler](https://cutle.fish/blog/12-signs-youre-working-in-a-feature-factory)
