# /plugins/gns3/__init__.py
from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.challenges import BaseChallenge, CHALLENGE_CLASSES
from CTFd.models import db, Challenges

class GNS3Challenge(BaseChallenge):
    __mapper_args__ = {'polymorphic_identity': 'gns3'}
    #id = db.Column(None, db.ForeignKey('challenges.id'), primary_key=True)
    id = "gns3"
    name = "GNS3"
    templates = {
        'create': '/plugins/gns3/assets/create.html',
        'update': '/plugins/gns3/assets/update.html',
        'view': '/plugins/gns3/assets/view.html',
    }
    scripts = {
        'create': '/plugins/gns3/assets/create.js',
        'update': '/plugins/gns3/assets/update.js',
        'view': '/plugins/gns3/assets/view.js',
    }

    @classmethod
    def create(cls, request):
        """Called when an admin creates a new GNS3 challenge."""
        name = request.form.get('challenge-name')
        description = request.form.get('challenge-description')
        value = request.form.get('challenge-value')
        category = request.form.get('challenge-category')
        # Create the base challenge row
        chal = Challenges(
            name=name,
            description=description,
            value=value,
            category=category,
            type='gns3'
        )
        db.session.add(chal)
        db.session.commit()
        # Store project_id in extra_data JSON
        project_id = request.form.get('project_id') or ""
        db.session.commit()
        return chal

    @classmethod
    def read(cls, challenge):
        """Return JSON for the edit modal; include our project_id."""
        return {
            'project_id': challenge.extra.get('project_id', "") if challenge.extra else ""
        }

    @classmethod
    def update(cls, challenge, request):
        """Called when an admin updates an existing GNS3 challenge."""
        # Update standard fields
        challenge.name = request.form.get('challenge-name')
        challenge.description = request.form.get('challenge-description')
        challenge.value = request.form.get('challenge-value')
        challenge.category = request.form.get('challenge-category')
        # Update our custom field
        project_id = request.form.get('project_id') or ""
        db.session.commit()
        return challenge

    @classmethod
    def delete(cls, challenge):
        """Called if a GNS3 challenge is deleted."""
        db.session.delete(challenge)
        db.session.commit()

    def __init__(self, name, desc, value, category, type='gns3'):
        self.name = name
        self.description = desc
        self.value = value
        self.category = category
        self.type = type

def load(app):
    app.db.create_all()
    # Register this plugin’s asset directory (JS/HTML/CSS)
    register_plugin_assets_directory(app, base_path='/plugins/gns3/assets/')
    # Register the challenge type
    CHALLENGE_CLASSES['gns3'] = GNS3Challenge
