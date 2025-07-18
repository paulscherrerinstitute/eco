from importlib import import_module
import sys

from eco.endstations.bernina_sample_environments import (
    GrazingIncidenceLowTemperatureChamber,
    High_field_thz_chamber,
)
from eco.epics import get_from_archive

from eco.xoptics.slits import SlitBladesGeneral

sys.path.append("..")
from ..devices_general.motors import MotorRecord, MotorRecord
from ..elements.adjustable import AdjustableMemory, AdjustableVirtual
from ..epics.adjustable import AdjustablePv

from epics import PV
from ..aliases import Alias, append_object_to_object
from ..endstations.hexapod import HexapodPI
from pathlib import Path
import subprocess
from ..elements.assembly import Assembly
from ..detector.jungfrau import Jungfrau
from .kappa_conversion import kappa2you, you2kappa
import numpy as np
from ..utilities.recspace import Crystals, DiffGeometryYou


def addMotorRecordToSelf(self, name=None, Id=None):
    try:
        self.__dict__[name] = MotorRecord(Id, name=name)
        self.alias.append(self.__dict__[name].alias)
    except:
        print(f"Warning! Could not find motor {name} (Id:{Id})")


def append_diffractometer_modules(obj, configuration):
    if configuration.base():
        ### motors base platform ###
        obj._append(
            MotorRecord,
            obj.pvname + ":MOT_TX",
            name="xbase",
            is_setting=True,
            is_display=True,
            pb_conf={"type": "motor", "axis": 3},
        )
        obj._append(
            MotorRecord,
            obj.pvname + ":MOT_TY",
            name="_ybase_deltatau",
            is_setting=False,
            is_display=False,
            pb_conf={"type": "virtual", "axis": 9},
        )
        obj._append(
            MotorRecord,
            obj.pvname + ":MOT_RX",
            name="_rxbase_deltatau",
            is_setting=False,
            is_display=False,
            pb_conf={"type": "virtual", "axis": 10},
        )
        obj._append(
            MotorRecord,
            obj.pvname + ":MOT_YU",
            name="_ybase_upstream",
            is_setting=True,
            is_display=False,
            backlash_definition=True,
            pb_conf={"type": "motor", "axis": 1},
        )
        obj._append(
            MotorRecord,
            obj.pvname + ":MOT_YD",
            name="_ybase_downstream",
            is_setting=True,
            is_display=False,
            backlash_definition=True,
            pb_conf={"type": "motor", "axis": 2},
        )
        obj._append(
            AdjustableVirtual,
            [obj._ybase_upstream, obj._ybase_downstream],
            lambda u, d: np.mean([u, d]),
            lambda v: [
                i.get_current_value() + (v - obj.ybase.get_current_value())
                for i in [obj._ybase_upstream, obj._ybase_downstream]
            ],
            check_limits=True,
            name="ybase",
            is_setting=False,
            is_display=True,
            unit="mm",
        )
        obj._append(
            AdjustableVirtual,
            [obj._ybase_upstream, obj._ybase_downstream],
            lambda u, d: np.arctan(np.diff([d, u])[0] / 1146) * 180 / np.pi,
            lambda v: [
                obj.ybase.get_current_value() + i * np.tan(v * np.pi / 180) * 1146 / 2
                for i in [1, -1]
            ],
            check_limits=True,
            name="rxbase",
            is_setting=False,
            is_display=True,
            unit="deg",
        )

        obj._append(
            MotorRecord,
            obj.pvname + ":MOT_NY_RY2TH",
            name="gamma",
            is_setting=True,
            pb_conf={"type": "motor", "axis": 4},
        )

        obj._append(
            MotorRecord,
            obj.pvname + ":MOT_MY_RYTH",
            name="mu",
            is_setting=True,
            pb_conf={"type": "motor", "axis": 5},
        )
        obj.set_base_off = DeltaTauCurrOff("SARES22-GPS:asyn2.AOUT")

    if hasattr(configuration, "detector_flighttube"):
        if configuration.detector_flighttube():
            ### slit close to sample
            # up down according to You-B geometry
            obj._append(
                SlitBladesGeneral,
                def_blade_up={"args": [MotorRecord,obj.pvname + ":MOT_SLT_T_X2"], "kwargs": {'resolution_pars':True, 'backlash_definition':True}},
                def_blade_down={"args": [MotorRecord,obj.pvname + ":MOT_SLT_T_X1"], "kwargs": {'resolution_pars':True, 'backlash_definition':True}},
                def_blade_left={"args": [MotorRecord,obj.pvname + ":MOT_SLT_T_Y2"], "kwargs": {'resolution_pars':True, 'backlash_definition':True}},
                def_blade_right={"args": [MotorRecord,obj.pvname + ":MOT_SLT_T_Y1"], "kwargs": {'resolution_pars':True, 'backlash_definition':True}},
                name='slit_sam'
                )
            ### slit close to detector
            # up down according to You-B geometry
            obj._append(
                SlitBladesGeneral,
                def_blade_up={"args": [MotorRecord,obj.pvname + ":MOT_SLT_C_X2"], "kwargs": {'resolution_pars':True, 'backlash_definition':True}},
                def_blade_down={"args": [MotorRecord,obj.pvname + ":MOT_SLT_C_X1"], "kwargs": {'resolution_pars':True, 'backlash_definition':True}},
                def_blade_left={"args": [MotorRecord,obj.pvname + ":MOT_SLT_C_Y2"], "kwargs": {'resolution_pars':True, 'backlash_definition':True}},
                def_blade_right={"args": [MotorRecord,obj.pvname + ":MOT_SLT_C_Y1"], "kwargs": {'resolution_pars':True, 'backlash_definition':True}},
                name='slit_det'
                )
            
            # missing: slits of flight tube
            obj.set_det_slits_off = DeltaTauCurrOff("SARES21-XRD:asyn2.AOUT")

    if configuration.arm():
        obj._append(
            MotorRecord,
            obj.pvname + ":MOT_DT_RX2TH",
            name="delta",
            is_setting=True,
            is_display=True,
            pb_conf={"type": "motor", "axis": 1},
        )
        ### motors XRD area detector branch ###
        obj._append(
            MotorRecord,
            obj.pvname + ":MOT_D_T",
            name="tdet",
            is_setting=True,
            is_display=True,
            pb_conf={"type": "motor", "axis": 3},
        )

        ### motors XRD polarisation analyzer branch ###
        obj._append(
            MotorRecord,
            obj.pvname + ":MOT_P_T",
            name="tpol",
            is_setting=True,
            is_display=True,
            pb_conf={"type": "motor", "axis": 2},
        )
        # missing: slits of flight tube
        obj.set_detarm_off = DeltaTauCurrOff("SARES21-XRD:asyn3.AOUT")

    if configuration.polana():
        obj._append(
            MotorRecord,
            obj.pvname + ":MOT_P_ETA",
            name="pol",
            is_setting=True,
            is_display=True,
            pb_conf={"type": "motor", "axis": 4},
        )

        obj._append(
            MotorRecord,
            obj.pvname + ":MOT_P_TH",
            name="pthe",
            is_setting=True,
            is_display=True,
            pb_conf={"type": "motor", "axis": 5},
        )

        obj._append(
            MotorRecord,
            obj.pvname + ":MOT_P_T2TH",
            name="ptth",
            is_setting=True,
            is_display=True,
            pb_conf={"type": "motor", "axis": 6},
        )

    if configuration.phi_table():
        ### motors phi table ###
        obj._append(
            MotorRecord,
            obj.pvname + ":MOT_HEX_RX",
            name="eta",
            is_setting=True,
            pb_conf={"type": "motor", "axis": 1},  # 6
        )
        obj._append(
            MotorRecord,
            obj.pvname + ":MOT_HEX_TX",
            name="transl_eta",
            is_setting=True,
            pb_conf={"type": "motor", "axis": 4},  # 7
        )

    if configuration.phi_hex():
        ### motors PI hexapod ###
        if hasattr(obj, "fina_hex_angle_offset"):
            fina_hex_angle_offset = Path(obj.fina_hex_angle_offset).expanduser()

        else:
            fina_hex_angle_offset = None

        obj._append(
            HexapodPI,
            "SARES20-HEX_PI",
            name="hex",
            fina_angle_offset=fina_hex_angle_offset,
            is_setting=True,
            is_display="recursive",
        )

    if configuration.hlxz():
        ### motors heavy load goniometer ###
        obj._append(
            MotorRecord,
            obj.pvname + ":MOT_TBL_TX",
            name="xhl",
            is_setting=True,
            pb_conf={"type": "motor", "axis": 1},
        )
        obj._append(
            MotorRecord,
            obj.pvname + ":MOT_TBL_TZ",
            name="zhl",
            is_setting=True,
            pb_conf={"type": "motor", "axis": 2},
        )

    if configuration.hly():
        obj._append(
            MotorRecord,
            obj.pvname + ":MOT_TBL_TY",
            name="yhl",
            is_setting=True,
            pb_conf={"type": "motor", "axis": 3},
        )

    if configuration.hlrxrz():
        obj._append(
            MotorRecord,
            obj.pvname + ":MOT_TBL_RX",
            name="rxhl",
            is_setting=True,
            pb_conf={"type": "motor", "axis": 4},
        )
        obj._append(
            MotorRecord,
            obj.pvname + ":MOT_TBL_RZ",
            name="rzhl",
            is_setting=True,
            pb_conf={"type": "motor", "axis": 5},
        )
    obj.set_samplestg_off = DeltaTauCurrOff("SARES22-GPS:asyn1.AOUT")
    if configuration.kappa():
        obj._append(
            MotorRecord,
            obj.pvname + ":MOT_KAP_KRX",
            name="eta_kap",
            is_setting=True,
            is_display=True,
            pb_conf={"type": "motor", "axis": 1},
        )
        obj._append(
            MotorRecord,
            obj.pvname + ":MOT_KAP_KAP",
            name="kappa",
            is_setting=True,
            is_display=True,
            pb_conf={"type": "motor", "axis": 2},
        )
        obj._append(
            MotorRecord,
            obj.pvname + ":MOT_KAP_KPH",
            name="phi_kap",
            is_setting=True,
            is_display=True,
            pb_conf={"type": "motor", "axis": 3},
        )
        obj._append(
            MotorRecord,
            obj.pvname + ":MOT_KAP_DTY",
            name="zkap",
            is_setting=True,
            is_display=True,
            pb_conf={"type": "motor", "axis": 6},
        )
        obj._append(
            MotorRecord,
            obj.pvname + ":MOT_KAP_DTX",
            name="xkap",
            is_setting=True,
            is_display=True,
            pb_conf={"type": "motor", "axis": 4},
        )
        obj._append(
            MotorRecord,
            obj.pvname + ":MOT_KAP_DTZ",
            name="ykap",
            is_setting=True,
            is_display=True,
            pb_conf={"type": "motor", "axis": 5},
        )
        obj._append(
            MotorRecord,
            obj.pvname + ":MOT_KAP_DRX",
            name="rxkap",
            is_setting=True,
            is_display=True,
            pb_conf={"type": "motor", "axis": 7},
        )
        obj._append(
            MotorRecord,
            obj.pvname + ":MOT_KAP_DRZ",
            name="rykap",
            is_setting=True,
            is_display=True,
            pb_conf={"type": "motor", "axis": 8},
        )
        obj.set_kappa_off = DeltaTauCurrOff(obj.pvname + ":asyn1.AOUT")

        def get_current_kappa2you():
            return obj.calc_kappa2you(
                obj.eta_kap.get_current_value(),
                obj.kappa.get_current_value(),
                obj.phi_kap.get_current_value(),
            )

        def set_youvar_value_to_current_kappa(value, varind):
            vars = list(get_current_kappa2you())
            vars[varind] = value
            return obj.calc_you2kappa(*vars)

        obj._append(
            AdjustableVirtual,
            [obj.eta_kap, obj.kappa, obj.phi_kap],
            lambda eta_kap, kappa, phi_kap: obj.calc_kappa2you(eta_kap, kappa, phi_kap)[
                0
            ],
            lambda value_eta: set_youvar_value_to_current_kappa(value_eta, 0),
            check_limits=True,
            name="eta",
            unit="deg",
        )
        obj._append(
            AdjustableVirtual,
            [obj.eta_kap, obj.kappa, obj.phi_kap],
            lambda eta_kap, kappa, phi_kap: obj.calc_kappa2you(eta_kap, kappa, phi_kap)[
                1
            ],
            lambda value_chi: set_youvar_value_to_current_kappa(value_chi, 1),
            check_limits=True,
            name="chi",
            unit="deg",
        )
        obj._append(
            AdjustableVirtual,
            [obj.eta_kap, obj.kappa, obj.phi_kap],
            lambda eta_kap, kappa, phi_kap: obj.calc_kappa2you(eta_kap, kappa, phi_kap)[
                2
            ],
            lambda value_phi: set_youvar_value_to_current_kappa(value_phi, 2),
            check_limits=True,
            name="phi",
            unit="deg",
        )
    if configuration.robot():
        ### spherical robot motors ###
        import eco.bernina as b

        rob = b.__dict__["rob"]
        obj.gamma_robot = rob.spherical.gamma
        obj.delta_robot = rob.spherical.delta


