---
title: Extraherade opportunity-kandidater — Team Aurora Våg 1
date: 2026-05-26
team: Aurora
purpose: Extracted opportunity candidates from interview transcripts for this opportunity-selection round
source_transcripts:
  - transcripts/intervju-1-aurora-apr-08.md
  - transcripts/intervju-2-aurora-apr-09.md
  - transcripts/intervju-3-aurora-apr-13.md
  - transcripts/intervju-4-aurora-apr-13.md
based_on_outcome: "Öka andelen nya kunder som på egen hand når sitt första lyckade produktionsanrop mot API:et utan att kontakta Flowbase, från 40% till 80% inom 60 dagar från avtalstecknande."
tags: [aurora, discovery, opportunities, extraction]
---

# Extraherade opportunity-kandidater

## Metadata

| | Intervju 1 (Anders) | Intervju 2 (Niklas) | Intervju 3 (Lina) | Intervju 4 (David) | **Totalt** |
|---|---|---|---|---|---|
| Klar opportunity | 4 | 5 | 12 | 10 | **31** |
| Möjlig opportunity | 3 | 2 | 2 | 4 | **11** |
| Lösning förklädd | 0 | 1 | 0 | 1 | **2** |
| **Summa** | **7** | **8** | **14** | **15** | **44** |

**Antal transkript lästa:** 4

**Noteringar:**

- **Intervju 1 (Anders)** — Lågt antal kandidater (7). Anders är intern utvecklare och upplever minimal friktion eftersom han litar på organisationen och har insiderskunskap. Hans perspektiv belyser systemiska problem (domänkunskap, verifiering) snarare än onboarding-friktion. Trion bör väga detta: hans erfarenhet är inte analog med en extern kunds.
- **Intervju 2 (Niklas)** — Transkriptionskvaliteten är ojämn (Teams auto-transkription). Intervjun var primärt en arkitekturgenomgång, inte en kundintervju — Erik ställde inga frågor om kundresan. Opportunity-signalerna finns främst i Niklas beskrivningar av manuella processer och saknade funktioner. Niklas skickade även skriftliga reservationer efter intervjun om att skala SSO-integrationer (se post-intervju-reflektioner i transkript, rad 85-95) — dessa är inte extraherade som citat-stickies men bör läsas av trion.
- **Intervju 3 (Lina)** — Rikast på opportunities. Lina beskriver konkreta incidenter (specialfall-buggen, felaktiga behörigheter) och återkommande mönster (domänkunskap, gissningar, kunders upptäckt av fel).
- **Intervju 4 (David)** — Enda externa kunden. Mest direkt relevant för product outcome. David är dataanalytiker utan utvecklarbakgrund som byggde sin API-integration med ChatGPT. Hans perspektiv representerar troligen en växande kundprofil.
- **Intervjuarteknik-notering:** I intervju 1 och 4 accepterade intervjuarna ledande frågor som framkallade bekräftande svar snarare än berättelser. Några av David mer generella uttalanden kan vara färgade av Saras kontextsättning (t.ex. kring transaktionskostnad). Flaggas men extraheras ändå där underliggande signal finns.

---

### Intervju 1 — Anders Berg, intern utvecklare (Datarapport/Datahubben-integration)

[Klar opportunity]

> "Vi gjorde allt på eget. Ingen hjälp."
>
> Anders, intervju-1-aurora-apr-08, ~rad 45

[Klar opportunity]

> "Vi har väldigt mycket bra grejer på bra ställen, men vi har inte riktigt helheten. [...] Vi saknar förståelse mellan delarna ibland. [...] vi skulle jobba mer som en enhet, med en gemensam kraft. Tydligare möten mellan de olika delarna."
>
> Anders, intervju-1-aurora-apr-08, ~rad 107-109

[Klar opportunity]

> "Jag får ett 200-svar och kanske en fil, så det gick bra. Men jag har ingen aning om det är korrekt eller om det används rätt. Hur skulle jag kunna veta det?"
>
> Anders, intervju-1-aurora-apr-08, ~rad 133

