import json
import importlib
from colorama import Fore as _color
from functools import partial
from .lazy_proxy import Proxy

class Component:
    def __init__(self,namestring):
        self.name = namestring

class Alias:
    def __init__(self,alias,channel=None,channeltype=None):
        self.alias = alias
        self.channel = channel
        self.channeltype = channeltype
        self.children = []

    def append(self,subalias):
        assert type(subalias) is Alias, 'You can only append aliases to aliases!'
        assert not (subalias.alias in [tc.alias for tc in self.children]),\
                f'Alias {subalias.alias} exists already!'
        self.children.append(subalias)

    def get_all(self):
        aa = []
        if self.channel:
            ta = {}
            ta['alias'] = self.alias
            ta['channel'] = self.channel
            if self.channeltype:
                ta['channeltype'] = self.channeltype
            aa.append(ta)
        if self.children:
            for tc in self.children:
                taa = tc.get_all()
                for ta in taa:
                    ta['alias'] = self.alias + ta['alias']
                    aa.append(ta)




def init_device(type_string,name,args=[],kwargs={},verbose=True,lazy=False):
    imp_p,type_name = type_string.split(sep=':')
    imp_p = imp_p.split(sep='.')
    if verbose:
        print(('Configuring %s '%(name)).ljust(25), end='')
        print(('(%s)'%(type_name)).ljust(25), end='')
    try:
        tg = importlib.import_module('.'.join(imp_p)).__dict__[type_name]

        if lazy:
            tdev = Proxy(init_name_obj(tg,args,kwargs,name=name))
            if verbose:
                print((_color.YELLOW+'LAZY'+_color.RESET).rjust(5))
        else:
            tdev = init_name_obj(tg,args,kwargs,name=name)
            if verbose:
                print((_color.GREEN+'OK'+_color.RESET).rjust(5))
        return tdev
    except Exception as expt:
        #tb = traceback.format_exc()
        if verbose:
            print((_color.RED+'FAILED'+_color.RESET).rjust(5))
            #print(sys.exc_info())
        raise expt

def initFromConfigList(config_list):
    op = {}
    for td in config_list:
        args = [op[ta.name] 
                if isinstance(ta,Component) 
                else ta for ta in td['args']]
        kwargs = {tkwk:op[tkwv.name]
                if isinstance(tkwv,Component) 
                else tkwv for tkwk,tkwv in td['kwargs'].items()}
        op[td['name']] = init_device(td['type'],td['name'],args,kwargs)
    return op



def initializeFromConfig(config):
    pass


def loadConfig(fina):
    with open(fina,'r') as f:
        return json.load(f)

def writeConfig(fina,obj):
    with open(fina,'w') as f:
        json.dump(obj,f)
