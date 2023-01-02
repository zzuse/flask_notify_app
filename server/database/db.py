from flask_sqlalchemy import SQLAlchemy
from server.flask_inst import g_app
from server.config.config_inst import g_cfg

SUPER_MAX = 4096
PATH_MAX = 512
PATH_MIN = 256

LON_STR = 512
NOR_STR = 128
TINY_STR = 32

g_db = SQLAlchemy()
g_app.config['SQLALCHEMY_DATABASE_URI'] = g_cfg.server_cfg.SQLALCHEMY_DATABASE_URI
g_db.init_app(g_app)



