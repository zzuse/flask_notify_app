from server.utils.server_logger import g_logger as logger
from .db_base import DBBase
from server.model.m_user import UserModel
from server.flask_inst import g_app

# This clase can only be used in class DBManager. Because this clase has no db create_all() and no self.db_inst
# VersionModel use for user authentication check.
class DBManagerUser(DBBase):
    def register_user_by_name(self, username, passwdhash, email, group):
        if not username:
            return False
        if not passwdhash:
            return False
        t = UserModel()

        t.user_name = username
        t.user_pass = passwdhash
        t.user_email = email
        t.user_group = group
        bSuccess = True
        with g_app.app_context():
            try:
                self.db_inst.session.add(t)
                self.db_inst.session.commit()
            except Exception as e:
                bSuccess = False
                logger.error(str(e))
                self.db_inst.session.rollback()
            finally:
                self.db_inst.session.close()
        logger.info("user register in DB {}: {}".format(username, passwdhash))
        if not bSuccess:
            return False
        return True

    def query_user_by_name(self,username):
        if not username:
            return False
        d = None
        with g_app.app_context():
            try:
                d = UserModel.query.filter_by(user_name=username).first()
            except Exception as e:
                logger.error(str(e))
            finally:
                self.db_inst.session.close()
        if d is not None:
            return d.to_dict()
        else:
            return None

    def query_user_by_id(self, uid):
        if not uid:
            return False
        d = None
        with g_app.app_context():
            try:
                d = UserModel.query.filter_by(user_id=uid).first()
                logger.info("get user by id : %s" % d.to_dict())
            except Exception as e:
                logger.error(str(e))
            finally:
                self.db_inst.session.close()
        if d is not None:
            return d
        else:
            return None

    def query_user_by_group_like(self, group):
        if not group:
            return False
        clist = []
        likestr = self.check_admin_str(group)
        with g_app.app_context():
            try:
                for c in UserModel.query.filter(UserModel.user_group.like(likestr)).all():
                    clist.append(c.to_dict())
                for c in UserModel.query.filter_by(user_group=None).all():
                    clist.append(c.to_dict())
                for c in UserModel.query.filter_by(user_group='').all():
                    clist.append(c.to_dict())
                logger.info("get all User that group like %s : %s" % (group, clist))
            except Exception as e:
                logger.error(str(e))
            finally:
                self.db_inst.session.close()
        return clist

    def update_user_by_id(self, c_info):
        if not c_info:
            return "NO json in body for update_user"
        logger.info("regist user info: %s %s" % (type(c_info), c_info))
        t = UserModel()
        t.user_id = c_info["user_id"]
        t.user_name = c_info["user_name"]
        t.user_pass = c_info["user_pass"]
        t.user_email = c_info["user_email"]
        t.user_group = c_info["user_group"]

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
        if not bSuccess:
            return "Error happened in merge database"
        return {"user_id": c_info["user_id"]}

    def delete_user_by_id(self,id):
        if not id:
            return False
        ret = "SUCCESS"
        logger.info("delete user by id : %s"%id)
        with g_app.app_context():
            try:
                d = UserModel.query.filter_by(user_id=id).first()
                self.db_inst.session.delete(d)
                self.db_inst.session.commit()
            except Exception as e:
                ret = "FAIL"
                logger.error(str(e))
                self.db_inst.session.rollback()
            finally:
                self.db_inst.session.close()
        return ret
