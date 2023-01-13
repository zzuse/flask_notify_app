from celery import Celery
from kombu import Exchange, Queue
from datetime import datetime
import logging
import traceback

config = {}
config['broker'] = 'amqp://guest:guest@127.0.0.1:5672//'
config['backend'] = 'redis://127.0.0.1:6379/0'

g_celery = Celery('do_task', broker=config['broker'], backend=config['backend'])
g_celery.conf.update(
    task_serializer='pickle',
    result_serializer="json",
    accept_content=['json'],
    worker_concurrency=1,
    task_create_missing_queues=True,
    task_default_exchange='transit',
    task_default_exchange_type='direct',
    task_acks_late=True,
    broker_pool_limit=1000
)


@g_celery.task(name='client.task.do_task', bind=True)
def do_task(args):
    celery_task_start_time = datetime.now()
    # formatter = logging.Formatter('%(asctime)s %(module)s %(levelname)-4s: %(message)s')
    logger = logging.getLogger("client")
    logger.setLevel(logging.INFO)
    logger.propagate = 0
    try:
        logger.info("received task!")
        logger.info("args.task: {}".format(args.task))
        logger.info("args.device: {}".format(args.device))
        logger.info("args.container: {}".format(args.container))
        logger.info("args.parameter list: {}".format(args.parameterlist))
        # logger.info("args.celery task id: {}".format(self.request.id))
        # task = args.task
        # device = args.device
        # container = args.container
        # parameterlist = args.parameterlist
        # task = Task(celerytask=self, task=task, device=device, container=container, parameterlist=parameterlist,
        #             celery_task_start_time=celery_task_start_time, logger=logger)
        logger.info("task.run called")
        g_queues = {"macosx": Queue("macosx", exchange=Exchange('transit', type='direct'), routing_key="macosx")}
        g_celery.conf.update(queues=g_queues)
        g_celery.worker_main(args)
        return True
    except Exception as e:
        failed_reason = str(e)
        logger.error(failed_reason)
        logger.error("Unknown Task ERROR")
        logger.error(traceback.format_exc())
        return False

# @g_celery.task(name='celery.do_task', bind=True)
# def say_hello(name: str):
#     g_queues = {"macosx": Queue("macosx", exchange=Exchange('transit', type='direct'), routing_key="macosx")}
#     g_celery.conf.update(queues=g_queues)
#     return f"Hello {name}"
