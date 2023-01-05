from .db_base import DBBase
import uuid
from server.model.m_task import TaskModel
from server.utils.server_logger import g_logger as logger
from server.flask_inst import g_app
import shortuuid


# This clase can only be used in class DBManager. Because this clase has no db create_all() and no self.db_inst
# This is not celery task. This task is used for task type of endtoend task or broadcast task
class DBManagerTask(DBBase):
    # db operation for task
    def register_task(self, task_info, id_str=""):
        if not task_info:
            return False
        logger.info(" register_task in DB ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        logger.info(task_info)
        logger.info(id_str)
        t = TaskModel()
        if id_str == "":
            str_id = uuid.uuid1()
        else:
            str_id = uuid.uuid3(uuid.NAMESPACE_DNS, id_str)
        str_id = str(shortuuid.encode(str_id))
        t.ID = str_id
        t.Alias = task_info["alias"]
        t.Type = task_info["type"]
        bSuccess = True
        with g_app.app_context():
            try:
                self.db_inst.session.merge(t)
                self.db_inst.session.commit()
            except Exception as e:
                bSuccess = False
                logger.error(str(e))
                self.db_inst.session.rollback()
            finally:
                self.db_inst.session.close()
            logger.info("regist Task ID:%s" % str_id)
            if not bSuccess:
                return False
        return str_id

    def get_all_tasks(self):
        arr = []
        with g_app.app_context():
            try:
                for t in TaskModel.query.all():
                    arr.append(t.to_dict())
                logger.info("get all tasks ID:%s" % arr)
            except Exception as e:
                logger.error(str(e))
            finally:
                self.db_inst.session.close()
        return arr

    def query_task_by_id(self, id):
        if not id:
            return False
        t = None
        with g_app.app_context():
            try:
                t = TaskModel.query.filter_by(ID=id).first()
                logger.info("get task by id %s : %s" % (id, t))
            except Exception as e:
                logger.error(str(e))
            finally:
                self.db_inst.session.close()
        return t.to_dict() if t else None

    def query_tasks_by_name(self, name):
        if not name:
            return False
        arr = []
        with g_app.app_context():
            try:
                for t in TaskModel.query.filter_by(Alias=name).all():
                    arr.append(t.to_dict())
                logger.info("get all tasks by name %s : %s" % (name, t))
            except Exception as e:
                logger.error(str(e))
            finally:
                self.db_inst.session.close()
        return arr

    def delete_task_by_id(self, id):
        if not id:
            return False
        ret = "SUCCESS"
        logger.info("delete task by id : %s" % id)
        with g_app.app_context():
            try:
                d = TaskModel.query.filter_by(ID=id).first()
                self.db_inst.session.delete(d)
                self.db_inst.session.commit()
            except Exception as e:
                ret = "FAIL"
                logger.error(str(e))
                self.db_inst.session.rollback()
            finally:
                self.db_inst.session.close()
        return ret
