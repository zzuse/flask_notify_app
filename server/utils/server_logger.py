import os
import sys
import re
import logging
from logging.handlers import RotatingFileHandler
from server.config.config_inst import g_cfg
from .singleton import Singleton


class ServerLogger(object,metaclass=Singleton):

    def __init__(self, log_file='server.log', app_name="Server", level=logging.INFO):
        self.log_file = log_file
        self.app_name = app_name
        self.logger = self.__init_logger__()

    def __init_logger__(self):
        self.__check_log_file__()
        formatter = logging.Formatter('%(asctime)s %(module)s %(levelname)-4s: %(message)s')
        logger = logging.getLogger(self.app_name)
        logger.setLevel(logging.INFO)
        logger.propagate = 0   #avoid repeat

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        logger.addHandler(console_handler)

        file_handler = RotatingFileHandler(self.log_file, maxBytes=10 * 1024 * 1024, backupCount=5)
        file_handler.suffix = "%Y-%m-%d_%H.%M.%S.log"
        file_handler.setFormatter(formatter)
        file_handler.extMatch = re.compile("^\d{4}-\d{2}-\d{2}_\d{2}.\d{2}.\d{2}.log$")
        file_handler.setLevel(logging.INFO)  #logging.INFO
        logger.addHandler(file_handler)
        
        return logger

    def __check_log_file__(self):
        print("logfile:%s" % self.log_file)
        log_path = os.path.dirname(self.log_file)
        if len(log_path) and not os.path.exists(log_path):
            os.makedirs(log_path)
        if not os.path.exists(log_path):
            print("do not make log folder, use current path", log_path)
        return True

    def get_logger(self):
        return self.logger


g_logger = ServerLogger(g_cfg.server_cfg.DEVICE_MANAGER_LOG).get_logger()


