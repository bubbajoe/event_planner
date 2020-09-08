import re
import os
import yaml
import cerberus

from hashlib import sha256

from aiohttp.web import json_response


def schema(schema):
    def decorator(f):
        async def helper(request):
            data = await request.json()
            valitator = cerberus.Validator(schema, purge_unknown=True)
            valitator.validate(data)
            if valitator.errors:
                print(valitator.errors)
                return json_response(
                    { 'error': valitator.errors }, status=400)
            return await f(request, valitator.document)
        return helper
    return decorator


def email_check(field, value, error):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
        error(field, "invalid email format")

def hash_password(password):
    h = sha256(password.encode())
    return h.hexdigest()

def check_password(hashed, check):
    h = sha256(check.encode())
    return h.hexdigest() == hashed


class Config:
    _config = None

    def __init__(self):
        if not Config._config:
            config_file = 'config.yml'
            with open(config_file) as f:
                Config._config = yaml.safe_load(f.read())
        self.config = Config._config

    def get(self, key, *args, default=None):
        position = self.config[key]
        for arg in args:
            if arg not in position:
                if default is None:
                    raise KeyError(f"'{'.'.join(args)}' doesn't exist in config file")
                return default
            position = position[arg]
        return position