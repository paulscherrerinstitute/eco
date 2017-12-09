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

class vonHamosBragg:
	def __init__(self,Id,alias_namespace=None):
		self.Id = Id
		
		### Owis linear stages ###
		self.cry1 = MotorRecord(Id+':CRY_1')
		self.cry2 = MotorRecord(Id+':CRY_2')

class table:
	def __init__(self,Id,alias_namespace=None):
		self.Id = Id
		
		### ADC optical table ###
		self.x1 = MotorRecord(Id+':MOTOR_X1')
		self.y1 = MotorRecord(Id+':MOTOR_Y1')
		self.y2 = MotorRecord(Id+':MOTOR_Y2')
		self.y3 = MotorRecord(Id+':MOTOR_Y3')
		self.z1 = MotorRecord(Id+':MOTOR_Z1')
		self.z2 = MotorRecord(Id+':MOTOR_Z2')
		
class microscopeOpt:
	def __init__(self,Id,alias_namespace=None):
		self.Id = Id
		
		### Microscope focus and zoom motors ###
		self.focus = MotorRecord(Id+':FOCUS')
		self.zoom = MotorRecord(Id+':ZOOM')