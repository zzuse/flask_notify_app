from server.utils.singleton import Singleton
from .env import Env


class Config(object, metaclass=Singleton):

    def __init__(self, Env):
        self.server_cfg = {}
        self.celery_cfg = {}
        self.env = Env
        if self.env == "development":
            print("Need to be implemented")
            pass

        if self.env == "production":
            print("Need to be implemented")
            pass

        if self.env == "local":
            from server.config.cfg_server_local import Config
            self.server_cfg = Config
            self.celery_cfg = "server.config.cfg_celery_local"

        if self.env == "test":
            print("Need to be implemented")
            pass


g_cfg = Config(Env)
