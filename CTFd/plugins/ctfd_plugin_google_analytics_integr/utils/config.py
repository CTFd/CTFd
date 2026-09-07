from CTFd.utils import get_config, set_config


# config keys prefix
key_prefix = "google_analytics_integr_"

# config script
def key_script() -> str:
  return f"{key_prefix}script"

def get_script() -> str | None:
  return get_config(key_script())

def set_script(script):
  set_config(key_script(), script)

# config is_enabled
def key_is_enabled() -> str:
  return f"{key_prefix}is_enabled"

def get_is_enabled() -> bool:
  val = get_config(key_is_enabled())
  return str(val).lower() == 'true'

def set_is_enabled(enabled: bool):
  set_config(key_is_enabled(), 'true' if enabled else 'false')