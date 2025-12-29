# Contradiction Detector

## Setup (uv)
1. Create a virtual environment:
   `uv venv`
2. Activate it:
   `source .venv/bin/activate`
3. Install dependencies:
   `uv pip install -e .`
4. Install dev tools:
   `uv pip install -e ".[dev]"`

## Lint (ruff)
- `ruff check src`
- `ruff format src`
