Real-life plugin walkthrough
============================

0. Introduction
---------------
Provided the overall lack of documentation about CTFd plugins, I decided to write a 'real-life example' of a plugin's creation.
This guide covers a small part of my own plugin created for the need of the company I work for. Basically, we use the plugin to synchrnize Gitlab pipelines with CTFd (solve challenges when pipelines passes).

.. Tip::
    The most important and most basic tip I can have for this guide: clone the CTFd repository, have it always opened in your favorite IDE and be ready to Ctrl-Click & read CTFd's code. Exploring is the key!

1. What we're going to do
-------------------------
The plugin we're going to write wil have one basic goal the automation of creation of a Gitlab account when a new user sign up for our CTFd instance.


2. Setup
--------
I personally use a Docker image for development, but you can just set it up on your own computer.
Here's my Dockerfile / docker-compose:

.. code-block:: Dockerfile

    FROM ctfd/ctfd

    RUN pip install --user python-gitlab # dependencies
    ENV PYTHONUNBUFFERED 1 # easier to debug

    ENTRYPOINT ["python", "serve.py"]

.. code-block:: yaml
    
    version: "3.7"

    services:
      ctfd-dev:

        build:
          context: .
          dockerfile: dev.Dockerfile

        ports:
          - 4000:4000

        volumes:
          - ./seculabs-trainings:/opt/CTFd/CTFd/plugins/seculabs-trainings
          - ./serve.py:/opt/CTFd/serve.py
          - ./ctfd.db:/opt/CTFd/CTFd/ctfd.db

        restart: always


I customize the `serve.py` file to use debug mode:

.. code-block:: python

    from CTFd import create_app, socketio

    app = create_app()

    # Debug mode, listening on any hosts
    socketio.run(app, debug=True, host="0.0.0.0", port=4000)


3. Plugin architecture
----------------------
Let's create a directory that will hold our source files, config files, etc, and `touch` a few files.

.. code-block:: bash

    mkdir my_plugin
    touch my_plugin/config.json # Plugin configuration
    touch my_plugin/__init__.py # File executed when plugin loads
    touch my_plugin/blueprint.py # Flask blueprint source code
    touch my_plugin/challenge.py # Custom challenge source code
    touch my_plugin/controllers.py # Controllers source code
    touch my_plugin/hooks.py # Hooks source code
    
And that should do it. No worries, every file will be written during this guide.

Let's write the `config.json` file right now:

.. code-block:: json

    {
        "name": "My Plugin",
        "route": "/admin/my_plugin"
    }

And `__init__.py`:

.. code-block:: python
    
    def load(app):
        print("My plugin is ready!")


Yay, we just registered a new plugin to the CTFd instance!
If you `docker-compose up --build` now, you should see (among other things):

.. code-block:: bash

    ctfd-dev_1  | My plugin is loaded!
    ctfd-dev_1  |  * Loaded module, <module 'CTFd.plugins.my_plugin' from '/opt/CTFd/CTFd/plugins/my_plugin/__init__.pyc'>
    ctfd-dev_1  |  * Debugger is active!
    ctfd-dev_1  |  * Debugger PIN: 118-698-857


4. Admin configuration page
---------------------------

Okay, so we will probably need a way to hold our configuration. CTFd stores `things` in a SQLite database, so we'll juste use that.

If you login as an admin and access the admin configuration page (Login as admin > Admin > Plugins > My Plugin), you'll get a 404, because CTFd does not provides any default way to handle plugins pages.
That's why we'll use the `blueprint.py` file for. I'm assuming you have a correct unsderstanding of Flask and its concepts.

.. code-block:: python

    from flask import request, render_template, Blueprint, abort
    from .controllers import ConfigController

    my_plugin_bp = Blueprint("my_plugin", __name__, template_folder="templates")

    def load_bp(plugin_route):
        @my_plugin_bp.route(plugin_route, methods=["GET"])
        def get_config():
            config = ConfigController.get_all()
            return render_template("config.html", all_config=config)

        @my_plugin_bp.route(plugin_route, methods=["POST"])
        def update_config():
            conf = request.form.to_dict()
            del conf["nonce"]

            ConfigController.update_all(conf)
            return get_config()

        return my_plugin_bp

We basically register two methods for the same route (defined in our `config.json` file), one to retrieve the configuration (GET) and one to update it (POST).
You might have seen that I've introduced the :code:`controller` notion here, let's juste create a :code:`ConfigController` in the `controllers.py` file which does nothing - we will update it later.

.. code-block:: python

    class ConfigController:
        @staticmethod
        def get_all():
            return []

        @staticmethod
        def update_all(conf):
            pass


For that to work, we must call the :code:`load_bp` function in our `__init__.py` file:

.. code-block:: python

    import json
    import os

    from .blueprint import load_bp
    from .controllers import ConfigController

    PLUGIN_PATH = os.path.dirname(__file__)
    CONFIG = json.load(open("{}/config.json".format(PLUGIN_PATH)))


    def load(app):
        app.db.create_all()

        ConfigController.load_default()

        bp = load_bp(CONFIG["route"])
        app.register_blueprint(bp)


