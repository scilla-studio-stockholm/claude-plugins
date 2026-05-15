---
title: Assumption types for solution validation
date: 2026-05-06
purpose: Reference taxonomy for categorizing assumptions that must hold for a product solution to deliver its intended impact. Used by the assumption categorizer assist in workshop 3 fas 3, and as learning material for trios developing assumption-identification skill.
tags: [assumptions, ost, validation, cagan, risk]

---

# Assumption types for solution validation

## What this document is

A reference taxonomy with five categories of assumptions that need to hold for a product solution to deliver its intended impact. Each category corresponds to a class of risk that, if the underlying assumption turns out to be false, will sink the solution.

The taxonomy is used in two places:

- **By the AI assumption categorizer** (`claude-plugins/product-discovery/skills-design/opportunity-solution-tree-agents.md`, fas 3) when classifying generated assumptions into a structured output for the trio.
- **By trios** as a learning aid when practicing assumption identification on their own solutions.

## Where this sits in the OST flow

After a trio has chosen an opportunity and identified candidate solutions, the next step is to surface the assumptions that must hold for each solution to work. Torres calls this "decompose into assumptions" and treats it as the prerequisite to assumption testing, where the trio designs lightweight experiments against the riskiest assumptions.

The taxonomy below is for the **decomposition step**. It does not say which assumption is riskiest. That is a separate evaluation.

## The five categories

The categories are anchored in Marty Cagan's "five product risks" from *Transformed* (see `knowledge/foundations/product-operating-model-marty-cagan.md`, principle 10), with terminology adjusted to match how Metria's trios discuss assumptions in workshops.

### 1. Desirability assumptions

**Definition:** Assumptions about whether customers and users actually want the solution and will derive value from it.

**Surfacing question:** "Why would users care about this? What must be true for them to want it?"

**Example assumptions (from workshop practice):**

- Våra kunder och användare vill ha det här
- Användare upplever värde när de använder det
- Användare är beredda att göra det vi ber dem göra för att kunna använda det

**Cagan equivalent:** Value risk.

### 2. Usability assumptions

**Definition:** Assumptions about whether users can figure out how to use the solution to achieve their goal.

**Surfacing question:** "Will users understand what to do? Will they find what they need?"

**Example assumptions:**

- Användarna förstår hur de ska använda det
- De hittar vad de behöver för att kunna utföra uppgiften

**Cagan equivalent:** Usability risk.

### 3. Feasibility assumptions

**Definition:** Assumptions about whether the team can build the solution with the available technology, skills, time, and constraints.

**Surfacing question:** "Can we actually build this? With what we have?"

**Example assumptions:**

- Det är tekniskt möjligt
- Det är säkert
- Det är skalbart
- Vi har rätt kompetens för det här i teamet

**Cagan equivalent:** Feasibility risk.

### 4. Viability assumptions

**Definition:** Assumptions about whether the solution makes business sense for Metria over time.

**Surfacing question:** "Is this defensible as a business decision? Does it generate more value than it costs? Is it required to enable something else strategic?"

**Example assumptions:**

- Det är affärsmässigt försvarbart att bygga lösningen
- Lösningen skalar till fler kunder
- Den genererar mer än vad den kostar att bygga
- Alternativt: den måste byggas för att möjliggöra något annat strategiskt

**Cagan equivalent:** Business viability risk.

### 5. Other assumptions

**Definition:** A catch-all for assumptions that do not fit the four primary categories. In practice this most often covers ethical defensibility and resource or timing constraints that are not strictly feasibility.

**Surfacing question:** "What else has to be true that we have not named yet?"

**Example assumptions:**

- Det är etiskt försvarbart
- Vi har tid att bygga det
- Det går i linje med pågående lagar och regelverk

**Cagan equivalent:** Ethics risk, plus pragmatic catch-alls Cagan does not formalize.

## Application notes

- **One assumption can touch multiple categories.** When that happens, place it in the category that best describes the risk if the assumption fails. If a feasibility-flavored assumption would actually sink the business case if false, file it under viability.
- **The categories are scaffolding, not the goal.** The goal is to see assumptions clearly enough to decide which to test. Trios learn to surface assumptions without leaning on the categories over time. Per the workshop note: "Ju mer tränade ni blir i att se egna antaganden desto mindre kommer ni behöva luta er mot strukturerade metoder."
- **The categorization is per solution.** Assumptions for solution A are kept separate from assumptions for solution B even if they look similar. Two solutions can have superficially similar assumptions that fail differently.

## Open evolutions

- The "other" category is a known weak point. If the same kind of assumption keeps landing there (e.g. regulatory or compliance-flavored), promote it to its own category in v0.2.
- Workshop practice may produce category-specific surfacing methods beyond the three current methods (storymap, pre-mortem, outcome-impact). When that happens, link them per category.
