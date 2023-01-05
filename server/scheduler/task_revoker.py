from server.celery_inst import g_celery
from server.utils.server_logger import g_logger as logger
from datetime import datetime
from server.server import g_dbm


class TaskRevoker(object):
    def __init__(self, celery):
        self.celery = celery

    def revoke_task_by_celerytaskid(self, celerytaskid):
        self.celery.control.revoke(celerytaskid, terminate=True)
        result = g_dbm.revoke_report_by_id(id=celerytaskid)
        return result

    def revoke_task_by_devicetask(self, deviceid):
        report_list = g_dbm.query_report_by_status_device(status="START", deviceid=deviceid)
        if not report_list:
            return "No task id on this device"
        for i in report_list:
            self.celery.control.revoke(i["CeleryTaskID"], terminate=True)
        return True


g_trv = TaskRevoker(g_celery)
