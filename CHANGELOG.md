2.3.1 / 2020-02-17
==================

**General**
* User confirmation emails now have the correct URL format


2.3.0 / 2020-02-17
==================

**General**
* During setup, admins can register their email address with the CTFd LLC newsletter for news and updates
* Fix editting hints from the admin panel
* Allow admins to insert HTML code directly into the header and footer (end of body tag) of pages. This replaces and supercedes the custom CSS feature.
    * The `views.custom_css` route has been removed.
* Admins can now customize the content of outgoing emails and inject certain variables into email content.
* The `manage.py` script can now manipulate the CTFd Configs table via the `get_config` and `set_config` commands. (e.g. `python manage.py get_config ctf_theme` and `python manage.py set_config ctf_theme core`)

**Themes**
* Themes should now reference the `theme_header` and `theme_footer` configs instead of the `views.custom_css` endpoint to allow for user customizations. See the `base.html` file of the core theme.

**Plugins**
* Make `ezq` functions available to `CTFd.js` under `CTFd.ui.ezq`

**Miscellaneous**
* Python imports sorted with `isort` and import order enforced
* Black formatter running on a majority of Python code


2.2.3 / 2020-01-21
==================

### This release includes a critical security fix for CTFd versions >= 2.0.0

All CTFd administrators are recommended to take the following steps:
1. Upgrade their installations to the latest version
2. Rotate the `SECRET_KEY` value
3. Reset the passwords for all administrator users

**Security**
* This release includes a fix for a vulnerability allowing an arbitrary user to take over other accounts given their username and a CTFd instance with emails enabled

**General**
* Users will receive an email notification when their passwords are reset
* Fixed an error when users provided incorrect team join information


2.2.2 / 2020-01-09
==================

**General**
* Add jQuery, Moment, nunjucks, and Howl to window globals to make it easier for plugins to access JS modules
* Fix issue with timezone loading in config page which was preventing display of CTF times


2.2.1 / 2020-01-04
==================

**General**
* Fix issue preventing admins from creating users or teams
* Fix issue importing backups that contained empty directories


2.2.0 / 2019-12-22
==================

## Notice
2.2.0 focuses on updating the front end of CTFd to use more modern programming practices and changes some aspects of core CTFd design. If your current installation is using a custom theme or custom plugin with ***any*** kind of JavaScript, it is likely that you will need to upgrade that theme/plugin to be useable with v2.2.0.

**General**
* Team size limits can now be enforced from the configuration panel
* Access tokens functionality for API usage
* Admins can now choose how to deliver their notifications
    * Toast (new default)
    * Alert
    * Background
    * Sound On / Sound Off
* There is now a notification counter showing how many unread notifications were received
* Setup has been redesigned to have multiple steps
    * Added Description
    * Added Start time and End time,
    * Added MajorLeagueCyber integration
    * Added Theme and color selection
* Fixes issue where updating dynamic challenges could change the value to an incorrect value
* Properly use a less restrictive regex to validate email addresses
* Bump Python dependencies to latest working versions
* Admins can now give awards to team members from the team's admin panel page

**API**
* Team member removals (`DELETE /api/v1/teams/[team_id]/members`) from the admin panel will now delete the removed members's Submissions, Awards, Unlocks

**Admin Panel**
* Admins can now user a color input box to specify a theme color which is injected as part of the CSS configuration. Theme developers can use this CSS value to change colors and styles accordingly.
* Challenge updates will now alert you if the challenge doesn't have a flag
* Challenge entry now allows you to upload files and enter simple flags from the initial challenge creation page

**Themes**
* Significant JavaScript and CSS rewrite to use ES6, Webpack, yarn, and babel
* Theme asset specially generated URLs
    * Static theme assets are now loaded with either .dev.extension or .min.extension depending on production or development (i.e. debug server)
    * Static theme assets are also given a `d` GET parameter that changes per server start. Used to bust browser caches.
