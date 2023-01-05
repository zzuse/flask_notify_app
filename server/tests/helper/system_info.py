import platform
import uuid
import socket
import os
if 'ANDROID_ROOT' in os.environ or 'ANDROID_DATA' in os.environ or 'ANDROID_HOME' in os.environ:
    ANDROID_PLATFORM = 1
else:
    ANDROID_PLATFORM = 0
    import psutil

class SystemInfo(object):

    def __init__(self):
        pass

    # get platform info
    @staticmethod
    def get_current_pid():
        return os.getpid()

    @staticmethod
    def get_platform_info():
        platform_info = dict()
        if ANDROID_PLATFORM == 1:
            platform_info["system"] = platform.system() + '_ANDROID'
        else:
            platform_info["system"] = platform.system()
        platform_info["platform"] = platform.platform()
        platform_info["node"] = platform.node()
        platform_info["machine"] = platform.machine()
        platform_info["architecture"] = platform.architecture()
        platform_info["processor"] = platform.processor()
        if ANDROID_PLATFORM == 1:
            platform_info['logical_cpu_num'] = 0
            platform_info['physical_cpu_num'] = 0
        else:
            platform_info['logical_cpu_num'] = SystemInfo.get_cpu_count_logical()
            platform_info['physical_cpu_num'] = SystemInfo.get_cpu_count()
        return platform_info

    # get ip address
    @staticmethod
    def get_ip_address():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        return ip

    # get mac address
    @staticmethod
    def get_mac_address():
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
        return ":".join([mac[e:e + 2] for e in range(0, 11, 2)])

    # get logical cpu count
    @staticmethod
    def get_cpu_count_logical():
        return psutil.cpu_count()

    # get cpu count
    @staticmethod
    def get_cpu_count():
        return psutil.cpu_count(logical=False)

    # get mem info
    @staticmethod
    def get_mem_info():
        mem_dic = dict()
        if ANDROID_PLATFORM == 1:
            mem_dic["total"] = "{:.0f}".format(0) + " MB"
            mem_dic["used"] = "{:.0f}".format(0) + " MB"
            mem_dic["free"] = "{:.0f}".format(0) + " MB"
            mem_dic["percent"] = "{:.2f}".format(0)
        else:
            memory_convent = 1024 * 1024
            mem = psutil.virtual_memory()
            mem_dic["total"] = "{:.0f}".format(mem.total / memory_convent) + " MB"
            mem_dic["used"] = "{:.0f}".format(mem.used / memory_convent) + " MB"
            mem_dic["free"] = "{:.0f}".format(mem.free / memory_convent) + " MB"
            mem_dic["percent"] = "{:.2f}".format(mem.percent)
        return mem_dic

    # get cpu info
    @staticmethod
    def get_cpu_ino():
        cpu_dic = dict()
        if ANDROID_PLATFORM == 1:
            cpu_dic["user_time"] = "{:.2f}%".format(0)
            cpu_dic["sys_time"] = "{:.2f}%".format(0)
            cpu_dic["idle_time"] = "{:.2f}%".format(0)
        else:
            cpu_status = psutil.cpu_times()
            cpu_time = 0
            for item in cpu_status:
                if item != 0:
                    cpu_time = cpu_time + item
            cpu_dic["user_time"] = "{:.2f}%".format(cpu_status.user / cpu_time * 100)
            cpu_dic["sys_time"] = "{:.2f}%".format(cpu_status.system / cpu_time * 100)
            cpu_dic["idle_time"] = "{:.2f}%".format(cpu_status.idle / cpu_time * 100)
        return cpu_dic


    # get disk info
    @staticmethod
    def get_disk_info():
        disk_info = dict()
        if ANDROID_PLATFORM == 1:
            disk_info["total"] = "{:.3f}".format(0) + " G"
            disk_info["used"] = "{:.3f}".format(0) + " G"
            disk_info["free"] = "{:.3f}".format(0) + " G"
            disk_info["percent"] = "{:.2f}%".format(0)
        else:
            memory_convent = 1024*1024*1024
            disk_usage = psutil.disk_usage('/')
            disk_info["total"] = "{:.3f}".format(disk_usage.total / memory_convent) + " G"
            disk_info["used"] = "{:.3f}".format(disk_usage.used / memory_convent) + " G"
            disk_info["free"] = "{:.3f}".format(disk_usage.free / memory_convent) + " G"
            disk_info["percent"] = "{:.2f}%".format(disk_usage.percent)
        return disk_info

    @staticmethod
    def get_user_login_info():
        psutil.users()

    @staticmethod
    def get_static_info():
        sys_info = dict()
        sys_info['cmd'] = "static_info"
        sys_info["platform_info"] = SystemInfo.get_platform_info()
        sys_info["mem_info"] = SystemInfo.get_mem_info()
        sys_info["cpu_info"] = SystemInfo.get_cpu_ino()
        sys_info["disk_info"] = SystemInfo.get_disk_info()
        sys_info['alias'] = "VirtualHostNameForTestingOnly"
        sys_info['ip'] = SystemInfo.get_ip_address()
        sys_info['mac'] = SystemInfo.get_mac_address()
        sys_info['pid'] = ''
        return sys_info

    @staticmethod
    def get_dynamic_info():
        sys_info = dict()
        sys_info['cmd'] = "dynamic_info"
        sys_info["mem_info"] = SystemInfo.get_mem_info()
        sys_info["cpu_info"] = SystemInfo.get_cpu_ino()
        sys_info["disk_info"] = SystemInfo.get_disk_info()
        sys_info['alias'] = "VirtualHostNameForTestingOnly"
        sys_info['ip'] = SystemInfo.get_ip_address()
        sys_info['mac'] = SystemInfo.get_mac_address()
        return sys_info


if __name__ == '__main__':
    print (SystemInfo.get_static_info())
    print (SystemInfo.get_dynamic_info())
