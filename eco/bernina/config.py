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
from ..utilities.config import Component,Alias,init_device,initFromConfigList

_eco_lazy_init = False

components = [
#        {
#            'name'  : 'device_alias_name',
#            'type'  : 'package.module.submodule:ClassOrFactory',
#            'args'  : ['all','the','requires','args'],
#            'kwargs': {}
#            }
        {
            'name'  : 'elog',
            'type'  : 'eco.utilities.elog:Elog',
            'args'  : [
                'https://elog-gfa.psi.ch/Bernina'],
            'kwargs': {
                'user':'gac-bernina',
                'screenshot_directory':'/sf/bernina/config/screenshots'
                }
            },
        {
            'name'  : 'screenshot',
            'type'  : 'eco.utilities.elog:Screenshot',
            'args'  : [],
            'kwargs': {
                'screenshot_directory':'/sf/bernina/config/screenshots'}
            },
        {
            'name'  : 'slitUnd',
            'type'  : 'eco.xoptics.slits:SlitFourBlades',
            'args'  : ['SARFE10-OAPU044'],
            'kwargs': {},
            'desc'  : 'Slit after Undulator'
            },
        {
            'name'  : 'attFE',
            'type'  : 'eco.xoptics.attenuator_aramis:AttenuatorAramis',
            'args'  : ['SARFE10-OATT053'],
            'kwargs': {},
            'desc'  : 'Attenuator in Front End'
            },
        {
            'name'  : 'profFE',
            'args'  : ['SARFE10-PPRM064'],
            'kwargs': {},
            'z_und' : 64,
            'desc'  : 'Profile monitor after Front End',
            'type'  : 'eco.xdiagnostics.profile_monitors:Pprm'
            },
        {
            'name'  : 'profMirrAlv1',
            'args'  : ['SAROP11-PPRM066'],
            'kwargs': {},
            'z_und' : 66,
            'desc'  : 'Profile monitor after Alvra Mirror 1',
            'type'  : 'eco.xdiagnostics.profile_monitors:Pprm',
            },
        {
            'name'  : 'slitSwitch',
            'z_und' : 92,
            'desc'  : 'Slit in Optics hutch after Photon switchyard and before Bernina optics',
            'type'  : 'eco.xoptics.slits:SlitBlades',
            'args'  : ['SAROP21-OAPU092'],
            'kwargs': {}
            },
        {
            'name'  : 'profMirr1',
            'args'  : ['SAROP21-PPRM094'],
            'kwargs': {},
            'z_und' : 94,
            'desc'  : 'Profile monitor after Mirror 1',
            'type'  : 'eco.xdiagnostics.profile_monitors:Pprm'
            },
        {
            'name'  : 'mono',
            'args'  : ['SAROP21-ODCM098'],
            'kwargs': {},
            'z_und' : 98,
            'desc'  : 'DCM Monochromator',
            'type'  : 'eco.xoptics.dcm:Double_Crystal_Mono'
            },
        {
            'name'  : 'profMono',
            'args'  : ['SAROP21-PPRM102'],
            'kwargs': {},
            'z_und' : 102,
            'desc'  : 'Profile monitor after Monochromator',
            'type'  : 'eco.xdiagnostics.profile_monitors:Pprm'
            },
        {
            'name'  : 'monOpt',
            'z_und' : 133,
            'desc'  : 'Intensity/position monitor after Optics hutch',
            'type'  : 'eco.xdiagnostics.intensity_monitors:SolidTargetDetectorPBPS',
            'args'  : ['SAROP21-PBPS133'],
            'kwargs': {'VME_crate':'SAROP21-CVME-PBPS1','link':9}
            },
        {
            'name'  : 'profOpt',
            'args'  : ['SAROP21-PPRM133'],
            'kwargs': {},
            'z_und' : 133,
            'desc'  : 'Profile monitor after Optics hutch',
            'type'  : 'eco.xdiagnostics.profile_monitors:Pprm'
            },
        {
            'name'  : 'att',
            'args'  : ['SAROP21-OATT135'],
            'kwargs': {},
            'z_und' : 135,
            'desc'  : 'Attenuator Bernina',
            'type'  : 'eco.xoptics.attenuator_aramis:AttenuatorAramis'
            },
        {
            'name'  : 'refLaser',
            'args'  : ['SAROP21-OLAS136'],
            'kwargs': {},
            'z_und' : 136,
            'desc'  : 'Bernina beamline reference laser before KBs',
            'type'  : 'eco.xoptics.reflaser:RefLaser_Aramis'
            },
        {
            'name'  : 'slitAtt',
            'args'  : ['SAROP21-OAPU136'],
            'kwargs': {},
            'z_und' : 136,
            'desc'  : 'Slits behind attenuator',
            'type'  : 'eco.xoptics.slits:SlitPosWidth'
            },
        {
            'name'  : 'monAtt',
            'args'  : ['SAROP21-PBPS138'],
            'z_und' : 138,
            'desc'  : 'Intensity/Position monitor after Attenuator',
            'type'  : 'eco.xdiagnostics.intensity_monitors:SolidTargetDetectorPBPS',
            'kwargs': {'VME_crate':'SAROP21-CVME-PBPS2','link':9}
            },
        {
            'name'  : 'detDio',
            'args'  : ['SAROP21-PDIO138'],
            'z_und' : 138,
            'desc'  : 'Diode digitizer for exp data',
            'type'  : 'eco.devices_general.detectors:DiodeDigitizer',
            'kwargs': {'VME_crate':'SAROP21-CVME-PBPS2','link':9}
            },
        {
            'name'  : 'profAtt',
            'args'  : ['SAROP21-PPRM138'],
            'kwargs': {},
            'z_und' : 138,
            'desc'  : 'Profile monitor after Attenuator',
            'type'  : 'eco.xdiagnostics.profile_monitors:Pprm'
            },
        {
            'name'  : 'kbVer',
            'args'  : ['SAROP21-OKBV139'],
            'z_und' : 139,
            'desc'  : 'Vertically focusing Bernina KB mirror',
            'type'  : 'eco.xoptics.KBver:KBver',
            'kwargs': {}
            },
        {
            'args'  : ['SAROP21-OKBH140'],
            'name'  : 'kbHor',
            'z_und' : 140,
            'desc'  : 'Horizontally focusing Bernina KB mirror',
            'type'  : 'eco.xoptics.KBhor:KBhor',
            'kwargs': {}
            },
#        {
#            'args'  : ['SARES22-GPS'],
#            'name'  : 'gps',
#            'z_und' : 142,
#            'desc'  : 'General purpose station',
#            'type'  : 'eco.endstations.bernina_gps:GPS',
#            'kwargs': {}
#            },
        {
            'args'  : ['SARES20-PROF142-M1'],
            'name'  : 'xeye',
            'z_und' : 142,
            'desc'  : 'Mobile X-ray eye in Bernina hutch',
            'type'  : 'eco.xdiagnostics.profile_monitors:Bernina_XEYE',
            'kwargs': {'bshost':'sf-daqsync-01.psi.ch','bsport':11173}
            },
        {
            'args'  : ['SLAAR02-TSPL-EPL'],
            'name'  : 'phaseShifter',
            'z_und' : 142,
            'desc'  : 'Experiment laser phase shifter',
            'type'  : 'eco.devices_general.timing:PhaseShifterAramis',
            'kwargs': {}
            },
        {
            'args'  : ['SLAAR21-LMOT'],
            'name'  : 'las',
            'z_und' : 142,
            'desc'  : 'Experiment laser optics',
            'type'  : 'eco.loptics.bernina_experiment:Laser_Exp',
            'kwargs': {}
            },
        {
            'args'  : ['SLAAR21-LTIM01-EVR0'],
            'name'  : 'laserShutter',
            'z_und' : 142,
            'desc'  : 'Laser Shutter',
            'type'  : 'eco.loptics.laser_shutter:laser_shutter',
            'kwargs': {}
            },


        ]
            


