from server.utils.server_logger import g_logger as logger


class DBBase:
    def _check_parameter(self, info, *args):
        logger.info("check_info: if {} is in {}".format(args, info))
        for i in args:
            if i not in info:
                return False, "{} is needed".format(i)
        return True, None

    def check_admin_str(self, group):
        if group.endswith('_admin'):
            tmp = group.split('_')
            likestr = "%{}%".format(tmp[0])
        elif group == 'Admin':
            likestr = '%'
        else:
            likestr = "%{}%".format(group)
        return likestr
