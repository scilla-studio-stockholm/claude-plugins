---
title: "Riskiest assumptions: opp-7-1 - jag har inte haft någon guide eller information"
date: 2026-05-29
purpose: Per-solution assumptions scored on importance x evidence (Bland 2x2), with the riskiest flagged and seen against the full categorized set. Phase-3 trio review-and-approve gate. Machine JSON at _working/riskiest-assumptions.json. Input to assist 12 (OST-validation-experiment-designer).
tags: [assumption-risk-mapping, ost, bland, schema-v0.2]

---

# Riskiest assumptions: opp-7-1

> **Trio HITL gate.** Review the importance/evidence calls per assumption. If you disagree with any importance/evidence scoring, edit `decided.assumptions.riskiest[]` in `decisions.json` directly (add or remove entries). The `decided.assumptions` section is the ratified record. Riskiest rows are flagged `[RISKIEST]` inline; each solution opens with a `Riskiest:` summary line of the flagged ids.

Source assumptions-categorized: `_working/assumptions-categorized.json`
Source assumptions: `assumptions.json`
Source top 3 solutions: `OST-discovery/_working/top-three-solutions.json`
Source chosen opportunity: `OST-discovery/decisions.json`
Source product outcome: `OST-discovery/decisions.json`
Schema version: 0.2
Machine JSON: `_working/riskiest-assumptions.json`

Framework: 2x2 importance x evidence (David Bland, *Testing Business Ideas* 2019). Riskiest = high importance + weak evidence. Evidence rule: soft (domain norms and industry conventions count). Rationale format: single sentence, importance-then-evidence.

Total assumptions: 33. Total riskiest: 21.

## Chosen opportunity

**opp-7-1** (Phase: fas-7) - "jag har inte haft någon guide eller information, och ni har ju också sagt att ni inte jobbar med att hjälpa till att implementera - det får kunden göra själv" - *David, intervju-4-aurora-apr-13, ~rad 58*

## Product outcome

> Öka andelen nya kunder som på egen hand når sitt första lyckade produktionsanrop mot API:et utan att kontakta Flowbase, från 40% till 80% inom 60 dagar från avtalstecknande.

## Riskiest assumptions (21)

The assumptions scored **importance=high AND evidence=weak**. These carry forward to assist 12 (validation experiments).

- **asm-sol-r1-pm-1-004** (sol-r1-pm-1: Automatiserad onboarding-portal med självbetjäning från dag ett) [usability] [high/weak] Steg-för-steg-guiden är tillräckligt tydlig och heltäckande för att kunden ska kunna följa den helt på egen hand, och täcker de vanligaste tekniska miljöerna, integrationsmönstren och hindren som Flowbases kunder faktiskt stöter på.
  - Importance=high (en otydlig eller ofullständig guide leder direkt till kontakt med Flowbase); evidence=weak (att en guide täcker alla vanliga miljöer och hinder är obevisat).
  - Why high importance: en otydlig eller ofullständig guide leder direkt till kontakt med Flowbase
  - Why weak evidence: att en guide täcker alla vanliga miljöer och hinder är obevisat
- **asm-sol-r1-pm-1-005** (sol-r1-pm-1: Automatiserad onboarding-portal med självbetjäning från dag ett) [feasibility] [high/weak] Testmiljön liknar produktionsmiljön tillräckligt för att ett lyckat testanrop ger kunden tillräcklig tillit och direkt översätts till ett lyckat produktionsanrop utan ytterligare felsökning.
  - Importance=high (utfallet mäts på produktionsanrop, inte testanrop); evidence=weak (paritet mellan test- och produktionsmiljö är ett känt svårt problem).
  - Why high importance: utfallet mäts på produktionsanrop, inte testanrop
  - Why weak evidence: paritet mellan test- och produktionsmiljö är ett känt svårt problem
- **asm-sol-r1-pm-1-006** (sol-r1-pm-1: Automatiserad onboarding-portal med självbetjäning från dag ett) [usability] [high/weak] Guiden täcker hela vägen från testmiljö till produktionsmiljö, inklusive eventuella konfigurationsskillnader, så att kunden klarar det sista steget utan extern hjälp.
  - Importance=high (sista steget till produktion är just där utfallet avgörs); evidence=weak (att guiden täcker konfigurationsskillnaderna hela vägen är obevisat).
  - Why high importance: sista steget till produktion är just där utfallet avgörs
  - Why weak evidence: att guiden täcker konfigurationsskillnaderna hela vägen är obevisat
