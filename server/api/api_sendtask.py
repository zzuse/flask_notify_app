from flask_restx import Resource, fields
from flask import request
from server.utils.server_logger import g_logger as logger
from server.api.api_inst import g_api as api, token_required
from server.scheduler.task_sender import TaskSender
from server.scheduler.task_revoker import g_trv

ns = api.namespace('send_task', description='Operations related to send task')


@ns.route('/')
class ApiSendTask(Resource):
    def get(self):
        return {"task_id": "", "container_id": "", "queue_id": "", "user_mail_list": ""}

    def post(self):
        info = request.get_json(force=True)
        logger.info("send task api called!{}".format(info))

        from server.celery_inst import g_celery
        from server.server import g_dbm

        request_host = request.headers['Host']
        g_ts = TaskSender(g_celery, "", g_dbm, request_host)
        result = g_ts.send(info)
        logger.info("{}!{}".format(result, info))
        return result


@ns.route("/rerun")
class ApiTaskRerun(Resource):
    @ns.doc(params={'celerytaskid': 'CeleryTaskID'})
    def post(self):
        celerytaskid = request.args.get("celerytaskid")
        if not id:
            return "report celerytaskid is needed"
        logger.info("rerun task api called! {}".format(celerytaskid))
        from server.server import g_dbm
        result = g_dbm.rerun_report_info_by_id(celerytaskid)
        return result


@ns.route("/revoke")
class ApiRevokeTask(Resource):
    @ns.doc(params={'deviceid': 'DeviceID'})
    @ns.doc(params={'celerytaskid': 'CeleryTaskID'})
    def post(self):
        logger.info("Revoke Task api called!")
        celerytaskid = request.args.get("celerytaskid")
        if celerytaskid:
            logger.info("Revoke Task by celerytaskid: %s" % celerytaskid)
            return g_trv.revoke_task_by_celerytaskid(celerytaskid=celerytaskid)
        deviceid = request.args.get("deviceid")
        if deviceid:
            logger.info("Revoke Task by deviceid: %s" % deviceid)
            return g_trv.revoke_task_by_devicetask(deviceid=deviceid)
        return "celerytaskid or deviceid is needed"


@ns.route("/pause")
class ApiRevokeTask(Resource):
    @ns.doc(params={'celerytaskid': 'CeleryTaskID'},
            description='This api will revoke task then rerun it. You will get a new task id here')
    def post(self):
        logger.info("Pause Task api called!")
        celerytaskid = request.args.get("celerytaskid")
        if celerytaskid:
            logger.info("Pause Task by celerytaskid: %s" % celerytaskid)
            logger.info("Firstly Revoke Task by celerytaskid: %s" % celerytaskid)
            result = g_trv.revoke_task_by_celerytaskid(celerytaskid=celerytaskid)
            if not result:
                return "pause task failed because of revoke task failed"
            from server.server import g_dbm
            result = g_dbm.rerun_report_info_by_id(celerytaskid)
            return result
        return "celerytaskid or deviceid is needed"
