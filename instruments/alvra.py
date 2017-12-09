
from ..aliases.alvra import elog as _elog_info
from ..utilities.elog import Elog as _Elog
from ..utilities.elog import Screenshot as _Screenshot
from epics import PV


from colorama import Fore as _color
import traceback

elog = _Elog(_elog_info['url'],user='gac-alvra',screenshot_directory=_elog_info['screenshot_directory'])
screenshot = _Screenshot(screenshot_directory=_elog_info['screenshot_directory'])



from ..aliases.alvra import aliases as _aliases
def _attach_device(devDict,devId,args,kwargs):
    imp_p = devDict['eco_type'].split(sep='.')
    dev_alias = devDict['alias']
    dev_alias = dev_alias[0].lower() + dev_alias[1:]
    eco_type_name = imp_p[-1] 
    istr = 'from ..'+'.'.join(imp_p[:-1])+' import '
    istr += '%s as _%s'%(eco_type_name,eco_type_name)
    #print(istr)
    print(('Configuring %s '%(dev_alias)).ljust(25), end='')
    print(('(%s)'%(devId)).ljust(25), end='')
    error = None
    try:
        exec(istr)
        tdev = eval('_%s(Id=\'%s\',*args,**kwargs)'%(eco_type_name,devId))
        tdev.name = dev_alias
        tdev._z_und = devDict['z_und']
        globals().update([(dev_alias,tdev)])
        print((_color.GREEN+'OK'+_color.RESET).rjust(5))
    except Exception as e:
        print((_color.RED+'FAILED'+_color.RESET).rjust(5))
        error = e
    return error

errors = []
for device_Id in _aliases.keys():
    if 'eco_type' in _aliases[device_Id].keys() \
    and _aliases[device_Id]['eco_type']:
        if 'args' in _aliases[device_Id].keys() \
        and _aliases[device_Id]['args']:
            args = _aliases[device_Id]['args']
        else:
            args = tuple()

        if 'kwargs' in _aliases[device_Id].keys() \
        and _aliases[device_Id]['kwargs']:
            kwargs = _aliases[device_Id]['kwargs']
        else:
            kwargs = dict()
        
        e = _attach_device(_aliases[device_Id],device_Id,args,kwargs)
        if e: errors.append((_aliases[device_Id]['alias'],e))

if len(errors)>0:
    print('Found errors when configuring %s'%[te[0] for te in errors])
    if input('Would you like to see error traces? (y/n)')=='y':
        for error in errors:
            print('---> Error when configuring %s'%error[0])
            traceback.print_tb(error[1].__traceback__)



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

channellist = dict(alvra_channel_list=
        parseChannelListFile('/sf/alvra/config/com/channel_lists/default_channel_list'))
bsdaq = BStools(default_channel_list=channellist,default_file_path='%s')

## following seems JF specific so comment out for now
# from eco.devices_general.detectors import JF_BS_writer
# bsdaqJF = JF_BS_writer('bsdaqJF') 


checkerPV=PV('SARFE10-PBPG050:HAMP-INTENSITY-CAL')

def checker_function(limits):
    cv = checkerPV.get()
    if cv>limits[0] and cv<limits[1]:
        return True
    else:
        return False


checker = {}
checker['checker_call'] = checker_function
checker['args'] = [[100,300]]
checker['kwargs'] = {}
checker['wait_time'] = 3


## removed below for JF
# scansJF = _scan.Scans(data_base_dir='/sf/alvra/config/com/data/scan_data',scan_info_dir='/sf/alvra/config/com/data/scan_info',default_counters=[bsdaqJF],checker=checker)
scansBsreadLocal = _scan.Scans(data_base_dir='/sf/alvra/config/com/data/scan_data',scan_info_dir='/sf/alvra/config/com/data/scan_info',default_counters=[bsdaq])

from ..timing.alvralasertiming import Lxt as _Lxt

lxt = _Lxt()
