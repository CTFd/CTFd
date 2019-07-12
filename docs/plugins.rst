Plugins
=======

Introduction
------------

CTFd features a plugin interface allowing for the modification of CTFd behavior without modifying the core CTFd code. This has a number of benefits over forking and modifying CTFd:

* Your modifications and plugins can be shared more easily
* CTFd can be updated without losing any custom behavior

The CTFd developers will do their best to not introduce breaking changes but keep in mind that the plugin interface is still under development and could change.

.. Tip::
   Official CTFd plugins are available at https://ctfd.io/store. `Contact us <https://ctfd.io/contact/>`_ regarding custom plugins and special projects.

.. Tip::
   Community plugins are available at https://github.com/CTFd/plugins.

Architecture
------------

CTFd plugins are implemented as Python modules with some CTFd specific files.

::

    CTFd
    └── plugins
       └── CTFd-plugin
           ├── README.md          # README file
           ├── __init__.py        # Main code file loaded by CTFd
           ├── requirements.txt   # Any requirements that need to be installed
           └── config.json        # Plugin configuration file

Effectively CTFd will look at every folder in the ``CTFd/plugins`` folder for the ``load()`` function.

If the ``load()`` function is found, CTFd will call that function with itself (as a Flask app) as a parameter (i.e. ``load(app)``). This is done after CTFd has added all of its internal routes but before CTFd has fully instantiated itself. This allows plugins to modify many aspects of CTFd without having to modify CTFd itself.

config.json
~~~~~~~~~~~

``config.json`` exists to give plugin developers a way to define attributes about their plugin. It's primary usage within CTFd is to give users a way to access a Configuration or Settings page for the plugin.

This is an example ``config.json`` file:

.. code-block:: json

    {
        "name": "CTFd Plugin",
        "route": "/admin/custom_plugin_route"
    }

This is ultimately rendered to the user with the following template snippet:

.. code-block:: html

    {% if plugins %}
    <li>
        <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">Plugins <span class="caret"></span></a>
        <ul class="dropdown-menu">
                {% for plugin in plugins %}
                        <li><a href="{{ request.script_root }}{{ plugin.route }}">{{ plugin.name }}</a></li>
                {% endfor %}
        </ul>
    </li>
    {% endif %}

config.html
~~~~~~~~~~~

In the past CTFd used a static file known as ``config.html`` which existed to give plugin developers a page that is loaded by the CTFd admin panel. This has been superceded in favor of `config.json` but is still supported for backwards compatability.

The ``config.html`` file for a plugin is available by CTFd admins at ``/admin/plugins/<plugin-folder-name>``. Thus if ``config.html`` is stored in ``CTFd-S3-plugin``, it would be available at ``/admin/plugins/CTFd-S3-plugin``.

``config.html`` is loaded as a Jinja template so it has access to all of the same functions and abilities that CTFd exposes to Jinja. Jinja templates are technically also capable of running arbitrary Python code but this is ancillary.

Adding New Routes
-----------------

Adding new routes in CTFd is effectively just an exercise in writing new Flask routes. Since the plugin itself is passed the entire app, the plugin can leverage the ``app.route`` decorator to add new routes.

A simple example is as follows:

.. code-block:: python

    from flask import render_template


    def load(app):
        @app.route('/faq', methods=['GET'])
        def view_faq():
            return render_template('page.html', content="<h1>FAQ Page</h1>")

Modifying Existing Routes
-------------------------

It is slightly more complicated to override existing routes in CTFd/Flask because it is not strictly supported by Flask. The approach currently used is to modify the ``app.view_functions`` dictionary which contains the mapping of routes to the functions used to handle them.


.. code-block:: python

    from flask import render_template

    from CTFd.models import db
    from CTFd.utils import admins_only, is_admin

    from CTFd import utils

    def load(app):
        def view_challenges():
            return render_template('page.html', content="<h1>Challenges are currently closed</h1>")

        # The format used by the view_functions dictionary is blueprint.view_function_name
        app.view_functions['challenges.challenges_view'] = view_challenges

If for some reason you wish to add a new method to an existing route you can modify the ``url_map`` as follows:

.. code-block:: python

    from werkzeug.routing import Rule

    app.url_map.add(Rule('/challenges', endpoint='challenges.challenges_view', methods=['GET', 'POST']))

Adding Database Tables
----------------------

Sometimes CTFd doesn't have enough database tables or columns to let you do what you need. In this case you can use a plugin to create a new table and then use the information in the previous two sections to create routes or modify existing routes to access your new table.

