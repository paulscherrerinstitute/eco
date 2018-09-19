
from ..utilities.config import loadConfig
from ..utilities.config import Component,Alias,init_device,initFromConfigList
from epics import PV
import sys,os


from .config import components

for key,value in initFromConfigList(components).items():
    globals()[key] = value

###########  configurations  ########################
#currexp_file_path = '/sf/bernina/config/exp/current_experiment.json'
#if os.path.exists(currexp_file_path):
#    exp_config = loadConfig(currexp_file_path)
#else:
#    print('NB: Could not load experiment config in path %s .'%currexp_file_path)

########### GENERAL IMPLEMENTATIONS ##################
#from .config import aliases as _aliases
#
#
#from importlib import import_module
#from functools import partial
#
#
#
#def getDevPar(dev):
#    args = ()
#    kwargs = {}
#    alias = ''
#    if 'args' in dev.keys():
#        args = dev['args']
#    if 'kwargs' in dev.keys():
#        kwargs = dev['kwargs']
#    if 'alias' in dev.keys():
#        alias = dev['alias']
#        alias = alias[0].lower() + alias[1:]
#
#    return alias, args, kwargs
#
#
#def initObj(obj,*args,**kwargs):
#    return obj(*args,**kwargs)
#
#
#for device_Id,dev in _aliases.items():
#    if 'eco_type' in dev.keys():
#        tt = dev['eco_type']
#        i = tt.rfind('.')
#        tt = ':'.join([tt[:i],tt[(i+1):]])
#        mod,obj = tt.split(':')
#        try:
#            tobj = getattr(import_module('.'.join(['eco',mod])),obj)
#            alias,args,kwargs = getDevPar(dev)
#            kwargs['Id'] = device_Id
#            globals()[alias] = LazyProxy(partial(initObj,tobj,*args,**kwargs))
#        except:
#            print(f'failed {obj} from {mod}.')
#            print(traceback.format_exc())
#
#
#
#print('done')
#
#def init_device(devDict,devId,args,kwargs,verbose=True):
#    imp_p = devDict['eco_type'].split(sep='.')
#    dev_alias = devDict['alias']
#    dev_alias = dev_alias[0].lower() + dev_alias[1:]
#    eco_type_name = imp_p[-1] 
#    istr = 'from ..'+'.'.join(imp_p[:-1])+' import '
#    istr += '%s as _%s'%(eco_type_name,eco_type_name)
#    #print(istr)
#    if verbose:
#        
#        print(('Configuring %s '%(dev_alias)).ljust(25), end='')
#        print(('(%s)'%(devId)).ljust(25), end='')
#    error = None
#    try:
#        exec(istr)
#        tdev = eval('_%s(Id=\'%s\',*args,**kwargs)'%(eco_type_name,devId))
#        tdev.name = dev_alias
#        tdev._z_und = devDict['z_und']
#        if verbose:
#            print((_color.GREEN+'OK'+_color.RESET).rjust(5))
#        return tdev
#    except Exception as expt:
#        #tb = traceback.format_exc()
#        if verbose:
#            print((_color.RED+'FAILED'+_color.RESET).rjust(5))
#            #print(sys.exc_info())
#        raise expt
#
#def initDeviceAliasList(aliases,lazy=False,verbose=True):
#    devices = {}
#    problems = {}
#    for device_Id in aliases.keys():
#        alias = aliases[device_Id]['alias']
#        alias = alias[0].lower() + alias[1:]
#        if 'eco_type' in aliases[device_Id].keys() \
#        and aliases[device_Id]['eco_type']:
#            if 'args' in aliases[device_Id].keys() \
#            and aliases[device_Id]['args']:
#                args = aliases[device_Id]['args']
#            else:
#                args = tuple()
#
#            if 'kwargs' in aliases[device_Id].keys() \
#            and aliases[device_Id]['kwargs']:
#                kwargs = aliases[device_Id]['kwargs']
#            else:
#                kwargs = dict()
#            try: 
#                devices[alias] = {}
#                devices[alias]['device_Id'] = device_Id
#                if lazy:
#                    devices[alias]['factory'] = lambda:init_device(aliases[device_Id],device_Id,args,kwargs,verbose=verbose)
#                    dev = LazyProxy(devices[alias]['factory'])
#                else:
#                    dev = init_device(aliases[device_Id],device_Id,args,kwargs,verbose=verbose)
#                devices[alias]['instance'] = dev
#            except:
#                device.pop(alias)
#                problems[alias] = {}
#                problems[alias]['device_Id'] = device_Id
#                problems[alias]['trace'] = traceback.format_exc()
#    return devices, problems 
#
#
#
##dev,problems = initDeviceAliasList(_aliases,lazy=True,verbose=True)
#
