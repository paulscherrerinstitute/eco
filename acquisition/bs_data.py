from bsread import Source
from bsread.h5 import receive
from bsread.avail import dispatcher
import zmq
import os


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
            print('!!! File %s already exists, would you like to delete it?')
            if input('(y/n)')=='y':
                print('Deleting %s .'%fina)
                os.remove(fina)
        if not channel_list:
            print('No channels specified, using default list \'%s\' instead.'%list(self._default_channel_list.keys())[0])
            channel_list = self._default_channel_list[list(self._default_channel_list.keys())[0]]
            
        source = dispatcher.request_stream(channel_list)
        mode = zmq.SUB
        receive(source, fina, queue_size=queue_size, mode=mode, n_messages=N_pulses)





