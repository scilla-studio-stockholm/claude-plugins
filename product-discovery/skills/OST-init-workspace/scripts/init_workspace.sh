#!/usr/bin/env bash
# OST-init-workspace: scaffold the discovery/ tree and context templates
# that all OST-* skills depend on.
#
# Two layout modes:
#   - Multi-product (default): discovery/<team>/<product>/...
#   - Single-product (--single-product): discovery/...   (no team/product nesting)
#
# Idempotent: existing files are never overwritten. Each action prints
# CREATED, SKIPPED (exists), or ERROR. Summary at the end.

set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  Multi-product mode (default):
    init_workspace.sh --team <slug> --product <slug>
                      [--opportunity <slug>] [--selection]
                      [--date YYYY-MM-DD]

  Single-product mode:
    init_workspace.sh --single-product --product <slug>
                      [--opportunity <slug>] [--selection]
                      [--date YYYY-MM-DD]

Required:
  --product <slug>      Short lowercase ASCII slug (e.g. fsok, pmf-analyse)
  --team <slug>         Required unless --single-product. Short slug (e.g. fast).

Optional:
  --single-product      Drop the <team>/<product>/ nesting. Use when the repo
                        will only ever hold one product. Cannot combine with --team.
  --opportunity <slug>  Also scaffold opportunities/<slug>/ + a discovery round
                        folder dated today; set .current-scope to that round.
  --selection           Scaffold opportunity-selection/<today>/ and set
                        .current-scope there. Mutually exclusive with --opportunity.
  --date YYYY-MM-DD     Override today's date for the round folder name.

Run from the repo root where discovery/ should live.
EOF
}

TEAM=""
PRODUCT=""
OPPORTUNITY=""
SELECTION=0
SINGLE_PRODUCT=0
DATE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --team)            TEAM="$2"; shift 2 ;;
    --product)         PRODUCT="$2"; shift 2 ;;
    --opportunity)     OPPORTUNITY="$2"; shift 2 ;;
    --selection)       SELECTION=1; shift ;;
    --single-product)  SINGLE_PRODUCT=1; shift ;;
    --date)            DATE="$2"; shift 2 ;;
    -h|--help)         usage; exit 0 ;;
    *) echo "ERROR: unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ -z "$PRODUCT" ]]; then
  echo "ERROR: --product is required." >&2
  usage >&2
  exit 2
fi

if [[ "$SINGLE_PRODUCT" -eq 1 ]]; then
  if [[ -n "$TEAM" ]]; then
    echo "ERROR: --single-product and --team are mutually exclusive." >&2
    echo "Single-product mode drops the team/product nesting; the team layer has no place to live." >&2
    exit 2
  fi
else
  if [[ -z "$TEAM" ]]; then
    echo "ERROR: --team is required in multi-product mode." >&2
    echo "Use --single-product if this repo will only ever hold one product." >&2
    usage >&2
    exit 2
  fi
fi

if [[ "$SELECTION" -eq 1 && -n "$OPPORTUNITY" ]]; then
  echo "ERROR: --selection and --opportunity are mutually exclusive (a single .current-scope can only point at one round)." >&2
  exit 2
fi

