from server.flask_inst import g_app

from server.database.db_manager import g_dbm
from server.celery_inst import g_celery

from server.utils.server_logger import g_logger

from server.api.api_inst import g_api
from flask import Blueprint
from server.web.auth import auth_bp
from server.web.index import index_bp
from server.web.show_user import user_bp
from server.web.show_report import report_bp
from server.web.show_task import task_bp

from .scheduler.task_statustimer import TaskTimer


def start_api(app, api):
    g_logger.info("Starting Flask Resource Api...")
    api_bp = Blueprint('api', __name__, url_prefix='/api')
    api.init_app(api_bp)
    from server.api.api_report import ns as ns_report
    from server.api.api_sendtask import ns as ns_sendtask
    from server.api.api_welcome import ns as ns_welcome
    api.add_namespace(ns_sendtask)
    api.add_namespace(ns_report)
    api.add_namespace(ns_welcome)
    app.register_blueprint(api_bp)
    return api


def start_info(app, info_bp):
    g_logger.info("Starting Flask Resource {} Info...".format(info_bp.name))
    app.register_blueprint(info_bp)
    return info_bp


def start_server():
    g_taskTimer = TaskTimer(g_celery, g_dbm)
    g_taskTimer.start_timer()

    start_api(g_app, g_api)
    g_app.register_blueprint(auth_bp)
    start_info(g_app, index_bp)
    start_info(g_app, user_bp)
    start_info(g_app, report_bp)
    start_info(g_app, task_bp)

    g_logger.info("Starting Flask App...")
    g_app.run(host='0.0.0.0', port=8000, threaded=True, debug=False)
