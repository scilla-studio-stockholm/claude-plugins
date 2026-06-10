# Golden-run rubric

Structural checklist for the OST pipeline in the flat 2.0.0 model. Run these against
`expected-output/OST-discovery/` (the reference run) or against a fresh run of `input/`.
Because the skills are non-deterministic, this rubric checks **structure and invariants**,
not exact output text.

Run all commands from `fixtures/golden/`. ✅ = passing on the committed reference run.

## 1. Flat workspace — exactly 5 files at the scope root ✅

```sh
find expected-output/OST-discovery -maxdepth 1 -type f | sort
```
Expect exactly: `1-opportunity.md`, `2-solutions.md`, `3-riskiest-assumptions.md`,
`4-experiments.md`, `decisions.json`. No nested/dated round folders.

## 2. Phase 07 — 18 solution candidates ✅

```sh
python3 -c "import json;d=json.load(open('expected-output/OST-discovery/_working/solution-candidates.json'));print(d['generation_summary']['total_solutions'], len(d['solutions']))"
```
Expect `18 18` (3 rounds × 3 roles × 2 ideas).

## 3. Phase 10 — all three method-passes present ✅

```sh
python3 -c "import json,collections;d=json.load(open('expected-output/OST-discovery/_working/assumptions.json'));c=collections.Counter(m for s in d['assumptions_per_solution'] for a in s['assumptions'] for m in a['source_methods']);print(dict(c))"
```
Expect all of `storymap`, `pre-mortem`, `outcome-impact` to appear (method-diversified).

## 4. Phase 12 — riskiest = importance:high AND evidence:weak ✅

```sh
python3 -c "import json;r=json.load(open('expected-output/OST-discovery/decisions.json'))['decided']['assumptions']['riskiest'];print(len(r), all(a['importance']=='high' and a['evidence']=='weak' for a in r))"
```
Expect a non-zero count and `True`.

## 5. Phase 13 — one test card per riskiest assumption ✅

```sh
python3 -c "import json;d=json.load(open('expected-output/OST-discovery/decisions.json'))['decided'];print(len(d['experiments']['test_cards']), len(d['assumptions']['riskiest']))"
```
Expect the two counts to be equal.

## 6. Milestones are self-contained ✅

Each `N-*.md` at the root must be understandable without opening `_working/`. Spot check
that `3-riskiest-assumptions.md` carries both a "Riskiest assumptions" section (flagged,
with rationale) and a "Seen against the full set" section (every assumption with its score).

## 7. All JSON is schema-valid ✅

```sh
for f in $(find expected-output/OST-discovery -name '*.json'); do python3 -c "import json,sys;json.load(open(sys.argv[1]))" "$f" || echo "INVALID $f"; done
```
Expect no `INVALID` lines.

## 8. Viewer has data for every tab ✅

The viewer renders these from `_working/` plus `decisions.json` at the root. All must exist:

```sh
cd expected-output/OST-discovery && ls decisions.json \
  _working/comparison-matrix.json _working/riskiest-assumptions.json \
  _working/validation-experiments.json _working/solution-candidates.json \
  _working/experience-map-extracted.json _working/experience-map-clustered.json
```

## 9. Safety gate — zero identifying terms (must pass before any commit) ✅

```sh
grep -rinoE "\b(metria|norrsken|fastighet[a-zåäö]*|lantmäteri[a-zåäö]*|delfi|fsök|vendure|\bipm\b|markus|torbjörn|nordström|jonna|\bfrans\b|eriksson|therese|boverket|hedman|koordinat[a-zåäö]*|geodata|samfällighet[a-zåäö]*|tomtareal|\bareal\b|taxerad|lagfaren|\bägare\b|team fast|team popcorn)\b" . \
  | grep -viE "intervju-[0-9]+-aurora" || echo "CLEAN"
```
Expect `CLEAN`. (The `aurora` interview slugs are the fixture's own names, not residue.)
