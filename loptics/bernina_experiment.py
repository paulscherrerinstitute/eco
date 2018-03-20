from ..devices_general.motors import MotorRecord
from ..devices_general.smaract import SmarActRecord
from epics import PV
from .delay_stage import DelayStage

class Laser_Exp:
    def __init__(self,Id):
        self.Id = Id



        try:
            self.lensx = MotorRecord('SARES20-EXP:MOT_DIODE')
        except:
            print('No owis lens x motor')
            pass
        
        #Waveplate and Delay stage
        self.wp = MotorRecord(Id+'-M533:MOT')
  
        #SmarAct ID
        self.IdSA = 'SARES23'
        self._delayStg = SmarActRecord(self.IdSA+'-ESB17')
        self.eos_delay = DelayStage(self._delayStg)


        ### Mirrors used in the expeirment ###
        try:
            self.eos_rot = SmarActRecord(self.IdSA+'-ESB18')
        except:
            print('No Smaract EOSrot')
            pass

        try:
            self.eos_gonio = SmarActRecord(self.IdSA+'-ESB3')
        except:
            print('No Smaract EOSGonio')
            pass

        try:
            self.thz_rot = SmarActRecord(self.IdSA+'-ESB16')
        except:
            print('No Smaract THzrot')
            pass

        try:
            self.thz_gonio = SmarActRecord(self.IdSA+'-ESB2')
        except:
            print('No Smaract THzGonio')
            pass
        
        try:
            self.thz_z = SmarActRecord(self.IdSA+'-ESB1')
        except:
            print('No Smaract THzZ')
            pass

        try:
            self.par_x = SmarActRecord(self.IdSA+'-ESB5')
        except:
            print('No Smaract ParX')
            pass
        try:
            self.par_z = SmarActRecord(self.IdSA+'-ESB4')
        except:
            print('No Smaract ParZ')
            pass


    def get_adjustable_positions_str(self):
        ostr = '*****SmarAct motor positions******\n'

        for tkey,item in self.__dict__.items():
            if hasattr(item,'get_current_value'):
                pos = item.get_current_value()
                ostr += '  ' + tkey.ljust(10) + ' : % 14g\n'%pos
        return ostr
                


    #def pos(self):
    #    s = []
    #    for i in sorted(self.__dict__.keys()):
    #        s.append[i]
    #    for n, mo^tor in enumerate (s):
    #        s[n] += ':  ' + str(self.__dict__[motor])
    #    return s

    def __repr__(self):
        return self.get_adjustable_positions_str()
        
