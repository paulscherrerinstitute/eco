from ..devices_general.motors import MotorRecord
from epics import PV

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

<<<<<<< HEAD
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
    
=======
        self.th = MotorRecord(Id+':RX12')
        self.x = MotorRecord(Id+':TX12')
        self.gap = MotorRecord(Id+':T2')
        self.roll1 = MotorRecord(Id+':RZ1')
        self.roll2 = MotorRecord(Id+':RZ2')
        self.pitch2 = MotorRecord(Id+':RX2')

        self.energy = PV(Id+':ENERGY').value
#		self.set_energy = PV(Id+':ENERGY_SP').value
		
>>>>>>> 1e1a12d037b38eb4dd93c24a0eb6ee6a55ab6548
