from ..aliases.alvra import aliases as _aliases


def _attach_device(devDict,devId):
    imp_p = devDict['eco_type'].split(sep='.')
    dev_alias = devDict['alias']
    dev_alias = dev_alias[0].lower() + dev_alias[1:]
    eco_type_name = imp_p[-1] 
    istr = 'from ..'+'.'.join(imp_p[:-1])+' import '
    istr += '%s as _%s'%(eco_type_name,eco_type_name)
    print(istr)
    exec(istr)
    tdev = eval('_%s(Id=\'%s\')'%(eco_type_name,devId))
    globals().update([(dev_alias,tdev)])


for device_Id in _aliases.keys():
    if 'eco_type' in _aliases[device_Id].keys() and _aliases[device_Id]['eco_type']:
        _attach_device(_aliases[device_Id],device_Id)







