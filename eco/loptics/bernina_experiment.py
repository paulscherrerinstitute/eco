from ..aliases import Alias
from ..devices_general.motors import MotorRecord
from ..devices_general.smaract import SmarActRecord

from epics import PV
from ..devices_general.delay_stage import DelayStage
from ..devices_general.adjustable import AdjustableVirtual


def addMotorRecordToSelf(self, Id=None, name=None):
    self.__dict__[name] = MotorRecord(Id, name=name)
    self.alias.append(self.__dict__[name].alias)


def addSmarActRecordToSelf(self, Id=None, name=None):
    self.__dict__[name] = SmarActRecord(Id, name=name)
    self.alias.append(self.__dict__[name].alias)


def addDelayStageToSelf(self, stage=None, name=None):
    self.__dict__[name] = DelayStage(stage, name=name)
    self.alias.append(self.__dict__[name].alias)


class DelayTime(AdjustableVirtual):
    def __init__(self, stage, direction=1, passes=2, set_current_value=True, name=None):
        self._direction = direction
        self._group_velo = 299798458  # m/s
        self._passes = passes
        self.Id = stage.Id + "_delay"
        AdjustableVirtual.__init__(
            self,
            [stage],
            self._mm_to_s,
            self._s_to_mm,
            set_current_value=set_current_value,
            name=name,
        )

    def _mm_to_s(self, mm):
        return mm * 1e-3 * self._passes / self._group_velo * self._direction

    def _s_to_mm(self, s):
        return s * self._group_velo * 1e3 / self._passes * self._direction


class DelayCompensation(AdjustableVirtual):
    """Simple virtual adjustable for compensating delay adjustables. It assumes the first adjustable is the master for 
    getting the current value."""

    def __init__(self, adjustables, directions, set_current_value=True, name=None):
        self._directions = directions
        self.Id = name
        AdjustableVirtual.__init__(
            self,
            adjustables,
            self._from_values,
            self._calc_values,
            set_current_value=set_current_value,
            name=name,
        )

    def _calc_values(self, value):
        return tuple(tdir * value for tdir in self._directions)

    def _from_values(self, *args):
        positions = [ta * tdir for ta, tdir in zip(args, self._directions)]
        return positions[0]

        tuple(tdir * value for tdir in self._directions)


class Laser_Exp:
    def __init__(self, Id=None, name=None, smar_config=None):
        self.Id = Id
        self.IdExp1 = "SARES20-EXP"
        self.IdSA = "SARES23"
        self.name = name
        self.alias = Alias(name)
        self.smar_config = smar_config

        # Waveplate and Delay stage
        try:
            addMotorRecordToSelf(self, self.Id + "-M534:MOT", name="pump_wp")
            addMotorRecordToSelf(self, self.Id + "-M533:MOT", name="tt_wp")
        except:
            print("No wp found")

        try:
            addMotorRecordToSelf(
                self, Id=self.Id + "-M521:MOTOR_1", name="_pump_delaystg"
            )
            addDelayStageToSelf(
                self, stage=self.__dict__["_pump_delaystg"], name="pump_delay"
            )
        except Exception as expt:
            print("No eos delay stage")
            print(expt)

        # try:
        addMotorRecordToSelf(self, Id=self.Id + "-M521:MOTOR_1", name="delay_eos_stg")
        self.delay_eos = DelayTime(self.delay_eos_stg, name="delay_eos")
        self.alias.append(self.delay_eos.alias)
        # except Exception as expt:
        # print("Problems initializing eos delay stage")
        # print(expt)

        try:
            addMotorRecordToSelf(
                self, Id=self.Id + "-M522:MOTOR_1", name="delay_tt_stg"
            )
            self.delay_tt = DelayTime(self.delay_tt_stg, name="delay_tt")
            self.alias.append(self.delay_tt.alias)
        except:
            print("Problems initializing global delay stage")
        try:
            addMotorRecordToSelf(
                self, Id=self.Id + "-M523:MOTOR_1", name="delay_glob_stg"
            )
            self.delay_glob = DelayTime(self.delay_glob_stg, name="delay_glob")
            self.alias.append(self.delay_glob.alias)
        except:
            print("Problems initializing global delay stage")

        # Implementation of delay compensation, this assumes for now that delays_glob and delay_tt actually delay in positive directions.
        self.delay_lxtt = DelayCompensation(
            [self.delay_glob, self.delay_tt], [1, -1], name="delay_lxtt"
        )
        self.alias.append(self.delay_lxtt.alias)

        # compressor
        addMotorRecordToSelf(self, Id=self.Id + "-M532:MOT", name="compressor")
        # self.compressor = MotorRecord(Id+'-M532:MOT')

        # LAM delay stages
        addSmarActRecordToSelf(self, Id="SLAAR21-LMTS-LAM11", name="_lam_delay_smarstg")
        addDelayStageToSelf(
            self, self.__dict__["_lam_delay_smarstg"], name="lam_delay_smar"
        )
        # self._lam_delayStg_Smar = SmarActRecord('SLAAR21-LMTS-LAM11')
        # self.lam_delay_Smar = DelayStage(self._lam_delayStg_Smar)

        addMotorRecordToSelf(self, Id=self.Id + "-M548:MOT", name="_lam_delaystg")
        addDelayStageToSelf(self, self.__dict__["_lam_delaystg"], name="lam_delay")
        # self._lam_delayStg = MotorRecord(self.Id+'-M548:MOT')
        # self.lam_delay = DelayStage(self._lam_delayStg)

        # PALM delay stages
        addMotorRecordToSelf(self, Id=self.Id + "-M552:MOT", name="_palm_delaystg")
        addDelayStageToSelf(self, self.__dict__["_palm_delaystg"], name="palm_delay")
        # self._palm_delayStg = MotorRecord(self.Id+'-M552:MOT')
        # self.palm_delay = DelayStage(self._palm_delayStg)

        # PSEN delay stages
        # self._psen_delayStg = MotorRecord(self.Id+'')
        # self.psen_delay = DelayStage(self._pump_delayStg)

        # SmarAct ID
        ### Mirrors used in the experiment ###

        for smar_name, smar_address in self.smar_config.items():
            try:
                addSmarActRecordToSelf(
                    self, Id=(self.IdSA + smar_address), name=smar_name
                )
            except:
                print("Loading %s SmarAct motor in bernina laser conifg failed") % (
                    smar_name
                )
                pass

    def get_adjustable_positions_str(self):
        ostr = "*****Laser motor positions******\n"

        for tkey, item in sorted(self.__dict__.items()):
            if hasattr(item, "get_current_value"):
                pos = item.get_current_value()
                ostr += "  " + tkey.ljust(17) + " : % 14g\n" % pos
        return ostr

    def __repr__(self):
        return self.get_adjustable_positions_str()


