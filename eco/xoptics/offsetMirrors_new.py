from ..devices_general.motors import MotorRecord_new
from ..devices_general.adjustable import PvRecord, PvEnum
from ..elements.assembly import Assembly


class OffsetMirror(Assembly):
    def __init__(self, pvname, name=None):
        super().__init__(name=name)
        self.pvname = pvname
        self._append(MotorRecord_new, self.pvname + ":W_X", name="x", is_setting=True)
        self._append(MotorRecord_new, self.pvname + ":W_Y", name="y", is_setting=True)
        self._append(MotorRecord_new, self.pvname + ":W_RX", name="rx", is_setting=True)
        self._append(MotorRecord_new, self.pvname + ":W_RZ", name="rz", is_setting=True)
        self._append(
            PvRecord,
            self.pvname + ":CURV_SP",
            pvreadbackname=self.pvname + ":CURV",
            accuracy=None,
            name="curvature",
            is_setting=True,
        )
        self._append(
            PvRecord,
            self.pvname + ":ASYMMETRY_SP",
            pvreadbackname=self.pvname + ":ASYMMETRY",
            accuracy=None,
            name="asymmetry",
            is_setting=True,
        )


class OffsetMirrorsBernina(Assembly):
    def __init__(self, name=None):
        super().__init__(name=name)
        self._append(
            OffsetMirror,
            "SAROP21-OOMV092",
            name="mirr1",
            is_setting=True,
            view_toplevel_only=False,
        )
        self._append(
            OffsetMirror,
            "SAROP21-OOMV096",
            name="mirr2",
            is_setting=True,
            view_toplevel_only=False,
        )