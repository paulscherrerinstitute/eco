from ..devices_general.motors import SmaractRecord
from ..elements.assembly import Assembly


class SmaractController(Assembly):
    def __init__(self, pvbase, name=None):
        super().__init__(name=name)
        self.pvbase = pvbase
        self.all_stages = []
        for n in range(1, 19):
            self._append(
                SmaractRecord,
                f"{pvbase}{n}",
                name=f"stage{n}",
                is_setting=True,
                is_display=True,
            )
            self.all_stages.append(self.__dict__[f"stage{n}"])
        self.set_autozero_on()
    def home_all(self):
        pass

    def set_autozero_on(self):
        for stg in self.all_stages:
            stg.motor_parameters.autozero_on_homing(1)
