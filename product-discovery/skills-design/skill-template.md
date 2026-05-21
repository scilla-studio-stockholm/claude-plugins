---
title: "Skill template för product-discovery-assister"
date: 2026-05-06
purpose: Mall och konventioner för CC-skills som implementerar product-discovery-assisterna i skills-design/opportunity-solution-tree-agents.md. Härledd från OST-opportunity-extractor (assist 3a-extractor) som proof-of-concept för wrapper-mönster över befintliga skills.

---

# Skill template för product-discovery-assister

Mallen härledd från `OST-opportunity-extractor` som proof-of-concept (wrapper på `scilla-research:knowledge-finder`). Använd den som mall för resterande tolv assister.

## Cross-cutting beslut som gäller alla skills

**Filplats:** Skills bor i `.claude/skills/<skill-name>/SKILL.md` enligt CC-konvention. Kebab-case för skill-namn.

**Frontmatter:** Bara CC-fält (`name`, `description`). Inte Metrias title/date/purpose. SKILL.md är ett funktionellt CC-artefakt med egen schema.

**Invocation-yta:** CC-skills triggas via NL-match på description-fältet (default) plus optionell slash-command (`/<skill-name>`). Description-fältet är därmed load-bearing och följer "for X, when Y, output Z"-mönster på engelska, med tydlig skiljelinje mot andra skills i samma domän. Slash-commands läggs till opportunistiskt för det som körs ofta; namnet följer skillens kebab-case (skill `extract-opportunities` blir `/extract-opportunities`).

**Output-mapp:** Skills sparar artefakter i `workspace/<fas>/<artifact-typ>-<YYYY-MM-DD>.<ext>` där `<fas>` är phasade subdirs (`1-opportunity-val/`, `2-solution-brainstorm/`, osv.) och `<ext>` är `.json`, `.md`, eller båda för paired output. Paired output (JSON + markdown med samma rotnamn) är default för skills vars output både konsumeras downstream och läses av människor; markdown-renderingen genereras deterministiskt från JSON via renderingsmall i skill-prompten. Workspace är klient-repots arbetsmapp, så per-klient-isolering är implicit. Fullständig datakontrakts-spec i `opportunity-solution-tree-agents.md`.

**Språk:** Svenska i body och output. Behåll engelska begreppsnamn (product outcome, opportunity, citatformat, Test Card, assumption, journey).

**Knowledge-anchors:** Skills läser knowledge-filer från `knowledge/` vid körtid (runtime-access) snarare än som inbyggt i skill-prompten. Skills tillämpar den befintliga taxonomin snarare än att uppfinna egen. Knowledge/ ligger idag i klient-repots rot; principen är oberoende av framtida distribution (delat scilla-repo, plugin, eller global config).

**Wrapper-mönster:** När en skill bygger på en annan skill (t.ex. `OST-opportunity-extractor` bygger på `scilla-research:knowledge-finder`), dokumentera dependency tydligt under "Prerequisites" och exit om den saknas, snarare än att försöka degradera tyst.

## SKILL.md-struktur

```markdown
---
name: <kebab-case-skill-name>
description: <En till två meningar på engelska som följer mönstret "for <role>, when <trigger>, output <artifact-type>". CC-skills triggas via description-match (NL) plus optionell slash-command, så fältet är load-bearing. Skapa tydlig skiljelinje mot andra skills i samma domän, t.ex. "extract opportunities from raw transcripts" är distinkt från "validate opportunities against citatformat".>
---

# <Skill name>

You help a Metria product trio <ett-meningsbeskrivning av jobbet>.

This skill is assist <N> in `skills-design/opportunity-solution-tree-agents.md`.

## Prerequisites (om några)

- <Externa skills som krävs, t.ex. `scilla-research:transcript-cleaner`>
- <Filer eller artefakter som måste existera i förväg>

## Steps

1. **Read the knowledge anchors:** <list>
2. **Get input from user:** <vad, accept-format>
3. **<Kärnsteget med konkret instruktion>**
4. **<Fortsätt med numrerade steg>**
5. **Save output** as `workspace/<fas>/<artifact>-<YYYY-MM-DD>.<ext>` om användaren inte specificerar. För paired output, skriv båda `.json` och `.md` med samma rotnamn.

## Output principles

- <Direkta principer som styr ton, format, vad som inkluderas>
- <Skriv på svenska, behåll engelska begreppsnamn>

## Vad skill INTE gör

- <Lista de saker som hör till andra assister, så scope är tydligt>
```

