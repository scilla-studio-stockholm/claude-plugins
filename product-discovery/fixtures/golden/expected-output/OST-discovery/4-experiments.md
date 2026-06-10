---
title: "Validation experiments: opp-7-1 - jag har inte haft någon guide eller information"
date: 2026-05-29
purpose: Self-contained MILESTONE doc. Bland Test Cards for the riskiest assumptions surfaced in phase 4. Terminal run-list for the trio. Machine JSON at _working/validation-experiments.json (plumbing; not required to run experiments).
tags: [assumption-validation, ost, bland, test-card, schema-v0.2]

---

# Validation experiments: opp-7-1

> **Trio run-list handoff.** This is the terminal artifact for the discovery critical path. Read the Test Cards; pick execution order based on resource availability, dependencies, and team capacity; run the cheapest viable test first per Bland's principle. The skill does NOT pick sequence. Capture results separately (a future Learning-Card skill is parked). If a recommended test does not fit your context, swap to one of the 2 alternatives.

Source chosen opportunity: `OST-discovery/decisions.json`
Source product outcome: `OST-discovery/decisions.json`
Source OST-riskiest-assumptions: `riskiest-assumptions.json`
Source assumptions-categorized: `assumptions-categorized.json`
Source top 3 solutions: `OST-discovery/_working/top-three-solutions.json`
Schema version: 0.2
Machine JSON (plumbing, not required to run): `_working/validation-experiments.json`

Framework: Bland Test Card with cheapest-viable selection. Category-default + named override. alternative_tests fixed at 2. success_criteria regex-anchored.

Total riskiest: 21. Total Test Cards: 21.

## Chosen opportunity

**opp-7-1** (Phase: fas-7) - "jag har inte haft någon guide eller information, och ni har ju också sagt att ni inte jobbar med att hjälpa till att implementera - det får kunden göra själv" - *David, intervju-4-aurora-apr-13, ~rad 58*

## Product outcome

> Öka andelen nya kunder som på egen hand når sitt första lyckade produktionsanrop mot API:et utan att kontakta Flowbase, från 40% till 80% inom 60 dagar från avtalstecknande.

## Solution 1: Automatiserad onboarding-portal med självbetjäning från dag ett

**sol-r1-pm-1** [PM, R1]

När kunden signerar avtalet aktiveras automatiskt en personaliserad onboarding-portal med steg-för-steg-guide, API-nycklar och testmiljö - allt utan att Flowbase behöver agera. Kunden kan göra sitt första lyckade API-anrop helt på egen hand, vilket direkt mäter sig mot målet om 80% självbetjänade kunder.

**Test Cards in this solution (5):**

### asm-sol-r1-pm-1-004 [OI+PrM+SM] [usability] [high/weak]

**Assumption:** Steg-för-steg-guiden är tillräckligt tydlig och heltäckande för att kunden ska kunna följa den helt på egen hand, och täcker de vanligaste tekniska miljöerna, integrationsmönstren och hindren som Flowbases kunder faktiskt stöter på.

**Upstream rationale:** Importance=high (en otydlig eller ofullständig guide leder direkt till kontakt med Flowbase); evidence=weak (att en guide täcker alla vanliga miljöer och hinder är obevisat).

**Recommended test: Paper or click-through prototype**

> **Hypothesis:** We believe that en steg-för-steg-guide kan vara tillräckligt tydlig och heltäckande för att kunder ska genomföra integrationen på egen hand utan att kontakta Flowbase.
> **Test:** To verify that, we will skapa en klickbar prototyp av guiden och låta 8 representativa kunder försöka ta sig genom en typisk API-integration utan hjälp. Vi observerar var de fastnar och loggar varje punkt guiden inte täcker.
> **Metric:** And measure andelen testdeltagare som når ett lyckat anrop utan att be om hjälp, samt antalet och typen av blockeringspunkter.
> **Success criteria:** We are right if minst 6 av 8 deltagare når ett lyckat anrop utan extern hjälp.

**Cost:** low | **Time:** days | **Evidence:** moderate

**Why this test:** Default for usability is Paper or click-through prototype (used as-is.)

**Alternatives:**

- **Concierge:** Om vi vill hitta guidens luckor genom att manuellt stötta några kunder live innan en prototyp byggs.
- **Customer interview:** Om vi först vill kartlägga vilka miljöer och hinder kunderna faktiskt möter.

---

### asm-sol-r1-pm-1-005 [PrM+SM] [feasibility] [high/weak]

**Assumption:** Testmiljön liknar produktionsmiljön tillräckligt för att ett lyckat testanrop ger kunden tillräcklig tillit och direkt översätts till ett lyckat produktionsanrop utan ytterligare felsökning.

**Upstream rationale:** Importance=high (utfallet mäts på produktionsanrop, inte testanrop); evidence=weak (paritet mellan test- och produktionsmiljö är ett känt svårt problem).

