# Abstract Backend

Abstract Backend provides a **pluggable backend layer** for Python services. Applications code against shared protocols while concrete providers—Redis, Kafka, AWS SQS, or your own implementation—are discovered at runtime. Install a provider with `pip`, remove it with `pip uninstall`, and keep your business logic unchanged.

[![CI](https://github.com/Chisanan232/abstract-backend/actions/workflows/ci.yaml/badge.svg)](https://github.com/Chisanan232/abstract-backend/actions/workflows/ci.yaml)
[![Docs Build](https://github.com/Chisanan232/abstract-backend/actions/workflows/documentation.yaml/badge.svg)](https://github.com/Chisanan232/abstract-backend/actions/workflows/documentation.yaml)
[![Docs Check](https://github.com/Chisanan232/abstract-backend/actions/workflows/docs-build-check.yaml/badge.svg)](https://github.com/Chisanan232/abstract-backend/actions/workflows/docs-build-check.yaml)
[![Type Check](https://github.com/Chisanan232/abstract-backend/actions/workflows/type-check.yml/badge.svg)](https://github.com/Chisanan232/abstract-backend/actions/workflows/type-check.yml)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://pre-commit.com/)
[![Docker](https://github.com/Chisanan232/abstract-backend/actions/workflows/rw_docker_operations.yaml/badge.svg)](https://github.com/Chisanan232/abstract-backend/actions/workflows/rw_docker_operations.yaml)
[![Coverage](https://img.shields.io/codecov/c/github/Chisanan232/abstract-backend?logo=codecov)](https://codecov.io/gh/Chisanan232/abstract-backend)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)

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
pip install mcp-backend-message-queue-redis
```

Set `QUEUE_BACKEND=redis` (or the entry-point name) and `load_backend()` will resolve the correct provider at runtime.

## Quick start ⚡️

```python
from abe.backends.queue.loader import load_backend
from abe.backends.queue.consumer import AsyncLoopConsumer


async def process(payload: dict[str, object]) -> None:
    ...


async def main() -> None:
    backend = load_backend()
    consumer = AsyncLoopConsumer(backend, group="billing")
    await consumer.run(process)
```

See `docs/contents/development/architecture/` for diagrams explaining the flow and provider relationships.

## Building providers 🧩

1. Implement the protocols from `abe/types.py` (especially `QueueBackendProtocol`).
2. Expose a `from_env()` constructor for runtime configuration.
3. Register an entry point under `abe.backends.queue` in `pyproject.toml`.
4. Run the contract tests in `test/contract_test/backends/queue/` against your provider.
5. Publish your package to PyPI; users activate it with `pip install` and `QUEUE_BACKEND`.

The showcase at `/docs/src/pages/showcase.tsx` highlights template and reference implementations.

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
