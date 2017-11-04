from ..devices_general.motors import MotorRecord
from ..devices_general.detectors import CameraCA
#from ..devices_general.epics_wrappers import EnumSelector
from epics import PV

class Pprm:
    def __init__(self,Id,alias_namespace=None):
        self.Id = Id
        self.targetY = MotorRecord(Id+':MOTOR_PROBE')
        self.cam = CameraCA(Id)
        self._led = PV(self.Id+':LED')

    def illuminate(self,value=None):
        if value:
            self._led.put(value)
        else:
            self._led.put(
                    not self.get_illumination_state())

    def get_illumination_state(self):
        return bool(self._led.get())





        



