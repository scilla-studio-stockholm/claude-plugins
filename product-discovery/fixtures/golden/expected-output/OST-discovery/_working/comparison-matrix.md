---
title: Comparison matrix - Licenstilldelning (Aurora)
date: 2026-05-26
purpose: Opportunity comparison matrix for OST opportunity selection, paired with comparison-matrix.json
tags: [opportunity-comparison, ost, schema-v0.1]

---

# Comparison matrix: Licenstilldelning (Aurora)

Source clustered map: `experience-map-clustered.json`
Source product outcome: `_product-context/product-outcome.md`
Schema version: 0.1
Paired JSON: `comparison-matrix.json`

## Product outcome

> Öka andelen nya kunder som på egen hand når sitt första lyckade produktionsanrop mot API:et utan att kontakta Flowbase, från 40% till 80% inom 60 dagar från avtalstecknande.

## Konsolidering

44 citat-stickies extraherades. 8 exkluderades (verdict). Av de 34 godkända konsoliderades tematiskt lika citat under 12 representativa opportunities. Stödjande citat refereras i cell-motiveringarna.

| Representant | Stödjande citat |
|---|---|
| opp-5-1 (behörighetsfel) | opp-5-2 |
| opp-5-5 (secret-rotation) | opp-5-6, opp-5-7 |
| opp-7-1 (ingen onboarding) | opp-7-3 |
| opp-0-8 (domänkunskap) | opp-0-7, opp-0-9, opp-0-10, opp-0-11, opp-0-12, opp-0-13, opp-0-16, opp-0-26 |
| opp-0-14 (övervakning) | opp-0-15, opp-0-17 |
| opp-0-22 (kostnadsoro) | opp-0-21, opp-0-23 |
| opp-0-1 (integrationsstöd) | opp-0-2, opp-0-5, opp-0-18, opp-0-19, opp-0-20, opp-0-25 |

## Opportunities compared (12)

**Fas 5 — Licens-upplägg (high friction):**
- **opp-5-1** — "det blev ofta fel när vi lade upp nya kunder — de fick inte alla behörigheter de behövde, vilket ledde till en hel del fram-och-tillbaka innan en kund var igång." - *Lina, intervju 3*
- **opp-5-5** — "sen när vi väl ska byta så måste vi göra det i samförstånd med kunden [...] det tar alltid några timmar" - *Niklas, intervju 2*
- **opp-5-8** — "jag har obstruerat lite grann mot att storskaligt gå ut och sälja [SSO-]integrationer just för att jag tycker inte att vi riktigt är redo" - *Niklas, intervju 2*
- **opp-5-10** — "vi använder fortfarande gemensamma användare — vilket innebär att vi inte kan använda vissa funktioner i Datahubben" - *Lina, intervju 3*

**Fas 7 — Aktivering & leverans:**
- **opp-7-1** — "jag har inte haft någon guide eller information, och ni har ju också sagt att ni inte jobbar med att hjälpa till att implementera" - *David, intervju 4*
- **opp-7-6** — "det finns tre olika sätt att logga in i Swagger, och man måste veta vilket man ska använda" - *Lina, intervju 3*

**Fas 1 — Förfrågan inkommer:**
- **opp-1-1** — "Jag frågade Robin Sandell - egentligen bara kundtjänst - om det var möjligt att hämta datan via API" - *David, intervju 4*

**Utanför resan:**
- **opp-0-8** — "kunskapen om själva informationen man får. Där finns fortfarande ett glapp. Vi har ingen riktig domänexpert" - *Lina, intervju 3*
- **opp-0-14** — "vi har ingen direkt övervakning [...] kunder ibland är de som upptäcker att något inte fungerar" - *Lina, intervju 3*
- **opp-0-22** — "Min enda önskan är kostnadsbudget [...] det är en systemrisk" - *David, intervju 4*
- **opp-0-3** — "Jag har ingen aning om det är korrekt eller om det används rätt" - *Anders, intervju 1*
- **opp-0-1** — "Vi gjorde allt på eget. Ingen hjälp." - *Anders, intervju 1*

## Excluded from comparison (8)

