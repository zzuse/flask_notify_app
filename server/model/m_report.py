from datetime import datetime
from server.database.db import g_db as db
from server.database.db import PATH_MAX,PATH_MIN,NOR_STR,SUPER_MAX,TINY_STR

class ReportModel(db.Model):

    __tablename__ = 'REPORT_T'

    CeleryTaskID = db.Column(db.String(NOR_STR), primary_key=True)
    TaskID = db.Column(db.String(NOR_STR))
    TaskType = db.Column(db.String(NOR_STR))
    DeviceId = db.Column(db.String(NOR_STR))
    QueueId = db.Column(db.String(NOR_STR))
    ContainerId = db.Column(db.String(NOR_STR))
    ParameterList = db.Column(db.Text)
    Status = db.Column(db.String(NOR_STR))
    Description = db.Column(db.String(PATH_MAX)) #TODO
    LogLocation = db.Column(db.String(PATH_MAX)) #TODO
    ReportLocation= db.Column(db.String(PATH_MAX))  #TODO
    EmailReceiverList = db.Column(db.String(PATH_MAX))  #TODO
    Current = db.Column(db.String(TINY_STR))
    CeleryTaskStartTime = db.Column(db.DateTime)
    StartRunTime = db.Column(db.DateTime, nullable=False, default=datetime.now())
    LastRunTime = db.Column(db.DateTime, nullable=False, default=datetime.now())
    FailedReason = db.Column(db.String(PATH_MIN))
    ResyncPath = db.Column(db.String(PATH_MAX))  #TODO
    TaskOwner = db.Column(db.String(PATH_MAX))
    Group = db.Column(db.String(PATH_MAX))

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

    def to_dict_datetime(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class StepTime(db.Model):

    __tablename__ = 'STEP_TIME_T'

    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Current = db.Column(db.String(32))
    FinishTime = db.Column(db.DateTime, nullable=False)

    ReportModelID = db.Column(db.String(128), db.ForeignKey('REPORT_T.CeleryTaskID'))
    ReportModel = db.relationship('ReportModel', backref=db.backref('celeryid', lazy='dynamic'))

    def to_dict(self):
        r_dict={}
        for c in self.__table__.columns:
            r_value = getattr(self, c.name)
            if type(r_value) == datetime:
                dtf = "%Y-%m-%dT%H:%M:%S.%f"
                r_dict[c.name] = r_value.strftime(dtf)
            else:
                r_dict[c.name]=r_value
        return r_dict
