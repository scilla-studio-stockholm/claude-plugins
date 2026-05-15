---
title: Product Trio — Operational Practices
date: 2026-03-05
tags: [frameworks, product-trio, continuous-discovery, teresa-torres, collaboration, discovery]
purpose: Kunskapssammanfattning av hur produkttrion fungerar operativt. Referens for triocoaching.

---

# Product Trio — Operational Practices

How high-functioning product trios actually operate day-to-day. Based on Teresa Torres' research, the 2024 CDH Benchmark Survey (n=680), and cross-referenced findings from 2022 (n≈2,000).

## What a Product Trio Is

A cross-functional unit of three: **product manager + designer + engineer**. Sometimes quads or quints depending on the org, but three is the minimum viable composition.

Not a committee. Not a hand-off chain. A small team with **joint ownership** of product decisions — across both discovery and delivery.

## The Keystone Habit: Weekly Customer Interviews Together

The single most reported practice of high-functioning trios: **all three roles interview customers together, at least weekly**.

Not PM-only research handed downstream. Everyone hears the same things, builds the same mental model, and avoids the "telephone game" of secondhand insights. This is what Torres calls the shift from *individual* to *team-based* continuous discovery.

Minimum viable definition of continuous discovery: "At minimum weekly touchpoints with customers by the team that's building the product, where they conduct small research activities in pursuit of a desired product outcome."

## Core Operational Practices

### 1. Shared visual artifacts

- Each member draws their own version of the customer experience map first
- Then the trio co-creates one shared map — a synthesis of all three perspectives
- The Opportunity Solution Tree (OST) is maintained collectively, not PM-owned
- Externalizing thinking visually is non-negotiable for staying aligned across three different functional lenses

#### What the experience map looks like

Torres' experience map is a **directed graph** — not a swimlane or staged journey map.

- **Nodes** = a specific user action or event (a discrete moment in time)
- **Links** = arrows showing transitions between moments
- **Annotations** = speech bubbles or notes capturing what users think/feel/do at that node

Format is deliberately simple: boxes, arrows, stick figures. Torres says to use as few words as possible because "language is vague and drawing is more concrete."

The map captures not just the happy path but also where users get stuck, loop back, work around problems, or give up. The gaps and disagreements between the trio's individual maps are the point — they become the interview agenda.

**How it differs from other map types:**


| Type                   | Perspective    | Structure                       | Purpose                                     |
| ---------------------- | -------------- | ------------------------------- | ------------------------------------------- |
| Torres' experience map | User's journey | Directed graph (nodes + arrows) | Expose knowledge gaps, guide interviews     |
| Customer journey map   | User's journey | Swimlane by stage               | Understand emotions + touchpoints           |
| Service blueprint      | Organization's | Swimlanes incl. backstage       | Document how the org creates the experience |


Torres' version is simpler and more tactical than a typical journey map — it's a living hypothesis document updated as interviews happen, not a polished deliverable.

### 2. Equal say in decision-making

From the 2024 CDH Benchmark Survey: the more equal decision-making felt, the more satisfied people were — both with their team and their company.

Power imbalances toward PM are the single most cited dysfunction.

### 3. Time spent together (quantity matters)

Simple correlation from the survey data: **more hours together → more satisfaction**.

No magic cadence or ritual structure is reported as universal. The quantity of shared time matters more than any specific meeting format.

### 4. Co-located assumption testing

After interviewing for opportunities, the trio together designs and runs small experiments. Engineers are involved *before* specs exist, not after.

Two repeating activities, week over week:

1. **Customer interviewing** — to discover opportunities
2. **Assumption testing** — to discover solutions

## 12 Reported Hurdles (Product Talk, 2024)

Research identified 12 categories of challenges. The most structurally dangerous:


| Hurdle                   | Pattern                                                                       |
| ------------------------ | ----------------------------------------------------------------------------- |
| PM dominance             | PM held accountable for outcomes → takes over, others disengage               |
| Engineer disengagement   | "My job is to build, not challenge assumptions"                               |
| Designer split attention | Designer spans multiple teams or is a contractor → missing context, low voice |
| Technical debt priority  | Engineering concerns crowd out time for discovery                             |


The traditional handoff model — PM writes requirements → designer designs → engineer builds — is described as "rife with challenges" and the root cause of most scope, budget, and timeline failures.

## What the Data Shows

From the 2024 CDH Benchmark Survey (Sep–Nov 2024, n=680), replicated from 2022 (n≈2,000):

- People working in product trios report **higher satisfaction** with both their team and their company
- The effect strengthens with: more time spent together, more equal decision-making, and longer duration of working together

## Implications for Metria (FAST and Mercury)

Risk factors likely present in both teams based on enterprise context:

- PM-heavy accountability structures (common in Swedish enterprise)
- Engineers who haven't been invited into discovery before
- Designers potentially spread thin across teams

Highest-leverage first intervention: **get all three roles into the same customer interview**, before any OST or opportunity structure work. That shared experience is what generates the common knowledge base everything else depends on.

## The Trio and the Extended Team

### The fundamental principle

