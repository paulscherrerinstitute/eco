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

    def __str__(self):
        return "Huber Sample Stage %s\nx: %s mm\ny: %s mm\nz: %s mm" \
                %(self.Id, self.x.wm(),self.y.wm(),self.z.wm())

    def __repr__(self):
        return "{'X': %s, 'Y': %s, 'Z': %s}"%(self.x.wm(),self.y.wm(),self.z.wm())

class vonHamosBragg:
    def __init__(self,Id,alias_namespace=None):
        self.Id = Id
		
        ### Owis linear stages ###
        self.cry1 = MotorRecord(Id+':CRY_1')
        self.cry2 = MotorRecord(Id+':CRY_2')

    def __str__(self):
        return "von Hamos positions\nCrystal 1: %s mm\nCrystal 2: %s mm" \
                  % (self.cry1.wm(),self.cry2.wm())

    def __repr__(self):
        return "{'Crystal 1': %s, 'Crystal 2': %s}" % (self.cry1.wm(),self.cry2.wm())

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
        self.x = MotorRecord(Id+':W_X')
        self.y = MotorRecord(Id+':W_Y')
        self.z = MotorRecord(Id+':W_Z')
        self.pitch = MotorRecord(Id+':W_RX')
        self.yaw = MotorRecord(Id+':W_RY')
        self.pitch = MotorRecord(Id+':W_RX')
        
    def __str__(self):
        return "Table positions\nx: %s mm\ny: %s mm\nz: %s\npitch: %s mm\nyaw: %s mm" \
            % (self.x.wm(),self.y.wm(),self.z.wm(),self.pitch.wm(),self.yaw.wm())

    def __repr__(self):
        return "{'x': %s, 'y': %s,'z': %s,'pitch': %s, 'yaw': %s}" \
            % (self.x,self.y,self.z,self.pitch,self.yaw)

class microscope:
    def __init__(self,Id,alias_namespace=None):
        self.Id = Id
		
        ### Microscope motors ###
        self.focus = MotorRecord(Id+':FOCUS')
        self.zoom = MotorRecord(Id+':ZOOM')
        self._smaractaxes = {
            'gonio': '_xmic_gon',   # will become self.gonio
            'rot':   '_xmic_rot'}   # """ self.rot

    def __str__(self):
        return "Microscope positions\nfocus: %s\nzoom:  %s\ngonio: %s\nrot:   %s"\
            % (self.focus.wm(),self.zoom.wm(),self.gonio.wm(),self.rot.wm())
            
    def __repr__(self):
        return "{'Focus': %s, 'Zoom': %s, 'Gonio': %s, 'Rot': %s}"\
            % (self.focus.wm(),self.zoom.wm(),self.gonio.wm(),self.rot.wm())
            
# prism (as a SmarAct-only stage) is defined purely in ../aliases/alvra.py
            