- **asm-sol-r1-pm-1-009** (sol-r1-pm-1: Automatiserad onboarding-portal med självbetjäning från dag ett) [usability] [high/weak] Kunden vet vem internt som ska genomföra den tekniska integrationen och att rätt person får tillgång till onboarding-portalen från dag ett.
  - Importance=high (når åtkomsten fel person stannar integrationen och kontakt uppstår); evidence=weak (vem internt som äger integrationen är ett oprövat organisationsantagande).
  - Why high importance: når åtkomsten fel person stannar integrationen och kontakt uppstår
  - Why weak evidence: vem internt som äger integrationen är ett oprövat organisationsantagande
- **asm-sol-r1-pm-1-010** (sol-r1-pm-1: Automatiserad onboarding-portal med självbetjäning från dag ett) [desirability] [high/weak] Antalet kundinitierade interaktioner med Flowbase minskar när tillgång till credentials och guidad dokumentation ges omedelbart - det vill säga att avsaknad av självbetjäning är den primära orsaken till dagens interaktioner, inte andra faktorer.
  - Importance=high (är självbetjäning inte den primära orsaken rör lösningen inte utfallet); evidence=weak (endast en intervju stödjer orsakshypotesen).
  - Why high importance: är självbetjäning inte den primära orsaken rör lösningen inte utfallet
  - Why weak evidence: endast en intervju stödjer orsakshypotesen
- **asm-sol-r1-ux-1-004** (sol-r1-ux-1: Interaktiv kom-igång-guide direkt efter avtalssignering) [usability] [high/weak] Guiden täcker de tekniska konfigurationssteg, miljöer, autentiseringsmetoder och programmeringsspråk som kunderna faktiskt använder, så att ingen fastnar på ett steg som guiden inte adresserar.
  - Importance=high (ett steg guiden inte adresserar gör att kunden fastnar och kontaktar Flowbase); evidence=weak (att guiden täcker alla språk, miljöer och autentiseringsmetoder är obevisat).
  - Why high importance: ett steg guiden inte adresserar gör att kunden fastnar och kontaktar Flowbase
  - Why weak evidence: att guiden täcker alla språk, miljöer och autentiseringsmetoder är obevisat
- **asm-sol-r1-ux-1-005** (sol-r1-ux-1: Interaktiv kom-igång-guide direkt efter avtalssignering) [feasibility] [high/weak] Portalen kan detektera om ett anrop mot produktionsmiljön lyckades och ge kunden omedelbar, korrekt feedback per steg utan fördröjning.
  - Importance=high (utan korrekt feedback per steg uteblir lösningens kärndifferentiator); evidence=weak (realtidsdetektering av kundens produktionsanrop per steg är tekniskt oprövat).
  - Why high importance: utan korrekt feedback per steg uteblir lösningens kärndifferentiator
  - Why weak evidence: realtidsdetektering av kundens produktionsanrop per steg är tekniskt oprövat
- **asm-sol-r1-ux-1-008** (sol-r1-ux-1: Interaktiv kom-igång-guide direkt efter avtalssignering) [usability] [high/weak] Den direkta feedbacken per steg (t.ex. grönt bock) är tillräckligt tydlig för att kunden ska förstå om ett anrop lyckades eller om felet ligger i deras egen integration, och inte initiera kontakt med Flowbase för verifiering.
  - Importance=high (oklar feedback utlöser verifieringskontakter som ska elimineras); evidence=weak (att feedbacken särskiljer lyckat anrop från eget integrationsfel är spekulativt).
  - Why high importance: oklar feedback utlöser verifieringskontakter som ska elimineras
  - Why weak evidence: att feedbacken särskiljer lyckat anrop från eget integrationsfel är spekulativt
- **asm-sol-r1-ux-1-009** (sol-r1-ux-1: Interaktiv kom-igång-guide direkt efter avtalssignering) [desirability] [high/weak] Kunderna väljer att följa guiden i stället för att falla tillbaka på gamla kontaktmönster när de stöter på motstånd.
  - Importance=high (faller kunden tillbaka på gamla kontaktmönster bryts utfallet); evidence=weak (att kunder väljer guiden framför invant kontaktbeteende är ett oprövat beteendeantagande).
  - Why high importance: faller kunden tillbaka på gamla kontaktmönster bryts utfallet
  - Why weak evidence: att kunder väljer guiden framför invant kontaktbeteende är ett oprövat beteendeantagande
