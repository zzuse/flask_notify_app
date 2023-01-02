import traceback
from threading import Timer
from threading import current_thread
from datetime import datetime, timedelta

from .task_sendreport import *

import pickle
import requests
import os
import json

STARTED_TIMER = 10
FINISHED_TIMER = 60


class TaskTimer(object):
    def __init__(self, celery, dbm):
        self.celery = celery
        self.timer = None
        self.dbm = dbm
        self.s = requests.Session()
        self.queues = {}

    def start_timer(self):
        self.set_timer(self.scanStartedWork, STARTED_TIMER)
        self.set_timer(self.scanFinishedWork, FINISHED_TIMER)

    def set_timer(self, func, interval=5):
        self.timer = Timer(interval, func)
        self.timer.start()

    def scanStartedWork(self):
        '''scan report table then update it, success '''
        self.set_timer(self.scanStartedWork, STARTED_TIMER)
        logger.debug(current_thread())
        self.get_started_report()

    def __convert_to_datetime(self, dt):
        logger.debug("Converting to datetime...")
        if type(dt) == datetime:
            return dt
        if type(dt) == str:
            dtf = "%Y-%m-%dT%H:%M:%S.%f"
            return datetime.strptime(dt, dtf)
        return None

    def get_started_report(self):
        reports = self.dbm.query_report_by_status_start_revoking()
        report_list = []
        for report in reports:
            report_list.append(report.to_dict_datetime())

        for report_info in report_list:
            try:
                r = self.celery.AsyncResult(report_info['CeleryTaskID'])
                logger.debug("r state:{}".format(r.state))
                logger.debug("r result:{}".format(r.result))

                report_tmp = self.dbm.query_report_celeryid(report_info['CeleryTaskID']).to_dict_datetime()
                if report_tmp['Status'] != 'START' and report_tmp['Status'] != 'REVOKING':
                    continue

                if r.state == "SUCCESS":
                    report_tmp['Status'] = 'HANDLING_SUCCESS'
                    self.dbm.register_or_update_report(report_tmp)

                    if r.result.get('container_state') == "Pass":
                        report_info['Status'] = 'SUCCESS'
                    else:
                        report_info['Status'] = 'FAILED'

                    report_info['Current'] = r.result.get('current', None)
                    report_info['CeleryTaskStartTime'] = self.__convert_to_datetime(
                        r.result.get('celery_task_start_time'))
                    report_info['StepDuringTime'] = r.result.get('step_during_time', [])
                    report_info['LogLocation'] = os.path.join(g_cfg.server_cfg.UPLOAD_URL,
                                                              r.result['log_url']) if r.result.get('log_url',
                                                                                                   None) else None
                    report_info['Relative_ReportLocation'] = r.result.get('report_url', None)
                    report_info['ReportLocation'] = os.path.join(g_cfg.server_cfg.UPLOAD_URL,
                                                                 r.result['report_url']) if r.result.get('report_url',
                                                                                                         None) else None
                    report_info['FailedReason'] = r.result.get('failed_reason', None)
                    report_info['LastRunTime'] = datetime.now()

                    logger.info('SUCCESS -- Need RsyncPath: %s %s' % (
                        report_info['LogLocation'], report_info['ReportLocation']))
                    device_info = self.dbm.query_device_by_id(report_info['DeviceId'])
                    container_info = self.dbm.query_container_by_id(report_info['ContainerId'])
                    send_report(report_info, device_info, container_info)
                    self.dbm.register_or_update_report(report_info)

                elif r.state == "FAILURE":
                    report_tmp['Status'] = 'HANDLING_FAILURE'
                    self.dbm.register_or_update_report(report_tmp)
                    report_info['Status'] = 'FAILED'
                    report_info['Current'] = 'assign_task'
                    report_info['CeleryTaskStartTime'] = None
                    report_info['StepDuringTime'] = []
                    report_info['LogLocation'] = None
                    report_info['Relative_ReportLocation'] = None
                    report_info['ReportLocation'] = None
                    report_info['FailedReason'] = 'Client internal error. Please contact QA admin.'
                    report_info['LastRunTime'] = datetime.now()

                    logger.info(
                        'FAILURE -- Need Resync: %s %s' % (report_info['LogLocation'], report_info['ReportLocation']))
                    device_info = self.dbm.query_device_by_id(report_info['DeviceId']) if report_info[
                        'DeviceId'] else None
                    container_info = self.dbm.query_container_by_id(report_info['ContainerId'])
                    send_report(report_info, device_info, container_info)
                    result = self.dbm.register_or_update_report(report_info)

                elif r.state == "REVOKED":
                    report_tmp['Status'] = 'HANDLING_REVOKED'
                    self.dbm.register_or_update_report(report_tmp)
                    report_info['Status'] = 'FAILED'
                    report_info['Current'] = 'waiting'
                    report_info['CeleryTaskStartTime'] = None
                    report_info['StepDuringTime'] = []
                    report_info['LogLocation'] = None
                    report_info['Relative_ReportLocation'] = None
                    report_info['ReportLocation'] = None
                    report_info['FailedReason'] = 'REVOKED BY USER!!!'
                    report_info['LastRunTime'] = datetime.now()

                    logger.info(
                        'FAILURE -- Need Resync: %s %s' % (report_info['LogLocation'], report_info['ReportLocation']))
                    device_info = self.dbm.query_device_by_id(report_info['DeviceId']) if report_info[
                        'DeviceId'] else None
                    container_info = self.dbm.query_container_by_id(report_info['ContainerId'])
                    send_report(report_info, device_info, container_info)
                    self.dbm.register_or_update_report(report_info)

            except Exception as e:
                logger.error(traceback.format_exc())
                logger.error("TIMER REPORT get Backend Api Exception:{}".format(e))

    def __chop_microseconds(self, time):
        if type(time) == timedelta:
            return time - timedelta(microseconds=time.microseconds)
        if type(time) == datetime:
            return time.replace(microsecond=0)
        return time

    def scanFinishedWork(self):
        ''' scan report table then update it, success '''
        self.set_timer(self.scanFinishedWork, FINISHED_TIMER)

        logger.debug("Finished work:{}".format(current_thread()))
        try:
            self.put_taskid_to_history_table()
        except Exception as e:
            logger.error("TIMER REPORT update DB Exception:{}".format(e))

    def put_taskid_to_history_table(self):
        '''
        Move long time report to History table
        '''
        success_list = self.dbm.query_report_by_status('SUCCESS')
        history_lists = []
        for success in success_list:
            history_lists.append(success.to_dict_datetime())
        failed_list = self.dbm.query_report_by_status('FAILED')
        for failed in failed_list:
            history_lists.append(failed.to_dict_datetime())
        logger.debug("log_lists size:{}".format(len(history_lists)))
        for history in history_lists:
            try:
                days = int(g_cfg.server_cfg.REPORT_TABLE_MOVE_TO_HISTORY_TABLE)
                if history['LastRunTime'] > datetime.now() - timedelta(days=days):
                    continue
                history["InsertTime"] = datetime.now()
                if self.dbm.insert_report_to_history(history):
                    logger.debug("One report move to history table")
                    self.dbm.delete_report_by_id(history['CeleryTaskID'])
            except Exception as e:
                logger.error("Move report to log table Exception:{}".format(e))
