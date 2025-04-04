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
from ..elements.adjustable import AdjustableFS


class EpicsDaq:
    def __init__(
        self,
        elog=None,
        name=None,
        channel_list=None,
    ):
        self.name = name
        self.default_file_path = AdjustableFS(
            f"/sf/bernina/config/eco/reference_values/{name}_default_file_path.json",
            default_value="~/data/",
            name="default_file_path",
        )
        self._elog = elog
        self.channels = {}
        self.pulse_id = PV("SLAAR11-LTIM01-EVR0:RX-PULSEID")
        self.channel_list = channel_list
        self.update_channels()

    @property
    def _default_file_path(self):
        return self.default_file_path()

    @_default_file_path.setter
    def _default_file_path(self, val):
        self.default_file_path(val)

    def update_channels(self):
        channels = self.channel_list.get_current_value()
        for channel in channels:
            if not (channel in self.channels.keys()):
                self.channels[channel] = PV(channel, auto_monitor=True)

    def h5(self, fina=None, channel_list=None, N_pulses=None, queue_size=100):
        if channel_list is None:
            channel_list = self.channel_list
        if not channel_list.get_current_value() == list(self.channels.keys()):
            self.update_channels()

        if os.path.isfile(fina):
            print("!!! File %s already exists, would you like to delete it?" % fina)
            if input("(y/n)") == "y":
                print("Deleting %s ." % fina)
                os.remove(fina)
            else:
                return

        data = {}
        counters = {}
        channels = self.channels
        for k, channel in channels.items():
            channelval = channel.value
            if type(channelval) == np.ndarray:
                shape = (N_pulses,) + channelval.shape
                dtype = channelval.dtype
            else:
                shape = (N_pulses,)
                dtype = type(channelval)
            data[k] = np.ndarray(shape, dtype=dtype)
            counters[k] = 0

        def cb_getdata(ch=None, k="", *args, **kwargs):
            data[k][counters[k]] = kwargs["value"]
            counters[k] = counters[k] + 1
            if counters[k] == N_pulses:
                ch.clear_callbacks()

        for k, channel in channels.items():
            channel.add_callback(callback=cb_getdata, ch=channel, k=k)
        while True:
            sleep(0.005)
            if np.mean(list(counters.values())) == N_pulses:
                break

        f = h5py.File(name=fina, mode="w")
        for k in channels.keys():
            dat = f.create_group(name=k)
            dat.create_dataset(name="data", data=data[k])
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

        for m, channel in enumerate(channels):
            channel.add_callback(callback=cb_getdata, ch=channel, m=m)
        while True:
            sleep(0.005)
            if np.mean(counters) == N_pulses:
                break

        f = h5py.File(name=fina, mode="w")
        for n, channel in enumerate(channel_list):
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
