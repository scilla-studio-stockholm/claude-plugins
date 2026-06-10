---
title: Intervju 4 med David om självserviceaktivering av Flowbase-API:et
date: 2026-04-13
purpose: Syntetisk discovery-intervju med en extern API-licenskund som kom igång på egen hand. Underlag för team Auroras discovery i våg 1. ALLT INNEHÅLL ÄR PÅHITTAT (se ../README.md).
participants:
  - Maja (intervjuare)
  - Erik (intervjuare)
  - Sara (observatör, team Aurora)
  - David (intervjuperson, extern kund)
tags:
  - aurora
  - discovery
  - intervju
  - aktivering
  - sjalvservice
---

# Intervju 4 — Aurora, 13 april 2026

## Inledning och kontextsättning

**Maja:** Tack för att du tog dig tid, David. Vi tittar på hur nya kunder kommer igång med vårt API, från att avtalet är påskrivet till första lyckade anropet i produktion. Du gjorde ju den resan ganska nyligen.

**David:** Ja, precis. Säg bara till om jag spårar ur, jag är ingen expert.

**Erik:** Det är precis din upplevelse vi är ute efter. Kan du börja med att berätta vad du använder API:et till?

**David:** Egentligen jobbar jag som dataanalytiker — det här är ett intresse. Jag har ingen bakgrund alls i det egentligen, utan tycker bara att det är lite kul och är trött på att manuellt mata in data.

**Maja:** Hur gjorde ni tidigare, innan API:et?

**David:** Tidigare har vi manuellt skrivit av mycket: skrivit in fält för fält, kopierat mellan system. Man la datavyn på ena sidan och rapporten på den andra. Det var hopplöst i längden.

## Att komma igång

**Erik:** Ta mig till första gången du skulle använda API:et. Vad hände?

**David:** Jag fick inloggningsuppgifter och en länk, och sen var det lite "kör hårt". Det är väl att man egentligen inte vet vad man gör — så det är lite säkerhetsfrågor och sånt som kan vara jobbigt. Var lägger jag nyckeln, hur vet jag att den funkar, sånt.

**Maja:** Fanns det något stöd när du fastnade?

**David:** Nej, inte direkt. Ärligt talat — jag har inte haft någon guide eller information, och ni har ju också sagt att ni inte jobbar med att hjälpa till att implementera — det får kunden göra själv. Så jag fick treva mig fram.

**Erik:** Vad hade hjälpt dig allra mest där i början?

**David:** Det hade varit lättare att komma igång om det fanns någon typ av liten säljande startsida för vad man kan använda API:et till. Något som möter en på ens egen nivå.

**Maja:** Du sa "egen nivå" — kan du utveckla?

**David:** API:et är skrivet för folk som vet vad API är — för dem är det inga konstigheter. Men vi som inte visste fick det att ta längre tid att leta sig fram än vad det hade behövt göra.

## Testmiljö och kostnad

**Erik:** Du nämnde innan att du höll på i en testmiljö. Hur var det?

**David:** Jag tyckte det var lite jobbigt att be om förlängning av testmiljön och sånt. Jag var osäker på om Flowbase hade någon kostnad för det — jag som inte jobbar med sånt här funderade lite: "kostar jag Flowbase en massa pengar nu?"

**Maja:** Och i produktion?

**David:** Min enda önskan är kostnadsbudget. Jag tyckte det var synd att jag inte kunde sätta ett tak på våra anrop — om någon av min amatörkod fastnar i en loop. Det är en systemrisk — antingen att någon använder programmet fel eller att någonting buggar och det jobbas upp ganska höga kostnader. Det hade bara varit skönt att ha ett kostnadstak helt enkelt för att sova gott.

## Hur skrev du integrationen?

**Erik:** Du sa att du inte är utvecklare. Hur byggde du den faktiska integrationen?

**David:** Jag har skrivit allt med AI. ChatGPT är min bästa vän. Man har inte behövt någon bakgrund alls i kodskrivning. Det är egentligen ganska otroligt.

**Sara:** Stötte du på saker där AI:n ledde dig fel?

**David:** Ja, lite. Det handlade mest om att förstå vilket fält man faktiskt vill ha — det finns ju registrerad innehavare och bekräftad innehavare. Det var en sån sak där AI:n tog fel. Samma sak med totala area och nettoarea — då behöver man fundera på vilken det är man vill ha. Det har egentligen inte med koden att göra, utan med att förstå datan.

## Nyheter och uppföljning

**Maja:** Hur tar ni del av nyheter eller ändringar i API:erna?

**David:** Inte alls, liksom. Om det kanske mejlas till mig. Kommer det något så hade jag nog läst det, men annars inte.

**Erik:** Om du fick önska en sak till för att göra starten enklare — vad?

**David:** Det enda jag saknar är nog bara en säljsida för API:et och hur man kommer igång. Det ska stå någonting i stil med "vill du hämta data via kod istället? Så här kommer du igång med API:et". Om ni tittar till exempel på Stripe med sina utvecklarguider — där finns en bra säljsida och man fattar direkt vad man ska göra.

**Maja:** Det här var jättevärdefullt, David. Tack.

**David:** Tack själva. Kul att någon frågar.
