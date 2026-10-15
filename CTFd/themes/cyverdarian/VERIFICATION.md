# Verification

Tested on this repository's CTFd 3.8.8, with its pinned Python requirements, Vite 3.0.5, and headless Chromium against isolated in-memory SQLite fixtures.

- Production build: passed, 678 modules transformed.
- Asset formatting check: passed.
- Every theme Jinja template: compiled in CTFd's actual sandbox.
- User-mode and team-mode browser suites: passed, with no browser JavaScript errors.
- Desktop, tablet and mobile: 1440, 768 and 390 px; no page-level horizontal overflow across the tested home, challenge, scoreboard, user profile and notification routes.
- Guest login and registration layouts checked at all three widths.
- Real login and registration, category filtering, text search, incorrect/correct flags and solved-card refresh passed.
- Standard and dynamic challenge submissions passed through the unchanged CTFd APIs.
- Hint disclosure, attachment download, direct challenge links, keyboard dismissal and mobile account navigation passed.
- Public/private team profiles, team listing and captain edit dialog passed at desktop/mobile sizes.

Fixtures and screenshots are in ignored `.data/`; repeatable runners are in `tests/`. No existing database was modified or theme selection changed.

Remaining deployment verification: third-party plugins, external OAuth/email providers, and existing admin Page content or header/footer injections. The inherited ECharts bundle produces Vite's >500 KiB chunk warning; this does not fail the build. The theme is based specifically on the installed 3.8.8 templates and should be reviewed when upgrading CTFd.