Here we read the configuration file, create all DB entities, and load our default configuration settings (detailed below).
Lastly, load the blueprint and register it in the Flask app.

Now, you can go to the plugin page (Admin > Plugins > My Plugin). This will raise a Jinja2 exception because we haven't yet created the template, that's what we're going to do next!

Now we need to add the template file used in our blueprint. To do so, create a new directory :code:`my_plugin/templates` and a :code:`config.html` file inside it.
I'm assuming you're a bit familiar with templating engines.

.. code-block:: html

    {% extends "admin/base.html" %}

    {% block content %}

    <style>.body { margin-top: 3vh; }</style>

    <div class="container body">
        <h2>My Plugin configuration</h2>

        <form method="POST">
            {% for config in all_config %}
                <div class="form-group">
                    <label for="{{ config.key }}">{{ config.key }}</label>
                    <input type="text" value="{{ config.value }}" name="{{ config.key }}" id="{{ config.key }}" class="form-control" />
                </div>
            {% endfor %}

            <input type="hidden" value="{{ nonce }}" name="nonce" id="nonce" />

            <button type="submit" class="btn btn-primary">Update configuration</button>
        </form>
    </div>

    {% endblock %}

This will just render a form with an input for each configuration key/value pair.
The hidden input is the nonce, aka a CSRF token. It must be included in every form you create (unless the route have a :code:`bypass_csrf_protection` decorator).

The last step now is to update the :code:`ConfigController`. I'm assuming decent knowledge of SQLAlchemy.

.. code-block:: python

    import functools

    from CTFd.models import Configs, db


    class ConfigController:
        DEFAULT_CONFIG = [
            {"key": "MP_GITLAB_URL", "value": ""},
            {"key": "MP_GITLAB_TOKEN", "value": ""},
            {"key": "MP_GITLAB_DEFAULT_PASSWORD", "value": ""},
        ]

        # Some magic to filter by configuration keys
        FBY_CONFIG_KEYS = functools.reduce(lambda x, y: x | (
            Configs.key == y["key"]), DEFAULT_CONFIG, Configs.key)

        @staticmethod
        def get_all():
            return Configs.query.filter(ConfigController.FBY_CONFIG_KEYS).all()

        # Will be used later
        @staticmethod
        def get(key):
            return Configs.query.filter_by(key=key).first()

        @staticmethod
        def update(key, value):
            cv = Configs.query.filter_by(key=key).first()
            if not cv:
                raise KeyError("Config key %s not found" % key)

            cv.value = value

        @staticmethod
        def update_all(conf):
            for key in conf:
                ConfigController.update(key, conf[key])
            db.session.commit()

        @staticmethod
        def load_default():
            for cv in ConfigController.DEFAULT_CONFIG:
                # Query for the config setting
                k = Configs.query.filter_by(key=cv["key"]).first()

                # If its not created yet, create it with its default value
                if not k:
                    c = Configs(key=cv["key"], value=cv["value"])
                    db.session.add(c)

            db.session.commit()

Obivously, to write this I read multiple times the source of the `CTFd/models.py` file, which I urge you to do as well!

We now have a configuration readable, editable and saved in CTFd database!

5. Creating a gitlab account on user creation
---------------------------------------------

Let's follow the same pattern to load our hooks (hook on user account creation):

In the `hooks.py` file, add this code:

.. code-block:: python

    from sqlalchemy.event import listen
    from CTFd.models import Users
    from .controllers import GitlabController

    def on_users_create(mapper, conn, user):
        GitlabController.create_user(user.email, user.name)

    def load_hooks():
        listen(Users, "after_insert", on_users_create)


This is very basic, we listen for the after_insert (after because it ensures the CTFd account is valid and will be created) using SQLAlchemy, and call our GitlabController which we will be writing just below:

.. code-block:: python

    class GitlabController:
        @staticmethod
        def gitlab_instance():
            url = ConfigController.get("MP_GITLAB_URL").value
            token = ConfigController.get("MP_GITLAB_TOKEN").value

            return gitlab.Gitlab(url, private_token=token)

        @staticmethod
        def create_user(email, name):
            gl = GitlabController.gitlab_instance()

            user = gl.users.create({
                "email": email,
                "password": ConfigController.get("MP_GITLAB_DEFAULT_PASSWORD").value,
                "username": name,
                "name": name,
                "skip_confirmation": True
            })

            return user

We're using the :code:`python-gitlab` package installed with Pip (which already is in our Dockerfile). The code above is just a copy/paste of the example provided in the documentation of :code:`python-gitlab`.

Lastly, we just have to update our `init.py` file to call the :code:`load_hooks` method.


6. The end
----------

I hope this covered less documented features of CTFd, and this will be able to help some new plugin developers.

.. Tip::
    The CTFd Slack is quite active and helpful for plugin development! 

To achieve the goal I edicted in the introduction, we need a few more steps:

1. After Gitlab account creation, fork the main project and setup integration webhooks.
2. Add a new route to the blueprint to handle gitlab's webhook and solve challenge.
3. This needs a lot of reading CTFd's code for challenges! Don't be afraid to do so.