- **asm-sol-r1-ux-1-010** (sol-r1-ux-1: Interaktiv kom-igång-guide direkt efter avtalssignering) [viability] [high/weak] Flowbase kan hålla guiden uppdaterad i takt med förändringar i API:et, så att steg-för-steg-instruktionerna inte leder kunden fel vid nästa release.
  - Importance=high (en inaktuell guide leder kunden fel och utlöser kontakt); evidence=weak (att Flowbase orkar hålla guiden synkad med varje release är obevisat).
  - Why high importance: en inaktuell guide leder kunden fel och utlöser kontakt
  - Why weak evidence: att Flowbase orkar hålla guiden synkad med varje release är obevisat
- **asm-sol-r1-ux-1-012** (sol-r1-ux-1: Interaktiv kom-igång-guide direkt efter avtalssignering) [usability] [high/weak] En steg-för-steg-guide i portalen räcker som enda informationskälla - kunden behöver inte komplettera med extern dokumentation, support eller kollegors hjälp för att ta sig från API-nyckel till första lyckade anrop.
  - Importance=high (räcker inte guiden ensam söker kunden extern hjälp eller support); evidence=weak (att en enda guide ersätter all annan informationskälla är obevisat).
  - Why high importance: räcker inte guiden ensam söker kunden extern hjälp eller support
  - Why weak evidence: att en enda guide ersätter all annan informationskälla är obevisat
- **asm-sol-r1-ux-1-013** (sol-r1-ux-1: Interaktiv kom-igång-guide direkt efter avtalssignering) [desirability] [high/weak] De vanligaste skälen till att kunder kontaktar Flowbase under aktivering är informationsbrist och osäkerhet om nästa steg - inte tekniska blockerare som kräver mänsklig hjälp från Flowbase.
  - Importance=high (är orsaken tekniska blockerare rör en informationsguide inte utfallet); evidence=weak (endast en intervju stödjer orsakshypotesen).
  - Why high importance: är orsaken tekniska blockerare rör en informationsguide inte utfallet
  - Why weak evidence: endast en intervju stödjer orsakshypotesen
- **asm-sol-r1-ux-2-001** (sol-r1-ux-2: Automatisk välkomstpåse med konfigurerade kodexempel för kundens miljö) [feasibility] [high/weak] Flowbases system känner till exakt när en kund aktiveras och kan automatiskt trigga utskicket av välkomstpåsen utan manuellt steg, och levererar uppgifterna snabbt nog för att välkomstpåsen ska skickas i rätt tid i förhållande till när kunden är redo att testa.
  - Importance=high (uteblir automatiskt och rättidigt utskick återinförs manuell hantering); evidence=weak (att systemet skickar i rätt tid relativt kundens faktiska redo-läge är oprövat).
  - Why high importance: uteblir automatiskt och rättidigt utskick återinförs manuell hantering
  - Why weak evidence: att systemet skickar i rätt tid relativt kundens faktiska redo-läge är oprövat
- **asm-sol-r1-ux-2-002** (sol-r1-ux-2: Automatisk välkomstpåse med konfigurerade kodexempel för kundens miljö) [feasibility] [high/weak] Alla uppgifter som behövs för att personalisera paketet - API-nyckel, bas-URL och kundens föredragna programmeringsspråk - finns tillgängliga i Flowbases system vid aktiveringstillfället, och är korrekta och giltiga när kunden faktiskt försöker använda dem.
  - Importance=high (saknas eller felar persondatan blir paketet obrukbart och kontakt uppstår); evidence=weak (kundens föredragna programmeringsspråk finns sällan i Flowbases system).
  - Why high importance: saknas eller felar persondatan blir paketet obrukbart och kontakt uppstår
  - Why weak evidence: kundens föredragna programmeringsspråk finns sällan i Flowbases system
- **asm-sol-r1-ux-2-003** (sol-r1-ux-2: Automatisk välkomstpåse med konfigurerade kodexempel för kundens miljö) [usability] [high/weak] Välkomstpåsen når rätt teknisk kontaktperson hos kunden i rätt tid, och hamnar inte hos en icke-teknisk mottagare eller i ett spamfilter.
  - Importance=high (når paketet fel mottagare eller spam agerar ingen och kontakt uppstår); evidence=weak (att B2B-utskick når rätt teknisk kontakt och undviker spamfilter är osäkert).
  - Why high importance: når paketet fel mottagare eller spam agerar ingen och kontakt uppstår
  - Why weak evidence: att B2B-utskick når rätt teknisk kontakt och undviker spamfilter är osäkert
