from functools import lru_cache

from dotenv import dotenv_values


@lru_cache
def get_config():
    config = dotenv_values(".env")
    return config
