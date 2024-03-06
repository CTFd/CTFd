# -*- coding: utf-8 -*-

from collections import OrderedDict
from pycountry import countries

COUNTRIES_LIST = [(one_ctr.alpha_2, one_ctr.name) for one_ctr in countries]

# Nicely titled (and translatable) country names.
COUNTRIES_DICT = OrderedDict(COUNTRIES_LIST)

# List of countries suitable for use in forms
# TODO: CTFd 4.0 Move SELECT_COUNTRIES_LIST into constants
SELECT_COUNTRIES_LIST = [("", "")] + COUNTRIES_LIST


def get_countries():
    return COUNTRIES_DICT


def lookup_country_code(country_code):
    one_ctr = countries.get(alpha_2=country_code)
    return one_ctr.name
