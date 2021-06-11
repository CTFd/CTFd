import geoacumen_city
import maxminddb
from flask import current_app

IP_ADDR_LOOKUP = maxminddb.open_database(
    current_app.config.get("GEOIP_DATABASE_PATH", geoacumen_city.db_path)
)


def lookup_ip_address(addr):
    try:
        response = IP_ADDR_LOOKUP.get(addr)
        return response["country"]["iso_code"]
    except (KeyError, ValueError, TypeError):
        return None


def lookup_ip_address_city(addr):
    try:
        response = IP_ADDR_LOOKUP.get(addr)
        return response["city"]["names"]["en"]
    except (KeyError, ValueError, TypeError):
        return None
