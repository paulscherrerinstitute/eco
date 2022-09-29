import numpy as np
import h5py
from epics import PV
import os
import datetime
from threading import Thread
from time import sleep
from pathlib import Path
from .utilities import Acquisition
import time
from eco.elements.assembly import Assembly
from eco.elements.adjustable import AdjustableFS
from eco.epics.adjustable import AdjustablePv, AdjustablePvEnum

class IoxosChannel(Assembly):
    def __init__(
        self,
        pvbase = "SLAB-LSCP1-ESB1",
        name=None,
        ch=None,

    ):
        super().__init__(name=name)
        self.pvbase = pvbase
        self._append(AdjustablePv, self.pvbase + f":CH{ch}:BSTART_NEW", name = "bg_start", is_setting=True)
        self._append(AdjustablePv, self.pvbase + f":CH{ch}:BEND_NEW", name = "bg_end", is_setting=True)
        self._append(AdjustablePv, self.pvbase + f":CH{ch}:START_NEW", name = "sig_start", is_setting=True)
        self._append(AdjustablePv, self.pvbase + f":CH{ch}:END_NEW", name = "sig_end", is_setting=True)
        self._append(AdjustablePvEnum, self.pvbase + f":BOX_STAT{ch}", name = "boxcar_calculation", is_setting=True)
        self._append(AdjustableFS, f"/sf/slab/config/eco/reference_values/ioxos_{name}_chopper_ch", name="chopper_ch", is_setting=True, default_value=0)
        self._append(AdjustableFS, f"/sf/slab/config/eco/reference_values/ioxos_{name}_chopper_thr", name="chopper_thr", is_setting=True, default_value=1000)
        self._append(AdjustableFS, f"/sf/slab/config/eco/reference_values/ioxos_{name}_chopper_inv", name="chopper_inv", is_setting=True, default_value=True)

class Slab_Ioxos(Assembly):
    def __init__(
        self,
        name=None,
        pvbase = "SLAB-LSCP1-ESB1",
    ):
        super().__init__(name=name)
        self.pvbase= pvbase        
        self._append(AdjustablePv, self.pvbase + ":BOX_RESTART.PROC", name="restart", is_setting=False)
        self._append(AdjustablePv, self.pvbase + ":BOX_SAMS_IN_ARRAY", name="samples", is_setting=True)
        self._append(AdjustablePv, self.pvbase + ":BOX_BLOCKS_TO_SEND", name="blocks", is_setting=True)
        self._append(AdjustablePvEnum, self.pvbase + ":BOX_INARRAY", name="active_channels", is_setting=True)
        self._append(AdjustablePv, self.pvbase + ":BOX_FREQ", name="trigger_rate", is_setting=True)
        self.samples(10)
        self.blocks(0)
        self.restart(1)
        self.active_channels(7)
        self.data = PV("SLAB-LSCP1-ESB1:BOX_DATA", auto_monitor=True)
        for ch in range(8):
            self._append(IoxosChannel, pvbase=self.pvbase, name=f"ch{ch}", ch=ch, is_setting=False, is_display=False,)

