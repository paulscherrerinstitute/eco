# # New configuration of components:
# components is an ordered list of
# - name in parent package
# - type, describing the python Class or factory function.
# - arguments of that type args
# - kwargs of that type

# # Conventions for the type
# the call of type will try to pass a kwarg 'name' with the
# name of the component, before only calling args and kwargs.
# if arg or kwarg is of type eco.utilities.Component (dummy class)
# this indicates that an earlier initialized object is used
# (e.g. from same configuration).
from ..utilities.config import (
    Component,
    init_device,
    initFromConfigList,
    Configuration,
)

_eco_lazy_init = False

config = Configuration(
    "/sf/bernina/config/eco/bernina_config_eco.json", name="bernina_config"
)

components = [
    # {
    #     "type": "eco.utilities.config:append_to_path",
    #     "args": config["path_exp"],
    #     "name": "path_exp",
    #     "kwargs": {},
    #     "lazy": True,
    # },
    # {
    #     "name": "screenshot",
    #     "type": "eco.utilities.elog:Screenshot",
    #     "args": [],
    #     "kwargs": {"screenshot_directory": "/sf/bernina/config/screenshots"},
    # },
    #    {
    #        "name": "fel",
    #        "type": "eco.fel.swissfel:SwissFel",
    #        "args": [],
    #        "kwargs": {},
    #        "desc": "Fel related control and feedback",
    #    },
    #    {
    #        "name": "mono",
    #        "args": ["SAROP21-ODCM098"],
    #        "kwargs": {},
    #        "z_und": 98,
    #        "desc": "DCM Monochromator",
    #        "type": "eco.xoptics.dcm_new:DoubleCrystalMono",
    #    },
    # {
    # "name": "slit_und",
    # "type": "eco.xoptics.slits:SlitFourBlades_old",
    # "args": ["SARFE10-OAPU044"],
    # "kwargs": {},
    # "desc": "Slit after Undulator",
    # },
    # {
    #     "name": "slit_und_epics",
    #     "type": "eco.xoptics.slits:SlitFourBlades_old",
    #     "args": ["SARFE10-OAPU044"],
    #     "kwargs": {},
    #     "desc": "Slit after Undulator",
    # },
    # {
    # "name": "mon_und",
    # "args": ["SARFE10-PBPS053"],
    # "z_und": 53,
    # "desc": "Intensity/Position monitor after Undolator",
    # "type": "eco.xdiagnostics.intensity_monitors:SolidTargetDetectorPBPS",
    # "kwargs": {"VME_crate": "SAROP21-CVME-PBPS2", "link": 9},
    # },
    # {
    #     "name": "mon_und",
    #     "z_und": 53,
    #     "desc": "Intensity/position monitor after Undulator",
    #     "type": "eco.xdiagnostics.intensity_monitors:SolidTargetDetectorPBPS_new",
    #     "args": ["SARFE10-PBPS053"],
    #     "kwargs": {
    #         "VME_crate": "SAROP21-CVME-PBPS1",
    #         "link": 9,
    #         "channels": {
    #             "up": "SLAAR21-LSCP1-FNS:CH6:VAL_GET",
    #             "down": "SLAAR21-LSCP1-FNS:CH7:VAL_GET",
    #             "left": "SLAAR21-LSCP1-FNS:CH4:VAL_GET",
    #             "right": "SLAAR21-LSCP1-FNS:CH5:VAL_GET",
    #         },
    #         "calc": {
    #             "itot": "SLAAR21-LTIM01-EVR0:CALCI",
    #             "xpos": "SLAAR21-LTIM01-EVR0:CALCX",
    #             "ypos": "SLAAR21-LTIM01-EVR0:CALCY",
    #         },
    #     },
    # },
    # {
    #     "name": "pshut_und",
    #     "type": "eco.xoptics.shutters:PhotonShutter",
    #     "args": ["SARFE10-OPSH044:REQUEST"],
    #     "kwargs": {},
    #     "z_und": 44,
    #     "desc": "First shutter after Undulators",
    # },
    # {
    #     "name": "pshut_fe",
    #     "type": "eco.xoptics.shutters:PhotonShutter",
    #     "args": ["SARFE10-OPSH059:REQUEST"],
    #     "kwargs": {},
    #     "z_und": 59,
    #     "desc": "Photon shutter end of front end",
    # },
    # {
    #     "name": "sshut_opt",
    #     "type": "eco.xoptics.shutters:SafetyShutter",
    #     "args": ["SGE01-EPKT822:BST1_oeffnen"],
    #     "kwargs": {},
    #     "z_und": 115,
    #     "desc": "Bernina safety shutter",
    # },
    # {
    #     "name": "sshut_fe",
    #     "type": "eco.xoptics.shutters:SafetyShutter",
    #     "args": ["SGE01-EPKT820:BST1_oeffnen"],
    #     "kwargs": {},
    #     "z_und": 115,
    #     "desc": "Bernina safety shutter",
    # },
    # {
    #     "name": "att_fe",
    #     "type": "eco.xoptics.attenuator_aramis:AttenuatorAramis",
    #     "args": ["SARFE10-OATT053"],
    #     "kwargs": {"shutter": Component("pshut_und")},
    #     "z_und": 53,
    #     "desc": "Attenuator in Front End",
    # },
    # {
    #    "name": "mon_und",
    #    "z_und": 53,
    #    "desc": "Intensity/position monitor after Optics hutch",
    #    "type": "eco.xdiagnostics.intensity_monitors:SolidTargetDetectorPBPS",
    #    "args": ["SARFE10-PBPS053"],
    #    "kwargs": {},
    # },
    # {
    #     "name": "xspect",
    #     "z_und": 53,
    #     "desc": "X-ray single shot spectrometer",
    #     "type": "eco.xdiagnostics.xspect:Xspect",
    #     "args": [],
    #     "kwargs": {},
    # },
    # {
    #     "name": "mono_old",
    #     "args": ["SAROP21-ODCM098"],
    #     "kwargs": {
    #         "energy_sp": "SAROP21-ARAMIS:ENERGY_SP",
    #         "energy_rb": "SAROP21-ARAMIS:ENERGY",
    #     },
    #     "z_und": 98,
    #     "desc": "DCM Monochromator",
    #     "type": "eco.xoptics.dcm:Double_Crystal_Mono",
    # },
    # {
    #     "name": "xp",
    #     "args": [],
    #     "kwargs": {
    #         "Id": "SAROP21-OPPI113",
    #         "evronoff": "SGE-CPCW-72-EVR0:FrontUnivOut15-Ena-SP",
    #         "evrsrc": "SGE-CPCW-72-EVR0:FrontUnivOut15-Src-SP",
    #     },
    #     "z_und": 103,
    #     "desc": "X-ray pulse picker",
    #     "type": "eco.xoptics.pp:Pulsepick",
    # },
    # {
    #    "name": "mon_opt_old",
    #    "z_und": 133,
    #    "desc": "Intensity/position monitor after Optics hutch",
    #    "type": "eco.xdiagnostics.intensity_monitors:SolidTargetDetectorPBPS",
    #    "args": ["SAROP21-PBPS133"],
    #    "kwargs": {"VME_crate": "SAROP21-CVME-PBPS1", "link": 9},
    # },
    # {
    #     "name": "att",
    #     "args": ["SAROP21-OATT135"],
    #     "kwargs": {"shutter": Component("xp"), "set_limits": []},
    #     "z_und": 135,
    #     "desc": "Attenuator Bernina",
    #     "type": "eco.xoptics.attenuator_aramis:AttenuatorAramis",
    # },
    # {
    #     "name": "slit_att",
    #     "args": ["SAROP21-OAPU136"],
    #     "kwargs": {},
    #     "z_und": 136,
    #     "desc": "Slits behind attenuator",
    #     "type": "eco.xoptics.slits:SlitPosWidth",
    # },
    # {
    #     "name": "det_dio",
    #     "args": ["SAROP21-PDIO138"],
    #     "z_und": 138,
    #     "desc": "Diode digitizer for exp data",
    #     "type": "eco.devices_general.detectors:DiodeDigitizer",
    #     "kwargs": {"VME_crate": "SAROP21-CVME-PBPS2", "link": 9},
    # },
    # {
    # "name": "spatial_tt",
    # "args": [],
    # "kwargs": {"reduction_client_address": "http://sf-daqsync-02:12003/"},
    # "z_und": 141,
    # "desc": "spatial encoding timing diagnostics before sample.",
    # "type": "eco.xdiagnostics.timetools:SpatialEncoder",
    # "lazy": True,
    # },
    # {
    # "name": "slit_kb",
    # "args": [],
    # "kwargs": {"pvname": "SARES20-MF1"},
    # "z_und": 141,
    # "desc": "Slits behind Kb",
    # "type": "eco.xoptics.slits:SlitBlades_JJ",
    # # "type": "eco.xoptics.slits:SlitBladesJJ_old",
    # },
    # {
    #     "args": [],
    #     "name": "gps_old",
    #     "z_und": 142,
    #     "desc": "General purpose station",
    #     "type": "eco.endstations.bernina_diffractometers:GPS_old",
    #     "kwargs": {
    #         "Id": "SARES22-GPS",
    #         "configuration": config["gps_config"],
    #         "fina_hex_angle_offset": "/sf/bernina/config/eco/reference_values/hex_pi_angle_offset.json",
    #     },
    #     "lazy": True,
    # },
    # {
    #     "args": [],
    #     "name": "xrd_old",
    #     "z_und": 142,
    #     "desc": "Xray diffractometer",
    #     "type": "eco.endstations.bernina_diffractometers:XRD_old",
    #     "kwargs": {"Id": "SARES21-XRD", "configuration": config["xrd_config"]},
    # },
    # {
    # "args": [],
    # "name": "xrd",
    # "z_und": 142,
    # "desc": "Xray diffractometer",
    # "type": "eco.endstations.bernina_diffractometers:XRD",
    # "kwargs": {
    # "Id": "SARES21-XRD",
    # "configuration": config["xrd_config"],
    # "diff_detector": {"jf_id": "JF01T03V01"},
    # },
    # },
    # {
    #     "args": [],
    #     "name": "gasjet",
    #     "z_und": 142,
    #     "desc": "ToF comm. gasjet",
    #     "type": "tof:jet",
    #     "kwargs": {},
    # },
    # {
    #     "args": [],
    #     "name": "xeye",
    #     "z_und": 142,
    #     "desc": "Mobile X-ray eye in Bernina hutch",
    #     "type": "eco.xdiagnostics.profile_monitors:Bernina_XEYE",
    #     "kwargs": {
    #         "zoomstage_pv": config["xeye"]["zoomstage_pv"],
    #         "camera_pv": config["xeye"]["camera_pv"],
    #         "bshost": "sf-daqsync-01.psi.ch",
    #         "bsport": 11151,
    #     },
    # },
    # {
    #    "args": ["SARES20-CAMS142-C3"],
    #    "name": "cam_sample_xrd",
    #    "z_und": 142,
    #    "desc": "",
    #    "type": "eco.devices_general.cameras_swissfel:CameraBasler",
    #    "kwargs": {},
    # },
    # {
    # "args": [],
    # "name": "cams_qioptiq",
    # "z_und": 142,
    # "desc": "Qioptic sample viewer in Bernina hutch",
    # "type": "eco.endstations.bernina_cameras:Qioptiq",
    # "kwargs": {
    # "bshost": "sf-daqsync-01.psi.ch",
    # "bsport": 11149,
    # "zoomstage_pv": config["cams_qioptiq"]["zoomstage_pv"],
    # "camera_pv": config["cams_qioptiq"]["camera_pv"],
    # },
    # },
    # {
    #     "args": ["SLAAR02-TSPL-EPL"],
    #     "name": "phase_shifter",
    #     "z_und": 142,
    #     "desc": "Experiment laser phase shifter",
    #     "type": "eco.devices_general.timing:PhaseShifterAramis",
    #     "kwargs": {},
    # },
    # {
    #     "args": ["SLAAR21-LTIM01-EVR0"],
    #     "name": "laser_shutter",
    #     "z_und": 142,
    #     "desc": "Laser Shutter",
    #     "type": "eco.loptics.laser_shutter:laser_shutter",
    #     "kwargs": {},
    # },
    # {
    #     "args": [],
    #     "name": "daq_dia_old",
    #     "desc": "server based acquisition",
    #     "type": "eco.acquisition.dia:DIAClient",
    #     "kwargs": {
    #         "instrument": "bernina",
    #         "api_address": config["daq_address"],
    #         "pgroup": config["pgroup"],
    #         "pedestal_directory": config["jf_pedestal_directory"],
    #         "gain_path": config["jf_gain_path"],
    #         "config_default": config["daq_dia_config"],
    #         "jf_channels": config["jf_channels"],
    #         "default_file_path": None,
    #     },
    # },
    # {
    #    "args": [
    #        config["checker_PV"],
    #        config["checker_thresholds"],
    #        config["checker_fractionInThreshold"],
    #    ],  #'SARFE10-PBPG050:HAMP-INTENSITY-CAL',[60,700],.7],
    #    "name": "checker",
    #    "desc": "checker functions for data acquisition",
    #    "type": "eco.acquisition.checkers:CheckerCA",
    #    "kwargs": {},
    # },
    # {
    #     "args": [
    #         "SARES20-LSCP9-FNS:CH1:VAL_GET",
    #         [-100000, 100000],
    #         config["checker_fractionInThreshold"],
    #     ],  #'SARFE10-PBPG050:HAMP-INTENSITY-CAL',[60,700],.7],
    #     "name": "checker_epics",
    #     "desc": "checker functions for data acquisition",
    #     "type": "eco.acquisition.checkers:CheckerCA",
    #     "kwargs": {},
    # },
    # {
    #     "args": [],
    #     "name": "lxt",
    #     "desc": "laser timing with pockels cells and phase shifter",
    #     "type": "eco.timing.lasertiming:Lxt",
    #     "kwargs": {},
    # },
    # {
    #     "args": ["SARES20-CVME-01-EVR0"],
    #     "name": "evr_bernina",
    #     "desc": "Bernina event receiver",
    #     "type": "eco.timing.event_timing:EventReceiver",
    #     "kwargs": {},
    # },
    # {
    #     "args": [],
    #     "name": "default_channel_list",
    #     "desc": "Bernina default channels, used in daq",
    #     "type": "eco.utilities.config:ChannelList",
    #     "kwargs": {
    #         "file_name": "/sf/bernina/config/channel_lists/default_channel_list"
    #     },
    # },
    # {
    #     "args": [],
    #     "name": "default_channel_list_bs",
    #     "desc": "Bernina default bs channels, used by bs_daq",
    #     "type": "eco.utilities.config:ChannelList",
    #     "kwargs": {
    #         "file_name": "/sf/bernina/config/channel_lists/default_channel_list_bs"
    #     },
    # },
    # {
    #     "args": [],
    #     "name": "channels_spectrometer_projection",
    #     "desc": "",
    #     "type": "eco.utilities.config:ChannelList",
    #     "kwargs": {
    #         "file_name": "/sf/bernina/config/channel_lists/channel_list_PSSS_projection"
    #     },
    # },
    # {
    #     "args": [],
    #     "name": "bs_daq",
    #     "desc": "bs daq writer (locally!)",
    #     "type": "eco.acquisition.bs_data:BStools",
    #     "kwargs": {
    #         "default_channel_list": {
    #             "bernina_default_channels_bs": Component("default_channel_list_bs")
    #         },
    #         "default_file_path": f"/sf/bernina/data/{config['pgroup']}/res/%s",
    #     },
    # },
    # {
    #     "args": ["SARES23-"],
    #     "name": "slit_kb",
    #     "z_und": 141,
    #     "desc": "Upstream diagnostics slits",
    #     "type": "eco.xoptics.slit_USD:Upstream_diagnostic_slits",
    #     "kwargs": {"right": "LIC4", "left": "LIC3", "up": "LIC2", "down": "LIC1"},
    # },
    # {
    #    "args": ["SARES23-"],
    #    "name": "slit_cleanup",
    #    "z_und": 141,
    #    "desc": "Upstream diagnostics slits",
    #    "type": "eco.xoptics.slit_USD:Upstream_diagnostic_slits",
    #    "kwargs": {"right": "LIC7", "left": "LIC8", "up": "LIC8", "down": "LIC5"},
    # },
    # {
    #     "args": [
    #         [
    #             Component("slit_und"),
    #             Component("slit_switch"),
    #             Component("slit_att"),
    #             Component("slit_kb"),
    #         ]
    #     ],
    #     "name": "slits",
    #     "desc": "collection of all slits",
    #     "type": "eco.utilities.beamline:Slits",
    #     "kwargs": {},
    # },
    # {
    #     "args": [
    #         [Component("slit_switch"), Component("slit_att"), Component("slit_kb"),]
    #     ],
    #     "name": "slits",
    #     "desc": "collection of all slits",
    #     "type": "eco.utilities.beamline:Slits",
    #     "kwargs": {},
    #     "lazy": False,
    # },
    # {
    #    "args": [],
    #    "name": "thc",
    #    "z_und": 142,
    #    "desc": "High field THz Chamber",
    #    "type": "eco.endstations.bernina_sample_environments:High_field_thz_chamber",
    #    "kwargs": {"Id": "SARES23", "configuration": ["ottifant"]},
    # },
    #    {
    #        "args": [],
    #        "name": "ocb",
    #        "z_und": 142,
    #        "desc": "Organic Crystal Breadboard",
    #        "type": "eco.endstations.bernina_sample_environments:Organic_crystal_breadboard",
    #        "kwargs": {"Id": "SARES23"},
    #    },
    #    {
    #        "args": [],
    #        "name": "eos",
    #        "z_und": 142,
    #        "desc": "electro optic sampling stages",
    #        "type": "eco.endstations.bernina_sample_environments:Electro_optic_sampling",
    #        "kwargs": {
    #            "Id": "SARES23",
    #            "pgroup": config["pgroup"],
    #            "diode_channels": {
    #                "d1": "SARES20-LSCP9-FNS:CH1:VAL_GET",
    #                "d2": "SARES20-LSCP9-FNS:CH2:VAL_GET",
    #                "diff": "SARES20-LSCP9-FNS:CH3:VAL_GET",
    #            },
    #        },
    #    },
]

try:
    components.extend(config["components"])
    print("Did append additional components!")
except:
    print("Could not append components from config.")