.. code-block:: python

    from CTFd.models import db


    class Avatars(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        team = db.Column(db.Integer, db.ForeignKey('teams.id'))
        location = db.Column(db.Text)

        def __init__(self, team, location):
            self.target = team
            self.location = location


    def load(app):
        app.db.create_all()
        @app.route('/profile/avatar', methods=['GET', 'POST'])
        def profile_avatars():
            raise NotImplementedError

Replacing Templates
-------------------

In some situations it might make sense for your plugin to replace the logic for a single page template instead of creating an entire theme.

The ``utils.override_template()`` function allows a plugin to replace the content of a single template within CTFd such that CTFd will use the new content instead of the content in the original file.

.. code-block:: python

    from CTFd.utils import override_template
    import os

    def load(app):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        template_path = os.path.join(dir_path, 'new-scoreboard.html')
        override_template('scoreboard.html', open(template_path).read())

With this code CTFd will use ``new-scoreboard.html`` instead of the ``scoreboard.html`` file it normally would have used.


Registering Assets
------------------

Very often you will want to provide users with static assets (e.g. JS, CSS). Instead of registering handlers for them on your own, you can use the CTFd built in plugin utilities, ``register_plugin_assets_directory`` and ``register_plugin_asset``.

For example to register an entire assets directory as available to the user:

.. code-block:: python

    from CTFd.plugins import register_plugin_assets_directory

    def load(app):
        # Available at http://ctfd/plugins/test_plugin/assets/
        register_plugin_assets_directory(app, base_path='/plugins/test_plugin/assets/')


Or to only provide a single file:

.. code-block:: python

    from CTFd.plugins import register_plugin_asset

    def load(app):
        # Available at http://ctfd/plugins/test_plugin/assets/file.js
        register_plugin_asset(app, asset_path='/plugins/test_plugin/assets/file.js')


Challenge Types
---------------

In CTFd, there is a concept of a type of challenge. Most CTFs only ever provide challenges as a snippet of text alongside some files. CTFd expands upon this and allows developers to create new challenge types which diversify what users will see.

Ultimately, users will still read some text, and submit some value but CTFd allows you to style and customize this so users can submit data in new ways.

For example, instead of an input to submit a single flag value, you might require teams to submit multiple flags or you might create some kind of customized UI where teams need to arrange blocks or text in some order.

The approach used by CTFd here is to give each "type" of challenge an ID and a name.

.. Tip::
    You can see how CTFd implements its `default standard challenge here <https://github.com/CTFd/CTFd/blob/master/CTFd/plugins/challenges/__init__.py>`_. You can also see how CTFd implements `dynamic scoring using this feature <https://github.com/CTFd/CTFd/tree/master/CTFd/plugins/dynamic_challenges>`_.

Each challenge is implemented as a child class of the ``BaseChallenge`` and implements static methods named ``create``, ``read``, ``update``, ``delete``, ``attempt``, ``solve``, and ``fail``.

When a user attempts to solve a challenge, CTFd will look up the challenge type and then call the ``solve`` method as shown in the following snippet of code:

.. code-block:: python

    chal_class = get_chal_class(chal.type)
    status, message = chal_class.attempt(chal, request)

    if status:  # The challenge plugin says the input is right
        if ctftime() or is_admin():
            chal_class.solve(team=team, chal=chal, request=request)
        return jsonify({'status': 1, 'message': message})

    else:  # The challenge plugin says the input is wrong
        if ctftime() or is_admin():
            chal_class.fail(team=team, chal=chal, request=request)

This structure allows each Challenge Type to dictate how they are attempted, solved, and marked incorrect.

The Challenge Type also dictates the database table that it uses to store data. By default this uses the ``type`` column as a ``polymorphic_identity`` to implement `table inheritance <http://docs.sqlalchemy.org/en/latest/orm/inheritance.html#joined-table-inheritance>`_. Effectively each child table will use the Challenges table as a parent. The child table can add whatever columns it wishes but still leverage the existing columns from the parent.

We can see in the following code that the polymorphic_identity is specified to be ``dynamic`` as well as the ``type`` parameter. We can also see the call to ``create_all()`` which will create the table in our database.

.. code-block:: python

    class DynamicChallenge(Challenges):
        __mapper_args__ = {'polymorphic_identity': 'dynamic'}
        id = db.Column(None, db.ForeignKey('challenges.id'), primary_key=True)
        initial = db.Column(db.Integer)
        minimum = db.Column(db.Integer)
        decay = db.Column(db.Integer)

        def __init__(self, name, description, value, category, type='dynamic', minimum=1, decay=50):
            self.name = name
            self.description = description
            self.value = value
            self.initial = value
            self.category = category
            self.type = type
            self.minimum = minimum
            self.decay = decay


    def load(app):
        app.db.create_all()
        CHALLENGE_CLASSES['dynamic'] = DynamicValueChallenge
        register_plugin_assets_directory(app, base_path='/plugins/DynamicValueChallenge/assets/')

This code creates the necessary tables for the Challenge Type plugin which should be used in addition to the staticmethods used to define the challenge's behavior.

Every challenge type must be added to the global dictionary that specifies all challenge types:

.. code-block:: python

    CHALLENGE_CLASSES = {
        "standard": CTFdStandardChallenge
    }


    def get_chal_class(class_id):
        cls = CHALLENGE_CLASSES.get(class_id)
        if cls is None:
            raise KeyError
        return cls

The `Standard Challenge type <https://github.com/CTFd/CTFd/tree/master/CTFd/plugins/challenges>`_ provided within CTFd can be used as a base from which to build additional Challenge Type plugins.

Once new challenges are registered, CTFd will provide a dropdown allowing you to choose from all the challenge types you can create.

Each Challenge Type contains templates and scripts dictionaries which contain the routes for HTML and JS files needed for the operation of the modals used to create and update the challenges.

**These routes are not automatically defined by CTFd.**

Each challenge type plugin specifies the location of their own templates and scripts. An example is the built in `standard challenge type plugin <https://github.com/CTFd/CTFd/blob/master/CTFd/plugins/challenges/__init__.py>`_. It specifies the URLs that the assets are located at for the user's browser to load:

.. code-block:: python

    templates = {  # Templates used for each aspect of challenge editing & viewing
        'create': '/plugins/challenges/assets/create.html',
        'update': '/plugins/challenges/assets/update.html',
        'view': '/plugins/challenges/assets/view.html',
    }
    scripts = {  # Scripts that are loaded when a template is loaded
        'create': '/plugins/challenges/assets/create.js',
        'update': '/plugins/challenges/assets/update.js',
        'view': '/plugins/challenges/assets/view.js',
    }

These files are registered with Flask with the following code:

.. code-block:: python

    from CTFd.plugins import register_plugin_assets_directory

    def load(app):
        register_plugin_assets_directory(app, base_path='/plugins/challenges/assets/')


The aforementioned code handles the Python logic around new challenges but in order to fully integrate with CTFd you will need to create new Nunjucks templates to give admins/teams the ability to modify/update/solve your challenge. The `templates used by the Standard Challenge Type <https://github.com/CTFd/CTFd/tree/master/CTFd/plugins/challenges/assets>`_ should serve as examples.

Flag Types
----------

Flag types conversely are used to give developers a way to allow teams to submit flags which do not conform to a hardcoded string or a regex-able value.

The approach is very similar to Challenges with a base Flag/Key class and a global dictionary specifying all the Flag/Key types:

.. code-block:: python

    class BaseFlag(object):
        name = None
        templates = {}

        @staticmethod
        def compare(self, saved, provided):
            return True


    class CTFdStaticFlag(BaseFlag):
        name = "static"
        templates = {  # Nunjucks templates used for key editing & viewing
            "create": "/plugins/flags/assets/static/create.html",
            "update": "/plugins/flags/assets/static/edit.html",
        }

        @staticmethod
        def compare(chal_key_obj, provided):
            saved = chal_key_obj.content
            data = chal_key_obj.data

            if len(saved) != len(provided):
                return False
            result = 0

            if data == "case_insensitive":
                for x, y in zip(saved.lower(), provided.lower()):
                    result |= ord(x) ^ ord(y)
            else:
                for x, y in zip(saved, provided):
                    result |= ord(x) ^ ord(y)
            return result == 0


    class CTFdRegexFlag(BaseFlag):
        name = "regex"
        templates = {  # Nunjucks templates used for key editing & viewing
            "create": "/plugins/flags/assets/regex/create.html",
            "update": "/plugins/flags/assets/regex/edit.html",
        }

        @staticmethod
        def compare(chal_key_obj, provided):
            saved = chal_key_obj.content
            data = chal_key_obj.data

            if data == "case_insensitive":
                res = re.match(saved, provided, re.IGNORECASE)
            else:
                res = re.match(saved, provided)

            return res and res.group() == provided


    FLAG_CLASSES = {"static": CTFdStaticFlag, "regex": CTFdRegexFlag}


    def get_flag_class(class_id):
        cls = FLAG_CLASSES.get(class_id)
        if cls is None:
            raise KeyError
        return cls

When a challenge solution is submitted, the challenge plugin itself is responsible for:

1. Loading the appropriate Key class using the ``get_flag_class()`` function.
2. Properly calling the static ``compare()`` method defined by each Flag class.
3. Returning the correctness boolean and the message displayed to the user.

This is properly implemented by the following code `copied from the default standard challenge <https://github.com/CTFd/CTFd/blob/master/CTFd/plugins/challenges/__init__.py#L136>`_:

.. code-block:: python

    @staticmethod
    def attempt(challenge, request):
        data = request.form or request.get_json()
        submission = data['submission'].strip()
        flags = Flags.query.filter_by(challenge_id=challenge.id).all()
        for flag in flags:
            if get_flag_class(flag.type).compare(flag, submission):
                return True, 'Correct'
        return False, 'Incorrect'
