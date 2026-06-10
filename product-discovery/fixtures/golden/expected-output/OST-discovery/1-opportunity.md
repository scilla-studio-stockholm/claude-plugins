---
title: Chosen opportunity - Licenstilldelning (Aurora)
date: 2026-05-29
purpose: Milestone doc for OST opportunity selection (phase 06). Self-contained proposal the trio reviews and ratifies. Machine JSON paired at _working/chosen-opportunity-proposal.json; ratified record at decisions.json (decided.opportunity).
tags: [opportunity-selection, ost, schema-v0.1, milestone]

---

# Chosen opportunity: Licenstilldelning (Aurora)

Schema version: 0.1
Paired JSON: `_working/chosen-opportunity-proposal.json`
Ratified record: `decisions.json` (`decided.opportunity`)

> **Trio HITL:** This is the AI's proposal. Review the rationale and override if you disagree. If approved, `decided.opportunity` in `decisions.json` is the ratified record — you may edit it directly to adjust scores or rationale before approving. Creating a `chosen-opportunity.md` is optional (human reference only — downstream skills read from `decisions.json`).

**Product outcome:** Öka andelen nya kunder som på egen hand når sitt första lyckade produktionsanrop mot API:et utan att kontakta Flowbase, från 40% till 80% inom 60 dagar från avtalstecknande.

## 1. Proposed opportunity

**opp-7-1** (Journey phase: Fas 7 - Aktivering & leverans)

> "jag har inte haft någon guide eller information, och ni har ju också sagt att ni inte jobbar med att hjälpa till att implementera - det får kunden göra själv"
> - *David, intervju-4-aurora-apr-13, ~rad 58*

### Why this opportunity

opp-7-1 och opp-5-1 delar den starkaste profilen i kandidatpoolen med 3 strong vardera på de fyra övriga kriterierna och 0 weak. Tiebreak i steg 3 avgörs av opp-7-1:s 0 unknown-celler över samtliga fem kriterier, jämfört med opp-5-1:s 1 unknown på competitive-landscape. Den valda opportunity - avsaknad av guide och implementeringsstöd i fas 7 (Aktivering & leverans) - är korsbekräftad av både intern (Lina, stödjande opp-7-3) och extern (David) källa och drabbar varje ny API-kund universellt.

Profile summary: 4 strong, 1 medium, 0 weak, 0 unknown.

## 2. Alternatives considered (11)

Every other approved opportunity from the comparison, with a one-line reason it was not chosen.

| Opportunity | Journey phase | Why not chosen |
|-------------|---------------|----------------|
| **opp-5-1** | Fas 5 - Licens-upplägg | Lika stark som opp-7-1 med 3 strong på de fyra övriga kriterierna och 0 weak, men faller på steg 3-tiebreak: 1 unknown på competitive-landscape mot opp-7-1:s 0. |
| **opp-5-5** | Fas 5 - Licens-upplägg | Svagare profil än opp-7-1 i steg 2 med 2 strong mot 3 på de fyra övriga kriterierna; market-size scorer medium. |
| **opp-5-8** | Fas 5 - Licens-upplägg | Svagare profil än opp-7-1 med 1 strong mot 3 på de fyra övriga kriterierna; customer-importance och market-size scorer medium. |
| **opp-5-10** | Fas 5 - Licens-upplägg | Svagare profil än opp-7-1 med 1 strong mot 3 på de fyra övriga kriterierna; customer-importance och market-size scorer medium. |
| **opp-7-6** | Fas 7 - Aktivering & leverans | 0 strong på de fyra övriga kriterierna; customer-importance, market-size och strategic-fit scorer alla medium. |
| **opp-1-1** | Fas 1 - Förfrågan inkommer | 0 strong och 1 weak (customer-importance) på de fyra övriga kriterierna; market-size är unknown. Svagaste kandidatprofilen i poolen. |
| **opp-0-8** | Utanför resan | Deprioriterades i steg 1: scorer weak på outcome-alignment. |
| **opp-0-14** | Utanför resan | Svagare profil än opp-7-1 med 1 strong mot 3 på de fyra övriga kriterierna; market-size och strategic-fit scorer medium. |
| **opp-0-22** | Utanför resan | Deprioriterades i steg 1: scorer weak på outcome-alignment. |
| **opp-0-3** | Utanför resan | Deprioriterades i steg 1: scorer weak på outcome-alignment. |
| **opp-0-1** | Utanför resan | 0 strong på de fyra övriga kriterierna; svagare profil än opp-7-1 på samtliga kriterier utom outcome-alignment. |

## 3. How it compared

The decision-relevant slice of the comparison matrix: the five Torres criteria for the chosen opportunity and the top three alternatives by step-2 profile strength.

| Criterion               | **opp-7-1** (chosen) | opp-5-1 | opp-5-5 | opp-5-8 |
|-------------------------|----------------------|---------|---------|---------|
| Outcome alignment       | strong               | strong  | medium  | strong  |
| Customer importance     | strong               | strong  | strong  | medium  |
| Market size / frequency | strong               | strong  | medium  | medium  |
| Strategic fit           | strong               | strong  | strong  | strong  |
| Competitive landscape   | medium               | unknown | unknown | unknown |

Scores are the qualitative cells from the comparison matrix (`strong` / `medium` / `weak` / `unknown` / `n/a`), not aggregated.