## Mönster värt att kopiera

**Knowledge-läs först.** Steg 1 är alltid att läsa relevanta knowledge-filer. Det gör att skill alltid är ankrad mot källan, inte mot sin egen prompt-version av sanningen.

**Numrerade steg, fet-text rubriker.** Lättläst för LLM:en, lättare att felsöka när något går snett.

**Output-principles-sektion.** Direkta normer för ton och format. Hindrar LLM från att mjukna i prompts.

**"Vad skill INTE gör"-sektion.** Tydliggör scopegränser. Hindrar skill från att ta sig in i andra assisters territorium när trio ber om något brett.

**Filnamnskonvention med datum.** `workspace/<fas>/<typ>-<datum>.<ext>`. Datum gör det enkelt att köra över flera dagar utan att skriva över tidigare körningar. Paired output (JSON + markdown med samma rotnamn) är default för skills som producerar strukturerad data konsumerad downstream.

## Mönster att undvika

**Inbyggd taxonomi i prompten.** Lägg taxonomin i `knowledge/` och referera. När taxonomin utvecklas behöver vi inte hitta alla skills som har den hårdkodad.

**Tysta degradationer.** Om en dependency saknas, säg det och exit. Inte improvisera fram ett halvbra resultat.

**Egna tolkningar i citat.** För skills som hanterar kund-citat (OST-opportunity-extractor, opportunity-clusterer, comparator), bevara verbatim eller markera tweaks per `../knowledge/discovery/opportunity-citation-format.md`. Inga paraphraseringar.

## När mallen ska revideras

- När en skill kräver vision-tools (assist 2 är kandidat). Lägg till mönster för att läsa skärmdumpar.
- När paired output-renderingsmallen blir komplex nog att lyfta ut till en gemensam hjälp-skill snarare än ligga inline i SKILL.md.
- När en skill kräver multi-agent orchestration (assist 6). Lägg till sub-agent-mönster.

## Bygg-status

Per `opportunity-solution-tree-agents.md` är tretton assister speccade (steg 1, trios outcome-skrivande, är inte en AI-assist).

