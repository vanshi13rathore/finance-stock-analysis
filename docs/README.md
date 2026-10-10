# 📚 Documentation

Welcome to the Finance Stock Analysis documentation. Start here and follow the
guides in order, or jump directly to what you need.

## Guides

| Guide | What you'll learn |
|-------|-------------------|
| [Getting Started](getting-started.md) | Install dependencies and run your first analysis in 5 minutes |
| [User Guide](user-guide.md) | Walkthrough of the notebook, dashboard, and using `src/` as a library |
| [CLI Reference](cli-reference.md) | Every `run_analysis.py` option, with examples and outputs |
| [Methodology](methodology.md) | Metric definitions, formulas, assumptions, and limitations |
| [Data](data.md) | Data sources, caching, file schemas, and the synthetic fallback |
| [API Reference](api-reference.md) | Public functions in `src/` with signatures and examples |
| [Architecture](architecture.md) | Project structure and data-flow diagram |
| [Findings](findings.md) | Key results and how to reproduce them |
| [Troubleshooting](troubleshooting.md) | FAQ and fixes for common problems |

## Project-level files

- [README](../README.md) — project overview and quickstart
- [CONTRIBUTING](../CONTRIBUTING.md) — how to contribute code or docs
- [CHANGELOG](../CHANGELOG.md) — version history

## Conventions used in these docs

- `code` in backticks means a file, function, or something you type.
- Commands assume your working directory is the repository root and that you
  installed dependencies with `pip install -r requirements.txt`.
- "Live data" means prices downloaded from Yahoo Finance; "demo data" means the
  built-in reproducible synthetic dataset (see [Data](data.md)).
