from celery import Celery
g_celery = Celery(__name__)
g_queues = {}
