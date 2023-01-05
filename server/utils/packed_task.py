class PackedTask(object):

    def __init__(self, task, device, container, parameterlist = []):
        self.device = device
        self.container = container
        self.task = task
        self.parameterlist = parameterlist