**Recommended test: Technical spike or proof-of-concept**

> **Hypothesis:** We believe that testmiljön liknar produktionsmiljön tillräckligt för att ett lyckat testanrop direkt översätts till ett lyckat produktionsanrop utan ytterligare felsökning.
> **Test:** To verify that, we will köra en representativ uppsättning anrop mot både test- och produktionsmiljön med samma payloads. Vi jämför svar, statuskoder och konfigurationskrav steg för steg.
> **Metric:** And measure andelen testade anropsscenarier där test- och produktionsutfallet är identiskt utan extra konfiguration.
> **Success criteria:** We are right if minst 90% av de testade anropsscenarierna ger identiskt utfall i test och produktion.

**Cost:** low | **Time:** days | **Evidence:** strong

**Why this test:** Default for feasibility is Technical spike or proof-of-concept (used as-is.)

**Alternatives:**

- **Concierge:** Om vi vill följa några riktiga kunders test-till-prod-övergång manuellt för att se var de skiljer sig.
- **Customer interview:** Om vi vill fråga kunder som nyligen gått live var test och prod faktiskt skilde sig.

---

### asm-sol-r1-pm-1-006 [SM] [usability] [high/weak]

**Assumption:** Guiden täcker hela vägen från testmiljö till produktionsmiljö, inklusive eventuella konfigurationsskillnader, så att kunden klarar det sista steget utan extern hjälp.

**Upstream rationale:** Importance=high (sista steget till produktion är just där utfallet avgörs); evidence=weak (att guiden täcker konfigurationsskillnaderna hela vägen är obevisat).

**Recommended test: Concierge**

> **Hypothesis:** We believe that guiden kan täcka hela vägen från testmiljö till produktionsmiljö, inklusive konfigurationsskillnader, så att kunden klarar det sista steget utan extern hjälp.
> **Test:** To verify that, we will låta 5 nyaktiverade kunder ta sig från ett lyckat testanrop till ett lyckat produktionsanrop med enbart guideutkastet. Teamet observerar utan att ingripa förrän kunden kör fast och loggar varje punkt där guiden inte räcker.
> **Metric:** And measure andelen kunder som når ett lyckat produktionsanrop med enbart guiden, och antalet gånger teamet behövde ingripa.
> **Success criteria:** We are right if minst 4 av 5 kunder når ett lyckat produktionsanrop utan att teamet behöver ingripa.

**Cost:** medium | **Time:** days | **Evidence:** strong

**Why this test:** Default for usability is Paper or click-through prototype, but Concierge fits because det sista steget till produktion kräver verklig miljökonfiguration som en pappersprototyp inte kan återskapa.

**Alternatives:**

- **Paper or click-through prototype:** Om vi först vill screena guidens tydlighet billigt innan ett live-test.
- **Technical spike or proof-of-concept:** Om vi vill verifiera de tekniska konfigurationsskillnaderna mellan test och prod separat.

---

### asm-sol-r1-pm-1-009 [OI+PrM] [usability] [high/weak]

**Assumption:** Kunden vet vem internt som ska genomföra den tekniska integrationen och att rätt person får tillgång till onboarding-portalen från dag ett.

**Upstream rationale:** Importance=high (når åtkomsten fel person stannar integrationen och kontakt uppstår); evidence=weak (vem internt som äger integrationen är ett oprövat organisationsantagande).

**Recommended test: Customer interview**

> **Hypothesis:** We believe that kunden vet vem internt som ska genomföra den tekniska integrationen och att rätt person får tillgång till onboarding-portalen från dag ett.
> **Test:** To verify that, we will intervjua 8 nyligen onboardade kunder om vem som faktiskt fick portalinbjudan, vem som utförde integrationen och om rätt person hade åtkomst från start.
> **Metric:** And measure andelen kunder där den tekniska integratören var samma person som fick portalåtkomst dag ett.
> **Success criteria:** We are right if minst 6 av 8 intervjuade kunder bekräftar att rätt teknisk person hade portalåtkomst från dag ett.

**Cost:** low | **Time:** days | **Evidence:** moderate

**Why this test:** Default for usability is Paper or click-through prototype, but Customer interview fits because antagandet gäller kundens interna rollfördelning och åtkomst, inte gränssnittets användbarhet.

**Alternatives:**

- **Survey:** Om vi vill kartlägga bredare vem som äger integrationen hos kunderna.
- **Concierge:** Om vi vill följa några kunder från signering för att se vem som faktiskt agerar.

---

### asm-sol-r1-pm-1-010 [OI] [desirability] [high/weak]

**Assumption:** Antalet kundinitierade interaktioner med Flowbase minskar när tillgång till credentials och guidad dokumentation ges omedelbart - det vill säga att avsaknad av självbetjäning är den primära orsaken till dagens interaktioner, inte andra faktorer.

**Upstream rationale:** Importance=high (är självbetjäning inte den primära orsaken rör lösningen inte utfallet); evidence=weak (endast en intervju stödjer orsakshypotesen).

