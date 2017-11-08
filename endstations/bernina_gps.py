import sys
sys.path.append("..")
from ..devices_general.motors import MotorRecord

class GPS:
    def __init__(self,Id,alias_namespace=None):
        self.Id = Id

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
                                         
