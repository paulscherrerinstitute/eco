import subprocess
from threading import Thread
from epics import PV, ca
import time
from ..eco_epics import device
from ..eco_epics.device import Device
from .utilities import Changer
from ..aliases import Alias


_guiTypes = ["xdm"]

_status_messages = {
    -13: "invalid value (cannot convert to float).  Move not attempted.",
    -12: "target value outside soft limits.         Move not attempted.",
    -11: "drive PV is not connected:                Move not attempted.",
    -8: "move started, but timed-out.",
    -7: "move started, timed-out, but appears done.",
    -5: "move started, unexpected return value from PV.put()",
    -4: "move-with-wait finished, soft limit violation seen",
    -3: "move-with-wait finished, hard limit violation seen",
    0: "move-with-wait finish OK.",
    0: "move-without-wait executed, not cpmfirmed",
    1: "move-without-wait executed, move confirmed",
    3: "move-without-wait finished, hard limit violation seen",
    4: "move-without-wait finished, soft limit violation seen",
}


def _keywordChecker(kw_key_list_tups):
    for tkw, tkey, tlist in kw_key_list_tups:
        assert tkey in tlist, "Keyword %s should be one of %s" % (tkw, tlist)


class SmarActException(Exception):
    """raised to indicate a problem with a smartact"""

    def __init__(self, msg, *args):
        Exception.__init__(self, *args)
        self.msg = msg

    def __str__(self):
        return str(self.msg)


class SmarAct(Device):
    _extras = {"disabled": "_able.VAL"}
    _init_list = ("VAL", "DESC", "RTYP")
    _nonpvs = ("_prefix", "_pvs", "_delim", "_init", "_init_list", "_alias", "_extras")

    def __init__(self, name=None, timeout=3.0, record=None):
        if name is None:
            raise SmarActException("must supply SmarAct name")

        if name.endswith(".VAL"):
            name = name[:-4]
        if name.endswith("."):
            name = name[:-1]

        self._prefix = name
        self._record = record
        self._callbacks = {}

        device.Device.__init__(
            self, name, delim=".", attrs=self._init_list, timeout=timeout
        )


#        for key, val in self._extras.items():
#            pvname = "%s%s" % (name, val)
#            self.add_pv(pvname, attr=key)

# self.put('disabled', 0)


