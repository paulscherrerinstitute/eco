from epics import caget_many
from ..elements.adjustable import AdjustableMemory, AdjustableVirtual
from ..epics.adjustable import AdjustablePv, AdjustablePvEnum, AdjustablePvString
from ..epics.detector import DetectorPvData, DetectorPvDataStream
from ..detector.detectors_psi import DetectorBsStream
from eco.epics.utilities_epics import EpicsString
import logging
from ..elements.assembly import Assembly
from tabulate import tabulate

logging.getLogger("cta_lib").setLevel(logging.WARNING)


class TimingSystem(Assembly):
    """This is a wrapper object for the global timing system at SwissFEL"""

    def __init__(self, pv_master=None, pv_pulse_id=None, pv_eventset=None, name=None):
        super().__init__(name=name)
        self._append(MasterEventSystem, pv_master, name="event_master", is_display=True)
        # self._append(DetectorPvDataStream, pv_pulse_id, name="pulse_id")
        self._append(
            DetectorBsStream, "pulse_id", cachannel=pv_pulse_id, name="pulse_id"
        )
        self._append(DetectorBsStream, "lab_time", cachannel=None, name="lab_time")

        if pv_eventset:
            self._append(DetectorBsStream, pv_eventset, cachannel=None, name="eventset")


# EVR output mapping
evr_mapping = {
    0: "Pulser 0",
    1: "Pulser 1",
    2: "Pulser 2",
    3: "Pulser 3",
    4: "Pulser 4",
    5: "Pulser 5",
    6: "Pulser 6",
    7: "Pulser 7",
    8: "Pulser 8",
    9: "Pulser 9",
    10: "Pulser 10",
    11: "Pulser 11",
    12: "Pulser 12",
    13: "Pulser 13",
    14: "Pulser 14",
    15: "Pulser 15",
    16: "Pulser 16",
    17: "Pulser 17",
    18: "Pulser 18",
    19: "Pulser 19",
    20: "Pulser 20",
    21: "Pulser 21",
    22: "Pulser 22",
    23: "Pulser 23",
    32: "Distributed bus bit 0",
    33: "Distributed bus bit 1",
    34: "Distributed bus bit 2",
    35: "Distributed bus bit 3",
    36: "Distributed bus bit 4",
    37: "Distributed bus bit 5",
    38: "Distributed bus bit 6",
    39: "Distributed bus bit 7",
    40: "Prescaler 0",
    41: "Prescaler 1",
    42: "Prescaler 2",
    62: "Logic High",
    63: "Logic low",
}


# temporary mapping of Ids to codes, be aware of changes!
eventcodes = [
    1,
    2,
    3,
    4,
    5,
    0,
    6,
    7,
    8,
    12,
    0,
    11,
    9,
    10,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    26,
    27,
    28,
    29,
    30,
    31,
    32,
    33,
    34,
    35,
    36,
    37,
    38,
    39,
    40,
    41,
    42,
    43,
    44,
    45,
    46,
    47,
    48,
    49,
    50,
]

event_code_delays_fix = {
    200: 100,
    201: 107,
    202: 114,
    203: 121,
    204: 128,
    205: 135,
    206: 142,
    207: 149,
    208: 156,
    209: 163,
    210: 170,
    211: 177,
    212: 184,
    213: 191,
    214: 198,
    215: 205,
    216: 212,
    217: 219,
    218: 226,
    219: 233,
}

tim_tick = 7e-9


class MasterEventCode(Assembly):
    def __init__(self, pvname, slot_number, name=None):
        super().__init__(name=name)
        self.pvname = pvname
        self._slot_number = slot_number
        self._append(
            DetectorPvData,
            f"{self.pvname}:Evt-{slot_number}-Code-SP",
            name="code_number",
        )
        self._append(
            DetectorPvData, f"{self.pvname}:Evt-{slot_number}-Delay-RB", name="delay"
        )
        self._append(
            DetectorPvData, f"{self.pvname}:Evt-{slot_number}-Freq-I", name="frequency"
        )
        self._append(
            AdjustablePvString,
            f"{self.pvname}:Evt-{slot_number}.DESC",
            name="description",
        )


class MasterEventCodeFix(Assembly):
    def __init__(self, code_number, delay, description="fixed event code", name=None):
        super().__init__(name=name)
        self._append(AdjustableMemory, delay, name="code_number")
        self._append(AdjustableMemory, delay, name="delay")
        self._append(AdjustableMemory, None, name="frequency")
        self._append(AdjustableMemory, description, name="description")


