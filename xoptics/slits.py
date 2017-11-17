from ..devices_general.motors import MotorRecord

class SlitJJ(Id,elog=None):
    def __init__(Id,name=None,elog=None):
        self.Id = Id
        self.name = name
        self.xpos = MotorRecord(Id+':MOTOR_X')
        self.ypos = MotorRecord(Id+':MOTOR_Y')
        self.xgap = MotorRecord(Id+':MOTOR_W')
        self.y = MotorRecord(Id+':MOTOR_H')
        


    def set_hg(self,value):
        pass

    def set_vg(self,value):
        pass
    
    def set_ho(self,value):
        pass

    def set_vo(self,value):
        pass

    def set_gap(self,hor,ver):
        pass

    def set_offs(self,hor,ver):
        pass

    def __call__(self,*args):
        self.set_gap(*args)



