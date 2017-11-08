from ..devices_general.motors import MotorRecord

class Double_Crystal_Mono:
    def __init__(self,Id):	
        self.Id = Id

        self.phi = MotorRecord(Id+'')

