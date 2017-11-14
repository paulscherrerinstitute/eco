from ..devices_general.motors import MotorRecord
from ..eco_epics.utilities_epics import EnumWrapper
from ..devices_general.detectors import FeDigitizer

class GasDetector:
    def __init__(self):
        pass

class SolidTargetDetectorPBPS:
    def __init__(self,Id,VME_crate=None,link=None,
            ch_up=12,ch_down=13,ch_left=15,ch_right=14,
            elog=None):
        self.Id = Id
        self.x_diode = MotorRecord(Id+':MOTOR_X1',elog=elog)
        self.y_diode = MotorRecord(Id+':MOTOR_Y1',elog=elog)
        self.y_target = MotorRecord(Id+':MOTOR_PROBE',elog=elog)
        self.target = EnumWrapper(Id+':PROBE_SP',elog=elog)
        if VME_crate:
            self.diode_up = FeDigitizer('%s:Lnk%dCh%d'%(VME_crate,link,ch_up))
            self.diode_down = FeDigitizer('%s:Lnk%dCh%d'%(VME_crate,link,ch_down))
            self.diode_left = FeDigitizer('%s:Lnk%dCh%d'%(VME_crate,link,ch_left))
            self.diode_right = FeDigitizer('%s:Lnk%dCh%d'%(VME_crate,link,ch_right))


            

        #SAROP21-CVME-PBPS:Lnk10Ch15-WD-gain






