from ..devices_general.motors import MotorRecord
from ..eco_epics.utilities_epics import EnumWrapper

class GasDetector:
    def __init__(self):
        pass

class SolidTargetDetectorPBPS:
    def __init__(self,Id,elog=None):
        self.Id = Id
        self.x_diode = MotorRecord(Id+':MOTOR_X1',elog=elog)
        self.y_diode = MotorRecord(Id+':MOTOR_Y1',elog=elog)
        self.y_target = MotorRecord(Id+':MOTOR_PROBE',elog=elog)
        self.target = EnumWrapper(Id+':PROBE_SP',elog=elog)

        #SAROP21-CVME-PBPS:Lnk10Ch15-WD-gain