class MasterEventSystem(Assembly):
    def __init__(self, pvname="SIN-TIMAST-TMA", name=None):
        super().__init__(name=name)
        self.pvname = pvname
        slots, codes = self._get_slot_codes()
        self.event_codes = {}
        for slot, code in zip(slots, codes):
            self._append(
                MasterEventCode,
                self.pvname,
                slot,
                name=f"code{code:03d}",
                is_display="recursive",
            )
            self.event_codes[code] = self.__dict__[f"code{code:03d}"]
        for code, delay in event_code_delays_fix.items():
            self._append(
                MasterEventCodeFix,
                code,
                delay,
                "fix delay CTA sequencer code",
                name=f"code{code:03d}",
                is_display="recursive",
            )
            self.event_codes[code] = self.__dict__[f"code{code:03d}"]

    def _get_slot_codes(self, slots=range(1, 257)):
        pvs = [f"{self.pvname}:Evt-{slot}-Code-SP" for slot in slots]
        codes = caget_many(pvs)

        slots_out = []
        codes_out = []
        for s, c in zip(slots, codes):
            if not c == None:
                if c in codes_out:
                    # print(f"Code {c} exists multiple times!")
                    continue
                slots_out.append(s)
                codes_out.append(c)

        codes_out, slots_out = zip(*sorted(zip(codes_out, slots_out)))
        return slots_out, codes_out

    def status(self, code=None, printit=True):
        if code == None:
            code = self.event_codes.keys()
        else:
            try:
                iter(code)
            except TypeError:
                code = [code]

        o = []
        for cod in code:
            tc = self.__dict__[f"code{cod:03d}"]
            o.append([cod, tc.delay(), tc.frequency(), tc.description()])
        s = tabulate(o, ["Code", "Delay / us", "Freq. / Hz", "Description"], "simple")
        if printit:
            print(s)
        else:
            return s

    def __repr__(self):
        return self.status(printit=False)

class EvrSequencer(Assembly):
    def __init__(self, pv_base, name=None):
        super().__init__(name=name)
        try:
            self._append(AdjustablePvEnum, pv_base + ':SEQ_SOURCE', name='source', is_display=True, is_setting=True)
            self._append(AdjustablePvEnum, pv_base + ':SEQ_SNUMPD', name='pulser_number', is_display=True, is_setting=True)
            self._append(DetectorPvData, pv_base + ':SEQ_RUNNING', name='is_running', is_display=True)
            self._append(AdjustablePvEnum, pv_base + ':Seq-Ena-Sel', name='enabled', is_display=True, is_setting=True)
            self._append(DetectorPvData, pv_base + ':SEQ_SELECT_FREQ', name='frequency', is_display=True)
        except:
            print(f'The evr sequencer of {pv_base} is likely old type')
            self._append(AdjustableMemory, None, name='frequency', is_display=True)
        
        self._append(AdjustablePvEnum, pv_base + ':Seq-RunMode-Sel', name='mode', is_display=True, is_setting=True)
        
        
        self._append(AdjustablePv, pv_base + ':SEQ_DELAY', name='delay', is_display=True, is_setting=True)
        self._append(AdjustablePv, pv_base + ':SEQ_REPS', name='repetitions', is_display=True, is_setting=True)
        self._append(AdjustablePv, pv_base + ':SEQ_MULTIPLIER', name='freq_multiplier', is_display=True, is_setting=True)


