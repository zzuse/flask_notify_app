from importlib import import_module as imp
import copy


class Common(type):

    @staticmethod
    def classToDict(obj):
        dict = {}
        is_list = obj.__class__ == [].__class__
        is_set = obj.__class__ == set().__class__
        if is_list or is_set:
            return dict
        else:
            dict.update(obj.__dict__)
            return dict

    @staticmethod
    def cfgToDict(obj,keys = []):
        _dict = Common.classToDict(obj)
        bk = copy.copy(_dict)
        if len(keys):
            for k,v in _dict.items():
                if len(k) > 5 and k[:2] == '__'and k[-2:] == '__':
                    bk.pop(k)
                    continue
                if k not in keys:
                    bk.pop(k)
                    continue
        else:
            for k,v in _dict.items():
                if len(k) > 5 and k[:2] == '__'and k[-2:] == '__':
                    bk.pop(k)
        return bk

    @staticmethod
    def getAttrFromCfg(pn,keys = []):
        module_name, _, cls_name = pn.rpartition('.')
        output = {}
        try:
            module = imp(pn)
            for k in keys:
                if hasattr(module,k):
                    output[k] = getattr(module, k)
        except (ImportError, AttributeError):
            output = ""
        return output