**Recommended test: Customer interview**

> **Hypothesis:** We believe that avsaknad av självbetjäning är den primära orsaken till dagens kundinitierade interaktioner, så att omedelbar tillgång till credentials och guidad dokumentation minskar antalet interaktioner.
> **Test:** To verify that, we will intervjua 10 kunder som nyligen onboardats om varje gång de kontaktade Flowbase under aktiveringen. För varje kontakt frågar vi om omedelbar självbetjäning skulle ha tagit bort just den.
> **Metric:** And measure andelen rapporterade kontakter som kunderna bedömer skulle ha undvikits med omedelbar tillgång till credentials och guide.
> **Success criteria:** We are right if minst 70% av de rapporterade kontakterna bedöms ha kunnat undvikas med omedelbar självbetjäning.

**Cost:** low | **Time:** days | **Evidence:** moderate

**Why this test:** Default for desirability is Customer interview (used as-is.)

**Alternatives:**

- **Survey:** Om vi vill kvantifiera kontaktorsaker bland fler kunder än vi hinner intervjua.
- **A/B test (with existing traffic):** Om vi kan ge en grupp omedelbar självbetjäning och mäta faktisk kontaktfrekvens mot en kontrollgrupp.

## Solution 2: Interaktiv kom-igång-guide direkt efter avtalssignering

**sol-r1-ux-1** [UX, R1]

Kunden möts av en steg-för-steg-guide i portalen så fort avtalet är signerat - guiden leder dem från API-nyckel till första lyckade anrop i produktionsmiljö utan att behöva kontakta Flowbase. Varje steg bekräftas med direkt feedback (grönt bock = lyckat anrop) så att kunden vet exakt var de befinner sig i processen och vad som återstår.

**Test Cards in this solution (7):**

### asm-sol-r1-ux-1-004 [OI+PrM+SM] [usability] [high/weak]

**Assumption:** Guiden täcker de tekniska konfigurationssteg, miljöer, autentiseringsmetoder och programmeringsspråk som kunderna faktiskt använder, så att ingen fastnar på ett steg som guiden inte adresserar.

**Upstream rationale:** Importance=high (ett steg guiden inte adresserar gör att kunden fastnar och kontaktar Flowbase); evidence=weak (att guiden täcker alla språk, miljöer och autentiseringsmetoder är obevisat).

**Recommended test: Paper or click-through prototype**

> **Hypothesis:** We believe that guiden kan täcka de konfigurationssteg, miljöer, autentiseringsmetoder och programmeringsspråk som kunderna faktiskt använder, så att ingen fastnar på ett steg guiden inte adresserar.
> **Test:** To verify that, we will testa en klickbar prototyp av guiden med 8 kunder som representerar olika stackar och autentiseringsmetoder. Varje deltagare försöker nå ett lyckat anrop medan vi loggar varje steg guiden inte täcker.
> **Metric:** And measure antalet unika steg eller miljöer där minst en deltagare fastnar för att guiden inte adresserar dem.
> **Success criteria:** We are right if högst 2 oadresserade blockeringssteg upptäcks över alla 8 deltagare.

**Cost:** low | **Time:** days | **Evidence:** moderate

**Why this test:** Default for usability is Paper or click-through prototype (used as-is.)

**Alternatives:**

- **Customer interview:** Om vi först vill kartlägga vilka språk och miljöer kundbasen faktiskt använder.
- **Concierge:** Om vi vill live-stötta kunder genom integrationen för att hitta täckningsluckor i verkligheten.

---

### asm-sol-r1-ux-1-005 [SM] [feasibility] [high/weak]

**Assumption:** Portalen kan detektera om ett anrop mot produktionsmiljön lyckades och ge kunden omedelbar, korrekt feedback per steg utan fördröjning.

**Upstream rationale:** Importance=high (utan korrekt feedback per steg uteblir lösningens kärndifferentiator); evidence=weak (realtidsdetektering av kundens produktionsanrop per steg är tekniskt oprövat).

**Recommended test: Technical spike or proof-of-concept**

> **Hypothesis:** We believe that portalen tekniskt kan detektera om ett anrop mot produktionsmiljön lyckades och ge korrekt feedback per steg utan fördröjning.
> **Test:** To verify that, we will implementera en minimal detektor som registrerar en kunds produktionsanrop och returnerar lyckat eller misslyckat per steg. Vi testar den mot en serie simulerade och verkliga anrop.
> **Metric:** And measure andelen anrop där detektorn ger korrekt status inom acceptabel fördröjning.
> **Success criteria:** We are right if detektorn ger korrekt status för minst 95% av anropen inom 5 sekunder.

**Cost:** medium | **Time:** days | **Evidence:** strong

**Why this test:** Default for feasibility is Technical spike or proof-of-concept (used as-is.)

**Alternatives:**

