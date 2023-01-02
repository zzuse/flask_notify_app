from server.config.config_inst import g_cfg
import json
import requests
from server.utils.server_logger import g_logger as logger
from .task_sendmail import send_per_celerytask_email
import re
from server.database.db_manager import g_dbm as dbm


def __get_id_and_name_from_paramteterlist(paramteterlist, container_info):
    if container_info["Type"] != "nfs":
        return None
    paramteterlist = eval(paramteterlist)
    if type(paramteterlist) != list:
        return None
    if not paramteterlist:
        return None
    uta_id = ""
    uta_alias = ""
    data_id = ""
    data_name = ""
    tool_id = ""
    tool_alias = ""
    p1 = r"(?<=uta/).*?(?=/)"
    pattern1 = re.compile(p1)
    p2 = r"(?<=data/).*?(?=/)"
    pattern2 = re.compile(p2)
    p3 = r"(?<=tool/).*?(?=/)"
    pattern3 = re.compile(p3)

    for i in paramteterlist:
        if i["name"] == "uta" and "path" in i and i["path"]:
            uta_id_tmp = re.search(pattern1, i["path"]).group()
            uta_info = dbm.query_uta_by_id(uta_id_tmp)
            uta_id += uta_id_tmp
            if uta_info and uta_info["Alias"]:
                uta_alias += uta_info["Alias"]
        if i["name"] == "data" and "path" in i and i["path"]:
            data_id_tmp = re.search(pattern2, i["path"]).group()
            data_info = dbm.query_data_by_id(data_id_tmp)
            data_id += data_id_tmp
            if data_info and data_info["Name"]:
                data_name += data_info["Name"]
        if i["name"] == "tool" and "path" in i and i["path"]:
            tool_id_tmp = re.search(pattern3, i["path"]).group()
            tool_info = dbm.query_tool_by_id(tool_id_tmp)
            tool_id += tool_id_tmp
            if tool_info and tool_info["Alias"]:
                tool_alias += tool_info["Alias"]
    return uta_id, uta_alias, data_id, data_name, tool_id, tool_alias


def send_report_to_report_server(task_type, uta_id, uta_alias, device_id, data_id, data_name, tool_id, tool_alias,
                                 report_path):
    s = requests.Session()
    report_producer = {"task_type": task_type, "uta_id": uta_id, "uta_alias": uta_alias, "device_id": device_id,
                       "data_id": data_id, "data_name": data_name, "tool_id": tool_id, "tool_alias": tool_alias,
                       "report_path": report_path}
    url = g_cfg.server_cfg.REPORT_SERVER + g_cfg.server_cfg.REPORT_PRODUCER_SERVICE
    logger.info("Test Report Producer:")
    logger.info(report_producer)
    try:
        r = s.post(url, data=json.dumps(report_producer))
        logger.info(r.status_code)
        if r.status_code != 200:
            return False
        logger.info(json.loads(r.text))
        return json.loads(r.text)
    except Exception as e:
        failed_reason = str(e)
        logger.error(failed_reason)
        return False


def send_report(report_info, device_info, container_info):
    task_type = report_info["TaskType"]
    if not task_type:
        logger.info("No task_type in database. Skip send report request")
        report_path = ""
        send_per_celerytask_email(report_info, device_info, container_info, report_path)
    elif not report_info['Relative_ReportLocation']:
        logger.info("No Relative_ReportLocation. Skip send report request")
        report_path = ""
        send_per_celerytask_email(report_info, device_info, container_info, report_path)
    else:
        logger.info("task_type is {}. Send report request".format(task_type))
        uta_id, uta_alias, data_id, data_name, tool_id, tool_alias = __get_id_and_name_from_paramteterlist(
            report_info["ParameterList"], container_info)
        device_id = report_info["DeviceId"]
        result = send_report_to_report_server(task_type, uta_id, uta_alias, device_id, data_id, data_name, tool_id,
                                              tool_alias,
                                              report_info['Relative_ReportLocation'])
        if not result:
            no_report_reason = "Cannot connect to report server"
            send_per_celerytask_email(report_info, device_info, container_info, no_report_reason=no_report_reason)
            return
        report_path = result["result"]
        no_report_reason = result["failed_reason"]
        if report_path:
            send_per_celerytask_email(report_info, device_info, container_info, report_path=report_path)
        else:
            send_per_celerytask_email(report_info, device_info, container_info, no_report_reason=no_report_reason)
