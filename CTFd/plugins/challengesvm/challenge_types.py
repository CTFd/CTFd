from CTFd.plugins.challenges import BaseChallenge
from flask import render_template

class VMChallenge(BaseChallenge):
    """A virtual machine challenge type."""
    id = "vm"  # This *must* be unique and will be used internally
    name = "Virtual Machine"  # The name displayed to admins

    templates = {
        # This dict maps template modes to file paths
        'create': '/plugins/challengesvm/assets/create.html',
        'update': '/plugins/challengesvm/assets/update.html',
        'view': '/plugins/challengesvm/assets/view.html',
    }
    scripts = {
        # This dict maps script modes to file paths
        'create': '/plugins/challengesvm/assets/create.js',
        'update': '/plugins/challengesvm/assets/update.js',
        'view': '/plugins/challengesvm/assets/view.js',
    }

    @staticmethod
    def create(request, challenge):
        """Method used to process the challenge creation form for this challenge type."""
        vm_image = request.form.get('vm_image')
        challenge.vm_image = vm_image
        return challenge

    @staticmethod
    def read(challenge):
        """Method used to retrieve challenge data for display."""
        data = {
            'vm_image': challenge.vm_image,
        }
        return data

    @staticmethod
    def update(challenge, request):
        """Method used to process the update form for this challenge type."""
        challenge.vm_image = request.form.get('vm_image')
        return challenge

    @staticmethod
    def delete(challenge):
        """Method used to handle any cleanup needed when a challenge is deleted."""
        pass

    @staticmethod
    def attempt(challenge, request):
        """Method used to check if the user's submission is correct."""
        submission = request.form.get('submission')
        if submission == "correct_flag":
            return True, "Correct!"
        else:
            return False, "Incorrect."

    @staticmethod
    def solve(user, challenge, request):
        """Method used to perform any actions when a challenge is solved."""
        pass

    @staticmethod
    def fail(user, challenge, request):
        """Method used to perform any actions when a submission is incorrect."""
        pass