- **asm-sol-r1-ux-2-004** (sol-r1-ux-2: Automatisk välkomstpåse med konfigurerade kodexempel för kundens miljö) [usability] [high/weak] Mottagaren av välkomstpåsen är samma person som utför den tekniska integrationen - paketet hamnar hos den som faktiskt ska använda kodexemplen, inte bara hos den som skrivit under avtalet.
  - Importance=high (hamnar paketet inte hos integratören används kodexemplen aldrig); evidence=weak (att mottagaren är samma person som integrerar är ett oprövat organisationsantagande).
  - Why high importance: hamnar paketet inte hos integratören används kodexemplen aldrig
  - Why weak evidence: att mottagaren är samma person som integrerar är ett oprövat organisationsantagande
- **asm-sol-r1-ux-2-005** (sol-r1-ux-2: Automatisk välkomstpåse med konfigurerade kodexempel för kundens miljö) [desirability] [high/weak] Kunden läser och agerar på välkomstpåsen vid rätt tidpunkt i sin onboarding - paketet missas inte, arkiveras inte eller återfinns inte för sent.
  - Importance=high (missas eller arkiveras paketet kringgås hela mekanismen); evidence=weak (att ett pushat paket faktiskt konsumeras i rätt tid är ett spekulativt beteendeantagande).
  - Why high importance: missas eller arkiveras paketet kringgås hela mekanismen
  - Why weak evidence: att ett pushat paket faktiskt konsumeras i rätt tid är ett spekulativt beteendeantagande
- **asm-sol-r1-ux-2-006** (sol-r1-ux-2: Automatisk välkomstpåse med konfigurerade kodexempel för kundens miljö) [usability] [high/weak] Kodexemplen täcker det programmeringsspråk eller det tekniska format som kundens utvecklare faktiskt använder, och de vanligaste språken Python, JavaScript och cURL räcker för att täcka merparten av fallen - kunder med andra stackar utgör inte en tillräckligt stor grupp för att ge upphov till supportkontakter.
  - Importance=high (saknas kundens språk fastnar utvecklaren och kontaktar Flowbase); evidence=weak (att Python, JavaScript och cURL täcker merparten av kundernas stackar är obevisat).
  - Why high importance: saknas kundens språk fastnar utvecklaren och kontaktar Flowbase
  - Why weak evidence: att Python, JavaScript och cURL täcker merparten av kundernas stackar är obevisat
- **asm-sol-r1-ux-2-007** (sol-r1-ux-2: Automatisk välkomstpåse med konfigurerade kodexempel för kundens miljö) [feasibility] [high/weak] De förifyllda credentials och kodexemplen är syntaktiskt korrekta, körbara utan att kunden behöver ändra något, och pekar mot rätt miljö så att ett lyckat testanrop bekräftar att integrationen är klar.
  - Importance=high (felaktiga eller icke-körbara exempel utlöser direkt kontakt); evidence=weak (per-kund-genererad, körbar och rätt-riktad kod utan ändring är tekniskt oprövat).
  - Why high importance: felaktiga eller icke-körbara exempel utlöser direkt kontakt
  - Why weak evidence: per-kund-genererad, körbar och rätt-riktad kod utan ändring är tekniskt oprövat
- **asm-sol-r1-ux-2-009** (sol-r1-ux-2: Automatisk välkomstpåse med konfigurerade kodexempel för kundens miljö) [desirability] [high/weak] Kunder som får API-nyckel, bas-URL och färdiga kodexempel direkt vid aktivering kan genomföra sitt första anrop utan att behöva kontakta Flowbase för att få fram dessa uppgifter.
  - Importance=high (krävs ändå kontakt för att få fram uppgifterna rör lösningen inte utfallet); evidence=weak (att färdiga credentials och kodexempel tar bort kontaktbehovet är obevisat).
  - Why high importance: krävs ändå kontakt för att få fram uppgifterna rör lösningen inte utfallet
  - Why weak evidence: att färdiga credentials och kodexempel tar bort kontaktbehovet är obevisat
- **asm-sol-r1-ux-2-010** (sol-r1-ux-2: Automatisk välkomstpåse med konfigurerade kodexempel för kundens miljö) [desirability] [high/weak] Konfigurationsförvirring kring credentials och bas-URL är den primära anledningen till att kunder kontaktar Flowbase under aktivering - inte frågor om datakvalitet, dataformat, licensvillkor eller andra tekniska hinder.
  - Importance=high (är orsaken något annat än konfigurationsförvirring rör lösningen inte utfallet); evidence=weak (endast partiellt intervjustöd för orsakshypotesen).
  - Why high importance: är orsaken något annat än konfigurationsförvirring rör lösningen inte utfallet
  - Why weak evidence: endast partiellt intervjustöd för orsakshypotesen

## Seen against the full set

