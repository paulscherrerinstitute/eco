from ..devices_general.motors import MotorRecord
from ..eco_epics.utilities_epics import EnumWrapper
from ..devices_general.detectors import FeDigitizer
from ..devices_general.adjustable import PvEnum
from ..aliases import Alias


class GasDetector:
    def __init__(self):
        pass


class SolidTargetDetectorPBPS:
    def __init__(
        self,
        Id,
        VME_crate=None,
        link=None,
        ch_up=12,
        ch_down=13,
        ch_left=15,
        ch_right=14,
        elog=None,
        name=None,
    ):
        self.Id = Id
        self.name = name
        self.diode_x = MotorRecord(Id + ":MOTOR_X1", name="diode_x")
        self.diode_y = MotorRecord(Id + ":MOTOR_Y1", name="diode_y")
        self.target_pos = MotorRecord(Id + ":MOTOR_PROBE", name="target_pos")
        self.target = PvEnum(Id + ":PROBE_SP", name="target")
        if VME_crate:
            self.diode_up = FeDigitizer("%s:Lnk%dCh%d" % (VME_crate, link, ch_up))
            self.diode_down = FeDigitizer("%s:Lnk%dCh%d" % (VME_crate, link, ch_down))
            self.diode_left = FeDigitizer("%s:Lnk%dCh%d" % (VME_crate, link, ch_left))
            self.diode_right = FeDigitizer("%s:Lnk%dCh%d" % (VME_crate, link, ch_right))

        if self.name:
            self.alias = Alias(name)
            self.alias.append(self.diode_x.alias)
            self.alias.append(self.diode_y.alias)
            self.alias.append(self.target_pos.alias)
            self.alias.append(self.target.alias)

    def __repr__(self):
        s = f"**Intensity  monitor {self.name}**\n\n"

        s += f"Target in: {self.target.get_current_value().name}\n\n"
        try:
            sd = "**Biasd voltage**\n"
            sd += " - Diode up: %.4f\n" % (sdelf.diode_up.get_biasd())
            sd += " - Diode down: %.4f\n" % (sdelf.diode_down.get_biasd())
            sd += " - Diode left: %.4f\n" % (sdelf.diode_left.get_biasd())
            sd += " - Diode right: %.4f\n" % (sdelf.diode_right.get_biasd())
            sd += "\n"

            sd += "**Gain**\n"
            sd += " - Diode up: %i\n" % (sdelf.diode_up.gain.get())
            sd += " - Diode down: %i\n" % (sdelf.diode_down.gain.get())
            sd += " - Diode left: %i\n" % (sdelf.diode_left.gain.get())
            sd += " - Diode right: %i\n" % (sdelf.diode_right.gain.get())
            s += sd
        except:
            pass
        return s

    def set_gains(self, value):
        try:
            self.diode_up.gain.set(value)
            self.diode_down.gain.set(value)
            self.diode_left.gain.set(value)
            self.diode_right.gain.set(value)
        except:
            print("No diodes configured, can not change any gain!")

    def get_available_gains(self):
        try:
            nu = self.diode_up.gain.names
            nd = self.diode_down.gain.names
            nl = self.diode_left.gain.names
            nr = self.diode_right.gain.names
            assert (
                nu == nd == nl == nr
            ), "NB: the gain options of the four diodes are not equal!!!"
            return nu
        except:
            print("No diodes configured, can not change any gain!")

    def get_gains(self):
        try:
            gains = dict()
            gains["up"] = (self.diode_up.gain.get_name(), self.diode_up.gain.get())
            gains["down"] = (
                self.diode_down.gain.get_name(),
                self.diode_down.gain.get(),
            )
            gains["left"] = (
                self.diode_left.gain.get_name(),
                self.diode_left.gain.get(),
            )
            gains["right"] = (
                self.diode_right.gain.get_name(),
                self.diode_right.gain.get(),
            )
            return gains
        except:
            print("No diodes configured, can not change any gain!")

        # SAROP21-CVME-PBPS:Lnk10Ch15-WD-gain