class Slab_Ioxos_Daq(Assembly):
    def __init__(
        self,
        default_file_path="",
        name=None,
        ioxos = None,
    ):
        super().__init__(name=name)
        self.ioxos = ioxos
        self._append(AdjustableFS, "/sf/slab/config/eco/reference_values/ioxos_daq_single_shots", name="save_single_shots", is_setting=True)
        self._done = False
        self._default_file_path = default_file_path
        self._N_acqs = 0
        self._data = np.zeros((0,))
        self._meta_len = 12

        def cb_get_data(*args, **kwargs):
            if self._N_acqs > 0:
                d = kwargs["value"][self._meta_len:]
                idx0 = self._data.shape[0]-self._N_acqs*d.shape[0]
                idx1 = self._data.shape[0]-(self._N_acqs-1)*d.shape[0]
                self._data[idx0:idx1] = d
                self._N_acqs = self._N_acqs - 1
        self.ioxos.data.add_callback(callback = cb_get_data)

    def get_data(self, N_pulses=None):
        
        N_channels = 8
        if N_pulses > 10:
            N_acqs = N_pulses // 10
        else:
            N_pulses=10
            N_acqs = 1
        self._data=np.zeros((N_channels*N_pulses))
        self._N_acqs = N_acqs
        while(True):
            if self._N_acqs == 0:
                break
            sleep(.001)
        return self._data.reshape((N_pulses, N_channels)).T

    def save_single(self, file_name, data):
        if os.path.isfile(file_name):
            print(f"!!! File {file_name} already exists, would you like to delete it?")
            if input("(y/n)") == "y":
                print(f"Deleting {file_name} .")
                os.remove(file_name)
            else:
                return
        N_channels = data.shape[0]
        d = {f"ch{n}": data[n] for n in range(N_channels)}
        np.savez_compressed(file_name, **d)
        fp = Path(file_name)
        fp.chmod(0o775)

    def save_av(self, file_name, data, adjs_rb, adjs_name, N_pulses):
        chopper_chs = [self.ioxos.__dict__[f"ch{n}"].chopper_ch() for n in range(8)]
        chopper_thrs = [self.ioxos.__dict__[f"ch{n}"].chopper_thr() for n in range(8)]
        chopper_invs = [self.ioxos.__dict__[f"ch{n}"].chopper_inv() for n in range(8)]
        w = np.array([data[ch]<thr if inv else data[ch]>thr for ch, thr, inv in zip(chopper_chs, chopper_thrs, chopper_invs)])
        d_av_on = np.mean(data, axis=1, where=w)
        d_av_off = np.mean(data, axis=1, where=~w)
        d_std_on = np.std(data, axis=1, where=w)
        d_std_off = np.std(data, axis=1, where=~w)
        d_npulses_on = np.sum(w, axis=1)
        d_npulses_off = np.sum(~w, axis=1)
        filename_av = file_name.split("_step")[0] + ".txt"
        d = np.hstack([adjs_rb, d_av_on, d_av_off, d_std_on, d_std_off, d_npulses_on, d_npulses_off])
        exists = os.path.isfile(filename_av)
        with open(filename_av, "a") as f:
            if exists:
                np.savetxt(f,[d])
            else:
                head = [f"{n}, " for n in adjs_name]
                head.extend([f"ch{n}_on, " for n in range(8)])
                head.extend([f"ch{n}_off, " for n in range(8)])
                head.extend([f"ch{n}_on_std, " for n in range(8)])
                head.extend([f"ch{n}_off_std, " for n in range(8)])
                head.extend([f"ch{n}_on_npulses, " for n in range(8)])
                head.extend([f"ch{n}_off_npulses, " for n in range(8)])
                header = "".join(head)
                np.savetxt(f,[d],header=header)
                fp = Path(filename_av)
                fp.chmod(0o775)

    def acquire(self, file_name=None, N_pulses=100, adjs_rb = [], adjs_name=[], default_path=True):

        file_name += ".npz"
        if default_path:
            file_name = self._default_file_path + file_name
        data_dir = Path(os.path.dirname(file_name))

        if not data_dir.exists():
            print(
                f"Path {data_dir.absolute().as_posix()} does not exist, will try to create it..."
            )
            data_dir.mkdir(parents=True)
            print(f"Tried to create {data_dir.absolute().as_posix()}")
            data_dir.chmod(0o775)
            print(f"Tried to change permissions to 775")

        def acquire():
            d = self.get_data(N_pulses = N_pulses)
            self.save_av(file_name, d, adjs_rb, adjs_name, N_pulses)
            if self.save_single_shots():
                self.save_single(file_name=file_name, data=d)

        return Acquisition(
            acquire=acquire,
            acquisition_kwargs={"file_names": [file_name], "N_pulses": N_pulses, "adjs_rb": adjs_rb, "adjs_name": adjs_name},
            hold=False,
        )

    def wait_done(self):
        self.check_running()
        self.check_still_running()


class Epicstools:
    def __init__(
        self,
        default_channel_list={"listname": []},
        default_file_path="%s",
        elog=None,
        name=None,
        channel_list=None,
    ):
        self.name = name
        self._default_file_path = default_file_path
        self._default_channel_list = default_channel_list
        self._elog = elog
        self.channels = []
        self.pulse_id = PV("SLAAR11-LTIM01-EVR0:RX-PULSEID")

        if not channel_list:

            print("No channels specified, using all lists instead.")
            channel_list = []
            for tlist in self._default_channel_list.values():
                channel_list.extend(tlist)
        else:
            self.channel_list = channel_list
        for channel in self.channel_list:
            self.channels.append(PV(channel, auto_monitor=True))

    def h5(self, fina=None, channel_list=None, N_pulses=None, queue_size=100):
        channel_list = self.channel_list

        if os.path.isfile(fina):
            print("!!! File %s already exists, would you like to delete it?" % fina)
            if input("(y/n)") == "y":
                print("Deleting %s ." % fina)
                os.remove(fina)
            else:
                return

        data = []
        counters = []
        channels = self.channels
        for channel in channels:
            channelval = channel.value
            if type(channelval) == np.ndarray:
                shape = (N_pulses,) + channelval.shape
                dtype = channelval.dtype
            else:
                shape = (N_pulses,)
                dtype = type(channelval)
            data.append(np.ndarray(shape, dtype=dtype))
            counters.append(0)

        def cb_getdata(ch=None, m=0, *args, **kwargs):
            data[m][counters[m]] = kwargs["value"]
            counters[m] = counters[m] + 1
            if counters[m] == N_pulses:
                ch.clear_callbacks()

        for (m, channel) in enumerate(channels):
            channel.add_callback(callback=cb_getdata, ch=channel, m=m)
        while True:
            sleep(0.005)
            if np.mean(counters) == N_pulses:
                break

        f = h5py.File(name=fina, mode="w")
        for (n, channel) in enumerate(channel_list):
            dat = f.create_group(name=channel)
            dat.create_dataset(name="data", data=data[n])
            dat.create_dataset(
                name="pulse_id", data=np.arange(N_pulses) + round(time.time() * 100)
            )
        return data

    def acquire(self, file_name=None, Npulses=100, default_path=True):
        file_name += ".h5"
        if default_path:
            file_name = self._default_file_path + file_name
        data_dir = Path(os.path.dirname(file_name))

        if not data_dir.exists():
            print(
                f"Path {data_dir.absolute().as_posix()} does not exist, will try to create it..."
            )
            data_dir.mkdir(parents=True)
            print(f"Tried to create {data_dir.absolute().as_posix()}")
            data_dir.chmod(0o775)
            print(f"Tried to change permissions to 775")

        def acquire():
            self.h5(fina=file_name, N_pulses=Npulses)

        return Acquisition(
            acquire=acquire,
            acquisition_kwargs={"file_names": [file_name], "Npulses": Npulses},
            hold=False,
        )

    def wait_done(self):
        self.check_running()
        self.check_still_running()
