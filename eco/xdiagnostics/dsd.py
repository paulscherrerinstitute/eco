import sys

sys.path.append("..")

from ..devices_general.motors import MotorRecord
from ..devices_general.smaract import SmarActRecord
from ..epics.adjustable import AdjustablePv
from ..aliases import Alias, append_object_to_object
from ..elements.assembly import Assembly
from .profile_monitors import Pprm_dsd
from .intensity_monitors import SolidTargetDetectorPBPS_new_assembly
import numpy as np
from epics import PV


class DownstreamDiagnostic(Assembly):
    def __init__(
        self,
        name=None,
    ):
        super().__init__(name=name)
        self._append(
            MotorRecord, "SARES20-DSD:MOTOR_DSDX", name="xbase", is_setting=True
        )
        self._append(
            MotorRecord, "SARES20-DSD:MOTOR_DSDY", name="ybase", is_setting=True
        )

    def get_xyposition_for_kb_angles_in_rad(self, theta_kbver, theta_kbhor):
        y = np.tan(2 * theta_kbver) * 7075
        x = np.tan(2 * theta_kbhor) / np.cos(2 * theta_kbver) * 6325
        return x, y

    def home(self,**kwargs):
        self._run_cmd("python /ioc/qt/ESB_DSD_home.py SARES20-DSD", **kwargs)

    def gui(self):
        self._run_cmd("caqtdm -noMsg  -macro P=SARES20-DSD  /ioc/qt/ESB_DSD_motors.ui")
