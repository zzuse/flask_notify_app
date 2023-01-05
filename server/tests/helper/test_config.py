import os


class TestConfig(object):

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DEVICE_ALIAS = 'W_CFK'
    REPORT_INTERVAL = 5

    REST_SERVER = "http://127.0.0.1:5000"
    WELCOME_SERVICE = "/api/welcome/"
    DEVICE_SERVICE = "/api/device/"
    CLIENT_SERVICE = "/api/client/"
    TASK_SERVICE = "/api/task/"
    CONTAINER_SERVICE = "/api/container/"
    QUEUE_SERVICE = "/api/queue/"
    SENDTASK_SERVICE = "/api/send_task/"
    TASKRESULT_SERVICE = "/api/task_result/"
    TASKREPORT_SERVICE = "/api/report/"
    REMOTE_SERVICE = "/api/device/remote"

    DATA_SERVICE = "/api/data/"
    TOOL_SERVICE = "/api/tools/"
    UTA_SERVICE = "/api/uta/"

    REPORT_SERVICE = "/api/report/"

    STATIC_MSG_API = "static_info"
    DYNAMIC_MSG_API = "dynamic_info"
