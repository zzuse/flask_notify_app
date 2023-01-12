from server.utils.server_logger import g_logger
from server.config.config_inst import g_cfg
from celery import Celery

g_celery = Celery(__name__, broker=g_cfg.celery_cfg.broker_url, backend=g_cfg.celery_cfg.result_backend)
g_logger.info("CELERY CFG: {}".format(__name__))
g_celery.conf.update(
                     task_serializer=g_cfg.celery_cfg.task_serializer,
                     result_serializer=g_cfg.celery_cfg.result_serializer,
                     accept_content=g_cfg.celery_cfg.accept_content,
                     worker_concurrency=g_cfg.celery_cfg.worker_concurrency,
                     task_create_missing_queues=g_cfg.celery_cfg.task_create_missing_queues,
                     task_default_exchange=g_cfg.celery_cfg.task_default_exchange,
                     task_default_exchange_type=g_cfg.celery_cfg.task_default_exchange_type,
                     task_default_routing_key=g_cfg.celery_cfg.task_default_routing_key,
                     task_acks_late=g_cfg.celery_cfg.task_acks_late,
                     broker_pool_limit=g_cfg.celery_cfg.broker_pool_limit
                     )
g_logger.info(g_celery.conf)

