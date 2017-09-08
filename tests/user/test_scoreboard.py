#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.models import Teams, Solves, WrongKeys
from CTFd.utils import get_config, set_config
from CTFd import utils
from tests.helpers import *
from freezegun import freeze_time
from mock import patch
import json


def test_top_10():
    '''Make sure top10 returns correct information'''
    app = create_ctfd()
    with app.app_context():
        register_user(app, name="user1", email="user1@ctfd.io")
        register_user(app, name="user2", email="user2@ctfd.io")

        chal1 = gen_challenge(app.db)
        flag1 = gen_flag(app.db, chal=chal1.id, flag='flag')
        chal1_id = chal1.id

        chal2 = gen_challenge(app.db)
        flag2 = gen_flag(app.db, chal=chal2.id, flag='flag')
        chal2_id = chal2.id

        # Generates solve for user1
        with freeze_time("2017-10-3 03:21:34"):
            gen_solve(app.db, teamid=2, chalid=chal1_id)

        with freeze_time("2017-10-4 03:25:45"):
            gen_solve(app.db, teamid=2, chalid=chal2_id)

        # Generate solve for user2
        with freeze_time("2017-10-3 03:21:34"):
            gen_solve(app.db, teamid=3, chalid=chal1_id)

        client = login_as_user(app)
        r = client.get('/top/10')
        response = r.get_data(as_text=True)

        saved = '''{
          "places": {
            "1": {
              "id": 2,
              "name": "user1",
              "solves": [
                {
                  "chal": 1,
                  "team": 2,
                  "time": 1507000894,
                  "value": 100
                },
                {
                  "chal": 2,
                  "team": 2,
                  "time": 1507087545,
                  "value": 100
                }
              ]
            },
            "2": {
              "id": 3,
              "name": "user2",
              "solves": [
                {
                  "chal": 1,
                  "team": 3,
                  "time": 1507000894,
                  "value": 100
                }
              ]
            }
          }
        }'''
        saved = json.loads(saved)
        received = json.loads(response)
        assert saved == received
    destroy_ctfd(app)
