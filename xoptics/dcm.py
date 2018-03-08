from ..devices_general.motors import MotorRecord
from epics import PV
from ..devices_general.utilities import Changer
from time import sleep

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
        #sleep(.1)
        while abs(self.get_current_value()-value)>precision:
            print(abs(self.get_current_value()-value))
            sleep(checktime)
            print(abs(self.get_current_value()-value))

    def changeTo(self,value):
        self.energy_sp.put(value)
      
    def stop(self):
        self._stop.put(1) 	

    def get_current_value(self):
     currentenergy = self.energy_rbk.get()
     return currentenergy
    
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
