---
name: heroku-deploy-tpmdsa
description: 'Deploy the PTM Django project to the Heroku app tpmdsa, including safe code deploys, Postgres-backed production checks, and SQLite-to-Heroku data migration when local data must be preserved.'
argument-hint: 'What should be deployed or validated in tpmdsa?'
---

# Heroku Deploy TPMSDA

## When to Use
- Deploy updates from this PTM workspace to the Heroku app tpmdsa
- Validate whether a Heroku deploy completed correctly
- Migrate local SQLite data into the Heroku Postgres database without losing existing records
- Investigate Heroku runtime issues such as login failures, missing sessions, or release problems

## Project Facts
- Heroku app name: tpmdsa
- Git remote already used for deploys: heroku
- Normal deploy path: git push heroku main
- Production must use Postgres, not SQLite
- Local backup file previously used: db.sqlite3.pre-heroku-backup
- UTF-8 fixture previously used for data migration: heroku_data_utf8.json

## Standard Deploy Procedure
1. Confirm the project is in the PTM workspace and review the intended local changes.
2. Run the narrowest relevant validation available before deploy.
3. Verify that the Heroku app is reachable through the configured remote.
4. Stage the intended files only.
5. Create a deploy commit.
6. Push with git push heroku main.
7. Validate the result with Heroku release status, dyno status, and one application-level check.

## Data Safety Rules
- Never assume SQLite on Heroku is persistent.
- Before any data migration, preserve the local database with a copy of db.sqlite3.
- Do not create a fresh empty production data state if the local SQLite database contains authoritative records.
- Avoid sending Heroku API keys or tokens through chat; prefer the already authenticated local CLI session.

## SQLite To Heroku Postgres Migration Procedure
1. Copy the local SQLite database to a backup file before changing anything.
2. Record local row counts for key models so the migration can be verified afterward.
3. Ensure the Heroku app has a Postgres addon and a DATABASE_URL.
4. Run Django migrations against the Heroku database.
5. Generate a UTF-8 fixture from the local SQLite database.
6. Load that fixture into the Heroku Postgres database.
7. Recount the same key models in Heroku Postgres.
8. Test a real authenticated workflow, not just the homepage.

## Recommended Validation Checks
- heroku releases -a tpmdsa
- heroku ps -a tpmdsa
- Heroku logs if a route fails or a release command aborts
- Login flow and protected route: /ptmdsa/cadptm/
- Post-migration record counts for:
  - auth_user
  - cadptm_patrimonio
  - cadferramentas_ferramenta
  - pontoele_servidor

## Failure Signatures
- Error 500 immediately after login can indicate missing session tables or an ephemeral SQLite deployment.
- Missing DATABASE_URL or no Postgres addon means production is not configured for persistent data.
- Successful homepage load does not prove authenticated flows or database writes are working.

## Completion Criteria
- The intended code is deployed to tpmdsa.
- The dyno is up.
- The release command completed successfully.
- The authenticated target route opens without 500 errors.
- If data migration was required, Heroku row counts match the local SQLite baseline for the tracked models.

## Example Prompts
- Deploy the current PTM changes to tpmdsa and validate the release.
- Push this Django update to Heroku and check the login flow.
- Move the local SQLite data into the Heroku Postgres database without losing records.
- Diagnose a Heroku login error in tpmdsa after a deploy.