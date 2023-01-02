from flask import Flask
from flask import render_template

def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html', posts=e), 404

g_app = Flask(__name__)
g_app.config["SWAGGER_UI_JSONEDITOR"] = True
g_app.config["SECRET_KEY"] = 'secret_xxx'
g_app.register_error_handler(404, page_not_found)
g_app.register_error_handler(500, page_not_found)