import json
import importlib
from colorama import Fore as _color
from functools import partial

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


class LazyProxy(object):
    """
   Modified from http://code.activestate.com/recipes/496741-object-proxying/
    """
    __slots__ = ["_obj_fn", "__weakref__", "__proxy_storage"]
    def __init__(self, fn, storage=None):
        object.__setattr__(self, "_obj_fn", fn)
        object.__setattr__(self, "__proxy_storage", storage)
        
    #   
    # proxying (special cases)
    #   
    def __getattribute__(self, name):
        return getattr(object.__getattribute__(self, "_obj_fn")(), name)
    def __delattr__(self, name):
        delattr(object.__getattribute__(self, "_obj_fn")(), name)
    def __setattr__(self, name, value):
        setattr(object.__getattribute__(self, "_obj_fn")(), name, value)
    def __getitem__(self, index):
        return object.__getattribute__(self, "_obj_fn")().__getitem__(index)
    def __nonzero__(self):
        return bool(object.__getattribute__(self, "_obj_fn")())
    def __str__(self):
        return str(object.__getattribute__(self, "_obj_fn")())
    def __repr__(self):
        return repr(object.__getattribute__(self, "_obj_fn")())
    def __len__(self):
        return len(object.__getattribute__(self, "_obj_fn")())
        
    #   
    # factories
    #   
    _special_names = [ 
        '__abs__', '__add__', '__and__', '__call__', '__cmp__', '__coerce__', 
        '__contains__', '__delitem__', '__delslice__', '__div__', '__divmod__', 
        '__eq__', '__float__', '__floordiv__', '__ge__', #'__getitem__', 
        '__getslice__', '__gt__', '__hash__', '__hex__', '__iadd__', '__iand__',
        '__idiv__', '__idivmod__', '__ifloordiv__', '__ilshift__', '__imod__',
        '__imul__', '__int__', '__invert__', '__ior__', '__ipow__', '__irshift__',
        '__isub__', '__iter__', '__itruediv__', '__ixor__', '__le__', #'__len__',
        '__long__', '__lshift__', '__lt__', '__mod__', '__mul__', '__ne__',
        '__neg__', '__oct__', '__or__', '__pos__', '__pow__', '__radd__',
        '__rand__', '__rdiv__', '__rdivmod__', '__reduce__', '__reduce_ex__',
        '__repr__', '__reversed__', '__rfloorfiv__', '__rlshift__', '__rmod__',
        '__rmul__', '__ror__', '__rpow__', '__rrshift__', '__rshift__', '__rsub__',
        '__rtruediv__', '__rxor__', '__setitem__', '__setslice__', '__sub__', 
        '__truediv__', '__xor__', 'next',
    ]   
        
    @classmethod
    def _create_class_proxy(cls, theclass):
        """creates a proxy for the given class"""
        
        def make_method(name): 
            def method(self, *args, **kw):
                return getattr(object.__getattribute__(self, "_obj_fn")(), name)(*args, **kw)
            return method
                
        namespace = {}
        for name in cls._special_names:
            if hasattr(theclass, name):
                namespace[name] = make_method(name)
        return type("%s(%s)" % (cls.__name__, theclass.__name__), (cls,), namespace)
                
    def __new__(cls, obj, *args, **kwargs):
        """
        creates an proxy instance referencing `obj`. (obj, *args, **kwargs) are
        passed to this class' __init__, so deriving classes can define an
        __init__ method of their own.
        note: _class_proxy_cache is unique per deriving class (each deriving
        class must hold its own cache)
        """
        try:
            cache = cls.__dict__["_class_proxy_cache"]
        except KeyError:
            cls._class_proxy_cache = cache = {}
        try:
            theclass = cache[obj.__class__]
        except KeyError:
            cache[obj.__class__] = theclass = cls._create_class_proxy(obj.__class__)
        ins = object.__new__(theclass)
        theclass.__init__(ins, obj, *args, **kwargs)


def init_name_obj(obj,args,kwargs,name=None):
    try:
        tdev = obj(*args,name=name,**kwargs)
    except TypeError:
        tdev = obj(*args,**kwargs)
    print(tdev)
    return tdev


def init_device(type_string,name,args=[],kwargs={},verbose=True,lazy=False):
    imp_p,type_name = type_string.split(sep=':')
    imp_p = imp_p.split(sep='.')
    if verbose:
        print(('Configuring %s '%(name)).ljust(25), end='')
        print(('(%s)'%(type_name)).ljust(25), end='')
    try:
        tg = importlib.import_module('.'.join(imp_p)).__dict__[type_name]

        if lazy:
            tdev = LazyProxy(init_name_obj(tg,args,kwargs,name=name))
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
