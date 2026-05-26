# Viewer launch procedure

Shared reference for all skills that produce viewer-compatible JSON. Include as the final step in any skill that writes one of the viewer's data files.

## Path resolution

Try these locations in order. Use the first that exists:

1. `~/.claude/plugins/marketplaces/scilla-studio/product-discovery/templates/` — marketplace clone (full git checkout, includes `templates/`)
2. `~/.claude/plugins/cache/scilla-studio/product-discovery/*/templates/` — plugin cache (glob the version folder)

If neither exists, skip with a note:
> "Viewer not available — install the scilla-studio marketplace (`/plugin marketplace add scilla-studio-stockholm/claude-plugins && /plugin install product-discovery@scilla-studio`) to enable auto-open."

Let `VIEWER_ROOT` be the resolved path (the directory containing `serve.py` and `viewer/`).

## Discovery root resolution

Walk up from `<scope>` until you find a directory that:
- contains `.current-scope`, OR
- is named `discovery/`

This becomes `DISCOVERY_ROOT` (the `--data` argument to `serve.py`).

## Round path

The relative path from `DISCOVERY_ROOT` to `<scope>` (e.g. `metria/opp-1/2026-05-25`). This becomes the `?round=` query parameter.

## Server management

1. Check if port 3000 is already in use: `lsof -ti:3000`
2. If occupied, inspect the running server's command line: `ps -p <pid> -o args=`
   - If `--data` matches `DISCOVERY_ROOT`: reuse the existing server (no restart needed)
   - If `--data` does NOT match: kill the process and start fresh
3. If the port is free (or after killing a mismatched server), start:
   ```
   python3 VIEWER_ROOT/serve.py \
     --templates VIEWER_ROOT/viewer \
     --data DISCOVERY_ROOT \
     --port 3000
   ```
   Run in the background (the server blocks; use `&` or the background run tool).

## Open in browser

```
open "http://localhost:3000/_viewer/?round=<round-path>"
```

## Refresh-only shortcut

If the server is already running and pointing at the correct discovery root, skip the server management steps. Just open the browser URL — the viewer fetches JSON with `Cache-Control: no-cache`, so a page refresh picks up new data automatically.