class Laser_Exp_old:
    def __init__(self, Id=None, name=None, smar_config=None):
        self.Id = Id
        self.IdExp1 = "SARES20-EXP"
        self.IdSA = "SARES23"
        self.name = name
        self.alias = Alias(name)
        self.smar_config = smar_config

        # Waveplate and Delay stage
        try:
            addMotorRecordToSelf(self, self.Id + "-M534:MOT", name="pump_wp")
            addMotorRecordToSelf(self, self.Id + "-M533:MOT", name="tt_wp")
        except:
            print("No wp found")

        try:
            addMotorRecordToSelf(
                self, Id=self.Id + "-M521:MOTOR_1", name="_pump_delaystg"
            )
            addDelayStageToSelf(
                self, stage=self.__dict__["_pump_delaystg"], name="pump_delay"
            )
        except:
            print("No eos delay stage")
            pass
        try:
            addMotorRecordToSelf(
                self, Id=self.Id + "-M522:MOTOR_1", name="_tt_delaystg"
            )
            addDelayStageToSelf(self, self.__dict__["_tt_delaystg"], name="tt_delay")
            # addDelayStageToSelf(self,self.__dict__["_thz_delaystg"], name="thz_delay")
        except:
            print("No thz delay stage")
            pass

        try:
            addMotorRecordToSelf(self, Id=self.Id + "-M553:MOT", name="_exp_delaystg")
            addDelayStageToSelf(self, self.__dict__["_exp_delaystg"], name="exp_delay")
            # addDelayStageToSelf(self,self.__dict__["_thz_delaystg"], name="thz_delay")
        except:
            print("No thz delay stage")
            pass
        # compressor
        addMotorRecordToSelf(self, Id=self.Id + "-M532:MOT", name="compressor")
        # self.compressor = MotorRecord(Id+'-M532:MOT')

        # LAM delay stages
        addSmarActRecordToSelf(self, Id="SLAAR21-LMTS-LAM11", name="_lam_delay_smarstg")
        addDelayStageToSelf(
            self, self.__dict__["_lam_delay_smarstg"], name="lam_delay_smar"
        )
        # self._lam_delayStg_Smar = SmarActRecord('SLAAR21-LMTS-LAM11')
        # self.lam_delay_Smar = DelayStage(self._lam_delayStg_Smar)

        addMotorRecordToSelf(self, Id=self.Id + "-M548:MOT", name="_lam_delaystg")
        addDelayStageToSelf(self, self.__dict__["_lam_delaystg"], name="lam_delay")
        # self._lam_delayStg = MotorRecord(self.Id+'-M548:MOT')
        # self.lam_delay = DelayStage(self._lam_delayStg)

        # PALM delay stages
        addMotorRecordToSelf(self, Id=self.Id + "-M552:MOT", name="_palm_delaystg")
        addDelayStageToSelf(self, self.__dict__["_palm_delaystg"], name="palm_delay")
        # self._palm_delayStg = MotorRecord(self.Id+'-M552:MOT')
        # self.palm_delay = DelayStage(self._palm_delayStg)

        # PSEN delay stages
        # self._psen_delayStg = MotorRecord(self.Id+'')
        # self.psen_delay = DelayStage(self._pump_delayStg)

        # SmarAct ID
        ### Mirrors used in the experiment ###

        for smar_name, smar_address in self.smar_config.items():
            try:
                addSmarActRecordToSelf(
                    self, Id=(self.IdSA + smar_address), name=smar_name
                )
            except:
                print("Loading %s SmarAct motor in bernina laser conifg failed") % (
                    smar_name
                )
                pass

    def get_adjustable_positions_str(self):
        ostr = "*****Laser motor positions******\n"

        for tkey, item in sorted(self.__dict__.items()):
            if hasattr(item, "get_current_value"):
                pos = item.get_current_value()
                ostr += "  " + tkey.ljust(17) + " : % 14g\n" % pos
        return ostr

    def __repr__(self):
        return self.get_adjustable_positions_str()
