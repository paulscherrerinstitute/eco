from ..eco_epics.motor import Motor as _Motor
import subprocess
from threading import Thread

_MotorRocordStandardProperties = \
        {}
_posTypes = ['user','dial','raw']
_guiTypes = ['xdm']

def _keywordChecker(kw_key_list_tups):
    for tkw,tkey,tlist in kw_key_list_tups:
        assert tkey in tlist, "Keyword %s should be one of %s"%(tkw,tlist)

class MotorRecord:
    def __init__(self,pvname):
        self.Id = pvname
        self._motor = _Motor(pvname)

    # Conventional methods and properties for all Adjustable objects
    def changeTo(self, value, hold=False, check=True):
        """ Adjustable convention"""

        mover = lambda value: self._motor.move(\
                value, ignore_limits=(not check),
                wait=True)
        return Changer(
                target=value,
                parent=self,
                mover=mover,
                hold=hold,
                stopper=self._motor.stop)

    def get_current_value(self,posType='user'):
        """ Adjustable convention"""
        _keywordChecker([('posType',posType,_posTypes)])
        if posType == 'user':
            return self._motor.get_position()
        if posType == 'dial':
            return self._motor.get_position(dial=True)
        if posType == 'raw':
            return self._motor.get_position(raw=True)

    def set_current_value(self,value,posType='user'):
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
        cmd = ['caqtdm','-macro']

        cmd.append('\"P=%s:,M=%s\"'%tuple(self.Id.split(':')))
        cmd.append('/sf/common/config/qt/motorx_all.ui')
        #os.system(' '.join(cmd))
        return subprocess.Popen(' '.join(cmd),shell=True)



    # epics motor record specific methods


    # spec-inspired convenience methods
    def mv(self,value):
        self._currentChange = self.changeTo(value)
    def wm(self,*args,**kwargs):
        self.get_current_value(*args,**kwargs)
    def mvr(self,value,*args,**kwargs):
        startvalue = self.get_current_value(*args,**kwargs)
        self._currentChange = self.changeTo(value+startvalue,*args,**kwargs)
    def wait(self):
        self._currentChange.wait()












class Changer:
    def __init__(self, target=None, parent=None, mover=None, hold=True, stopper=None):
        self.target = target
        self._mover = mover
        self._stopper = stopper
        self._thread = Thread(target=self._mover,args=(target,))
        if not hold:
            self._thread.start()

    def wait(self):
        self._thread.join()

    def start(self):
        self._thread.start()

    def status(self):
        if self._thread.ident is None:
            return 'waiting'
        else:
            if self._isAlive:
                return 'changing'
            else:
                return 'done'
    def stop(self):
        self._stopper()



