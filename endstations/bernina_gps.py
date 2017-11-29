import sys
sys.path.append("..")
from ..devices_general.motors import MotorRecord
from epics import PV

class GPS:
    def __init__(self,Id,alias_namespace=None):
        self.Id = Id

        motors = {
            'xhl' : Id+':MOT_GPS_TBL_TX',
            'yhl' : Id+':MOT_GPS_TBL_TZ',
            'zhl' : Id+':MOT_GPS_TBL_TY'}

            
        ### motors heavy load gps table ###
        self.xhl = MotorRecord(Id+':MOT_GPS_TBL_TX')
        self.yhl = MotorRecord(Id+':MOT_GPS_TBL_TZ')
        self.zhl = MotorRecord(Id+':MOT_GPS_TBL_TY')
        self.th = MotorRecord(Id+':MOT_GPS_MY_RYTH')
        try:
            self.pitchhl = MotorRecord(Id+':MOT_GPS_TILT_RX')
        except:
            print ('GPS.pitch not found')
            pass
        try:
            self.rollhl = MotorRecord(Id+':MOT_GPS_TILT_RY')
        except:
            print ('GPS.roll not found')
            pass

        ### motors heavy load gonio base ###
        self.xmu = MotorRecord(Id+':MOT_GPS_PROBE_TX')
        self.mu = MotorRecord(Id+':MOT_GPS_PROBE_RX')
        self.tth = MotorRecord(Id+':MOT_GPS_NY_RY2TH')
        self.xbase = MotorRecord(Id+':MOT_GPS_TX')
        self.ybase = MotorRecord(Id+':MOT_GPS_TY')

        self.hex_x = PV("SARES20-HEX_PI:POSI-X")
        self.hex_y = PV("SARES20-HEX_PI:POSI-Y")
        self.hex_z = PV("SARES20-HEX_PI:POSI-Z")
        self.hex_u = PV("SARES20-HEX_PI:POSI-U")
        self.hex_v = PV("SARES20-HEX_PI:POSI-V")
        self.hex_w = PV("SARES20-HEX_PI:POSI-W")

    def __repr__(self):
        s = "**Heavy Load**\n"
        motors = "xmu mu tth xbase ybase".split()
        for motor in motors:
            s+= " - %s %.4f\n"%(motor,getattr(self,motor).wm())

        s+= " - HLX %.4f\n"%(self.xhl.wm())
        s+= " - HLY %.4f\n"%(self.yhl.wm())
        s+= " - HLZ %.4f\n"%(self.zhl.wm())
        s+= " - HLTheta %.4f\n"%(self.th.wm())
        s+= "\n"

        s+= "**Gonio**\n"
        motors = "xmu mu tth xbase ybase".split()
        for motor in motors:
            s+= " - %s %.4f\n"%(motor,getattr(self,motor).wm())
        s+= "\n"

        s+= "**Hexapod**\n"
        motors = "x y z u v w".split()
        for motor in motors:
            s+= " - hex_%s %.4f\n"%(motor,getattr(self,"hex_"+motor).get())
        return s
        
