from eco import Assembly
from eco.devices_general.motors import MotorRecord
from eco.detector.jungfrau import Jungfrau

class VHamos(Assembly):
    def __init__(self,name='vhamos',pgroup_adj=None, config_adjustable=None):
        super().__init__(name=name)
        # self._append(MotorRecord,"SARES20-MF1:MOT_8",name="cdist_downstream")
        self._append(MotorRecord,"SARES20-MF1:MOT_8",name="cdist")
        self._append(Jungfrau, "JF14T01V01", config_adj=config_adjustable, pgroup_adj=pgroup_adj, name="det_spec")