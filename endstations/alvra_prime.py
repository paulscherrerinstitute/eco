import sys
sys.path.append("..")
from ..devices_general.motors import MotorRecord
from epics import PV

class huber:
	def __init__(self,Id,alias_namespace=None):
		self.Id = Id
		
		### Huber sample stages ###
		self.x = MotorRecord(Id+':MOTOR_X1')
		self.y = MotorRecord(Id+':MOTOR_Y1')
		self.z = MotorRecord(Id+':MOTOR_Z1')
