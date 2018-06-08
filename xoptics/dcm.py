from ..devices_general.motors import MotorRecord
from epics import PV
from ..devices_general.utilities import Changer
from time import sleep
import numpy as np

class Double_Crystal_Mono:
    def __init__(self,Id):	
     self.Id = Id
     self.theta = MotorRecord(Id+':RX12')
     self.x = MotorRecord(Id+':TX12')
     self.gap = MotorRecord(Id+':T2')
     self.roll1 = MotorRecord(Id+':RZ1')
     self.roll2 = MotorRecord(Id+':RZ2')
     self.pitch2 = MotorRecord(Id+':RX2')
	
     self.energy_rbk = PV(Id+':ENERGY')
     self.energy_sp = PV(Id+':ENERGY_SP')
     self.moving = PV(Id+':MOVING')
     self._stop = PV(Id +':STOP.PROC')

    def move_and_wait(self,value,checktime=.01,precision=.5):
        self.energy_sp.put(value)
        while abs(self.wait_for_valid_value()-value)>precision:
            sleep(checktime)

    def changeTo(self,value,hold=False):
        changer = lambda value: self.move_and_wait(value)
        return Changer(
                target=value,
                parent=self,
                changer=changer,
                hold=hold,
                stopper=self.stop)
      
    def stop(self):
        self._stop.put(1) 	

    def get_current_value(self):
     currentenergy = self.energy_rbk.get()
     return currentenergy

    def wait_for_valid_value(self):
        tval = np.nan
        while not np.isfinite(tval):
            tval = self.energy_rbk.get()
        return(tval)
    
    def set_current_value(self,value):
     self.energy_sp.put(value)
    
    def get_moveDone(self):
     inmotion = int(self.moving.get())
     return inmotion   
    
    # spec-inspired convenience methods
    def mv(self,value):
        self._currentChange = self.changeTo(value)
    def wm(self,*args,**kwargs):
        return self.get_current_value(*args,**kwargs)
    def mvr(self,value,*args,**kwargs):

        if(self.get_moveDone == 1):
            startvalue = self.get_current_value(*args,**kwargs)
        else:
            startvalue = self.get_current_value(*args,**kwargs)
        self._currentChange = self.changeTo(value+startvalue,*args,**kwargs)
    def wait(self):
        self._currentChange.wait()
        
    # return string with motor value as variable representation
    def __str__(self):
        return "Motor is at %s"%self.wm()
    
    def __repr__(self):
        return self.__str__()

    def __call__(self,value):
        self._currentChange = self.changeTo(value)


class EcolEnergy:
    def __init__(self,Id, val='SARCL02-MBND100:P-SET',rb='SARCL02-MBND100:P-READ' ,dmov='SFB_BEAM_ENERGY_ECOL:SUM-ERROR-OK'):
        self.Id = Id
        self.setter = PV(val)
        self.readback = PV(rb)
        self.dmov = PV(dmov)
        self.done = False

    def get_current_value(self):
        return self.readback.get()

    def move_and_wait(self,value,checktime=.01,precision=2):
        curr = self.setter.get()
        while abs(curr-value)>0.1:
            curr = self.setter.get()
            self.setter.put(curr + np.sign(value-curr)*.1)
            sleep(0.3)

        self.setter.put(value)
        while abs(self.get_current_value() - value)>precision:
            sleep(checktime)
        while not self.dmov.get():
            #print(self.dmov.get())
            sleep(checktime)
    
    def changeTo(self,value,hold=False):
        changer = lambda value: self.move_and_wait(value)
        return Changer(
                target=value,
                parent=self,
                changer=changer,
                hold=hold,
                stopper=None)


class MonoEcolEnergy:
    def __init__(self,Id):
        self.Id = Id
        self.name = 'energy_collimator'
        self.dcm = Double_Crystal_Mono(Id)
        self.ecol = EcolEnergy('ecol_dummy')
        self.offset = None
        self.MeVperEV = 0.78333
        

    def get_current_value(self):
        return self.dcm.get_current_value()

    def move_and_wait(self,value):
        ch = [self.dcm.changeTo(value),
                self.ecol.changeTo(self.calcEcol(value))]
        for tc in ch:
            tc.wait()

    def changeTo(self,value,hold=False):
        changer = lambda value: self.move_and_wait(value)
        return Changer(
                target=value,
                parent=self,
                changer=changer,
                hold=hold,
                stopper=self.dcm.stop)

    def alignOffsets(self):
        mrb = self.dcm.get_current_value()
        erb = self.ecol.get_current_value()
        self.offset = {'dcm':mrb, 'ecol':erb}

    def calcEcol(self,eV):
        return (eV-self.offset['dcm'])*self.MeVperEV + self.offset['ecol']