- **opp-5-3** (fas-5; solution_in_disguise) — Specifik feature (attributmappning i GUI).
- **opp-5-4** (fas-5; needs_tweak) — Citattweak behöver korrigeras.
- **opp-5-9** (fas-5; needs_tweak) — Beskriver saknad feature.
- **opp-7-2** (fas-7; needs_tweak) — Gränsar mot solution in disguise.
- **opp-7-4** (fas-7; solution_in_disguise) — Specifik lösning med benchmarkreferens.
- **opp-7-5** (fas-7; needs_tweak) — Deiktiska referenser utan tweak.
- **opp-0-24** (fas-0; needs_tweak) — Intervjuarfråga i citatet.
- **opp-0-27** (fas-0; needs_tweak) — Persona-kontext, inte fristående opportunity.

## Matrix

| Criterion | opp-5-1 | opp-5-5 | opp-5-8 | opp-5-10 | opp-7-1 | opp-7-6 | opp-1-1 | opp-0-8 | opp-0-14 | opp-0-22 | opp-0-3 | opp-0-1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Outcome alignment | strong | medium | strong | medium | strong | medium | medium | weak | medium | weak | weak | medium |
| Customer importance | strong | strong | medium | medium | strong | medium | weak | strong | strong | strong | medium | medium |
| Market size / frequency | strong | medium | medium | medium | strong | medium | unknown | strong | medium | unknown | medium | medium |
| Strategic fit | strong | strong | strong | strong | strong | medium | medium | medium | medium | medium | medium | medium |
| Competitive landscape | unknown | unknown | unknown | unknown | medium | unknown | medium | unknown | unknown | medium | unknown | unknown |

## Cell rationales

### Outcome alignment

- **opp-5-1** — strong. Behörighetsfel orsakar direkt fram-och-tillbaka med kunden innan licensen fungerar. Att eliminera dessa fel tar bort interaktioner rakt av. Cites: opp-5-1.
- **opp-5-5** — medium. Secret-rotation sker efter initial uppsättning och genererar interaktioner vid varje byte. Påverkar inte onboarding-vägen direkt men adderar löpande interaktioner. Cites: opp-5-5.
- **opp-5-8** — strong. Om Flowbase aktivt undviker att sälja SSO-licenser blockeras outcome direkt — kunder som vill ha SSO kommer aldrig till ett lyckat API-anrop. Cites: opp-5-8.
- **opp-5-10** — medium. Gemensamma användare hindrar features (t.ex. caching) som indirekt påverkar kundens integrationskvalitet, men kopplingen till antalet interaktioner är indirekt. Cites: opp-5-10.
- **opp-7-1** — strong. Avsaknaden av guide och implementeringsstöd tvingar kunden att kontakta Flowbase för hjälp — direkt orsak till interaktioner. Cites: opp-7-1.
- **opp-7-6** — medium. Tre loginmetoder i Swagger skapar förvirring som kan generera supportfrågor, men det är en avgränsad friktionspunkt. Cites: opp-7-6.
- **opp-1-1** — medium. Att kunden måste fråga kundtjänst för att upptäcka API-möjligheten är en interaktion, men tidigt i processen och engångshändelse. Cites: opp-1-1.
- **opp-0-8** — weak. Domänkunskapsgapet orsakar buggar som drabbar kunder men påverkar onboarding-interaktioner indirekt — yttrar sig primärt efter aktivering. Cites: opp-0-8.
- **opp-0-14** — medium. Kunder som upptäcker fel före Flowbase genererar reaktiva interaktioner. Bättre övervakning skulle förebygga dessa. Cites: opp-0-14.
- **opp-0-22** — weak. Kostnadsoro rör löpande API-användning, inte vägen från avtal till första lyckade anrop. Cites: opp-0-22.
- **opp-0-3** — weak. Verifieringsproblemet uppstår vid integratörens arbete och påverkar inte direkt antalet interaktioner med Flowbase. Cites: opp-0-3.
- **opp-0-1** — medium. "Ingen hjälp" under integration kan driva supportinteraktioner när integratörer kör fast. Cites: opp-0-1.

### Customer importance

