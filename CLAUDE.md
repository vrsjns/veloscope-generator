# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Veloscope Generator produces personalized daily horoscopes for cyclists. It is a three-stage batch pipeline built around OpenAI's asynchronous Batch API, with AWS S3 as the data store and the coordination medium. Each stage is an independent containerized job run on a schedule (AWS ECS Fargate via CloudWatch Events).

## Commands

All commands assume the repo root and an activated `venv` (`python -m venv venv && source venv/bin/activate && pip install -r requirements.txt`).

```bash
make lint        # flake8 + pylint + mypy over packages/ and shared/
make test        # pytest with coverage over packages/ and shared/
make security    # bandit -r packages/ shared/ -x tests/
make dev-setup   # install runtime + all dev tooling and `pre-commit install`
```

Run a single test:

```bash
pytest tests/test_get_zodiac_sign.py::test_returns_correct_sign
```

Run the pipeline stages locally (`make prepare` / `make upload` / `make download`, or `make pipeline` for all three). Each needs `PYTHONPATH` to include the repo root so `shared` resolves — the Makefile targets set this automatically:

```bash
PYTHONPATH=$PYTHONPATH:. python packages/batch-prepare/src/batch_prepare_input.py
```

Lint/type config lives in `pyproject.toml` (mypy targets Python 3.8, `disallow_untyped_defs` is on — all functions need type annotations). isort uses the black profile, line length 79.

## Architecture

### The three stages (`packages/`)
Each package has its own `src/` entrypoint, `Dockerfile`, and ECR image. They never call each other directly — they communicate only through S3 state.

1. **batch-prepare** (`batch_prepare_input.py`): loads `riders.json` from S3, derives each rider's zodiac sign from their `birth_date` (ISO `YYYY-MM-DD`), builds a horoscope prompt per rider, writes a JSONL file in OpenAI Batch request format, uploads it to S3 under `openai/input/`, and records a new batch (status `prepared`) in the control file. Targets *tomorrow's* date.
2. **batch-upload** (`batch_upload_input.py`): finds `prepared` batches, downloads their JSONL from S3, uploads to OpenAI (`files.create`), submits a batch job (`batches.create`, 24h completion window), and moves them to `submitted` — storing the returned `openai_batch_id`.
3. **batch-download** (`batch_download_result.py`): finds `submitted` batches, polls OpenAI for completion, and on success parses the result JSONL and writes one horoscope JSON per rider to S3 under `horoscope/<target_date>/<name>.json`, moving the batch to `completed` (or `failed`).

### The control file is the state machine
`batch_control.json` in S3 (key from `CONTROL_KEY`) is the single source of truth coordinating the stages. It holds a `{"batches": [...]}` list; each batch flows `prepared → submitted → completed`/`failed`. All reads/writes go through `shared/utils/control_file_utils.py` (`create_batch`, `get_prepared_batches`, `get_pending_batches`, `update_batch_status`). A batch is identified by its internal `batch_id` (a UUID) — distinct from the `openai_batch_id` assigned by OpenAI at upload time. There is no locking; concurrent writers would clobber each other.

### Shared code (`shared/`)
`config.py` centralizes all configuration, loaded from env vars via `python-dotenv` with development defaults — import constants from here rather than calling `os.getenv` in stage code. `utils/` holds the S3 client (`s3_utils.py`), control-file logic, OpenAI client init (`openai_utils.py`), and logging setup (`logging_utils.py`). The S3 utils swallow errors and return `None`/`False` on failure rather than raising; stage code checks return values and updates batch status accordingly.

### Important structural quirk
Package directories are hyphenated (`batch-prepare`), so they are **not importable as Python packages**. Two consequences:
- Tests add `packages/batch-prepare/src` and the repo root to `sys.path` in `tests/conftest.py`, then import the entrypoint module directly (`from batch_prepare_input import ...`).
- At Docker build time the CI workflow **copies `shared/` into each package directory** (`cp -r shared/* packages/<pkg>/shared/`) and copies `requirements.txt` in, because each Dockerfile builds with the package dir as context. `shared` is not pip-installed; it ships as copied source with `PYTHONPATH=/app`.

## Deployment

`.github/workflows/docker-build.yml` runs on push to `main`/`master`/`develop`. It uses `dorny/paths-filter` to detect which of `batch-prepare`/`batch-upload`/`batch-download`/`shared`/`requirements.txt` changed, then builds and pushes only the affected images to ECR (tagged `latest`, the commit SHA, and the environment). A change to `shared/` or `requirements.txt` rebuilds all three images. `.github/workflows/code-quality.yml` runs flake8/pylint/mypy/bandit on every push and PR to `main`.

Infrastructure is Terraform under `terraform/` (`modules/` + per-env `environments/{dev,prod}/`, plus `shared/` for cross-env resources like ECR). Stages run as scheduled ECS Fargate tasks driven by CloudWatch Event rules (`modules/scheduling`). Apply `terraform/shared` before any environment. State is in S3 with a DynamoDB lock table (see `terraform/README.md`).

## Configuration

Copy `.env.example` to `.env`. Key vars: `OPENAI_API_KEY`, `OPENAI_MODEL`, `S3_BUCKET_NAME`, `RIDERS_FILE`, `CONTROL_KEY`, `AWS_REGION`, plus optional `ENABLE_FILE_LOGGING`/`LOG_DIR`/`LOG_LEVEL`. AWS credentials come from the standard boto3 chain (env vars locally, task IAM role in Fargate).
