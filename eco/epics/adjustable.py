import time
from enum import IntEnum

import numpy as np
from epics import PV

from eco.aliases import Alias
from eco.elements.adjustable import (
    AdjustableMemory,
    tweak_option,
    spec_convenience,
    value_property,
)
from . import get_from_archive
from eco.devices_general.utilities import Changer
from ..elements.assembly import Assembly



# Work in progress! TODO
@spec_convenience
@get_from_archive
@tweak_option
@value_property
class AdjustableAtomicPv:
    def __init__(
        self,
        pvsetname,
    ):
        #        alias_fields={"setpv": pvsetname, "readback": pvreadbackname},
        #    ):
        self.pvname = pvsetname
        self.name = name
        #        for an, af in alias_fields.items():
        #            self.alias.append(
        #                Alias(an, channel=".".join([pvname, af]), channeltype="CA")
        #            )

        self._pv = PV(self.pvname, connection_timeout=0.05, count=element_count)
        self._currentChange = None
        self.accuracy = accuracy

        if pvreadbackname is None:
            self._pvreadback = PV(self.pvname, count=element_count, connection_timeout=0.05)
            pvreadbackname = self.pvname
            self.pvname = self.pvname
        else:
            self._pvreadback = PV(
                pvreadbackname, count=element_count, connection_timeout=0.05
            )
            self.pvname = pvreadbackname

        if pvlowlimname:
            self._pvlowlim = PV(
                pvlowlimname, count=element_count, connection_timeout=0.05
            )
        else:
            self._pvlowlim = None
        if pvhighlimname:
            self._pvhighlim = PV(
                pvhighlimname, count=element_count, connection_timeout=0.05
            )
        else:
            self._pvhighlim = None
        self.alias = Alias(name, channel=pvreadbackname, channeltype="CA")

    def _wait_for_initialisation(self):
        self._pv.wait_for_connection()
        if hasattr(self, "_pv_readback") and self._pv_readback:
            self._pv_readback.wait_for_connection()
        if hasattr(self, "_pv_lowliself.accuracy = accuracym") and self._pv_lowlim:
            self._pv_lowlim.wait_for_connection()
        if hasattr(self, "_pv_highlim") and self._pv_highlim:
            self._pv_highlim.wait_for_connection()
    
    def get_current_value(self, readback=True):
        if readback:
            currval = self._pvreadback.get()
        if not readback:
            currval = self._pv.get()
        return currval

    def get_change_done(self):
        """Adjustable convention"""
        """ 0: moving 1: move done"""
        change_done = 1
        if self.accuracy is not None:
            if (
                np.abs(
                    self.get_current_value(readback=False)
                    - self.get_current_value(readback=True)
                )
                > self.accuracy
            ):
                change_done = 0
        return change_done

    def change(self, value):
        if self._pvlowlim:
            if value < self._pvlowlim.get():
                raise Exception(
                    f"Target value of {self.name} is smaller than limit value!"
                )
        if self._pvhighlim:
            if self._pvhighlim.get() < value:
                raise Exception(
                    f"Target value of {self.name} is higher than limit value!"
                )

        self._pv.put(value)
        time.sleep(0.1)
        while self.get_change_done() == 0:
            time.sleep(0.1)

    def set_target_value(self, value, hold=False):
        """Adjustable convention"""

        changer = lambda value: self.change(value)
        return Changer(
            target=value, parent=self, changer=changer, hold=hold, stopper=None
        )


