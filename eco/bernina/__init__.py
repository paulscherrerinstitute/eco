from ..utilities.config import initFromConfigList
from epics import PV
from .. import ecocnf
from ..aliases import NamespaceCollection
import logging

from .config import components, config
import sys

try:
    from .bernina import *
    from ..utilities.runtable import Run_Table
except:
    print('Initializing of run_table failed')


_namespace = globals()

_mod = sys.modules[__name__]

_scope_name = "bernina"

alias_namespaces = NamespaceCollection()


def init(*args, lazy=None):
    if args:
        allnames = [tc["name"] for tc in components]
        comp_toinit = []
        for arg in args:
            if not arg in allnames:
                raise Exception(f"The component {arg} has no configuration defined!")
            else:
                comp_toinit.append(components[allnames.index(arg)])
    else:
        comp_toinit = components

    if lazy is None:
        lazy = ecocnf.startup_lazy

    op = {}
    for key, value in initFromConfigList(comp_toinit, components, lazy=lazy).items():
        # _namespace[key] = value
        _mod.__dict__[key] = value
        op[key] = value
        if not ecocnf.startup_lazy:
            try:
                for ta in value.alias.get_all():
                    alias_namespaces.bernina.update(
                        ta["alias"], ta["channel"], ta["channeltype"]
                    )
            except:
                pass
        alias_namespaces.bernina.store()
    try:
        run_table = bernina.init(config['pgroup'], alias_namespaces,_mod)
        _mod.__dict__['rt'] = run_table
        op['rt'] = run_table
    except:
        print('Initializing of run_table failed')
    return op




