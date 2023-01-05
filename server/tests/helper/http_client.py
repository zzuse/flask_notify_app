import json
import requests
from threading import Timer
from prototype.server.tests.helper.test_config import TestConfig
from prototype.server.tests.helper.system_info import SystemInfo


class ManagerClient(object):

    def __init__(self, url):
        self.url = url
        self.timer = ''
        self.sess = requests.Session()

    def set_timer(self, interval=5):
        self.timer = Timer(interval, lambda: self.send_dynamic_info())
        self.timer.start()

    def send_static_info(self):
        sys_info = SystemInfo.get_static_sys_info()
        json_sys_info = json.dumps(sys_info)
        try:
            r = self.sess.post(self.url, data=json_sys_info)
            logger.info("Response Header:{}".format(r.headers))
        except Exception as e:
            # logger.info(e)
            logger.info("Exception:{}".format(e))

    def send_dynamic_info(self):
        self.set_timer(TestConfig.REPORT_INTERVAL)
        sys_info = SystemInfo.get_dynamic_sys_info()
        json_sys_info = json.dumps(sys_info)
        try:
            r = self.sess.post(self.url, data=json_sys_info)
            logger.info("Response Header:{}".format(r.headers))
        except Exception as e:
            # logger.info(e)
            logger.info("Exception:{}".format(e))

    def start(self):
        self.set_timer(TestConfig.REPORT_INTERVAL)
        self.send_static_info()


app = ManagerClient(TestConfig.HTTP_SERVER)


if __name__ == '__main__':
    client = ManagerClient(TestConfig.HTTP_SERVER)