- **opp-5-1** — strong. Lina beskriver "en hel del fram-och-tillbaka" som drabbar kunder. Niklas bekräftar med hårdkodade behörigheter. Korskälla. Cites: opp-5-1.
- **opp-5-5** — strong. Niklas: "alltid tar ett par timmar" att diskutera, synkronisering krävs, inga parallella secrets möjliga. Tre stödjande citat. Cites: opp-5-5.
- **opp-5-8** — medium. Niklas uttrycker intern oro men inte direkt kundsmärta. Bristen påverkar kunder indirekt genom att tjänsten inte erbjuds. Cites: opp-5-8.
- **opp-5-10** — medium. Lina beskriver en teknisk begränsning. Kundpåverkan verklig men uttrycks som intern frustration. Cites: opp-5-10.
- **opp-7-1** — strong. David (extern kund): "det tog längre tid att leta sig fram." Lina bekräftar med splittrad dokumentation. Korskälla intern + extern. Cites: opp-7-1.
- **opp-7-6** — medium. Lina: "lite knölig." Märkbar men inte blockerande. Cites: opp-7-6.
- **opp-1-1** — weak. David nämner det utan stark emotionell laddning. Kundtjänst löste frågan snabbt. Cites: opp-1-1.
- **opp-0-8** — strong. Starkaste klustret: Lina ("håller tummarna", "buggar som drabbat kunder"), Anders ("team Fenix saknar domänkunskap"), David ("registrerad vs bekräftad"). 7+ citat, 3 intervjuer. Cites: opp-0-8.
- **opp-0-14** — strong. Kunder upptäcker fel före Flowbase. Specialfall-incidenten bekräftar med konkret förtroendeförlust. Cites: opp-0-14.
- **opp-0-22** — strong. David återkommer tre gånger ("sova gott", "systemrisk", "det var synd"). Hög emotionell intensitet. Cites: opp-0-22.
- **opp-0-3** — medium. Anders uttrycker frustration men som intern utvecklare. Oklart om externa kunder upplever samma. Cites: opp-0-3.
- **opp-0-1** — medium. Anders konstaterar sakligt. David byggde ensam men upplevde det som "fine". Blandad signal. Cites: opp-0-1.

### Market size / frequency

- **opp-5-1** — strong. Drabbar varje ny API-licenskund. Lina: "ofta." Cites: opp-5-1.
- **opp-5-5** — medium. SSO-kunder med tidsbegränsade secrets — delmängd men troligen enterprise-segmentet. Cites: opp-5-5.
- **opp-5-8** — medium. SSO-kunder är en delmängd men representerar troligen större organisationer. Cites: opp-5-8.
- **opp-5-10** — medium. Alla kunder med gemensamma användare, vilket idag är de flesta. Cites: opp-5-10.
- **opp-7-1** — strong. Varje ny API-kund går genom aktivering. Universell. Cites: opp-7-1.
- **opp-7-6** — medium. Swagger-användare. Inte alla kunder — David använde Excel/VBA direkt. Cites: opp-7-6.
- **opp-1-1** — unknown. Bara en kund. Okänt hur många potentiella API-kunder inte upptäcker möjligheten.
- **opp-0-8** — strong. Domänkomplexitet i plattformsdata är strukturell och drabbar alla integratörer. Cites: opp-0-8.
- **opp-0-14** — medium. Drabbar kunder vid incidenter. Systemiskt men inte varje dag. Cites: opp-0-14.
- **opp-0-22** — unknown. Bara en kund. Okänt hur utbrett bland API-kunder.
- **opp-0-3** — medium. Varje integratör möter verifieringsfrågan men inte alla upplever den lika starkt. Cites: opp-0-3.
- **opp-0-1** — medium. Alla integrerar, men stödbehovet varierar med teknisk mognad. Cites: opp-0-1.

### Strategic fit

