class CeleryConfig(object):
    task_serializer = 'pickle'
    result_serializer = 'json'
    worker_concurrency = 1
    task_create_missing_queues = True
    task_default_exchange = 'transit'
    task_default_exchange_type = 'direct'
    task_default_routing_key = 'macosx'
    worker_prefetch_multiplier = 1  # in common the value is same with count of core in cpu.  default 4
    accept_content = ['json']
    broker_pool_limit = 1000
    task_acks_late = True
    result_backend = "redis://127.0.0.1:6379/0"
    broker_url = "amqp://guest:guest@127.0.0.1:5672//"