Every categorized assumption with its importance/evidence score, grouped by solution. This is why the OTHER assumptions were NOT flagged as riskiest: only `[high/weak]` rows qualify. Read against `_working/assumptions-categorized.json` for the upstream categorization, but this section stands alone.

### Solution 1: Automatiserad onboarding-portal med självbetjäning från dag ett

**sol-r1-pm-1** [PM, R1]

När kunden signerar avtalet aktiveras automatiskt en personaliserad onboarding-portal med steg-för-steg-guide, API-nycklar och testmiljö - allt utan att Flowbase behöver agera. Kunden kan göra sitt första lyckade API-anrop helt på egen hand, vilket direkt mäter sig mot målet om 80% självbetjänade kunder.

**Riskiest:** asm-sol-r1-pm-1-004, asm-sol-r1-pm-1-005, asm-sol-r1-pm-1-006, asm-sol-r1-pm-1-009, asm-sol-r1-pm-1-010

#### Assumptions (10)

- **asm-sol-r1-pm-1-001** [PrM+SM] [feasibility] [high/strong] Avtalssigneringen sker i ett system som kan generera en maskinläsbar händelse som tillförlitligt triggar automatisk aktivering av onboarding-portalen utan manuell handpåläggning.
  - Importance=high (utan automatisk trigger krävs manuell aktivering och självbetjäningen faller); evidence=strong (webhook-baserad aktivering vid e-signering är ett etablerat integrationsmönster).
- **asm-sol-r1-pm-1-002** [OI+SM] [feasibility] [high/strong] Aktiveringen provisionerar korrekt kundspecifika API-nycklar, behörigheter och testmiljöåtkomst direkt vid trigger - utan manuella steg i Flowbases interna system.
  - Importance=high (manuell provisionering återinför den interaktion lösningen ska ta bort); evidence=strong (automatiserad nyckel- och behörighetsprovisionering är branschstandard för API-plattformar).
- **asm-sol-r1-pm-1-003** [SM] [usability] [high/strong] Kunden tar emot portalinbjudan, uppfattar den som nästa steg i onboardingen och loggar in utan att behöva kontakta Flowbase för hjälp.
  - Importance=high (loggar kunden inte in självmant uteblir hela självbetjäningen); evidence=strong (portalinbjudan som nästa steg är ett väletablerat onboarding-mönster).
- **asm-sol-r1-pm-1-004** [OI+PrM+SM] [usability] [high/weak] **[RISKIEST]** Steg-för-steg-guiden är tillräckligt tydlig och heltäckande för att kunden ska kunna följa den helt på egen hand, och täcker de vanligaste tekniska miljöerna, integrationsmönstren och hindren som Flowbases kunder faktiskt stöter på.
  - Importance=high (en otydlig eller ofullständig guide leder direkt till kontakt med Flowbase); evidence=weak (att en guide täcker alla vanliga miljöer och hinder är obevisat).
- **asm-sol-r1-pm-1-005** [PrM+SM] [feasibility] [high/weak] **[RISKIEST]** Testmiljön liknar produktionsmiljön tillräckligt för att ett lyckat testanrop ger kunden tillräcklig tillit och direkt översätts till ett lyckat produktionsanrop utan ytterligare felsökning.
  - Importance=high (utfallet mäts på produktionsanrop, inte testanrop); evidence=weak (paritet mellan test- och produktionsmiljö är ett känt svårt problem).
- **asm-sol-r1-pm-1-006** [SM] [usability] [high/weak] **[RISKIEST]** Guiden täcker hela vägen från testmiljö till produktionsmiljö, inklusive eventuella konfigurationsskillnader, så att kunden klarar det sista steget utan extern hjälp.
  - Importance=high (sista steget till produktion är just där utfallet avgörs); evidence=weak (att guiden täcker konfigurationsskillnaderna hela vägen är obevisat).
- **asm-sol-r1-pm-1-007** [OI+PrM] [usability] [high/strong] Kunden har tillräcklig teknisk kompetens för att genomföra API-integrationen självständigt utan mänskligt stöd från Flowbase.
  - Importance=high (saknar kunden teknisk kompetens uteblir det självständiga genomförandet); evidence=strong (API-konsumenter är typiskt utvecklare med grundläggande integrationsvana).
- **asm-sol-r1-pm-1-008** [OI+PrM] [desirability] [low/weak] Kunden är motiverad att sätta igång direkt efter signering och avvaktar inte till ett senare tillfälle när momentum har tappats.
  - Importance=low (fördröjd start bryter inte lösningen, kunden kan självbetjäna senare); evidence=weak (kundens motivationstajming är ett spekulativt beteendeantagande).
