from datetime import datetime
from server.db_inst import g_db as db
from server.db_inst import LON_STR, NOR_STR


class UserModel(db.Model):

    __tablename__ = 'USER_T'

    # USER Unique Info
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(NOR_STR), nullable=False, unique=True)
    user_pass = db.Column(db.String(LON_STR), )
    user_email = db.Column(db.String(NOR_STR), )
    user_group = db.Column(db.String(NOR_STR), )
    user_token = db.Column(db.String(LON_STR), )

    registerTime = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        r_dict = {}
        for c in self.__table__.columns:
            r_value = getattr(self, c.name)
            if type(r_value) == datetime:
                dtf = "%Y-%m-%dT%H:%M:%S.%f"
                r_dict[c.name] = r_value.strftime(dtf)
            else:
                r_dict[c.name] = r_value
        return r_dict
