from django import db

from CTFd.api.v1.websockets import emit_challenge_statistics, emit_scoreboard_statistics, emit_scores_distribution, emit_solve_percentages_statistics, emit_submissions_statistics, emit_teams_statistics, emit_users_statistics
from CTFd.models import Challenges, Fails, Solves, Submissions, Teams, Users


def test_emit_challenge_statistics(app, socket_client):
    with app.app_context():
        # Create test data
        challenge1 = Challenges(name="Challenge 1", value=100, category="Category 1")
        challenge2 = Challenges(name="Challenge 2", value=200, category="Category 2")
        db.session.add_all([challenge1, challenge2])
        db.session.commit()

        user = Users(name="test_user", email="test@example.com", password="password")
        db.session.add(user)
        db.session.commit()

        solve1 = Solves(account_id=user.id, challenge_id=challenge1.id)
        fail1 = Fails(account_id=user.id, challenge_id=challenge1.id)
        db.session.add_all([solve1, fail1])
        db.session.commit()

        # Connect to SocketIO
        socket_client.connect()

        # Trigger the function
        emit_challenge_statistics()

        # Check emitted data
        received = socket_client.get_received()
        assert len(received) > 0
        message = received[0]
        assert message['name'] == 'challenge_stats'
        data = message['args'][0]['data']
        assert len(data) == 2
        assert data[0]['name'] == "Challenge 1"
        assert data[0]['solves'] == 1
        assert data[0]['unsolved'] == 1
        assert data[0]['category'] == "Category 1"
        assert data[0]['points'] == 100
        assert data[1]['name'] == "Challenge 2"
        assert data[1]['solves'] == 0
        assert data[1]['unsolved'] == 0
        assert data[1]['category'] == "Category 2"
        assert data[1]['points'] == 200

        # Clean up
        db.session.delete(solve1)
        db.session.delete(fail1)
        db.session.delete(user)
        db.session.delete(challenge1)
        db.session.delete(challenge2)
        db.session.commit()

def test_emit_scores_distribution(app, socket_client):
    with app.app_context():
        # Create test data
        user1 = Users(name="user1", email="user1@example.com", password="password")
        user2 = Users(name="user2", email="user2@example.com", password="password")
        db.session.add_all([user1, user2])
        db.session.commit()
        
        emit_scores_distribution()

        # Check emitted data
        received = socket_client.get_received()
        assert len(received) > 0
        message = received[-1]
        assert message['name'] == 'scores_distribution'
        data = message['args'][0]['data']['brackets']
        assert isinstance(data, dict)
        assert sum(data.values()) == 2  # Two users

        # Clean up
        db.session.delete(user1)
        db.session.delete(user2)
        db.session.commit()

def test_emit_submissions_statistics(app, socket_client):
    with app.app_context():
        # Create test data
        user = Users(name="test_user", email="test@example.com", password="password")
        db.session.add(user)
        db.session.commit()

        submission1 = Submissions(type="correct", account_id=user.id)
        submission2 = Submissions(type="incorrect", account_id=user.id)
        db.session.add_all([submission1, submission2])
        db.session.commit()

        emit_submissions_statistics()

        # Check emitted data
        received = socket_client.get_received()
        assert len(received) > 0
        message = received[-1]
        assert message['name'] == 'submissions_stats'
        data = message['args'][0]['data']
        assert data['correct'] == 1
        assert data['incorrect'] == 1

        # Clean up
        db.session.delete(submission1)
        db.session.delete(submission2)
        db.session.delete(user)
        db.session.commit()

def test_emit_teams_statistics(app, socket_client):
    with app.app_context():
        # Create test data
        team1 = Teams(name="Team 1")
        team2 = Teams(name="Team 2")
        db.session.add_all([team1, team2])
        db.session.commit()

        emit_teams_statistics()

        # Check emitted data
        received = socket_client.get_received()
        assert len(received) > 0
        message = received[-1]
        assert message['name'] == 'teams_stats'
        data = message['args'][0]['data']
        assert data['registered'] == 2

        # Clean up
        db.session.delete(team1)
        db.session.delete(team2)
        db.session.commit()

def test_emit_users_statistics(app, socket_client):
    with app.app_context():
        # Create test data
        user1 = Users(name="user1", email="user1@example.com", password="password", verified=True)
        user2 = Users(name="user2", email="user2@example.com", password="password", verified=False)
        db.session.add_all([user1, user2])
        db.session.commit()

        emit_users_statistics()

        # Check emitted data
        received = socket_client.get_received()
        assert len(received) > 0
        message = received[-1]
        assert message['name'] == 'users_stats'
        data = message['args'][0]['data']
        assert data['registered'] == 2
        assert data['confirmed'] == 1

        # Clean up
        db.session.delete(user1)
        db.session.delete(user2)
        db.session.commit()

def test_emit_solve_percentages_statistics(app, socket_client):
    with app.app_context():
        # Create test data
        challenge = Challenges(name="Test Challenge", value=100)
        db.session.add(challenge)
        db.session.commit()

        user = Users(name="test_user", email="test@example.com", password="password")
        db.session.add(user)
        db.session.commit()

        solve = Solves(account_id=user.id, challenge_id=challenge.id)
        fail = Fails(account_id=user.id, challenge_id=challenge.id)
        db.session.add_all([solve, fail])
        db.session.commit()

        emit_solve_percentages_statistics()

        # Check emitted data
        received = socket_client.get_received()
        assert len(received) > 0
        message = received[-1]
        assert message['name'] == 'solve_percentages_stats'
        data = message['args'][0]['data']
        assert data['solved'] == 1
        assert data['unsolved'] == 1
        assert len(data['challenges']) == 1
        assert data['challenges'][0]['solve_percentage'] == 50.0
        assert data['challenges'][0]['unsolve_percentage'] == 50.0

        # Clean up
        db.session.delete(solve)
        db.session.delete(fail)
        db.session.delete(user)
        db.session.delete(challenge)
        db.session.commit()

def test_emit_scoreboard_statistics(app, socket_client):
    with app.app_context():
        # Create test data
        user1 = Users(name="user1", email="user1@example.com", password="password")
        user2 = Users(name="user2", email="user2@example.com", password="password")
        db.session.add_all([user1, user2])
        db.session.commit()

        emit_scoreboard_statistics()

        # Check emitted data
        received = socket_client.get_received()
        assert len(received) > 0
        message = received[-1]
        assert message['name'] == 'scoreboard_update'
        data = message['args'][0]['data']
        assert data['mode'] in ["teams", "users"]
        assert len(data['standings']) == 2
        assert data['user_standings'] is None  # Depends on mode

        # Clean up
        db.session.delete(user1)
        db.session.delete(user2)
        db.session.commit()