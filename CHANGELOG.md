# 3.7.5 / 2024-12-27

**Security**

- Change confirmation and reset password emails to be single use instead of only expiring in 30 minutes

**General**

- Fix issue where users could set their own bracket after registration
- If a user or team do not have a password set we allow setting a password without providing a previous password confirmation
- Fix issue where dynamic challenges did not return their attribution over the API
- Language selection is now available in the main theme navigation bar

**Admin Panel**

- A point breakdown graph showing the amount of challenge points allocated to each category has been added to the Admin Panel
- Bracket ID and Bracket Name have been added to CSV scoreboard exports
- Fix issue with certain interactions in the Media Library

**API**

- Swagger specification has been updated to properly validate
- `/api/v1/flags/types` and `/api/v1/flags/types/<type_name>` have been seperated into two seperate controllers

**Deployment**

- IP Tracking has been updated to only occur if we have not seen the IP before or on state changing methods
- Bump dependencies for `cmarkgfm` and `jinja2`

# 3.7.4 / 2024-10-08

**Security**

- Validate email length to be less than 320 chars to prevent Denial of Service in email validation

**General**

- Add attribution field to Challenges

**Admin Panel**

- Display brackets in the Admin Panel

**Themes**

- Display brackets for users/teams on listing pages and public/private pages
- Fix miscellaneous issues in core-beta
- Adds dark mode to core-beta theme
- Fix issue with long titles in challenge buttons
- Adds `type` and `extra` arguments to `Assets.js()` and default `defer` to `False` as `type="module"` automatically implies defer
- ECharts behavior for some graphs in core-beta can now be overriden using the following window objects `window.scoreboardChartOptions`, `window.teamScoreGraphChartOptions`, `window.userScoreGraphChartOptions`
- Update the scoreboard score graph to reflect the current active bracket changes

**Deployment**

- Add `.gitattributes` to keep LF line endings on .sh files under Windows
- Fix issues where None values are not cast to empty string
- Bump dependencies for `pybluemonday`, `requests`, and `boto3`

# 3.7.3 / 2024-07-24

**Security**

- Fix issue where challenge solves and account names could be seen despite accounts not being visible

**Admin Panel**

- Add a Localization section in the Config Panel
- Add the Default Language config in the Admin Panel to allow admins to configure a default language
  - Previously CTFd would default to an auto-detected language specified by the user's browser. This setting allows for that default to be set by the admin instead of auto-detected.

**Translations**

- Fix issue where Simplified Chinese would be used instead of Traditional Chinese
- Update the language names for Simplified Chinese and Traditional Chinese for clarity
- Update Vietnamese translation
- Add Catalan translation

# 3.7.2 / 2024-06-18

**Security**

- Patches an issue where on certain browsers flags could be leaked with admin interaction on a malicious page

**API**

- Disable returning 404s in listing pages with pagination
  - Instead of returning 404 these pages will now return 200
  - For API endpoints, the response will be a 200 with an empty listing instead of a 404

**Deployment**

- CTFd will now add the `Cross-Origin-Opener-Policy` response header to all responses with the default value of `same-origin-allow-popups`
- Add `CROSS_ORIGIN_OPENER_POLICY` setting to control the `Cross-Origin-Opener-Policy` header

# 3.7.1 / 2024-05-31

**Admin Panel**

- The styling of the Config Panel has been updated to better organize different settings
- When switching user modes via the Admin Panel, all teams will now be removed
- Fix issues where importing CSVs comprised of JSON entries would fail
- Add `serializeJSON` function back into the Admin Panel

**API**

- The `/api/v1/exports/raw` API endpoint has been added to allow for exports to be generated via the API
- Update the ScoreboardDetail endpoint (`/api/v1/scoreboard/top/<count>`) to return account URL, score, and bracket
- Add a query parameter to ScoreboardDetail endpoint (`/api/v1/scoreboard/top/<count>`) to filter by bracket
- Return `function` field for DynamicValue challenges data read

**General**

- Add Italian and Vietnamese languages
- Switch to Crowdin for translations

**Themes**

- Add `defer` parameter to `Assets.js()` to allow controlling the defer attribute of inserted `<script>` tags

**Plugins**

- Plugins can now define a `config` entry in `config.json` to define a template to embed into the Config Panel
- Add the `make_cache_key_with_query_string` to allow for caching based on query string arguments

**Deployment**

- MariaDB version provided in docker-compose.yml has been updated to `10.11`
- Static assets (theme files, static files) will now return a Cache-Control header with a `max-age` of 3600
- Add the `/debug` endpoint to show CTFd debugging information
  - Currently showing the IP address that CTFd is seeing for the request and the request headers
  - `/debug` will only be enabled if the `SAFE_MODE` config is enabled

# 3.7.0 / 2024-02-26

**General**

- Add ability for users to generate social share links after solving a challenge
  - After solving a challenge users can click a "share" button which can generate Twitter, Facebook, LinkedIn links
- Add Scoreboard Brackets feature to have multiple sub-scoreboards within the main scoreboard
  - Admins can add a bracket for users/teams which must be selected during the registration process. Within the scoreboard, accounts can be organized by bracket in addition to seeing the full list
- Calculate a files sha1sum on upload for future local change detection purposes
- Allow API clients (CTFd, ctfcli, etc) to control the location of an uploaded file
- Allow challenge CSVs to contain JSON in the hints and flags columns so that admins can import more complex data
- Fix issue where hints could not be unlocked during freeze time
- Use the CTF name to be the default index page name

**API**

- Add `bracket_name` and `bracket_id` to `/api/v1/scoreboard`
- Add `sha1sum` to `GET /api/v1/files`
- Add `location` to `POST /api/v1/files`

**Plugins**

- Add ability to control the link target for a page (i.e. open in a new tab) via `register_user_page_menu_bar()`
- Add `uploaders.open()` to open a file from an uploader
- Adds the optional path field to the `Uploaders.upload()` method to control where files get uploaded to

**Themes**

- Allow customization of the `<meta>` tag & page title via template files
- Exposes `unix_time_to_utc()` as a Jinja filter

**Admin Panel**

- Migrate Admin Panel from webpack to Vite
- Adds Alpine to Admin Panel for plugins to use to add interactivity

**Deployment**

- Update base image to `python:3.11-slim-bookworm`
- Added prefix option to S3 uploader under `AWS_S3_CUSTOM_PREFIX`
  - This allows CTFd to store files under a folder of an S3 bucket
- Raise exception if a built-in config is defined in the extra config section in config.ini
- CTFd will wait for an import to complete before starting
  - This tries to address issues where starting CTFd during an import can interfere with the import
- Add Pillow version 10.1.0 as a dependency
- Update boto3 version to 1.34.39
- Update isort version to 5.13.2
- Update dataset version to 1.6.2

# 3.6.1 / 2023-12-12

**Security**

- Fix an issue where users could bypass Score Visibility and see a user's score/place when not allowed by Admins

**General**

- Add Slovak, Japanese, Brazillian Portugese translations
- Update Chinese translation
- Fix Dynamic challenges not showing the Next Challenge

**API**

- Add `email` as a `field` to query to `/api/v1/users` and `/api/v1/teams` to allow searching via email address for Admins
- Accept multipart/form-data with token auth for file upload to `/api/v1/files`
- Always allow a user/team to see their own score when querying their own self endpoints regardless of Score Visibility
  - The rationale for this is that a user can always calculate their score regardless of any setting because they can simply sum all of their challenges

**Admin Panel**

- Fix an issue where polymorphic tables (i.e. solves) could not be CSV exported correctly

**Themes**

- When using core-beta, `meta` tags can now be inserted into pages from `render_template()` calls

**Deployment**

- Fix an issue where S3 uploads would not work if the server's timezone was not set to UTC
- Update gevent dependency to `23.9.1`

# 3.6.0 / 2023-08-21

**General**

- Translations support for Spanish, Polish, German, Chinese
  - If you wish to fix or maintain a language translation please join at CTFd's public [POEditor page](https://poeditor.com/join/project/p5jhdcrlm7).
- Add a total user registration limit option
- Dynamic value challenges can now choose between linear and logarithmic decay functions
- Free hints are now visible by unauthenticated users if challenges are visible by unauthenticated users
- Fix issue where a custom field named affiliation or website prevented registration
  - No longer special case "Affiliation" or "Website" as custom field titles. Previously custom fields with those titles would set the user's affiliation or website but this behavior has been removed.

**Admin Panel**

- Challenge Preview has been improved to support arbitrary custom themes
- Long flags in the Admin Panel are now truncated but can be expanded and copied
- Add UI to mark incorrect submissions as correct
  - Add the `discard` type for submissions
  - Add `PATCH /api/v1/submissions/[submission_id]` to mark submissions as correct
- Add section in the Config Panel to configure `HTML_SANITIZATION`
  - Setting `HTML_SANITIZATION` to true in `config.ini` cannot be disabled via the Admin Panel
- Add wildcard for email whitelisting

**Deployment**