- **Wizard of Oz:** Om vi vill testa värdet av feedbacken genom att manuellt verifiera anrop bakom kulisserna innan automatik byggs.
- **A/B test (with existing traffic):** Om vi vill jämföra kontaktfrekvens med och utan feedback när detektorn väl finns.

---

### asm-sol-r1-ux-1-008 [OI+PrM] [usability] [high/weak]

**Assumption:** Den direkta feedbacken per steg (t.ex. grönt bock) är tillräckligt tydlig för att kunden ska förstå om ett anrop lyckades eller om felet ligger i deras egen integration, och inte initiera kontakt med Flowbase för verifiering.

**Upstream rationale:** Importance=high (oklar feedback utlöser verifieringskontakter som ska elimineras); evidence=weak (att feedbacken särskiljer lyckat anrop från eget integrationsfel är spekulativt).

**Recommended test: Paper or click-through prototype**

> **Hypothesis:** We believe that den direkta feedbacken per steg är tillräckligt tydlig för att kunden ska förstå om ett anrop lyckades eller om felet ligger i deras egen integration, utan att kontakta Flowbase.
> **Test:** To verify that, we will testa en klickbar prototyp med feedback per steg med 8 kunder, i scenarier med både lyckade anrop och avsiktligt felande integrationer. Vi observerar om de tolkar feedbacken rätt och om de skulle vilja kontakta support.
> **Metric:** And measure andelen scenarier där deltagaren korrekt avgör om felet ligger hos dem själva eller hos Flowbase.
> **Success criteria:** We are right if minst 7 av 8 deltagare tolkar feedbacken korrekt utan att vilja kontakta Flowbase för verifiering.

**Cost:** low | **Time:** days | **Evidence:** moderate

**Why this test:** Default for usability is Paper or click-through prototype (used as-is.)

**Alternatives:**

- **Card sort or 5-second test:** Om vi snabbt vill testa om grönt-bock-tillståndet uppfattas som klart.
- **Concierge:** Om vi vill observera riktiga kunder tolka feedbacken live under aktivering.

---

### asm-sol-r1-ux-1-009 [PrM] [desirability] [high/weak]

**Assumption:** Kunderna väljer att följa guiden i stället för att falla tillbaka på gamla kontaktmönster när de stöter på motstånd.

**Upstream rationale:** Importance=high (faller kunden tillbaka på gamla kontaktmönster bryts utfallet); evidence=weak (att kunder väljer guiden framför invant kontaktbeteende är ett oprövat beteendeantagande).

**Recommended test: Concierge**

> **Hypothesis:** We believe that kunderna väljer att följa guiden i stället för att falla tillbaka på gamla kontaktmönster när de stöter på motstånd.
> **Test:** To verify that, we will erbjuda guiden till 8 nya kunder och observera, utan att proaktivt ingripa, om de fortsätter i guiden eller initierar kontakt med Flowbase när de stöter på ett hinder.
> **Metric:** And measure andelen kunder som fortsätter i guiden vid första hindret i stället för att kontakta Flowbase.
> **Success criteria:** We are right if minst 6 av 8 kunder fortsätter i guiden vid första hindret utan att kontakta Flowbase.

**Cost:** medium | **Time:** days | **Evidence:** strong

**Why this test:** Default for desirability is Customer interview, but Concierge fits because det här är ett beteendeantagande där faktiskt agerande vid motstånd väger tyngre än vad kunder säger i en intervju.

**Alternatives:**

- **A/B test (with existing traffic):** Om vi vill jämföra kontaktfrekvens mellan en guide-kohort och en kontrollgrupp.
- **Customer interview:** Om vi vill förstå varför kunder föll tillbaka på kontakt när de gjorde det.

---

### asm-sol-r1-ux-1-010 [PrM] [viability] [high/weak]

**Assumption:** Flowbase kan hålla guiden uppdaterad i takt med förändringar i API:et, så att steg-för-steg-instruktionerna inte leder kunden fel vid nästa release.

**Upstream rationale:** Importance=high (en inaktuell guide leder kunden fel och utlöser kontakt); evidence=weak (att Flowbase orkar hålla guiden synkad med varje release är obevisat).

**Recommended test: Technical spike or proof-of-concept**

> **Hypothesis:** We believe that Flowbase kan hålla guiden uppdaterad i takt med förändringar i API:et, så att instruktionerna inte leder kunden fel vid nästa release.
> **Test:** To verify that, we will gå igenom de senaste 5 API-releaserna och mäta hur mycket guideuppdatering var och en hade krävt. Vi kontrollerar också om en innehavare och rutin finns för att hinna med innan release.
> **Metric:** And measure andelen senaste releaser som hade kunnat speglas i guiden före release med nuvarande bemanning och rutin.
> **Success criteria:** We are right if minst 4 av de 5 senaste releaserna hade kunnat reflekteras i guiden före release.

**Cost:** low | **Time:** days | **Evidence:** moderate

