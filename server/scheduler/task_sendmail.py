from server.utils.smtp_client import EmailClient
from server.utils.email_template import *
from server.utils.server_logger import g_logger as logger
from datetime import datetime, timedelta
from server.config.config_inst import g_cfg
from collections import OrderedDict
from server.database.db_manager import g_dbm as dbm
import re
import os
import traceback

def __convert_to_datetime(dt):
    logger.debug("Converting to datetime {}".format(dt))
    if type(dt) == datetime:
        return dt
    if type(dt) == str:
        dtf = "%Y-%m-%dT%H:%M:%S.%f"
        return datetime.strptime(dt, dtf)
    return None


def __chop_microseconds(time):
    if type(time) == timedelta:
        return time - timedelta(microseconds=time.microseconds)
    if type(time) == datetime:
        return time.replace(microsecond=0)
    return time

def send_incapacitated_task_email(report_info):
    #TODO send email to task sender
    pass

def __get_utapath_from_paramteterlist(paramteterlist, container_info):
    try:
        if container_info["Type"] != "nfs":
            return None
        paramteterlist=eval(paramteterlist)
        if type(paramteterlist) != list:
            return None
        if not paramteterlist:
            return None
        uta_path_list=[]

        p1 = r"(?<=uta/).*?(?=/)"
        pattern = re.compile(p1)
        for i in paramteterlist:
            if i["name"] =="uta" and "path" in i:
                uta_id = re.search(pattern, i["path"])
                if uta_id:
                    tool_info = dbm.query_uta_by_id(uta_id.group())
                    if tool_info and tool_info["SourcePath"] != "None":
                        uta_path_list.append(tool_info["SourcePath"])
        return uta_path_list
    except Exception as e:
        logger.error("__get_utapath_from_paramteterlist error")
        logger.error(traceback.format_exc())
        return False

def __get_dataname_from_paramteterlist(paramteterlist, container_info):
    try:
        if container_info["Type"] != "nfs":
            return None
        paramteterlist=eval(paramteterlist)
        if type(paramteterlist) != list:
            return None
        if not paramteterlist:
            return None
        data_name_list=[]

        for i in paramteterlist:
            if i["name"] =="data" and "path" in i:
                data_name = os.path.basename(i["path"])
                if data_name:
                    data_name_list.append(data_name)
        return data_name_list
    except Exception as e:
        logger.error("__get_dataname_from_paramteterlist error")
        logger.error(traceback.format_exc())
        return False

def __get_toolname_from_paramteterlist(paramteterlist, container_info):
    try:
        # old version of container cannot do this
        if container_info["Type"] != "nfs":
            return None
        paramteterlist=eval(paramteterlist)
        if not paramteterlist:
            return None
        if type(paramteterlist) != list:
            return None
        tool_name_list=[]

        for i in paramteterlist:
            if i["name"] =="tool" and "path" in i:
                tool_name = os.path.basename(i["path"])
                if tool_name:
                    tool_name_list.append(tool_name)
        return tool_name_list
    except Exception as e:
        logger.error("__get_toolname_from_paramteterlist error")
        logger.error(traceback.format_exc())
        return False


