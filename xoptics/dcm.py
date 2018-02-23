from ..devices_general.motors import MotorRecord
from epics import PV

class Double_Crystal_Mono:
    def __init__(self,Id):	
        self.Id = Id

        self.th = MotorRecord(Id+':RX12')
        self.x = MotorRecord(Id+':TX12')
        self.gap = MotorRecord(Id+':T2')
        self.roll1 = MotorRecord(Id+':RZ1')
        self.roll2 = MotorRecord(Id+':RZ2')
        self.pitch2 = MotorRecord(Id+':RX2')
#        self.energy = MotorRecord(Id+':ENERGY')

        self.energy = PV(Id+':ENERGY').value
