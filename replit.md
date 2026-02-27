# Workspace

## Overview

pnpm workspace monorepo using TypeScript. Each package manages its own dependencies.

## Python Microservices (Лабораторная работа №2)

Three FastAPI microservices located in `services/`:

| Service | Port | Responsibility |
|---------|------|----------------|
| `user_deck` | 8001 | User registration, JWT auth, deck CRUD |
| `card` | 8002 | Card catalog with filtering, 12 seed cards |
| `game` | 8003 | Game creation and state retrieval |

### Python Stack
- **Runtime**: Python 3.11
- **Framework**: FastAPI (async)
- **Auth**: JWT (HMAC-SHA256, custom implementation)
- **Linter**: flake8
- **Type checker**: mypy
- **Formatter**: black
- **Testing**: pytest + FastAPI TestClient
- **Git hooks**: pre-commit (black → flake8 → mypy → pytest)
- **Containerization**: Docker + docker-compose

### Key Commands (per service)
- `PYTHONPATH=. python3 -m pytest tests/ -v` — run unit tests
- `python3 -m flake8 app tests` — lint check
- `python3 -m black app tests` — format code
- `python3 -m mypy app` — type check
- `pre-commit install` — install git hooks
- `uvicorn app.main:app --reload --port <port>` — run locally

### Docker
- `cd services && docker-compose up --build` — start all 3 services

## Stack

- **Monorepo tool**: pnpm workspaces
- **Node.js version**: 24
- **Package manager**: pnpm
- **TypeScript version**: 5.9
- **API framework**: Express 5
- **Database**: PostgreSQL + Drizzle ORM
- **Validation**: Zod (`zod/v4`), `drizzle-zod`
- **API codegen**: Orval (from OpenAPI spec)
- **Build**: esbuild (CJS bundle)

## Key Commands

- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- `pnpm --filter @workspace/api-server run dev` — run API server locally

See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details.
