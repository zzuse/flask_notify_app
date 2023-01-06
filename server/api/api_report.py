from flask_restx import Resource, fields
from flask import request
from server.utils.server_logger import g_logger as logger
from server.api.api_inst import g_api as api
from server.config.config_inst import g_cfg
import base64

# args = {
#     'id': fields.Str(
#             missing=None,
#         ),
#     'email': fields.Str(
#         missing=None,
#     ),
#     'device_id':fields.Str(
#             missing=None,
#         )
# }
#
# args_rerun = {
#     'id': fields.Str(
#             missing=None,
#         ),
# }

ns = api.namespace('report', description='Operations related to report')

@ns.route("/")
class ApiReport(Resource):

    @ns.doc(params={'id': 'CeleryTaskID', 'email': 'OneEmail', 'device_id': 'DeviceId'})
    # @use_kwargs(args)
    def get(self, id, email, device_id):
        from server.server import g_dbm
        if id:
            reports = g_dbm.query_join_report_info_by_id(id)
        elif email:
            reports = g_dbm.query_join_report_info_by_email(email)
        elif device_id:
            result = g_dbm.query_reportid_by_deviceid(device_id)
            return result
        else:
            reports = g_dbm.get_all_report()
        return {"report": reports}

    def post(self):
        from server.server import g_dbm
        info = request.get_json(force=True)
        id = g_dbm.register_or_update_report(info)
        logger.info("\n:::report_celery_taskid:::%s" % id)
        return {"celerytaskid": id}

    @ns.doc(params={'id': 'report ID','psw': 'password for delete'})
    def delete(self):
        psw = request.args.get('psw')
        if not psw:
            return "NEED PASSWORD"
        psw = base64.b64encode(psw.encode(encoding='utf-8')).decode()
        if psw != g_cfg.server_cfg.PSW_FOR_DELETE:
            return "PASSWORD CHECK FAIL"
        from server.server import g_dbm
        id = request.args.get('id')
        ret = g_dbm.delete_report_by_id(id)
        logger.info("\n:::report_delete::: %s" % (id))
        return ret
