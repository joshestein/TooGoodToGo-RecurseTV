from tgtg import TgtgClient

from config import get_config


class Client:
    def __init__(self):
        config = get_config()

        self.client = TgtgClient(
            access_token=config["ACCESS_TOKEN"],
            refresh_token=config["REFRESH_TOKEN"],
            user_id=config["USER_ID"],
            cookie=config["COOKIE"],
        )
