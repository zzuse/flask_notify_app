import unittest
import requests
import json
import time

from server.tests.helper.test_config import TestConfig
from server.tests.helper.system_info import SystemInfo

g_device_id = "macosx"
g_task_id = ""
# g_container_id = "hN4xCmwRncVGgTiZijTdtd"
g_container_id = ""
g_queue_id = ""


class TestEnd2End(unittest.TestCase):
    global g_task_id
    global g_container_id
    global g_device_id
    global g_queue_id

    def setUp(self):
        self.s = requests.Session()

    def tearDown(self):
        pass

    def test_restful_service(self):
        url = TestConfig.REST_SERVER + TestConfig.WELCOME_SERVICE
        print("Testing Restful Api:%s" % url)
        r = self.s.get(url)
        self.assertEqual(r.status_code, 200, "Access to restful service doesn't return 200!")
        self.assertTrue(r.text.find("Welcome") != -1, "Access to restful service, wrong welcome message!")

    def test_get_report(self):
        global g_task_id
        url = TestConfig.REST_SERVER + TestConfig.REPORT_SERVICE
        print("Testing Restful Api:%s" % url)
        r = self.s.get(url, params={'email': 'z@gmail.com'})
        print(r.status_code)
        self.assertEqual(r.status_code, 200, "get result failed, return code is not 200!")
        print(r.text)
        js = json.loads(r.text)
        print("\n", js, "\n")
        return js

    def test_nfs_container_report(self):
        send_info = dict()
        send_info["device_id"] = g_device_id
        send_info["task_id"] = "jUx7NpxYVpDirwKgr3sZp7"
        send_info["task_type"] = "0"
        send_info["container_id"] = "rH3fKs4d5Wg6AcZuhXvyj9"
        send_info["parameter_list"] = [
            {"name": "tool", "path": "tool/Uz7LZMJjtxzGSipYoWT39a/s-tar"},
            {"name": "data", "path": "data/G3M74KDx8kC7dhdRfApXVZ/test_.tar"},
            {"name": "uta", "path": "uta/MrNCKokYdZFPnCwc5u5ukU/model.tar"},
            {'name': 'report', 'cmd': 'python3 report.py', "param": ""}
        ]
        send_info["user_mail_list"] = ["z@xxx.com"]
        send_info["task_owner"] = "z"
        print(send_info)
        url = TestConfig.REST_SERVER + TestConfig.SENDTASK_SERVICE
        print("Send Task: %s" % url)
        task_id_list = []
        length = 1
        for i in range(length):
            r = self.s.post(url, data=json.dumps(send_info))
            print(r.status_code)
            self.assertEqual(r.status_code, 200, "send task failed, return code is not 200!")
            print(r.text)

            print("#" * 20)
            # task_info.append({})
            id = json.loads(r.text)
            print(id)
            task_id_list.append(id['celerytasks'][0])
            print(task_id_list)
            time.sleep(1)


'''
if __name__ == '__main__':
    unittest.main()
'''