* Use `defer` for script tags to not block page rendering
* Only show the MajorLeagueCyber button if configured in configuration
* The admin panel now links to https://help.ctfd.io/ in the top right
* Create an `ezToast()` function to use [Bootstrap's toasts](https://getbootstrap.com/docs/4.3/components/toasts/)
* The user-facing navbar now features icons
* Awards shown on a user's profile can now have award icons
* The default MarkdownIt render created by CTFd will now open links in new tabs
* Country flags can now be shown on the user pages

**Deployment**
* Switch `Dockerfile` from `python:2.7-alpine` to `python:3.7-alpine`
* Add `SERVER_SENT_EVENTS` config value to control whether Notifications are enabled
* Challenge ID is now recorded in the submission log

**Plugins**
* Add an endpoint parameter to `register_plugin_assets_directory()` and `register_plugin_asset()` to control what endpoint Flask uses for the added route

**Miscellaneous**
* `CTFd.utils.email.sendmail()` now allows the caller to specify subject as an argument
    * The subject allows for injecting custom variable via the new `CTFd.utils.formatters.safe_format()` function
* Admin user information is now error checked during setup
* Added yarn to the toolchain and the yarn dev, yarn build, yarn verify, and yarn clean scripts
* Prevent old CTFd imports from being imported


2.1.5 / 2019-10-2
=================

**General**
* Fixes `flask run` debug server by not monkey patching in `wsgi.py`
* Fix CSV exports in Python 3 by converting StringIO to BytesIO
* Avoid exception on sessions without a valid user and force logout
* Fix several issues in Vagrant provisioning

**API**
* Prevent users from nulling out profile values and breaking certain pages


2.1.4 / 2019-08-31
==================

**General**
* Make user pages show the team's score and place information instead of the user's information if in team mode
* Allow admins to search users by IP address
* Require password for email address changes in the user profile
* The place indicator in `Teams Mode` on the team pages and user pages now correctly excludes hidden teams
* Fix scoreboard place ordinalization in Python 3
* Fix for a crash where imports will fail on SQLite due to lack of ALTER command support
* Fix for an issue where files downloaded via S3 would have the folder name in the filename
* Make `Users.get_place()` and `Teams.get_place()` for return None instead of 0 if the account has no rank/place
* Properly redirect users or 403 if the endpoint requires a team but the user isn't in one
* Show affiliation in user and team pages in the admin panel and public and private user and team pages

**Themes**
* Remove invalid `id='submit'` on submit buttons in various theme files
* Set `tabindex` to 0 since we don't really care for forcing tab order
* Rename `statistics.js` to `graphs.js` in the Admin Panel as it was identified that adblockers can sometimes block the file

**API**
* The team profile endpoint (`/api/v1/teams/me`) will now return 403 instead of 400 if the requesting user is not the captain
* The Challenge API will now properly freeze the solve count to freeze time


2.1.3 / 2019-06-22
==================

**General**
* Fix issue with downloading files after CTF end when `view_after_ctf` is enabled
* Sort solves in admin challenge view by date
* Link to appropriate user and challenge in team, user, and challenge pages
* Redirect to `/team` instead of `/challenges` after a user registers in team mode
* Fixes bug where pages marked as `hidden` weren't loading
* Remove `data-href` from `pages.html` in the Admin Panel to fix the delete button
* Add UI to handle team member removal in Admin Panel
* Fixes account links on the scoreboard page created by `update()`. They now correctly point to the user instead of undefined when in user mode.
* `utils._get_config` will now return `KeyError` instead of `None` to avoid cache misses

**Deployment**
* Use `/dev/shm` for `--worker-tmp-dir` in gunicorn in Docker
* Cache `get_place` code for users and teams.
* Install `Flask-DebugToolbar` in development
* Cache the `/scoreboard` page to avoid having to rebuild the response so often
* Make unprivileged `ctfd` user usable for mysql connection in docker-compose by having the db image create the database instead of CTFd
* Fix bug causing apache2 + mod_wsgi deployments to break

**API**
* Change `/api/v1/teams/[team_id]/members` from taking `id` to `user_id`.
    * Endpoint was unused so the API change is considered non-breaking.
* Add `account_type` and `account_url` field in `/api/v1/scoreboard`
* Separate `/api/v1/[users,teams]/[me,id]/[solves,fails,awards]` into seperate API endpoints
* Clear standings cache after award creation/deletion

**Exports**
* Temporarily disable foreign keys in MySQL, MariaDB, and Postgres during `import_ctf()`
* Add `cache_timeout` parameter to `send_file`response in `/admin/export` to prevent the browser from caching the export

**Tests**
* Fix score changing test helpers to clear standings cache when generating a score changing row


2.1.2 / 2019-05-13
==================

**General**
* Fix freeze time regressions in 2.x
    * Make `/api/v1/[users,teams]/[me]/[solves,fails,awards]` endpoints load as admin so users can see their solves after freeze
    * Make `/api/v1/challenges/[id]/solves` only show solves before freeze time
        * Add the `?preview=true` GET parameter for admins to preview challenges solves as a user
* Team join attempts are now ratelimited

**Tests**
* More linting and autoformatting rules
    * Format Javascript and CSS files with `prettier`: `prettier --write 'CTFd/themes/**/*'`
    * Format Python with `black`: `black CTFd` and `black tests`
    * `make lint` and thus Travis now include the above commands as lint checks
* Travis now uses xenial instead of trusty.


2.1.1 / 2019-05-04
==================

**General**
* Allow admins to hit `/api/v1/challenges` and `/api/v1/challenges/[id]` without having a team to fix challenge previews
* Fix rate-limiting of flag submission when using team mode
* Fixes some modal close buttons not working in the admin panel
* Fixes `populate.py` to assign captains to teams.

**Models**
* Added `Challenges.flags` relationship and moved the `Flags.challenge` relationship to a backref on Challenges
* Added `ondelete='CASCADE'` to most ForeignKeys in models allowing for deletions to remove associated data
    * `Hints` should be deleted when their Challenge is deleted
    * `Tags` should be deleted when their Challenge is deleted
    * `Flags` should be deleted when their Challenge is deleted
    * `ChallengeFiles` should be deleted when their Challenge is deleted
        * Deletion of the file itself is not handled by the model/database
    * `Awards` should be deleted when their user or team is deleted
    * `Unlocks` should be deleted when their user or team is deleted
    * `Tracking` should be deleted when their user or team is deleted
    * `Teams.captain_id` should be set to NULL when the captain user is deleted

**Exports**
* Force `db.create_all()` to happen for imports on `sqlite` or on failure to create missing tables
* Force `ctf_theme` to be set to `core` in imports in case a theme is missing from the import or the instance
* Fix imports/exports to emit and accept JSON properly under MariaDB
    * MariaDB does not properly understand JSON so it must accept strings instead of dicts
    * MariaDB outputs strings instead of JSON for its JSON type so the export serializer will attempt to cast output JSON strings to JSON objects

**Deployment**
* Run as root when using docker-compose
    * This is necessary to be able to write to the volumes mounted from the host


2.1.0 / 2019-04-24
==================

**General**
* Remove Flask-SocketIO in favor of custom Server Side Events code
    * Removed the Flask-SocketIO dependency and removed all related code. See **Deployment** section.
    * Added EventSource polyfill from Yaffle/EventSource
    * Events are now rate-limited and only availble to authenticated users
        * This means real time notifications will only appear to authenticated users
    * Browser localStorage is now used to dictate which tab will maintain the persistent connection to the `/events` endpoint
        * Thanks to https://gist.github.com/neilj/4146038
    * Notifications (currently the only use of the events code) now appear with a notification sound
        * Thanks to [Terrence Martin](https://soundcloud.com/tj-martin-composer) for the sound
* Added UI to delete and download files from the media library
* Progress bars have been added to some actions which could take time
    * To file uploads on challenge page
    * To file uploads on the page editor page
    * To the import CTF functionality
* Challenge file downloads now require a token to download
    * `/files/<path>` now accepts a `?token=` parameter which is a serialized version of `{user_id: <>, team_id: <>, file_id: <>}`
    * If any of these sections are invalid or the user/team is banned the download is blocked
    * This allows files to be downloaded via `curl` or `wget` (i.e. without cookie authentication)
* Added a team captain concept. Team captains can edit team information such as name, team password, website, etc.
    * Only captains can change their team's captain
    * Captains are the first to join the team. But they can be transferred to the true captain later on
* Cache `/api/v1/scoreboard` and `/api/v1/scoreboard/top/[count]`
    * Adds `cache.make_cache_key` because Flask-Caching is unable to cleanly determine the endpoint for Flask-Restplus
    * This helper may change in a future release or be deprecated by an improvement in Flask-Caching
* Properly load hidden and banned properties in the admin team edit modal
* Adds a hover color change on table rows in the admin panel.
    * If a table row specifies the `data-href` attribute it will become clickable
* Add a simple Makefile to wrap some basic commands
    * make lint: lint the code base
    * make test: test the code base
    * make serve: create a debug application server
    * make shell: create a Python shell with the application preloaded
* Started work on a Sphinx documentation site available at [https://docs.ctfd.io](https://docs.ctfd.io)

**Dependencies**
* Upgraded `SQLAlchemy` to 1.3.3 for proper JSON columns in SQLite
* Pin `Werkzeug==0.15.2` in requirements.txt
* Flask-Profiler added to `serve.py --profile`

**Models**
* Awards table now has a `type` column which is used as a polymorphic identity
* Add `Teams.captain_id` column to Teams table

**API**
* Added /api/v1/teams/[team_id]/members
* Cache `/api/v1/scoreboard` and `/api/v1/scoreboard/top/[count]`
    * Adds `cache.make_cache_key` because Flask-Caching is unable to cleanly determine the endpoint for Flask-Restplus
    * This helper may change in a future release or be deprecated by an improvement in Flask-Caching
* Add `/api/v1/users?notify=true` to email user & password after creating new account
* Fix issue where admins could not modify their own profile or their own team

**Plugins**
* `CTFd.utils.security.passwords` deprecated and now available at `CTFd.utils.crypto`
* Built-in challenge plugins now linkify challenge text properly
* Challenge type plugins do not have to append `script_root` to file downloads anymore as that will now be managed by the API
* Awards are now polymorphic and subtables can be created for them

**Themes**
* Fix spelling mistake in `500.html`
* Removed `socket.io.min.js` from `base.html`
* Added EventSource polyfill from Yaffle/EventSource
* Added `howler.js` to play notification sounds
* Vendored/duplicated files which were shared between the `admin` and `core` themes have been de-duped
    * The files used in the `core` theme should now be considered free to use by other themes
* CTF start and end times are now injected into `base.html` and available in the `CTFd.js` object
* Register page now properly says "User Name" instead of "Team Name" since only users can see the Register page
* Users and Teams pages now use a public and private page.
    * user.html -> users/public.html and users/private.html
    * team.html -> teams/public.html and teams/private.html
* Separate `admin/templates/modals/users/create.html` into `admin/templates/modals/users/edit.html`

**Exports**
* Exports will now properly export JSON for all JSON columns
    * In some configurations the column would be exported as a string.
    * Legacy string columns will still be imported properly.
* Exports from old 2.x CTFd versions should upgrade and be installed properly
    * Any failure to do so should be considered a bug

**Deployment**
* User is no longer `root` in Docker image
    * Errors in writing log files will now fail silently as we expect a future rewrite
    * Logs will now also go to stdout
* Update Dockerfile to create and chown/chmod the folders used by `docker-compose` to store files/logs (`/var/log/CTFd`, `/var/uploads`)
    * This allows the container to write to the folder despite it being a volume mounted from the host
* Default worker changed back to `gevent`
* Removed Flask-SocketIO dependency
    * Removed the `SOCKETIO_ASYNC_MODE` config
* `gevent` is now required to allow the Server Sent Events client polling code to work
    * If you use the provided `wsgi.py` or `gevent` gunicorn workers, there shouldn't be any issues
* Cache `/api/v1/scoreboard` and `/api/v1/scoreboard/top/[count]` which is invalidated on new solves or every minute

**Configuration**
* Added `SWAGGER_UI` setting to config.py to control the existence of the `/api/v1/` Swagger UI documentation
* Removed the `SOCKETIO_ASYNC_MODE` config
* Renamed docstring that referenced `SQLALCHEMY_DATABASE_URI` to `DATABASE_URL`
* The `REVERSE_PROXY` configuration can be set to `True` or to a comma seperated string of integers (e.g. `1,1,1,1,1`)
    * See https://werkzeug.palletsprojects.com/en/0.15.x/middleware/proxy_fix/#werkzeug.middleware.proxy_fix.ProxyFix
    * For example to configure `x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1` specify `1,1,1,1,1`

**Tests**
* Tests are now executed in parallel
    * When using a non-memory database, test helpers will now randomize the database name to be able to parallelize execution
* Test tool switched from `nosetests` to `pytest`
* Lint tool switched from `pycodestyle` to `flake8`
* Basic security checking added using `bandit`
* Allow `create_ctfd()` test helper to take app configuration as an argument


2.0.6 / 2019-04-08
==================

**Security**
* Fixes an issue where user email addresses could be disclosed to non-admins

**General**
* Users/Teams set to hidden or banned are no longer visible by other users
    * This affects the API and the main user interface. This does not affect admins
* Users without a Team can no longer view challenges when the CTF is in Team Mode

2.0.5 / 2019-03-23
==================

**Security**
* Fixes an issue where user email addresses could be disclosed to non-admins

**General**
* Dockerfile now installs `linux-headers` package from apk
* Hidden teams are no longer visible publicly
* Fixes an issue where long content made it it difficult/impossible to edit flags and hints
* Fix for users not being able to edit portions of their own profile
* Fix for solves not being frozen for teams.
* Reimplement direct user email sending from the admin panel
* Fixes an issue where confirmation logs would report None instead of the user if the browser was unauthenticated
* Fixes an issue where SMTP server configuration (MAIL_SERVER, MAIL_PORT) were not being read from `config.py`
* Fixes for a user's place on their profile showing a different place than the scoreboard
* Fixes for an issue where dynamic challenge values would appear to change after being solved by a hidden user

**Exports**
* Exports are now saved on disk with `tempfile.NamedTemporaryFile()` instead of memory during creation
* After importing an export, CTFd will now recreate all tables it expects to be available. This resolves an issue where tables created by plugins would be missing after an import.

2.0.4 / 2019-01-30
==================

**General**
* Block user & team name changes if name changes are disabled (Closes #835)
* Set accounts to unconfirmed if email is changed while `verify_emails` is enabled
* Only allow users to change their email to emails with domains in the whitelist.
* Add `email.check_email_is_whitelisted()` to verify that a user's email is whitelisted.
* Create a `get_config` wrapper around the internal `_get_config` to let us set a default config value (Closes #659)
* Remove `utils.get_app_config()` from memoization and also give it a `default` parameter
* Move `utils.logging.init_logs()` into `utils.initialization` and properly call `init_logs()` to save logs to the logs folder
* Block the creation of users/teams from MLC if registration_visibility is private
* Fix showing incorrect 'CTF has ended' error if `view_after_ctf` is set.
* Fix creating users from the admin panel while name changes are disabled.

**API**
* `/api/v1/teams/<team_id>` now coerced to an int (i.e. `/api/v1/teams/<int:team_id>`)

**Deployment**
* Re-add the `LOG_FOLDER` envvar to docker-compose so we don't try to write to the read-only host
* Stop gunicorn from logging to `LOG_FOLDER` in docker without explicit opt-in
* Add `ACCESS_LOG` and `ERROR_LOG` envvars to docker to specify where gunicorn will log to
* Allow `DATABASE_URL` to contain custom MySQL ports for `docker-entrypoint.sh`
* Drop `WORKERS` count to 1 to avoid dealing with Flask-SocketIO sticky sessions'
* Install `gevent-websocket` and use it by default until we have a better solution
* NOTE: In future releases, websockets functionality will likely be removed. (#852)


2.0.3 / 2019-01-12
==================

**Security Release**

This release resolves a security issue that allowed malicious users to hijack admin browser sessions in certain browsers under certain configurations.

The implemented fix is to require the new `CSRF-Token` header on state-changing requests with a Content-Type of application/json.
The same nonce used for standard POST requests is re-used for the `CSRF-Token` header.

Because of the necessary changes to the API, the previously used call to `fetch()` in themes should now be replaced with `CTFd.fetch()`.

**Security**
* Require `CSRF-Token` header on all API requests.
* Require CSRF protection on all HTTP methods except `GET`, `HEAD`, `OPTIONS`, and `TRACE`.
* Default session cookie to `SameSite=Lax`
* Send initial user information request to MajorLeagueCyber over HTTPS

**General**
* Fix `update_check()` logic so that we don't accidentally remove the update notification.

**Themes**
* Remove explicit usage of `script_root` in public JS.
   * In custom themes, use the `CTFd.fetch()` function (defined in `CTFd.js`) and properly register the url root and CSRF nonce in `base.html` as shown below:
    ```javascript
    var script_root = "{{ request.script_root }}";
    var csrf_nonce = "{{ nonce }}";
    CTFd.options.urlRoot = script_root;
    CTFd.options.csrfNonce = csrf_nonce;
    ```
* Reduce required amount of parameters required for static theme files.
   * i.e. `url_for('views.themes')` no longer requires the themes parameter. It now defaults to the currently in-use theme.


2.0.2 / 2019-01-03
==================

**General**
* Fix regression where public challenges could not be attempted by unauthed users.
* Admin Config Panel UI no longer allows changing of user mode.
* Show notification titles and allow for deleting notifications
    * Update notification UI in admin panel to be similar to the public-facing UI
* Fix subdirectory deployments in a generic manner by modifying `request.path` to combine both `request.script_root` and `request.path`.
    * Also create a request preprocessor to redirect users into the true CTFd app when deploying on a subdirectory.
    * Redirect to `request.full_path` instead of just `request.path`.
* Fix `TestingConfig.SAFE_MODE` not being reset between tests.
* Disable `value` input in dynamic challenge update field since we calculate it on the user's behalf.
* Fix displaying incorrect account link in the solves tab of a challenge modal.
* Pin `normality` version because of an upstream issue in `dataset`.
* Fix `500`'s when users submit non-integer values to `?page=1`

**API**
* Add `/api/v1/notifications/<id>` to allow accessing notifactions by ID.
    * This is currently public but will become permission based later in the future
* Add `account_url` field to the response of `/api/v1/<challenge_id>/solves` so the client knows where an account is located.

**Plugins**
* Add new plugin utilities to register javascript and css files for the admin panel.
    * Also fixed issue where those scripts and files were shared between generated applications


2.0.1 / 2018-12-09
==================

2.0.1 is a patch release to fix regressions and bugs in 2.0.0.

If you are upgrading from a version prior to 2.0.0 please read the 2.0.0 change notes for instructions on updating to
2.0.0 before updating to 2.0.1.

**General**
* Fix setting auth for `get_smtp()`.
    * Add `MAIL_USEAUTH` to `config.py`.
* Add more mail documentation to `config.py`.
* Disable jinja cache properly by setting `cache_size` to 0 (#662)
    Regression from 1.2.0.
* Fix downloading files as an anonymous user.
* Fix viewing challenges anonymously if they have empty requirements. Closes #789
    * Allow anonymous users to see see challenges with empty requirements or anonymized challenges
* Clean up admin mail settings to use new label/small structure
* Fix email confirmations and improve test.
* Fix password resets from double hashing passwords

**Themes**
* Change `confirm.html` to use the variable user instead of team

**API**
* Grant admin write access to verified field in UserSchema.
* Fix setting `mail_username`, `mail_password`
* Prevent overriding smtp attributes on config update
* Fix hint loading for admins by adding `/api/v1/hints/<id>?preview=true` for use by admins
* Fixing a bug where prerequisites could not be set for dynamic challenges due to a division by zero error where defaults were being set unnecessarily.

**Exports**
* Fix syncing down an empty S3 bucket
* Fix `S3Uploader` in Python 3 and fix test
* Fix S3 sync function to only pull down files instead of trying to pull directories


2.0.0 / 2018-12-02
==================

2.0.0 is a *significant*, backwards-incompaitble release.

Many unofficial plugins will not be supported in CTFd 2.0.0. If you're having trouble updating your plugins
please join [the CTFd Slack](https://slack.ctfd.io/) for help and discussion.

If you are upgrading from a prior version be sure to make backups and have a reversion plan before upgrading.

* If upgrading from 1.2.0 please make use of the `migrations/1_2_0_upgrade_2_0_0.py` script as follows:
    1. Make all necessary backups. Backup the database, uploads folder, and source code directory.
    2. Upgrade the source code directory (i.e. `git pull`) but do not run any updated code yet.
    3. Set the `DATABASE_URL` in `CTFd/config.py` to point to your existing CTFd database.
    4. Run the upgrade script from the CTFd root folder i.e. `python migrations/1_2_0_upgrade_2_0_0.py`.
        * This migration script will attempt to migrate data inside the database to 2.0.0 but it cannot account for every situation.
        * Examples of situations where you may need to manually migrate data:
            * Tables/columns created by plugins
            * Tables/columns created by forks
            * Using databases which are not officially supported (e.g. sqlite, postgres)
    5. Setup the rest of CTFd (i.e. config.py), migrate/update any plugins, and run normally.
* If upgrading from a version before 1.2.0, please upgrade to 1.2.0 and then continue with the steps above.

**General**

* Seperation of Teams into Users and Teams.
    * Use User Mode if you want users to register as themselves and play on their own.
    * Use Team Mode if you want users to create and join teams to play together.
* Integration with MajorLeagueCyber (MLC). (https://majorleaguecyber.org)
    * Organizers can register their event with MLC and will receive OAuth Client ID & Client Secret.
    * Organizers can set those OAuth credentials in CTFd to allow users and teams to automatically register in a CTF.
* Data is now provided to the front-end via the REST API. (#551)
    * Javascript uses `fetch()` to consume the REST API.
* Dynamic Challenges are built in.
* S3 backed uploading/downloading built in. (#661)
* Real time notifications/announcements. (#600)
    * Uses long-polling instead of websockets to simplify deployment.
* Email address domain whitelisting. (#603)
* Database exporting to CSV. (#656)
* Imports/Exports rewritten to act as backups.
    * Importing no longer stacks values.
    * Exports are no longer partial.
* Reset CTF from config panel (Remove all users, solves, fails. i.e. only keep Challenge data.) (#639)
* Countries are pre-determined and selectable instead of being user-entered.
    * Countries stored based on country code.
    * Based on https://github.com/umpirsky/country-list/blob/master/data/en_US/country.csv.
* Sessions are no longer stored using secure cookies. (#658)
    * Sessions are now stored server side in a cache (`filesystem` or `redis`) allowing for session revocation.
    * In order to delete the cache during local development you can delete `CTfd/.data/filesystem_cache`.
* Challenges can now have requirements which must be met before the challenge can be seen/solved.
* Workshop mode, score hiding, registration hiding, challenge hiding have been changed to visibility settings.
* Users and Teams can now be banned preventing access to the CTF.
* Dockerfile improvements.
    * WORKERS count in `docker-entrypoint.sh` defaults to 1. (#716)
    * `docker-entrypoint.sh` exits on any error. (#717)
* Increased test coverage.
* Create `SAFE_MODE` configuration to disable loading of plugins.
* Migrations have been reset.

**Themes**

* Data is now provided to the front-end via the REST API.
    * Javascript uses `fetch()` to consume the REST API.
* The admin theme is no longer considered seperated from the core theme and should always be together.
* Themes now use `url_for()` to generate URLs instead of hardcoding.
* socket.io (via long-polling) is used to connect to CTFd to receive notifications.
* `ctf_name()` renamed to `get_ctf_name()` in themes.
* `ctf_logo()` renamed to `get_ctf_logo()` in themes.
* `ctf_theme()` renamed to `get_ctf_theme()` in themes.
* Update Font-Awesome to 5.4.1.
* Update moment.js to 2.22.2. (#704)
* Workshop mode, score hiding, registration hiding, challenge hiding have been changed to visibility functions.
    * `accounts_visible()`, `challenges_visible()`, `registration_visible()`, `scores_visible()`

**Plugins**

* Plugins are loaded in `sorted()` order
* Rename challenge type plugins to use `.html` and have simplified names. (create, update, view)
* Many functions have moved around because utils.py has been broken up and refactored. (#475)
* Marshmallow (https://marshmallow.readthedocs.io) is now used by the REST API to validate and serialize/deserialize API data.
    * Marshmallow schemas and views are used to restrict SQLAlchemy columns to user roles.
* The REST API features swagger support but this requires more utilization internally.
* Errors can now be provided between routes and decoraters through message flashing. (CTFd.utils.helpers; get_errors, get_infos, info_for, error_for)
* Email registration regex relaxed. (#693)
* Many functions have moved and now have dedicated utils packages for their category.
* Create `SAFE_MODE` configuration to disable loading of plugins.


1.2.0 / 2018-05-04
==================

**General**

* Updated to Flask 1.0 & switched documentation to suggest using `flask run` instead of `python serve.py`.
* Added the ability to make static & regex flags case insensitive.
* The `/chals` endpoint no longer lists the details of challenges.
    * The `/chals/:id` endpoint is now used to load challenge information before display.
* Admins can now see what users have solved a given challenge from the admin panel.
* Fixed issue with imports extracting files outside of the CTFd directory.
* Added import zipfile validation and optional size restriction.
* The ctftime, authentication, and admin restrictions have been converted to decorators to improve code reuse.
    * 403 is now a more common status code. Previously it only indicated CSRF failure, now it can indicate login failure
    or other Forbidden access situations.
* Challenge previews now work consistently instead of occasionally failing to show.
* Tests are now randomly ordered with `nose-randomly`.

**Themes**

* Admins now have the ability to upload a CTF logo from the config panel.
* Switched from the `marked` library to `Markdown-It` for client side markdown rendering.
    * This will break Challenge type plugins that override the markdown renderer since we are no longer using the marked renderers.
* Introduced the `ezpg()` JS function to make it easier to draw a progressbar modal.
* Introduced the `$.patch()` AJAX wrapper.
* Team names are truncated properly to 50 characters in `teams.html`.
* The admin panel now uses Bootstrap badges instead of buttons to indicate properties such as `admin`, `verified`, `visible`.

**Plugins**

* Challenge type plugins now use a global challenge object with exposed functions to specify how to display a challenge.
(`preRender()`, `render()`, `postRender()`, `submit()`).
    * Challenge type plugins also have access to window.challenge.data which allow for the previously mentioned functions to
    process challenge data and change logic accordingly.
* Challenge type plugins now get full control over how a challenge is displayed via the nunjucks files.
* Challenge plugins should now pass the entire flag/key object to a Custom flag type.
    * This allows the flag type to make use of the data column to decide how to operate on the flag. This is used to implement
    case insensitive flags.
* Challenge modals (`modal.njk`) now use `{{ description }}` instead of `{{ desc }}` properly aligning with the database schema.
* The update and create modals now inject data into the modal via nunjucks instead of client side Javascript.
* The `utils.base64decode()` & `utils.base64encode()` functions no longer expose url encoding/decoding parameters.


1.1.4 / 2018-04-05
==================

**General**

* [SECURITY] Fixed XSS in team website. (#604)
* Fixed deleting challenges that have a hint associated. (#601)

**Themes**

* Removed "SVG with JavaScript" in favor of "Web Fonts with CSS". (#604)


1.1.3 / 2018-03-26
==================

**General**

* [SECURITY] Fixed XSS in team name field on team deletion. (#592)
* Fixed an issue where MariaDB defaults in Docker Compose caused difficult to debug 500 errors. (#566)
* Improved Docker usage:
    * Redis cache
    * Configurable amount of workers
    * Easier to access logs
    * Plugin requirements are installed on image build.
    * Switched from the default gunicorn synchronous worker to gevent
* Fixed an issue where ties would be broken incorrectly if there are challenges that are worth 0 points. (#577)
* Fixed update checks not happening on CTFd start. (#595)
* Removed the static_html handler to access raw HTML files. (#561)
    * Pages is now the only supported means of accessing/creating a page.
* Removed uwsgi specific configuration files.
* Fixed issue with Docker image having a hard coded database host name. (#587)

**Themes**

* Fixed scrollbar showing on pages that are smaller than the screen size (#589)
* Fixed displaying the team rank while in workshop mode. (#590)
* Fixed flag modal not clearing when creating multiple new flags. (#594)

**Plugins**

* Add a utility decorator to allow routes to forego CSRF protection. (#596)


1.1.2 / 2018-01-23
==================

**General**

* Fixed page links on subdirectory deployments
* Fixed challenge updating on subdirectory deployments
* Fixed broken icon buttons on Safari

**Themes**

* Upgraded to Bootstrap 4.0.0
* Upgraded to jQuery 3.3.1
* Upgraded to FontAwesome 5.0.4


1.1.1 / 2018-01-08
==================

**General**

* Fixed regression where users could not be promoted to admins or verified.
* Fixed two icons in the Media Library which were not updated to Font Awesome 5.
* Challenge previews now include tags, hints, and files.
* Fixed an issue where a page could not be published immediately after being saved.

**Themes**

* Upgraded to Bootstrap 4 Beta v3. No major changes needed by themes.
* Fixed issue where the frozen message was not centered in the team page.
* The JavaScript `update()` function now has a callback instead of being hardcoded.
* `chalboard.js` now passes `script_root` into the Nunjucks templates so that file downloads work properly under subdirectories.


1.1.0 / 2017-12-22
==================

**Themes**

* The original theme has been replaced by the core theme. The core theme is written in Bootstrap v4.0.0-beta.2 and significantly reduces the amount of custom styles/classes used.
* Challenges can now be previewed from the admin panel.
* The modals to modify files, flags, tags, and hints are no longer controlled by Challenge Type Plugins and are defined in CTFd itself.
* The admin graphs and admin statistics pages have been combined.
* Percentage solved for challenges has been moved to the new statistics page.
* The scoregraph on the scoreboard has been cleaned up to better fit the page width.
* Score graphs now use user-specific colors.
* Hints can now be previewed from the admin panel.
* Various confirmation modals have been replaced with `ezq.js`, a simple Bootstrap modal wrapper.
* Fixed a bug where challenge buttons on the challenge board would load before being styled as solved.
* FontAwesome has been upgraded to FontAwesome 5.
* Themes are now rendered using the Jinja2 SandboxedEnvironment.

**Database**

* `Keys.key_type` has been renamed to `Keys.type`.
* Pages Improvements:
    * Page previews are now independent of the editor page.
    * Pages now have a title which refer to the link's name on the navbar.
    * Pages can now be drafts which cannot be seen by regular users.
    * Pages can now require authentication to view.
    * CSS editing has been moved to the config panel.

**Challenge Type Plugins**

* Handlebars has been replaced with Nunjucks which means Challenge Type Plugins using Handlebars must be updated to work with 1.1.0

**General**

* CTFs can now be paused to prevent solves.
* A new authed_only decorator is available to restrict pages to logged-in users.
* CTFd will now check for updates against `versioning.ctfd.io`. Admins will see in the admin panel that CTFd can be updated.
* A ratelimit function has been implemented. Authentication and email related functions are now ratelimited.
* Code coverage from codecov.
* Admins can now see the reason why an email to a team failed to send.
* SMTP email connections take priority over mailgun settings now. The opposite used to be true.
* The JavaScript `submitkey()` function now takes an optional callback.
* `utils.get_config()` no longer looks at `app.config` values. Instead use `utils.get_app_config()`.
* Only prompt about upgrades when running with a TTY.


1.0.5 / 2017-10-25
==================

* Challenge Type Plugins now have a static interface which should be implemented by all challenge types.
    * Challenge Type Plugins are now self-contained in the plugin system meaning you no longer need to manipulate themes in order to register Challenge Type Plugins.
    * Challenge Type plugins should implement the create, read, update, delete, attempt, solve, and fail static methods.
    * Challenge Type plugins now use strings for both their IDs and names.
    * Challenge Type plugins now contain references to their related modal template files.
* Plugins can now register directories and files to be served by CTFd
    * `CTFd.plugins.register_plugin_assets_directory` registers a directory to be served
    * `CTFd.plugins.register_plugin_asset` registers a file to be served
* Plugins can now add to the admin and user menu/nav bars
    * Plugins can now add to the admin menu bar with `CTFd.plugins. register_admin_plugin_menu_bar `
    * Plugins can now add to the user menu bar with `CTFd.plugins. register_user_page_menu_bar `
* Plugins should now use `config.json` to define plugin attributes in lieu of config.html. Backwards compatibility has been maintained. With `config.json`, plugins can now control where the user is linked to instead of being directed to config.html.
* The challenge type and key type columns are now strings.
* Some utils functions now have `CTFd.plugins` wrappers.
* There is now a `/team` endpoint which takes the user to their own public profile.
* Mail server username and passwords are no longer rendered in the Admin Config panel.
* Users can now see their own user graphs when scores are hidden.
* `prepare.sh` is now marked executable.
* Spinners are now properly removed if there is no data to display.

**Always backup your database before upgrading!**


1.0.4 / 2017-09-09
==================

* Add spinners to the original theme for loading graphs
* Plugins can register global JS files with `utils.register_plugin_script()`
* Plugins can register global CSS files with `utils.register_plugin_stylesheet()`
* Challenge type plugins can now control the response to a user's input
* Vagrantfile!
* Containers functionality has been moved into a [plugin](https://github.com/CTFd/CTFd-Docker)
* Hide solves from the JSON endpoint when hiding scores.
* The `utils.get_config()` function now checks for lower case and upper case values specified in `config.py`
* Pages are now cached so that we don't hit the database every time we need to load a page.
* The /top/10 endpoint has been changed to group users by ID instead of by name.
* Admins are allowed to see and solve challenges before a CTF starts.
* The CTF time configuration UI has been fixed to allow for the removal of times.
* The score graph in the original theme is now sorted by score.
* Bug fixes
    * Use strings to store IP addresses.
    * Take into account awards when we calculate a user's place.
    * Plugin configuration clears the cache.
    * More logging inside of auth.py.
    * Username and password in the SMTP mail configuration are now optional.
    * Markdown in challenges has been fixed to it's pre-regression state and is easier to write.
    * Improvements to Python 3 compatability.
    * Variety of new tests to further test behavior.
    * Fixed an old bug where users would incorrectly see a challenge with 0 solves.


1.0.3 / 2017-07-01
==================

* Increased Unicode support. Smileys everywhere 👌
    * MySQL charset defaults to utf8mb4
* Pages feature now supports Markdown and the Pages editor has a preview button
* IPv6 support for users' IP addresses
* Theme switching no longer requires a server restart
* Admins can now search for teams in the admin panel
* The config.html page for plugins are now Jinja templates giving them much more functionality
* Hints are automatically unlocked once the CTF is finished
* Themes now have a dedicated themes folder
* Graphs are now transparent so that themes can style the background
* Tags are now inserted into the classes of challenge buttons on the default theme
* There is now an `override_template()` function allowing plugins to replace the content of any template loaded by CTFd
* Changes to the email confirmation flow and making confirmation email resending user controlled.


1.0.2 / 2017-04-29
==================

* Challenges can now have max attempts set on a per challenge level
* Setup now automatically logs you in as an admin. Don't leave your CTFs unconfigured!
* Tests are now executed by TravisCI! Help out by adding tests for functionality!
* CTFd now has it's own Github organization!
* From a plugin you can replace most of the utils functions used by CTFd. This allows plugins to replace even more functionality within CTFd
* CTFd now has a concept of Hints!
* You can now customize the challenge editting modals in the admin panel
* There are now links to social media pages where you can follow CTFd to track updates.
* CTFd now has the ability to export and import data. This lets you save your CTFs as zip files and redeploy them again and again.


1.0.1 / 2017-03-08
==================

* Challenge types
    * This means CTFd now supports multiple kinds of challenges.
    * Challenges are now modifiable with a plugin.
* Solve types
    * This means CTFd now supports multiple kinds of flags/keys.
    * The flag/key logic is now modifiable with a plugin.
* Plugins are now allowed a configuration page
* The formerly massive admin.py is separated out into easier to work on chunks
* Improved Dockerfile and associated docker-compose file
* Fixes Python 3 compatibility
* Fixes a variety of glitches reported by users

* **Always backup database before upgrading!**

1.0.0 / 2017-01-24
==================

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
