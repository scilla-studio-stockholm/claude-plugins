---
title: Intervju 1 med Anders om en tidigare API-integration
date: 2026-04-08
purpose: Syntetisk discovery-intervju med en intern utvecklare om en tidigare integration mot Datahubben. Underlag för team Auroras discovery i våg 1. ALLT INNEHÅLL ÄR PÅHITTAT (se ../README.md).
participants:
  - Maja (intervjuare)
  - Erik (intervjuare)
  - Sara (observatör, team Aurora)
  - Anders (intervjuperson, utvecklare)
tags:
  - aurora
  - discovery
  - intervju
  - integration
---

# Intervju 1 — Aurora, 8 april 2026

## Inledning

**Erik:** Kul att du kunde vara med, Anders. Vi tittar på tiden från påskrivet avtal till att en kund faktiskt använder våra API-licenser. Du har ju byggt en del integrationer internt.

**Anders:** Ja, en del. Fråga på.

## Bygga själv eller köpa färdigt

**Maja:** Berätta om integrationen mot Datahubben. Gärna från början.

**Anders:** Vi utgick väldigt hårt från att bygga upp den själva, vilket gjorde att vi hämtade all information på det sättet. Sen förstod vi att det här kommer vi aldrig att få ordning på, så vi beslöt att ta det förpackat från Datahubben, vilket också finns som något man kan hämta.

**Sara:** Fick ni någon stöttning kring det vägvalet, eller gjorde ni det på egen hand?

**Anders:** Vi gjorde allt på eget. Ingen hjälp. Det löste sig till slut, men det tog tid.

## Hur vet man att det fungerar?

**Maja:** Hur avgjorde ni att integrationen faktiskt fungerade?

**Anders:** Det är en jättesvår fråga. Jag får ett 200-svar och kanske en fil, så det gick bra. Men jag har ingen aning om det är korrekt eller om det används rätt. Hur skulle jag kunna veta det?

**Erik:** Görs det automatiserade tester?

**Anders:** Det är "lowest of low". Man tar sin egen datapost och säger att det stämmer ungefär. Att garantera kvaliteten på det man levererar är inte jättelätt — att hela tiden kvalitetssäkra och beskriva data. Det kan vara längst bak i blocket, inga problem, men det ska finnas där.

## Helheten

**Maja:** Om du tänker på arbetssättet i stort — saknar du något?

**Anders:** Vi har väldigt mycket bra grejer på bra ställen, men vi har inte riktigt helheten. Vi saknar förståelse mellan delarna ibland. Vi skulle jobba mer som en enhet, med en gemensam kraft. Tydligare möten mellan de olika delarna.

**Erik:** Du har nämnt domänkunskap tidigare. Hur ser du på den?

**Anders:** Jag tror att i team Fenix saknar de mycket av den här domänkunskapen. Inte att de saknar det på det sättet, utan att de verkligen saknar den och skulle vilja ha den närmare sig. Det blir svårt att ta en extern kund hela vägen om vi själva inte äger förståelsen.

**Maja:** Tack, Anders. Det här gav oss mycket.

**Anders:** Ingen fara. Hör av er.
