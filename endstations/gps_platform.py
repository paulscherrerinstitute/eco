import sys
sys.path.append("..")
from ..devices_general.motors import MotorRecord

class GPS:
    def __init__(self,Id,alias_namespace=None):
        self.Id = Id

        ### motors gps table ###
        self.x = MotorRecord(Id+':MOT_GPS_TBL_TX')
        self.y = MotorRecord(Id+':MOT_GPS_TBL_TZ')
        self.z = MotorRecord(Id+':MOT_GPS_TBL_TY')
        self.th = MotorRecord(Id+':MOT_GPS_MY_RYTH')
        try:
            self.pitch = MotorRecord(Id+':MOT_GPS_TILT_RX')
        except:
            print ('GPS.pitch not found')
            pass
        try:
            self.roll = MotorRecord(Id+':MOT_GPS_TILT_RY')
        except:
            print ('GPS.roll not found')
            pass

        ### motors hl gonio ###
        self.xmu = MotorRecord(Id+':MOT_GPS_PROBE_TX')
        self.mu = MotorRecord(Id+':MOT_GPS_PROBE_RX')
        self.tth = MotorRecord(Id+':MOT_GPS_NY_RY2TH')
        self.xhl = MotorRecord(Id+':MOT_GPS_TX')
        self.yhl = MotorRecord(Id+':MOT_GPS_TY')
                                         