**Why this test:** Default for viability is Landing page with sign-up, but Technical spike or proof-of-concept fits because antagandet gäller intern förmåga att underhålla guiden över tid, inte marknadsefterfrågan.

**Alternatives:**

- **Customer interview:** Om vi vill fråga kunder hur ofta inaktuell dokumentation har lett dem fel.
- **Concierge:** Om vi vill köra en release med manuell guideuppdatering och mäta faktisk ledtid.

---

### asm-sol-r1-ux-1-012 [OI] [usability] [high/weak]

**Assumption:** En steg-för-steg-guide i portalen räcker som enda informationskälla - kunden behöver inte komplettera med extern dokumentation, support eller kollegors hjälp för att ta sig från API-nyckel till första lyckade anrop.

**Upstream rationale:** Importance=high (räcker inte guiden ensam söker kunden extern hjälp eller support); evidence=weak (att en enda guide ersätter all annan informationskälla är obevisat).

**Recommended test: Paper or click-through prototype**

> **Hypothesis:** We believe that en steg-för-steg-guide i portalen räcker som enda informationskälla för att kunden ska ta sig från API-nyckel till första lyckade anrop, utan extern dokumentation, support eller kollegor.
> **Test:** To verify that, we will köra en modererad prototyptest där 8 kunder får använda enbart guiden för att nå ett lyckat anrop, utan extern dokumentation eller support. Vi noterar varje gång de försöker söka information utanför guiden.
> **Metric:** And measure andelen deltagare som når ett lyckat anrop med enbart guiden, samt antalet försök att söka extern hjälp.
> **Success criteria:** We are right if minst 6 av 8 deltagare når ett lyckat anrop utan att söka information utanför guiden.

**Cost:** low | **Time:** days | **Evidence:** moderate

**Why this test:** Default for usability is Paper or click-through prototype (used as-is.)

**Alternatives:**

- **Concierge:** Om vi vill observera riktiga kunder under aktivering och räkna externa hjälpsökningar.
- **Customer interview:** Om vi vill kartlägga vilka externa källor kunder idag förlitar sig på.

---

### asm-sol-r1-ux-1-013 [OI] [desirability] [high/weak]

**Assumption:** De vanligaste skälen till att kunder kontaktar Flowbase under aktivering är informationsbrist och osäkerhet om nästa steg - inte tekniska blockerare som kräver mänsklig hjälp från Flowbase.

**Upstream rationale:** Importance=high (är orsaken tekniska blockerare rör en informationsguide inte utfallet); evidence=weak (endast en intervju stödjer orsakshypotesen).

**Recommended test: Customer interview**

> **Hypothesis:** We believe that de vanligaste skälen till att kunder kontaktar Flowbase under aktivering är informationsbrist och osäkerhet om nästa steg, inte tekniska blockerare som kräver mänsklig hjälp.
> **Test:** To verify that, we will intervjua 10 kunder och gå igenom kontakthistoriken, och klassificera varje kontakt under aktivering som informationsrelaterad eller teknisk blockerare.
> **Metric:** And measure andelen kontakter som klassificeras som informationsbrist eller osäkerhet snarare än tekniska blockerare.
> **Success criteria:** We are right if minst 60% av de klassificerade kontakterna beror på informationsbrist snarare än tekniska blockerare.

**Cost:** low | **Time:** days | **Evidence:** moderate

**Why this test:** Default for desirability is Customer interview (used as-is.)

**Alternatives:**

- **Survey:** Om vi vill klassificera kontaktorsaker brett över fler kunder.
- **A/B test (with existing traffic):** Om vi vill mäta om en informationsguide faktiskt sänker kontaktfrekvensen mot kontroll.

## Solution 3: Automatisk välkomstpåse med konfigurerade kodexempel för kundens miljö

**sol-r1-ux-2** [UX, R1]

Direkt vid aktivering skickas ett personaliserat paket - med API-nyckel, bas-URL och färdiga kodexempel i de vanligaste språken (Python, JavaScript, cURL) - där variablerna redan är ifyllda med kundens faktiska uppgifter. Kunden kopierar och kör, inget att konfigurera eller slå upp, vilket eliminerar det vanligaste skälet till att höra av sig till Flowbase under onboarding.

**Test Cards in this solution (9):**

### asm-sol-r1-ux-2-001 [OI+SM] [feasibility] [high/weak]

**Assumption:** Flowbases system känner till exakt när en kund aktiveras och kan automatiskt trigga utskicket av välkomstpåsen utan manuellt steg, och levererar uppgifterna snabbt nog för att välkomstpåsen ska skickas i rätt tid i förhållande till när kunden är redo att testa.

**Upstream rationale:** Importance=high (uteblir automatiskt och rättidigt utskick återinförs manuell hantering); evidence=weak (att systemet skickar i rätt tid relativt kundens faktiska redo-läge är oprövat).