class EvrPulser(Assembly):
    def __init__(self, pv_base, event_master, parent_evr=None, name=None):
        super().__init__(name=name)
        self.pv_base = pv_base
        self._event_master = event_master
        self._parent_evr = parent_evr

        self._append(
            AdjustablePvString, pv_base + "-Name-I", name="description", is_display=True
        )
        self._append(
            AdjustablePvEnum,
            f"{self.pv_base}-Polarity-Sel",
            name="polarity",
            is_setting=True,
        )
        self._append(
            AdjustablePvEnum, f"{self.pv_base}-Ena-Sel", name="enable", is_setting=True
        )
        self._append(
            AdjustablePv,
            f"{self.pv_base}-Evt-Trig0-SP",
            name="eventcode",
            is_setting=True,
        )
        self._append(
            AdjustablePv,
            f"{self.pv_base}-Evt-Set0-SP",
            name="event_set",
            is_setting=True,
        )
        self._append(
            AdjustablePv,
            f"{self.pv_base}-Evt-Reset0-SP",
            name="event_reset",
            is_setting=False,
        )

        self._append(
            AdjustablePv,
            f"{self.pv_base}-Delay-SP",
            pvreadbackname=f"{self.pv_base}-Delay-RB",
            name="delay_pulser",
            is_setting=True,
        )
        self._append(
            AdjustablePv,
            f"{self.pv_base}-Width-SP",
            pvreadbackname=f"{self.pv_base}-Width-RB",
            name="width",
            is_setting=True,
        )
        self.description = EpicsString(pv_base + "-Name-I")

        if self._eventcode is not None:
            self._append(
                AdjustableVirtual,
                [self._eventcode.frequency],
                lambda x: x,
                lambda x: x,
                name="frequency",
            )
            self._append(
                AdjustableVirtual,
                [self._eventcode.delay],
                lambda x: x,
                lambda x: x,
                name="delay_eventcode",
            )
            self._append(
                AdjustableVirtual,
                [self.delay_pulser],
                lambda tp: self.delay_eventcode.get_current_value() + tp,
                lambda x: x - self.delay_eventcode.get_current_value(),
                name="delay",
            )
        else:
            print(f"Error initializing pulser {self.name} of EVR {self.pv_base}: Event code {self.eventcode.get_current_value()} is missing in Timing Master")

    @property
    def _eventcode(self):
        if self.eventcode.get_current_value() == 27:
            return self._parent_evr.sequencer
        else:
            try:
                return self._event_master.event_codes[self.eventcode.get_current_value()]
            except KeyError:
                return None


class DummyPulser(Assembly):
    def __init__(self, name="dummy"):
        super().__init__(name=name)
        self._append(AdjustableMemory, None, name="delay")
        self._append(AdjustableMemory, None, name="delay_pulser")
        self._append(AdjustableMemory, None, name="delay_eventcode")
        self._append(AdjustableMemory, None, name="eventcode")
        self._append(AdjustableMemory, None, name="frequency")
        self._append(AdjustableMemory, None, name="enable")
        self._append(AdjustableMemory, None, name="polarity")
        self._append(AdjustableMemory, None, name="width")


class EvrOutput(Assembly):
    def __init__(self, pv_base, pulsers=None, name=None):
        super().__init__(name=name)
        self.pv_base = pv_base
        self._pulsers = pulsers
        # self._update_connected_pulsers()
        self._append(
            AdjustablePvString, pv_base + "-Name-I", name="description", is_display=True
        )
        self._append(
            AdjustablePvEnum, f"{self.pv_base}-Ena-SP", name="enable", is_setting=True
        )
        # self._append(
        # PvEnum,
        # f"{self.pv_base}_SOURCE",
        # name="sourceA",
        # is_setting=True,
        # )
        self._append(
            AdjustablePv,
            f"{self.pv_base}-Src-Pulse-SP",
            f"{self.pv_base}-Src-Pulse-RB",
            name="pulserA_number",
            is_setting=True,
        )
        self._append(
            AdjustableVirtual,
            [self.pulserA.delay],
            lambda x: x,
            lambda x: x,
            name="pulserA_delay",
        )
        self._append(
            AdjustableVirtual,
            [self.pulserA.delay_pulser],
            lambda x: x,
            lambda x: x,
            name="pulserA_delay_pulser",
        )
        self._append(
            AdjustableVirtual,
            [self.pulserA.delay_eventcode],
            lambda x: x,
            lambda x: x,
            name="pulserA_delay_eventcode",
        )
        self._append(
            AdjustableVirtual,
            [self.pulserA.eventcode],
            lambda x: x,
            lambda x: x,
            name="pulserA_eventcode",
        )
        self._append(
            AdjustableVirtual,
            [self.pulserA.frequency],
            lambda x: x,
            lambda x: x,
            name="pulserA_frequency",
        )
        self._append(
            AdjustableVirtual,
            [self.pulserA.enable],
            lambda x: x,
            lambda x: x,
            name="pulserA_enable",
        )
        self._append(
            AdjustableVirtual,
            [self.pulserA.polarity],
            lambda x: x,
            lambda x: x,
            name="pulserA_polarity",
        )
        self._append(
            AdjustableVirtual,
            [self.pulserA.width],
            lambda x: x,
            lambda x: x,
            name="pulserA_width",
        )
        # self._append(
        # PvEnum,
        # f"{self.pv_base}_SOURCE2",
        # name="sourceB",
        # is_setting=True,
        # )

        self._append(
            AdjustablePv,
            f"{self.pv_base}-Src2-Pulse-SP",
            f"{self.pv_base}-Src2-Pulse-RB",
            name="pulserB_number",
            is_setting=True,
        )
        self._append(
            AdjustableVirtual,
            [self.pulserB.delay],
            lambda x: x,
            lambda x: x,
            name="pulserB_delay",
        )
        self._append(
            AdjustableVirtual,
            [self.pulserB.delay_pulser],
            lambda x: x,
            lambda x: x,
            name="pulserB_delay_pulser",
        )
        self._append(
            AdjustableVirtual,
            [self.pulserB.delay_eventcode],
            lambda x: x,
            lambda x: x,
            name="pulserB_delay_eventcode",
        )
        self._append(
            AdjustableVirtual,
            [self.pulserB.eventcode],
            lambda x: x,
            lambda x: x,
            name="pulserB_eventcode",
        )
        self._append(
            AdjustableVirtual,
            [self.pulserB.frequency],
            lambda x: x,
            lambda x: x,
            name="pulserB_frequency",
        )
        self._append(
            AdjustableVirtual,
            [self.pulserB.enable],
            lambda x: x,
            lambda x: x,
            name="pulserB_enable",
        )
        self._append(
            AdjustableVirtual,
            [self.pulserB.polarity],
            lambda x: x,
            lambda x: x,
            name="pulserB_polarity",
        )
        self._append(
            AdjustableVirtual,
            [self.pulserB.width],
            lambda x: x,
            lambda x: x,
            name="pulserB_width",
        )

    @property
    def pulserA(self):
        try:
            return self._pulsers[self.pulserA_number.get_current_value()]
        except (IndexError, TypeError):
            return DummyPulser()

    @property
    def pulserB(self):
        try:
            return self._pulsers[self.pulserA_number.get_current_value()]
        except (IndexError, TypeError):
            return DummyPulser()


