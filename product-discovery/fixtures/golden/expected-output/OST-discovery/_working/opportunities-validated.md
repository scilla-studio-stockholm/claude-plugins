---
title: Opportunity-validering — Team Aurora Våg 1
date: 2026-05-26
team: Aurora
purpose: Per-opportunity verdict on citation format and opportunity vs solution classification
source: discovery/opportunity-selection/2026-05-25/opportunities-extracted.md
tags: [aurora, discovery, validation]
---

# Opportunity-validering — 2026-05-26

Källfil: `discovery/opportunity-selection/2026-05-25/opportunities-extracted.md`

## Intervju 1 — Anders Berg

| # | Opportunity (utdrag) | Verdict | Motivation |
|---|---|---|---|
| 1 | "Vi gjorde allt på eget. Ingen hjälp." | ✅ Godkänd | — |
| 2 | "Vi har väldigt mycket bra grejer på bra ställen, men vi har inte riktigt helheten. [...]" | ✅ Godkänd | — |
| 3 | "Jag får ett 200-svar och kanske en fil, så det gick bra. Men jag har ingen aning om det är korrekt..." | ✅ Godkänd | — |
| 4 | "Det är 'lowest of low'. Man tar sin egen datapost och säger att det stämmer ungefär." | ✅ Godkänd | — |
| 5 | "Vi utgick väldigt hårt från att bygga upp den själva [...] Sen förstod vi att det här kommer vi aldrig att få ordning på..." | ✅ Godkänd | — |
| 6 | "Att garantera kvaliteten på det man levererar är inte jättelätt. [...]" | ✅ Godkänd | — |
| 7 | "Jag tror att i team Fenix saknar de mycket av den här domänkunskapen..." | ✅ Godkänd | — |

## Intervju 2 — Niklas Klisics

| # | Opportunity (utdrag) | Verdict | Motivation |
|---|---|---|---|
| 8 | "det blir alltid [...] någon timme eller två och bara diskutera hur [man] för över den här [secret-]cykeln" | 🔧 Behöver tweak | Originalet säger "hur för vi över" — "vi" ändrades till "[man]" utan att det är deiktiskt. Bevara "vi", tweaka bara "cykeln" → "[secret-]cykeln". |
| 9 | "sen när vi väl ska byta så måste vi göra det i samförstånd med kunden..." | ✅ Godkänd | — |
| 10 | "vi har ingen koppling idag mellan en [SSO-]integration och en licens utan vi [...] hårdkodade behörigheterna..." | ✅ Godkänd | ASR-korrektioner motiverade. |
| 11 | "sådan information som hur länge [...] deras klient[secret] är giltig[t]..." | ✅ Godkänd | — |
| 12 | "vi har ingen möjlighet att köra två samtidigt aktiva [secrets]..." | ✅ Godkänd | — |
| 13 | "jag har obstruerat lite grann mot att storskaligt gå ut och sälja [SSO-]integrationer..." | ✅ Godkänd | Intern bedömning, men signalerar systemisk brist. |
| 14 | "[Självservice-]endpointsen är inte skapade [...]" | 🔧 Behöver tweak | Beskriver en saknad feature, inte kundfriktion. Trion bör omformulera till underliggande behov: kunder kan inte hantera sina nycklar/secrets själva. |
| 15 | "det bästa hade varit ifall [...] dom hade kunnat peka ut [...] attributet [...] och så kopplar det till en licens" | ⚠️ Solution in disguise | Beskriver specifik feature (attributmappning i självservice-GUI). Underliggande behov: SSO-kunder kan inte differentiera behörigheter per användargrupp. |

## Intervju 3 — Lina Falk

| # | Opportunity (utdrag) | Verdict | Motivation |
|---|---|---|---|
| 16 | "det blev ofta fel när vi lade upp nya kunder — de fick inte alla behörigheter de behövde..." | ✅ Godkänd | — |
| 17 | "vi använder fortfarande gemensamma användare — vilket innebär att vi inte kan använda vissa funktioner..." | ✅ Godkänd | — |
| 18 | "Det hade dock varit bättre om allt samlades på ett ställe och det var tydligare hur man hittar det." | 🔧 Behöver tweak | "allt" och "det" är deiktiska — refererar till API-dokumentation i kontexten. Tweaka: "om [API-dokumentationen] samlades på ett ställe och det var tydligare hur man hittar [den]." |
| 19 | "En sak som har varit lite knölig är att det finns tre olika sätt att logga in i Swagger..." | ✅ Godkänd | — |
| 20 | "det har egentligen inte med API:et [...] att göra, utan med kunskapen om själva informationen man får..." | ✅ Godkänd | — |
| 21 | "Det verkar inte vara allmänt känt vare sig hos Team Fenix eller hos oss i Team Comet..." | ✅ Godkänd | — |
| 22 | "Vi var tvungna att ta beslut och gissa utifrån det vi kunde analysera fram..." | ✅ Godkänd | — |
| 23 | "Vi håller tummarna, kan man säga..." | ✅ Godkänd | — |
| 24 | "Vi har missuppfattat saker eller missat att en viss typ av objekt finns..." | ✅ Godkänd | — |
| 25 | "Det som bekymrar mig är när till och med Team Fenix säger att de inte har en expert..." | ✅ Godkänd | — |
| 26 | "vi har ingen direkt övervakning på att integrationen fungerar. Det är en brist..." | ✅ Godkänd | — |
| 27 | "vi kan skylla på Datakällan hur mycket som helst, men det hjälper inte kunden." | ✅ Godkänd | — |
| 28 | "för samrådskrets-paketet är det så otroligt mycket i svaret att det inte är möjligt att läsa igenom..." | ✅ Godkänd | — |
| 29 | "vi insåg att en specialfall kan vara registrerad som innehavare [...] det fick oss att se sämre ut..." | ✅ Godkänd | Stark opportunity med konkret kundpåverkan — extraktorn klassade som [Möjlig] men trion bör överväga [Klar]. |

