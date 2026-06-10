---
title: Solution candidates - opp-7-1 (Aurora)
date: 2026-05-29
purpose: Divergent solution-candidate set for the chosen opportunity, paired with solution-candidates.json. Consumed by assist 7 (OST-cluster-solutions). Trio review at assist 8 (top-3 selector).
tags: [solution-brainstorm, ost, schema-v0.1]

---

# Solution candidates: opp-7-1 (Aurora)

Source: `OST-discovery/decisions.json`
Schema version: 0.1
Paired JSON: `_working/solution-candidates.json`

Generation summary: 3 rounds x 3 roles x 2 ideas = 18 total. Roles: Product Manager (PM), UX Designer (UX), Tech Lead (TL).

## Chosen opportunity

**opp-7-1** (Phase: fas-7) - "jag har inte haft någon guide eller information, och ni har ju också sagt att ni inte jobbar med att hjälpa till att implementera - det får kunden göra själv" - *David, intervju-4-aurora-apr-13, ~rad 58*

## Product outcome

> Öka andelen nya kunder som på egen hand når sitt första lyckade produktionsanrop mot API:et utan att kontakta Flowbase, från 40% till 80% inom 60 dagar från avtalstecknande.

## Round 1 (6)

- **[PM]** *Automatiserad onboarding-portal med självbetjäning från dag ett* - När kunden signerar avtalet aktiveras automatiskt en personaliserad onboarding-portal med steg-för-steg-guide, API-nycklar och testmiljö - allt utan att Flowbase behöver agera. Kunden kan göra sitt första lyckade API-anrop helt på egen hand, vilket direkt mäter sig mot målet om 80% självbetjänade kunder.
- **[PM]** *Interaktiv Quick Start-guide med live API-sandbox* - En inbyggd sandbox-miljö med kodexempel i vanliga programmeringsspråk gör att kunden kan testa och validera anrop mot ett simulerat API direkt i dokumentationen - utan att invänta produktionsuppgifter eller support. Det eliminerar det vanligaste skälet till att kunder hör av sig under aktiveringsperioden.
- **[UX]** *Interaktiv kom-igång-guide direkt efter avtalssignering* - Kunden möts av en steg-för-steg-guide i portalen så fort avtalet är signerat - guiden leder dem från API-nyckel till första lyckade anrop i produktionsmiljö utan att behöva kontakta Flowbase. Varje steg bekräftas med direkt feedback (grönt bock = lyckat anrop) så att kunden vet exakt var de befinner sig i processen och vad som återstår.
- **[UX]** *Automatisk välkomstpåse med konfigurerade kodexempel för kundens miljö* - Direkt vid aktivering skickas ett personaliserat paket - med API-nyckel, bas-URL och färdiga kodexempel i de vanligaste språken (Python, JavaScript, cURL) - där variablerna redan är ifyllda med kundens faktiska uppgifter. Kunden kopierar och kör, inget att konfigurera eller slå upp, vilket eliminerar det vanligaste skälet till att höra av sig till Flowbase under onboarding.
- **[TL]** *Automatiserad provisionering av API-nyckel direkt vid avtalsignering* - När ett avtal markeras som signerat i CRM:et triggar ett webhook-anrop en provisioning-pipeline som automatiskt skapar API-nyckel, sätter rättigheter och skickar kundspecifik onboarding-data till kunden utan manuell handpåläggning. Kunden får allt de behöver för att göra sitt första anrop utan att Flowbase behöver agera.
- **[TL]** *Interaktiv API-testmiljö i kundportalen som ersätter manuell vägledning* - En integrerad sandbox i kundportalen låter kunden autentisera sig och göra testanrop mot riktiga endpoints med sin egna nyckel, med inline-dokumentation och live-felsvar. Toilen med att vägleda kunden via e-post och möten ersätts av ett system som svarar kunden i realtid när de fastnar.

## Round 2 (6)

