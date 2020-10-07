from ..devices_general.motors import MotorRecord
from epics import PV
from ..aliases import Alias, append_object_to_object


class RefLaser_Aramis:
    def __init__(self, Id, elog=None, name=None, inpos=-18.818, outpos=-5):
        self.Id = Id
        self.elog = elog
        self.name = name
        self.alias = Alias(name)
        # append_object_to_object(self,

        self._inpos = inpos
        self._outpos = outpos
        self.mirrmotortest = MotorRecord(self.Id + ":MOTOR_1")
        self.mirrmotortest.set_limits(-20, 0)

    def __call__(self, *args, **kwargs):
        self.set(*args, **kwargs)

    def __str__(self):
        status = self.get_status()
        if status:
            return "Reflaser is In."
        elif status == False:
            return "Reflaser is Out."
        elif status == None:
            return "Reflaser status not defined."

    def get_status(self):
        v = self.mirrmotortest.get_current_value()
        if abs(v - self._inpos) < 0.2:
            isin = True
        elif abs(v - self._outpos) < 0.2:
            isin = False
        else:
            isin = None
        return isin

    def set(self, value):
        if type(value) is str:
            if value.lower() == "in":
                value = True
            elif value.lower() == "out":
                value = False
            else:
                print("String %s not recognized!" % value)
        if value:
            self.mirrmotortest.set_target_value(self._inpos)
        else:
            self.mirrmotortest.set_target_value(self._outpos)

    def movein(self):
        self.set("in")

    def moveout(self):
        self.set("out")

    def __repr__(self):
        return self.__str__()
