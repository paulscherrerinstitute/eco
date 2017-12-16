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
        return "Huber Stage %s\nx: %s mm\ny: %s mm\nz: %s mm" \
                %(self.Id, self.x.wm(),self.y.wm(),self.z.wm())

    def __repr__(self):
        return "{'x': %s, 'y': %s, 'z': %s}"%(self.x.wm(),self.y.wm(),self.z.wm())

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
        return "{'cry 1': %s, 'cry 2': %s}" % (self.cry1.wm(),self.cry2.wm())

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
        
    def __str__(self):
        return "Table positions\nx1: %s mm\ny1: %s mm\ny2: %s\ny3: %s mm\nz1: %s mm\nz2: %s mm" \
            % (self.x1.wm(),self.y1.wm(),self.y2.wm(),self.y3.wm(),self.z1.wm(),self.z2.wm())

    def __repr__(self):
        return "{'x1': %s, 'y1': %s,'y2': %s,'y3': %s, 'z1': %s, 'z2': %s}" \
            % (self.x1,self.y1,self.y2,self.y3,self.z1,self.z2)

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
        return "{'focus': %s, 'zoom': %s, 'gonio': %s, 'rot': %s}"\
            % (self.focus.wm(),self.zoom.wm(),self.gonio.wm(),self.rot.wm())
            
# prism (as a SmarAct-only stage) is defined purely in ../aliases/alvra.py
            