class EventReceiver(Assembly):
    def __init__(
        self,
        pvname,
        event_master,
        n_pulsers=24,
        n_output_front=8,
        n_output_rear=16,
        name=None,
    ):
        super().__init__(name=name)
        self.pvname = pvname

        self._append(EvrSequencer,self.pvname,name='sequencer', is_display=True, is_setting=True)
        

        pulsers = []
        for n in range(n_pulsers):
            self._append(
                EvrPulser,
                f"{self.pvname}:Pul{n}",
                event_master,
                parent_evr=self,
                name=f"pulser{n}",
                is_setting=True,
                is_display=False,
            )
            pulsers.append(self.__dict__[f"pulser{n}"])
        self.pulsers = tuple(pulsers)
        outputs = []
        for n in range(n_output_front):
            self._append(
                EvrOutput,
                f"{self.pvname}:FrontUnivOut{n}",
                pulsers=pulsers,
                name=f"output_front{n}",
                is_setting=True,
                is_display="recursive",
            )
            outputs.append(self.__dict__[f"output_front{n}"])
        for n in range(n_output_rear):
            self._append(
                EvrOutput,
                f"{self.pvname}:RearUniv{n}",
                pulsers=pulsers,
                name=f"output_rear{n}",
                is_setting=True,
                is_display="recursive",
            )
            outputs.append(self.__dict__[f"output_rear{n}"])
        # for to in outputs:
        #     to._pulsers = self.pulsers
        self.outputs = outputs

        

        self._append(
            AdjustablePv,
            self.pvname + ":SYSRESET",
            is_status=False,
            is_setting=False,
            name="restart_ioc_pv",
        )

    def restart_ioc(self):
        self.restart_ioc_pv.set_target_value(1)

    def gui(self):
        dev = self.pvname.split("-")[-1]
        sys = self.pvname[: -(len(dev) + 1)]
        ioc = self.pvname
        self._run_cmd(
            f"caqtdm -noMsg  -macro IOC={ioc},SYS={sys},DEVICE={dev}  /sf/laser/config/qt/S_LAS-TMAIN.ui"
        )

    def status(self, printit=True):
        o = []
        for output in self.outputs:
            o.append(
                [
                    output.name,
                    output.description(),
                    output.enable(),
                    f"{output.pulserA_number()}/{output.pulserA_number()}",
                    f"{output.pulserA_frequency()}/{output.pulserA_frequency()}",
                    f"{output.pulserA_eventcode()}/{output.pulserA_eventcode()}",
                ]
            )
        s = tabulate(
            o,
            ["Output name", "Description", "On", "Pulsers", "Freqs. / Hz", "EvtCds"],
            "simple",
        )
        if printit:
            print(s)
        else:
            return s

    def __repr__(self):
        return self.status(printit=False)