[Klar opportunity]

> "Det är 'lowest of low'. Man tar sin egen datapost och säger att det stämmer ungefär."
>
> Anders, intervju-1-aurora-apr-08, ~rad 137

[Möjlig opportunity]

> "Vi utgick väldigt hårt från att bygga upp den själva [...] Sen förstod vi att det här kommer vi aldrig att få ordning på, så vi beslöt att ta det förpackat från Datahubben, vilket också finns som något man kan hämta."
>
> Anders, intervju-1-aurora-apr-08, ~rad 39

[Möjlig opportunity]

> "Att garantera kvaliteten på det man levererar är inte jättelätt. [...] Att hela tiden kvalitetssäkra och beskriva data. [...] Det kan vara längst bak i blocket, inga problem, men det ska finnas där."
>
> Anders, intervju-1-aurora-apr-08, ~rad 141

[Möjlig opportunity]

> "Jag tror att i team Fenix saknar de mycket av den här domänkunskapen. Inte att de saknar det på det sättet, utan att de verkligen saknar den och skulle vilja ha den närmare sig."
>
> Anders, intervju-1-aurora-apr-08, ~rad 181

---

### Intervju 2 — Niklas Klisics, arkitekt (API Gateway/Explorer)

[Klar opportunity]

> "det blir alltid det går alltid någon timme eller två och bara diskutera hur [man] för över den här [secret-]cykeln"
>
> Niklas, intervju-2-aurora-apr-09, ~rad 207

[Klar opportunity]

> "sen när vi väl ska byta så måste vi göra det i samförstånd med kunden så att dom vet att ingenting bara slutar fungera [...] det tar alltid några timmar och kan de bara göra det själv så är det mycket smidigare"
>
> Niklas, intervju-2-aurora-apr-09, ~rad 211

[Klar opportunity]

> "vi har ingen koppling idag mellan en [SSO-]integration och en licens utan vi [...] hårdkodade behörigheterna kopplat [till] integrationen"
>
> Niklas, intervju-2-aurora-apr-09, ~rad 251

[Klar opportunity]

> "sådan information som hur länge [...] deras klient[secret] är giltig[t]. Det är ingenting vi systematiskt kan extrahera, utan det är information vi får via teams eller telefon."
>
> Niklas, intervju-2-aurora-apr-09, ~rad 295

[Klar opportunity]

> "vi har ingen möjlighet att köra två samtidigt aktiva [secrets] så att byt över den, ja, men då kommer det sluta funka för dom om dom inte har satt upp det på sin sida"
>
> Niklas, intervju-2-aurora-apr-09, ~rad 187

[Möjlig opportunity]

> "jag har obstruerat lite grann mot att storskaligt gå ut och sälja [SSO-]integrationer just för att jag tycker inte att vi riktigt är redo för det"
>
> Niklas, intervju-2-aurora-apr-09, ~rad 239

[Möjlig opportunity]

> "[Självservice-]endpointsen är inte skapade [...] Det finns i någon [...] epic eller nåt sånt [...] men det är inte implementerat"
>
> Niklas, intervju-2-aurora-apr-09, ~rad 159

[Lösning förklädd]

> "det bästa hade varit ifall [...] dom hade kunnat peka ut ja, men det här attributet eller den här grupptillhörigheten och så kopplar det till en licens [...] i självservice-gränssnittet"
>
> Niklas, intervju-2-aurora-apr-09, ~rad 271-275

---

### Intervju 3 — Lina Falk, arkitekt (Team Comet/Markhåll, Datahubben-integration)

[Klar opportunity]

> "det blev ofta fel när vi lade upp nya kunder — de fick inte alla behörigheter de behövde, vilket ledde till en hel del fram-och-tillbaka innan en kund var igång."
>
> Lina, intervju-3-aurora-apr-13, ~rad 42

[Klar opportunity]

> "vi använder fortfarande gemensamma användare — vilket innebär att vi inte kan använda vissa funktioner i Datahubben, till exempel caching."
>
> Lina, intervju-3-aurora-apr-13, ~rad 44

