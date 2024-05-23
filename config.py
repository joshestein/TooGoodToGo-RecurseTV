import os
from functools import lru_cache

from dotenv import dotenv_values


@lru_cache
def get_config(keys=None):
    if keys is None:
        keys = ["ACCESS_TOKEN", "REFRESH_TOKEN", "USER_ID", "COOKIE", "OSM_API_KEY"]

    fallback_values = dotenv_values(".env")
    config = {key: os.environ.get(key, fallback_values.get(key)) for key in keys}

    return config