- **opp-5-1** — strong. Behörighetshantering är kärnan i licensprocessen. Cites: opp-5-1.
- **opp-5-5** — strong. Secret-hantering är central licensinfrastruktur. Cites: opp-5-5.
- **opp-5-8** — strong. SSO-skalbarhet avgörande för att växa API-licensaffären. Cites: opp-5-8.
- **opp-5-10** — strong. Kundspecifika användare är den uttalade riktningen. Cites: opp-5-10.
- **opp-7-1** — strong. Onboarding stödjer direkt skalningsambitionerna. Cites: opp-7-1.
- **opp-7-6** — medium. Swagger-förbättringar stödjer skalning men är smalare. Cites: opp-7-6.
- **opp-1-1** — medium. API-synlighet i gränslandet av trions domän. Cites: opp-1-1.
- **opp-0-8** — medium. Domänkunskap fundamental men kräver bredare organisationsförändring. Cites: opp-0-8.
- **opp-0-14** — medium. Övervakning stödjer kvaliteten men är mer drift. Cites: opp-0-14.
- **opp-0-22** — medium. Kostnadsskydd kan minska adoptionshinder men utanför kärn-licensprocessen. Cites: opp-0-22.
- **opp-0-3** — medium. Kvalitetsverifiering stödjer kärnlöftet men är bredare. Cites: opp-0-3.
- **opp-0-1** — medium. Integrationsstöd kopplat till skalning men inte trion specifikt. Cites: opp-0-1.

### Competitive landscape

- **opp-5-1** — unknown. Ingen data om konkurrenters behörighetsuppsättning.
- **opp-5-5** — unknown. Ingen data om konkurrenters secret-rotation.
- **opp-5-8** — unknown. Ingen data om konkurrenters SSO-skalning.
- **opp-5-10** — unknown. Ingen data om konkurrenters autentiseringsmönster.
- **opp-7-1** — medium. David jämförde Stripe och Datakällan som benchmarks med bättre getting-started-material. Cites: opp-7-1.
- **opp-7-6** — unknown. Ingen data om konkurrenters API-verktyg.
- **opp-1-1** — medium. David kollade andra leverantörer, hittade likvärdigt utbud. Bättre synlighet kan differentiera. Cites: opp-1-1.
- **opp-0-8** — unknown. Ingen data om konkurrenters domändokumentation.
- **opp-0-14** — unknown. Ingen data om konkurrenters övervakningspraxis.
- **opp-0-22** — medium. David: "samma pris som alla leverantörer." Kostnadsskydd kan differentiera. Cites: opp-0-22.
- **opp-0-3** — unknown. Ingen data om konkurrenters kvalitetsverifiering.
- **opp-0-1** — unknown. Ingen data om konkurrenters integrationsstöd.

## Evidence gaps (11)

- **Market size / frequency x opp-1-1**: Hur många potentiella API-kunder upptäcker inte att API finns som alternativ till webbsökningen?
- **Market size / frequency x opp-0-22**: Hur vanlig är kostnadsoron bland API-kunder? Bara en kund uttryckte den.
- **Competitive landscape x opp-5-1**: Hur hanterar konkurrerande Datahubben-leverantörer behörighetsuppsättning?
- **Competitive landscape x opp-5-5**: Hur hanterar konkurrenter secret-rotation — erbjuds det som självservice?
- **Competitive landscape x opp-5-8**: Hur skalar konkurrenter SSO-integrationer?
- **Competitive landscape x opp-5-10**: Vilka autentiseringsmönster använder konkurrenter?
- **Competitive landscape x opp-7-6**: Hur ser konkurrenters API-dokumentationsverktyg ut?
- **Competitive landscape x opp-0-8**: Hur dokumenterar konkurrenter domänkunskap om plattformsdata?
- **Competitive landscape x opp-0-14**: Har konkurrenter proaktiv övervakning?
- **Competitive landscape x opp-0-3**: Erbjuder konkurrenter verktyg för att verifiera API-svar?
- **Competitive landscape x opp-0-1**: Vilken typ av integrationsstöd erbjuder konkurrenter?

## Notes

- **Competitive landscape** scored unknown for 9 av 12 opportunities. Trion har begränsad data om konkurrenter. De tre som fick medium (opp-7-1, opp-1-1, opp-0-22) baseras på David enda jämförelser. Trion bör överväga om detta kriterium är lastbärande nog att samla in mer data, eller om det kan viktas ned i HITL.