The trio leads discovery — it does not own it exclusively. Torres is explicit: the intent is **not to exclude** other engineers. The trio exists because it's impractical to involve 5 engineers in every customer interview, every assumption test, every decision. The trio is the *standing* cross-functional unit. Everyone else participates selectively and purposefully.

### Who the engineer in the trio actually is

The engineering representative should be the **tech lead** — but not in a managerial sense. Not a promotion, not seniority over other engineers. Just the engineer most involved in discovery.

**Real case — Ramsey Solutions** (40+ squads, each 4–5 engineers + a trio): They originally used the term "engineering lead" and it backfired. Some engineers thought it was a promotion; others feared it would stall their technical career. Their fix: made it a **rotating role**, swapped every quarter or two. Any engineer can do a stint in the trio. This kept discovery skills spreading across the team and removed the career-risk perception. The rotating trio engineer still occasionally ships code to stay connected to delivery, but discovery is their primary job during that rotation.

### What the trio decides alone vs. what involves the rest

| Decision type | Who is involved |
|---------------|-----------------|
| Which opportunities to pursue (OST prioritization) | Trio |
| Which assumptions to test | Trio |
| Solution direction / prototypes to explore | Trio |
| Feasibility: architecture, data model, infrastructure | Trio engineer + rest of engineering team |
| Sprint planning and what gets built | Whole team |
| Actual delivery / building | Whole engineering team |
| Assumption tests requiring engineering spikes | Trio designs it, engineer adds it as a user story to the sprint |

### When the extended team gets invited in

**Brainstorming / ideation sessions**
Once the trio has identified a target opportunity, the whole team can be brought in to generate solution ideas. Different engineering perspectives surface implementation options the trio wouldn't see on their own.

**Assumption tests that require engineering work**
Simple prototype tests are run by the trio. When testing technical feasibility — a research spike, a proof of concept — the trio designs the test and engineers execute it as a regular sprint story.

**Real case — Orion Labs**: Once engineers had been through brainstorming and story mapping alongside the trio, they could also participate in user testing sessions. The shared upstream context made alignment fast and reduced the friction when work hit delivery.

**Feasibility reviews**
The trio engineer does not make solo architecture calls. Anything touching system design, data model, or infrastructure is reviewed with the broader engineering team before a solution is committed to.

**Sprint planning**
Discovery outputs — the OST, assumption test results, prototype findings — are shared with the full team before sprint planning. The trio brings the "what and why," the full team co-owns the "how and when."

### How discovery output gets back to the rest of the team

The pattern reported across multiple teams: **keep the whole squad in the loop continuously**, not in a big reveal. Share interview insights, OST updates, and test results as they happen. Teams report this builds trust and keeps delivery moving faster because engineers aren't surprised by what comes into sprint.

### The discovery/delivery phase flip

| Phase | Who carries the load |
|-------|----------------------|
| Discovery (interviewing, OST, assumption testing) | PM + designer primarily; engineer consulted |
| Delivery (building, iterating on live product) | Full engineering team + designer primarily; PM informed |

The trio doesn't disappear in delivery — but the weight shifts to the full team.

## Sources

- [The Impact of Working in a Product Trio | Product Talk (2025)](https://www.producttalk.org/2025/02/impact-of-product-trios/)
- [12 Hurdles to Effective Product Trio Collaboration | Product Talk (2024)](https://www.producttalk.org/2024/10/hurdles-effective-product-trio-collaboration/)
- [Core Concept: The Product Trio | Product Talk](https://www.producttalk.org/product-trio/)
- [Getting to a team-based approach to continuous discovery | Mind the Product](https://www.mindtheproduct.com/getting-to-a-team-based-approach-to-continuous-discovery-by-teresa-torres/)
- [Product trios for designers | Péter Balázs Polgár / Medium](https://medium.com/product-design-community/e26-product-trios-for-designers-b3c0f65b11e2)
- [Continuous Discovery Habits | Key Takeaways](https://zeda.io/blog/continuous-discovery-habits)
- [Mapping: An introductory guide for product teams by Teresa Torres | Miro](https://miro.com/blog/mapping-product-teams-teresa-torres/)
- [Continuous Discovery Habits with Teresa Torres | Dovetail](https://dovetail.com/outlier/continuous-discovery-teresa-torres/)
- [Product in Practice: Why Ramsey Solutions Rotates Engineers in Their Product Trios | Product Talk (2024)](https://www.producttalk.org/2024/08/rotate-engineers-product-trio/)
- [Ask Teresa: Does the Engineer in the Product Trio Need to be the Tech Lead? | Product Talk (2024)](https://www.producttalk.org/2024/10/engineer-lead-product-trio/)
- [Product in Practice: Assumption Testing with Engineers at Orion Labs | Product Talk](https://www.producttalk.org/2022/02/assumption-testing-engineers/)
- [Core Concept: Getting Engineers to Embrace the Product Trio | Product Talk](https://www.producttalk.org/2021/07/engineers-and-product-trios/)
- [The Product Triad: Design's Role | NN/G](https://www.nngroup.com/articles/the-product-triad-designs-role/)

