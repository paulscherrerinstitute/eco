
from ..aliases.bernina import elog as _elog_info
from ..utilities.elog import Elog as _Elog
from ..utilities.elog import Screenshot as _Screenshot
from ..utilities.config import loadConfig
from epics import PV
import sys,os

from colorama import Fore as _color
import traceback

elog = _Elog(_elog_info['url'],user='gac-bernina',screenshot_directory=_elog_info['screenshot_directory'])
screenshot = _Screenshot(screenshot_directory=_elog_info['screenshot_directory'])

###########  configurations  ########################
currexp_file_path = '/sf/bernina/config/current_experiment.json'
if os.path.exists(currexp_file_path):
    exp_config = loadConfig(currexp_file_path)
else:
    print('NB: Could not load experiment config in path %s .'%currexp_file_path)

########### GENERAL IMPLEMENTATIONS ##################
from ..aliases.bernina import aliases as _aliases
from .utilities_instruments import initDeviceAliasList

_devices,_problems = initDeviceAliasList(_aliases,verbose=True,lazy=True)
for tdev_id,talias,tdev in _devices:
    globals().update([(talias,tdev)])


if _problems:
    print('Found errors when configuring %s'%[te[1] for te in _problems])
    if input('Would you like to see error traces? (y/n)')=='y':
        for error in _problems:
            print('---> Error when configuring %s (%s)'%(error[0],error[1]))
            print(error[2])



########### DAQ SECTION  ########################
# configuring bs daq

def parseChannelListFile(fina):
    out = []
    with open(fina,'r') as f:
        done = False
        while not done:
           d = f.readline()
           if not d:
               done=True
           if len(d)>0:
               if not d.isspace():
                   if not d[0]=='#':
                       out.append(d.strip())
    return out


from ..acquisition.bs_data import BStools
from ..acquisition import scan as _scan
from ..acquisition.ioxos_data import Ioxostools

channellist = dict(bernina_channel_list=
        parseChannelListFile('/sf/bernina/config/com/channel_lists/default_channel_list'))
bsdaq = BStools(default_channel_list=channellist,default_file_path='%s')

channellistioxos = dict(bernina_channel_list=
        parseChannelListFile('/sf/bernina/config/default_channels/default_channel_list_ioxos'))
ioxosdaq = Ioxostools(default_channel_list=channellistioxos,default_file_path='%s')


#from eco.devices_general.detectors import JF_BS_writer
#bsdaqJF = JF_BS_writer('bsdaqJF') d
from eco.devices_general.detectors import DIAClient
bsdaqJF = DIAClient('bsdaqJF', instrument="bernina", api_address = "http://sf-daq-1:10000") 

try:
    bsdaqJF.pgroup = int(exp_config['pgroup'][1:])
except:
    print('Could not set p group in bsdaqJF !!')

checkerPV=PV('SARFE10-PBPG050:HAMP-INTENSITY-CAL')

def checker_function(limits):
    cv = checkerPV.get()
    if cv>limits[0] and cv<limits[1]:
        return True
    else:
        return False


checker = {}
checker['checker_call'] = checker_function
checker['args'] = [[100,700]]
checker['kwargs'] = {}
checker['wait_time'] = 3


scansIoxos = _scan.Scans(data_base_dir='/sf/bernina/config/com/data/scan_data',scan_info_dir='/sf/bernina/config/com/data/scan_info',default_counters=[ioxosdaq])
scansJF = _scan.Scans(data_base_dir='scan_data',scan_info_dir='/sf/bernina/data/%s/res/scan_info'%exp_config['pgroup'],default_counters=[bsdaqJF],checker=checker,scan_directories=True)
scansBsreadLocal = _scan.Scans(data_base_dir='/sf/bernina/config/com/data/scan_data',scan_info_dir='/sf/bernina/config/com/data/scan_info',default_counters=[bsdaq])



###########  ADHOC IMPLEMENTED  ########################
bsdaqJF.gain_file = "/sf/bernina/config/com/data/gains_I0.h5"

import glob
list_of_files = glob.glob('/sf/bernina/data/p17247/res/JF_pedestal/pedestal_*_res.h5') 
latest_file = max(list_of_files, key=os.path.getctime)
bsdaqJF.pede_file = latest_file

from ..timing.lasertiming import Lxt as _Lxt

lxt = _Lxt()