- **asm-sol-r1-pm-1-009** [OI+PrM] [usability] [high/weak] **[RISKIEST]** Kunden vet vem internt som ska genomföra den tekniska integrationen och att rätt person får tillgång till onboarding-portalen från dag ett.
  - Importance=high (når åtkomsten fel person stannar integrationen och kontakt uppstår); evidence=weak (vem internt som äger integrationen är ett oprövat organisationsantagande).
- **asm-sol-r1-pm-1-010** [OI] [desirability] [high/weak] **[RISKIEST]** Antalet kundinitierade interaktioner med Flowbase minskar när tillgång till credentials och guidad dokumentation ges omedelbart - det vill säga att avsaknad av självbetjäning är den primära orsaken till dagens interaktioner, inte andra faktorer.
  - Importance=high (är självbetjäning inte den primära orsaken rör lösningen inte utfallet); evidence=weak (endast en intervju stödjer orsakshypotesen).

### Solution 2: Interaktiv kom-igång-guide direkt efter avtalssignering

**sol-r1-ux-1** [UX, R1]

Kunden möts av en steg-för-steg-guide i portalen så fort avtalet är signerat - guiden leder dem från API-nyckel till första lyckade anrop i produktionsmiljö utan att behöva kontakta Flowbase. Varje steg bekräftas med direkt feedback (grönt bock = lyckat anrop) så att kunden vet exakt var de befinner sig i processen och vad som återstår.

**Riskiest:** asm-sol-r1-ux-1-004, asm-sol-r1-ux-1-005, asm-sol-r1-ux-1-008, asm-sol-r1-ux-1-009, asm-sol-r1-ux-1-010, asm-sol-r1-ux-1-012, asm-sol-r1-ux-1-013

#### Assumptions (13)

- **asm-sol-r1-ux-1-001** [PrM+SM] [feasibility] [high/strong] Kunden har tillgång till portalen och guiden omedelbart efter avtalssignering, utan manuella mellansteg från Flowbases sida som försenar åtkomsten.
  - Importance=high (manuella mellansteg återinför fördröjning och kontakt); evidence=strong (omedelbar portalåtkomst efter signering är ett etablerat onboarding-mönster).
- **asm-sol-r1-ux-1-002** [SM] [usability] [high/strong] Kunden förstår guidens startpunkt och syfte vid första mötet med den, utan behov av förklarande kommunikation utanför portalen.
  - Importance=high (förstår kunden inte guidens start uppstår kontakt direkt); evidence=strong (självförklarande startpunkt är en designbar och konventionell guide-praxis).
- **asm-sol-r1-ux-1-003** [SM] [feasibility] [high/strong] Kunden kan självständigt generera och hämta sin API-nyckel direkt i portalen, utan att behöva invänta manuell provisionering från Flowbase.
  - Importance=high (utan egen nyckel kan inget anrop göras); evidence=strong (självbetjänad nyckelgenerering är standardfunktion i utvecklarportaler).
- **asm-sol-r1-ux-1-004** [OI+PrM+SM] [usability] [high/weak] **[RISKIEST]** Guiden täcker de tekniska konfigurationssteg, miljöer, autentiseringsmetoder och programmeringsspråk som kunderna faktiskt använder, så att ingen fastnar på ett steg som guiden inte adresserar.
  - Importance=high (ett steg guiden inte adresserar gör att kunden fastnar och kontaktar Flowbase); evidence=weak (att guiden täcker alla språk, miljöer och autentiseringsmetoder är obevisat).
- **asm-sol-r1-ux-1-005** [SM] [feasibility] [high/weak] **[RISKIEST]** Portalen kan detektera om ett anrop mot produktionsmiljön lyckades och ge kunden omedelbar, korrekt feedback per steg utan fördröjning.
  - Importance=high (utan korrekt feedback per steg uteblir lösningens kärndifferentiator); evidence=weak (realtidsdetektering av kundens produktionsanrop per steg är tekniskt oprövat).
- **asm-sol-r1-ux-1-006** [OI+SM] [usability] [high/strong] Kunden har tekniska förutsättningar att följa guiden självständigt: tillgång till en teknisk person med rätt befogenheter, grundläggande API-kunskaper och tillgång till en testmiljö.
  - Importance=high (saknas tekniska förutsättningar kan guiden inte följas självständigt); evidence=strong (API-kunder har typiskt en teknisk person och testmiljötillgång).
- **asm-sol-r1-ux-1-007** [PrM] [usability] [high/strong] Kunder med tillräcklig teknisk kompetens för att konsumera ett API klarar också att följa en steg-för-steg-guide i en portal utan extern hjälp.
  - Importance=high (klarar inte kompetenta kunder guiden faller självbetjäningen); evidence=strong (kan man konsumera ett API kan man rimligen följa en stegvis guide).
