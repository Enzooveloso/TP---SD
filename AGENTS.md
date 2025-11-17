# Repository Guidelines

## Project Structure & Module Organization
- `manage.py` is the entry point; Django settings and URLs live in `config/`.
- Domain logic, forms, views, URLs, signals, and migrations stay in `core/`; templates are under `templates/`, and uploaded PDFs land in `media/`.
- Container setup is defined in `Dockerfile` and `docker-compose.yml`; environment defaults sit in `.env.example`.

## Build, Test, and Development Commands
- Start full stack (PostgreSQL + app): `docker-compose up --build` (applies migrations automatically via web service command).
- Run database migrations after model changes: `docker-compose exec web poetry run python manage.py migrate`.
- Create admin user: `docker-compose exec web poetry run python manage.py createsuperuser`.
- Local dev without Docker (Postgres running): `poetry install` then `poetry run python manage.py runserver 0.0.0.0:8000`.
- Run tests: `docker-compose exec web poetry run python manage.py test` (or `poetry run python manage.py test` locally).

## Coding Style & Naming Conventions
- Python 3.12 with Django 5.2; use 4-space indentation and standard `black`-style spacing even though the formatter is not enforced here.
- Models/Forms/Views use `PascalCase` for classes, `snake_case` for fields/functions, and template blocks follow Django naming (`block content`, etc.).
- Keep settings driven by environment variables via `python-decouple`; never hardcode secrets—update `.env.example` when adding new config.
- Prefer explicit imports, small views, and template inheritance (`base.html`) to avoid duplication.

## Testing Guidelines
- Use Django’s `TestCase`/`SimpleTestCase`; place unit tests in `core/tests.py` or `core/tests/` with filenames like `test_models.py`, `test_views.py`.
- Name test methods `test_<behavior>` and isolate database expectations with factories/fixtures as needed.
- Add migration tests when altering schema: ensure new migrations are generated and committed.

## Commit & Pull Request Guidelines
- Follow the existing Conventional Commit style seen in history (`docs: ...`, `refactor: ...`, `style: ...`, `build: ...`); keep subjects short and in the imperative.
- Include relevant artifacts in PRs: description of change, steps to reproduce/verify, screenshots for UI, and linked issues or Trello tickets.
- Note any database migrations or new environment variables in the PR body; remind reviewers to run `migrate` when needed.
- Keep diffs focused and self-contained; prefer smaller PRs with clear scope.

## Security & Configuration Tips
- Copy `.env.example` to `.env` for local/dev; rotate `SECRET_KEY` and database credentials for production.
- Uploaded files persist in `media/`; avoid committing this folder—use it only for runtime storage.
- Ensure debug settings are off in production and `ALLOWED_HOSTS` is configured before deployment.
