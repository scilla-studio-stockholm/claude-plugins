---
title: "Top solutions: opp-7-1 - jag har inte haft någon guide eller information"
date: 2026-05-29
purpose: Milestone for OST step 6 (top solutions to explore in parallel). Trio reviews; decided.solutions in decisions.json is the ratified record. Input to assist 9 (assumption generator).
tags: [top-three-selection, ost, schema-v0.2]

---

# Top solutions: opp-7-1

Schema version: 0.2

> **Trio HITL:** This is the AI's proposal. Review the rationales, override if you disagree. When approved, `decided.solutions` in `decisions.json` is the ratified record. The trio may edit `decisions.json` directly to swap picks or adjust rationale.

## Chosen opportunity

**opp-7-1** (Phase: fas-7) - "jag har inte haft någon guide eller information, och ni har ju också sagt att ni inte jobbar med att hjälpa till att implementera - det får kunden göra själv" - *David, intervju-4-aurora-apr-13, ~rad 58*

## Product outcome

> Öka andelen nya kunder som på egen hand når sitt första lyckade produktionsanrop mot API:et utan att kontakta Flowbase, från 40% till 80% inom 60 dagar från avtalstecknande.

## The three picks

### Pick 1: Automatiserad onboarding-portal med självbetjäning från dag ett

**sol-r1-pm-1** [PM, R1]

När kunden signerar avtalet aktiveras automatiskt en personaliserad onboarding-portal med steg-för-steg-guide, API-nycklar och testmiljö - allt utan att Flowbase behöver agera. Kunden kan göra sitt första lyckade API-anrop helt på egen hand, vilket direkt mäter sig mot målet om 80% självbetjänade kunder.

*Why it can move the outcome:* Den kausala vägen är direkt: signerat avtal triggar automatisk aktivering av allt kunden behöver - credentials, guided workflow, testmiljö - utan att kunden behöver initiera kontakt med Flowbase. Lösningen adresserar aktiveringsgapet som ett systemsteg snarare än ett hjälpinnehåll, vilket gör den till den enskilt starkaste rörelsen mot 80% självbetjänade kunder.

### Pick 2: Interaktiv kom-igång-guide direkt efter avtalssignering

**sol-r1-ux-1** [UX, R1]

Kunden möts av en steg-för-steg-guide i portalen så fort avtalet är signerat - guiden leder dem från API-nyckel till första lyckade anrop i produktionsmiljö utan att behöva kontakta Flowbase. Varje steg bekräftas med direkt feedback (grönt bock = lyckat anrop) så att kunden vet exakt var de befinner sig i processen och vad som återstår.

*Why it can move the outcome:* Den valda opportuniteten namnger explicit 'ingen guide' som friktion - den här lösningen är den direkta motpolen. Realtidsfeedback per steg eliminerar de vanligaste kontaktskälen under aktivering: 'var är jag?', 'vad gör jag härnäst?' och 'fungerade det?'. Den kausala vägen är: kunden vet alltid sitt nästa steg och får bekräftelse på varje genomfört steg → behöver aldrig initiera kontakt med Flowbase → interaktionsräknaren stannar på noll.

### Pick 3: Automatisk välkomstpåse med konfigurerade kodexempel för kundens miljö

**sol-r1-ux-2** [UX, R1]

Direkt vid aktivering skickas ett personaliserat paket - med API-nyckel, bas-URL och färdiga kodexempel i de vanligaste språken (Python, JavaScript, cURL) - där variablerna redan är ifyllda med kundens faktiska uppgifter. Kunden kopierar och kör, inget att konfigurera eller slå upp, vilket eliminerar det vanligaste skälet till att höra av sig till Flowbase under onboarding.

*Why it can move the outcome:* Konfigurationsförvirring - rätt bas-URL, autentiseringshuvud, request-format - är det vanligaste skälet till att kunder kontaktar Flowbase under API-aktivering. Pre-populerade kodexempel med kundens egna credentials tar bort den interaktionen helt. Den kausala vägen är: kunden kör ett fungerande anrop utan att behöva fråga om syntax eller konfiguration → uppnår första lyckade produktionsanrop utan en enda kontakt med Flowbase.

## Also considered

Clusters and candidates not selected, from `_working/clustered-solutions.json`:

**c1 - Guidad portalupplevelse och felsökning (övriga 6 av 7)**

- **sol-r1-pm-2** *Interaktiv Quick Start-guide med live API-sandbox* - Sandbox-mekaniken täcks av den bredare aktiveringsportalen (sol-r1-pm-1); sol-r1-ux-1 är den starkare guideimplementationen.
- **sol-r1-tl-2** *Interaktiv API-testmiljö i kundportalen* - Samma sandbox-ansats som sol-r1-pm-2; sol-r1-ux-1 täcker aktiveringsresan mer komplett.
- **sol-r2-ux-1** *Progressiv onboarding med kontextuell hjälp* - Värdefull förfining av guidekonceptet men sekundär relativt den grundläggande steg-för-steg-guiden (sol-r1-ux-1).
- **sol-r2-ux-2** *Tom-state-design i portalen* - Adresserar specifika förvirringsmoment snarare än hela aktiveringsresan.
- **sol-r3-ux-1** *Diagnostiska felmeddelanden med felsökningsguide* - Felåterställning är sekundärt till att förebygga att kunden fastnar från början.
- **sol-r3-ux-2** *Beständig onboarding-tidslinje* - Progresstransparens hjälper men driver inte kunden till slutförande utan en aktiv guide.

**c2 - Automatiserad aktivering vid avtalssignering (övriga 2 av 4)**

- **sol-r1-tl-1** *Automatiserad provisionering av API-nyckel* - Credential-provisionering är en komponent i sol-r1-pm-1; täcks av den bredare portallösningen.
- **sol-r3-pm-2** *Onboarding-kit som obligatoriskt leveransvillkor* - Stark policyvariant uppströms men mer indirekt än en direkt produktförändring.

**c3 - Proaktiv statusspårning och eskalering**

- **sol-r2-pm-2** *Automatiserad statusspårning som triggar proaktiv hjälp* - Genererar interaktioner (automatiserade e-post, möteserbjudanden) snarare än att eliminera dem; minskar inte interaktionsräknaren mot noll.
- **sol-r2-pm-1** *Dedikerad kundframgångsstrategi för de första 30 dagarna* - CS-protokoll inkluderar fortfarande interaktioner (proaktiva, inte reaktiva); uppnår inte 0 interaktioner.
- **sol-r2-tl-1** *Händelsedriven statusspårning* - Internt verktyg som ger Flowbases support synlighet men inte direkt minskar kundinitierade interaktioner.

**c4 - Utvecklarverktyg och kodbaserad integration**

- **sol-r2-tl-2** *SDK och CLI-verktyg* - Stark för developer-native kunder men smalare målgrupp än portalbaserade lösningar; kodexempel-bunten (sol-r1-ux-2) täcker det omedelbara tekniska behovet bredare.
- **sol-r3-tl-1** *CI/CD-integrationspaket* - Kraftfullt men förutsätter att kunden redan använder CI/CD; täcker en delmängd av kundbasen.
- **sol-r3-tl-2** *Infrastruktur-as-Code-moduler* - Adresserar enbart de tekniskt mest mogna kunderna med IaC-mognadsgrad.

**c5 - Certifierat partnernätverk för sista-milen**

- **sol-r3-pm-1** *API-integrationspartners nätverk* - Omdirigerar implementeringshjälp till tredje part snarare än att minska den totala friktionen i kundens väg till första lyckade anrop.
