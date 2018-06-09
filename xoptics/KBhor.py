from ..devices_general.motors import MotorRecord
from epics import PV

class KBhor:
    def __init__(self,Id):	
        self.Id = Id

        self.x = MotorRecord(Id+':W_X')
        self.y = MotorRecord(Id+':W_Y')
        self.pitch = MotorRecord(Id+':W_RY')
        self.roll = MotorRecord(Id+':W_RZ')
        self.yaw = MotorRecord(Id+':W_RX')
        self.bend1 = MotorRecord(Id+':BU')
        self.bend2 = MotorRecord(Id+':BD')

        self.mode = PV(Id[:11]+':MODE').enum_strs[PV(Id[:11]+':MODE').value]

    def __str__(self):
        s = "**Horizontal KB mirror**\n\n"
        motors = "bend1 bend2 pitch roll yaw x y".split()
        for motor in motors:
            s+= " - %s = %.4f\n" %(motor, getattr(self,motor).wm())
        return s
    
    def __repr__(self):
        return self.__str__()
