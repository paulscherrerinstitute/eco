from ..devices_general.utilities import Changer
from epics import PV
from ..aliases import Alias


_status_messages = {
    -13: "invalid value (cannot convert to float).  Move not attempted.",
    -12: "target value outside soft limits.         Move not attempted.",
    -11: "drive PV is not connected:                Move not attempted.",
    -8: "move started, but timed-out.",
    -7: "move started, timed-out, but appears done.",
    -5: "move started, unexpected return value from PV.put()",
    -4: "move-with-wait finished, soft limit violation seen",
    -3: "move-with-wait finished, hard limit violation seen",
    0: "move-with-wait finish OK.",
    0: "move-without-wait executed, not comfirmed",
    1: "move-without-wait executed, move confirmed",
    3: "move-without-wait finished, hard limit violation seen",
    4: "move-without-wait finished, soft limit violation seen",
}


class DelayStage:
    def __init__(self, stage, name=None):
        self._stage = stage
        self.delay_stage_offset = 0.0
        self.name = name
        self.alias = Alias(name)
        self.Id = self._stage.Id
        self._elog = self._stage._elog

    def delay_to_motor(self, delay):
        motor_pos = delay / 2.0 / 3.33333333 * 1e12
        return motor_pos

    def get_current_value(self):
        """Adjustable convention"""
        motor_pos = self._stage.get_current_value()
        motor_pos -= self.delay_stage_offset
        delay = motor_pos * 2.0 * 3.33333333 * 1e-12
        return delay

    def set_current_value(self, value):
        motor_pos = self.delay_to_motor(value) + self.delay_stage_offset
        self._stage.set_current_value(motor_pos)
        return (value, motor_pos)

    def set_target_value(self, value, hold=False, check=True):
        value = self.delay_to_motor(value) + self.delay_stage_offset
        delay = (value - self.delay_stage_offset) * 2.0 * 3.33333333 * 1e-12
        return self._stage.set_target_value(value, hold, check)

    def gui(self, guiType="xdm"):
        return self._stage.gui()

    # spec-inspired convenience methods
    def mv(self, value):
        self._stage._currentChange = self.set_target_value(value)

    def wm(self, *args, **kwargs):
        return self.get_current_value(*args, **kwargs)

    def mvr(self, value, *args, **kwargs):
        motor_pos = self.delay_to_motor(value)
        self._stage.mvr(motor_pos)

    def wait(self):
        self._stage._currentChange.wait()

    def stop(self):
        """Adjustable convention"""
        try:
            self._stage._currentChange.stop()
        except:
            self._stage.stop()
        pass

    # return string with motor value as variable representation
    def __str__(self):
        return "Motor is at %s" % self.wm()

    def __repr__(self):
        return self.__str__()

    def __call__(self, value):
        self._currentChange = self.set_target_value(value)