[Klar opportunity]

> "Det hade dock varit bättre om allt samlades på ett ställe och det var tydligare hur man hittar det."
>
> Lina, intervju-3-aurora-apr-13, ~rad 98

[Klar opportunity]

> "En sak som har varit lite knölig är att det finns tre olika sätt att logga in i Swagger, och man måste veta vilket man ska använda beroende på om det är det gamla eller det nya sättet."
>
> Lina, intervju-3-aurora-apr-13, ~rad 102

[Klar opportunity]

> "det har egentligen inte med API:et eller den tekniska integrationen att göra, utan med kunskapen om själva informationen man får. Där finns fortfarande ett glapp. Vi har ingen riktig domänexpert på data från Datakällan — åtminstone inte någon vi pratar med."
>
> Lina, intervju-3-aurora-apr-13, ~rad 108

[Klar opportunity]

> "Det verkar inte vara allmänt känt vare sig hos Team Fenix eller hos oss i Team Comet. [...] det dök upp ett specialfall som ingen kände till. Det kanske finns en domänexpert på Flowbase, men vi har i alla fall inte kontakt med den personen."
>
> Lina, intervju-3-aurora-apr-13, ~rad 113

[Klar opportunity]

> "Vi var tvungna att ta beslut och gissa utifrån det vi kunde analysera fram, utan att kunna bekräfta att vi hade rätt. Vi kunde inte riktigt verifiera slutsatserna."
>
> Lina, intervju-3-aurora-apr-13, ~rad 116

[Klar opportunity]

> "Vi håller tummarna, kan man säga. Tyvvärr är det så att när vi saknar en expert på informationen måste vi gå på den samlade kunskapen vi har i Team Comet och Team Fenix och hoppas att vi kommit fram till rätt slutsatser."
>
> Lina, intervju-3-aurora-apr-13, ~rad 120

[Klar opportunity]

> "Vi har missuppfattat saker eller missat att en viss typ av objekt finns, bara för att den förekommer väldigt sällan. Det har resulterat i buggar som drabbat både teamet och kunder, och vi har fått göra snabba fixar."
>
> Lina, intervju-3-aurora-apr-13, ~rad 124

[Klar opportunity]

> "Det som bekymrar mig är när till och med Team Fenix säger att de inte har en expert på den bakomliggande domänen — på själva informationen. Det är en otroligt viktig del, både för oss och för våra kunder."
>
> Lina, intervju-3-aurora-apr-13, ~rad 128

[Klar opportunity]

> "vi har ingen direkt övervakning på att integrationen fungerar. Det är en brist. Tyvvärr är det i dag så att kunder ibland är de som upptäcker att något inte fungerar."
>
> Lina, intervju-3-aurora-apr-13, ~rad 154

[Klar opportunity]

> "vi kan skylla på Datakällan hur mycket som helst, men det hjälper inte kunden."
>
> Lina, intervju-3-aurora-apr-13, ~rad 158

[Möjlig opportunity]

> "för samrådskrets-paketet är det så otroligt mycket i svaret att det inte är möjligt att läsa igenom en specifikation — vi har fått göra mer analys av resultatet och byggt ut stegvis beroende på vad vi behöver."
>
> Lina, intervju-3-aurora-apr-13, ~rad 196

[Möjlig opportunity]

> "vi insåg att en specialfall kan vara registrerad som innehavare till en datapost — något Datakällan ibland gjort för att det var enklast. Det var ingenting som var specificerat någonstans [...] En kund råkade ut för det, det hindrade dem i deras arbete, och det fick oss att se sämre ut. Förtroendet tappades lite."
>
> Lina, intervju-3-aurora-apr-13, ~rad 206

---

### Intervju 4 — David Sörensen, dataanalytiker på Forum (extern kund)

[Klar opportunity]

> "egentligen jobbar jag som dataanalytiker - det här är ett intresse. Jag har ingen bakgrund alls i det egentligen, utan tycker bara att det är lite kul och är trött på att manuellt mata in data."
>
> David, intervju-4-aurora-apr-13, ~rad 27

