from kombu import Exchange, Queue
from datetime import datetime
from server.utils.server_logger import g_logger as logger
import uuid
from server.config.config_inst import g_cfg


class TaskSender(object):

    def __init__(self, celery, g_queues, dbm, request_host):
        self.celery = celery
        self.dbm = dbm
        self.queues = g_queues
        self.device_id_list = []
        self.task_id = ""
        self.task_type = ""
        self.container_id = ""
        self.parameter_list = []
        self.user_mail_list_l = []
        self.user_mail_list_str = ""
        self.resync_path = ""
        self.request_host = request_host

    def __send_info_oper(self, send_info):
        logger.info("send_info: %s" % (send_info))
        # task id is str and could be missing
        if "task_id" in send_info and send_info["task_id"]:
            if type(send_info["task_id"]) == str:
                self.task_id = send_info["task_id"].strip()
            else:
                return False, "task_id only supports str and can NOT be None"
        else:
            self.task_id = ""

        # task type is str and could be missing
        if "task_type" in send_info and send_info["task_type"]:
            if type(send_info["task_type"]) == str:
                self.task_type = send_info["task_type"].strip()
            else:
                return False, "task_type only supports str"
        else:
            return False, "task_type can NOT be missing or None"

        # device_id is str or list and could NOT be missing
        # right device_id format : "abc" or "abc, efg" or ["abc"]
        # wrong device_id format :  "[abc]" or "abc","efg" or None or ["abc", None]
        if "device_id" in send_info:
            device = send_info["device_id"]
            if type(device) == str:
                device_list = device.split(",")
                for i in device_list:
                    if not i or not i.strip():
                        return False, "device_id can NOT be None"
                    self.device_id_list.append(i.strip())
            elif type(device) == list:
                for i in device:
                    if not i or not i.strip():
                        return False, "device_id can NOT be None"
                    self.device_id_list.append(i.strip())
            else:
                return False, "device_id only supports str or list and can NOT be None"
        else:
            return False, "device_id can NOT be missing"

        # container_id is str and could Not be missing
        if "container_id" in send_info and send_info["container_id"]:
            container = send_info["container_id"]
            if type(container) == str and container.strip():
                self.container_id = send_info["container_id"]
            else:
                return False, "container_id only supports str can NOT be None"
        else:
            return False, "container_id can NOT be missing or None"

        # parameter list is list and could NOT be missing
        if "parameter_list" in send_info and send_info["parameter_list"]:
            if type(send_info["parameter_list"]) == list:
                self.parameter_list = send_info["parameter_list"]
            else:
                return False, "parameter_list only supports list"
        else:
            return False, "parameter_list can NOT be missing or None"

        # user_mail_list is str or list and could NOT be missing
        # right email format : "m@m.com" or "m@m.com, m@m.com" or ["m@m.com"]
        # wrong email format :  "[m@m.com]" or "m@m.com","m@m.com" or None or ["m@m.com", None]
        if "user_mail_list" in send_info:
            mail = send_info["user_mail_list"]
            if type(mail) == str:
                mail_list = mail.split(",")
                for i in mail_list:
                    if not i or not i.strip():
                        return False, "user_mail_list can NOT be None"
                    self.user_mail_list_l.append(i.strip())
            elif type(mail) == list:
                for i in mail:
                    if not i or not i.strip():
                        return False, "user_mail_list can NOT be None"
                    self.user_mail_list_l.append(i.strip())
            else:
                return False, "user_mail_list only supports str or list and can NOT be None"
        else:
            return False, "user_mail_list cannot be missing"

        if "task_owner" in send_info and send_info["task_owner"]:
            if type(send_info["task_owner"]) == str:
                self.task_owner = send_info["task_owner"].strip()
            else:
                return False, "task_owner only supports str and can NOT be None"
        else:
            self.task_owner = ""
        return True, None

    def send(self, send_info):
        res_id_list = []
        logger.info("TaskSender::send Called!")

        result, message = self.__send_info_oper(send_info)
        if not result:
            return message
        logger.info("task_id %s" % (self.task_id))
        logger.info("task_type %s" % (self.task_type))
        logger.info("device_id_list %s" % (self.device_id_list))
        logger.info("container_id %s" % (self.container_id))
        logger.info("parameter_list %s" % (self.parameter_list))
        logger.info("user_mail_list_l %s" % (self.user_mail_list_l))
        logger.info("task_owner %s" % (self.task_owner))

        if self.task_id == None or self.task_id == "":
            logger.info("TaskSender:: use default task")
            tasks = self.dbm.query_tasks_by_name("default")
            if not tasks:
                return "Server has not default task. Please find admin to solve this issue."
            task, tasktype = tasks[0], tasks[0]['Type']
        else:
            task = self.dbm.query_task_by_id(self.task_id)
            if task != None and task:
                tasktype = task['Type']
            else:
                logger.info("TaskSender:: failed because user send wrong task id:%s!" % self.task_id)
                return "No task id in database: {}".format(self.task_id)
        logger.info("task::  %s" % (task))

        container = ""
        # container = self.dbm.query_container_by_id(self.container_id)
        # if not container:
        #     return "No container id in database: {}".format(self.container_id)
        logger.info("container::  %s" % container)

        for device_id in self.device_id_list:
            if tasktype == '1':  # task.Type == '1'    send to all. Not work now, so don't use it
                res_id = self.__send_bc__(task, container, self.parameter_list)
                logger.debug("TaskSender:: broadcast done!")
            elif tasktype == '0':  # task.Type == '0'   send to one
                # device = self.dbm.query_device_by_id(device_id)
                # if not device:
                #     return "No device id in database: {}".format(device_id)
                logger.info("device::  %s" % device_id)
                res_id = self.__send_p2p__(task, device_id, container, self.parameter_list)
                logger.info("TaskSender:: send task done!")
            else:
                return "No support tasktype: {}".format(tasktype)

            res_id_list.append(str(res_id))
            celerytask_id = res_id
            logger.info("Register Report:")
            report_info = self.__report_info_init(celerytask_id=celerytask_id, device_id=device_id, task_id=task['ID'])

            logger.info(" user input mail_list {}".format(self.user_mail_list_l))

            # container['MailList'] is list convert to str, like ["m@m.com"]
            contmaill = container['MailList']

            logger.info("user input mail_list %s" % (self.user_mail_list_str))
            logger.info("containter's mail_list %s %s" % (type(contmaill), contmaill))

            # self.user_mail_list_l is list. contmaill from db is str, like "["123","567"]"
            wit = str(self.user_mail_list_l + list(eval(contmaill)))
            logger.info("All mail_list %s %s" % (type(wit), wit))

            report_info['EmailReceiverList'] = wit
            logger.info("report_info:  %s" % (report_info))
            self.dbm.register_or_update_report(report_info)
        return {"celerytasks": res_id_list}

    def __report_info_init(self, celerytask_id, device_id, task_id):
        report_info = dict()
        report_info["CeleryTaskID"] = celerytask_id
        report_info["TaskID"] = task_id
        report_info["TaskType"] = self.task_type
        report_info["DeviceId"] = device_id
        report_info["QueueId"] = ""
        report_info["ContainerId"] = self.container_id
        report_info["ParameterList"] = str(self.parameter_list)
        report_info["Status"] = "START"
        report_info["Description"] = "container run status report"
        report_info["LogLocation"] = ""
        report_info["ReportLocation"] = ""
        report_info["Current"] = "Begin"
        report_info['StartRunTime'] = datetime.now()
        report_info["CeleryTaskStartTime"] = None
        report_info["StepDuringTime"] = []
        report_info["FailedReason"] = ""
        report_info['LastRunTime'] = datetime.now()
        if g_cfg.server_cfg.BRAINPP_WH_HEADER in self.request_host:
            report_info['ResyncPath'] = g_cfg.server_cfg.BRAINPP_WH_HOST
        else:
            report_info['ResyncPath'] = g_cfg.server_cfg.BRAINPP_HOST
        report_info['TaskOwner'] = self.task_owner
        return report_info

    def __send_p2p__(self, task, device, container, parameterlist):
        packed_task = self.__pack_task__(task, device, container, parameterlist)
        logger.info("__send_p2p__ packed_task: %s" % (packed_task))
        # self.queues[queue_name] = Queue(queue_name, exchange=Exchange('xxx', type='direct'), routing_key=queue_name)
        # task_queues = (
        #     Queue("macosx", Exchange('transit', delivery_mode=1),
        #           routing_key='macosx', durable=False),
        # )
        task_queues = {"macosx": Queue("macosx", exchange=Exchange('transit', type='direct'), routing_key="macosx")}
        self.celery.conf.update(queues=task_queues)
        logger.info("__send_p2p__ queue name: %s" % device)
        res = self.celery.send_task('celery.do_task', args=[packed_task, ], queue=device,
                                    task_id=str(uuid.uuid1()))  # task_id = uuid.uuid1()
        return res.id

    def __send_bc__(self, task, container, parameterlist):
        packed_task = self.__pack_task__(task, [], container, parameterlist)
        logger.info("  __send_bc__  packed_task ::: %s" % (packed_task))
        self.queues['boardcast'] = Queue('boardcast', exchange=Exchange('boardcast', type='fanout'))
        self.celery.conf.update(CELERY_QUEUES=self.queues)
        res = self.celery.send_task('celery.dotask', args=[packed_task, ], queue='boardcast',
                                    task_id=str(uuid.uuid1()))  # task_id = uuid.uuid1()
        logger.info(res.id)
        return res.id

    def __pack_task__(self, task, device, container, parameterlist=[]):
        from server.utils.packed_task import PackedTask
        obj = PackedTask(task, device, container, parameterlist=parameterlist)
        return obj
