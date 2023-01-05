from server.utils.server_logger import g_logger
from server.config.config_inst import g_cfg
from celery import Celery
g_celery = Celery(__name__, broker=g_cfg.celery_cfg.broker_url, backend=g_cfg.celery_cfg.result_backend)
g_logger.info("CELERY CFG: %s" % g_cfg.celery_cfg)
g_logger.info(g_celery.conf)
# g_celery.config_from_object(g_cfg.celery_cfg, force=True)
