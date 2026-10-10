# 🤝 Contributing

Thanks for helping improve this project! Small, focused pull requests are best.

## Development setup

```bash
git clone https://github.com/vanshi13rathore/finance-stock-analysis.git
cd finance-stock-analysis
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest tests/ -q   # must be green before you start
```

## Workflow

1. Create a branch: `git checkout -b <type>/<short-description>`
   (e.g. `feat/capm-beta`, `fix/var-edge-case`, `docs/cli-examples`).
2. Make your change (code + tests + docs — see below).
3. Run the checks: `pytest tests/ -q` and, if you touched the pipeline,
   `python scripts/run_analysis.py --synthetic --no-cache`.
4. Open a pull request describing **what** changed and **why**.

## Code guidelines

- **One home per logic:** shared code goes in `src/` (`config`, `data`,
  `metrics`, `plots`, `portfolio`) — never duplicated in the notebook, CLI, or
  dashboard.
- **Keep `metrics`/`portfolio` pure:** no network, no plotting, no global
  state, so tests stay fast and offline.
- **Type hints + docstrings** on all public functions (see existing modules for
  style: one-line summary, then Parameters/Returns sections where useful).
- **No new heavy dependencies** without discussion — the Monte Carlo frontier
  intentionally avoids scipy.
- Match the existing style (4-space indent, `snake_case`, ≤ 88-ish columns).

## Tests

- New metrics/logic in `src/` **must** come with unit tests in `tests/`.
- Tests must be **deterministic** (fixed seeds) and **offline** (use
  `data.generate_synthetic_prices()` fixtures, never Yahoo).
- Run the suite: `pytest tests/ -q` (currently 23 tests).

## Docs

- User-facing changes need doc updates: behavior → `docs/user-guide.md` or
  `docs/cli-reference.md`; new metrics → `docs/methodology.md`;
  new functions → `docs/api-reference.md`.
- Keep [README](README.md) concise — details belong in `docs/`.
- Verify internal Markdown links still resolve (see below).

## Check before pushing

```bash
pytest tests/ -q                                          # tests green
python scripts/run_analysis.py --synthetic --no-cache     # pipeline runs
python - <<'EOF'                                          # links resolve
import re, pathlib
root = pathlib.Path(".")
ok = True
for md in list(root.glob("*.md")) + list(root.glob("docs/*.md")):
    for m in re.finditer(r"\]\(([^)#]+)(?:#[^)]*)?\)", md.read_text()):
        target = (md.parent / m.group(1)).resolve()
        if not target.exists():
            print(f"BROKEN: {md} -> {m.group(1)}"); ok = False
print("links OK" if ok else "BROKEN LINKS FOUND")
EOF
```
