from CTFd.models import db, Configs
from CTFd.utils import get_config, set_config


# config keys prefix
key_prefix = "chal_difficulties_"

# config no_difficulties
def key_no_difficulties() -> str:
  return f"{key_prefix}no_difficulties"

def get_no_difficulties() -> str | None:
  return get_config(key_no_difficulties())

def set_no_difficulties(no_difficulties) -> str | None:
  set_config(key_no_difficulties(), no_difficulties)

# default config
default = {
  key_no_difficulties(): "3",
}

def init():
  """sets config to the default if it doesn't exist yet"""

  # check if a config already exists
  if get_no_difficulties() is not None:
    return
  
  # set default config
  for key, val in default.items():
    set_config(key, val)

def reset():
  """resets the config to the default"""

  # erase existing config
  existing_config = Configs.query.filter(Configs.key.like(f"{key_prefix}%")).all()

  for row in existing_config:
    db.session.delete(row)
    
  db.session.commit()
  
  # set default config
  for key, val in default.items():
    set_config(key, val)

def set(request_form):
  for key in request_form:
    if key.startswith(f"{key_prefix}"):
      set_config(key, request_form[key])
