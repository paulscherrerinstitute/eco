from enum import Enum
from eco.elements.adjustable import AdjustableGetSet, AdjustableFS
from eco.epics.adjustable import AdjustablePvEnum
from ..devices_general.motors import MotorRecord, SmaractRecord
from epics import PV
from ..aliases import Alias, append_object_to_object
from ..elements.assembly import Assembly
import numpy as np


class RefLaser_BerninaUSD(Assembly):
    def __init__(
        self,
        pvname_mirrortranslation="SARES20-MCS1:MOT_12",
        pvname_onoff="SARES21-PS7071:LV_OMPV_1_CH1_SWITCH_SP",
        outpos_adjfs_path=None,
        indiff=0.3,
        elog=None,
        name=None,
    ):
        super().__init__(name=name)
        self.elog = elog
        self.indiff = indiff
        # append_object_to_object(self,

        self._append(
            SmaractRecord, pvname_mirrortranslation, name="x_mirror", is_setting=True
        )
        self._append(
            AdjustablePvEnum, pvname_onoff, name="laser_power", is_setting=True
        )
        if outpos_adjfs_path:
            self._append(AdjustableFS, outpos_adjfs_path, name="last_out_position")
        else:
            self.last_out_position = None

    def movein(self, wait=False):
        if (not self.isin()) and self.last_out_position:
            self.last_out_position.set_target_value(
                self.x_mirror.get_current_value()
            ).wait()
        try:
            self.presets.movein()
        except:
            print("No movein preset found.")
        if not self.isin():
            print("WARNING: Reference laser was not moving in properly!")

    def isin(self):
        inpos = self.presets.movein.get_memory()["settings"]["x_mirror"]
        diff = self.x_mirror.get_current_value() - inpos
        if np.abs(diff) < self.indiff:
            return True
        else:
            return False

    def moveout(self, wait=False):
        if self.last_out_position:
            if self.isin():
                print("moving to last out position")
                self.x_mirror.set_target_value(
                    self.last_out_position.get_current_value()
                ).wait()
                self.laser_power(0)
            else:
                pass
        else:
            try:
                self.presets.moveout()
            except:
                print("No moveout preset found.")

        # self._append(
        #     AdjustableGetSet,
        #     self.get_in_status,
        #     self.set,
        #     name="state",
        #     is_setting=False,
        # )

        # self._append(MotorRecord, self.Id + ":MOTOR_1", name="mirror", is_setting=True)

        # self._append(
        #     RefLaserLaser,
        #     self.Id,
        #     name="laser",
        #     is_setting=True,
        #     is_display="recursive",
        # )
        # self._append(
        #     RefLaserAperture,
        #     "SAROP21-OLIR134",
        #     name="aperture",
        #     is_setting=True,
        #     is_display="recursive",
        # )

        # self._append(MotorRecord, pv_lir0 + ":MOTOR_MX", name="x_ap1", is_setting=True)
        # self._append(MotorRecord, pv_lir0 + ":MOTOR_MY", name="y_ap1", is_setting=True)
        # pv_lir1 = "SAROP21-OLIR138"  # TODO hardcoded
        # self._append(MotorRecord, pv_lir1 + ":MOTOR_MX", name="x_ap2", is_setting=True)
        # self._append(MotorRecord, pv_lir1 + ":MOTOR_MY", name="y_ap2", is_setting=True)
        # self.mirror.set_limits(-20, 0)


class RefLaser_Aramis(Assembly):
    def __init__(self, Id, elog=None, name=None, inpos=-19, outpos=-5):
        super().__init__(name=name)
        self.Id = Id
        self.elog = elog
        # append_object_to_object(self,

        self._inpos = inpos
        self._outpos = outpos

        self._append(
            AdjustableGetSet,
            self.get_in_status,
            self.set,
            name="state",
            is_setting=False,
        )

        self._append(MotorRecord, self.Id + ":MOTOR_1", name="mirror", is_setting=True)

        self._append(
            RefLaserLaser,
            self.Id,
            name="laser",
            is_setting=True,
            is_display="recursive",
        )
        self._append(
            RefLaserAperture,
            "SAROP21-OLIR134",
            name="aperture",
            is_setting=True,
            is_display="recursive",
        )

        # self._append(MotorRecord, pv_lir0 + ":MOTOR_MX", name="x_ap1", is_setting=True)
        # self._append(MotorRecord, pv_lir0 + ":MOTOR_MY", name="y_ap1", is_setting=True)
        # pv_lir1 = "SAROP21-OLIR138"  # TODO hardcoded
        # self._append(MotorRecord, pv_lir1 + ":MOTOR_MX", name="x_ap2", is_setting=True)
        # self._append(MotorRecord, pv_lir1 + ":MOTOR_MY", name="y_ap2", is_setting=True)
        self.mirror.set_limits(-20, 0)

    def __call__(self, *args, **kwargs):
        self.set(*args, **kwargs)

    def __str__(self):
        status = self.get_in_status()
        if status:
            return "Reflaser is In."
        elif status == False:
            return "Reflaser is Out."
        elif status == None:
            return "Reflaser status not defined."

    def get_in_status(self):
        v = self.mirror.get_current_value()
        if abs(v - self._inpos) < 0.2:
            isin = True
        elif abs(v - self._outpos) < 0.2:
            isin = False
        else:
            isin = None
        # return State(isin)
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
            self.mirror.set_target_value(self._inpos)
        else:
            self.mirror.set_target_value(self._outpos)

    def movein(self):
        self.set("in")

    def moveout(self):
        self.set("out")

    def __repr__(self):
        return self.__str__() + "\n" + super().__repr__()


class RefLaserAperture(Assembly):
    def __init__(self, pvname, name=None):
        super().__init__(name=name)
        self._append(
            MotorRecord,
            pvname + ":MOTOR_MX",
            name="x",
            is_setting=True,
            is_display=True,
        )
        self._append(
            MotorRecord,
            pvname + ":MOTOR_MY",
            name="y",
            is_setting=True,
            is_display=True,
        )


class RefLaserLaser(Assembly):
    def __init__(self, pvname, name=None):
        super().__init__(name=name)

        self._append(MotorRecord, pvname + ":MOTOR_X1", name="x", is_setting=True)
        self._append(MotorRecord, pvname + ":MOTOR_Z1", name="z", is_setting=True)
        self._append(MotorRecord, pvname + ":MOTOR_ROT_X1", name="rx", is_setting=True)
        self._append(MotorRecord, pvname + ":MOTOR_ROT_Z1", name="rz", is_setting=True)


class State(Enum):
    IN = 1
    OUT = 0
    UNDEFINED = None