- **asm-sol-r1-ux-1-008** [OI+PrM] [usability] [high/weak] **[RISKIEST]** Den direkta feedbacken per steg (t.ex. grönt bock) är tillräckligt tydlig för att kunden ska förstå om ett anrop lyckades eller om felet ligger i deras egen integration, och inte initiera kontakt med Flowbase för verifiering.
  - Importance=high (oklar feedback utlöser verifieringskontakter som ska elimineras); evidence=weak (att feedbacken särskiljer lyckat anrop från eget integrationsfel är spekulativt).
- **asm-sol-r1-ux-1-009** [PrM] [desirability] [high/weak] **[RISKIEST]** Kunderna väljer att följa guiden i stället för att falla tillbaka på gamla kontaktmönster när de stöter på motstånd.
  - Importance=high (faller kunden tillbaka på gamla kontaktmönster bryts utfallet); evidence=weak (att kunder väljer guiden framför invant kontaktbeteende är ett oprövat beteendeantagande).
- **asm-sol-r1-ux-1-010** [PrM] [viability] [high/weak] **[RISKIEST]** Flowbase kan hålla guiden uppdaterad i takt med förändringar i API:et, så att steg-för-steg-instruktionerna inte leder kunden fel vid nästa release.
  - Importance=high (en inaktuell guide leder kunden fel och utlöser kontakt); evidence=weak (att Flowbase orkar hålla guiden synkad med varje release är obevisat).
- **asm-sol-r1-ux-1-011** [OI] [desirability] [low/weak] Kunder som precis signerat ett avtal är motiverade att komma igång omedelbart och söker aktivt upp guiden i portalen utan att behöva påminnas.
  - Importance=low (uteblir omedelbar start kan kunden söka guiden senare utan att lösningen bryts); evidence=weak (kundens motivation att agera direkt är ett spekulativt beteendeantagande).
- **asm-sol-r1-ux-1-012** [OI] [usability] [high/weak] **[RISKIEST]** En steg-för-steg-guide i portalen räcker som enda informationskälla - kunden behöver inte komplettera med extern dokumentation, support eller kollegors hjälp för att ta sig från API-nyckel till första lyckade anrop.
  - Importance=high (räcker inte guiden ensam söker kunden extern hjälp eller support); evidence=weak (att en enda guide ersätter all annan informationskälla är obevisat).
- **asm-sol-r1-ux-1-013** [OI] [desirability] [high/weak] **[RISKIEST]** De vanligaste skälen till att kunder kontaktar Flowbase under aktivering är informationsbrist och osäkerhet om nästa steg - inte tekniska blockerare som kräver mänsklig hjälp från Flowbase.
  - Importance=high (är orsaken tekniska blockerare rör en informationsguide inte utfallet); evidence=weak (endast en intervju stödjer orsakshypotesen).

### Solution 3: Automatisk välkomstpåse med konfigurerade kodexempel för kundens miljö

**sol-r1-ux-2** [UX, R1]

Direkt vid aktivering skickas ett personaliserat paket - med API-nyckel, bas-URL och färdiga kodexempel i de vanligaste språken (Python, JavaScript, cURL) - där variablerna redan är ifyllda med kundens faktiska uppgifter. Kunden kopierar och kör, inget att konfigurera eller slå upp, vilket eliminerar det vanligaste skälet till att höra av sig till Flowbase under onboarding.

**Riskiest:** asm-sol-r1-ux-2-001, asm-sol-r1-ux-2-002, asm-sol-r1-ux-2-003, asm-sol-r1-ux-2-004, asm-sol-r1-ux-2-005, asm-sol-r1-ux-2-006, asm-sol-r1-ux-2-007, asm-sol-r1-ux-2-009, asm-sol-r1-ux-2-010

#### Assumptions (10)

- **asm-sol-r1-ux-2-001** [OI+SM] [feasibility] [high/weak] **[RISKIEST]** Flowbases system känner till exakt när en kund aktiveras och kan automatiskt trigga utskicket av välkomstpåsen utan manuellt steg, och levererar uppgifterna snabbt nog för att välkomstpåsen ska skickas i rätt tid i förhållande till när kunden är redo att testa.
  - Importance=high (uteblir automatiskt och rättidigt utskick återinförs manuell hantering); evidence=weak (att systemet skickar i rätt tid relativt kundens faktiska redo-läge är oprövat).
