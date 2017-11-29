from bsread import Source
from bsread.h5 import receive
from bsread.avail import dispatcher
import zmq
import os
import data_api as api
import datetime
from threading import Thread

from .utilities import Acquisition

class BStools:
    def __init__(self,
            default_channel_list={'listname':[]},
            default_file_path='%s',
            elog=None):
        self._default_file_path = default_file_path
        self._default_channel_list = default_channel_list
        self._elog = elog

    def avail(self,*args,**kwargs):
        return dispatcher.get_current_channels(*args,**kwargs)

    def h5(self,fina=None,channel_list=None,N_pulses=None,default_path=True,queue_size=100):
        if default_path:
            fina = self._default_file_path%fina
        
        if os.path.isfile(fina):
            print('!!! File %s already exists, would you like to delete it?'%fina)
            if input('(y/n)')=='y':
                print('Deleting %s .'%fina)
                os.remove(fina)
            else:
                return
        if not channel_list:
            print('No channels specified, using default list \'%s\' instead.'%list(self._default_channel_list.keys())[0])
            channel_list = self._default_channel_list[list(self._default_channel_list.keys())[0]]
            
        source = dispatcher.request_stream(channel_list)
        mode = zmq.SUB
        receive(source, fina, queue_size=queue_size, mode=mode, n_messages=N_pulses)
    def db(self,channel_list=None,start_time_delta=dict(),end_time_delta=dict(),default_path=True):
        if not channel_list:
            print('No channels specified, using default list \'%s\' instead.'%list(self._default_channel_list.keys())[0])
            channel_list = self._default_channel_list[list(self._default_channel_list.keys())[0]]
        now = datetime.datetime.now()
        end = now-datetime.timedelta(**end_time_delta)
        start = end-datetime.timedelta(**start_time_delta)
        return api.get_data(channels=channel_list, start=start, end=end) 

    def h5_db(self,fina,channel_list=None,start_time_delta=dict(),end_time_delta=dict(),default_path=True):
        data = self.db(channel_list=None,start_time_delta=start_time_delta,end_time_delta=end_time_delta,default_path=True)    
        if default_path:
            fina = self._default_file_path%fina
        
        if os.path.isfile(fina):
            print('!!! File %s already exists, would you like to delete it?'%fina)
            if input('(y/n)')=='y':
                print('Deleting %s .'%fina)
                os.remove(fina)
            else:
                return
        
        data.to_hdf(fina,"/data")


    def acquire(self,file_name=None,Npulses=100):
        file_name += '.h5'
        def acquire():
            self.h5(fina=file_name,N_pulses=Npulses)
        return Acquisition(acquire=acquire,acquisition_kwargs={'file_names':[file_name], 'Npulses':Npulses},hold=False)

    def wait_done(self):
        self.check_running()
        self.check_still_running()


