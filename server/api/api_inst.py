from flask_restx import Api
from flask import request
from functools import wraps

authorizations = {
    'api_key': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-API_KEY'
    }
}

g_api = Api(version='1.0', title='API',
            description='Automation Testing System API, Flask RestX powered API',
            authorizations=authorizations)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = None
        if 'X-API-KEY' in request.headers:
            token = request.headers['X-API-KEY']

        if not token:
            return {'message': 'Token is missing'}, 401

        if token != 'my_token':
            return {'message': 'Your token is wrong'}

        print('TOKEN {}'.format(token))
        return f(*args, **kwargs)

    return decorated


'''
def start_api(app):
    g_logger.info("Start initializing restful api...")
    g_api = Api(app)
    from .api_welcome import ApiWelcome
    from .api_client import ApiClient
    from .api_sendtask import ApiSendTask
    from .api_taskresult import ApiTaskResult
    from .api_device import ApiDevice
    from .api_task import ApiTask
    from .api_container import ApiContainer
    from .api_queue import ApiQueue
    from .api_report import ApiReport

    g_api.add_resource(ApiWelcome, '/')
    g_api.add_resource(ApiClient, '/client')
    g_api.add_resource(ApiSendTask, '/send_task')
    g_api.add_resource(ApiTaskResult, '/taskresult')
    g_api.add_resource(ApiDevice, '/device')
    g_api.add_resource(ApiTask, '/task')
    g_api.add_resource(ApiContainer, '/container')
    g_api.add_resource(ApiQueue, '/queue')
    g_api.add_resource(ApiReport,'/report')
    g_logger.info("End initializing restful api...")
    return g_api

'''
