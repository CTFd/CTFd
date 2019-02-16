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
    3. Run the upgrade script from the CTFd root folder i.e. `python migrations/1_2_0_upgrade_2_0_0.py`.
        * This migration script will attempt to migrate data inside the database to 2.0.0 but it cannot account for every situation.
        * Examples of situations where you may need to manually migrate data:
            * Tables/columns created by plugins
            * Tables/columns created by forks
            * Using databases which are not officially supported (e.g. sqlite, postgres)
    4. Setup the rest of CTFd (i.e. config.py), migrate/update any plugins, and run normally.
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