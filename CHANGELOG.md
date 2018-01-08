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