- ✅ `OST-opportunity-extractor` (assist 3a-extractor) byggd som wrapper på scilla-research:knowledge-finder
- ✅ `OST-validate-opportunities` (assist 3a-validator) byggd 2026-05-09: första generiska skill med engelsk body, flag-only-mönster (ingen rewrite-suggestion)
- ✅ `OST-extract-experience-map` (assist 2) byggd 2026-05-09: första vision-baserade skill, paired JSON + markdown med deterministisk rendering, tiered strictness
- ✅ `OST-cluster-opportunities` (assist 3b) byggd 2026-05-09: kombinerar tre inputs (experience-map JSON + validated table + extracted quotes) till v0.2 paired output med phase-clustering, parent-child inom fas (max 2 nivåer), och synthetic fas-0-unphased bucket. Bumpa schema till v0.2.
- ✅ `OST-compare-opportunities` (assist 4) byggd 2026-05-09: läser v0.2 clustered JSON + product outcome, filtrerar approved-only, scorar 5 Torres-kriterier × N opportunities med strong/medium/weak/unknown/n/a och trace-back via opp_refs, deriverar evidence_gaps från unknown-celler. Ny knowledge anchor opportunity-comparison.md (schema v0.1).
- ✅ `OST-select-opportunity` (assist 5) byggd 2026-05-10: läser v0.1 comparison-matrix + product outcome, applicerar tre-stegs beslutsregel (outcome-alignment-filter → strongest-aggregate-profile-rank → fewer-evidence-gaps-tiebreak), producerar paired JSON + markdown proposal med chosen_opportunity, alternatives_considered (alla andra approved opps), och AI-bedömd evidence_gaps_carried/excluded. Ny knowledge anchor opportunity-selection.md (schema v0.1). Trio ratificerar separat in i workspace/context/chosen-opportunity.md.
- ✅ `OST-brainstorm-solutions` (assist 6) byggd 2026-05-10: läser trio-ratificerad workspace/context/chosen-opportunity.md + product outcome + tre generiska roll-anchorer från knowledge/foundations/, spawnar tre roll-sub-agenter parallellt via Agent-tool för var och en av tre rundor (PM, UX, Tech Lead × 5 idéer = 45 solutions). Anti-duplicering är prompt-only ('new or build-on, no paraphrases'); assist 7 (clusterer) gör dedup-jobbet. Ny knowledge anchor solution-brainstorm.md (schema v0.1). Ratification format-sektion tillagd i opportunity-selection.md. Helt företagsagnostisk.
- ✅ `OST-cluster-solutions` (assist 7) byggd 2026-05-11: läser v0.1 solution-candidates JSON + workspace/context/chosen-opportunity.md + product outcome, kör en LLM-pass som grupperar 45 kandidater i 5-9 tematiska kluster (free-form by theme). Full member embed (id/title/generating_role/round_number/description). Post-sort clusters by member count descending, cluster_ids c1..cN tilldelas post-sort. Single-member clusters tillåtna; inget build_on field i v0.1. Chosen-opp cross-check (source-JSON vs context-md bold-id) som hard-exit. Ny knowledge anchor solution-cluster.md (schema v0.1). **Off-pipeline från 2026-05-11 (v2-redesign av assist 8):** skillet stannar byggt och tillgängligt som fristående tooling för trios som vill ha clustered review av brainstormen, men ingår inte i critical-path längre. Assist 8 v2 läser OST-brainstorm-solutions output direkt utan clustering-pass.
- ✅ `OST-select-top-three-solutions` (assist 8) byggd 2026-05-11 (v2-redesign samma dag efter v0.1-smoke-test): läser v0.1 solution-candidates JSON från OST-brainstorm-solutions + workspace/context/chosen-opportunity.md + product outcome, kör en LLM-pass som plockar exakt 3 specifika lösningar rankade by descending outcome-impact probability. Varje pick har 2-3 meningar outcome-mapping rationale (ingen customer-evidence anchor, ingen cluster-context, ingen assumption-reasoning). Inga clusters, ingen discriminator, ingen alternatives-sektion (trio läser brainstormer-markdown om de vill överrida). Trio-ratifiering via workspace/context/ratifications.md. Knowledge anchor top-three-selection.md bumpad till v0.2 (v0.1-design bevarad i Evolution-sektionen). v0.1-skill-implementeringen (commits 9693096..2553a1e) och v0.1-design-doc (commit 36a2826) bevarade i git-historiken som lärande-artefakt; v2 omskriven in place.
- ✅ `OST-generate-assumptions` (assist 9) byggd 2026-05-11: läser trio-ratificerad top-three-solutions JSON via ratification-flag-mönstret i workspace/context/ratifications.md (första konsumenten av mönstret), workspace/context/chosen-opportunity.md, workspace/context/product-outcome.md, och senaste experience-map-extracted-*.json. Spawnar 9 method-pass sub-agenter parallellt via Agent-tool (storymap, pre-mortem, outcome-impact × 3 lösningar × 6 idéer = 54 raw), kör sedan 3 per-solution LLM dedup-passes som mergar similar assumptions across methods med source_methods som array (triangulerings-signal). Per-solution-struktur, ingen cross-solution shared_with-markering. Ingen in-skill HITL-banner; trios gate är downstream på assist 11 (OST-riskiest-assumptions). Ny knowledge anchor assumption-generation.md (schema v0.1). Storymap-sub-agents får experience map som "future flow, not today"-anchoring.
- ✅ `OST-assumption-categorizer` (assist 10) byggd 2026-05-12: läser senaste `assumptions-*.json` från `workspace/7-assumptions/` (latest-by-date, ingen ratification-gate mellan 9 och 10 eftersom fas-3 trio-gate ligger downstream på assist 11). En LLM-pass klassificerar varje antagande i exakt en av Cagans fem product-risk-kategorier (desirability, usability, feasibility, viability, other) med risk-falls-regeln. Identity-mapping är load-bearing: varje upstream-fält carry-through byte-identical; bara ett nytt `category`-fält per antagande. 'Other' reserverat för icke-Cagan-antaganden (legal, ethical, regulatory, market-timing, organizational). Ny knowledge anchor assumption-categorization.md (schema v0.1). Etablerar identity-mapping som strukturellt mönster, single-pass classification mot låst taxonomi, och latest-by-date-input mellan intermediate-phase-assists.
- ✅ `OST-riskiest-assumptions` (assist 11) byggd 2026-05-12: läser senaste `assumptions-categorized-*.json` från `workspace/8-assumptions-categorized/` (latest-by-date). En LLM-pass scorer alla ~30-42 antaganden across 3 lösningar på Bland's 2x2 (importance: high/low; evidence: strong/weak; rationale: structured single sentence regex-checked). `is_riskiest` beräknas av skill från importance + evidence (LLM får inte returnera det). Identity-mapping över upstream assist-10 output: varje upstream-fält byte-identical; bara 4 nya per-antagande-fält (importance, evidence, is_riskiest, rationale). Soft-evidence-regel: domain norms och industry conventions räknas som evidens (trio overrider vid HITL). Markdown öppnar med Trio HITL gate banner; per-solution `Riskiest:` summary-rad + inline `[RISKIEST]`-tagg. Ingen ratifications.md-entry; assist 12 läser latest-by-date. Bumpar `assumption-risk-mapping.md` till v0.2 (extension, inte replacement). Etablerar schema-extension-precedent, multi-field-add identity-mapping, deterministic-derivation field, structured rationale format, och markdown-HITL-banner-without-ratifications.
- ✅ `OST-validation-experiment-designer` (assist 12) byggd 2026-05-12: läser senaste `riskiest-assumptions-*.json` från `workspace/9-riskiest-assumptions/` (latest-by-date), filtrerar till `is_riskiest=true` only. En LLM-pass designar en Bland Test Card per riskfyllt antagande (Hypothesis / Test / Metric / Success criteria + 2 alternative tests + cost/time/evidence-meta) med hybrid category-default + named override-regel. success_criteria regex-checked för numeric anchor (måste innehålla siffra). Filtered identity-mapping över upstream: varje upstream-fält byte-identical för retained antaganden; non-riskiest dropped; bara 2 nya per-antagande-fält (recommended_test, alternative_tests). alternative_tests fixed at 2. Markdown öppnar med Trio run-list handoff banner (terminal assist; ingen review-and-approve gate). Ingen ratifications.md-entry. Bumpar `assumption-validation.md` till v0.2 (extension). Etablerar filtered identity-mapping precedent, terminal-assist HITL framing, regex-anchored content rule, och category-default + named-override pattern.
- 🎉 Critical path complete: all 12 required assists built. Cluster-solutions (assist 7) stays off-pipeline per the 2026-05-11 decision.

Bygg-ordningen i brainstorm-input-doc:n står som riktlinje. Wrapper-mönstret etablerat genom OST-opportunity-extractor är det viktigaste mönsterstödet inför resten.
