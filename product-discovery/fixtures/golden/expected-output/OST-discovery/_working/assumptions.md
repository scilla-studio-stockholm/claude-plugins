---
title: "Assumptions: opp-7-1 - jag har inte haft någon guide eller information"
date: 2026-05-29
purpose: Per-solution deduped assumption lists with source-method attribution. Paired with assumptions.json. Input to assist 10 (OST-assumption-categorizer); trio gate downstream at assist 11 (OST-riskiest-assumptions).
tags: [assumption-generation, ost, schema-v0.1]

---

# Assumptions: opp-7-1

Source decisions: `OST-discovery/decisions.json`
Source top 3 solutions: `OST-discovery/_working/top-three-solutions.json`
Source experience map: `experience-map-extracted.json`
Schema version: 0.1
Paired JSON: `_working/assumptions.json`

Generation summary: 3 methods (storymap, pre-mortem, outcome-impact) x 3 solutions x 6 assumptions = 54 raw, then per-solution dedup with source-method attribution.

## Chosen opportunity

**opp-7-1** (Phase: fas-7) - "jag har inte haft någon guide eller information, och ni har ju också sagt att ni inte jobbar med att hjälpa till att implementera - det får kunden göra själv" - *David, intervju-4-aurora-apr-13, ~rad 58*

## Product outcome

> Öka andelen nya kunder som på egen hand når sitt första lyckade produktionsanrop mot API:et utan att kontakta Flowbase, från 40% till 80% inom 60 dagar från avtalstecknande.

## Solution 1: Automatiserad onboarding-portal med självbetjäning från dag ett

**sol-r1-pm-1** [PM, R1]

När kunden signerar avtalet aktiveras automatiskt en personaliserad onboarding-portal med steg-för-steg-guide, API-nycklar och testmiljö - allt utan att Flowbase behöver agera. Kunden kan göra sitt första lyckade API-anrop helt på egen hand, vilket direkt mäter sig mot målet om 80% självbetjänade kunder.

### Assumptions (10)

- **asm-sol-r1-pm-1-001** [PrM+SM] Avtalssigneringen sker i ett system som kan generera en maskinläsbar händelse som tillförlitligt triggar automatisk aktivering av onboarding-portalen utan manuell handpåläggning.
- **asm-sol-r1-pm-1-002** [OI+SM] Aktiveringen provisionerar korrekt kundspecifika API-nycklar, behörigheter och testmiljöåtkomst direkt vid trigger - utan manuella steg i Flowbases interna system.
- **asm-sol-r1-pm-1-003** [SM] Kunden tar emot portalinbjudan, uppfattar den som nästa steg i onboardingen och loggar in utan att behöva kontakta Flowbase för hjälp.
- **asm-sol-r1-pm-1-004** [OI+PrM+SM] Steg-för-steg-guiden är tillräckligt tydlig och heltäckande för att kunden ska kunna följa den helt på egen hand, och täcker de vanligaste tekniska miljöerna, integrationsmönstren och hindren som Flowbases kunder faktiskt stöter på.
- **asm-sol-r1-pm-1-005** [PrM+SM] Testmiljön liknar produktionsmiljön tillräckligt för att ett lyckat testanrop ger kunden tillräcklig tillit och direkt översätts till ett lyckat produktionsanrop utan ytterligare felsökning.
- **asm-sol-r1-pm-1-006** [SM] Guiden täcker hela vägen från testmiljö till produktionsmiljö, inklusive eventuella konfigurationsskillnader, så att kunden klarar det sista steget utan extern hjälp.
- **asm-sol-r1-pm-1-007** [OI+PrM] Kunden har tillräcklig teknisk kompetens för att genomföra API-integrationen självständigt utan mänskligt stöd från Flowbase.
- **asm-sol-r1-pm-1-008** [OI+PrM] Kunden är motiverad att sätta igång direkt efter signering och avvaktar inte till ett senare tillfälle när momentum har tappats.
- **asm-sol-r1-pm-1-009** [OI+PrM] Kunden vet vem internt som ska genomföra den tekniska integrationen och att rätt person får tillgång till onboarding-portalen från dag ett.
- **asm-sol-r1-pm-1-010** [OI] Antalet kundinitierade interaktioner med Flowbase minskar när tillgång till credentials och guidad dokumentation ges omedelbart - det vill säga att avsaknad av självbetjäning är den primära orsaken till dagens interaktioner, inte andra faktorer.

## Solution 2: Interaktiv kom-igång-guide direkt efter avtalssignering

**sol-r1-ux-1** [UX, R1]

Kunden möts av en steg-för-steg-guide i portalen så fort avtalet är signerat - guiden leder dem från API-nyckel till första lyckade anrop i produktionsmiljö utan att behöva kontakta Flowbase. Varje steg bekräftas med direkt feedback (grönt bock = lyckat anrop) så att kunden vet exakt var de befinner sig i processen och vad som återstår.

### Assumptions (13)

