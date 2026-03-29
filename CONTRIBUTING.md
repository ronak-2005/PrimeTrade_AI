# Contributing

## Setup

```bash
git clone <repo>
cd primetrade-assignment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running locally

```bash
make run          # Jupyter notebook
make pipeline     # Headless pipeline
```

## Running with Docker

```bash
make docker-build
make docker-run       # Opens Jupyter on localhost:8888
make docker-pipeline  # Runs headless pipeline
```

## Code style

- Follow PEP 8
- Max line length: 100 characters
- All paths go through `src/config.py` — no hardcoded paths in notebooks or scripts
- All reusable functions go in `src/utils.py`
- Run `make lint` before committing

## Branch naming

- `main` — stable, production
- `develop` — integration branch
- `feature/your-feature-name` — new work

## Notebook conventions

- Notebooks are numbered and sequential: `01_`, `02_`, etc.
- Each notebook has a markdown header with Input / Output clearly stated
- All charts saved via `save_chart()` — never `plt.savefig()` directly
- No hardcoded paths inside notebooks
