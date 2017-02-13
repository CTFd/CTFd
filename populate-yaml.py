#!/usr/bin/python
# -*- coding: utf-8 -*-
from CTFd.models import Teams, Challenges, Keys, Pages
from CTFd import create_app
from CTFd.utils import set_config
import os
import yaml
import sys

app = create_app()


class Loader(yaml.Loader):
    # https://stackoverflow.com/questions/528281/how-can-i-include-an-yaml-file-inside-another
    def __init__(self, stream):
        self._root = os.path.split(stream.name)[0]
        super(Loader, self).__init__(stream)

    def include(self, node):
        filename = os.path.join(self._root, self.construct_scalar(node))
        with open(filename, 'r') as f:
            return yaml.load(f, Loader)


Loader.add_constructor('!include', Loader.include)


def main():
    with app.app_context():
        db = app.db

        # Generating Challenges
        with open(sys.argv[1], 'r') as handle:
            data = yaml.load(handle, Loader)

        print("CONFIGURING SERVER")
        for key in data['meta']:
            value = data['meta'][key]
            if key in ('admin', 'url', 'homepage'):
                continue

            set_config(key, value)

        set_config('start', '')

        # Index page
        page = Pages('index', data['meta']['homepage'])

        # Start time
        set_config('start', None)
        set_config('end', None)
        set_config('setup', True)
        db.session.add(page)
        db.session.commit()

        print("LOADING CHALLENGES")
        for idx, challenge in enumerate(data['challenges']):
            flags = [{
                'flag': challenge['flag'],
                'type': 0
            }]
            db.session.add(Challenges(
                challenge['title'],
                challenge['body'],
                challenge['points'],
                challenge['category'],
                flags)
            )

            db.session.commit()
            db.session.add(Keys(idx + 1, challenge['flag'], 0))
            db.session.commit()

        # Generating Users
        print("LOADING USERS")
        for user in data.get('users', []) + [data['meta']['admin']]:
            team = Teams(
                user['username'],
                user['email'],
                user['password'],
            )
            if 'admin' in user and user['admin']:
                team.admin = True
            team.verified = True
            db.session.add(team)
        db.session.commit()

        db.session.close()


if __name__ == '__main__':
    main()