is_slug() {
  [[ "$1" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]
}

for arg_name in TEAM PRODUCT OPPORTUNITY; do
  val="${!arg_name}"
  if [[ -n "$val" ]] && ! is_slug "$val"; then
    echo "ERROR: --${arg_name,,} value '$val' is not a valid slug." >&2
    echo "Slug rules: lowercase ASCII letters/digits, hyphen-separated, no leading/trailing hyphen." >&2
    echo "Transliterate Swedish chars: å→a, ä→a, ö→o." >&2
    exit 2
  fi
done

if [[ -z "$DATE" ]]; then
  DATE=$(date +%Y-%m-%d)
fi

if ! [[ "$DATE" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
  echo "ERROR: --date must be YYYY-MM-DD, got: $DATE" >&2
  exit 2
fi

DISCOVERY_DIR="discovery"
if [[ "$SINGLE_PRODUCT" -eq 1 ]]; then
  PRODUCT_ROOT="$DISCOVERY_DIR"
  MODE="single-product"
else
  PRODUCT_ROOT="$DISCOVERY_DIR/$TEAM/$PRODUCT"
  MODE="multi-product"
fi
CONTEXT_DIR="$PRODUCT_ROOT/_product-context"

declare -a TOUCHED=()

mk_dir() {
  local path="$1"
  if [[ -d "$path" ]]; then
    echo "SKIPPED (exists): $path/"
  else
    mkdir -p "$path"
    echo "CREATED:          $path/"
    TOUCHED+=("$path/")
  fi
}

mk_file() {
  local path="$1"
  local content="$2"
  if [[ -e "$path" ]]; then
    echo "SKIPPED (exists): $path"
  else
    mkdir -p "$(dirname "$path")"
    printf '%s' "$content" > "$path"
    echo "CREATED:          $path"
    TOUCHED+=("$path")
  fi
}

# ----- product-outcome.md template -----
PRODUCT_OUTCOME_TEMPLATE=$(cat <<EOF
---
title: Product outcome — $PRODUCT
date: $DATE
purpose: The product outcome this product is trying to move. Referenced by every OST-* skill (validation, comparison, brainstorming, assumption generation).
tags: [product-context, outcome]

---

# Product outcome

<!-- Write the product outcome here.
     Format: a measurable customer-behavior change with a target value and time horizon.
     See product-discovery/knowledge/discovery/product-outcomes-i-olika-skeden.md
     for examples and the outcome-vs-business-outcome distinction.

     Example:
     "Increase the share of new users who complete first-search within 60s
      from 40% to 65% by end of Q3 2026."

     Downstream OST skills hard-exit when this file is missing or empty.
     Replace this comment and the TBD line below before running any other OST skill. -->

TBD — fill this in before running any OST-* skill.
EOF
)

# ----- experience-map.md template -----
if [[ "$SINGLE_PRODUCT" -eq 1 ]]; then
  EXP_TITLE="$PRODUCT"
else
  EXP_TITLE="$TEAM/$PRODUCT"
fi
EXPERIENCE_MAP_TEMPLATE=$(cat <<EOF
---
title: Experience map — $EXP_TITLE
date: $DATE
purpose: The customer journey this product supports. Consumed by OST-cluster-opportunities and OST-extract-experience-map.
tags: [product-context, experience-map]

---

# Experience map

<!-- Two ways to populate this:

     1. Save a screenshot at _product-context/experience-map.png and run
        OST-extract-experience-map. The skill will produce a structured
        JSON + markdown rendering inside the active round folder.

     2. Write the journey here directly (phases, steps, friction levels,
        decision branches). See
        product-discovery/knowledge/discovery/experience-mapping.md
        for schema v0.1 and the structural pattern. -->

TBD.
EOF
)

# ----- chosen-opportunity.md template (only if --opportunity) -----
chosen_opportunity_template() {
  local opp="$1"
  cat <<EOF
---
title: Chosen opportunity — $opp
date: $DATE
purpose: Persistent context for this opportunity. Survives across discovery rounds and is read by every phase-B OST-* skill.
tags: [opportunity, persistent-context]

---

# Chosen opportunity: $opp

## Opportunity (citation format)

<!-- The customer-voice statement in citation format.
     See product-discovery/knowledge/discovery/opportunity-citation-format.md.
     A valid citation includes: who said it, what they said (verbatim or
     paraphrased with quote markers), and the underlying job-to-be-done. -->

TBD.

## Why this one

<!-- Why the trio picked this opportunity over the alternatives compared
     in the opportunity-selection round. Reference the comparison-matrix
     if useful. -->

TBD.

## Ratified

$DATE by <names>
EOF
}

# ----- round-folder READMEs -----
SELECTION_ROUND_README=$(cat <<'EOF'
# Opportunity-selection round (phase A)

This dated folder collects the artifacts from one run of the
opportunity-selection workflow: extract candidates from interviews,
validate them against the citation format, compare against the product
outcome, and produce a proposal for one opportunity to ratify.

Each dated subfolder under `opportunity-selection/` is a separate run.
Re-run when you have new interview material or want to compare a fresh
set of candidates against the same outcome.

## Files that will land here (produced by the OST-* skills in order)

- `opportunities-extracted.{md,json}` — raw opportunity citations extracted from interview transcripts (OST-opportunity-extractor).
- `experience-map-extracted.{md,json}` — structured experience map extracted from a screenshot, if you have one (OST-extract-experience-map).
- `experience-map-clustered.{md,json}` — opportunities clustered onto the journey phases (OST-cluster-opportunities).
- `opportunities-validated.md` — trio's verdict per opportunity: approved / needs tweak / solution in disguise (OST-validate-opportunities).
- `comparison-matrix.{md,json}` — qualitative matrix of approved opportunities × Torres criteria (OST-compare-opportunities).
- `chosen-opportunity-proposal.{md,json}` — AI's proposal of one opportunity to ratify, with rationale and alternatives considered (OST-select-opportunity).

After the trio ratifies a proposal, copy/refine it into
`../../opportunities/<opp-slug>/chosen-opportunity.md` (or re-run
`OST-init-workspace --opportunity <slug>` to scaffold that folder).
EOF
)

DISCOVERY_ROUND_README=$(cat <<'EOF'
# Discovery round (phase B)

This dated folder collects the artifacts from one run of the
solution-discovery workflow for the chosen opportunity in the parent
folder. Brainstorm divergent solutions, cluster, pick top three,
surface assumptions, and design validation experiments.

Each dated subfolder is a separate run. Re-run when you want to
brainstorm again with new constraints or after experiments invalidate
earlier assumptions.

## Files that will land here (produced by the OST-* skills in order)

- `solution-candidates.{md,json}` — 18 divergent solution candidates from three role-diverse sub-agents (OST-brainstorm-solutions).
- `clustered-solutions.{md,json}` — candidates collapsed into 3-5 thematic clusters (OST-cluster-solutions).
- `top-three-solutions.{md,json}` — three solutions picked to carry into assumption testing (OST-select-top-three-solutions).
- `assumptions.{md,json}` — assumptions that must hold for each of the three solutions to move the product outcome (OST-generate-assumptions).
- `assumptions-categorized.{md,json}` — assumptions tagged into Cagan's five product-risk categories (OST-assumption-categorizer).
- `riskiest-assumptions.{md,json}` — assumptions where importance is high AND evidence is weak (OST-riskiest-assumptions).
- `validation-experiments.{md,json}` — Bland Test Cards for each riskiest assumption (OST-validation-experiment-designer).

The parent folder `../chosen-opportunity.md` holds the persistent context
for this opportunity. The parent's `../ratifications.md` is an optional
trio log of decisions made.
EOF
)

# ----- discovery README (formerly workspace README) -----
DISCOVERY_README=$(cat <<'EOF'
# Discovery workspace

This directory holds artifacts produced by the `product-discovery` plugin's
OST-* skills. Layout and conventions are shared across all skills — do
not move files around without checking the workspace-scope spec.

## Layout modes

Two modes are supported. Both use the same relative-path math, so the
phase skills do not care which mode the repo uses.

### Multi-product

For organisations with multiple teams or products in one repo:

```text
discovery/
├── .current-scope                                # one-line file: relative path to the active round folder
├── <team>/                                       # e.g. fast, norrsken
│   ├── _team-context/                            # team-level docs (optional)
│   └── <product>/                                # e.g. fsok
│       ├── _product-context/                     # product-outcome.md, experience-map.{md,json}
│       ├── opportunity-selection/<YYYY-MM-DD>/   # phase A round
│       └── opportunities/<opp-slug>/             # ratified opportunity
│           ├── chosen-opportunity.md             # persistent context
│           ├── ratifications.md                  # optional trio log
│           └── <YYYY-MM-DD>/                     # phase B round
```

### Single-product

For small repos with exactly one product (no team/product nesting):

```text
discovery/
├── .current-scope
├── _product-context/                             # product-outcome.md, experience-map.{md,json}
├── opportunity-selection/<YYYY-MM-DD>/           # phase A round
└── opportunities/<opp-slug>/                     # ratified opportunity
    ├── chosen-opportunity.md
    ├── ratifications.md                          # optional
    └── <YYYY-MM-DD>/                             # phase B round
```

## Scope resolution

Every OST-* skill resolves its scope (the round folder it reads/writes
inside) in this order, taking the first that exists:

1. Explicit `scope=` argument passed by the user when invoking the skill.
2. `discovery/.current-scope` — one-line file with a relative path from
   the repo root to the active round folder.
3. Prompt the user, defaulting to the latest dated round under the most
   recently touched opportunity.

A scope is an **opportunity-selection round** if its path contains
`/opportunity-selection/`, otherwise a **discovery round** if it
contains `/opportunities/`.

## Adding a new opportunity or round

Re-run `OST-init-workspace` with the new `--opportunity <slug>` or
`--selection` flag. The script is idempotent: existing files are never
overwritten.

## Full spec

The canonical convention (filenames, slug rules, context walk-up rules,
both layout modes) lives in the plugin source at
`product-discovery/knowledge/discovery/workspace-scope.md`.
EOF
)

# ----- scaffold -----
if [[ "$MODE" == "single-product" ]]; then
  echo "Scaffolding OST discovery workspace (single-product mode) for product=$PRODUCT (date=$DATE)..."
else
  echo "Scaffolding OST discovery workspace for team=$TEAM product=$PRODUCT (date=$DATE)..."
fi
echo

mk_dir "$DISCOVERY_DIR"
if [[ "$PRODUCT_ROOT" != "$DISCOVERY_DIR" ]]; then
  mk_dir "$PRODUCT_ROOT"
fi
mk_dir "$CONTEXT_DIR"
mk_dir "$PRODUCT_ROOT/opportunity-selection"
mk_dir "$PRODUCT_ROOT/opportunities"

mk_file "$DISCOVERY_DIR/README.md" "$DISCOVERY_README"
mk_file "$CONTEXT_DIR/product-outcome.md" "$PRODUCT_OUTCOME_TEMPLATE"
mk_file "$CONTEXT_DIR/experience-map.md" "$EXPERIENCE_MAP_TEMPLATE"

CURRENT_SCOPE_TARGET=""

if [[ -n "$OPPORTUNITY" ]]; then
  OPP_DIR="$PRODUCT_ROOT/opportunities/$OPPORTUNITY"
  ROUND_DIR="$OPP_DIR/$DATE"
  mk_dir "$OPP_DIR"
  mk_file "$OPP_DIR/chosen-opportunity.md" "$(chosen_opportunity_template "$OPPORTUNITY")"
  mk_dir "$ROUND_DIR"
  mk_file "$ROUND_DIR/README.md" "$DISCOVERY_ROUND_README"
  CURRENT_SCOPE_TARGET="$ROUND_DIR"
fi

if [[ "$SELECTION" -eq 1 ]]; then
  ROUND_DIR="$PRODUCT_ROOT/opportunity-selection/$DATE"
  mk_dir "$ROUND_DIR"
  mk_file "$ROUND_DIR/README.md" "$SELECTION_ROUND_README"
  CURRENT_SCOPE_TARGET="$ROUND_DIR"
fi

CURRENT_SCOPE_FILE="$DISCOVERY_DIR/.current-scope"
if [[ -n "$CURRENT_SCOPE_TARGET" ]]; then
  if [[ -e "$CURRENT_SCOPE_FILE" ]]; then
    existing=$(cat "$CURRENT_SCOPE_FILE")
    if [[ "$existing" == "$CURRENT_SCOPE_TARGET" ]]; then
      echo "SKIPPED (exists): $CURRENT_SCOPE_FILE (already points at $CURRENT_SCOPE_TARGET)"
    else
      echo "SKIPPED (exists): $CURRENT_SCOPE_FILE (currently points at $existing; not overwriting)"
      echo "                  To change scope, edit $CURRENT_SCOPE_FILE manually or delete it and re-run."
    fi
  else
    printf '%s\n' "$CURRENT_SCOPE_TARGET" > "$CURRENT_SCOPE_FILE"
    echo "CREATED:          $CURRENT_SCOPE_FILE → $CURRENT_SCOPE_TARGET"
    TOUCHED+=("$CURRENT_SCOPE_FILE")
  fi
fi

# ----- summary -----
echo
echo "Summary"
echo "-------"
echo "Mode: $MODE"
if [[ ${#TOUCHED[@]} -eq 0 ]]; then
  echo "Nothing scaffolded — all targets already existed."
else
  echo "${#TOUCHED[@]} path(s) created:"
  for p in "${TOUCHED[@]}"; do
    echo "  $p"
  done
fi
echo
echo "Next steps"
echo "----------"
if grep -q "^TBD" "$CONTEXT_DIR/product-outcome.md" 2>/dev/null; then
  echo "1. Edit $CONTEXT_DIR/product-outcome.md and write the product outcome."
  echo "   Downstream OST skills hard-exit when this file is empty or contains TBD."
fi
if [[ ! -f "$CONTEXT_DIR/experience-map.png" && ! -f "$CONTEXT_DIR/experience-map.jpg" ]]; then
  echo "2. Either save a screenshot at $CONTEXT_DIR/experience-map.{png,jpg} and run OST-extract-experience-map,"
  echo "   or write the journey directly into $CONTEXT_DIR/experience-map.md."
fi
if [[ -n "$CURRENT_SCOPE_TARGET" ]]; then
  echo "3. Active scope: $CURRENT_SCOPE_TARGET"
  echo "   Subsequent OST-* skills will read/write inside that folder unless you pass scope= explicitly."
  echo "   Open $CURRENT_SCOPE_TARGET/README.md to see what files will land there."
fi