class SmarActRecord:
    def __init__(
        self,
        Id,
        name=None,
        elog=None,
        alias_fields={"readback": "MOTRBV", "homed": "GET_HOMED"},
    ):

        self.Id = Id
        self._device = Device(Id, delim=":")
        self._drive = SmarAct(Id + ":DRIVE")
        self._rbv = SmarAct(Id + ":MOTRBV")
        self._hlm = SmarAct(Id + ":HLM")
        self._llm = SmarAct(Id + ":LLM")
        self._statusstg = SmarAct(Id + ":STATUS")
        self._status = []
        self._set_pos = SmarAct(Id + ":SET_POS")
        self._stop = SmarAct(Id + ":STOP")
        self._hold = SmarAct(Id + ":HOLD")
        self._twv = SmarAct(Id + ":TWV")
        self._elog = elog
        self.name = name
        self.units = self._drive.get("EGU")
        self.alias = Alias(name)
        for an, af in alias_fields.items():
            self.alias.append(
                Alias(an, channel=".".join([self.Id, af]), channeltype="CA")
            )

    # Conventional methods and properties for all Adjustable objects
    def set_target_value(self, value, hold=False, check=True):
        """Adjustable convention"""

        def changer(value):
            self._status = self.move(value, ignore_limits=(not check), wait=True)
            self._status_message = _status_messages[self._status]
            # if not self._status == 0:
            # print(self._status_message)

        # mover = lambda value: self.move(\
        #        value, ignore_limits=(not check),
        #        wait=True)
        return Changer(
            target=value,
            parent=self,
            changer=changer,
            hold=hold,
            stopper=self._stop.put("PROC", 1),
        )

    def stop(self):
        """Adjustable convention"""
        try:
            self._currentChange.stop()
        except:
            self._stop.put("VAL", 1)
        pass

    def within_limits(self, val):
        """returns whether a value for a motor is within drive limits"""
        return val <= self._hlm.get("VAL") and val >= self._llm.get("VAL")

    def move(
        self,
        val,
        relative=False,
        wait=False,
        timeout=300.0,
        ignore_limits=False,
        confirm_move=False,
    ):
        """moves smaract drive to position

        arguments:
        ==========
         val            value to move to (float) [Must be provided]
         relative       move relative to current position    (T/F) [F]
         wait           whether to wait for move to complete (T/F) [F]
         ignore_limits  try move without regard to limits    (T/F) [F]
         confirm_move   try to confirm that move has begun   (T/F) [F]
         timeout        max time for move to complete (in seconds) [300]

        return values:
          -13 : invalid value (cannot convert to float).  Move not attempted.
          -12 : target value outside soft limits.         Move not attempted.
          -11 : drive PV is not connected:                Move not attempted.
           -8 : move started, but timed-out.
           -7 : move started, timed-out, but appears done.
           -5 : move started, unexpected return value from PV.put()
           -4 : move-with-wait finished, soft limit violation seen
           -3 : move-with-wait finished, hard limit violation seen
            0 : move-with-wait finish OK.
            0 : move-without-wait executed, not cpmfirmed
            1 : move-without-wait executed, move confirmed
            3 : move-without-wait finished, hard limit violation seen
            4 : move-without-wait finished, soft limit violation seen

        """
        NONFLOAT, OUTSIDE_LIMITS, UNCONNECTED = -13, -12, -11
        TIMEOUT = -8
        UNKNOWN_ERROR = -5
        DONE_OK = 0
        MOVE_BEGUN, MOVE_BEGUN_CONFIRMED = 0, 1
        try:
            val = float(val)
        except TypeError:
            return NONFLOAT

        if relative:
            val += self._drive.get("VAL")

        # Check for limit violations
        if not ignore_limits:
            if not self.within_limits(val):
                return OUTSIDE_LIMITS

        stat = self._drive.put("VAL", val, wait=wait, timeout=timeout)
        if stat is None:
            return UNCONNECTED

        if wait and stat == -1:
            return TIMEOUT

        if 1 == stat:
            s0 = self._statusstg.get("VAL")
            s1 = s0
            t0 = time.time()
            t1 = t0 + min(10.0, timeout)  # should be moving by now
            thold = self._hold.get("VAL") * 0.001 + t0
            tout = t0 + timeout
            if wait or confirm_move:
                while time.time() <= thold and s1 == 3:
                    ca.poll(evt=1.0e-2)
                    s1 = self._statusstg.get("VAL")
                while time.time() <= t1 and s1 == 0:
                    ca.poll(evt=1.0e-2)
                    s1 = self._statusstg.get("VAL")
                if s1 == 4:
                    if wait:
                        while time.time() <= tout and s1 == 4:
                            ca.poll(evt=1.0e-2)
                            s1 = self._statusstg.get("VAL")
                        if s1 == 3 or s1 == 4:
                            if time.time() > tout:
                                return TIMEOUT
                            else:
                                twv = abs(self._twv.get("VAL"))
                                while (
                                    s1 == 3
                                    and time.time() <= tout
                                    and abs(self._rbv.get("VAL") - val) >= twv
                                ):
                                    ca.poll(evt=1.0e-2)
                                return DONE_OK
                    else:
                        return MOVE_BEGUN_CONFIRMED
                elif time.time() > tout:
                    return TIMEOUT
                else:
                    return UNKNOWN_ERROR
            else:
                return MOVE_BEGUN
        return UNKNOWN_ERROR

    def get_current_value(self, readback=True):
        if readback:
            return self._rbv.get("VAL")
        else:
            return self._drive.get("VAL")

    def set_current_value(self, value):
        return self._set_pos.put("VAL", value)

    def get_precision(self):
        """Adjustable convention"""
        pass

    def set_precision(self):
        """Adjustable convention"""
        pass

    precision = property(get_precision, set_precision)

    def set_speed(self):
        """Adjustable convention"""
        pass

    def get_speed(self):
        """Adjustable convention"""
        pass

    def set_speedMax(self):
        """Adjustable convention"""
        pass

    def get_moveDone(self):
        pass

    def set_limits(self, values, posType="user", relative_to_present=False):
        """Adjustable convention"""
        if relative_to_present:
            v = self.get_current_value()
            values = [v - values[0], v - values[1]]
        self._llm.put("VAL", values[0])
        self._hlm.put("VAL", values[1])

    def get_limits(self, posType="user"):
        """Adjustable convention"""
        return self._llm.get("VAL"), self._hlm.get("VAL")

    def gui(self, guiType="xdm"):
        """Adjustable convention"""
        cmd = ["caqtdm", "-macro"]

        for i in range(len(self.Id) - 1):
            if self.Id[-i - 1].isnumeric() is False:
                M = self.Id[-i:]
                P = self.Id[:-i]
                print(P, M)
                break

        cmd.append('"P=%s,M=%s"' % (P, M))
        #        #cmd.append('/sf/common/config/qt/motorx_more.ui')
        cmd.append("/sf/common/config/qt/ESB_MX_SmarAct_mot_exp.ui")
        #        #os.system(' '.join(cmd))
        return subprocess.Popen(" ".join(cmd), shell=True)

    def mv(self, value):
        self._currentChange = self.set_target_value(value)

    def wm(self, *args, **kwargs):
        return self.get_current_value(*args, **kwargs)

    def mvr(self, value, *args, **kwargs):
        startvalue = self.get_current_value(readback=True, *args, **kwargs)
        self._currentChange = self.set_target_value(value + startvalue, *args, **kwargs)

    def wait(self):
        self._currentChange.wait()

    # return string with motor value as variable representation
    def __str__(self):
        return "SmarAct is at %s" % (self.wm())
        # return "SmarAct is at %s %s"%(self.wm(),self.units)

    def __repr__(self):
        return self.__str__()

    def __call__(self, value):
        self._currentChange = self.set_target_value(value)


class SmarActDevice(SmarActRecord):
    def __init__(self, Id, alias_namespace=None):
        SmarActRecord.__init__(self, Id)


#        self.Id = Id
#
#        self.x = SmarActRecord(Id+':DRIVE')


class SmarActStage:
    def __init__(self, axes, name):
        self._keys = axes.keys()
        for axis in self._keys:
            self.__dict__[axis] = axes[axis]
        self.name = name

    def __str__(self):
        return "SmarAct positions\n%s" % "\n".join(
            ["%s: %s" % (key, self.__dict__[key].wm()) for key in self._keys]
        )

    def __repr__(self):
        return str({key: self.__dict__[key].wm() for key in self._keys})


class Changer_old:
    def __init__(self, target=None, parent=None, mover=None, hold=True, stopper=None):
        self.target = target
        self._mover = mover
        self._stopper = stopper
        self._thread = Thread(target=self._mover, args=(target,))
        if not hold:
            self._thread.start()

    def wait(self):
        self._thread.join()

    def start(self):
        self._thread.start()

    def status(self):
        if self._thread.ident is None:
            return "waiting"
        else:
            if self._isAlive:
                return "changing"
            else:
                return "done"

    def stop(self):
        self._stopper()
