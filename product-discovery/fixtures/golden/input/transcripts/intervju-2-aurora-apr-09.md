---
title: Intervju 2 med Niklas om SSO-integrationer och secrets
date: 2026-04-09
purpose: Syntetisk discovery-intervju med en intern utvecklare om behörigheter, secret-rotation och självservice. Underlag för team Auroras discovery i våg 1. ALLT INNEHÅLL ÄR PÅHITTAT (se ../README.md).
participants:
  - Maja (intervjuare)
  - Erik (intervjuare)
  - Sara (observatör, team Aurora)
  - Niklas (intervjuperson, utvecklare)
tags:
  - aurora
  - discovery
  - intervju
  - sso
  - behorigheter
---

# Intervju 2 — Aurora, 9 april 2026

## Inledning

**Maja:** Tack för att du är med, Niklas. Vi vill förstå friktionen i hur kunder får åtkomst och kommer igång. Du jobbar nära SSO och behörigheter.

**Niklas:** Japp. Det finns en del att säga där.

## Secrets och rotation

**Erik:** Berätta om en typisk gång ni behöver byta en kunds secret.

**Niklas:** Det går alltid någon timme eller två och bara diskutera hur man för över den här secret-cykeln. Sen när vi väl ska byta så måste vi göra det i samförstånd med kunden så att dom vet att ingenting bara slutar fungera. Det tar alltid några timmar, och kan de bara göra det själv så är det mycket smidigare.

**Sara:** Vad gör det extra känsligt?

**Niklas:** Vi har ingen möjlighet att köra två samtidigt aktiva secrets. Så att byta över den, ja, men då kommer det sluta funka för dom om dom inte har satt upp det på sin sida. Det blir en manuell dans varje gång.

## Koppling mellan integration och licens

**Maja:** Hur hänger en SSO-integration ihop med själva licensen?

**Niklas:** Vi har ingen koppling idag mellan en SSO-integration och en licens, utan vi hårdkodade behörigheterna kopplat till integrationen. Det fungerar, men det skalar inte.

**Erik:** Finns det självservice för det här?

**Niklas:** Självservice-endpointsen är inte skapade. Det finns i någon epic eller nåt sånt, men det är inte implementerat. Så allt går via oss idag.

**Maja:** Om du fick önska?

**Niklas:** Det bästa hade varit ifall dom hade kunnat peka ut: ja, men det här attributet eller den här grupptillhörigheten, och så kopplar det till en licens, i självservice-gränssnittet. Då slipper kunden vänta på oss.

**Maja:** Tack, Niklas. Värdefullt.

**Niklas:** Bara hojta till om ni vill gräva mer.
