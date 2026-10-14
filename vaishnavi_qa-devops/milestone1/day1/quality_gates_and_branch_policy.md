# Day 1: Code-Quality Tooling, PR Checklist and Branch Policy

## Tooling in the repo (all free / open-source)

| Concern                   | Tool                          | Config                                                        |
| ------------------------- | ----------------------------- | ------------------------------------------------------------- |
| Python lint               | Flake8 7.x                    | `.flake8` (max line 100, ignores E203/W503, excludes venvs)   |
| Python format             | Black                         | `pyproject.toml` `[tool.black]` (line 100, py311)             |
| JS lint                   | ESLint 8                      | `.eslintrc.json` (recommended + import + prettier)            |
| JS / MD / JSON format     | Prettier 3                    | `.prettierrc.json`, `.prettierignore`                         |
| Inline `<script>` in HTML | `QA/tools/check_inline_js.js` | ESLint does not read HTML, so this parses every inline script |
| Tests                     | pytest                        | `pyproject.toml` `testpaths` (includes `QA/milestone1/tests`) |

Run everything locally:

```bash
npm install
npm run quality            # eslint + black --check + flake8
npx prettier --check .
python -m pytest -q
```

## PR review checklist

Use `docs/PR-REVIEW-CHECKLIST.md`. Milestone 1 adds these items:

- [ ] Any change to a frozen contract (SRS 7.1–7.3) was agreed in stand-up and is reflected in `QA/milestone1/tests` the same day (SRS 12.3).
- [ ] New or changed endpoints show up in Swagger `/docs`.
- [ ] No deployment config, cloud credentials or release scripts were added (deployment is out of scope until after Milestone 4).

## Branch policy

| Branch                        | Purpose                      | Rules                                               |
| ----------------------------- | ---------------------------- | --------------------------------------------------- |
| `main`                        | Milestone sign-off snapshots | PR only, CI green, 1 approval, up to date with base |
| `develop`                     | Integration                  | PR only, CI green                                   |
| `Team-1`, `<intern>_<domain>` | Feature / domain work        | Open a PR to `develop`; CI runs on that PR          |

CI (`.github/workflows/ci.yml`) triggers on push and PR to `main` and `develop`. There is no deploy job.

## Quality gates for Milestone 1 sign-off

1. CI `tests` job is green.
2. CI `code-quality` job is green, or its failures are logged as a defect with an owner (DEF-M1-007).
3. No open Critical defects. Every open High defect has an owner and a target.
4. The integration cycle passes in local `docker-compose.dev.yml`.
5. No deployment activity.

> `docs/QUALITY-GATES.md` mentions "release owner sign-off before deployment". That applies from Milestone 4 onward, not to Milestone 1.
