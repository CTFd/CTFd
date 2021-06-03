from flask import current_app

import geoacumen
import maxminddb

IP_ADDR_LOOKUP = maxminddb.open_database(
    current_app.config.get("GEOIP_DATABASE_PATH", geoacumen.db_path)
)


def lookup_ip_address(addr):
    try:
        response = IP_ADDR_LOOKUP.get(addr)
        return response["country"]["iso_code"]
    except (KeyError, ValueError):
        return None
