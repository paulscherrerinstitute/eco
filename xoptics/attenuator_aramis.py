from ..devices_general.motors import MotorRecord
from epics import PV

class AttenuatorAramis:
    def __init__(self, Id):
        self.Id = Id
        self._pv_status_str = PV(self.Id+':MOT2TRANS.VALD')
        self._pv_status_int = PV(self.Id+':IDX_RB')
        pass


    def __call__(self):
        pass
    def __str__(self):
        pass
    def __status__(self):
        pass
    def updateE(self, THG = False):
        energy = PV("SARUN03-UIND030:FELPHOTENE").value
        if (THG == True):
            energy = energy*3
        energy = energy *1000
        PV(self.Id+":ENERGY").put(energy)  
        print("Set energy to %s eV"%energy)
        return

    def set_transmission(self,value, THG = False):
        self.updateE(THG)
        PV(self.Id+":TRANS_SP").put(value)
        self.updateE(THG = False)
        print("Transmission Fundamental: %s THG: %s"%self.get_transmission())
        pass

    def setE(self):
        pass

    def get_transmission(self):
        tFun = PV(self.Id+":TRANS_RB").value
        tTHG = PV(self.Id+":TRANS3EDHARM_RB").value
        return (tFun, tTHG)

    def get_status(self):
        s_str = self._pv_status_str.get(as_string=True)
        s_int = self._pv_status_int.get()
        return s_str, s_int

    def __repr__(self):
        t = self.get_transmission()
        s =  '1st harm. transmission = %g\n'%t[0]
        s += '3rd harm. transmission = %g\n'%t[1]
        s += 'Targets in beam:\n'
        s += '%s'%self.get_status()[0]
        return s

    def __call__(self,*args,**kwargs):
        self.set_transmission(*args,**kwargs)
        





