from flask import request, render_template
from functools import wraps
import logging
import requests
import json
from requests.auth import HTTPBasicAuth
from .hooks import load_hooks
import os

logging.basicConfig(level=logging.DEBUG)


def load(app):
    load_hooks()