**Recommended test: Technical spike or proof-of-concept**

> **Hypothesis:** We believe that Flowbases system kan känna till exakt när en kund aktiveras och automatiskt trigga utskicket av välkomstpåsen i rätt tid i förhållande till när kunden är redo att testa.
> **Test:** To verify that, we will koppla en lyssnare till aktiveringshändelsen och trigga ett testutskick. Vi mäter om händelsen fångas tillförlitligt och hur lång tid det tar från aktivering till utskick.
> **Metric:** And measure andelen aktiveringar som korrekt triggar ett utskick, och fördröjningen från aktivering till utskick.
> **Success criteria:** We are right if minst 95% av aktiveringarna triggar ett korrekt utskick inom 10 minuter.

**Cost:** low | **Time:** days | **Evidence:** strong

**Why this test:** Default for feasibility is Technical spike or proof-of-concept (used as-is.)

**Alternatives:**

- **Wizard of Oz:** Om vi vill skicka påsen manuellt vid aktivering för att testa värdet innan automatiken byggs.
- **Concierge:** Om vi vill följa några aktiveringar manuellt för att fastställa rätt tidpunkt relativt kundens readiness.

---

### asm-sol-r1-ux-2-002 [PrM+SM] [feasibility] [high/weak]

**Assumption:** Alla uppgifter som behövs för att personalisera paketet - API-nyckel, bas-URL och kundens föredragna programmeringsspråk - finns tillgängliga i Flowbases system vid aktiveringstillfället, och är korrekta och giltiga när kunden faktiskt försöker använda dem.

**Upstream rationale:** Importance=high (saknas eller felar persondatan blir paketet obrukbart och kontakt uppstår); evidence=weak (kundens föredragna programmeringsspråk finns sällan i Flowbases system).

**Recommended test: Technical spike or proof-of-concept**

> **Hypothesis:** We believe that alla uppgifter som behövs för att personalisera paketet - API-nyckel, bas-URL och kundens föredragna programmeringsspråk - finns tillgängliga, korrekta och giltiga i Flowbases system vid aktiveringstillfället.
> **Test:** To verify that, we will granska de senaste 30 aktiverade kunderna och kontrollera om varje datafält fanns, var korrekt och pekade mot rätt miljö vid aktiveringen.
> **Metric:** And measure andelen kunder där samtliga personaliseringsfält fanns och var korrekta vid aktivering.
> **Success criteria:** We are right if samtliga fält fanns och var korrekta för minst 90% av de 30 granskade kunderna.

**Cost:** low | **Time:** days | **Evidence:** strong

**Why this test:** Default for feasibility is Technical spike or proof-of-concept (used as-is.)

**Alternatives:**

- **Customer interview:** Om vi vill se om kundens föredragna språk ens kan härledas genom att fråga vilket de använder.
- **Concierge:** Om vi vill sätta ihop paket manuellt för några kunder och se vilka fält som saknas.

---

### asm-sol-r1-ux-2-003 [SM] [usability] [high/weak]

**Assumption:** Välkomstpåsen når rätt teknisk kontaktperson hos kunden i rätt tid, och hamnar inte hos en icke-teknisk mottagare eller i ett spamfilter.

**Upstream rationale:** Importance=high (når paketet fel mottagare eller spam agerar ingen och kontakt uppstår); evidence=weak (att B2B-utskick når rätt teknisk kontakt och undviker spamfilter är osäkert).

**Recommended test: Concierge**

> **Hypothesis:** We believe that välkomstpåsen når rätt teknisk kontaktperson hos kunden i rätt tid och inte hamnar hos en icke-teknisk mottagare eller i ett spamfilter.
> **Test:** To verify that, we will manuellt skicka en välkomstpåse till de kontaktuppgifter Flowbase har för 10 nyligen aktiverade kunder och följa upp om den nådde rätt teknisk person, öppnades och inte fastnade i spam.
> **Metric:** And measure andelen utskick som nådde och öppnades av den person som faktiskt utför integrationen.
> **Success criteria:** We are right if minst 7 av 10 utskick nådde och öppnades av rätt teknisk person.

**Cost:** low | **Time:** days | **Evidence:** moderate

**Why this test:** Default for usability is Paper or click-through prototype, but Concierge fits because antagandet gäller om utskicket faktiskt levereras till rätt person, inte hur ett gränssnitt används.

**Alternatives:**

- **Customer interview:** Om vi vill fråga nyligen onboardade kunder vem som fick onboarding-mejlen och om de hamnade i skräpposten.
- **Survey:** Om vi vill kartlägga vilken kontakt kunder anger som teknisk innehavare.

---

### asm-sol-r1-ux-2-004 [PrM] [usability] [high/weak]

**Assumption:** Mottagaren av välkomstpåsen är samma person som utför den tekniska integrationen - paketet hamnar hos den som faktiskt ska använda kodexemplen, inte bara hos den som skrivit under avtalet.

