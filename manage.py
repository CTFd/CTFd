from flask.cli import FlaskGroup

from CTFd import create_app

app = create_app()

cli = FlaskGroup(app)


if __name__ == "__main__":
    cli()
