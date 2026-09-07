from CTFd.models import db, Configs
from CTFd.utils import get_config, set_config


# config keys prefix
key_prefix = "bloods_"

# config no_bloods
def key_no_bloods() -> str:
  return f"{key_prefix}no_bloods"

def get_no_bloods() -> str | None:
  return get_config(key_no_bloods())

# config bloods
def key_blood_val(blood_num: int) -> str:
  return f"{key_prefix}blood_{blood_num}_val"

def get_blood_val(blood_num: int) -> str | None:
  return get_config(key_blood_val(blood_num))

def key_blood_title(blood_num: int) -> str:
  return f"{key_prefix}blood_{blood_num}_title"

def get_blood_title(blood_num: int) -> str | None:
  return get_config(key_blood_title(blood_num))

def key_blood_icon(blood_num: int) -> str:
  return f"{key_prefix}blood_{blood_num}_icon"

def get_blood_icon(blood_num: int) -> str | None:
  return get_config(key_blood_icon(blood_num))

# config filtering
def key_filter_mode() -> str:
  return f"{key_prefix}filter_mode"

def get_filter_mode() -> str | None:
  return get_config(key_filter_mode())

def key_filter_list() -> str:
  return f"{key_prefix}filter_list"

def get_filter_list() -> str:
  return get_config(key_filter_list()) or ""

# default config
default = {
  key_no_bloods(): "3",
  
  key_blood_val(1): "20",
  key_blood_title(1): "First Blood",
  key_blood_icon(1): "lightning",
  
  key_blood_val(2): "10",
  key_blood_title(2): "Second Blood",
  key_blood_icon(2): "lightning",
  
  key_blood_val(3): "5",
  key_blood_title(3): "Third Blood",
  key_blood_icon(3): "lightning",
  
  key_filter_mode(): "blacklist",
  key_filter_list(): ""
}

def init():
  """sets config to the default if it doesn't exist yet"""

  # check if a config already exists
  if get_no_bloods() is not None:
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
