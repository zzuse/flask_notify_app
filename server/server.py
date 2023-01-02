from server.flask_inst import g_app
from server.config.config_inst import g_cfg
from server.database.db_manager import g_dbm
from server.celery_inst import g_celery

from server.utils.server_logger import g_logger
from server.web.show_report import report_bp
from .scheduler.task_statustimer import TaskTimer


def start_info(app,info_bp):
    g_logger.info("Starting Flask Resource {} Info...".format(info_bp.name))
    app.register_blueprint(info_bp)
    return info_bp

def start_server():
    g_logger.info("CELERY CFG: %s" % g_cfg.celery_cfg)
    g_celerytaskTimer = TaskTimer(g_celery, g_dbm)
    g_celerytaskTimer.start_timer()

    start_info(g_app, report_bp)

    g_app.add_url_rule('/', endpoint='index')
    g_logger.info("Starting Flask App...")
    g_app.run(host='0.0.0.0', port=8000, threaded=True, debug=False)