@get_from_archive
class GPS(Assembly):
    def __init__(
        self,
        name=None,
        pvname=None,
        configuration=None,
        pgroup_adj=None,
        jf_config=None,
        fina_hex_angle_offset=None,
        recspace_conv="escape.swissfel.recspace_conv:SixCircleBernina",
        recspace_conv_JFID="JF01T03V01",
        xp = None,
        helium_control_valve = None,
        illumination_mpod = None, 
        thc_config = [],
    ):
        super().__init__(name=name)
        self.pvname = pvname
        self.configuration = configuration
        self.fina_hex_angle_offset = fina_hex_angle_offset

        append_diffractometer_modules(self, configuration)

        for jf_id, jf_name in configuration.jfs():
            self._append(
                Jungfrau,
                jf_id,
                pgroup_adj=pgroup_adj,
                config_adj=jf_config,
                name=jf_name,
            )

        if configuration.thc():
            self._append(
                High_field_thz_chamber,
                name="thc",
                illumination_mpod=illumination_mpod,
                configuration=thc_config,
                helium_control_valve = helium_control_valve,
                is_setting=False,
                is_display=True,
            )

        if configuration.gic():
            self._append(
                GrazingIncidenceLowTemperatureChamber,
                name="gic",
                xp = xp,
                helium_control_valve = helium_control_valve,
                is_setting=False,
                is_display=True,
            )
        if configuration.diffcalc():
            self._append(
                Crystals,
                diffractometer_you=self,
                name="diffcalc",
                is_setting=False,
                is_display=False,
            )

        if recspace_conv is not None:
            module_name, Conv_name = recspace_conv.split(":")
            Conv = getattr(import_module(module_name), Conv_name)
            self.recspace_conv = Conv(JF_ID=recspace_conv_JFID)
        else:
            self.recspace_conv = None

    def gui(self, guiType="xdm"):
        """Adjustable convention"""
        cmd = ["caqtdm", "-macro"]
        cmd += [
            "-noMsg",
            "-stylefile",
            "sfop.qss",
            "-macro",
            "P=SARES22-GPS",
            "/ioc/modules/qt/ESB_GPS_exp.ui",
        ]
        return self._run_cmd(" ".join(cmd))
        # bash -c 'caqtdm -noMsg  -stylefile sfop.qss -macro P=SARES22-GPS  /ioc/modules/qt/ESB_GPS_exp.ui'

    def calc_you2kappa(
        self,
        eta,
        chi,
        phi,
        kappa_angle=60,
        degrees=True,
        bernina_kappa=True,
        invert_elbow=False,
    ):
        """tool to convert from you definition angles to kappa angles, in
        particular the bernina kappa where the"""
        if bernina_kappa:
            eta = -eta
        if degrees:
            eta, chi, phi, kappa_angle = np.deg2rad([eta, chi, phi, kappa_angle])
        if invert_elbow:
            delta_angle = np.pi - np.arcsin(-np.tan(chi / 2) / np.tan(kappa_angle))
        else:
            delta_angle = np.arcsin(-np.tan(chi / 2) / np.tan(kappa_angle))
        eta_k = eta - delta_angle
        if invert_elbow:
            kappa = -2 * np.arcsin(np.sin(chi / 2) / np.sin(kappa_angle))
        else:
            kappa = 2 * np.arcsin(np.sin(chi / 2) / np.sin(kappa_angle))

        phi_k = phi - delta_angle

        if bernina_kappa:
            eta_k = eta_k - np.pi / 2
            kappa = -kappa
            phi_k = phi_k

        if True:

            def flip_ang(ang):
                if 1 < abs(ang // np.pi):
                    return ang - np.sign(ang) * abs(ang) // (2 * np.pi) * np.pi * 2
                else:
                    return ang

            # phi_k = flip_ang(phi_k)
            eta_k = flip_ang(eta_k)
            kappa = flip_ang(kappa)

        if degrees:
            eta_k, kappa, phi_k = np.rad2deg([eta_k, kappa, phi_k])
        return eta_k, kappa, phi_k

    def calc_kappa2you(
        self,
        eta_k,
        kappa,
        phi_k,
        kappa_angle=60,
        degrees=True,
        bernina_kappa=True,
        invert_elbow=False,
    ):
        if degrees:
            eta_k, kappa, phi_k, kappa_angle = np.deg2rad(
                [eta_k, kappa, phi_k, kappa_angle]
            )
        if bernina_kappa:
            eta_k = eta_k + np.pi / 2
            kappa = -kappa
            phi_k = phi_k
        if invert_elbow:
            kappa = -kappa
            delta_angle = np.pi - np.arctan(np.tan(kappa / 2) * np.cos(kappa_angle))
        else:
            delta_angle = np.arctan(np.tan(kappa / 2) * np.cos(kappa_angle))
        eta = eta_k - delta_angle
        chi = 2 * np.arcsin(np.sin(kappa / 2) * np.sin(kappa_angle))
        phi = phi_k - delta_angle
        if degrees:
            eta, chi, phi = np.rad2deg([eta, chi, phi])
        if bernina_kappa:
            eta = -eta
        return eta, chi, phi

    # def get_adjustable_positions_str(self):
    #     ostr = "*****GPS motor positions******\n"

    #     for tkey, item in self.__dict__.items():
    #         if hasattr(item, "get_current_value"):
    #             pos = item.get_current_value()
    #             ostr += "  " + tkey.ljust(17) + " : % 14g\n" % pos
    #     return ostr

    # def __repr__(self):
    #     return self.get_adjustable_positions_str()


class DeltaTauCurrOff:
    def __init__(self, pvname, name=None):
        self.pvname = pvname
        self.PV = PV(pvname)

    def set_off(self):
        self.PV.put("#1..8k")

    def __call__(self):
        self.set_off()


class XRDYou(Assembly):
    def __init__(
        self,
        name=None,
        Id=None,
        configuration=None,
        invert_kappa_ellbow=True,
        pgroup_adj=None,
        jf_config=None,
        fina_hex_angle_offset=None,
    ):
        """X-ray diffractometer platform in SiwssFEL Bernina.\
                <configuration> : list of elements mounted on 
                the plaform, options are kappa, nutable, hlgonio, polana"""
        # self.Id = Id
        self.pvname = Id
        pvname = Id
        super().__init__(name=name)
        self.configuration = configuration
        self.invert_kappa_ellbow = invert_kappa_ellbow
        self.fina_hex_angle_offset = fina_hex_angle_offset

        append_diffractometer_modules(self, configuration)

        if configuration.diffcalc():
            self._append(
                Crystals,
                diffractometer_you=self,
                name="diffcalc",
                is_setting=False,
                is_display=False,
            )
        for jf_id, jf_name in configuration.jfs():
            self._append(
                Jungfrau,
                jf_id,
                pgroup_adj=pgroup_adj,
                config_adj=jf_config,
                name=jf_name,
            )

    def get_adjustable_positions_str(self):
        ostr = "*****XRD motor positions******\n"

        for tkey, item in self.__dict__.items():
            if hasattr(item, "get_current_value"):
                pos = item.get_current_value()
                ostr += "  " + tkey.ljust(17) + " : % 14g\n" % pos
        return ostr

    def gui(self, guiType="xdm"):
        """Adjustable convention"""
        cmd = ["caqtdm", "-macro"]
        cmd += [
            "-noMsg",
            "-stylefile",
            "sfop.qss",
            "-macro",
            "P=SARES21-XRD",
            "ESB_XRD_exp.ui",
        ]
        return self._run_cmd(" ".join(cmd))

    # def calc_kappa2you(self, eta_k, kappa, phi_k):
    #     return kappa2you(eta_k, kappa, phi_k)

    # def calc_you2kappa(self, eta, chi, phi):
    #     return you2kappa(eta, chi, phi)
    #################

    def calc_you2kappa(
        self,
        eta,
        chi,
        phi,
        kappa_angle=60,
        degrees=True,
        bernina_kappa=True,
        invert_elbow=None,
    ):
        """tool to convert from you definition angles to kappa angles, in
        particular the bernina kappa where the"""
        if invert_elbow is None:
            invert_elbow = self.invert_kappa_ellbow
        if bernina_kappa:
            eta = -eta
            phi = -phi
        if degrees:
            eta, chi, phi, kappa_angle = np.deg2rad([eta, chi, phi, kappa_angle])
        if invert_elbow:
            delta_angle = np.pi - np.arcsin(-np.tan(chi / 2) / np.tan(kappa_angle))
        else:
            delta_angle = np.arcsin(-np.tan(chi / 2) / np.tan(kappa_angle))
        eta_k = eta - delta_angle
        if invert_elbow:
            kappa = -2 * np.arcsin(np.sin(chi / 2) / np.sin(kappa_angle))
        else:
            kappa = 2 * np.arcsin(np.sin(chi / 2) / np.sin(kappa_angle))

        phi_k = phi - delta_angle

        if bernina_kappa:
            eta_k = eta_k - np.pi / 2
            kappa = -kappa
        if True:

            def flip_ang(ang):
                if 2 <= abs(ang // np.pi):
                    return ang - np.sign(ang) * np.pi * 2
                else:
                    return ang

            phi_k = flip_ang(phi_k)
            # phi_k = phi_k + np.pi * 2
            eta_k = flip_ang(eta_k)
            kappa = flip_ang(kappa)
        if degrees:
            eta_k, kappa, phi_k = np.rad2deg([eta_k, kappa, phi_k])
        return eta_k, kappa, phi_k

    def calc_kappa2you(
        self,
        eta_k,
        kappa,
        phi_k,
        kappa_angle=60,
        degrees=True,
        bernina_kappa=True,
        invert_elbow=None,
    ):
        if invert_elbow is None:
            invert_elbow = self.invert_kappa_ellbow
        if degrees:
            eta_k, kappa, phi_k, kappa_angle = np.deg2rad(
                [eta_k, kappa, phi_k, kappa_angle]
            )
        if bernina_kappa:
            eta_k = eta_k + np.pi / 2
            kappa = -kappa
            # phi_k = -phi_k
        if invert_elbow:
            kappa = -kappa
            delta_angle = np.pi - np.arctan(np.tan(kappa / 2) * np.cos(kappa_angle))
        else:
            delta_angle = np.arctan(np.tan(kappa / 2) * np.cos(kappa_angle))
        eta = eta_k - delta_angle
        chi = 2 * np.arcsin(np.sin(kappa / 2) * np.sin(kappa_angle))
        phi = phi_k - delta_angle
        if degrees:
            eta, chi, phi = np.rad2deg([eta, chi, phi])
        if bernina_kappa:
            eta = -eta
            phi = -phi
        return eta, chi, phi


#################
# def calc_you2kappa(
#     self, eta, chi, phi, kappa_angle=60, degrees=True, bernina_kappa=True
# ):
#     """tool to convert from you definition angles to kappa angles, in
#     particular the bernina kappa where the"""
#     if bernina_kappa:
#         eta = -eta
#     if degrees:
#         eta, chi, phi, kappa_angle = np.deg2rad([eta, chi, phi, kappa_angle])
#     delta_angle = np.arcsin(-np.tan(chi / 2) / np.tan(kappa_angle))
#     eta_k = eta - delta_angle
#     kappa = 2 * np.arcsin(np.sin(chi / 2) / np.sin(kappa_angle))
#     phi_k = phi - delta_angle
#
#     if bernina_kappa:
#         eta_k = eta_k - np.pi / 2
#         kappa = -kappa
#         phi_k = phi_k
#     if degrees:
#         eta_k, kappa, phi_k = np.rad2deg([eta_k, kappa, phi_k])
#     return eta_k, kappa, phi_k
#
# def calc_kappa2you(
#     self, eta_k, kappa, phi_k, kappa_angle=60, degrees=True, bernina_kappa=True
# ):
#     if degrees:
#         eta_k, kappa, phi_k, kappa_angle = np.deg2rad(
#             [eta_k, kappa, phi_k, kappa_angle]
#         )
#     if bernina_kappa:
#         eta_k = eta_k + np.pi / 2
#         kappa = -kappa
#         phi_k = phi_k
#     delta_angle = np.arctan(np.tan(kappa / 2) * np.cos(kappa_angle))
#     eta = eta_k - delta_angle
#     chi = 2 * np.arcsin(np.sin(kappa / 2) * np.sin(kappa_angle))
#     phi = phi_k - delta_angle
#     if degrees:
#         eta, chi, phi = np.rad2deg([eta, chi, phi])
#     if bernina_kappa:
#         eta = -eta
#     return eta, chi, phi
#
# # def __repr__(self):
# #     return self.get_adjustable_positions_str()


class XRD(Assembly):
    def __init__(
        self,
        name=None,
        Id=None,
        configuration=["base"],
        diff_detector=None,
        pgroup_adj=None,
    ):
        """X-ray diffractometer platform in AiwssFEL Bernina.\
                <configuration> : list of elements mounted on 
                the plaform, options are kappa, nutable, hlgonio, polana,"""
        # self.Id = Id
        super().__init__(name=name)
        self.configuration = configuration

        if "base" in self.configuration:
            ### motors base platform ###

            self._append(
                MotorRecord,
                pvname + ":MOT_TX",
                name="xbase",
                is_setting=True,
                is_display=True,
            )
            self._append(
                MotorRecord,
                pvname + ":MOT_TY",
                name="_ybase_deltatau",
                is_setting=False,
                is_display=False,
            )
            self._append(
                MotorRecord,
                pvname + ":MOT_RX",
                name="_rxbase_deltatau",
                is_setting=False,
                is_display=False,
            )
            self._append(
                MotorRecord,
                pvname + ":MOT_YU",
                name="_ybase_upstream",
                is_setting=True,
                is_display=False,
                backlash_definition=True,
            )
            self._append(
                MotorRecord,
                pvname + ":MOT_YD",
                name="_ybase_downstream",
                is_setting=True,
                is_display=False,
                backlash_definition=True,
            )
            self._append(
                AdjustableVirtual,
                [self._ybase_upstream, self._ybase_downstream],
                lambda u, d: np.mean([u, d]),
                lambda v: [
                    i.get_current_value() + (v - self.ybase.get_current_value())
                    for i in [self._ybase_upstream, self._ybase_downstream]
                ],
                name="ybase",
                is_setting=False,
                is_display=True,
                unit="mm",
            )
            self._append(
                AdjustableVirtual,
                [self._ybase_upstream, self._ybase_downstream],
                lambda u, d: np.arctan(np.diff([d, u])[0] / 1146) * 180 / np.pi,
                lambda v: [
                    self.ybase.get_current_value()
                    + i * np.tan(v * np.pi / 180) * 1146 / 2
                    for i in [1, -1]
                ],
                name="rxbase",
                is_setting=False,
                is_display=True,
                unit="deg",
            )

            self._append(
                MotorRecord, Id + ":MOT_MY_RYTH", name="alpha", is_setting=True
            )
            self.set_base_off = DeltaTauCurrOff("SARES21-XRD:asyn4.AOUT")

        if "arm" in self.configuration:
            ### motors XRD detector arm ###
            self._append(
                MotorRecord, Id + ":MOT_NY_RY2TH", name="gamma", is_setting=True
            )
            self._append(
                MotorRecord, Id + ":MOT_DT_RX2TH", name="delta", is_setting=True
            )
            ### motors XRD area detector branch ###
            self._append(MotorRecord, Id + ":MOT_D_T", name="tdet", is_setting=True)

            ### motors XRD polarisation analyzer branch ###
            self._append(MotorRecord, Id + ":MOT_P_T", name="tpol", is_setting=True)
            # missing: slits of flight tube
            self.set_detarm_off = DeltaTauCurrOff("SARES21-XRD:asyn3.AOUT")

        if "hlxz" in self.configuration:
            ### motors heavy load goniometer ###
            self._append(MotorRecord, Id + ":MOT_TBL_TX", name="xhl", is_setting=True)
            self._append(MotorRecord, Id + ":MOT_TBL_TZ", name="zhl", is_setting=True)
            self.set_phi_off = DeltaTauCurrOff("SARES21-XRD:asyn1.AOUT")
        if "hly" in self.configuration:
            self._append(MotorRecord, Id + ":MOT_TBL_TY", name="yhl", is_setting=True)
            self.set_phi_off = DeltaTauCurrOff("SARES21-XRD:asyn1.AOUT")

        if "hlrxrz" in self.configuration:
            try:
                self._append(
                    MotorRecord, Id + ":MOT_TBL_RX", name="rxhl", is_setting=True
                )
            except:
                print("XRD.rxhl not found")
                pass
            try:
                self._append(
                    MotorRecord, Id + ":MOT_TBL_RY", name="rzhl", is_setting=True
                )
            except:
                print("XRD.rzhl not found")
            self.set_phi_off = DeltaTauCurrOff("SARES21-XRD:asyn1.AOUT")

        if "phi_table" in self.configuration:
            ### motors nu table ###
            self._append(MotorRecord, Id + ":MOT_HEX_TX", name="tphi", is_setting=True)
            self._append(MotorRecord, Id + ":MOT_HEX_RX", name="phi", is_setting=True)

        if "phi_hex" in self.configuration:
            ### motors PI hexapod ###
            append_object_to_object(
                self,
                AdjustablePv,
                "SARES20-HEX_PI:SET-POSI-X",
                pvreadbackname="SARES20-HEX_PI:POSI-X",
                name="xhex",
            )
            append_object_to_object(
                self,
                AdjustablePv,
                "SARES20-HEX_PI:SET-POSI-Y",
                pvreadbackname="SARES20-HEX_PI:POSI-Y",
                name="yhex",
            )
            append_object_to_object(
                self,
                AdjustablePv,
                "SARES20-HEX_PI:SET-POSI-Z",
                pvreadbackname="SARES20-HEX_PI:POSI-Z",
                name="zhex",
            )
            append_object_to_object(
                self,
                AdjustablePv,
                "SARES20-HEX_PI:SET-POSI-U",
                pvreadbackname="SARES20-HEX_PI:POSI-U",
                name="uhex",
            )
            append_object_to_object(
                self,
                AdjustablePv,
                "SARES20-HEX_PI:SET-POSI-V",
                pvreadbackname="SARES20-HEX_PI:POSI-V",
                name="vhex",
            )
            append_object_to_object(
                self,
                AdjustablePv,
                "SARES20-HEX_PI:SET-POSI-W",
                pvreadbackname="SARES20-HEX_PI:POSI-W",
                name="whex",
            )

        if "kappa" in self.configuration:
            self._append(
                MotorRecord, "SARES21-XRD:MOT_KAP_KRX", name="eta", is_setting=True
            )
            self._append(
                MotorRecord,
                "SARES21-XRD:MOT_KAP_KAP",
                name="kappa",
                is_setting=True,
            )
            self._append(
                MotorRecord, "SARES21-XRD:MOT_KAP_KPH", name="phi", is_setting=True
            )
            self._append(
                MotorRecord, "SARES21-XRD:MOT_KAP_DTY", name="zkap", is_setting=True
            )
            self._append(
                MotorRecord, "SARES21-XRD:MOT_KAP_DTX", name="xkap", is_setting=True
            )
            self._append(
                MotorRecord, "SARES21-XRD:MOT_KAP_DTZ", name="ykap", is_setting=True
            )
            self._append(
                MotorRecord,
                "SARES21-XRD:MOT_KAP_DRX",
                name="rxkap",
                is_setting=True,
            )
            self._append(
                MotorRecord,
                "SARES21-XRD:MOT_KAP_DRZ",
                name="rykap",
                is_setting=True,
            )
            self.set_kappa_off = DeltaTauCurrOff("SARES21-XRD:asyn1.AOUT")

        if diff_detector:
            self._append(
                Jungfrau,
                diff_detector["jf_id"],
                name="det_diff",
                is_setting=False,
                is_display=True,
                pgroup_adj=pgroup_adj,
                view_toplevel_only=True,
            )

    def get_adjustable_positions_str(self):
        ostr = "*****XRD motor positions******\n"

        for tkey, item in self.__dict__.items():
            if hasattr(item, "get_current_value"):
                pos = item.get_current_value()
                ostr += "  " + tkey.ljust(17) + " : % 14g\n" % pos
        return ostr

    def gui(self, guiType="xdm"):
        """Adjustable convention"""
        cmd = ["caqtdm", "-macro"]
        cmd += [
            "-noMsg",
            "-stylefile",
            "sfop.qss",
            "-macro",
            "P=SARES21-XRD",
            "ESB_XRD_exp.ui",
        ]
        return self._run_cmd(" ".join(cmd))

    def calc_kappa2you(self, eta_k, kappa, phi_k):
        return kappa2you(eta_k, kappa, phi_k)

    def calc_you2kappa(self, eta, chi, phi):
        return you2kappa(eta, chi, phi)

    # def __repr__(self):
    #     return self.get_adjustable_positions_str()


class XRD_old:
    def __init__(self, name=None, Id=None, configuration=["base"]):
        """X-ray diffractometer platform in AiwssFEL Bernina.\
                <configuration> : list of elements mounted on 
                the plaform, options are kappa, nutable, hlgonio, polana"""
        self.Id = Id
        self.name = name
        self.alias = Alias(name)
        self.configuration = configuration

        if "base" in self.configuration:
            ### motors base platform ###
            ### motors base platform ###
            addMotorRecordToSelf(self, Id=Id + ":MOT_TX", name="xbase")
            addMotorRecordToSelf(self, Id=Id + ":MOT_TY", name="ybase")
            addMotorRecordToSelf(self, Id=Id + ":MOT_RX", name="rxbase")
            addMotorRecordToSelf(self, Id=Id + ":MOT_MY_RYTH", name="alpha")

        if "arm" in self.configuration:
            ### motors XRD detector arm ###
            addMotorRecordToSelf(self, Id=Id + ":MOT_NY_RY2TH", name="gamma")
            addMotorRecordToSelf(self, Id=Id + ":MOT_DT_RX2TH", name="delta")
            ### motors XRD area detector branch ###
            addMotorRecordToSelf(self, Id=Id + ":MOT_D_T", name="tdet")

            ### motors XRD polarisation analyzer branch ###
            addMotorRecordToSelf(self, Id=Id + ":MOT_P_T", name="tpol")
            # missing: slits of flight tube

        if "hlxz" in self.configuration:
            ### motors heavy load goniometer ###
            addMotorRecordToSelf(self, Id=Id + ":MOT_TBL_TX", name="xhl")
            addMotorRecordToSelf(self, Id=Id + ":MOT_TBL_TZ", name="zhl")
        if "hly" in self.configuration:
            addMotorRecordToSelf(self, Id=Id + ":MOT_TBL_TY", name="yhl")

        if "hlrxrz" in self.configuration:
            try:
                addMotorRecordToSelf(self, Id=Id + ":MOT_TBL_RX", name="rxhl")
            except:
                print("XRD.rxhl not found")
                pass
            try:
                addMotorRecordToSelf(self, Id=Id + ":MOT_TBL_RY", name="rzhl")
            except:
                print("XRD.rzhl not found")
                pass

        if "phi_table" in self.configuration:
            ### motors nu table ###
            addMotorRecordToSelf(self, Id=Id + ":MOT_HEX_TX", name="tphi")
            addMotorRecordToSelf(self, Id=Id + ":MOT_HEX_RX", name="phi")

        if "phi_hex" in self.configuration:
            ### motors PI hexapod ###
            append_object_to_object(
                self,
                AdjustablePv,
                "SARES20-HEX_PI:SET-POSI-X",
                pvreadbackname="SARES20-HEX_PI:POSI-X",
                name="xhex",
            )
            append_object_to_object(
                self,
                AdjustablePv,
                "SARES20-HEX_PI:SET-POSI-Y",
                pvreadbackname="SARES20-HEX_PI:POSI-Y",
                name="yhex",
            )
            append_object_to_object(
                self,
                AdjustablePv,
                "SARES20-HEX_PI:SET-POSI-Z",
                pvreadbackname="SARES20-HEX_PI:POSI-Z",
                name="zhex",
            )
            append_object_to_object(
                self,
                AdjustablePv,
                "SARES20-HEX_PI:SET-POSI-U",
                pvreadbackname="SARES20-HEX_PI:POSI-U",
                name="uhex",
            )
            append_object_to_object(
                self,
                AdjustablePv,
                "SARES20-HEX_PI:SET-POSI-V",
                pvreadbackname="SARES20-HEX_PI:POSI-V",
                name="vhex",
            )
            append_object_to_object(
                self,
                AdjustablePv,
                "SARES20-HEX_PI:SET-POSI-W",
                pvreadbackname="SARES20-HEX_PI:POSI-W",
                name="whex",
            )

        if "kappa" in self.configuration:
            append_object_to_object(
                self, MotorRecord, "SARES21-XRD:MOT_KAP_KRX", name="eta"
            )
            append_object_to_object(
                self, MotorRecord, "SARES21-XRD:MOT_KAP_KAP", name="kappa"
            )
            append_object_to_object(
                self, MotorRecord, "SARES21-XRD:MOT_KAP_KPH", name="phi"
            )
            append_object_to_object(
                self, MotorRecord, "SARES21-XRD:MOT_KAP_DTY", name="zkap"
            )
            append_object_to_object(
                self, MotorRecord, "SARES21-XRD:MOT_KAP_DTX", name="xkap"
            )
            append_object_to_object(
                self, MotorRecord, "SARES21-XRD:MOT_KAP_DTZ", name="ykap"
            )
            append_object_to_object(
                self, MotorRecord, "SARES21-XRD:MOT_KAP_DRX", name="rxkap"
            )
            append_object_to_object(
                self, MotorRecord, "SARES21-XRD:MOT_KAP_DRZ", name="rykap"
            )

    def get_adjustable_positions_str(self):
        ostr = "*****XRD motor positions******\n"

        for tkey, item in self.__dict__.items():
            if hasattr(item, "get_current_value"):
                pos = item.get_current_value()
                ostr += "  " + tkey.ljust(17) + " : % 14g\n" % pos
        return ostr

    def gui(self, guiType="xdm"):
        """Adjustable convention"""
        cmd = ["caqtdm", "-macro"]
        cmd = [
            "-noMsg",
            "-stylefile",
            "sfop.qss",
            "-macro",
            "P=SARES21-XRD",
            "/sf/common/config/qt/ESB_XRD_exp.ui",
        ]
        return subprocess.Popen(" ".join(cmd), shell=True)

    def __repr__(self):
        return self.get_adjustable_positions_str()
