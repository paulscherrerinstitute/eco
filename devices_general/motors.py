from ...eco_epics.motor import Motor as _Motor

_MotorRocordStandardProperties = \
        {}
_posTypes = ['user','dial','raw']
_guiTypes = ['xdm']

def _keywordChecker(kw_key_list_tups):
    for tkw,tkey,tlist in keyw_list_pairs:
        assert tkey in tlist, "Keyword %s should be one of %s"%(tkw,tlist)

class MotorRecord:
    def __init__(self,pvname):
        self.Id = pvname
        self._motor = _Motor(pvname)

    # Conventional methods and properties for all Adjustable objects
    def changeTo(self, value, hold=False, check=True):
        """ Adjustable convention"""

        mover = lambda value: self._motor.move(\
                value, ignore_limits=(not check))
        return Changer(
                target=value,
                parent=self,
                mover=mover,
                stopper=self._motor.stop,
                blocker)

    def get_position(self,posType='user'):
        """ Adjustable convention"""
        _keywordChecker([('posType',posType,_posTypes)])
        if posType == 'user':
            return self._motor.get_position()
        if posType == 'dial':
            return self._motor.get_position(dial=True)
        if posType == 'raw':
            return self._motor.get_position(raw=True)

    def set_position(self,value,posType='user'):
        """ Adjustable convention"""
        _keywordChecker([('posType',posType,_posTypes)])
        if posType == 'user':
            return self._motor.set_position(value)
        if posType == 'dial':
            return self._motor.set_position(value,dial=True)
        if posType == 'raw':
            return self._motor.set_position(value,raw=True)

    def get_precision(self):
        """ Adjustable convention"""
        pass

    def set_precision(self):
        """ Adjustable convention"""
        pass

    precision = property(get_precision,set_precision)

    def set_speed(self):
        """ Adjustable convention"""
        pass
    def set_limits(self, posType='user'):
        """ Adjustable convention"""
        _keywordChecker([('posType',posType,_posTypes)])

    def get_limits(self, posType='user'):
        """ Adjustable convention"""
        _keywordChecker([('posType',posType,_posTypes)])
        ll_name, hl_name = 'LLM', 'HLM'
        if posType is 'dial':
            ll_name, hl_name = 'DLLM', 'DHLM'
        return self._motor.get(ll_name), self._motor.get(hl_name)

    def gui(self, guiType='xdm'):
        """ Adjustable convention"""
        pass


    # epics motor record specific methods


    # spec-inspired convenience methods
    def mv(self,value):
        pass
    def wm(self):
        pass
    def mvr(self,value):
        pass
    def wait(self):
        pass












class Changer:
    def __init__(self, parent=None, mover=None, hold=True, ):
        
        pass
    def wait(self):
        pass
    def start(self):
        pass
    def status(self):
        pass





