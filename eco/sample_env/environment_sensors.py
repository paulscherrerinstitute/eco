from ..epics.detector import DetectorPvDataStream
from ..elements.assembly import Assembly

class Env_Sensors(Assembly):
    def __init__(self, name=None):
        super().__init__(name=name)
        self._append(
            DetectorPvDataStream,
            "SLAB-LI2C01_CH1:TEMP",
            name="sens1_temperature",
        )
        self._append(
            DetectorPvDataStream,
            "SLAB-LI2C01_CH1:HUMIREL",
            name="sens1_humidity",
        )
        self._append(
            DetectorPvDataStream, 
            "SLAB-LI2C01_CH1:PRES", 
            name="sens1_pressure"
        )
        self._append(
            DetectorPvDataStream,
            "SLAB-LI2C01_CH2:TEMP",
            name="sens2_temperature",
        )
        self._append(
            DetectorPvDataStream,
            "SLAB-LI2C01_CH2:HUMIREL",
            name="sens2_humidity",
        )
        self._append(
            DetectorPvDataStream, 
            "SLAB-LI2C01_CH2:PRES", 
            name="sens2_pressure"
        )
        self._append(
            DetectorPvDataStream,
            "SLAB-LI2C01_CH3:TEMP",
            name="pt100_temperature",
        )