**Upstream rationale:** Importance=high (hamnar paketet inte hos integratören används kodexemplen aldrig); evidence=weak (att mottagaren är samma person som integrerar är ett oprövat organisationsantagande).

**Recommended test: Customer interview**

> **Hypothesis:** We believe that mottagaren av välkomstpåsen är samma person som utför den tekniska integrationen, inte bara den som skrivit under avtalet.
> **Test:** To verify that, we will intervjua 8 nyligen onboardade kunder om vem som tog emot onboarding-materialet och vem som faktiskt utförde integrationen.
> **Metric:** And measure andelen kunder där mottagaren av materialet var samma person som utförde integrationen.
> **Success criteria:** We are right if mottagaren var integratören i minst 6 av 8 fall.

**Cost:** low | **Time:** days | **Evidence:** moderate

**Why this test:** Default for usability is Paper or click-through prototype, but Customer interview fits because antagandet gäller kundens interna rollfördelning, inte gränssnittets användbarhet.

**Alternatives:**

- **Survey:** Om vi vill kartlägga bredare vem som äger integrationen hos kunderna.
- **Concierge:** Om vi vill följa utskick till mottagare och se vem som faktiskt agerar.

---

### asm-sol-r1-ux-2-005 [OI+PrM] [desirability] [high/weak]

**Assumption:** Kunden läser och agerar på välkomstpåsen vid rätt tidpunkt i sin onboarding - paketet missas inte, arkiveras inte eller återfinns inte för sent.

**Upstream rationale:** Importance=high (missas eller arkiveras paketet kringgås hela mekanismen); evidence=weak (att ett pushat paket faktiskt konsumeras i rätt tid är ett spekulativt beteendeantagande).

**Recommended test: Concierge**

> **Hypothesis:** We believe that kunden läser och agerar på välkomstpåsen vid rätt tidpunkt i sin onboarding, så att paketet inte missas, arkiveras eller återfinns för sent.
> **Test:** To verify that, we will skicka välkomstpåsen till 10 nyaktiverade kunder och mäta, utan påminnelser, hur många som öppnar och gör ett första anrop inom en bestämd tidsperiod.
> **Metric:** And measure andelen mottagare som öppnar paketet och gör ett första anrop inom 7 dagar utan påminnelse.
> **Success criteria:** We are right if minst 6 av 10 mottagare gör ett första anrop inom 7 dagar utan påminnelse.

**Cost:** low | **Time:** days | **Evidence:** strong

**Why this test:** Default for desirability is Customer interview, but Concierge fits because faktiskt öppnande och agerande på ett pushat paket är ett beteende som mäts bättre än det utfrågas.

**Alternatives:**

- **A/B test (with existing traffic):** Om vi vill jämföra aktiveringsgrad mellan kunder som får påsen och en kontrollgrupp.
- **Customer interview:** Om vi vill förstå varför paket missas eller arkiveras.

---

### asm-sol-r1-ux-2-006 [OI+PrM+SM] [usability] [high/weak]

**Assumption:** Kodexemplen täcker det programmeringsspråk eller det tekniska format som kundens utvecklare faktiskt använder, och de vanligaste språken Python, JavaScript och cURL räcker för att täcka merparten av fallen - kunder med andra stackar utgör inte en tillräckligt stor grupp för att ge upphov till supportkontakter.

**Upstream rationale:** Importance=high (saknas kundens språk fastnar utvecklaren och kontaktar Flowbase); evidence=weak (att Python, JavaScript och cURL täcker merparten av kundernas stackar är obevisat).

**Recommended test: Survey**

> **Hypothesis:** We believe that de vanligaste språken Python, JavaScript och cURL täcker det programmeringsspråk eller format som merparten av kundernas utvecklare faktiskt använder.
> **Test:** To verify that, we will skicka en kort enkät till den aktiva kundbasens tekniska kontakter och fråga vilket språk eller format de använder för att konsumera API:et.
> **Metric:** And measure andelen svarande vars språk eller format täcks av Python, JavaScript eller cURL.
> **Success criteria:** We are right if minst 80% av de svarande täcks av Python, JavaScript eller cURL.

**Cost:** low | **Time:** days | **Evidence:** moderate

**Why this test:** Default for usability is Paper or click-through prototype, but Survey fits because antagandet gäller vilken språkfördelning kundbasen har, vilket är en faktafråga som besvaras billigast brett.

**Alternatives:**

- **Technical spike or proof-of-concept:** Om vi vill analysera API-loggar och User-Agent-data för att se vilka klienter och språk som faktiskt anropar.
- **Customer interview:** Om vi vill förstå stackar djupare hos segment som faller utanför de tre språken.

---

### asm-sol-r1-ux-2-007 [OI+SM] [feasibility] [high/weak]

**Assumption:** De förifyllda credentials och kodexemplen är syntaktiskt korrekta, körbara utan att kunden behöver ändra något, och pekar mot rätt miljö så att ett lyckat testanrop bekräftar att integrationen är klar.

