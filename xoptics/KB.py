from ..devices_general.motors import MotorRecord
from epics import PV

class KB:
    def __init__(self,Id):	
        self.Id = Id

        self.x = MotorRecord(Id+':W_X')
        self.y = MotorRecord(Id+':W_Y')
        self.pitch = MotorRecord(Id+':W_RX')
        self.roll = MotorRecord(Id+':W_RZ')
        self.yaw = MotorRecord(Id+':W_RY')
        self.bend1 = MotorRecord(Id+':BU')
        self.bend2 = MotorRecord(Id+':BD')

        self.mode = PV(Id[:11]+':MODE').enum_strs[PV(Id[:11]+':MODE').value]

    def __str__(self):
        return "KB is %s"%self.mode.lower()
    
    def __repr__(self):
        return self.__str__()
