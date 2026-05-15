#!/usr/bin/env bash
# OST-init-workspace: scaffold the workspace/<team>/<product>/... tree
# and context templates that all OST-* skills depend on.
#
# Idempotent: existing files are never overwritten. Each action prints
# CREATED, SKIPPED (exists), or ERROR. Summary at the end.

set -euo pipefail

usage() {
  cat <<'EOF'
Usage: init_workspace.sh --team <slug> --product <slug>
                         [--opportunity <slug>]
                         [--portfolio]
                         [--date YYYY-MM-DD]

Required:
  --team <slug>         Short lowercase ASCII slug (e.g. fast, norrsken)
  --product <slug>      Short lowercase ASCII slug (e.g. fsok)

Optional:
  --opportunity <slug>  Also scaffold opportunities/<slug>/ + an empty
                        discovery round folder dated today; set .current-scope
                        to that round.
  --portfolio           Scaffold portfolio/<today>/ and set .current-scope
                        there. Mutually exclusive with --opportunity.
  --date YYYY-MM-DD     Override today's date for the round folder name.

Run from the repo root where workspace/ should live.
EOF
}

TEAM=""
PRODUCT=""
OPPORTUNITY=""
PORTFOLIO=0
DATE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --team)        TEAM="$2"; shift 2 ;;
    --product)     PRODUCT="$2"; shift 2 ;;
    --opportunity) OPPORTUNITY="$2"; shift 2 ;;
    --portfolio)   PORTFOLIO=1; shift ;;
    --date)        DATE="$2"; shift 2 ;;
    -h|--help)     usage; exit 0 ;;
    *)             echo "ERROR: unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ -z "$TEAM" || -z "$PRODUCT" ]]; then
  echo "ERROR: --team and --product are required." >&2
  usage >&2
  exit 2
fi

if [[ "$PORTFOLIO" -eq 1 && -n "$OPPORTUNITY" ]]; then
  echo "ERROR: --portfolio and --opportunity are mutually exclusive (a single .current-scope can only point at one round)." >&2
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

WORKSPACE="workspace"
PRODUCT_ROOT="$WORKSPACE/$TEAM/$PRODUCT"
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
EXPERIENCE_MAP_TEMPLATE=$(cat <<EOF
---
title: Experience map — $TEAM/$PRODUCT
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
     in the portfolio round. Reference the comparison-matrix if useful. -->

TBD.

## Ratified

$DATE by <names>
EOF
}

# ----- workspace README -----
WORKSPACE_README=$(cat <<'EOF'
# OST workspace

This directory holds artifacts produced by the `product-discovery` plugin's
OST-* skills. Layout and conventions are shared across all 13 skills — do
not move files around without checking the workspace-scope spec.

## Layout

```text
workspace/
├── .current-scope                       # one-line file: relative path to the active round folder
├── <team>/                              # e.g. fast, norrsken
│   ├── _team-context/                   # team-level docs (optional)
│   └── <product>/                       # e.g. fsok
│       ├── _product-context/            # product-outcome.md, experience-map.{md,json}
│       ├── portfolio/<YYYY-MM-DD>/      # phase A round: validate / compare / select
│       └── opportunities/<opp-slug>/    # ratified opportunity
│           ├── chosen-opportunity.md    # persistent context
│           ├── ratifications.md         # optional trio log
│           └── <YYYY-MM-DD>/            # phase B round: brainstorm → experiments
```

Underscore-prefixed folders (`_team-context/`, `_product-context/`) are
read-only context for skills.

## Scope resolution

Every OST-* skill resolves its scope (the round folder it reads/writes
inside) in this order, taking the first that exists:

1. Explicit `scope=` argument passed by the user when invoking the skill.
2. `workspace/.current-scope` — one-line file with a relative path from
   the repo root to the active round folder.
3. Prompt the user, defaulting to the latest dated round under the most
   recently touched opportunity.

A scope is a **portfolio round** if its path contains `/portfolio/`,
otherwise a **discovery round** if it contains `/opportunities/`.

## Adding a new opportunity or round

Re-run `OST-init-workspace` with the new `--opportunity <slug>` or
`--portfolio` flag. The script is idempotent: existing files are never
overwritten.

## Full spec

The canonical workspace convention (filenames, slug rules, context
walk-up rules) lives in the plugin source at
`product-discovery/knowledge/discovery/workspace-scope.md`.
EOF
)

# ----- scaffold -----
echo "Scaffolding OST workspace for team=$TEAM product=$PRODUCT (date=$DATE)..."
echo

mk_dir "$WORKSPACE"
mk_dir "$PRODUCT_ROOT"
mk_dir "$CONTEXT_DIR"
mk_dir "$PRODUCT_ROOT/portfolio"
mk_dir "$PRODUCT_ROOT/opportunities"

mk_file "$WORKSPACE/README.md" "$WORKSPACE_README"
mk_file "$CONTEXT_DIR/product-outcome.md" "$PRODUCT_OUTCOME_TEMPLATE"
mk_file "$CONTEXT_DIR/experience-map.md" "$EXPERIENCE_MAP_TEMPLATE"

CURRENT_SCOPE_TARGET=""

if [[ -n "$OPPORTUNITY" ]]; then
  OPP_DIR="$PRODUCT_ROOT/opportunities/$OPPORTUNITY"
  ROUND_DIR="$OPP_DIR/$DATE"
  mk_dir "$OPP_DIR"
  mk_file "$OPP_DIR/chosen-opportunity.md" "$(chosen_opportunity_template "$OPPORTUNITY")"
  mk_dir "$ROUND_DIR"
  CURRENT_SCOPE_TARGET="$ROUND_DIR"
fi

if [[ "$PORTFOLIO" -eq 1 ]]; then
  ROUND_DIR="$PRODUCT_ROOT/portfolio/$DATE"
  mk_dir "$ROUND_DIR"
  CURRENT_SCOPE_TARGET="$ROUND_DIR"
fi

CURRENT_SCOPE_FILE="$WORKSPACE/.current-scope"
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
if [[ ! -s "$CONTEXT_DIR/product-outcome.md" ]] || grep -q "^TBD" "$CONTEXT_DIR/product-outcome.md" 2>/dev/null; then
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
fi
