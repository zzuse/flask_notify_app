from server.utils.server_logger import g_logger as logger
from server.config.config_inst import g_cfg
from .db_manager_report import DBManagerReport
from .db_manager_task import DBManagerTask
from server.flask_inst import g_app
from .db import g_db


class DBManager(DBManagerReport, DBManagerTask):

    def __init__(self, db):
        self.db_inst = db
        self.__create_all__()

    def __create_all__(self):
        logger.info("DB create_all called")
        with g_app.app_context():
            try:
                self.db_inst.create_all()
                self.db_inst.session.commit()
            except Exception as e:
                logger.error(str(e))
                self.db_inst.session.rollback()
            finally:
                self.db_inst.session.close()


g_dbm = DBManager(g_db)
g_dbm.register_task({'alias': 'default', 'type': '0'}, "default")
