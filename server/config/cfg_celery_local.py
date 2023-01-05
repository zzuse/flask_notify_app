class CeleryConfig(object):
    task_serializer = 'json'
    result_serializer = 'json'
    worker_concurrency = 1
    task_create_missing_queues = True
    task_default_exchange = 'xxx'
    task_default_exchange_type = 'direct'
    task_default_routing_key = 'xxx.default'
    worker_prefetch_multiplier = 1  # in common the value is same with count of core in cpu.  default 4
    accept_content = ['json']
    broker_pool_limit = 1000
    task_acks_late = True
    result_backend = 'redis://localhost:6379'
    broker_url = "amqp://guest:guest@localhost:5672//"
