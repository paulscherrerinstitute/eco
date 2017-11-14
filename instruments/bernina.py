
from ..aliases.bernina import elog as _elog_info
from ..utilities.elog import Elog as _Elog


elog = _Elog(_elog_info['url'],user='gac-bernina',screenshot_directory=_elog_info['screenshot_directory'])



from ..aliases.bernina import aliases as _aliases
def _attach_device(devDict,devId,args,kwargs):
    imp_p = devDict['eco_type'].split(sep='.')
    dev_alias = devDict['alias']
    dev_alias = dev_alias[0].lower() + dev_alias[1:]
    eco_type_name = imp_p[-1] 
    istr = 'from ..'+'.'.join(imp_p[:-1])+' import '
    istr += '%s as _%s'%(eco_type_name,eco_type_name)
    print(istr)
    exec(istr)
    tdev = eval('_%s(Id=\'%s\',*args,**kwargs)'%(eco_type_name,devId))
    tdev.name = dev_alias
    globals().update([(dev_alias,tdev)])


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
        
        _attach_device(_aliases[device_Id],device_Id,args,kwargs)


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
channellist = dict(bernina_channel_list=
        parseChannelListFile('/sf/bernina/config/com/channel_lists/default_channel_list'))
bsdaq = BStools(default_channel_list=channellist,default_file_path='%s')