- **asm-sol-r1-ux-2-002** [PrM+SM] [feasibility] [high/weak] **[RISKIEST]** Alla uppgifter som behövs för att personalisera paketet - API-nyckel, bas-URL och kundens föredragna programmeringsspråk - finns tillgängliga i Flowbases system vid aktiveringstillfället, och är korrekta och giltiga när kunden faktiskt försöker använda dem.
  - Importance=high (saknas eller felar persondatan blir paketet obrukbart och kontakt uppstår); evidence=weak (kundens föredragna programmeringsspråk finns sällan i Flowbases system).
- **asm-sol-r1-ux-2-003** [SM] [usability] [high/weak] **[RISKIEST]** Välkomstpåsen når rätt teknisk kontaktperson hos kunden i rätt tid, och hamnar inte hos en icke-teknisk mottagare eller i ett spamfilter.
  - Importance=high (når paketet fel mottagare eller spam agerar ingen och kontakt uppstår); evidence=weak (att B2B-utskick når rätt teknisk kontakt och undviker spamfilter är osäkert).
- **asm-sol-r1-ux-2-004** [PrM] [usability] [high/weak] **[RISKIEST]** Mottagaren av välkomstpåsen är samma person som utför den tekniska integrationen - paketet hamnar hos den som faktiskt ska använda kodexemplen, inte bara hos den som skrivit under avtalet.
  - Importance=high (hamnar paketet inte hos integratören används kodexemplen aldrig); evidence=weak (att mottagaren är samma person som integrerar är ett oprövat organisationsantagande).
- **asm-sol-r1-ux-2-005** [OI+PrM] [desirability] [high/weak] **[RISKIEST]** Kunden läser och agerar på välkomstpåsen vid rätt tidpunkt i sin onboarding - paketet missas inte, arkiveras inte eller återfinns inte för sent.
  - Importance=high (missas eller arkiveras paketet kringgås hela mekanismen); evidence=weak (att ett pushat paket faktiskt konsumeras i rätt tid är ett spekulativt beteendeantagande).
- **asm-sol-r1-ux-2-006** [OI+PrM+SM] [usability] [high/weak] **[RISKIEST]** Kodexemplen täcker det programmeringsspråk eller det tekniska format som kundens utvecklare faktiskt använder, och de vanligaste språken Python, JavaScript och cURL räcker för att täcka merparten av fallen - kunder med andra stackar utgör inte en tillräckligt stor grupp för att ge upphov till supportkontakter.
  - Importance=high (saknas kundens språk fastnar utvecklaren och kontaktar Flowbase); evidence=weak (att Python, JavaScript och cURL täcker merparten av kundernas stackar är obevisat).
- **asm-sol-r1-ux-2-007** [OI+SM] [feasibility] [high/weak] **[RISKIEST]** De förifyllda credentials och kodexemplen är syntaktiskt korrekta, körbara utan att kunden behöver ändra något, och pekar mot rätt miljö så att ett lyckat testanrop bekräftar att integrationen är klar.
  - Importance=high (felaktiga eller icke-körbara exempel utlöser direkt kontakt); evidence=weak (per-kund-genererad, körbar och rätt-riktad kod utan ändring är tekniskt oprövat).
- **asm-sol-r1-ux-2-008** [PrM] [usability] [high/strong] Kunden kan tolka och använda API-svaret utan stöd - det räcker att det första anropet exekverar utan fel för att kunden ska kunna gå vidare på egen hand.
  - Importance=high (kan kunden inte tolka API-svaret uppstår kontakt); evidence=strong (utvecklare som konsumerar ett API kan typiskt tolka ett API-svar).
- **asm-sol-r1-ux-2-009** [OI] [desirability] [high/weak] **[RISKIEST]** Kunder som får API-nyckel, bas-URL och färdiga kodexempel direkt vid aktivering kan genomföra sitt första anrop utan att behöva kontakta Flowbase för att få fram dessa uppgifter.
  - Importance=high (krävs ändå kontakt för att få fram uppgifterna rör lösningen inte utfallet); evidence=weak (att färdiga credentials och kodexempel tar bort kontaktbehovet är obevisat).
- **asm-sol-r1-ux-2-010** [OI+PrM] [desirability] [high/weak] **[RISKIEST]** Konfigurationsförvirring kring credentials och bas-URL är den primära anledningen till att kunder kontaktar Flowbase under aktivering - inte frågor om datakvalitet, dataformat, licensvillkor eller andra tekniska hinder.
  - Importance=high (är orsaken något annat än konfigurationsförvirring rör lösningen inte utfallet); evidence=weak (endast partiellt intervjustöd för orsakshypotesen).
