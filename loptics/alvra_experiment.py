from ..devices_general.motors import MotorRecord
#from ..devices_general.smaract import SmarActRecord

from epics import PV
from ..devices_general.delay_stage import DelayStage
from ..devices_general.user_to_motor import User_to_motor

class Laser_Exp:
	def __init__(self,Id):
		self.Id = Id

        #PALM delay stages 
		self.palm_delay = MotorRecord(self.Id+'-M423:MOT')
		self.palm_delayTime = DelayStage(self.palm_delay)
        
		self.palmEO_delay = MotorRecord(self.Id+'-M422:MOT')
		self.palmEO_delayTime = DelayStage(self.palmEO_delay)

        #PSEN delay stages
		self.psen_delay = MotorRecord(self.Id+'-M424:MOT')
		self.psen_delayTime = DelayStage(self.psen_delay)

	def get_adjustable_positions_str(self):
        ostr = '*****Motor positions******\n'

        for tkey,item in self.__dict__.items():
            if hasattr(item,'get_current_value'):
                pos = item.get_current_value()
                ostr += '  ' + tkey.ljust(10) + ' : % 14g\n'%pos
        return ostr

	def __repr__(self):
        return self.get_adjustable_positions_str()
        
