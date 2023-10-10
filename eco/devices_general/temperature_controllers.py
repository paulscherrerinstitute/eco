from ..aliases import Alias, append_object_to_object
from ..elements.adjustable import AdjustableVirtual, AdjustableGetSet, value_property
from ..epics.adjustable import AdjustablePv, AdjustablePvEnum
from ..elements.assembly import Assembly
class Lakeshore_331(Assembly):
    def __init__(self, pvname, name=None):
        super().__init__(name=name)
        self.pvname = pvname
        self._append(
            AdjustablePv,
            pvsetname = "SLAB-LLS-UNIT1:HT-LVL_RBV",
            pvreadbackname = "SLAB-LLS-UNIT1:HT-LVL_RBV",
            accuracy = 0.5,
            name="heater_level",
            is_display=True,
            is_setting=False,
        )
        self._append(
            AdjustablePv,
            pvsetname = f"{self.pvname}:TEMP.VAL",
            pvreadbackname = f"{self.pvname}:TEMP_RBV",
            accuracy = 0.5,
            name="temperature",
            is_display=True,
            is_setting=True,
        )
        self._append(
            AdjustablePvEnum,
            pvname = self.pvname + ":CONN",
            name="connect",
            is_setting=True,
            is_display=False,
        )
        self._append(
            AdjustablePvEnum,
            pvname = self.pvname + ":HT-RNG_RBV",
            pvname_set = self.pvname + ":HT-RNG",
            name="heater_range",
            is_setting=True,
            is_display=True,
        )
        self._append(
            AdjustablePvEnum,
            pvname = self.pvname + ":MODE_RBV",
            pvname_set = self.pvname + ":MODE",
            name="operation",
            is_setting=True,
            is_display=True,
        )