components_old = {
        'SARFE10-OPSH044' : {
            'alias' : 'ShutUnd',
            'z_und' : 44,
            'desc' : 'Photon shutter after Undulator'},
        'SARFE10-PBIG050' : {
            'alias' : 'GasMon',
            'z_und' : 50,
            'desc' : 'Gas Monitor Intensity'},
        'SARFE10-PBPS053' : {
            'alias' : 'MonUnd',
            'z_und' : 44,
            'desc' : 'Intensity position monitor after Undulator'},
        'SARFE10-SBST060' : {
            'alias' : 'ShutFE',
            'z_und' : 60,
            'desc' : 'Photon shutter in the end of Front End'},
        'SAROP11-OOMH064' : {
            'alias' : 'MirrAlv1',
            'z_und' : 64,
            'desc' : 'Horizontal mirror Alvra 1'},
        'SAROP21-OOMV092' : {
            'alias' : 'Mirr1',
            'z_und' : 92,
            'desc' : 'Vertical offset Mirror 1'},
        'SAROP21-OOMV096' : {
            'alias' : 'Mirr2',
            'z_und' : 96,
            'desc' : 'Vertical offset mirror 2'},
        'SAROP21-PSCR097' : {
                'alias' : 'ProfMirr2',
                'z_und' : 97,
                'desc' : 'Profile Monitor after Mirror 2'},
        'SAROP21-OPPI103' : {
                'alias' : 'Pick',
                'z_und' : 103,
                'desc' : 'X-ray pulse picker'},
        'SAROP21-BST114' : {
                'alias' : 'ShutOpt',
                'z_und' : 114,
                'desc' : 'Shutter after Optics hutch'},
        'SAROP21-PALM134' : {
                'alias' : 'TimTof',
                'z_und' : 134,
                'desc' : 'Timing diagnostics THz streaking/TOF'},
        'SAROP21-PSEN135' : {
                'alias' : 'TimRef',
                'z_und' : 135,
                'desc' : 'Timing diagnostics spectral encoding of ref. index change'}
#        'SLAAR21-LMOT' : {
#                'alias' : 'Palm',
#                'z_und' : 142,
#                'desc' : 'Streaking arrival time monitor',
#                'eco_type' : 'timing.palm.Palm'},
#        'SLAAR21-LMOT' : {
#                'alias' : 'Psen',
#                'z_und' : 142,
#                'desc' : 'Streaking arrival time monitor',
#                'eco_type' : 'timing.psen.Psen'}

#         = dict(
#            alias = ''
#            z_und = 
#            desc = ''},
      }


