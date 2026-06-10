---
title: Experience map — Licenstilldelning (Team Aurora)
date: 2026-05-25
purpose: The customer journey this product supports. Consumed by OST-cluster-opportunities and OST-extract-experience-map.
tags: [product-context, experience-map]
---

# Experience map — Licenstilldelning

**Team:** Aurora
**Product outcome:** Öka andelen nya kunder som på egen hand når sitt första lyckade produktionsanrop mot API:et utan att kontakta Flowbase, från 40% till 80% inom 60 dagar från avtalstecknande.

## Faser

### Fas 1 — Förfrågan inkommer
**Friktion:** low

**Steg:**
1. Inkommen förfrågan, offert, förnyelse/tillval. Kund eller säljare.
2. Rabatt? (beslutspunkt: Ja → Säljare förhandlar rabatt, Nej → vidare)
3. Säljare förhandlar rabatt

### Fas 2 — Behovsanalys & avtal
**Friktion:** low

**Steg:**
1. Skickar avtal (Word) till kund per post i Freshdesk

### Fas 3 — Avtalsskrivning
**Friktion:** medium

**Steg:**
1. Avtalsprocess
2. Ny eller befintlig kund? (beslutspunkt: Ny → Lägg upp kund i SalesForce, Befintlig → vidare)
3. Lägg upp kund / Uppdatera kundinfo i SalesForce

### Fas 4 — Kreditkontroll & ekonomi
**Friktion:** medium

**Steg:**
1. Kreditbetyg (beslutspunkt: Rating under 40 → kreditprövning, Rating över 40 → faktureringsunderlag)
2. Support gör kreditprövning via Credit Safe
3. Godkänd? (beslutspunkt: Nej → Meddela avslag till kund, Ja → vidare)
4. Beställer faktureringsunderlag. Ekonomi via e-post
5. Färdigställer avtalet och laddar upp i SalesForce

### Fas 5 — Licens-upplägg
**Friktion:** high

**Steg:**
1. API-flöde / SSO-flöde / Webb-flöde (beslutspunkt vid ingång: API, SSO eller Webb)
2. Skapar avtal i Kärnprodukten Admin med konfiguration, transaktioner och behörigheter
3. Kopplar avtal och projekt för fakturering via Debiteringssystemet
4. Lägger till abonnemangsavgift i Debiteringssystemet
5. Skapar transaktionsanvändare i Keycloak
6. Finns licenspaket i Licenshanteraren? (beslutspunkt: Ja → Tilldelar licens, Nej → Beställer nytt licenspaket från Aurora)
7. Beställer nytt licenspaket från Aurora
8. Tilldelar licens till kund utifrån licenspaket i Licenshanteraren
9. Lägger till användare och licensadministratör för kund i Licenshanteraren

### Fas 6 — Rabatter
**Friktion:** high

**Steg:**
1. Rabatt avtalad? (beslutspunkt: Ja → rabattprocess, Nej → vidare till fas 7)
2. Petra/Karin beställer tillägg av rabatter via e-post till Olof. Uppdaterar rabatt-fil
3. Olof räknar ut och fyller i rabattprislistan i Prisverktyget

### Fas 7 — Aktivering & leverans
**Friktion:** low

**Steg:**
1. Skickar välkomstmail till kund med inloggningsuppgifter, prislista och lathund. Meddelar licensadministratör

## System

Freshdesk, SalesForce, Credit Safe, Kärnprodukten Admin, Debiteringssystemet, Keycloak, Licenshanteraren, Prisverktyget