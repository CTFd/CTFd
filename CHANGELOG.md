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