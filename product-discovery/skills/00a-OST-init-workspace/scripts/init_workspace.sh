#!/usr/bin/env bash
# OST-init-workspace: scaffold the flat OST-discovery/ tree and context
# templates that all OST-* skills depend on.
#
# Default layout is flat, single-product, single-round:
#   OST-discovery/
#   ├── product-context/   product-outcome.md, experience-map.md
#   ├── _working/          all phase JSON + intermediate markdown
#   └── decisions.json     ratified decisions (the spine)
#
# Multi-product and multi-round nesting are opt-in and created manually
# only when needed (see workspace-scope.md). This script scaffolds the
# flat default.
#
# Idempotent: existing files are never overwritten. Each action prints
# CREATED, SKIPPED (exists), or ERROR. Summary at the end.

set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  init_workspace.sh --product <slug> [--date YYYY-MM-DD]

Required:
  --product <slug>   Short lowercase ASCII slug (e.g. fsok, pmf-analyse).
                     Names the product in decisions.json and context templates.

Optional:
  --date YYYY-MM-DD  Override today's date used in template frontmatter.

Run from the repo root where OST-discovery/ should live. Scaffolds the
flat default layout. For multi-product or multi-round setups, see
product-discovery/knowledge/discovery/workspace-scope.md.
EOF
}

PRODUCT=""
DATE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --product) PRODUCT="$2"; shift 2 ;;
    --date)    DATE="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "ERROR: unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ -z "$PRODUCT" ]]; then
  echo "ERROR: --product is required." >&2
  usage >&2
  exit 2
fi

is_slug() {
  [[ "$1" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]
}

if ! is_slug "$PRODUCT"; then
  echo "ERROR: --product value '$PRODUCT' is not a valid slug." >&2
  echo "Slug rules: lowercase ASCII letters/digits, hyphen-separated, no leading/trailing hyphen." >&2
  echo "Transliterate Swedish chars: å→a, ä→a, ö→o." >&2
  exit 2
fi

if [[ -z "$DATE" ]]; then
  DATE=$(date +%Y-%m-%d)
fi

if ! [[ "$DATE" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
  echo "ERROR: --date must be YYYY-MM-DD, got: $DATE" >&2
  exit 2
fi

DISCOVERY_DIR="OST-discovery"
CONTEXT_DIR="$DISCOVERY_DIR/product-context"
WORKING_DIR="$DISCOVERY_DIR/_working"

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
title: Experience map — $PRODUCT
date: $DATE
purpose: The customer journey this product supports. Consumed by OST-cluster-opportunities and OST-extract-experience-map.
tags: [product-context, experience-map]

---

# Experience map

<!-- Two ways to populate the experience map:

     1. Save a screenshot at product-context/experience-map.png and run
        OST-extract-experience-map. The skill writes the structured
        experience-map-extracted.{md,json} into _working/.

     2. Run OST-setup-product and walk through the experience map
        interview. It writes experience-map-extracted.{md,json} into _working/.

     Both paths write to _working/, not this file. Downstream skills
     (OST-cluster-opportunities) read _working/experience-map-extracted.json.
     This file stays as a human-readable placeholder/summary. -->

TBD.
EOF
)

# ----- decisions.json template -----
decisions_json_template() {
  local product="$1"
  cat <<ENDJSON
{
  "schema_version": "1.0",
  "product": "$product",
  "team": null,
  "round": ".",
  "product_outcome": "",
  "decided": {}
}
ENDJSON
}

# ----- scaffold -----
echo "Scaffolding flat OST-discovery/ workspace for product=$PRODUCT (date=$DATE)..."
echo

mk_dir "$DISCOVERY_DIR"
mk_dir "$CONTEXT_DIR"
mk_dir "$WORKING_DIR"

mk_file "$CONTEXT_DIR/product-outcome.md" "$PRODUCT_OUTCOME_TEMPLATE"
mk_file "$CONTEXT_DIR/experience-map.md" "$EXPERIENCE_MAP_TEMPLATE"
mk_file "$DISCOVERY_DIR/decisions.json" "$(decisions_json_template "$PRODUCT")"

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
if grep -q "^TBD" "$CONTEXT_DIR/product-outcome.md" 2>/dev/null; then
  echo "1. Edit $CONTEXT_DIR/product-outcome.md and write the product outcome."
  echo "   Downstream OST skills hard-exit when this file is empty or contains TBD."
fi
if [[ ! -f "$CONTEXT_DIR/experience-map.png" && ! -f "$CONTEXT_DIR/experience-map.jpg" ]]; then
  echo "2. Either save a screenshot at $CONTEXT_DIR/experience-map.{png,jpg} and run OST-extract-experience-map,"
  echo "   or write the journey directly into $CONTEXT_DIR/experience-map.md."
fi
echo "3. Active scope: $DISCOVERY_DIR/ (flat). OST-* skills read/write here; plumbing lands in _working/."
