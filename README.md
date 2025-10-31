# Abstract Backend

Abstract Backend provides a **pluggable backend layer** for Python services. Applications code against shared protocols while concrete providers—Redis, Kafka, AWS SQS, or your own implementation—are discovered at runtime. Install a provider with `pip`, remove it with `pip uninstall`, and keep your business logic unchanged.

## Status & Quality

### CI/CD & Testing
[![CI](https://github.com/Chisanan232/abstract-backend/actions/workflows/ci.yaml/badge.svg)](https://github.com/Chisanan232/abstract-backend/actions/workflows/ci.yaml)
[![Documentation](https://github.com/Chisanan232/abstract-backend/actions/workflows/documentation.yaml/badge.svg)](https://github.com/Chisanan232/abstract-backend/actions/workflows/documentation.yaml)
[![Documentation Build Check](https://github.com/Chisanan232/abstract-backend/actions/workflows/docs-build-check.yaml/badge.svg)](https://github.com/Chisanan232/abstract-backend/actions/workflows/docs-build-check.yaml)

### Code Coverage & Quality
[![codecov](https://codecov.io/gh/Chisanan232/abstract-backend/graph/badge.svg?token=FXfgxZ1xQU)](https://codecov.io/gh/Chisanan232/abstract-backend)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=Chisanan232_abstract-backend&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=Chisanan232_abstract-backend)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=Chisanan232_abstract-backend&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=Chisanan232_abstract-backend)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=Chisanan232_abstract-backend&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=Chisanan232_abstract-backend)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=Chisanan232_abstract-backend&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=Chisanan232_abstract-backend)

### Code Style & Standards
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Type Checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](http://mypy-lang.org/)

### Package Info
[![PyPI version](https://badge.fury.io/py/abstract-backend.svg)](https://badge.fury.io/py/abstract-backend)
[![Supported Versions](https://img.shields.io/pypi/pyversions/abstract-backend.svg?logo=python&logoColor=FBE072)](https://pypi.org/project/abstract-backend)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

### Downloads
[![Downloads](https://pepy.tech/badge/abstract-backend)](https://pepy.tech/project/abstract-backend)
[![Downloads/Month](https://pepy.tech/badge/abstract-backend/month)](https://pepy.tech/project/abstract-backend)
[![Downloads/Week](https://pepy.tech/badge/abstract-backend/week)](https://pepy.tech/project/abstract-backend)

---

## Why it exists

- **🚫 Stop copying backend code** – Extracted from real MCP server projects so multiple services can share the same queue abstraction.
- **📐 Protocol-first design** – Contracts live in `abe/types.py`, keeping providers honest with structural typing and contract tests.
- **🔍 Runtime discovery** – `load_backend()` selects implementations via Python entry points, driven by environment variables.
- **📊 Operational clarity** – Logging helpers, contract suites, and documentation make backends observable and portable.

## Features

- **📮 Queue provider protocols** covering publish, consume, and lifecycle operations.
- **⚙️ AsyncLoopConsumer** helper to execute handlers against any compliant backend.
- **🪵 Logging utilities** for consistent configuration across providers and apps.
- **🧪 Contract tests** to validate third-party implementations.
- **📚 Documentation & examples** detailing architecture, provider lifecycle, and runtime flow.

## Installation

Install the core library:

```bash
pip install abstract-backend
```

Then install one or more providers, for example the Redis backend:

```bash
pip install abe-redis
```

Set `QUEUE_BACKEND=redis` (the entry-point exposed by `abe-redis`) and `load_backend()` will resolve the correct provider at runtime.

## Quick start ⚡️

```python
from abe.backends.message_queue.loader import load_backend
from abe.backends.message_queue.consumer import AsyncLoopConsumer


async def process(payload: dict[str, object]) -> None:
    ...


async def main() -> None:
    backend = load_backend()
    consumer = AsyncLoopConsumer(backend, group="billing")
    await consumer.run(process)
```

See `docs/contents/development/architecture/` for diagrams explaining the flow and provider relationships.

## Building providers 🧩

1. Implement the protocols from `abe/types.py` (especially `MessageQueueBackendProtocol`).
2. Expose a `from_env()` constructor for runtime configuration.
3. Register an entry point under `abe.backends.message_queue` in `pyproject.toml`.
4. Run the contract tests in `test/contract_test/backends/message_queue/` against your provider.
5. Publish your package to PyPI; users activate it with `pip install` and `QUEUE_BACKEND`.

The showcase at `/docs/src/pages/showcase.tsx` highlights template and reference implementations such as `abe-redis`.

## Development 🛠️

- Install dev dependencies with `uv pip install -r pyproject.toml` or your preferred tool.
- Run tests: `uv run pytest`.
- Type checking: `uv run mypy`.
- Linting: `uv run pylint abe tests`.

The project follows `black` formatting and `pylint` linting (see `.pre-commit-config.yaml`).

## Documentation & showcase 📖

- Developer docs live under `docs/contents/development/` and include architecture, provider lifecycle, and layer integration guides.
- A Showcase page (`/docs/src/pages/showcase.tsx`) lists template and implementation repositories with release badges.
- Run `cd docs && pnpm start` for local previews.

## CI/CD & workflows 🤖

- GitHub Actions definitions reside in `.github/workflows/`.
- Reusable workflows leverage the logging, testing, and packaging helpers of this project.
- `docusaurus.config.ts` and `docs/contents/development/sidebars.ts` manage documentation navigation.

## License

This project is licensed under the [MIT License](./LICENSE).
