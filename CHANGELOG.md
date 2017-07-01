1.0.2 / 2017-07-01
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

***Always backup database before upgrading!**

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