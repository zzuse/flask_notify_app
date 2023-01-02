from server.utils.server_logger import g_logger as logger
from .db_base import DBBase
from server.model.m_report import ReportModel, StepTime
from server.model.m_report_history import ReportHistoryModel, StepTimeHistory
from sqlalchemy import and_, or_, not_
import traceback
from datetime import datetime
from server.flask_inst import g_app

# This clase can only be used in class DBManager. Because this class has no db create_all() and no self.db_inst
class DBManagerReport(DBBase):
    # db operation for report
    def register_or_update_report(self, r_info):
        logger.debug("regist or update report info:  %s" % r_info)
        mdl = ReportModel()
        mdl.CeleryTaskID = r_info["CeleryTaskID"]
        mdl.TaskID = r_info["TaskID"]
        mdl.TaskType = r_info["TaskType"]
        mdl.DeviceId = r_info["DeviceId"]
        mdl.QueueId = r_info["QueueId"]
        mdl.ContainerId = r_info["ContainerId"]
        mdl.ParameterList = r_info["ParameterList"]
        mdl.Status = r_info["Status"]
        mdl.Description = r_info["Description"]
        mdl.StartRunTime = r_info["StartRunTime"]
        mdl.LastRunTime = r_info["LastRunTime"]
        mdl.LogLocation = r_info["LogLocation"]
        mdl.ReportLocation = r_info["ReportLocation"]
        mdl.EmailReceiverList = r_info["EmailReceiverList"]
        mdl.Current = r_info["Current"]
        mdl.CeleryTaskStartTime = r_info["CeleryTaskStartTime"]
        mdl.FailedReason = r_info["FailedReason"]
        mdl.TaskOwner = r_info["TaskOwner"]
        mdl.Group = r_info["Group"] if "Group" in r_info and r_info["Group"] else ''
        if "ResyncPath" in r_info:
            mdl.ResyncPath = r_info["ResyncPath"]
        with g_app.app_context():
            try:
                self.db_inst.session.merge(mdl)
                mdl_time = StepTime()
                if 'StepDuringTime' not in r_info or not r_info['StepDuringTime']:
                    r_info['StepDuringTime'] = []
                for i in r_info["StepDuringTime"]:
                    # info in i is client info. It should be low case with _
                    mdl_time.Current = i["current"]
                    mdl_time.FinishTime = self.__convert_to_datetime(i["step_finish_time"])
                    mdl_time.ReportModel = mdl
                    self.db_inst.session.merge(mdl_time)
                self.db_inst.session.commit()
            except Exception as e:
                logger.error(str(e))
                logger.error(traceback.format_exc())
                self.db_inst.session.rollback()
            finally:
                self.db_inst.session.close()

        logger.info("report ID:%s" % r_info["CeleryTaskID"])
        return True

    def __convert_to_datetime(self, dt):
        # Converting to datetime...
        logger.debug("Converting to datetime {}".format(dt))
        if type(dt) == datetime:
            return dt
        if type(dt) == str:
            dtf = "%Y-%m-%dT%H:%M:%S.%f"
            return datetime.strptime(dt, dtf)
        return None

    def get_all_report(self):
        arr = []
        with g_app.app_context():
            try:
                for q in ReportModel.query.all():
                    q_dict = q.to_dict()
                    step_list = []
                    for q_time in StepTime.query.filter_by(ReportModelID=q.CeleryTaskID):
                        step_list.append(q_time.to_dict())
                    q_dict.update({"step": step_list})

                    arr.append(q_dict)
                logger.info("get all report : %s" % (arr))
            except Exception as e:
                logger.error(str(e))
                logger.error(traceback.format_exc())
                self.db_inst.session.rollback()
            finally:
                self.db_inst.session.close()
        return arr

    def rerun_report_info_by_id(self, id):
        with g_app.app_context():
            try:
                bSuccess = True
                r = ReportModel.query.filter_by(CeleryTaskID=id).first()
                if not r:
                    return 'Id :{} is not in database.'.format(id)

                s_info = dict()
                s_info["task_owner"] = r.TaskOwner
                s_info["task_type"] = r.TaskType
                s_info["device_id"] = r.DeviceId
                s_info["task_id"] = r.TaskID if r.TaskID else ""
                s_info["container_id"] = r.ContainerId
                s_info["parameter_list"] = eval(r.ParameterList)
                s_info["user_mail_list"] = eval(r.EmailReceiverList)

                from server.celery_inst import g_celery, g_queues
                from server.server import g_dbm
                result = s_info

            except Exception as e:
                bSuccess = False
                logger.error(str(e))
                logger.error(traceback.format_exc())
                self.db_inst.session.rollback()
            finally:
                self.db_inst.session.close()
        if bSuccess:
            return result
        else:
            return False

    def query_join_report_info_by_id(self, id):
        if not id:
            return False
        arr = []
        with g_app.app_context():
            try:
                r = ReportModel.query.filter_by(CeleryTaskID=id).first()
                if not r:
                    return None
                report = r.to_dict()
                step_list = []
                for q_time in StepTime.query.filter_by(ReportModelID=r.CeleryTaskID):
                    step_list.append(q_time.to_dict())
                report.update({"step": step_list})

                arr.append(report)
                device_info = self.query_device_by_id(report['DeviceId'])
                arr.append(device_info)
                container_info = self.query_container_by_id(report['ContainerId'])
                arr.append(container_info)
                if len(report['TaskID']):
                    task_info = self.query_task_by_id(report['TaskID'])
                    arr.append(task_info)
            except Exception as e:
                logger.error(str(e))
                logger.error(traceback.format_exc())
            finally:
                self.db_inst.session.close()
        return arr

    def query_join_report_info_by_email(self, email):
        if not email:
            return False
        r_arr = []

        likestr = "%{}%".format(email)
        with g_app.app_context():
            try:
                for r in ReportModel.query.filter(ReportModel.EmailReceiverList.like(likestr)).all():
                    arr = []
                    if not r:
                        return None
                    report = r.to_dict()
                    step_list = []
                    for q_time in StepTime.query.filter_by(ReportModelID=r.CeleryTaskID):
                        step_list.append(q_time.to_dict())
                    report.update({"step": step_list})

                    arr.append(report)
                    device_info = self.query_device_by_id(report['DeviceId'])
                    arr.append(device_info)
                    container_info = self.query_container_by_id(report['ContainerId'])
                    arr.append(container_info)
                    if len(report['TaskID']):
                        task_info = self.query_task_by_id(report['TaskID'])
                        arr.append(task_info)
                    r_arr.append(arr)
            except Exception as e:
                logger.error(str(e))
                logger.error(traceback.format_exc())
            finally:
                self.db_inst.session.close()
        return r_arr

    def query_reportid_by_deviceid(self, device_id):
        with g_app.app_context():
            try:
                r_dict = {}
                arr_start = []
                arr_revoking = []
                arr_success = []
                arr_failed = []
                for r in ReportModel.query.filter_by(DeviceId=device_id).order_by(ReportModel.StartRunTime).all():
                    if r.Status == 'START':
                        arr_start.append(r.CeleryTaskID)
                    if r.Status == 'REVOKING':
                        arr_revoking.append(r.CeleryTaskID)
                    if r.Status == 'SUCCESS':
                        arr_success.append(r.CeleryTaskID)
                    if r.Status == 'FAILED':
                        arr_failed.append(r.CeleryTaskID)
                r_dict = {'arr_start': arr_start,
                          'arr_revoking': arr_revoking,
                          'arr_success': arr_success,
                          'arr_failed': arr_failed}
            except Exception as e:
                failed_reason = str(e)
                logger.error(failed_reason)
                logger.error(traceback.format_exc())
            finally:
                self.db_inst.session.close()
        return r_dict

    def query_report_by_status(self, status):
        """
        It's Not api function. This function will not return child StepTime result
        """
        if not status:
            return False
        r = None
        with g_app.app_context():
            try:
                r = ReportModel.query.filter_by(Status=status).all()
            except Exception as e:
                logger.error(str(e))
                logger.info("query report by status %s : %s" % (status, r))
            finally:
                self.db_inst.session.close()
        return r

    def query_report_by_status_start_revoking(self):
        """
        It's Not api function. This function will not return child StepTime result
        """
        r = None
        with g_app.app_context():
            try:
                r = ReportModel.query.filter(or_(ReportModel.Status == 'START', ReportModel.Status == 'REVOKING')).all()
            except Exception as e:
                logger.error(str(e))
                logger.info("query report by status %s : %s" % ('START or REVOKING', r))
            finally:
                self.db_inst.session.close()
        return r

    def query_report_by_status_handling(self):
        """
        It's Not api function. This function will not return child StepTime result
        """
        r = None
        with g_app.app_context():
            try:
                r = ReportModel.query.filter(
                    or_(ReportModel.Status == 'HANDLING_SUCCESS', ReportModel.Status == 'HANDLING_REVOKED',
                        ReportModel.Status == 'HANDLING_FAILURE')).all()
            except Exception as e:
                logger.error(str(e))
                logger.info("query report by status %s : %s" % ('START or REVOKING', r))
            finally:
                self.db_inst.session.close()
        return r

    def query_report_by_status_start_revoking_device(self, deviceid):
        arr = []
        with g_app.app_context():
            try:
                for r in ReportModel.query.filter(
                        or_(ReportModel.Status == 'START', ReportModel.Status == 'REVOKING')).filter(
                        ReportModel.DeviceId == deviceid).all():
                    arr.append(r.to_dict_datetime())
                logger.info("query report by status and device : %s" % (arr))
            except Exception as e:
                failed_reason = str(e)
                logger.error(failed_reason)
                logger.error(traceback.format_exc())
            finally:
                self.db_inst.session.close()
        return arr

    def query_report_by_status_device(self, status, deviceid):
        if not status:
            return False
        arr = []
        with g_app.app_context():
            try:
                for r in ReportModel.query.filter(ReportModel.Status == status).filter(
                        ReportModel.DeviceId == deviceid).all():
                    arr.append(r.to_dict_datetime())
                logger.info("query report by status and device : %s" % (arr))
            except Exception as e:
                failed_reason = str(e)
                logger.error(failed_reason)
                logger.error(traceback.format_exc())
            finally:
                self.db_inst.session.close()
        return arr

    def revoke_report_by_id(self, id):
        bSuccess = True
        with g_app.app_context():
            try:
                r = ReportModel.query.filter_by(CeleryTaskID=id).filter_by(Status='START').first()
                r.Status = 'REVOKING'
                self.db_inst.session.merge(r)
                self.db_inst.session.commit()
                logger.info("revoke report by id : %s" % (id))
            except Exception as e:
                bSuccess = False
                failed_reason = str(e)
                logger.error(failed_reason)
                logger.error(traceback.format_exc())
            finally:
                self.db_inst.session.close()
        if bSuccess:
            return True
        else:
            return False

    def query_report_by_owner(self, owner):
        if not owner:
            return False
        r = None
        with g_app.app_context():
            try:
                r = ReportModel.query.filter_by(TaskOwner=owner).all()
            except Exception as e:
                logger.error(str(e))
                self.db_inst.session.rollback()
                logger.info("query report by owner %s : %s" % (owner, r))
            finally:
                self.db_inst.session.close()
        return r

    def query_report_by_group_like(self, group):
        if not group:
            return False
        arr = []
        likestr = self.check_admin_str(group)
        with g_app.app_context():
            try:
                for t in ReportModel.query.filter(ReportModel.Group.like(likestr)).all():
                    arr.append(t.to_dict())
                for t in ReportModel.query.filter_by(Group=None).all():
                    arr.append(t.to_dict())
                for t in ReportModel.query.filter_by(Group='').all():
                    arr.append(t.to_dict())
                logger.info("get all ReportModel that Group like %s : %s" % (group, arr))
            except Exception as e:
                logger.error(str(e))
            finally:
                self.db_inst.session.close()
        return arr

    def query_report_celeryid(self, celeryid):
        if not celeryid:
            return False
        r = None
        with g_app.app_context():
            try:
                r = ReportModel.query.filter_by(CeleryTaskID=celeryid).first()
            except Exception as e:
                logger.error(str(e))
                logger.info("query report celeryid %s : %s" % (celeryid, r))
            finally:
                self.db_inst.session.close()
        return r

    def delete_report_by_status_device(self, status, deviceid):
        if not status:
            return False
        ret = "SUCCESS"
        logger.info("delete report by status and device ")
        with g_app.app_context():
            try:
                for r in ReportModel.query.filter(ReportModel.Status == status).filter(
                        ReportModel.DeviceId == deviceid).all():
                    self.db_inst.session.delete(r)
                self.db_inst.session.delete(r)
                self.db_inst.session.commit()
            except Exception as e:
                ret = "FAIL"
                logger.error(str(e))
                self.db_inst.session.rollback()
            finally:
                self.db_inst.session.close()
        return ret

    def delete_report_by_id(self, id):
        if not id:
            return False
        ret = "SUCCESS"
        logger.info("delete report by id : %s" % id)
        with g_app.app_context():
            try:
                d = ReportModel.query.filter_by(CeleryTaskID=id).first()
                for i in StepTime.query.filter_by(ReportModelID=id):
                    self.db_inst.session.delete(i)
                self.db_inst.session.delete(d)
                self.db_inst.session.commit()
            except Exception as e:
                ret = "FAIL"
                logger.error(str(e))
                self.db_inst.session.rollback()
            finally:
                self.db_inst.session.close()
        return ret

    def insert_report_to_history(self, r_info):
        logger.info("regist log info:  %s" % (r_info))
        mdl = ReportHistoryModel()
        mdl.CeleryTaskID = r_info["CeleryTaskID"]
        mdl.TaskID = r_info["TaskID"]
        mdl.DeviceId = r_info["DeviceId"]
        mdl.QueueId = r_info["QueueId"]
        mdl.ContainerId = r_info["ContainerId"]
        mdl.ParameterList = r_info["ParameterList"]
        mdl.Status = r_info["Status"]
        mdl.Description = r_info["Description"]
        mdl.StartRunTime = r_info["StartRunTime"]
        mdl.LastRunTime = r_info["LastRunTime"]
        mdl.LogLocation = r_info["LogLocation"]
        mdl.ReportLocation = r_info["ReportLocation"]
        mdl.EmailReceiverList = r_info["EmailReceiverList"]
        mdl.current = r_info["Current"]
        mdl.celery_task_start_time = r_info["CeleryTaskStartTime"]
        mdl.failed_reason = r_info["FailedReason"]
        mdl.InsertTime = r_info["InsertTime"]

        bSuccess = True
        with g_app.app_context():
            try:
                self.db_inst.session.merge(mdl)
                self.db_inst.session.commit()
            except Exception as e:
                bSuccess = False
                logger.error(str(e))
                self.db_inst.session.rollback()
            finally:
                self.db_inst.session.close()

            try:
                mdl_time_history = StepTimeHistory()
                for i in StepTime.query.filter_by(ReportModelID=r_info["CeleryTaskID"]):
                    # info in i is client info. It should be low case with _
                    mdl_time_history.Current = i.Current
                    mdl_time_history.FinishTime = i.FinishTime
                    mdl_time_history.ReportHistoryModel = mdl

                    self.db_inst.session.merge(mdl_time_history)
                self.db_inst.session.commit()
            except Exception as e:
                bSuccess = False
                logger.error(str(e))
                self.db_inst.session.rollback()
            finally:
                self.db_inst.session.close()

        logger.info("log ID:%s" % r_info["CeleryTaskID"])
        if not bSuccess:
            return False
        return True

    def delete_report_history_by_id(self, id):
        if not id:
            return False
        ret = "SUCCESS"
        logger.info("delete report history by id : %s" % id)
        with g_app.app_context():
            try:
                d = ReportHistoryModel.query.filter_by(CeleryTaskID=id).first()
                for i in StepTimeHistory.query.filter_by(ReportHistoryModelID=id):
                    self.db_inst.session.delete(i)
                self.db_inst.session.delete(d)
                self.db_inst.session.commit()
            except Exception as e:
                ret = "FAIL"
                logger.error(str(e))
                self.db_inst.session.rollback()
            finally:
                self.db_inst.session.close()
        return ret