## Intervju 4 — David Sörensen

| # | Opportunity (utdrag) | Verdict | Motivation |
|---|---|---|---|
| 30 | "egentligen jobbar jag som dataanalytiker [...] trött på att manuellt mata in data." | ✅ Godkänd | Friktionssignal finns: "trött på att manuellt mata in data." |
| 31 | "Tidigare har vi manuellt skrivit av mycket: skrivit in adress, volym, innehavare..." | ✅ Godkänd | — |
| 32 | "det är väl att man egentligen inte vet vad man gör - så det är lite säkerhetsfrågor..." | ✅ Godkänd | — |
| 33 | "jag har inte haft någon guide eller information, och ni har ju också sagt att ni inte jobbar med att hjälpa..." | ✅ Godkänd | — |
| 34 | "Det hade varit lättare att komma igång om det fanns någon typ av liten säljande startsida..." | 🔧 Behöver tweak | Gränsar mot solution in disguise — "säljande startsida" är en lösningsidé. Underliggande friktion: det var svårt att förstå vad API:et erbjuder och hur man kommer igång. Trion bör separera behovet från lösningsförslaget. |
| 35 | "API:et [är] skrivet för folk som vet vad API är [...] vi som inte visste fick det att ta längre tid..." | ✅ Godkänd | — |
| 36 | "Transaktionskostnaden upplevs som dyr - har alltid gjort det." | ✅ Godkänd | — |
| 37 | "Min enda önskan är kostnadsbudget [...] det är en systemrisk..." | ✅ Godkänd | Kunden formulerar naturligt som lösning ("tak") men friktionen ("systemrisk") är tydlig. |
| 38 | "Det hade bara varit skönt att ha ett kostnadstak helt enkelt för att sova gott." | ✅ Godkänd | — |
| 39 | "[Hur tar ni del av nyheter i API:erna?] Inte alls, liksom..." | 🔧 Behöver tweak | Intervjuarens fråga "[Hur tar ni del av nyheter...]" ska inte ingå i citatet. Ta bort den eller flytta utanför citattecknen som kontextrad. |
| 40 | "Jag frågade Robin Sandell - egentligen bara kundtjänst - om det var möjligt att hämta datan via API..." | ✅ Godkänd | — |
| 41 | "Jag tyckte det var lite jobbigt att be om förlängning [av testmiljön]..." | ✅ Godkänd | — |
| 42 | "Till exempel innehavare - det finns ju registrerad innehavare och bekräftad innehavare..." | ✅ Godkänd | — |
| 43 | "Jag har skrivit allt med AI. ChatGPT är min bästa vän..." | 🔧 Behöver tweak | Beskriver arbetssätt/persona men uttrycker inte friktion i sig. Fungerar som kontextnotering till andra opportunities, inte som fristående opportunity. |
| 44 | "Det enda jag saknar är nog bara en säljsida för API:et [...] Om ni tittar till exempel på Stripe..." | ⚠️ Solution in disguise | Specifik lösning ("säljsida") med detaljerat innehåll och benchmarkreferens (Stripe). Underliggande behov: det var inte uppenbart att man kunde hämta data via API, eller hur man kom igång. |

## Sammanfattning

| Verdict | Antal |
|---|---|
| ✅ Godkänd | 34 |
| 🔧 Behöver tweak | 8 |
| ⚠️ Solution in disguise | 2 |
| **Totalt** | **44** |

### Tweaks att åtgärda

| # | Vad behöver fixas |
|---|---|
| 8 | Återställ "vi" istället för "[man]" — originalet säger "hur för vi över". |
| 14 | Omformulera från saknad feature till underliggande kundbehov (inte kunna hantera nycklar/secrets själva). |
| 18 | Tweaka deiktiska "allt" och "det" till "[API-dokumentationen]" / "[den]". |
| 34 | Separera behovet (svårt att komma igång) från lösningsförslaget ("säljande startsida"). |
| 39 | Ta bort intervjuarens fråga ur citatet. |
| 43 | Bedöm om citatet ska vara kontextnotering eller strykas som fristående opportunity. |

### Solutions in disguise att omformulera

| # | Nuvarande formulering | Underliggande behov |
|---|---|---|
| 15 | Attributmappning till licens i självservice-GUI | SSO-kunder kan inte differentiera behörigheter per användargrupp utan manuellt ingrepp. |
| 44 | "Säljsida" för API med Stripe som förebild | Det var inte uppenbart att data kunde hämtas via API, eller hur man kom igång. |
