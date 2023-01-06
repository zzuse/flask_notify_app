from flask_restx import Resource
from server.api.api_inst import g_api as api, token_required

ns = api.namespace('welcome', description='Operations related to welcome')


# api.root
@ns.route('/')
class ApiWelcome(Resource):

    def get(self):
        return {"message": "Welcome to Platform SYSTEM!"}

    def post(self):
        return {"message": "Welcome to Platform SYSTEM!"}
