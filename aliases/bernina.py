elog = {'url': 'https://elog-gfa.psi.ch/Bernina',
        'screenshot_directory': '/sf/bernina/config/screenshots'}

aliases = {
        'SARFE10-OPSH044' : {
            'alias' : 'ShutUnd',
            'z_und' : 44,
            'desc' : 'Photon shutter after Undulator'},
        'SARFE10-OAPU044' : {
            'alias' : 'SlitUnd',
            'z_und' : 44,
            'desc' : 'Slit after Undulator'},
        'SARFE10-PBIG050' : {
            'alias' : 'GasMon',
            'z_und' : 50,
            'desc' : 'Gas Monitor Intensity'},
        'SARFE10-PBPS053' : {
            'alias' : 'MonUnd',
            'z_und' : 44,
            'desc' : 'Intensity position monitor after Undulator'},
        'SARFE10-OATT053' : {
            'alias' : 'AttFE',
            'z_und' : 53,
            'desc' : 'Attenuator in Front End'},
        'SARFE10-SBST060' : {
            'alias' : 'ShutFE',
            'z_und' : 60,
            'desc' : 'Photon shutter in the end of Front End'},
        'SARFE10-PPRM064' : {
            'alias' : 'ProfFE',
            'z_und' : 64,
            'desc' : 'Profile monitor after Front End'},
        'SAROP11-OOMH064' : {
            'alias' : 'MirrAlv1',
            'z_und' : 64,
            'desc' : 'Horizontal mirror Alvra 1'},
        'SAROP11-PPRM066' : {
            'alias' : 'ProfMirrAlv1',
            'z_und' : 66,
            'desc' : 'Profile monitor after Alvra Mirror 1',
            'eco_type' : 'xdiagnostics.profile_monitors.Pprm'},
        'SAROP21-OAPU092' : {
            'alias' : 'SlitSwitch',
            'z_und' : 92,
            'desc' : 'Slit in Optics hutch after Photon switchyard and before Bernina optics'},
        'SAROP21-OOMV092' : {
            'alias' : 'Mirr1',
            'z_und' : 92,
            'desc' : 'Vertical offset Mirror 1'},
        'SAROP21-PPRM094' : {
            'alias' : 'ProfMirr1',
            'z_und' : 94,
            'desc' : 'Profile monitor after Mirror 1'},
        'SAROP21-OOMV096' : {
            'alias' : 'Mirr2',
            'z_und' : 96,
            'desc' : 'Vertical offset mirror 2'},
        'SAROP21-PSCR097' : {
                'alias' : 'ProfMirr2',
                'z_und' : 97,
                'desc' : 'Profile Monitor after Mirror 2'},
        'SAROP21-ODCM098' : {
                'alias' : 'Mono',
                'z_und' : 98,
                'desc' : 'DCM Monochromator',
                'eco_type' : 'xoptics.dcm.Double_Crystal_Mono'},
        'SAROP21-PPRM102' : {
                'alias' : 'ProfMono',
                'z_und' : 102,
                'desc' : 'Profile monitor after Monochromator'},
        'SAROP21-OPPI103' : {
                'alias' : 'Pick',
                'z_und' : 103,
                'desc' : 'X-ray pulse picker'},
        'SAROP21-BST114' : {
                'alias' : 'ShutOpt',
                'z_und' : 114,
                'desc' : 'Shutter after Optics hutch'},
        'SAROP21-PBPS133' : {
                'alias' : 'MonOpt',
                'z_und' : 133,
                'desc' : 'Intensity/position monitor after Optics hutch',
            'eco_type' : 'xdiagnostics.intensity_monitors.SolidTargetDetectorPBPS',
              'kwargs' : {'VME_crate':'SAROP21-CVME-PBPS','link':9} },
        'SAROP21-PPRM133' : {
                'alias' : 'ProfOpt',
                'z_und' : 133,
                'desc' : 'Profile monitor after Optics hutch'},
        'SAROP21-PALM134' : {
                'alias' : 'TimTof',
                'z_und' : 134,
                'desc' : 'Timing diagnostics THz streaking/TOF'},
        'SAROP21-PSEN135' : {
                'alias' : 'TimRef',
                'z_und' : 135,
                'desc' : 'Timing diagnostics spectral encoding of ref. index change'},
        'SAROP21-OATT135' : {
                'alias' : 'Att',
                'z_und' : 135,
                'desc' : 'Attenuator Bernina',
                'eco_type' : 'xoptics.attenuator_aramis.AttenuatorAramis'},
        'SAROP21-OAPU136' : {
                'alias' : 'SlitAtt',
                'z_und' : 136,
                'desc' : 'Slits behind attenuator'},
        'SAROP21-PBPS138' : {
                'alias' : 'MonAtt',
                'z_und' : 138,
                'desc' : 'Intensity/Position monitor after Attenuator',
            'eco_type' : 'xdiagnostics.intensity_monitors.SolidTargetDetectorPBPS',
              'kwargs' : {'VME_crate':'SAROP21-CVME-PBPS','link':9} },
        'SAROP21-PDIO138' : {
                'alias' : 'DetDio',
                'z_und' : 138,
                'desc' : 'Diode digitizer for exp data',
            'eco_type' : 'devices_general.detectors.DiodeDigitizer',
              'kwargs' : {'VME_crate':'SAROP21-CVME-PBPS','link':10} },
        'SAROP21-PPRM138' : {
                'alias' : 'ProfAtt',
                'z_und' : 138,
                'desc' : 'Profile monitor after Attenuator',
                'eco_type' : 'xdiagnostics.profile_monitors.Pprm'},
        'SAROP21-OKBV139' : {
                'alias' : 'KbVer',
                'z_und' : 139,
                'desc' : 'Vertically focusing Bernina KB mirror',
                'eco_type' : 'xoptics.KB.KB'},
        'SAROP21-OKBH140' : {
                'alias' : 'KbHor',
                'z_und' : 140,
                'desc' : 'Horizontally focusing Bernina KB mirror',
                'eco_type' : 'xoptics.KB.KB'},
        'SARES22-GPS' : {
                'alias' : 'Gps',
                'z_und' : 142,
                'desc' : 'General purpose station',
                'eco_type' : 'endstations.bernina_gps.GPS'},
        'SARES20-PROF142-M1' : {
                'alias' : 'Xeye',
                'z_und' : 142,
                'desc' : 'Mobile X-ray eye in Bernina hutch',
                'eco_type' : 'xdiagnostics.profile_monitors.Bernina_XEYE'},
        'SLAAR21-LMOT' : {
                'alias' : 'LasExp',
                'z_und' : 142,
                'desc' : 'Experiment laser optics',
                'eco_type' : 'loptics.bernina_experiment.Laser_Exp'},
#         = dict(
#            alias = ''
#            z_und = 
#            desc = ''},
      }


