# Cyverdarian CTFd theme

A separate theme for **CTFd 3.8.8**, copied from the installed `core` theme. It uses the same Jinja2 templates, Bootstrap 5, Alpine.js, CTFd JavaScript SDK, ECharts, and Vite 3 build. The supplied Home, Challenges, Scoreboard, and Player Profile references guide its charcoal surfaces, lime accent, spacing, branding, cards, and typography.

## Build and activate

From the repository root:

```powershell
cd CTFd/themes/cyverdarian
npm ci
npm run build
npm run lint
```

Use the repository's Node version (`.node-version`) when available. `npm run dev` watches sources and rebuilds files; Flask serves the result. This is a build watcher, not a Vite hot-reload server. No new runtime dependencies were introduced.

The production `static/` assets and Vite manifest are included. Copy the entire `cyverdarian` directory into `CTFd/themes/` on the server. Exclude `node_modules` and the optional `tests` directory from a deployment package. Restart the CTFd workers after deploying rebuilt assets so cached manifests are refreshed.

In **Admin → Config → Theme**, select **cyverdarian**, then save. Re-select **core** to roll back. The theme has not been selected in your existing database by this implementation.

For Docker, ensure the theme is included in the image or theme volume, then rebuild/restart using your normal deployment process. CTFd's backend and database require no migration for this theme.

## What changed

- Shared dark tokens, native sans typography, responsive cards, focus indicators, a skip link, reduced-motion support, and consistent form/table/modal treatments.
- Home hero and supplied mascot, AIM and LVCC footer marks. Optimized copies are included locally; original image files are untouched.
- Navigation retains page/plugin menu entries, account-visibility conditions, language changes, unread notifications, profile, settings, team, admin, and logout controls. Account links use a dropdown on desktop and mobile.
- Login and registration reuse their original WTForms, nonce, OAuth link, custom fields, error messages, and policy links.
- Challenge cards show actual categories, values, solves, and solved status. Category pills, text search, and completion progress use the existing challenge response. Custom sorting and tag classes remain supported.
- Challenge details retain Bootstrap's modal controller and CTFd's original tabs, flag submission, attempts, hints, files, connection info, solutions, reviews, share and next-challenge hooks.
- Scoreboard retains actual standings, bracket selection, score history and the stock five-minute polling interval. The chart uses the reference's stepped lines and palette.
- Public/private user and team profiles retain metadata, awards, solves, history, privacy conditions and team captain controls. User profiles gain category panels; graph initialization handles unloaded data and zero attempts.
- All copied base templates and assets remain inside this theme. **No CTFd backend, core theme, API, database, authentication, scoring or validation file was modified.** The only existing repository file changed is `.gitignore`, to allow tracking the new theme.

`FILES.md` is the exact file inventory, including inherited files and compiled output; it also identifies customized files relative to `core`.

## Content and compatibility

- The home hero is displayed only at `/`; existing home Page content is rendered beneath it. If that content contains CTFd's default logo/welcome block or another hero, edit the index Page in Admin → Pages to avoid duplicate introductory content. Other Pages, including Rules, remain editable normally. A Rules navigation link appears when the corresponding published menu Page exists; the theme does not create live Pages.
- Existing configured logos take precedence over the bundled navigation branding. Header/footer injections and plugin CSS/JS still run and may override this theme. Review old theme injections when enabling it.
- The design is intentionally dark. The stock light/dark toggle is removed from this theme, while locale support is retained.
- Rankings follow the configured user/team mode; CTFd does not offer two independent leaderboards through this page. Unsupported reference columns such as institution, total solves and last-solve age are not fabricated. Category profile bars represent the share of the profile's recorded solves, not all available challenge totals.
- Challenge detail windows retain the standard accessible modal interaction instead of the reference's permanently docked panel. The theme configuration's small/large/extra-large window choices remain available; the default window is 660 px wide and adapts to smaller displays.
- Standard and bundled dynamic challenges are tested. Third-party plugins retain the same integration points but require checking in the deployed instance, especially plugins shipping their own markup or CSS. External OAuth/email services were not exercised.
- Vite reports its inherited ECharts chunk above 500 KiB (about 570 KiB, 193 KiB gzip). The build succeeds; the chart remains its existing separate chunk.

## Repeatable isolated browser checks

`tests/preview.py` creates an **in-memory test database** using the existing repository test helpers, eight challenges including a dynamic challenge, a player/team, a hint, an attachment and a notification. It binds only to `127.0.0.1:5080`; logs and an attachment go under ignored `.data/`. It never connects to the configured production database. Do not deploy this development preview as a public server.

From the repository root, using a Python environment with `requirements.txt` installed:

```powershell
python CTFd/themes/cyverdarian/tests/preview.py
```

In another terminal, with Playwright and its Chromium browser installed for QA:

```powershell
node CTFd/themes/cyverdarian/tests/browser.cjs
```

If Playwright is installed outside Node's module search path, set `PLAYWRIGHT_MODULE` to its absolute module path. This is an optional test tool, not a theme dependency. Stop and restart the preview between runs to reset the fixtures. Repeat both commands with `--teams` to exercise team mode and captain controls.

The suite checks routes, login/registration, filters/search, incorrect/correct flags, solved refresh, a dynamic flag, hint display, attachment download, deep links, keyboard modal dismissal, mobile navigation, browser errors, and overflow at 1440/768/390 px. Screenshots are written under `.data/`. Test data and browser screenshots are excluded from Git.