@spec_convenience
@get_from_archive
@tweak_option
@value_property
class AdjustablePv:
    def __init__(
        self,
        pvsetname,
        pvreadbackname=None,
        pvlowlimname=None,
        pvhighlimname=None,
        accuracy=None,
        name=None,
        elog=None,
        element_count=None,
        unit=None,
    ):
        #        alias_fields={"setpv": pvsetname, "readback": pvreadbackname},
        #    ):
        self.Id = pvsetname
        self.name = name
        #        for an, af in alias_fields.items():
        #            self.alias.append(
        #                Alias(an, channel=".".join([pvname, af]), channeltype="CA")
        #            )

        self._pv = PV(self.Id, connection_timeout=0.05, count=element_count)
        self._currentChange = None
        self.accuracy = accuracy
        if unit:
            self.unit = AdjustableMemory(unit, name="unit")

        if pvreadbackname is None:
            self._pvreadback = PV(self.Id, count=element_count, connection_timeout=0.05)
            pvreadbackname = self.Id
            self.pvname = self.Id
        else:
            self._pvreadback = PV(
                pvreadbackname, count=element_count, connection_timeout=0.05
            )
            self.pvname = pvreadbackname

        if pvlowlimname:
            self._pvlowlim = PV(
                pvlowlimname, count=element_count, connection_timeout=0.05
            )
        else:
            self._pvlowlim = None
        if pvhighlimname:
            self._pvhighlim = PV(
                pvhighlimname, count=element_count, connection_timeout=0.05
            )
        else:
            self._pvhighlim = None
        self.alias = Alias(name, channel=pvreadbackname, channeltype="CA")

    def _wait_for_initialisation(self):
        self._pv.wait_for_connection()
        if hasattr(self, "_pv_readback") and self._pv_readback:
            self._pv_readback.wait_for_connection()
        if hasattr(self, "_pv_lowlim") and self._pv_lowlim:
            self._pv_lowlim.wait_for_connection()
        if hasattr(self, "_pv_highlim") and self._pv_highlim:
            self._pv_highlim.wait_for_connection()
    
    def get_current_value(self, readback=True):
        if readback:
            currval = self._pvreadback.get()
        if not readback:
            currval = self._pv.get()
        return currval

    def get_change_done(self):
        """Adjustable convention"""
        """ 0: moving 1: move done"""
        change_done = 1
        if self.accuracy is not None:
            
            if (
                np.abs(
                    self.get_current_value(readback=False)
                    - self.get_current_value(readback=True)
                )
                > self.accuracy
            ):
                change_done = 0
        return change_done

    def change(self, value):
        if self._pvlowlim:
            if value < self._pvlowlim.get():
                raise Exception(
                    f"Target value of {self.name} is smaller than limit value!"
                )
        if self._pvhighlim:
            if self._pvhighlim.get() < value:
                raise Exception(
                    f"Target value of {self.name} is higher than limit value!"
                )

        self._pv.put(value)
        while self.get_change_done() == 0:
            time.sleep(0.01)

    def set_target_value(self, value, hold=False):
        """Adjustable convention"""

        changer = lambda value: self.change(value)
        return Changer(
            target=value, parent=self, changer=changer, hold=hold, stopper=None
        )

    def get_limits(self):
        return(self._pvlowlim.get(),self._pvhighlim.get())
    
    def set_limits(self, lowlim, highlim):
        return(self._pvlowlim.put(lowlim),self._pvhighlim.put(highlim))

    # spec-inspired convenience methods
    # def mv(self, value):
    # self._currentChange = self.set_target_value(value)

    # def wm(self, *args, **kwargs):
    # return self.get_current_value(*args, **kwargs)

    # def mvr(self, value, *args, **kwargs):

    # if self.get_moveDone == 1:
    # startvalue = self.get_current_value(readback=True, *args, **kwargs)
    # else:
    # startvalue = self.get_current_value(readback=False, *args, **kwargs)
    # self._currentChange = self.set_target_value(value + startvalue, *args, **kwargs)

    # def wait(self):
    # self._currentChange.wait()

    def __repr__(self):
        return "%s is at: %s" % (self.Id, self.get_current_value())


@spec_convenience
@get_from_archive
@value_property
class AdjustablePvEnum:
    def __init__(self, pvname, pvname_set=None, name=None):
        self.Id = pvname
        self.pvname = pvname
        self._pv = PV(pvname, connection_timeout=0.05*2)
        self.name = name
        self._pv.wait_for_connection()
        self.enum_strs = self._pv.enum_strs
        # while not self.enum_strs:  ### HACK to understand gateway slowness
        #     print(f'could not find enum strs for {self.pvname}')
        #     time.sleep(.1)
        #     self.enum_strs = self._pv.enum_strs

        if pvname_set:
            self._pv_set = PV(pvname_set, connection_timeout=0.05*2)
            tstrs = self._pv_set.enum_strs
            if not all([tstr in self.enum_strs for tstr in tstrs]):
                raise Exception("pv enum setter strings are not all a readback option!")
            
            self.get2set={}
            for nset,tstr in enumerate(tstrs):
                self.get2set[self.enum_strs.index(tstr)] = nset
            

        else:
            self._pv_set = None

        if name:
            enumname = self.name
        else:
            enumname = self.Id
        self.PvEnum = IntEnum(
            enumname, {tstr: n for n, tstr in enumerate(self.enum_strs)}
        )
        self.alias = Alias(name, channel=self.Id, channeltype="CA")

    def _wait_for_initialisation(self):
        self._pv.wait_for_connection()
        if hasattr(self, "_pv_set") and self._pv_set:
            self._pv_set.wait_for_connection()

    def validate(self, value):
        if type(value) is str:
            return self.PvEnum.__members__[value]
        else:
            return self.PvEnum(value)

    def get_current_value(self):
        return self.validate(self._pv.get())

    def set_target_value(self, value, hold=False):
        """Adjustable convention"""
        value = self.validate(value)
        if self._pv_set:
            tpv = self._pv_set
            if hasattr(self,'get2set'):
                value = self.get2set[value]
        else:
            tpv = self._pv
        changer = lambda value: tpv.put(value, wait=True)
        return Changer(
            target=value, parent=self, changer=changer, hold=hold, stopper=None
        )

    def __repr__(self):
        if not self.name:
            name = self.Id
        else:
            name = self.name
        cv = self.get_current_value()
        s = f"{name} (enum) at value: {cv}" + "\n"
        s += "{:<5}{:<5}{:<}\n".format("Num.", "Sel.", "Name")
        # s+= '_'*40+'\n'
        for name, val in self.PvEnum.__members__.items():
            if val == cv:
                sel = "x"
            else:
                sel = " "
            s += "{:>4}   {}  {}\n".format(val, sel, name)
        return s


class AdjustablePvString:
    def __init__(self, pvname, name=None, elog=None):
        self.name = name
        self.pvname = pvname
        self._pv = PV(pvname, connection_timeout=0.05)
        self._elog = elog
        self.alias = Alias(name, channel=self.pvname, channeltype="CA")

    def get_current_value(self):
        return self._pv.get()

    def set_target_value(self, value, hold=False):
        changer = lambda value: self._pv.put(bytes(value, "utf8"), wait=True)
        return Changer(
            target=value, parent=self, changer=changer, hold=hold, stopper=None
        )

    def __repr__(self):
        return str(self.get_current_value())

    def __call__(self, string=None):
        if not string is None:
            self.set_target_value(string)
        else:
            return self.get_current_value()