- Add new envvar `SKIP_DB_PING` to instruct the CTFd Docker image to not test if the database server is available
- Add new config `AWS_S3_ADDRESSING_STYLE`
  - Support selecting the [S3 addressing style](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-bucket-intro.html#access-bucket-console-ex). It defaults to "auto" as when it's not set, but can also be set to `virtual` or `path`
- Add new config `AWS_S3_CUSTOM_DOMAIN` which specifies a domain that replaces the default one in presigned download URLs
  - Required for certain S3 implementations
- Flask and Werkzeug have been upgraded to v2.0.3. Other dependencies have been updated for compatability.
- SQLAlchemy has been updated to v1.4.
- PyMySQL has been upgraded to v1.0.2.
- The `flask` cli tool is now offered as an alternative to the `manage.py` script.
- gzip compression is now enabled in the provided nginx configuration

**API**

- API tokens now have a description field
- API tokens now start with a `ctfd_` prefix to make them easier to identify
- `GET /api/v1/hints/[hint_id]` will now return hint information for free hints for unauthenticated users if challenges are visible

**Themes**

- core-beta is now provided in all CTFd instances
- core-beta is the default theme during setup

# 3.5.3 / 2023-06-08

**Deployment**

- Fixed permissions error in Dockerfile
- Bump dependencies for pybluemonday

# 3.5.2 / 2023-05-01

**General**

- Generate cachable S3 URLs by rounding time down to the previous hour to generate a consistent URL
- Change email whitelist error message to not include the list of allowed domains
- Clean up the language for confirming the password on team password change
- Fix issue where dynamic challenges break if the decay is 0 and prevent users from adding a decay limit of 0 to dynamic value challenges

**Admin Panel**

- Adds support for admins to control `robots.txt`
- Clean up the aesthetics for the 'Pause CTF' and 'View After CTF' configs
- Replaced TLS and SSL checkbox text to match the defaults used by Mozilla Thunderbird to eliminate confusion when configuring SMTP

**Deployment**

- Slim down Docker image by removing several dependencies not needed for production usage
  - The image size has been reduced from 648MB to 398MB
- In the Docker image run CTFd in a virtual environment located at `/opt/venv`
- Add freezegun to application dependencies
- Bump dependencies for pybluemonday, redis, SQLAlchemy-Utils, python-geoacumen-city
- Fix race conditions on cache healthcheck
- Fix situations where numeric config items in config.ini could cause CTFd to not start

# 3.5.1 / 2023-01-23

**General**

- The public scoreboard page is no longer shown to users if account visibility is disabled
- Teams created by admins using the normal team creation flow are now hidden by default
- Redirect users to the team creation page if they access a certain pages before the CTF starts
- Added a notice on the Challenges page to remind Admins if they are in Admins Only mode
- Fixed an issue where users couldn't login to their team even though they were already on the team
- Fixed an issue with scoreboard tie breaking when an award results in a tie
- Fixed the order of solves, fails, and awards to always be in chronological ordering (latest first).
- Fixed an issue where certain custom fields could not be submitted

**Admin Panel**

- Improved the rendering of Admin Panel tables on mobile devices
- Clarified the behavior of Score Visibility with respect to Account Visibility in the Admin Panel help text
- Added user id and user email fields to the user mode scoreboard CSV export
- Add CSV export for `teams+members+fields` which is teams with Custom Field entries and their team members with Custom Field entries
- The import process will now catch all exceptions in the import process to report them in the Admin Panel
- Fixed issue where `field_entries` could not be imported under MariaDB
- Fixed issue where `config` entries sometimes would be recreated for some reason causing an import to fail
- Fixed issue with Firefox caching checkboxes by adding `autocomplete='off'` to Admin Panel pages
- Fixed issue where Next selection for a challenge wouldn't always load in Admin Panel

**API**

- Improve response time of `/api/v1/challenges` and `/api/v1/challenges/[challenge_id]/solves` by caching the solve count data for users and challenges
- Add `HEAD /api/v1/notifications` to get a count of notifications that have happened.
  - This also includes a `since_id` parameter to allow for a notification cursor.
  - Unread notification count can now be tracked by themes that track which notifications a user has read
- Add `since_id` to `GET /api/v1/notifications` to get Notifications that have happened since a specific ID

**Deployment**

- Imports have been disabled when running with a SQLite database backend
  - See https://github.com/CTFd/CTFd/issues/2131
- Added `/healthcheck` endpoint to check if CTFd is ready
- There are now ARM Docker images for OSS CTFd
- Bump dependencies for passlib, bcrypt, requests, gunicorn, gevent, python-geoacumen-city, cmarkgfm
- Properly load `SAFE_MODE` config from environment variable
- The `AWS_S3_REGION` config has been added to allow specifying an S3 region. The default is `us-east-1`
- Add individual DATABASE config keys as an alternative to `DATABASE_URL`
  - `DATABASE_PROTOCOL`: SQLAlchemy DB protocol (+ driver, optionally)
  - `DATABASE_USER`: Username to access DB server with
  - `DATABASE_PASSWORD`: Password to access DB server with
  - `DATABASE_HOST`: Hostname of the DB server to access
  - `DATABASE_PORT`: Port of the DB server to access
  - `DATABASE_NAME`: Name of the database to use
- Add individual REDIS config keys as an alternative to `REDIS_URL`
  - `REDIS_PROTOCOL`: Protocol to access Redis server with (either redis or rediss)
  - `REDIS_USER`: Username to access Redis server with
  - `REDIS_PASSWORD`: Password to access Redis server with
  - `REDIS_HOST`: Hostname of the Redis server to access
  - `REDIS_PORT`: Port of the Redis server to access
  - `REDIS_DB`: Numeric ID of the database to access

**Plugins**

- Adds support for `config.json` to have multiple paths to add to the Plugins dropdown in the Admin Panel
- Plugins and their migrations now have access to the `get_all_tables` and `get_columns_for_table` functions
- Email sending functions have now been seperated into classes that can be customized via plugins.
  - Add `CTFd.utils.email.providers.EmailProvider`
  - Add `CTFd.utils.email.providers.mailgun.MailgunEmailProvider`
  - Add `CTFd.utils.email.providers.smtp.SMTPEmailProvider`
  - Deprecate `CTFd.utils.email.mailgun.sendmail`
  - Deprecate `CTFd.utils.email.smtp.sendmail`

**Themes**

- The beta interface `Assets.manifest_css` has been removed
- `event-source-polyfill` is now pinned to 1.0.19.
  - See https://github.com/CTFd/CTFd/issues/2159
  - Note that we will not be using this polyfill starting with the `core-beta` theme.
- Add autofocus to text fields on authentication pages

# 3.5.0 / 2022-05-09

**General**

- Add a next challenge recommendation to challenges
- Add support for only viewing hints after unlocking another hint
- Add size checking and recommendation for images uploaded during setup

**Admin Panel**

- Imports now happen in the background so that admins can watch the status of the import
  - Add progress tracking to backup/export importing
  - Add `GET /admin/import` to see status of import
  - The public user facing portion of CTFd is now disabled during imports
- Fix issue where custom field entries for Users and Teams would be misaligned in the scoreboard CSV export
- Show admins the email server error message when email sending fails
- Fix issue where the current theme cannot be found in list of themes
- Fix page preview so that it accounts for the provided format
- Add links from User/Team Profile IP addresses to a User IP address search page
- Add city geolocation to Team Profile IP addresses

**API**

- Add the `count` meta field to the following endpoints:
  - `/api/v1/users/me/solves`
  - `/api/v1/users/me/fails`
  - `/api/v1/users/me/awards`
  - `/api/v1/teams/me/awards`
  - `/api/v1/users/[user_id]/solves`
  - `/api/v1/users/[user_id]/fails`
  - `/api/v1/users/[user_id]/awards`
  - `/api/v1/teams/[team_id]/solves`
  - `/api/v1/teams/[team_id]/awards`
- Improve speed of `/api/v1/teams/me/fails`
- Improve speed of `/api/v1/teams/[team_id]/fails`
- Improve speed of `/api/v1/users/me/fails`
- Improve speed of `/api/v1/users/[user_id]/fails`

**Deployment**

- Use Python 3.9 as the default Python version
- Prevent any possible usage of an already existing session ID by checking for duplicates during during session ID generation
- No longer install `python3-dev` in Dockerfile
- docker-compose.yml now uses `nginx:stable` as the image for nginx

**Plugins**

- `CTFd._internal.challenge.render` and `CTFd._internal.challenge.renderer` in the `view.js` Challenge type file has been deprecated. Instead Challenge plugins should refer to the `challenge.html` attribute provided by the API. Essentially CTFd is moving to having markdown & HTML rendered by the server instead of rendering on the client.

**Themes**

- Create the [`core-beta` theme](https://github.com/CTFd/core-beta) and begin documenting the creation of themes using Vite
- Add `userName` and `userEmail` to the CTFd init object in `base.html` for easier integration with other JavaScript code
- Add `teamId` and `teamName` to the CTFd init object in `base.html` for easier integration with other JavaScript code
- Adds the `Assets` constant to access front end assets from Jinja templates
- Adds a `views.themes_beta` route to avoid the `.dev`/`.min` extension being added automatically to frontend asset urls

**Miscellaneous**

- Fix double logging in `log()` function
- Add `--delete_import_on_finish` to `python manage.py import_ctf`
- Fix issue where `field_entries` table could not be imported when moving between MySQL and MariaDB

# 3.4.3 / 2022-03-07

**Security**

- Bump cmarkgfm to 0.8.0 to resolve CVE-2022-24724. Copied entry from 3.4.2 since 3.4.2 introduced a bug that prevented writing raw HTML.

**General**

- Fix issue where raw HTML would not be rendered in markdown

# 3.4.2 / 2022-03-07

**Security**

- Bump cmarkgfm to 0.8.0 to resolve CVE-2022-24724

**General**

- Fix issue where unauthed users couldn't download challenge files after CTF end but viewing after CTF was enabled

# 3.4.1 / 2022-02-19

**General**

- Make session cookies persist in the browser after close
- Fix issue where all-numeric registration codes wouldn't work
- Fix issue where a user's session isn't cleared properly after they are deleted by an admin
- Fix issue where CTF end time couldn't be set during setup

**API**

- Improved speed of the `/api/v1/challenges/[challenge_id]/solves` endpoint
- Document API authentication and `Content-Type` header requirement
- Add nested `UserSchema` and `TeamSchema` to `SubmissionSchema` for easier access to account name

**Admin Panel**

- Improve CSV import error reporting and validation
- Fix non-clickable checkbox label in user creation form in Admin Panel
- Allow submissions per minute ratelimit to be configurable in Admin Panel
- Add a link in the Pages Editor to the [Page Variables documentation page](https://docs.ctfd.io/docs/pages/variables/)

**Themes**

- Fix issue where invalid `theme_settings` can cause broken frontend
- Replace `node-sass` with `sass` and upgrade `sass-loader`

**Deployment**

- Serve all assets from CTFd regardless of internet availability (i.e. fonts and font-awesome)
- Fix regression in `REVERSE_PROXY` to allow comma seperated integers
- Bump `flask-restx` to 0.5.1
- Bump `pybluemonday` to 0.0.9
- Added support for S3 signature version 4 authentication to support alternative S3 buckets (Google Cloud Storage, DigitalOcean Spaces, etc)

**Miscellaneous**

- Add a Github Actions job to publish Docker images to Dockerhub and ghcr

# 3.4.0 / 2021-08-11

**General**

- Added the ability to have Challenge Topics
  - Challenge Topics are small topic strings which are only visible to Admins
  - They should denote what topics a given challenge involves
- Added `connection_info` to Challenges to allow Admins to more easily specify the connection info for a challenge
- Added ability to import CSVs of users, teams, and challenges
- Added ability to limit the total number of teams
- Pages now have access to variables `ctf_name`, `ctf_description`, `ctf_start`, `ctf_end`, `ctf_freeze`. (e.g. `{{ ctf_name }}`)
- IP Addresses in the Admin Panel will now show the city of the IP address as well as the country
- Make User Mode it's own dedicated tab in the setup flow and more clearly explain what each user mode does
- Added the ability to have a registration password
  - Does not currently apply to SSO/auth provider or API based account creation
- Prevent users from participating with challenges if their profile is not complete (i.e. haven't filled out all required custom fields)
- Fixed an issue where admins couldn't see some challenges in the add requirements interface
- Fixed an issue where a challenge couldn't be accessed beacuse it had prerequisites on a deleted challenge
- Fixed an issue where User profiles could not be loaded in the Admin Panel due to missing/invalid Tracking IP addresses
- Fixed an issue where users with authentication provider accoutns would get an error when attempting to login
- Fixed an issue where MajorLeagueCyber config from config.ini was not being respected

**API**

- Added `connection_info` field to `/api/v1/challenges/[challenge_id]`
- Added `/api/v1/topics` for admins to create/delete topics
- Added `/api/v1/challenges/[challenge_id]/topics` for admins to list the topics on a challenge
- `/api/v1/challenges` will now sort by ID as value to better standardize API output with different databases
- `/api/v1/configs` will now provide an error message when provided Config values are too long
- `PATCH /api/v1/teams/[team_id]` will now only let team members be team captain
  - No security issues here, it would just be invalid data.

**Themes**

- CTFd now has the `THEME_FALLBACK` option enabled by default. This allows users to provide incomplete themes. Missing theme files will be provided from the built-in core theme
- CTFd will now pass the title of a Page over to the template when rendering
- No longer show the token type in user settings
- Added `window.BETA_sortChallenges` to `/challenges` so that theme code can more easily define how to sort challenges
  - Note that this functionality is beta because we expect to revamp the entire themes system
- Added `window.updateChallengeBoard` to `/challenges` so that theme code can more easily define when to update challenges
  - Note that this functionality is beta because we expect to revamp the entire themes system
- Added `window.updateScoreboard` to `/scoreboard` so that theme code can more easily define when to update the scoreboard
  - Note that this functionality is beta because we expect to revamp the entire themes system

**Plugins**

- Added `Challenges.plugin_class` to the Challenges model to access the challenge type plugin class from the Model
  - Allows templates to access the plugin class more easily
  - Allows plugins to access the plugin class without having to load the class explicitly

**Admin Panel**

- Reworked the Challenge Requirements UI
  - Officially support the concept of anonymized challenges if prerequisites aren't met
- Added ability for Pages to be written in direct HTML instead of Markdown
- Pages now have access to variables `ctf_name`, `ctf_description`, `ctf_start`, `ctf_end`, `ctf_freeze`
  - `ctf_start`, `ctf_end`, `ctf_freeze` are represented as ISO8601 timestamps
- Make it easier to change the user mode without having to delete all accounts. Instead we will only delete all submissions.
- When in team mode, user pages will now show their team's score instead of their own personal score
- Show a team member's individual score on their team's page
- Made the challenge creation form wider

**Deployment**

- The `THEME_FALLBACK` config is now set to true by default
- Replace installation and usage of `mysqladmin` (specifically `mysqladmin ping`) with a custom Python script
- Bump version of `pybluemonday` to 0.0.7 (fixes HTML sanitization bypasses and allows comments in HTML)
- Bump `pydantic` from 1.5.1 to 1.6.2

**Miscellaneous**

- Make `.dockerignore` ignore `node_modules` in any subdirectory
- Added `solves` and `solved_by_me` fields to the Swagger documentation for Challenges
- Dynamic challenges will now take their initial valuation from the `inital` keyword instead of the previous `value` keyword.
  - This allows ctfcli to manage dynamic challenges. See https://github.com/CTFd/CTFd/issues/1875
- Added a timestamp to a CTFd export's filename
- Deleting uploads under the Filesystem upload provider will now delete the parent folder as well as the target file

# 3.3.1 / 2021-07-15

**Security**

- Fixes an issue where users could join teams without knowing the team password or having a team invite

# 3.3.0 / 2021-03-26

**General**

- Don't require a team for viewing challenges if Challenge visibility is set to public
- Add a `THEME_FALLBACK` config to help develop themes. See **Themes** section for details.

**API**

- Implement a faster `/api/v1/scoreboard` endpoint in Teams Mode
- Add the `solves` item to both `/api/v1/challenges` and `/api/v1/challenges/[challenge_id]` to more easily determine how many solves a challenge has
- Add the `solved_by_me` item to both `/api/v1/challenges` and `/api/v1/challenges/[challenge_id]` to more easily determine if the current account has solved the challenge
- Prevent admins from deleting themselves through `DELETE /api/v1/users/[user_id]`
- Add length checking to some sensitive fields in the Pages and Challenges schemas
- Fix issue where `PATCH /api/v1/users[user_id]` returned a list instead of a dict
- Fix exception that occured on demoting admins through `PATCH /api/v1/users[user_id]`
- Add `team_id` to `GET /api/v1/users` to determine if a user is already in a team
- Provide a more useful error message when using an expired token

**Themes**

- Add a `THEME_FALLBACK` config to help develop themes.
  - `THEME_FALLBACK` will configure CTFd to try to find missing theme files in the default built-in `core` theme.
  - This makes it easier to develop themes or use incomplete themes.
- Allow for one theme to reference and inherit from another theme through approaches like `{% extends "core/page.html" %}`
- Allow for the automatic date rendering format to be overridden by specifying a `data-time-format` attribute.
- Add styling for the `<blockquote>` element.
- Change `users/private.html`, `users/public.html` to show awards before a user gets a solve
- Change `teams/private.html`, `teams/public.html` to show awards before a team gets a solve
- Change `colorHash` function to use HSL color values to avoid generating too light/dark colors
- Fix an issue where hidden users couldn't see their graphing data on their private user page (`/user`)
- Fix scoreboard table identifier to switch between User/Team depending on configured user mode
- Switch the challenges page in core to use the new API information in `/api/v1/challenges` to mark solves and display solve counts
- Switch to using Bootstrap's scss in `core/main.scss` to allow using Bootstrap variables
- Consolidate Jinja error handlers into a single function and better handle issues where error templates can't be found

**Plugins**

- Set plugin migration version after successful migrations
- Fix issue where Page URLs injected into the navbar were relative instead of absolute

**Admin Panel**

- Add User standings as well as Teams standings to the admin scoreboard when in Teams Mode
- Add a UI for adding members to a team from the team's admin page
- Add ability for admins to disable public team creation
- Link directly to users who submitted something in the submissions page if the CTF is in Teams Mode
- Fix Challenge Requirements interface in Admin Panel to not allow empty/null requirements to be added
- Fixed an issue where config times (start, end, freeze times) could not be removed
- Fix an exception that occurred when demoting an Admin user
- Adds a temporary hack for re-enabling Javascript snippets in Flag editor templates. (See #1779)

**Deployment**

- Fix boolean configs from the `config.ini` optional section
- Install `python3-dev` instead of `python-dev` in apt
- Require `pybluemonday` as pip dependency
- Remove `lxml` and `html5lib` from pip dependencies
- Bump `Jinja2` to 2.11.3
- Bump `pip-tools` to 5.4.0

**Miscellaneous**

- Rewrite the HTML santiziation feature (controlled by `HTML_SANITIZATION`) to use the `pybluemonday` library instead of `lxml`/`html5lib`
  - Note that this feature is still in beta
- Cache Docker builds more by copying and installing Python dependencies before copying CTFd
- Change the default emails slightly and rework confirmation email page to make some recommendations clearer
- Use `examplectf.com` as testing/development domain instead of `ctfd.io`
- Fix issue where user's name and email would not appear in logs properly
- Add more linting by also linting with `flake8-comprehensions` and `flake8-bugbear`
- Add `.pyc` files and `__pycache__` to `.dockerignore`

# 3.2.1 / 2020-12-09

- Fixed an issue where Users could not unlock Hints

# 3.2.0 / 2020-12-07

**General**

- Add Team invites.
  - Team invites are links containing a token that allow a user to join a team without knowing the team password
  - Captains can generate invite tokens for their teams
  - Admins can generate Team invite links as well
- Improved Team handling
  - Prevent team joining while already on a team
  - Return 403 instead of 200 for team join/create errors
  - Allow team captains whose teams haven't done anything to disband their team
- Allow for uploading navbar logo, favicon, and index page banner during initial setup
- Fixed issue in teams mode where a user couldn't unlock a hint despite their team having enough points
  - The fix for this is essentially to allow the user's points to go negative
- Imports have been made more stable
  - This is primarily done by killing MySQL processes that are locking metadta
  - This is a subpar approach but it seems to be the only solution to avoid a metadata lock in MySQL. This approach did not appear to be needed under Postgres or SQLite

**API**

- Addition of `POST /api/v1/teams/me/members` to generate invite tokens for teams
- Fixed an issue in `POST /api/v1/awards` where CTFd would 500 when a user could not be found by the provided `user_id`
- `POST /api/v1/unlocks` in teams mode now uses the team's score to determine if a user can purchase a hint
  - Properly check for existing unlocks in teams mode in `POST /api/v1/unlocks`
- `/api/v1/notifications` and `/api/v1/notifications/[notification_id]` now have an html parameter which specifies the rendered content of the notification content

**Themes**

- Add Team Invite icon and Disband Team icon to teams/private.html
- Add teams/invite.html file to handle team joining with invites
- Added syntax highlighting to challenge descriptions, pages, hints, notifications, comments, and markdown editors
  - This is done with `highlight.js` which has been added to `package.json`
- Fix notifications to properly fix/support Markdown and HTML notifications
  - Notifications SQL Model now has an html propery
  - Notifications API schemas now has an html field
- Removed MomentJS (see https://momentjs.com/docs/#/-project-status/) in favor of dayjs
  - dayjs is mostly API compatible with MomentJS. The only major changes were:
    - dayjs always uses browser local time so you don't need to call `.local()`
    - dayjs segments out some MomentJS functionality into plugins which need to be imported in before using those features
- Fixed issue in `challenge.html` where the current attempt count would have a typo
- Fixed issue in `challenge.html` where the max attempts for a challenge would not show if it was set to 1
- Edit donut charts to have easier to read legends and labels
- Make data zoom bars thinner and more transparent
- Add logo, banner, and favicon settings to the setup.html

**Plugins**

- The `auth.register` (`/register`) endpoint now accepts a `?next=` parameter to define where to redirect to after registration
- There is now a `registered_only` decorator to redirect users to `auth.register` (`/register`) instead of `auth.login` (`/login`)
- Don't run `db.create_all()` as much during plugin upgrade or during imports
  - By avoiding this we can let alembic and migrations do more of the table creation work but this means that plugins specifically opt into `app.db.create_all()` and will not implicitly get it through `upgrade()`.
  - This means plugins that run `upgrade()` without a migrations folder (no idea who would do this really) will need to upgrade their code.
- The plugin `upgrade()` function now accepts a `lower` parameter which specifies what lower revision should be used to start from.
  - This is used to support plugin migrations during import so that we can import data directly at the point that the import was taken from
  - `lower="current"` means to use the current revision and `lower=None` would mean to use the absolute base revision (e.g. plugin's first installation)
  - By default this doesn't change `upgrade()` behavior

**Admin Panel**

- Add Favicon uploading to the Admin Panel
- Move Logo uploading to the Theme tab in the Admin Panel
- The challenge left side bar tabs have been rewritten into VueJS components.
  - This fixes a number of issues with the consistency of what data is deleted/edited in the challenge editor
  - This also prevents having to refresh the page in most challenge editing situations
- Fixed a possible bug where the update available alert wouldn't go away on server restart
- Examples for regex flags are now provided
- Wrong submissions has been renamed to Incorrect Submissions
- Graphs in the Admin Statistics page will now scroll with mouse wheel to improve browsing large datasets
- Fixed an issue where Users/Teams could be created with a null password

**Deployment**

- A restart policy set to `always` has been added to nginx in docker-compose
- Rename `requirements.txt` to `requirements.in` and generate `requirements.txt` using `pip-tools` under Python 3.6
- `UPLOAD_PROVIDER` no longer has a default `filesystem` set in config.ini. Instead it is defaulted through `config.py`

**Miscellaneous**

- The `psycopg2` dependency in development.txt has been removed in favor of `psycopg2-binary` which was updated to 2.8.6
- The `moto` dependency in development.txt has been updated to 1.3.16
- Add `pip-tools` to `development.txt`
- Add `import_ctf` and `export_ctf` commands to `manage.py` and deprecate `import.py` and `export.py`
- Override the `MAIL_SERVER` config with the `TESTING_MAIL_SERVER` envvar during tests
- `ping` events in the notification event handler have been fixed to not send duplicates

# 3.1.1 / 2020-09-22

**General**

- Fix notification deliverability when there are multiple tabs open
- Only play notification sounds in the master tab that receives the notification

**Admin Panel**

- Fix issue preventing admins from emailing users through the Admin Panel
- Improve Notification UI
  - Clears notification form after notification submission
  - Add notification to notification list after creation

**Themes**

- Add fix for trying to increment solves when solves are hidden
- Update JS dependencies to fix a transpiliation error preventing optional custom fields from being left empty
  - `@babel/core`, `@babel/preset-env`, `@fortawesome/fontawesome-free`, `babel-loader`, and `@babel/polyfill` were updated but only `@babel/core` needs to be updated to resolve the transpiliation issue
- Remove `console.log` statements from minified production JS
- Compress notification sound and document the compression command

**Miscellaneous**

- Add the ability to override the sender header of email sent via SMTP with the `MAILSENDER_ADDR` config value

# 3.1.0 / 2020-09-08

**General**

- Loosen team password confirmation in team settings to also accept the team captain's password to make it easier to change the team password
- Adds the ability to add custom user and team fields for registration/profile settings.
- Improve Notifications pubsub events system to use a subscriber per server instead of a subscriber per browser. This should improve the reliability of CTFd at higher load and make it easier to deploy the Notifications system

**Admin Panel**

- Add a comments functionality for admins to discuss challenges, users, teams, pages
- Adds a legal section in Configs where users can add a terms of service and privacy policy
- Add a Custom Fields section in Configs where admins can add/edit custom user/team fields
- Move user graphs into a modal for Admin Panel

**API**

- Add `/api/v1/comments` to manipulate and create comments

**Themes**

- Make scoreboard caching only cache the score table instead of the entire page. This is done by caching the specific template section. Refer to #1586, specifically the changes in `scoreboard.html`.
- Add custom field inputs to profile pages (`teams/public.html`, `teams/private.html`, `users/public.html`, `users/private.html`), registration pages (`register.html`), and settings pages (`settings.html`).
  - This is implemented in the core theme with `form.extra` & `user.fields` with a special helper (`render_extra_fields`) defined in `macros/forms.html`. The best way to implement this is to look at how the core theme handles it and copy the relevant behavior.
- Add rel=noopener to external links to prevent tab napping attacks
- Change the registration page to reference links to Terms of Service and Privacy Policy if specified in configuration

**Miscellaneous**

- Make team settings modal larger in the core theme
- Update tests in Github Actions to properly test under MySQL and Postgres
- Make gevent default in serve.py and add a `--disable-gevent` switch in serve.py
- Add `tenacity` library for retrying logic
- Add `pytest-sugar` for slightly prettier pytest output
- Add a `listen()` method to `CTFd.utils.events.EventManager` and `CTFd.utils.events.RedisEventManager`.
  - This method should implement subscription for a CTFd worker to whatever underlying notification system there is. This should be implemented with gevent or a background thread.
  - The `subscribe()` method (which used to implement the functionality of the new `listen()` function) now only handles passing notifications from CTFd to the browser. This should also be implemented with gevent or a background thread.

# 3.0.2 / 2020-08-23

**Admin Panel**

- Fix submission searching in Admin Panel
- Fix update banner being hidden behind navbar

**Plugins**

- Change default `input` & `submit` blocks in `challenge.html` to use the default values specified in the original challenge type plugins

# 3.0.1 / 2020-08-12

**General**

- Fix issue where admins could not see user graphs/api data if score visibility was set to hidden

**Admin Panel**

- Allow the Admin Panel Submissions page to filter by Account IDs, Challenge IDs, and Challenge Names
- Link to correct submissions for challenge from the challenge page

**API**

- Fix regression for creating hints via ctfcli. See #1582 for details. https://github.com/CTFd/CTFd/issues/1582.
- Deprecate `CTFd.api.v1.helpers.models.build_model_filters` and wrap it to `CTFd.utils.helpers.models.build_model_filters`

**Themes**

- Fix team pages to use the correct core errors component

**Plugins**

- Fix issues with previewing challenges under some challenge type plugins

**Deployment**

- Values specified in `config.ini` will now supercede values specified via environment variable. Config behavior is as follows:
  1. Config Key exists in `config.ini` and is set to a value. That value becomes the app config.
  2. Config Key exists in `config.ini` but is set to an empty string. An envvar with the same name is looked up. The envvar's value is used as the app config.
  3. If the envvar is not found, fall back to the default specified value in `config.py`
  4. If there is no default, use None or an empty string

# 3.0.0 / 2020-07-27

## Changelog Summary

The CTFd v3 Changelog represents the changes from v2.5.0 to v3. It is a summarized version of the changes that occured in all CTFd v3 beta/alpha releases.

CTFd v3 contains some breaking changes but many plugins remain compatible. Themes will need some minor changes to be compatible with v3.

These changes are made with great consideration to existing installations and for the health of the overall CTFd project. If you rely on specific behavior, you can always download the last CTFd v2 release on Github. Official plugin/theme updates will be sent to the email addresses on file.

The major changes in CTFd v3 are as follows with the detailed changelog beneath:

- ### Server Side HTML/Markdown Rendering

HTML rendering in some cases (challenge description rendering, hint content rendering) has been moved to the server side. Previously it was rendered by the browser but this led to a lot of duplicated behavior and complexity in some plugins. Rendering that HTML content on the server allows CTFd to take more advantage of theme content and reduce duplicated code across themes.

In addition, HTML sanitization can be enabled on the CTFd installation to prevent the injection of malicious scripts in HTML content.

- ### CommonMark

CTFd now uses [CommonMark](https://commonmark.org/) for HTML/Markdown rendering. This leads to much more consistent rendering of HTML/Markdown content.

In some cases, this can break your HTML output. You can use our [development testing script](https://gist.github.com/ColdHeat/085c47359ab86c18864135a198cbe505) to check if your HTML output will change and correct it accordingly.

- ### Forms, Nonces, Sessions

CTFd no longer directly injects values into the global session object for a theme. You may have used this as `{{ nonce }}` or `{{ id }}`. Instead these values should be accessed via the `Session` global as so: `{{ Session.nonce }}`.

All of the public facing forms in CTFd have been converted to form globals with WTForms. You can access them via the `Form` global in Jinja. For example, `{{ Forms.auth.LoginForm() }}`. A `{{ form.nonce() }}` function is available on all forms for easier access to the CSRF nonce as well.

Old forms will still work if the nonce used in the form is updated to `{{ Session.nonce }}`.

Values provided by configuration and plugins can now be accessed via the `Configs` and `Plugins` globals. For example `{{ Configs.ctf_name }}` and `{{ Plugins.scripts }}`. See the `base.html` file of the core theme to get an idea of how to use these values.

- ### Challenge Type Plugin Enhancements

Challenge type plugins now have better re-useability with the rest of CTFd. Plugin code no longer needs to copy unchanged methods over from the base challenge plugin classes.

In addition, challenge HTML is now rendered on the server side using a new `challenge.html` file provided by the current theme. This means that the theme effectively controls how a challenge should look overall, but the challenge plugin controls the overall content.

- ### Python 3

CTFd v3 is Python 3 only.

- ### Docker image based on Debian

The Docker image used in CTFd is now based on Debian.

- ### config.ini

Instead of editting `config.py` directly, it's now a better idea to edit `config.ini` or provide your configuration via environment variables

## Detailed Changelog

**General**

- CTFd is now Python 3 only
- Render markdown with the CommonMark spec provided by `cmarkgfm`
- HTML/Markdown content is now rendered on the server side in most cases.
  - This includes challenge descriptions, hint content, and page content
- Ability to render markdown stripped of any malicious JavaScript or HTML.
  - Controlled via the `HTML_SANITIZATION` server side configuration value
- Inject `Config`, `User`, `Team`, `Session`, and `Plugin` globals into Jinja
- User sessions no longer store any user-specific attributes.
  - Sessions only store the user's ID, CSRF nonce, and an hmac of the user's password
  - This allows for session invalidation on password changes
- The user facing side of CTFd now has user and team searching
- Accept additional profile fields during registration (affiliation, website, country)
  - This does not add additional inputs. Themes or additional JavaScript can add the form inputs.

**Admin Panel**

- Use EasyMDE as an improved description/text editor for Markdown enabled fields.
- Media Library button now integrated into EasyMDE enabled fields
- VueJS now used as the underlying implementation for the Media Library
- Fix setting theme color in Admin Panel
- Green outline border has been removed from the Admin Panel
- GeoIP support now available for converting IP addresses to guessed countries
- Redesign the challenge creation form to use a radio button with challenge type selection instead of a select input

**API**

- Significant overhauls in API documentation provided by Swagger UI and Swagger json
- Make almost all API endpoints provide filtering and searching capabilities
- Change `GET /api/v1/config/<config_key>` to return structured data according to ConfigSchema
- Admins can no longer ban themselves through `PATCH /api/v1/users/[user_id]`
- Add `html` item for `GET /api/v1/hints/[hint_id]` which contains the rendered HTML of the Hint content
- Remove `content` from `GET /api/v1/hints`

**Themes**

- Themes now have access to the `Configs` global which provides wrapped access to `get_config`.
  - For example, `{{ Configs.ctf_name }}` instead of `get_ctf_name()` or `get_config('ctf_name')`
- Themes must now specify a `challenge.html` which control how a challenge should look.
- The main library for charts has been changed from Plotly to Apache ECharts.
- Forms have been moved into wtforms for easier form rendering inside of Jinja.
  - From Jinja you can access forms via the Forms global i.e. `{{ Forms }}`
  - This allows theme developers to more easily re-use a form without having to copy-paste HTML.
- Themes can now provide a theme settings JSON blob which can be injected into the theme with `{{ Configs.theme_settings }}`
- Core theme now includes the challenge ID in location hash identifiers to always refer the right challenge despite duplicate names
- Spinner centering has been switched from a hard coded margin in CSS to flexbox CSS classes from Bootstrap

**Plugins**

- Challenge plugins have changed in structure to better allow integration with themes and prevent obtrusive Javascript/XSS.
  - Challenge rendering now uses `challenge.html` from the provided theme.
  - Accessing the challenge view content is now provided by `/api/v1/challenges/<challenge_id>` in the `view` section. This allows for HTML to be properly sanitized and rendered by the server allowing CTFd to remove client side Jinja rendering.
  - `challenge.html` now specifies what's required and what's rendered by the theme. This allows the challenge plugin to avoid having to deal with aspects of the challenge besides the description and input.
  - A more complete migration guide will be provided when CTFd v3 leaves beta
- Display current attempt count in challenge view when max attempts is enabled
- `get_standings()`, `get_team_stanadings()`, `get_user_standings()` now has a fields keyword argument that allows for specificying additional fields that SQLAlchemy should return when building the response set.
  - Useful for gathering additional data when building scoreboard pages
- Flags can now control the message that is shown to the user by raising `FlagException`
- Fix `override_template()` functionality

**Deployment**

- Enable SQLAlchemy's `pool_pre_ping` by default to reduce the likelihood of database connection issues
- Mailgun email settings are now deprecated. Admins should move to SMTP email settings instead.
- Postgres is now considered a second class citizen in CTFd. It is tested against but not a main database backend. If you use Postgres, you are entirely on your own with regards to supporting CTFd.
- Docker image now uses Debian instead of Alpine. See https://github.com/CTFd/CTFd/issues/1215 for rationale.
- `docker-compose.yml` now uses a non-root user to connect to MySQL/MariaDB
- `config.py` should no longer be editting for configuration, instead edit `config.ini` or the environment variables in `docker-compose.yml`

**Miscellaneous**

- Fix an issue where email sending would be broken if the CTF name contained a colon
- Lint Markdown files with Prettier
- Lint Dockerfile and docker-compose.yml in Github Actions
- Lint JavaScript files with eslint
- Certain static strings have been converted into Enums for better re-useability throughout the code base
- Switch to using Github Actions for testing and linting
- Better handling of missing challenge types. Missing challenge types no longer bring down all other challenges.
- Documentation has been seperated out into a seperate repo (https://github.com/CTFd/docs).
- Documentation hosting has moved from ReadTheDocs to Netlify
- Any links in the codebase to help.ctfd.io have been changed to docs.ctfd.io.

# 3.0.0b3 / 2020-07-22

**General**

- Render Hint content on the server side and provide it in the Hint API response
  - In a sense this would deprecate the `content` field but it's left in for backwards compatability

**API**

- Add `html` item for `GET /api/v1/hints/[hint_id]` which contains the rendered HTML of the Hint content
- Remove `content` from `GET /api/v1/hints`

**Admin Panel**

- Fix an issue where an admin couldn't submit more than once on a challenge preview
- Fix an issue where the theme settings editor wouldn't load if the theme settings JSON was malformed

**Miscellaneous**

- Fix an issue where email sending would be broken if the CTF name contained a colon

# 3.0.0b2 / 2020-07-19

**General**

- Make HTML Sanitization an optional setting that's configurable via `HTML_SANITIZATION` in config.ini
- Allow HTML comments through sanitization
- Allow Bootstrap data attributes through sanitization

**Admin Panel**

- Fix an unclickable label in the Challenge creation interface

**Plugins**

- Fix bug preventing deleting alternative challenge types

**Miscellaneous**

- Switch to using Github Actions for testing and linting

# 3.0.0b1 / 2020-07-15

**General**

- Fix an issue where dynamic challenge solutions could not be submitted

**Documentation**

- Documentation has been seperated out into a seperate repo (https://github.com/CTFd/docs).
- Documentation hosting has moved from ReadTheDocs to Netlify
- Any links in the codebase to help.ctfd.io have been changed to docs.ctfd.io.

# 3.0.0a2 / 2020-07-09

**General**

- Accept additional profile fields during registration (affiliation, website, country)
  - This does not add additional inputs. Themes or additional JavaScript can add the form inputs.

**Admin Panel**

- Redesign the challenge creation form to use a radio button with challenge type selection instead of a select input

**API**

- Admins can no longer ban themselves through `PATCH /api/v1/users/[user_id]`

**Themes**

- Spinner centering has been switched from a hard coded margin in CSS to flexbox CSS classes from Bootstrap

**Plugins**

- Revert plugin menu (`register_admin_plugin_menu_bar`, `register_user_page_menu_bar`) changes to 2.x code

**Miscellaneous**

- Fix issue with `Configs.ctf_name` returning incorrect value
- Add prerender step back into challenges.js
- Better handling of missing challenge types. Missing challenge types no longer bring down all other challenges.

# 3.0.0a1 / 2020-07-01

**General**

- CTFd is now Python 3 only
- Render markdown with the CommonMark spec provided by `cmarkgfm`
- Render markdown stripped of any malicious JavaScript or HTML.
  - This is a significant change from previous versions of CTFd where any HTML content from an admin was considered safe.
- Inject `Config`, `User`, `Team`, `Session`, and `Plugin` globals into Jinja
- User sessions no longer store any user-specific attributes.
  - Sessions only store the user's ID, CSRF nonce, and an hmac of the user's password
  - This allows for session invalidation on password changes
- The user facing side of CTFd now has user and team searching
- GeoIP support now available for converting IP addresses to guessed countries

**Admin Panel**

- Use EasyMDE as an improved description/text editor for Markdown enabled fields.
- Media Library button now integrated into EasyMDE enabled fields
- VueJS now used as the underlying implementation for the Media Library
- Fix setting theme color in Admin Panel
- Green outline border has been removed from the Admin Panel

**API**

- Significant overhauls in API documentation provided by Swagger UI and Swagger json
- Make almost all API endpoints provide filtering and searching capabilities
- Change `GET /api/v1/config/<config_key>` to return structured data according to ConfigSchema

**Themes**

- Themes now have access to the `Configs` global which provides wrapped access to `get_config`.
  - For example, `{{ Configs.ctf_name }}` instead of `get_ctf_name()` or `get_config('ctf_name')`
- Themes must now specify a `challenge.html` which control how a challenge should look.
- The main library for charts has been changed from Plotly to Apache ECharts.
- Forms have been moved into wtforms for easier form rendering inside of Jinja.
  - From Jinja you can access forms via the Forms global i.e. `{{ Forms }}`
  - This allows theme developers to more easily re-use a form without having to copy-paste HTML.
- Themes can now provide a theme settings JSON blob which can be injected into the theme with `{{ Configs.theme_settings }}`
- Core theme now includes the challenge ID in location hash identifiers to always refer the right challenge despite duplicate names

**Plugins**

- Challenge plugins have changed in structure to better allow integration with themes and prevent obtrusive Javascript/XSS.
  - Challenge rendering now uses `challenge.html` from the provided theme.
  - Accessing the challenge view content is now provided by `/api/v1/challenges/<challenge_id>` in the `view` section. This allows for HTML to be properly sanitized and rendered by the server allowing CTFd to remove client side Jinja rendering.
  - `challenge.html` now specifies what's required and what's rendered by the theme. This allows the challenge plugin to avoid having to deal with aspects of the challenge besides the description and input.
  - A more complete migration guide will be provided when CTFd v3 leaves beta
- Display current attempt count in challenge view when max attempts is enabled
- `get_standings()`, `get_team_stanadings()`, `get_user_standings()` now has a fields keyword argument that allows for specificying additional fields that SQLAlchemy should return when building the response set.
  - Useful for gathering additional data when building scoreboard pages
- Flags can now control the message that is shown to the user by raising `FlagException`
- Fix `override_template()` functionality

**Deployment**

- Enable SQLAlchemy's `pool_pre_ping` by default to reduce the likelihood of database connection issues
- Mailgun email settings are now deprecated. Admins should move to SMTP email settings instead.
- Postgres is now considered a second class citizen in CTFd. It is tested against but not a main database backend. If you use Postgres, you are entirely on your own with regards to supporting CTFd.
- Docker image now uses Debian instead of Alpine. See https://github.com/CTFd/CTFd/issues/1215 for rationale.
- `docker-compose.yml` now uses a non-root user to connect to MySQL/MariaDB
- `config.py` should no longer be editting for configuration, instead edit `config.ini` or the environment variables in `docker-compose.yml`

**Miscellaneous**

- Lint Markdown files with Prettier
- Lint Dockerfile and docker-compose.yml in Github Actions
- Lint JavaScript files with eslint
- Certain static strings have been converted into Enums for better re-useability throughout the code base
- Main testing now done by Github Actions. Travis testing is deprecated but still used until full parity exists
- Travis testing has been upgraded to use Ubuntu Bionic (18.04)

# 2.5.0 / 2020-06-04

**General**

- Use a session invalidation strategy inspired by Django. Newly generated user sessions will now include a HMAC of the user's password. When the user's password is changed by someone other than the user the previous HMACs will no longer be valid and the user will be logged out when they next attempt to perform an action.
- A user and team's place, and score are now cached and invalidated on score changes.

**API**

- Add `/api/v1/challenges?view=admin` to allow admin users to see all challenges regardless of their visibility state
- Add `/api/v1/users?view=admin` to allow admin users to see all users regardless of their hidden/banned state
- Add `/api/v1/teams?view=admin` to allow admin users to see all teams regardless of their hidden/banned state
- The scoreboard endpoint `/api/v1/scoreboard` is now significantly more performant (20x) due to better response generation
- The top scoreboard endpoint `/api/v1/scoreboard/top/<count>` is now more performant (3x) due to better response generation
- The scoreboard endpoint `/api/v1/scoreboard` will no longer show hidden/banned users in a non-hidden team

**Deployment**

- `docker-compose` now provides a basic nginx configuration and deploys nginx on port 80
- `Dockerfile` now installs `python3` and `python3-dev` instead of `python` and `python-dev` because Alpine no longer provides those dependencies

**Miscellaneous**

- The `get_config` and `get_page` config utilities now use SQLAlchemy Core instead of SQLAlchemy ORM for slight speedups
- The `get_team_standings` and `get_user_standings` functions now return more data (id, oauth_id, name, score for regular users and banned, hidden as well for admins)
- Update Flask-Migrate to 2.5.3 and regenerate the migration environment. Fixes using `%` signs in database passwords.

# 2.4.3 / 2020-05-24

**Miscellaneous**

- Notifications/Events endpoint will now immediately send a ping instead of waiting a few seconds.
- Upgrade `gunicorn` dependency to `19.10.0`
- Upgrade `boto3` dependency to `1.13.9`
- Improve `import_ctf()` reliability by closing all connections before dropping & recreating database
- Close database session in IP tracking code in failure situations to avoid potential dangling database connections
- Don't allow backups to be imported if they do not have a `db` folder
- Change `import_ctf()` process slightly to import built-in tables first and then plugin tables
- Handle exception where a regex Flag is invalid

**API**

- File deletion endpoint (`DELETE /api/v1/files/[file_id]`) will now correctly delete the associated file

**Plugins**

- Add `CTFd.plugins.get_plugin_names()` to get a list of available plugins
- Add `CTFd.plugins.migrations.current()` to get the current revision of a plugin migration
- Improve `CTFd.plugins.migrations.upgrade()` to be able to upgrade to a specific plugin migration
- Run plugin migrations during import process

**Themes**

- Update jQuery to v3.5.1 to fix mobile hamburger menu
- Upgrade some dependencies in yarn lockfile
- Fix invalid team link being generated in `scoreboard.js`

**Admin Panel**

- Fix sending of user creation notification email
- Fix button to remove users from teams

# 2.4.2 / 2020-05-08

**Admin Panel**

- Fix Challenge Reset in Admin Panel where Dynamic Challenges prevented resetting Challenges

**Plugins**

- Add the `CTFd.plugins.migrations` module to allow plugins to handle migrations. Plugins should now call `CTFd.plugins.migrations.upgrade` instead of `app.db.create_all` which will allow the plugin to have database migrations.
- Make Dynamic Challenges have a cascading deletion constraint against their respective Challenge row

**Miscellaneous**

- Add `app.plugins_dir` object to refer to the directory where plugins are installed

# 2.4.1 / 2020-05-06

**Admin Panel**

- Fix issue where admins couldn't update the "Account Creation" email
- Fix issue where the Submissions page in the Admin Panel could not be paginated correctly

**Miscellaneous**

- Add `SQLALCHEMY_ENGINE_OPTIONS` to `config.py` with a slightly higher default `max_overflow` setting for `SQLALCHEMY_MAX_OVERFLOW`. This can be overridden with the `SQLALCHEMY_MAX_OVERFLOW` envvar
- Add `node_modules/` to `.dockerignore`

# 2.4.0 / 2020-05-04

**General**

- Cache user and team attributes and use those perform certain page operations intead of going to the database for data
  - After modifying the user/team attributes you should call the appropriate cache clearing function (clear_user_session/clear_team_session)
- Cache user IPs for the last hour to avoid hitting the database on every authenticated page view
  - Update the user IP's last seen value at least every hour or on every non-GET request
- Replace `flask_restplus` with `flask_restx`
- Remove `datafreeze`, `normality`, and `banal` dependencies in favor of in-repo solutions to exporting database

**Admin Panel**

- Add bulk selection and deletion for Users, Teams, Scoreboard, Challenges, Submissions
- Make some Admin tables sortable by table headers
- Create a score distribution graph in the statistics page
- Make instance reset more granular to allow for choosing to reset Accounts, Submissions, Challenges, Pages, and/or Notificatoins
- Properly update challenge visibility after updating challenge
- Show total possible points in Statistics page
- Add searching for Users, Teams, Challenges, Submissions
- Move User IP addresses into a modal
- Move Team IP addresses into a modal
- Show User website in a user page button
- Show Team website in a team page button
- Make the Pages editor use proper HTML syntax highlighting
- Theme header and footer editors now use CodeMirror
- Make default CodeMirror font-size 12px
- Stop storing last action via location hash and switch to using sessionStorage

**Themes**

- Make page selection a select and option instead of having a lot of page links
- Add the JSEnum class to create constants that can be accessed from webpack. Generate constants with `python manage.py build jsenums`
- Add the JinjaEnum class to inject constants into the Jinja environment to access from themes
- Update jQuery to 3.5.0 to resolve potential security issue
- Add some new CSS utilities (`.min-vh-*` and `.opacity-*`)
- Change some rows to have a minimum height so they don't render oddly without data
- Deprecate `.spinner-error` CSS class
- Deprecate accessing the type variable to check user role. Instead you should use `is_admin()`

**Miscellaneous**

- Enable foreign key enforcement for SQLite. Only really matters for the debug server.
- Remove the duplicated `get_config` from `CTFd.models`
- Fix possible email sending issues in Python 3 by using `EmailMessage`
- Dont set User type in the user side session. Instead it should be set in the new user attributes
- Fix flask-profiler and bump dependency to 1.8.1
- Switch to using the `Faker` library for `populate.py` instead of hardcoded data
- Add a `yarn lint` command to run eslint on JS files
- Always insert the current CTFd version at the end of the import process
- Fix issue where files could not be downloaded on Windows

# 2.3.3 / 2020-04-12

**General**

- Re-enable the Jinja LRU Cache for **significant speedups** when returning HTML content

**API**

- `POST /api/v1/unlocks` will no longer allow duplicate unlocks to happen

**Admin Panel**

- Makes `Account Visibility` subtext clearer by explaining the `Private` setting in Config Panel

**Themes**

- Fixes an issue with using a theme with a purely numeric name
- Fixes issue where the scoreboard graph always said Teams regardless of mode

**Miscellaneous**

- Bump max log file size to 10 MB and fix log rotation
- Docker image dependencies (apk & pip) are no longer cached reducing the image size slightly

# 2.3.2 / 2020-03-15

**General**

- Fix awards not being properly assigned to teams in `TEAMS_MODE`

**API**

- Set `/api/v1/statistics/users` route to be admins_only
- When POST'ing to `/api/v1/awards`, CTFd will look up a user's team ID if `team_id` is not specified

**Admin Panel**

- Adds a setting to registration visibility to allow for MLC registration while registration is disabled
- Fix setting theme color during the setup flow and from the Admin Panel

**Themes**

- Fixes users/admins being able to remove profile settings.
  - Previously a bug prevented users from removing some profile settings. Now the `core` theme stores the initial value of inputs as a `data` attribute and checks for changes when updating data. This should be a temporary hack until a proper front-end framework is in place.
- Fix `ezToast()` issue that was keeping toast messages visible indefinitely
- Fix `modal-body` parameters in ezq.js for `ezAlert` and `ezQuery` and fix the progress bar for certain cases in `ezProgressBar`
- Use `authed()` function to check if user is authed in `base.html`. This fixes an issue where a page could look as if the user was logged in.

**Miscellaneous**

- Fix behavior for `REVERSE_PROXY` config setting when set to a boolean instead of a string
- Improve `Dockerfile` to run fewer commands and re-use the build cache
- Add `make coverage` to generate an HTML coverage report
- Update `coverage` and `pytest-cov` development dependencies

# 2.3.1 / 2020-02-17

**General**

- User confirmation emails now have the correct URL format

# 2.3.0 / 2020-02-17

**General**

- During setup, admins can register their email address with the CTFd LLC newsletter for news and updates
- Fix editting hints from the admin panel
- Allow admins to insert HTML code directly into the header and footer (end of body tag) of pages. This replaces and supercedes the custom CSS feature.
  - The `views.custom_css` route has been removed.
- Admins can now customize the content of outgoing emails and inject certain variables into email content.
- The `manage.py` script can now manipulate the CTFd Configs table via the `get_config` and `set_config` commands. (e.g. `python manage.py get_config ctf_theme` and `python manage.py set_config ctf_theme core`)

**Themes**

- Themes should now reference the `theme_header` and `theme_footer` configs instead of the `views.custom_css` endpoint to allow for user customizations. See the `base.html` file of the core theme.

**Plugins**

- Make `ezq` functions available to `CTFd.js` under `CTFd.ui.ezq`

**Miscellaneous**

- Python imports sorted with `isort` and import order enforced
- Black formatter running on a majority of Python code

# 2.2.3 / 2020-01-21

### This release includes a critical security fix for CTFd versions >= 2.0.0

All CTFd administrators are recommended to take the following steps:

1. Upgrade their installations to the latest version
2. Rotate the `SECRET_KEY` value
3. Reset the passwords for all administrator users

**Security**

- This release includes a fix for a vulnerability allowing an arbitrary user to take over other accounts given their username and a CTFd instance with emails enabled

**General**

- Users will receive an email notification when their passwords are reset
- Fixed an error when users provided incorrect team join information

# 2.2.2 / 2020-01-09

**General**

- Add jQuery, Moment, nunjucks, and Howl to window globals to make it easier for plugins to access JS modules
- Fix issue with timezone loading in config page which was preventing display of CTF times

# 2.2.1 / 2020-01-04

**General**

- Fix issue preventing admins from creating users or teams
- Fix issue importing backups that contained empty directories

# 2.2.0 / 2019-12-22

## Notice

2.2.0 focuses on updating the front end of CTFd to use more modern programming practices and changes some aspects of core CTFd design. If your current installation is using a custom theme or custom plugin with **_any_** kind of JavaScript, it is likely that you will need to upgrade that theme/plugin to be useable with v2.2.0.

**General**

- Team size limits can now be enforced from the configuration panel
- Access tokens functionality for API usage
- Admins can now choose how to deliver their notifications
  - Toast (new default)
  - Alert
  - Background
  - Sound On / Sound Off
- There is now a notification counter showing how many unread notifications were received
- Setup has been redesigned to have multiple steps
  - Added Description
  - Added Start time and End time,
  - Added MajorLeagueCyber integration
  - Added Theme and color selection
- Fixes issue where updating dynamic challenges could change the value to an incorrect value
- Properly use a less restrictive regex to validate email addresses
- Bump Python dependencies to latest working versions
- Admins can now give awards to team members from the team's admin panel page

**API**

- Team member removals (`DELETE /api/v1/teams/[team_id]/members`) from the admin panel will now delete the removed members's Submissions, Awards, Unlocks

**Admin Panel**

- Admins can now user a color input box to specify a theme color which is injected as part of the CSS configuration. Theme developers can use this CSS value to change colors and styles accordingly.
- Challenge updates will now alert you if the challenge doesn't have a flag
- Challenge entry now allows you to upload files and enter simple flags from the initial challenge creation page

**Themes**

- Significant JavaScript and CSS rewrite to use ES6, Webpack, yarn, and babel
- Theme asset specially generated URLs
  - Static theme assets are now loaded with either .dev.extension or .min.extension depending on production or development (i.e. debug server)
  - Static theme assets are also given a `d` GET parameter that changes per server start. Used to bust browser caches.
- Use `defer` for script tags to not block page rendering
- Only show the MajorLeagueCyber button if configured in configuration
- The admin panel now links to https://help.ctfd.io/ in the top right
- Create an `ezToast()` function to use [Bootstrap's toasts](https://getbootstrap.com/docs/4.3/components/toasts/)
- The user-facing navbar now features icons
- Awards shown on a user's profile can now have award icons
- The default MarkdownIt render created by CTFd will now open links in new tabs
- Country flags can now be shown on the user pages

**Deployment**

- Switch `Dockerfile` from `python:2.7-alpine` to `python:3.7-alpine`
- Add `SERVER_SENT_EVENTS` config value to control whether Notifications are enabled
- Challenge ID is now recorded in the submission log

**Plugins**

- Add an endpoint parameter to `register_plugin_assets_directory()` and `register_plugin_asset()` to control what endpoint Flask uses for the added route

**Miscellaneous**

- `CTFd.utils.email.sendmail()` now allows the caller to specify subject as an argument
  - The subject allows for injecting custom variable via the new `CTFd.utils.formatters.safe_format()` function
- Admin user information is now error checked during setup
- Added yarn to the toolchain and the yarn dev, yarn build, yarn verify, and yarn clean scripts
- Prevent old CTFd imports from being imported

# 2.1.5 / 2019-10-2

**General**

- Fixes `flask run` debug server by not monkey patching in `wsgi.py`
- Fix CSV exports in Python 3 by converting StringIO to BytesIO
- Avoid exception on sessions without a valid user and force logout
- Fix several issues in Vagrant provisioning

**API**

- Prevent users from nulling out profile values and breaking certain pages

# 2.1.4 / 2019-08-31

**General**

- Make user pages show the team's score and place information instead of the user's information if in team mode
- Allow admins to search users by IP address
- Require password for email address changes in the user profile
- The place indicator in `Teams Mode` on the team pages and user pages now correctly excludes hidden teams
- Fix scoreboard place ordinalization in Python 3
- Fix for a crash where imports will fail on SQLite due to lack of ALTER command support
- Fix for an issue where files downloaded via S3 would have the folder name in the filename
- Make `Users.get_place()` and `Teams.get_place()` for return None instead of 0 if the account has no rank/place
- Properly redirect users or 403 if the endpoint requires a team but the user isn't in one
- Show affiliation in user and team pages in the admin panel and public and private user and team pages

**Themes**

- Remove invalid `id='submit'` on submit buttons in various theme files
- Set `tabindex` to 0 since we don't really care for forcing tab order
- Rename `statistics.js` to `graphs.js` in the Admin Panel as it was identified that adblockers can sometimes block the file

**API**

- The team profile endpoint (`/api/v1/teams/me`) will now return 403 instead of 400 if the requesting user is not the captain
- The Challenge API will now properly freeze the solve count to freeze time

# 2.1.3 / 2019-06-22

**General**

- Fix issue with downloading files after CTF end when `view_after_ctf` is enabled
- Sort solves in admin challenge view by date
- Link to appropriate user and challenge in team, user, and challenge pages
- Redirect to `/team` instead of `/challenges` after a user registers in team mode
- Fixes bug where pages marked as `hidden` weren't loading
- Remove `data-href` from `pages.html` in the Admin Panel to fix the delete button
- Add UI to handle team member removal in Admin Panel
- Fixes account links on the scoreboard page created by `update()`. They now correctly point to the user instead of undefined when in user mode.
- `utils._get_config` will now return `KeyError` instead of `None` to avoid cache misses

**Deployment**

- Use `/dev/shm` for `--worker-tmp-dir` in gunicorn in Docker
- Cache `get_place` code for users and teams.
- Install `Flask-DebugToolbar` in development
- Cache the `/scoreboard` page to avoid having to rebuild the response so often
- Make unprivileged `ctfd` user usable for mysql connection in docker-compose by having the db image create the database instead of CTFd
- Fix bug causing apache2 + mod_wsgi deployments to break

**API**

- Change `/api/v1/teams/[team_id]/members` from taking `id` to `user_id`.
  - Endpoint was unused so the API change is considered non-breaking.
- Add `account_type` and `account_url` field in `/api/v1/scoreboard`
- Separate `/api/v1/[users,teams]/[me,id]/[solves,fails,awards]` into seperate API endpoints
- Clear standings cache after award creation/deletion

**Exports**

- Temporarily disable foreign keys in MySQL, MariaDB, and Postgres during `import_ctf()`
- Add `cache_timeout` parameter to `send_file`response in `/admin/export` to prevent the browser from caching the export

**Tests**

- Fix score changing test helpers to clear standings cache when generating a score changing row

# 2.1.2 / 2019-05-13

**General**

- Fix freeze time regressions in 2.x
  - Make `/api/v1/[users,teams]/[me]/[solves,fails,awards]` endpoints load as admin so users can see their solves after freeze
  - Make `/api/v1/challenges/[id]/solves` only show solves before freeze time
    - Add the `?preview=true` GET parameter for admins to preview challenges solves as a user
- Team join attempts are now ratelimited

**Tests**

- More linting and autoformatting rules
  - Format Javascript and CSS files with `prettier`: `prettier --write 'CTFd/themes/**/*'`
  - Format Python with `black`: `black CTFd` and `black tests`
  - `make lint` and thus Travis now include the above commands as lint checks
- Travis now uses xenial instead of trusty.

# 2.1.1 / 2019-05-04

**General**

- Allow admins to hit `/api/v1/challenges` and `/api/v1/challenges/[id]` without having a team to fix challenge previews
- Fix rate-limiting of flag submission when using team mode
- Fixes some modal close buttons not working in the admin panel
- Fixes `populate.py` to assign captains to teams.

**Models**

- Added `Challenges.flags` relationship and moved the `Flags.challenge` relationship to a backref on Challenges
- Added `ondelete='CASCADE'` to most ForeignKeys in models allowing for deletions to remove associated data
  - `Hints` should be deleted when their Challenge is deleted
  - `Tags` should be deleted when their Challenge is deleted
  - `Flags` should be deleted when their Challenge is deleted
  - `ChallengeFiles` should be deleted when their Challenge is deleted
    - Deletion of the file itself is not handled by the model/database
  - `Awards` should be deleted when their user or team is deleted
  - `Unlocks` should be deleted when their user or team is deleted
  - `Tracking` should be deleted when their user or team is deleted
  - `Teams.captain_id` should be set to NULL when the captain user is deleted

**Exports**

- Force `db.create_all()` to happen for imports on `sqlite` or on failure to create missing tables
- Force `ctf_theme` to be set to `core` in imports in case a theme is missing from the import or the instance
- Fix imports/exports to emit and accept JSON properly under MariaDB
  - MariaDB does not properly understand JSON so it must accept strings instead of dicts
  - MariaDB outputs strings instead of JSON for its JSON type so the export serializer will attempt to cast output JSON strings to JSON objects

**Deployment**

- Run as root when using docker-compose
  - This is necessary to be able to write to the volumes mounted from the host

# 2.1.0 / 2019-04-24

**General**

- Remove Flask-SocketIO in favor of custom Server Side Events code
  - Removed the Flask-SocketIO dependency and removed all related code. See **Deployment** section.
  - Added EventSource polyfill from Yaffle/EventSource
  - Events are now rate-limited and only availble to authenticated users
    - This means real time notifications will only appear to authenticated users
  - Browser localStorage is now used to dictate which tab will maintain the persistent connection to the `/events` endpoint
    - Thanks to https://gist.github.com/neilj/4146038
  - Notifications (currently the only use of the events code) now appear with a notification sound
    - Thanks to [Terrence Martin](https://soundcloud.com/tj-martin-composer) for the sound
- Added UI to delete and download files from the media library
- Progress bars have been added to some actions which could take time
  - To file uploads on challenge page
  - To file uploads on the page editor page
  - To the import CTF functionality
- Challenge file downloads now require a token to download
  - `/files/<path>` now accepts a `?token=` parameter which is a serialized version of `{user_id: <>, team_id: <>, file_id: <>}`
  - If any of these sections are invalid or the user/team is banned the download is blocked
  - This allows files to be downloaded via `curl` or `wget` (i.e. without cookie authentication)
- Added a team captain concept. Team captains can edit team information such as name, team password, website, etc.
  - Only captains can change their team's captain
  - Captains are the first to join the team. But they can be transferred to the true captain later on
- Cache `/api/v1/scoreboard` and `/api/v1/scoreboard/top/[count]`
  - Adds `cache.make_cache_key` because Flask-Caching is unable to cleanly determine the endpoint for Flask-Restplus
  - This helper may change in a future release or be deprecated by an improvement in Flask-Caching
- Properly load hidden and banned properties in the admin team edit modal
- Adds a hover color change on table rows in the admin panel.
  - If a table row specifies the `data-href` attribute it will become clickable
- Add a simple Makefile to wrap some basic commands
  - make lint: lint the code base
  - make test: test the code base
  - make serve: create a debug application server
  - make shell: create a Python shell with the application preloaded
- Started work on a Sphinx documentation site available at [https://docs.ctfd.io](https://docs.ctfd.io)

**Dependencies**

- Upgraded `SQLAlchemy` to 1.3.3 for proper JSON columns in SQLite
- Pin `Werkzeug==0.15.2` in requirements.txt
- Flask-Profiler added to `serve.py --profile`

**Models**

- Awards table now has a `type` column which is used as a polymorphic identity
- Add `Teams.captain_id` column to Teams table

**API**

- Added /api/v1/teams/[team_id]/members
- Cache `/api/v1/scoreboard` and `/api/v1/scoreboard/top/[count]`
  - Adds `cache.make_cache_key` because Flask-Caching is unable to cleanly determine the endpoint for Flask-Restplus
  - This helper may change in a future release or be deprecated by an improvement in Flask-Caching
- Add `/api/v1/users?notify=true` to email user & password after creating new account
- Fix issue where admins could not modify their own profile or their own team

**Plugins**

- `CTFd.utils.security.passwords` deprecated and now available at `CTFd.utils.crypto`
- Built-in challenge plugins now linkify challenge text properly
- Challenge type plugins do not have to append `script_root` to file downloads anymore as that will now be managed by the API
- Awards are now polymorphic and subtables can be created for them

**Themes**

- Fix spelling mistake in `500.html`
- Removed `socket.io.min.js` from `base.html`
- Added EventSource polyfill from Yaffle/EventSource
- Added `howler.js` to play notification sounds
- Vendored/duplicated files which were shared between the `admin` and `core` themes have been de-duped
  - The files used in the `core` theme should now be considered free to use by other themes
- CTF start and end times are now injected into `base.html` and available in the `CTFd.js` object
- Register page now properly says "User Name" instead of "Team Name" since only users can see the Register page
- Users and Teams pages now use a public and private page.
  - user.html -> users/public.html and users/private.html
  - team.html -> teams/public.html and teams/private.html
- Separate `admin/templates/modals/users/create.html` into `admin/templates/modals/users/edit.html`

**Exports**

- Exports will now properly export JSON for all JSON columns
  - In some configurations the column would be exported as a string.
  - Legacy string columns will still be imported properly.
- Exports from old 2.x CTFd versions should upgrade and be installed properly
  - Any failure to do so should be considered a bug

**Deployment**

- User is no longer `root` in Docker image
  - Errors in writing log files will now fail silently as we expect a future rewrite
  - Logs will now also go to stdout
- Update Dockerfile to create and chown/chmod the folders used by `docker-compose` to store files/logs (`/var/log/CTFd`, `/var/uploads`)
  - This allows the container to write to the folder despite it being a volume mounted from the host
- Default worker changed back to `gevent`
- Removed Flask-SocketIO dependency
  - Removed the `SOCKETIO_ASYNC_MODE` config
- `gevent` is now required to allow the Server Sent Events client polling code to work
  - If you use the provided `wsgi.py` or `gevent` gunicorn workers, there shouldn't be any issues
- Cache `/api/v1/scoreboard` and `/api/v1/scoreboard/top/[count]` which is invalidated on new solves or every minute

**Configuration**

- Added `SWAGGER_UI` setting to config.py to control the existence of the `/api/v1/` Swagger UI documentation
- Removed the `SOCKETIO_ASYNC_MODE` config
- Renamed docstring that referenced `SQLALCHEMY_DATABASE_URI` to `DATABASE_URL`
- The `REVERSE_PROXY` configuration can be set to `True` or to a comma seperated string of integers (e.g. `1,1,1,1,1`)
  - See https://werkzeug.palletsprojects.com/en/0.15.x/middleware/proxy_fix/#werkzeug.middleware.proxy_fix.ProxyFix
  - For example to configure `x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1` specify `1,1,1,1,1`

**Tests**

- Tests are now executed in parallel
  - When using a non-memory database, test helpers will now randomize the database name to be able to parallelize execution
- Test tool switched from `nosetests` to `pytest`
- Lint tool switched from `pycodestyle` to `flake8`
- Basic security checking added using `bandit`
- Allow `create_ctfd()` test helper to take app configuration as an argument

# 2.0.6 / 2019-04-08

**Security**

- Fixes an issue where user email addresses could be disclosed to non-admins

**General**

- Users/Teams set to hidden or banned are no longer visible by other users
  - This affects the API and the main user interface. This does not affect admins
- Users without a Team can no longer view challenges when the CTF is in Team Mode

# 2.0.5 / 2019-03-23

**Security**

- Fixes an issue where user email addresses could be disclosed to non-admins

**General**

- Dockerfile now installs `linux-headers` package from apk
- Hidden teams are no longer visible publicly
- Fixes an issue where long content made it it difficult/impossible to edit flags and hints
- Fix for users not being able to edit portions of their own profile
- Fix for solves not being frozen for teams.
- Reimplement direct user email sending from the admin panel
- Fixes an issue where confirmation logs would report None instead of the user if the browser was unauthenticated
- Fixes an issue where SMTP server configuration (MAIL_SERVER, MAIL_PORT) were not being read from `config.py`
- Fixes for a user's place on their profile showing a different place than the scoreboard
- Fixes for an issue where dynamic challenge values would appear to change after being solved by a hidden user

**Exports**

- Exports are now saved on disk with `tempfile.NamedTemporaryFile()` instead of memory during creation
- After importing an export, CTFd will now recreate all tables it expects to be available. This resolves an issue where tables created by plugins would be missing after an import.

# 2.0.4 / 2019-01-30

**General**

- Block user & team name changes if name changes are disabled (Closes #835)
- Set accounts to unconfirmed if email is changed while `verify_emails` is enabled
- Only allow users to change their email to emails with domains in the whitelist.
- Add `email.check_email_is_whitelisted()` to verify that a user's email is whitelisted.
- Create a `get_config` wrapper around the internal `_get_config` to let us set a default config value (Closes #659)
- Remove `utils.get_app_config()` from memoization and also give it a `default` parameter
- Move `utils.logging.init_logs()` into `utils.initialization` and properly call `init_logs()` to save logs to the logs folder
- Block the creation of users/teams from MLC if registration_visibility is private
- Fix showing incorrect 'CTF has ended' error if `view_after_ctf` is set.
- Fix creating users from the admin panel while name changes are disabled.

**API**

- `/api/v1/teams/<team_id>` now coerced to an int (i.e. `/api/v1/teams/<int:team_id>`)

**Deployment**

- Re-add the `LOG_FOLDER` envvar to docker-compose so we don't try to write to the read-only host
- Stop gunicorn from logging to `LOG_FOLDER` in docker without explicit opt-in
- Add `ACCESS_LOG` and `ERROR_LOG` envvars to docker to specify where gunicorn will log to
- Allow `DATABASE_URL` to contain custom MySQL ports for `docker-entrypoint.sh`
- Drop `WORKERS` count to 1 to avoid dealing with Flask-SocketIO sticky sessions'
- Install `gevent-websocket` and use it by default until we have a better solution
- NOTE: In future releases, websockets functionality will likely be removed. (#852)

# 2.0.3 / 2019-01-12

**Security Release**

This release resolves a security issue that allowed malicious users to hijack admin browser sessions in certain browsers under certain configurations.

The implemented fix is to require the new `CSRF-Token` header on state-changing requests with a Content-Type of application/json.
The same nonce used for standard POST requests is re-used for the `CSRF-Token` header.

Because of the necessary changes to the API, the previously used call to `fetch()` in themes should now be replaced with `CTFd.fetch()`.

**Security**

- Require `CSRF-Token` header on all API requests.
- Require CSRF protection on all HTTP methods except `GET`, `HEAD`, `OPTIONS`, and `TRACE`.
- Default session cookie to `SameSite=Lax`
- Send initial user information request to MajorLeagueCyber over HTTPS

**General**

- Fix `update_check()` logic so that we don't accidentally remove the update notification.

**Themes**

- Remove explicit usage of `script_root` in public JS.
  - In custom themes, use the `CTFd.fetch()` function (defined in `CTFd.js`) and properly register the url root and CSRF nonce in `base.html` as shown below:
  ```javascript
  var script_root = "{{ request.script_root }}";
  var csrf_nonce = "{{ nonce }}";
  CTFd.options.urlRoot = script_root;
  CTFd.options.csrfNonce = csrf_nonce;
  ```
- Reduce required amount of parameters required for static theme files.
  - i.e. `url_for('views.themes')` no longer requires the themes parameter. It now defaults to the currently in-use theme.

# 2.0.2 / 2019-01-03

**General**

- Fix regression where public challenges could not be attempted by unauthed users.
- Admin Config Panel UI no longer allows changing of user mode.
- Show notification titles and allow for deleting notifications
  - Update notification UI in admin panel to be similar to the public-facing UI
- Fix subdirectory deployments in a generic manner by modifying `request.path` to combine both `request.script_root` and `request.path`.
  - Also create a request preprocessor to redirect users into the true CTFd app when deploying on a subdirectory.
  - Redirect to `request.full_path` instead of just `request.path`.
- Fix `TestingConfig.SAFE_MODE` not being reset between tests.
- Disable `value` input in dynamic challenge update field since we calculate it on the user's behalf.
- Fix displaying incorrect account link in the solves tab of a challenge modal.
- Pin `normality` version because of an upstream issue in `dataset`.
- Fix `500`'s when users submit non-integer values to `?page=1`

**API**

- Add `/api/v1/notifications/<id>` to allow accessing notifactions by ID.
  - This is currently public but will become permission based later in the future
- Add `account_url` field to the response of `/api/v1/<challenge_id>/solves` so the client knows where an account is located.

**Plugins**

- Add new plugin utilities to register javascript and css files for the admin panel.
  - Also fixed issue where those scripts and files were shared between generated applications

# 2.0.1 / 2018-12-09

2.0.1 is a patch release to fix regressions and bugs in 2.0.0.

If you are upgrading from a version prior to 2.0.0 please read the 2.0.0 change notes for instructions on updating to
2.0.0 before updating to 2.0.1.

**General**

- Fix setting auth for `get_smtp()`.
  - Add `MAIL_USEAUTH` to `config.py`.
- Add more mail documentation to `config.py`.
- Disable jinja cache properly by setting `cache_size` to 0 (#662)
  Regression from 1.2.0.
- Fix downloading files as an anonymous user.
- Fix viewing challenges anonymously if they have empty requirements. Closes #789
  - Allow anonymous users to see see challenges with empty requirements or anonymized challenges
- Clean up admin mail settings to use new label/small structure
- Fix email confirmations and improve test.
- Fix password resets from double hashing passwords

**Themes**

- Change `confirm.html` to use the variable user instead of team

**API**

- Grant admin write access to verified field in UserSchema.
- Fix setting `mail_username`, `mail_password`
- Prevent overriding smtp attributes on config update
- Fix hint loading for admins by adding `/api/v1/hints/<id>?preview=true` for use by admins
- Fixing a bug where prerequisites could not be set for dynamic challenges due to a division by zero error where defaults were being set unnecessarily.

**Exports**

- Fix syncing down an empty S3 bucket
- Fix `S3Uploader` in Python 3 and fix test
- Fix S3 sync function to only pull down files instead of trying to pull directories

# 2.0.0 / 2018-12-02

2.0.0 is a _significant_, backwards-incompaitble release.

Many unofficial plugins will not be supported in CTFd 2.0.0. If you're having trouble updating your plugins
please join [the CTFd Slack](https://slack.ctfd.io/) for help and discussion.

If you are upgrading from a prior version be sure to make backups and have a reversion plan before upgrading.

- If upgrading from 1.2.0 please make use of the `migrations/1_2_0_upgrade_2_0_0.py` script as follows:
  1. Make all necessary backups. Backup the database, uploads folder, and source code directory.
  2. Upgrade the source code directory (i.e. `git pull`) but do not run any updated code yet.
  3. Set the `DATABASE_URL` in `CTFd/config.py` to point to your existing CTFd database.
  4. Run the upgrade script from the CTFd root folder i.e. `python migrations/1_2_0_upgrade_2_0_0.py`.
     - This migration script will attempt to migrate data inside the database to 2.0.0 but it cannot account for every situation.
     - Examples of situations where you may need to manually migrate data:
       - Tables/columns created by plugins
       - Tables/columns created by forks
       - Using databases which are not officially supported (e.g. sqlite, postgres)
  5. Setup the rest of CTFd (i.e. config.py), migrate/update any plugins, and run normally.
- If upgrading from a version before 1.2.0, please upgrade to 1.2.0 and then continue with the steps above.

**General**

- Seperation of Teams into Users and Teams.
  - Use User Mode if you want users to register as themselves and play on their own.
  - Use Team Mode if you want users to create and join teams to play together.
- Integration with MajorLeagueCyber (MLC). (https://majorleaguecyber.org)
  - Organizers can register their event with MLC and will receive OAuth Client ID & Client Secret.
  - Organizers can set those OAuth credentials in CTFd to allow users and teams to automatically register in a CTF.
- Data is now provided to the front-end via the REST API. (#551)
  - Javascript uses `fetch()` to consume the REST API.
- Dynamic Challenges are built in.
- S3 backed uploading/downloading built in. (#661)
- Real time notifications/announcements. (#600)
  - Uses long-polling instead of websockets to simplify deployment.
- Email address domain whitelisting. (#603)
- Database exporting to CSV. (#656)
- Imports/Exports rewritten to act as backups.
  - Importing no longer stacks values.
  - Exports are no longer partial.
- Reset CTF from config panel (Remove all users, solves, fails. i.e. only keep Challenge data.) (#639)
- Countries are pre-determined and selectable instead of being user-entered.
  - Countries stored based on country code.
  - Based on https://github.com/umpirsky/country-list/blob/master/data/en_US/country.csv.
- Sessions are no longer stored using secure cookies. (#658)
  - Sessions are now stored server side in a cache (`filesystem` or `redis`) allowing for session revocation.
  - In order to delete the cache during local development you can delete `CTfd/.data/filesystem_cache`.
- Challenges can now have requirements which must be met before the challenge can be seen/solved.
- Workshop mode, score hiding, registration hiding, challenge hiding have been changed to visibility settings.
- Users and Teams can now be banned preventing access to the CTF.
- Dockerfile improvements.
  - WORKERS count in `docker-entrypoint.sh` defaults to 1. (#716)
  - `docker-entrypoint.sh` exits on any error. (#717)
- Increased test coverage.
- Create `SAFE_MODE` configuration to disable loading of plugins.
- Migrations have been reset.

**Themes**

- Data is now provided to the front-end via the REST API.
  - Javascript uses `fetch()` to consume the REST API.
- The admin theme is no longer considered seperated from the core theme and should always be together.
- Themes now use `url_for()` to generate URLs instead of hardcoding.
- socket.io (via long-polling) is used to connect to CTFd to receive notifications.
- `ctf_name()` renamed to `get_ctf_name()` in themes.
- `ctf_logo()` renamed to `get_ctf_logo()` in themes.
- `ctf_theme()` renamed to `get_ctf_theme()` in themes.
- Update Font-Awesome to 5.4.1.
- Update moment.js to 2.22.2. (#704)
- Workshop mode, score hiding, registration hiding, challenge hiding have been changed to visibility functions.
  - `accounts_visible()`, `challenges_visible()`, `registration_visible()`, `scores_visible()`

**Plugins**

- Plugins are loaded in `sorted()` order
- Rename challenge type plugins to use `.html` and have simplified names. (create, update, view)
- Many functions have moved around because utils.py has been broken up and refactored. (#475)
- Marshmallow (https://marshmallow.readthedocs.io) is now used by the REST API to validate and serialize/deserialize API data.
  - Marshmallow schemas and views are used to restrict SQLAlchemy columns to user roles.
- The REST API features swagger support but this requires more utilization internally.
- Errors can now be provided between routes and decoraters through message flashing. (CTFd.utils.helpers; get_errors, get_infos, info_for, error_for)
- Email registration regex relaxed. (#693)
- Many functions have moved and now have dedicated utils packages for their category.
- Create `SAFE_MODE` configuration to disable loading of plugins.

# 1.2.0 / 2018-05-04

**General**

- Updated to Flask 1.0 & switched documentation to suggest using `flask run` instead of `python serve.py`.
- Added the ability to make static & regex flags case insensitive.
- The `/chals` endpoint no longer lists the details of challenges.
  - The `/chals/:id` endpoint is now used to load challenge information before display.
- Admins can now see what users have solved a given challenge from the admin panel.
- Fixed issue with imports extracting files outside of the CTFd directory.
- Added import zipfile validation and optional size restriction.
- The ctftime, authentication, and admin restrictions have been converted to decorators to improve code reuse.
  - 403 is now a more common status code. Previously it only indicated CSRF failure, now it can indicate login failure
    or other Forbidden access situations.
- Challenge previews now work consistently instead of occasionally failing to show.
- Tests are now randomly ordered with `nose-randomly`.

**Themes**

- Admins now have the ability to upload a CTF logo from the config panel.
- Switched from the `marked` library to `Markdown-It` for client side markdown rendering.
  - This will break Challenge type plugins that override the markdown renderer since we are no longer using the marked renderers.
- Introduced the `ezpg()` JS function to make it easier to draw a progressbar modal.
- Introduced the `$.patch()` AJAX wrapper.
- Team names are truncated properly to 50 characters in `teams.html`.
- The admin panel now uses Bootstrap badges instead of buttons to indicate properties such as `admin`, `verified`, `visible`.

**Plugins**

- Challenge type plugins now use a global challenge object with exposed functions to specify how to display a challenge.
  (`preRender()`, `render()`, `postRender()`, `submit()`).
  - Challenge type plugins also have access to window.challenge.data which allow for the previously mentioned functions to
    process challenge data and change logic accordingly.
- Challenge type plugins now get full control over how a challenge is displayed via the nunjucks files.
- Challenge plugins should now pass the entire flag/key object to a Custom flag type.
  - This allows the flag type to make use of the data column to decide how to operate on the flag. This is used to implement
    case insensitive flags.
- Challenge modals (`modal.njk`) now use `{{ description }}` instead of `{{ desc }}` properly aligning with the database schema.
- The update and create modals now inject data into the modal via nunjucks instead of client side Javascript.
- The `utils.base64decode()` & `utils.base64encode()` functions no longer expose url encoding/decoding parameters.

# 1.1.4 / 2018-04-05

**General**

- [SECURITY] Fixed XSS in team website. (#604)
- Fixed deleting challenges that have a hint associated. (#601)

**Themes**

- Removed "SVG with JavaScript" in favor of "Web Fonts with CSS". (#604)

# 1.1.3 / 2018-03-26

**General**

- [SECURITY] Fixed XSS in team name field on team deletion. (#592)
- Fixed an issue where MariaDB defaults in Docker Compose caused difficult to debug 500 errors. (#566)
- Improved Docker usage:
  - Redis cache
  - Configurable amount of workers
  - Easier to access logs
  - Plugin requirements are installed on image build.
  - Switched from the default gunicorn synchronous worker to gevent
- Fixed an issue where ties would be broken incorrectly if there are challenges that are worth 0 points. (#577)
- Fixed update checks not happening on CTFd start. (#595)
- Removed the static_html handler to access raw HTML files. (#561)
  - Pages is now the only supported means of accessing/creating a page.
- Removed uwsgi specific configuration files.
- Fixed issue with Docker image having a hard coded database host name. (#587)

**Themes**

- Fixed scrollbar showing on pages that are smaller than the screen size (#589)
- Fixed displaying the team rank while in workshop mode. (#590)
- Fixed flag modal not clearing when creating multiple new flags. (#594)

**Plugins**

- Add a utility decorator to allow routes to forego CSRF protection. (#596)

# 1.1.2 / 2018-01-23

**General**

- Fixed page links on subdirectory deployments
- Fixed challenge updating on subdirectory deployments
- Fixed broken icon buttons on Safari

**Themes**

- Upgraded to Bootstrap 4.0.0
- Upgraded to jQuery 3.3.1
- Upgraded to FontAwesome 5.0.4

# 1.1.1 / 2018-01-08

**General**

- Fixed regression where users could not be promoted to admins or verified.
- Fixed two icons in the Media Library which were not updated to Font Awesome 5.
- Challenge previews now include tags, hints, and files.
- Fixed an issue where a page could not be published immediately after being saved.

**Themes**

- Upgraded to Bootstrap 4 Beta v3. No major changes needed by themes.
- Fixed issue where the frozen message was not centered in the team page.
- The JavaScript `update()` function now has a callback instead of being hardcoded.
- `chalboard.js` now passes `script_root` into the Nunjucks templates so that file downloads work properly under subdirectories.

# 1.1.0 / 2017-12-22

**Themes**

- The original theme has been replaced by the core theme. The core theme is written in Bootstrap v4.0.0-beta.2 and significantly reduces the amount of custom styles/classes used.
- Challenges can now be previewed from the admin panel.
- The modals to modify files, flags, tags, and hints are no longer controlled by Challenge Type Plugins and are defined in CTFd itself.
- The admin graphs and admin statistics pages have been combined.
- Percentage solved for challenges has been moved to the new statistics page.
- The scoregraph on the scoreboard has been cleaned up to better fit the page width.
- Score graphs now use user-specific colors.
- Hints can now be previewed from the admin panel.
- Various confirmation modals have been replaced with `ezq.js`, a simple Bootstrap modal wrapper.
- Fixed a bug where challenge buttons on the challenge board would load before being styled as solved.
- FontAwesome has been upgraded to FontAwesome 5.
- Themes are now rendered using the Jinja2 SandboxedEnvironment.

**Database**

- `Keys.key_type` has been renamed to `Keys.type`.
- Pages Improvements:
  - Page previews are now independent of the editor page.
  - Pages now have a title which refer to the link's name on the navbar.
  - Pages can now be drafts which cannot be seen by regular users.
  - Pages can now require authentication to view.
  - CSS editing has been moved to the config panel.

**Challenge Type Plugins**

- Handlebars has been replaced with Nunjucks which means Challenge Type Plugins using Handlebars must be updated to work with 1.1.0

**General**

- CTFs can now be paused to prevent solves.
- A new authed_only decorator is available to restrict pages to logged-in users.
- CTFd will now check for updates against `versioning.ctfd.io`. Admins will see in the admin panel that CTFd can be updated.
- A ratelimit function has been implemented. Authentication and email related functions are now ratelimited.
- Code coverage from codecov.
- Admins can now see the reason why an email to a team failed to send.
- SMTP email connections take priority over mailgun settings now. The opposite used to be true.
- The JavaScript `submitkey()` function now takes an optional callback.
- `utils.get_config()` no longer looks at `app.config` values. Instead use `utils.get_app_config()`.
- Only prompt about upgrades when running with a TTY.

# 1.0.5 / 2017-10-25

- Challenge Type Plugins now have a static interface which should be implemented by all challenge types.
  - Challenge Type Plugins are now self-contained in the plugin system meaning you no longer need to manipulate themes in order to register Challenge Type Plugins.
  - Challenge Type plugins should implement the create, read, update, delete, attempt, solve, and fail static methods.
  - Challenge Type plugins now use strings for both their IDs and names.
  - Challenge Type plugins now contain references to their related modal template files.
- Plugins can now register directories and files to be served by CTFd
  - `CTFd.plugins.register_plugin_assets_directory` registers a directory to be served
  - `CTFd.plugins.register_plugin_asset` registers a file to be served
- Plugins can now add to the admin and user menu/nav bars
  - Plugins can now add to the admin menu bar with `CTFd.plugins. register_admin_plugin_menu_bar`
  - Plugins can now add to the user menu bar with `CTFd.plugins. register_user_page_menu_bar`
- Plugins should now use `config.json` to define plugin attributes in lieu of config.html. Backwards compatibility has been maintained. With `config.json`, plugins can now control where the user is linked to instead of being directed to config.html.
- The challenge type and key type columns are now strings.
- Some utils functions now have `CTFd.plugins` wrappers.
- There is now a `/team` endpoint which takes the user to their own public profile.
- Mail server username and passwords are no longer rendered in the Admin Config panel.
- Users can now see their own user graphs when scores are hidden.
- `prepare.sh` is now marked executable.
- Spinners are now properly removed if there is no data to display.

**Always backup your database before upgrading!**

# 1.0.4 / 2017-09-09

- Add spinners to the original theme for loading graphs
- Plugins can register global JS files with `utils.register_plugin_script()`
- Plugins can register global CSS files with `utils.register_plugin_stylesheet()`
- Challenge type plugins can now control the response to a user's input
- Vagrantfile!
- Containers functionality has been moved into a [plugin](https://github.com/CTFd/CTFd-Docker)
- Hide solves from the JSON endpoint when hiding scores.
- The `utils.get_config()` function now checks for lower case and upper case values specified in `config.py`
- Pages are now cached so that we don't hit the database every time we need to load a page.
- The /top/10 endpoint has been changed to group users by ID instead of by name.
- Admins are allowed to see and solve challenges before a CTF starts.
- The CTF time configuration UI has been fixed to allow for the removal of times.
- The score graph in the original theme is now sorted by score.
- Bug fixes
  - Use strings to store IP addresses.
  - Take into account awards when we calculate a user's place.
  - Plugin configuration clears the cache.
  - More logging inside of auth.py.
  - Username and password in the SMTP mail configuration are now optional.
  - Markdown in challenges has been fixed to it's pre-regression state and is easier to write.
  - Improvements to Python 3 compatability.
  - Variety of new tests to further test behavior.
  - Fixed an old bug where users would incorrectly see a challenge with 0 solves.

# 1.0.3 / 2017-07-01

- Increased Unicode support. Smileys everywhere 👌
  - MySQL charset defaults to utf8mb4
- Pages feature now supports Markdown and the Pages editor has a preview button
- IPv6 support for users' IP addresses
- Theme switching no longer requires a server restart
- Admins can now search for teams in the admin panel
- The config.html page for plugins are now Jinja templates giving them much more functionality
- Hints are automatically unlocked once the CTF is finished
- Themes now have a dedicated themes folder
- Graphs are now transparent so that themes can style the background
- Tags are now inserted into the classes of challenge buttons on the default theme
- There is now an `override_template()` function allowing plugins to replace the content of any template loaded by CTFd
- Changes to the email confirmation flow and making confirmation email resending user controlled.

# 1.0.2 / 2017-04-29

- Challenges can now have max attempts set on a per challenge level
- Setup now automatically logs you in as an admin. Don't leave your CTFs unconfigured!
- Tests are now executed by TravisCI! Help out by adding tests for functionality!
- CTFd now has it's own Github organization!
- From a plugin you can replace most of the utils functions used by CTFd. This allows plugins to replace even more functionality within CTFd
- CTFd now has a concept of Hints!
- You can now customize the challenge editting modals in the admin panel
- There are now links to social media pages where you can follow CTFd to track updates.
- CTFd now has the ability to export and import data. This lets you save your CTFs as zip files and redeploy them again and again.

# 1.0.1 / 2017-03-08

- Challenge types
  - This means CTFd now supports multiple kinds of challenges.
  - Challenges are now modifiable with a plugin.
- Solve types
  - This means CTFd now supports multiple kinds of flags/keys.
  - The flag/key logic is now modifiable with a plugin.
- Plugins are now allowed a configuration page
- The formerly massive admin.py is separated out into easier to work on chunks
- Improved Dockerfile and associated docker-compose file
- Fixes Python 3 compatibility
- Fixes a variety of glitches reported by users

- **Always backup database before upgrading!**

# 1.0.0 / 2017-01-24

**Implemented enhancements:**

- 1.0.0 release! Things work!
- Manage everything from a browser
- Run Containers
- Themes
- Plugins
- Database migrations

**Closed issues:**

- Closed out 94 issues before tagging 1.0.0

**Merged pull requests:**

- Merged 42 pull requests before tagging 1.0.0
