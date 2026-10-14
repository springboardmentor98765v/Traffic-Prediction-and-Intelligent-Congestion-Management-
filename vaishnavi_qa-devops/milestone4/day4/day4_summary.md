# Milestone 4 Day 4 — Full application testing (live system)

| Suite                                   | What it covers                                                                                                                                                                                                                           | Script                |
| --------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------- |
| Full system (API, 75 checks)            | W1 user journey, W2 operator, W3 admin, W4 alert pipeline, W5 AI insights, W6 cross-service consistency, W7 negative/security, W8 pages                                                                                                  | `full_system_test.py` |
| Selenium UI (cross-browser, responsive) | U1 every page at desktop/tablet/mobile (loads, no horizontal scroll, viewport meta, JS errors); U2 login through the UI with CAPTCHA → dashboard → all pages → logout → page guard; U3 wrong CAPTCHA/password; U4 operator/admin routing | `selenium_ui_test.py` |

Run (or Actions → Live QA → `full-system` / `ui-selenium`):

```
python QA/milestone4/day4/full_system_test.py --report QA/milestone4/day4/full_system_test_report.md --json QA/milestone4/day4/full_system_results.json
python QA/milestone4/day4/selenium_ui_test.py --browsers chrome,firefox,edge --report QA/milestone4/day4/selenium_ui_report.md --shots QA/milestone4/day4/screenshots
```

Keep the JSON: Day 6 compares against it.

## Rehearsal results (2026-10-07, local)

- Full system: **75/75 passed** against the production images.
- Selenium: Chrome 55/59, Firefox 31/31, Edge 29/31. Every login, role-routing, logout,
  page-guard and responsive check (no horizontal scroll at 1366/768/390 px) passed. The
  failures were JS console errors: DEF-M4-011 (Login calls alerts before sign-in — real)
  and the local dev analytics container being down (DEF-M4-016, environment only).

## Pending (live)

- [ ] Both suites against Render; reports and screenshots committed here
- [ ] Carried-over M3 defects confirmed live (DEF-M3-005/024/025 passed in rehearsal)
