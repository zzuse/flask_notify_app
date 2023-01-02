from datetime import datetime
from server.database.db import g_db as db
from server.database.db import PATH_MAX,PATH_MIN,NOR_STR

class TaskModel(db.Model):

    __tablename__ = 'TASK_T'

    ID = db.Column(db.String(128), primary_key=True)
    Alias = db.Column(db.String(NOR_STR))
    Type = db.Column(db.String(NOR_STR))
    CreatedTime = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    #def to_dict(self):
    #    return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def to_dict(self):
        r_dict={}
        for c in self.__table__.columns:
            r_value=getattr(self, c.name)
            if type(r_value)==datetime:
                dtf = "%Y-%m-%dT%H:%M:%S.%f"
                r_dict[c.name] = r_value.strftime(dtf)
            else:
                r_dict[c.name]=r_value
        return r_dict