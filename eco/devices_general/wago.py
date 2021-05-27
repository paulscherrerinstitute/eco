
from eco.elements import Assembly
from eco.epics.detector import DetectorPvData
from eco.epics.adjustable import AdjustablePvString, AdjustablePv

class AnalogInput(Assembly):
    def __init__(self,pvname,name=None):
        super().__init__(name=name)
        self.pvname = pvname
        self._append(DetectorPvData, self.pvname, name='value', is_setting=False, is_status=True)
        self._append(AdjustablePvString, self.pvname + '.DESC', name='description', is_setting=True, is_status=True)
        self._append(AdjustablePvString, self.pvname + '.EGU', name='unit', is_setting=False, is_status=False)
        self._append(DetectorPvData, self.pvname + '.RVAL', name='raw', is_setting=False, is_status=False)
    def get_current_value(self):
        return self.value.get_current_value()


class WagoAnalogInputs(Assembly):
    def __init__(self,pvbase,name=None):
        super().__init__(name=name)
        self.pvbase = pvbase
        for n in range(1,9):
            self._append(AnalogInput,pvbase+f':ADC{n:02d}', name=f'ch{n:d}')