- **[PM]** *Dedikerad kundframgångsstrategi för de första 30 dagarna* - Flowbase inför ett strukturerat 30-dagars aktiveringsprotokoll där en utsedd Customer Success-kontakt proaktivt checkar in med kunden vid dag 1, dag 7 och dag 30 - utan att kunden behöver initiera kontakten. Målet är att eliminera 'vi hjälper inte med implementation'-upplevelsen genom att Flowbase äger ansvaret för kundens första lyckade anrop, inte kunden.
- **[PM]** *Automatiserad statusspårning som triggar proaktiv hjälp* - Kundportalen övervakar om kunden gjort sitt första lyckade produktionsanrop inom X dagar efter aktivering - om inte triggas automatiskt en åtgärd: ett e-postmeddelande med felsökningsguide, ett erbjudande om bokat genomgångsmöte, eller eskalering till Customer Success. Detta vänder på ansvaret så att Flowbase agerar på uteblivet framsteg, istället för att kunden måste söka hjälp.
- **[UX]** *Progressiv onboarding med kontextuell hjälp vid varje steg* - Istället för en linjär guide exponeras rätt information precis när kunden behöver den - vid API-nyckelskärmen visas autentiseringshjälp, vid första anropsfelet visas felsökningsguide. Systemet spårar var kunden fastnar och justerar vilket innehåll som visas härnäst.
- **[UX]** *Tom-state-design i portalen som aktivt vägleder nästa åtgärd* - Varje tom vy i kundportalen - innan API-nyckeln hämtats, innan första anropet gjorts - ersätts med en handlingsbar tom-state som berättar exakt vad kunden ska göra härnäst och varför. Ingenting lämnas tomt utan syfte, och kunden vet alltid sitt nästa steg utan att behöva söka efter information.
- **[TL]** *Händelsedriven statusspårning som ersätter manuell uppföljning* - Bygg ett event-drivet system som automatiskt trackar var kunden befinner sig i onboardingflödet - från signerat avtal till första lyckade produktionsanrop - och triggar interna alerts om en kund fastnar i mer än X timmar på ett steg. Det eliminerar behovet av att kunden hör av sig för statusuppdateringar och ger supporten proaktiv synlighet utan manuell övervakning.
- **[TL]** *SDK och CLI-verktyg för nyckelhantering utan portalinloggning* - Publicera ett officiellt SDK (Python, JavaScript, Java) och ett CLI-verktyg som låter kunden hämta och rotera sin API-nyckel, inspektera rättigheter och köra en diagnostikcheck mot produktionsmiljön direkt från terminalen. Kunden behöver aldrig öppna en portal eller kontakta Flowbase för att verifiera att integrationen är korrekt konfigurerad.

## Round 3 (6)

- **[PM]** *API-integrationspartners nätverk för sista-milen implementering* - Flowbase bygger ett certifierat partnernätverk av systemintegratörer och konsulter som erbjuds direkt i kundportalen vid avtalssignering - kunder som vill ha hjälp med implementering kan med ett klick bli matchade med en partner som redan kan Flowbase API:et. Flowbase äger inte leveransen men möjliggör den, och tar bort implementeringsfriktion utan att behöva bygga en egen supportorganisation.
- **[PM]** *Onboarding-kit som obligatoriskt leveransvillkor i avtalsmall* - Flowbase förhandlar in ett standardiserat tekniskt onboarding-kit (credential-leverans, testmiljötillgång, teknisk snabbstart) som ett obligatoriskt leveransvillkor i ramavtalstexter och direktavtalsmallar. Lösningen är en policyändring uppströms - innan kunden ens signerat vet de exakt vad de får och när, och Flowbase är kontraktuellt bundet att leverera det automatiserat.
- **[UX]** *Diagnostiska felmeddelanden med inbyggd felsökningsguide per felkod* - När ett API-anrop misslyckas returneras inte bara en felkod utan ett kontextuellt meddelande i portalen som förklarar exakt vad som gick fel, varför det troligen hände, och vilket nästa steg är. Varje vanligt fel (felaktig nyckel, fel endpoint, saknad parameter) har en dedikerad recovery-vy med konkret åtgärd - kunden behöver inte kontakta Flowbase för att förstå felet.
- **[UX]** *Beständig onboarding-tidslinje som visar var kunden befinner sig* - En beständig statusrad i portalen visar var kunden faktiskt är i aktiveringsflödet (avtal signerat - nyckel genererad - testanrop gjort - produktionsanrop gjort) och vad som återstår. Varje steg inkluderar en indikator om det fastnat - t.ex. 'nyckel genererad för 3 dagar sedan men inget anrop registrerat' - med en synlig nästa-steg-länk direkt i tidslinjen.
- **[TL]** *CI/CD-integrationspaket med pipeline-templates för vanliga byggmiljöer* - Flowbase publicerar officiella integrationspaket (GitHub Actions, GitLab CI, Azure DevOps) med färdiga workflow-filer för autentisering, nyckelinjicering och röktest mot produktions-API:et. Kunden importerar ett template-repo eller kör ett init-kommando som genererar korrekt konfigurerad pipeline - första lyckade anrop sker automatiskt som en del av deploy-pipeline och det manuella valideringssteget försvinner ur onboardingflödet.
- **[TL]** *Infrastruktur-as-Code-moduler för direktintegration utan portalsteg* - Officiella Terraform- och Pulumi-moduler för Flowbases API-resurser publiceras i respektive publikt registry. En infrastrukturansvarig hos kunden deklarerar API-nyckel och endpoint-konfiguration direkt i sin IaC-kodbas utan att passera kundportalen - provisionering, nyckelrotation och behörighetshantering drivs av versionskontrollerade manifests i kundens eget repo. Portalen förblir ett alternativ men är inte längre i den kritiska vägen för kunder med IaC-mognad.