[Klar opportunity]

> "Tidigare har vi manuellt skrivit av mycket: skrivit in adress, volym, innehavare. Man la datavyn på ena sidan och rapporten på den andra."
>
> David, intervju-4-aurora-apr-13, ~rad 35

[Klar opportunity]

> "det är väl att man egentligen inte vet vad man gör - så det är lite säkerhetsfrågor och sånt som kan vara jobbigt"
>
> David, intervju-4-aurora-apr-13, ~rad 58

[Klar opportunity]

> "jag har inte haft någon guide eller information, och ni har ju också sagt att ni inte jobbar med att hjälpa till att implementera - det får kunden göra själv"
>
> David, intervju-4-aurora-apr-13, ~rad 58

[Klar opportunity]

> "Det hade varit lättare att komma igång om det fanns någon typ av liten säljande startsida för vad man kan använda API:et till."
>
> David, intervju-4-aurora-apr-13, ~rad 60

[Klar opportunity]

> "API:et [är] skrivet för folk som vet vad API är - för dem är det inga konstigheter. Men vi som inte visste fick det att ta längre tid att leta sig fram än vad det hade behövt göra."
>
> David, intervju-4-aurora-apr-13, ~rad 61

[Klar opportunity]

> "Transaktionskostnaden upplevs som dyr - har alltid gjort det."
>
> David, intervju-4-aurora-apr-13, ~rad 82

[Klar opportunity]

> "Min enda önskan är kostnadsbudget. Jag tyckte det var synd att jag inte kunde sätta ett tak på våra anrop - om någon av min amatörkod fastnar i en loop. [...] det är en systemrisk - antingen att någon använder programmet fel eller att någonting buggar och det jobbas upp ganska höga kostnader."
>
> David, intervju-4-aurora-apr-13, ~rad 96

[Klar opportunity]

> "Det hade bara varit skönt att ha ett kostnadstak helt enkelt för att sova gott."
>
> David, intervju-4-aurora-apr-13, ~rad 104

[Klar opportunity]

> "[Hur tar ni del av nyheter i API:erna?] Inte alls, liksom. Om det kanske mejlas till mig [...] Kommer det något så hade jag nog läst det, men annars inte."
>
> David, intervju-4-aurora-apr-13, ~rad 110

[Möjlig opportunity]

> "Jag frågade Robin Sandell - egentligen bara kundtjänst - om det var möjligt att hämta datan via API [...] Och då skickade han de här XML-strängarna som innehåller all data."
>
> David, intervju-4-aurora-apr-13, ~rad 42

[Möjlig opportunity]

> "Jag tyckte det var lite jobbigt att be om förlängning [av testmiljön] och sånt [...] Jag var osäker på om Flowbase hade någon kostnad [...] jag som inte jobbar med sånt här funderade lite: 'kostar jag Flowbase en massa pengar nu?'"
>
> David, intervju-4-aurora-apr-13, ~rad 138-142

[Möjlig opportunity]

> "Till exempel innehavare - det finns ju registrerad innehavare och bekräftad innehavare. Det var en sån sak där [AI:n] tog fel [...] Samma sak med totala area och nettoarea - då behöver man fundera på vilken det är man vill ha."
>
> David, intervju-4-aurora-apr-13, ~rad 168-169

[Möjlig opportunity]

> "Jag har skrivit allt med AI. ChatGPT är min bästa vän. [...] Man har inte behövt någon bakgrund alls i kodskrivning."
>
> David, intervju-4-aurora-apr-13, ~rad 46-52

[Lösning förklädd]

> "Det enda jag saknar är nog bara en säljsida för API:et och hur man kommer igång. Det ska stå någonting i stil med 'vill du hämta data via kod istället? Så här kommer du igång med API:et'. Om ni tittar till exempel på Stripe med sina utvecklarguider - där finns en bra säljsida"
>
> David, intervju-4-aurora-apr-13, ~rad 172-173