**Upstream rationale:** Importance=high (felaktiga eller icke-körbara exempel utlöser direkt kontakt); evidence=weak (per-kund-genererad, körbar och rätt-riktad kod utan ändring är tekniskt oprövat).

**Recommended test: Technical spike or proof-of-concept**

> **Hypothesis:** We believe that de förifyllda credentials och kodexemplen är syntaktiskt korrekta, körbara utan ändring och pekar mot rätt miljö, så att ett lyckat testanrop bekräftar att integrationen är klar.
> **Test:** To verify that, we will generera personaliserade paket för 10 testkunder och köra varje kodexempel som det är, i varje språk, mot rätt miljö. Vi loggar om det exekverar utan ändring och ger ett lyckat svar.
> **Metric:** And measure andelen genererade kodexempel som körs utan ändring och returnerar ett lyckat anrop.
> **Success criteria:** We are right if minst 95% av de genererade kodexemplen körs utan ändring och returnerar ett lyckat anrop.

**Cost:** low | **Time:** days | **Evidence:** strong

**Why this test:** Default for feasibility is Technical spike or proof-of-concept (used as-is.)

**Alternatives:**

- **Concierge:** Om vi vill låta riktiga kunder köra de genererade exemplen och observera fel.
- **A/B test (with existing traffic):** Om vi vill jämföra andel lyckade förstaanrop med och utan förifyllda exempel.

---

### asm-sol-r1-ux-2-009 [OI] [desirability] [high/weak]

**Assumption:** Kunder som får API-nyckel, bas-URL och färdiga kodexempel direkt vid aktivering kan genomföra sitt första anrop utan att behöva kontakta Flowbase för att få fram dessa uppgifter.

**Upstream rationale:** Importance=high (krävs ändå kontakt för att få fram uppgifterna rör lösningen inte utfallet); evidence=weak (att färdiga credentials och kodexempel tar bort kontaktbehovet är obevisat).

**Recommended test: Concierge**

> **Hypothesis:** We believe that kunder som får API-nyckel, bas-URL och färdiga kodexempel direkt vid aktivering kan genomföra sitt första anrop utan att kontakta Flowbase för att få fram dessa uppgifter.
> **Test:** To verify that, we will ge 10 nyaktiverade kunder ett färdigt välkomstpaket och mäta hur många som når ett första lyckat anrop utan att kontakta Flowbase för credentials eller konfigurationsuppgifter.
> **Metric:** And measure andelen kunder som når ett första lyckat anrop utan att kontakta Flowbase för uppgifterna.
> **Success criteria:** We are right if minst 8 av 10 kunder når ett första lyckat anrop utan att kontakta Flowbase för uppgifterna.

**Cost:** low | **Time:** days | **Evidence:** strong

**Why this test:** Default for desirability is Customer interview, but Concierge fits because effekten på faktisk kontaktfrekvens mäts bättre genom verkligt beteende än genom utfrågning.

**Alternatives:**

- **A/B test (with existing traffic):** Om vi vill jämföra kontaktfrekvens mellan paket-kohort och kontrollgrupp i befintligt flöde.
- **Customer interview:** Om vi vill förstå kvarvarande skäl till kontakt trots materialet.

---

### asm-sol-r1-ux-2-010 [OI+PrM] [desirability] [high/weak]

**Assumption:** Konfigurationsförvirring kring credentials och bas-URL är den primära anledningen till att kunder kontaktar Flowbase under aktivering - inte frågor om datakvalitet, dataformat, licensvillkor eller andra tekniska hinder.

**Upstream rationale:** Importance=high (är orsaken något annat än konfigurationsförvirring rör lösningen inte utfallet); evidence=weak (endast partiellt intervjustöd för orsakshypotesen).

**Recommended test: Customer interview**

> **Hypothesis:** We believe that konfigurationsförvirring kring credentials och bas-URL är den primära anledningen till att kunder kontaktar Flowbase under aktivering, inte datakvalitet, dataformat, licensvillkor eller andra tekniska hinder.
> **Test:** To verify that, we will intervjua 10 kunder och gå igenom kontakthistoriken, och klassificera varje aktiveringskontakt som konfigurationsförvirring eller annan orsak.
> **Metric:** And measure andelen kontakter som beror på konfigurationsförvirring kring credentials eller bas-URL.
> **Success criteria:** We are right if minst 50% av de klassificerade kontakterna beror på konfigurationsförvirring kring credentials eller bas-URL.

**Cost:** low | **Time:** days | **Evidence:** moderate

**Why this test:** Default for desirability is Customer interview (used as-is.)

**Alternatives:**

- **Survey:** Om vi vill kvantifiera kontaktorsaker brett över fler kunder.
- **Technical spike or proof-of-concept:** Om vi vill analysera supportärenden och loggar för att kategorisera orsaker.
