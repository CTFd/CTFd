from CTFd import create_app
from CTFd.models import *

app = create_app()

with app.app_context():
    try:
        from IPython import embed
        embed()
    except:
        import code
        variables = globals().copy()
        variables.update(locals())
        shell = code.InteractiveConsole(variables)
        shell.interact()
