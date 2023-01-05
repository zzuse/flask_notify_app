from datetime import datetime
from server.db_inst import g_db as db
from server.db_inst import PATH_MAX, NOR_STR, TINY_STR

class ReportHistoryModel(db.Model):

    __tablename__ = 'REPORT_HISTORY_T'

    CeleryTaskID = db.Column(db.String(NOR_STR), primary_key=True)
    TaskID = db.Column(db.String(NOR_STR))
    TaskType = db.Column(db.String(NOR_STR))
    DeviceId = db.Column(db.String(NOR_STR))
    QueueId = db.Column(db.String(NOR_STR))
    ContainerId = db.Column(db.String(NOR_STR))
    ParameterList = db.Column(db.Text)
    Status = db.Column(db.String(NOR_STR))
    Description = db.Column(db.String(PATH_MAX))  #TODO
    LogLocation = db.Column(db.String(PATH_MAX))  #TODO
    ReportLocation= db.Column(db.String(PATH_MAX))  #TODO
    EmailReceiverList = db.Column(db.String(PATH_MAX))  #TODO
    Current = db.Column(db.String(TINY_STR))
    CeleryTaskStartTime = db.Column(db.DateTime)
    StartRunTime = db.Column(db.DateTime, nullable=False, default=datetime.now())
    LastRunTime = db.Column(db.DateTime, nullable=False, default=datetime.now())
    FailedReason = db.Column(db.String(PATH_MAX))  #TODO
    InsertTime = db.Column(db.DateTime, nullable=False, default=datetime.now())
    TaskOwner = db.Column(db.String(PATH_MAX))

    def to_dict(self):
        r_dict={}
        for c in self.__table__.columns:
            r_value=getattr(self, c.name)
            if type(r_value)==datetime:
                dtf = "%Y-%m-%dT%H:%M:%S.%f"
                print(r_value.strftime(dtf))
                r_dict[c.name] = r_value.strftime(dtf)
            else:
                r_dict[c.name]=r_value
        return r_dict

    def to_dict_datetime(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class StepTimeHistory(db.Model):

    __tablename__ = 'STEP_TIME_HISTORY_T'

    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Current = db.Column(db.String(32))
    FinishTime = db.Column(db.DateTime, nullable=False)

    ReportHistoryModelID = db.Column(db.String(128), db.ForeignKey('REPORT_HISTORY_T.CeleryTaskID'))
    ReportHistoryModel = db.relationship('ReportHistoryModel', backref=db.backref('celeryid', lazy='dynamic'))

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
