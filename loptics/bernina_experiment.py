from ..devices_general.motors import MotorRecord
from epics import PV


class Laser_Exp:
    def __init__(self,Id):
        self.Id = Id
        self.delay_stage_offset =160.

        ### Mirrors used in the expeirment ###
        try:
            self.phi = MotorRecord(Id+'-M517:MOT')
        except:
            print('No Standa steering phi mirror')
            pass
        try:
            self.th = MotorRecord(Id+'-M518:MOT')
        except:
            print('No Standa steering theta mirror')
            pass
        
        self.delay_stage = MotorRecord(Id+'-M521:MOTOR_1')



    def get_delay(self):

        motor_pos = self.delay_stage.wm()
        motor_pos -= self.delay_stage_offset
        delay = motor_pos*2.*3.33333333
        return delay

    def delay_to_motor(self,delay):
        motor_pos = delay/2./3.33333333 + self.delay_stage_offset
        return motor_pos

    def set_delay(self, delay):
        motor_pos = self.delay_to_motor(delay)
        self.delay_stage.mv(motor_pos)
        return (delay, motor_pos) 

    
