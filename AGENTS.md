# PTM Project Guide

This repository is a Django app for PTM operations, with multiple feature apps and a Heroku-ready deployment setup.

## Project map

- Core Django project: [ptm/settings.py](ptm/settings.py), [ptm/urls.py](ptm/urls.py)
- Main apps: [principal](principal), [cadptm](cadptm), [cadferramentas](cadferramentas), [pontoele](pontoele)
- Templates: [templates](templates) plus per-app template folders
- Static assets: [static](static), [staticfiles](staticfiles)
- Media uploads: [media](media)
- Deployment config: [Procfile](Procfile), [heroku.yml](heroku.yml), [runtime.txt](runtime.txt), [Dockerfile](Dockerfile)
- Heroku workflow: [.github/skills/heroku-deploy-tpmdsa/SKILL.md](.github/skills/heroku-deploy-tpmdsa/SKILL.md)

## Working conventions

- Prefer the existing Django app structure and naming conventions over introducing new patterns.
- Keep model, view, URL, form, and template changes inside the relevant app.
- When changing models, consider migration impact and keep migrations consistent.
- Local development uses SQLite; production uses PostgreSQL when DATABASE_URL is present. See [ptm/settings.py](ptm/settings.py).
- Keep static/media handling consistent with the project settings and the existing templates.

## Validation commands

Run the narrowest relevant command for the change:

- `python manage.py check`
- `python manage.py test`
- `python manage.py makemigrations --check`
- `python manage.py migrate`
- `python manage.py runserver`

## Deployment notes

- The repo is configured for Heroku deployment and includes a dedicated deploy skill at [.github/skills/heroku-deploy-tpmdsa/SKILL.md](.github/skills/heroku-deploy-tpmdsa/SKILL.md).
- Do not assume SQLite is safe in production; verify DATABASE_URL and Postgres-backed runtime behavior before shipping.
- Validate the authenticated app flow, not just the homepage, after deployment changes.

## Preferred agent behavior

- Read the relevant app files before editing.
- Keep changes minimal and scoped to the bug or feature.
- Prefer repo-native commands and existing patterns over ad hoc conventions.
- Summarize any follow-up work, migrations, or deployment risk clearly after the change.
