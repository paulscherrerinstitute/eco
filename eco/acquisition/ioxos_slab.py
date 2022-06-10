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
        self._append(AdjustableFS, "/photonics/home/gac-slab/config/eco/reference_values/ioxos_daq_single_shots", name="save_single_shots", is_setting=True)
        self._done = False
        self._default_file_path = default_file_path

    def get_data(self, N_pulses=None):
        N_channels = 8
        if N_pulses > 10:
            N_blocks = N_pulses // 10
            N_samples = 10
        else:
            N_samples = N_pulses
            N_blocks = 1
        #self.ioxos.blocks(N_blocks)
        #self.ioxos.samples(N_samples)

        block_len = N_channels*N_samples
        meta_len = 12
        data_acc = np.ndarray((N_channels*N_pulses,))
        meta_acc = np.ndarray((N_blocks))
        self._m = 0

        def cb_getdata(pv=None, *args, **kwargs):
            data_acc[self._m*block_len:(self._m+1)*block_len] = kwargs["value"][meta_len:]
            self._m = self._m + 1
            if self._m == N_blocks:
                pv.clear_callbacks()
                self._done = True

        self._done = False
        self.ioxos.data.add_callback(callback=cb_getdata, pv=self.ioxos.data)
        self.ioxos.restart(1)
        while(True):
            sleep(.001)
            if self._done:
                break
        return data_acc.reshape((N_pulses, N_channels)).T

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

    def save_av(self, file_name, data, adjs_rb, adjs_name, N_pulses):
        print(adjs_name, "in saveav")
        filename_av = file_name.split("_step")[0] + ".txt"
        d_av = np.mean(data, axis=1)
        d_err = np.std(data, axis=1)/np.sqrt(N_pulses)
        d = np.hstack([adjs_rb, d_av, d_err])
        exists = os.path.isfile(filename_av)
        with open(filename_av, "a") as f:
            if exists:
                np.savetxt(f,[d])
            else:
                head = [f"{n}, " for n in adjs_name]
                head.extend([f"ch{n}, " for n in range(8)])
                head.extend([f"ch{n}_err, " for n in range(8)])
                header = "".join(head)
                np.savetxt(f,[d],header=header)

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