def send_per_celerytask_email(report_info, device_info, container_info, report_path=False, no_report_reason=None):
    try:
        arr = OrderedDict()
        arr["RESULT:"] = report_info['Status']
        arr["STAGE:"] = report_info['Current']
        arr["FAILED_REASON:"] = report_info['FailedReason']
        arr["CELERY_TASK_ID:"] = report_info['CeleryTaskID']
        arr["DEVICE_ID:"] = device_info["ID"]
        arr["CONTAINER_ID:"] = container_info["ID"]

        start_time = report_info['CeleryTaskStartTime']
        step_finish_time = datetime.now()
        steplist = []
        test_duration = timedelta(0)
        for i in report_info['StepDuringTime']:
            # info in i is client format use lowcase and _
            step_finish_time = __convert_to_datetime(i['step_finish_time'])
            during_time = step_finish_time - start_time
            test_duration += during_time
            text = "{0}\t-- Elapsed time\t{1}\n".format(i['current'], __chop_microseconds(during_time))
            steplist.append(text)
            start_time = step_finish_time
        if report_info['Status'] == 'FAILED':
            text = "...\n...\n"
            steplist.append(text)

        ec = EmailClient()
        ec.set_subject("[AUTOMATION] [{0}] {1} on {2} {3}".format(report_info["Status"], container_info['Alias'], device_info["Alias"] ," by "+report_info["TaskOwner"] if report_info["TaskOwner"] else ""))
        html = email_first + email_hi + email_brief_begin
        report_text = "\n"
        html += table_begin + row_begin

        if report_info['Status'] == 'SUCCESS':
            html += email_brief_content.format("<b>RESULT: <b><b style=\"color: #1DC127;\">{}".format(report_info['Status']))
        else:
            html += email_brief_content.format(
                "<b>RESULT: <b><b style=\"color: #E74C3C;\">{}".format(report_info['Status']))

        html += email_brief_content.format("<b>TASK OWNER: </b>{}".format(report_info['TaskOwner'] if report_info['TaskOwner'] else " "))

        html += row_finish + row_begin
        html += email_brief_content.format("<b>CONTAINER: </b>{}".format(container_info['Alias']))
        html += email_brief_content.format(
            "<b>START FROM: </b>{0} ".format(__chop_microseconds(report_info["StartRunTime"])))

        html += row_finish + row_begin
        html += email_brief_content.format("<b>DURATION: </b>{0}".format(__chop_microseconds(test_duration)))
        html += email_brief_content.format("<b>WAITING:</b> {0} ".format(
            __chop_microseconds(report_info["LastRunTime"] - report_info["StartRunTime"] - test_duration)))
        html += row_finish + row_begin

        html += email_brief_content.format("<b>DEVICE: </b>{}".format(device_info['Alias']))
        html += email_brief_content.format("<b></b>")

        html += row_finish + row_begin
        data_name_list=__get_dataname_from_paramteterlist(report_info["ParameterList"], container_info)
        html += email_brief_highlight.format("DATA NAME LIST: ", "{}".format(data_name_list))

        html += row_finish + row_begin
        tool_name_list=__get_toolname_from_paramteterlist(report_info["ParameterList"], container_info)
        html += email_brief_highlight.format("TOOL NAME LIST: ", "{}".format(tool_name_list))

        html += row_finish + row_begin
        uta_path_list=__get_utapath_from_paramteterlist(report_info["ParameterList"], container_info)
        html += email_brief_highlight.format("UTA PATH LIST: ", "{}".format(uta_path_list))

        html += row_finish + row_begin
        html += email_brief_content_2.format("REPORT LOCATION: ", "{}".format(report_info['ReportLocation']))

        if 'BrainppReport' in report_info and len(report_info['BrainppReport']) > 0:
            html += row_finish + row_begin
            rob = report_info['BrainppReport'].split(':')
            if len(rob):
                html += email_brief_content_2.format("REPORT on Brain++: ", "{}".format(rob[-1]))
            else:
                html += email_brief_content_2.format("REPORT on Brain++: ", "{}".format(report_info['ReportLocation']))
            if report_info['Relative_ReportLocation']:
                html += row_finish + row_begin

                if report_info['ResyncPath'] == g_cfg.server_cfg.BRAINPP_WH_HOST:
                    tmp_path = os.path.join(g_cfg.server_cfg.BRAINPP_WH_HTTP, report_info['Relative_ReportLocation'])
                else:
                    tmp_path = os.path.join(g_cfg.server_cfg.BRAINPP_HTTP, report_info['Relative_ReportLocation'])
                html += email_brief_content_2.format("REPORT HTTP LINK: ", "{}".format(tmp_path))

        html += row_finish + row_begin
        html += email_brief_content_2.format("LOG LOCATION: ", "{}".format(report_info['LogLocation']))

        if 'BrainppLog' in report_info and len(report_info['BrainppLog']) > 0:
            html += row_finish + row_begin

            lob = report_info['BrainppLog'].split(':')
            if len(lob):
                html += email_brief_content_2.format("LOG on Brain++: ", "{}".format(lob[-1]))
            else:
                html += email_brief_content_2.format("LOG on Brain++: ", "{}".format(report_info['BrainppLog']))

        if report_path:
            if 'ftp_path' in report_path:
                html += row_finish + row_begin
                html += email_brief_content_2.format("IMAGE LOCATION: ", "{}".format(report_path['ftp_path']))
            if 'brainpp_path' in report_path:
                html += row_finish + row_begin
                if report_info['ResyncPath'] == g_cfg.server_cfg.BRAINPP_WH_HOST:
                    brainpp_path = os.path.join(g_cfg.server_cfg.BRAINPP_WH_HTTP, report_path['brainpp_path'])
                else:
                    brainpp_path = os.path.join(g_cfg.server_cfg.BRAINPP_HTTP, report_path['brainpp_path'])

                html += email_brief_content_2.format("IMAGE BRAINPP: ", "{}".format(brainpp_path))
        else:
            arr["NO IMAGE REASON:"] = no_report_reason

        html += row_finish + table_finish
        html += email_button
        html += email_list_begin.format("Detail Infos:")
        html += email_list_2.format("ENV: ", g_cfg.env + '\n')
        report_text += "ENV: "+ g_cfg.env + '\n'
        for k, v in arr.items():
            if k == 'RESULT:':
                continue
            html += email_list_2.format(k, (v if v else 'None') + '\n')
            report_text += k + (v if v else 'None') + '\n'
        for v in steplist:
            html += email_list_2.format("STEP_NAME: ", v + '\n')
            report_text += "STEP_NAME: " + v + '\n'

        html += email_list_end + email_last
        logger.info(report_text)
        ec.set_plain_text(report_text)
        ec.set_html_text(html)
        if hasattr(g_cfg.server_cfg, "DEFAULT_MAIL"):
            all_mail=eval(report_info['EmailReceiverList'])+g_cfg.server_cfg.DEFAULT_MAIL
        else:
            all_mail=eval(report_info['EmailReceiverList'])
        ec.set_to_addresses(all_mail)
        logger.info(all_mail)
        ec.send()
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error("TIMER REPORT send_per_celerytask_email Exception:{}".format(e))

def send_alarm_email_to_admin(msg):
    if not g_cfg.server_cfg.DEFAULT_MAIL:
        logger.error("no DEFAULT_MAIL. Cannot send alarm email")
        return
    ec = EmailClient()
    ec.set_subject("[AUTOMATION] [ALARM MESSAGE] {}".format(msg))
    ec.set_plain_text(msg)
    html = email_first + email_hi + email_brief_begin
    html+=email_alarm_msg.format(msg)
    html += email_list_end + email_last
    ec.set_html_text(html)

    ec.set_to_addresses(g_cfg.server_cfg.DEFAULT_MAIL)
    logger.info(g_cfg.server_cfg.DEFAULT_MAIL)
    ec.send()