- **asm-sol-r1-ux-1-001** [PrM+SM] Kunden har tillgång till portalen och guiden omedelbart efter avtalssignering, utan manuella mellansteg från Flowbases sida som försenar åtkomsten.
- **asm-sol-r1-ux-1-002** [SM] Kunden förstår guidens startpunkt och syfte vid första mötet med den, utan behov av förklarande kommunikation utanför portalen.
- **asm-sol-r1-ux-1-003** [SM] Kunden kan självständigt generera och hämta sin API-nyckel direkt i portalen, utan att behöva invänta manuell provisionering från Flowbase.
- **asm-sol-r1-ux-1-004** [OI+PrM+SM] Guiden täcker de tekniska konfigurationssteg, miljöer, autentiseringsmetoder och programmeringsspråk som kunderna faktiskt använder, så att ingen fastnar på ett steg som guiden inte adresserar.
- **asm-sol-r1-ux-1-005** [SM] Portalen kan detektera om ett anrop mot produktionsmiljön lyckades och ge kunden omedelbar, korrekt feedback per steg utan fördröjning.
- **asm-sol-r1-ux-1-006** [OI+SM] Kunden har tekniska förutsättningar att följa guiden självständigt: tillgång till en teknisk person med rätt befogenheter, grundläggande API-kunskaper och tillgång till en testmiljö.
- **asm-sol-r1-ux-1-007** [PrM] Kunder med tillräcklig teknisk kompetens för att konsumera ett API klarar också att följa en steg-för-steg-guide i en portal utan extern hjälp.
- **asm-sol-r1-ux-1-008** [OI+PrM] Den direkta feedbacken per steg (t.ex. grönt bock) är tillräckligt tydlig för att kunden ska förstå om ett anrop lyckades eller om felet ligger i deras egen integration, och inte initiera kontakt med Flowbase för verifiering.
- **asm-sol-r1-ux-1-009** [PrM] Kunderna väljer att följa guiden i stället för att falla tillbaka på gamla kontaktmönster när de stöter på motstånd.
- **asm-sol-r1-ux-1-010** [PrM] Flowbase kan hålla guiden uppdaterad i takt med förändringar i API:et, så att steg-för-steg-instruktionerna inte leder kunden fel vid nästa release.
- **asm-sol-r1-ux-1-011** [OI] Kunder som precis signerat ett avtal är motiverade att komma igång omedelbart och söker aktivt upp guiden i portalen utan att behöva påminnas.
- **asm-sol-r1-ux-1-012** [OI] En steg-för-steg-guide i portalen räcker som enda informationskälla - kunden behöver inte komplettera med extern dokumentation, support eller kollegors hjälp för att ta sig från API-nyckel till första lyckade anrop.
- **asm-sol-r1-ux-1-013** [OI] De vanligaste skälen till att kunder kontaktar Flowbase under aktivering är informationsbrist och osäkerhet om nästa steg - inte tekniska blockerare som kräver mänsklig hjälp från Flowbase.

## Solution 3: Automatisk välkomstpåse med konfigurerade kodexempel för kundens miljö

**sol-r1-ux-2** [UX, R1]

Direkt vid aktivering skickas ett personaliserat paket - med API-nyckel, bas-URL och färdiga kodexempel i de vanligaste språken (Python, JavaScript, cURL) - där variablerna redan är ifyllda med kundens faktiska uppgifter. Kunden kopierar och kör, inget att konfigurera eller slå upp, vilket eliminerar det vanligaste skälet till att höra av sig till Flowbase under onboarding.

### Assumptions (10)

- **asm-sol-r1-ux-2-001** [OI+SM] Flowbases system känner till exakt när en kund aktiveras och kan automatiskt trigga utskicket av välkomstpåsen utan manuellt steg, och levererar uppgifterna snabbt nog för att välkomstpåsen ska skickas i rätt tid i förhållande till när kunden är redo att testa.
- **asm-sol-r1-ux-2-002** [PrM+SM] Alla uppgifter som behövs för att personalisera paketet - API-nyckel, bas-URL och kundens föredragna programmeringsspråk - finns tillgängliga i Flowbases system vid aktiveringstillfället, och är korrekta och giltiga när kunden faktiskt försöker använda dem.
- **asm-sol-r1-ux-2-003** [SM] Välkomstpåsen når rätt teknisk kontaktperson hos kunden i rätt tid, och hamnar inte hos en icke-teknisk mottagare eller i ett spamfilter.
- **asm-sol-r1-ux-2-004** [PrM] Mottagaren av välkomstpåsen är samma person som utför den tekniska integrationen - paketet hamnar hos den som faktiskt ska använda kodexemplen, inte bara hos den som skrivit under avtalet.
- **asm-sol-r1-ux-2-005** [OI+PrM] Kunden läser och agerar på välkomstpåsen vid rätt tidpunkt i sin onboarding - paketet missas inte, arkiveras inte eller återfinns inte för sent.
- **asm-sol-r1-ux-2-006** [OI+PrM+SM] Kodexemplen täcker det programmeringsspråk eller det tekniska format som kundens utvecklare faktiskt använder, och de vanligaste språken Python, JavaScript och cURL räcker för att täcka merparten av fallen - kunder med andra stackar utgör inte en tillräckligt stor grupp för att ge upphov till supportkontakter.
- **asm-sol-r1-ux-2-007** [OI+SM] De förifyllda credentials och kodexemplen är syntaktiskt korrekta, körbara utan att kunden behöver ändra något, och pekar mot rätt miljö så att ett lyckat testanrop bekräftar att integrationen är klar.
- **asm-sol-r1-ux-2-008** [PrM] Kunden kan tolka och använda API-svaret utan stöd - det räcker att det första anropet exekverar utan fel för att kunden ska kunna gå vidare på egen hand.
- **asm-sol-r1-ux-2-009** [OI] Kunder som får API-nyckel, bas-URL och färdiga kodexempel direkt vid aktivering kan genomföra sitt första anrop utan att behöva kontakta Flowbase för att få fram dessa uppgifter.
- **asm-sol-r1-ux-2-010** [OI+PrM] Konfigurationsförvirring kring credentials och bas-URL är den primära anledningen till att kunder kontaktar Flowbase under aktivering - inte frågor om datakvalitet, dataformat, licensvillkor eller andra tekniska hinder.
