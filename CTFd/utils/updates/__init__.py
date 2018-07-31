import requests

def update_check(force=False):
    # If UPDATE_CHECK is disabled don't check for updates at all.
    if app.config.get('UPDATE_CHECK') is False:
        return

    # Get when we should check for updates next.
    next_update_check = get_config('next_update_check') or 0

    # If we have passed our saved time or we are forcing we should check.
    update = (next_update_check < time.time()) or force

    if update:
        try:
            params = {
                'current': app.VERSION
            }
            check = requests.get(
                'https://versioning.ctfd.io/versions/latest',
                params=params,
                timeout=0.1
            ).json()
        except requests.exceptions.RequestException as e:
            pass
        else:
            try:
                latest = check['resource']['tag']
                html_url = check['resource']['html_url']
                if StrictVersion(latest) > StrictVersion(app.VERSION):
                    set_config('version_latest', html_url)
                elif StrictVersion(latest) <= StrictVersion(app.VERSION):
                    set_config('version_latest', None)
            except KeyError:
                set_config('version_latest', None)
        finally:
            # 12 hours later
            next_update_check_time = int(time.time() + 43200)
            set_config('next_update_check', next_update_check_time)
    else:
        set_config('version_latest', None)