import numpy as np
from epics import caget
from epics import PV
from ..eco_epics.utilities_epics import EnumWrapper

from cam_server import PipelineClient
from cam_server.utils import get_host_port_from_stream_address
from bsread import source, SUB
import subprocess
import h5py
from time import sleep
from threading import Thread

from ..acquisition.utilities import Acquisition

try:
    import sys, os
    tpath = os.path.dirname(__file__)
    sys.path.insert(0,os.path.join(tpath,'../../detector_integration_api'))
    sys.path.insert(0,os.path.join(tpath,'../../jungfrau_utils'))
    from detector_integration_api import DetectorIntegrationClient
except:
    print('NB: detector integration could not be imported!')


_cameraArrayTypes = ['monochrome','rgb']

class CameraCA:
    def __init__(self, pvname, cameraArrayType='monochrome',elog=None):
        self.Id = pvname
        self.isBS = False
        self.px_height = None
        self.px_width = None
        self.elog = elog

    def get_px_height(self):
        if not self.px_height:
            self.px_height = caget(self.Id + ':HEIGHT')
        return self.px_height

    def get_px_width(self):
        if not self.px_width:
            self.px_width = caget(self.Id + ':WIDTH')
        return self.px_width

    def get_data(self):
        w = self.get_px_width()
        h = self.get_px_height()
        numpix = int(caget(self.Id+':FPICTURE.NORD'))
        i = caget(self.Id+':FPICTURE', count=numpix)
        return i.reshape(h,w)

    def record_images(self,fina,N_images,sleeptime=0.2):
        with h5py.File(fina,'w') as f:
            d = []
            for n in range(N_images):
                d.append(self.get_data())
                sleep(sleeptime)
            f['images'] = np.asarray(d)

    def gui(self, guiType='xdm'):
        """ Adjustable convention"""
        cmd = ['caqtdm','-macro']

        cmd.append('\"NAME=%s,CAMNAME=%s\"'%(self.Id, self.Id))
        cmd.append('/sf/controls/config/qt/Camera/CameraMiniView.ui')
        return subprocess.Popen(' '.join(cmd),shell=True)

#/sf/controls/config/qt/Camera/CameraMiniView.ui" with macro "NAME=SAROP21-PPRM138,CAMNAME=SAROP21-PPRM138        

class CameraBS:
    def __init__(self,host=None,port=None,elog=None):
        self._stream_host = host
        self._stream_port = port

    def checkServer(self):
        # Check if your instance is running on the server.
        if self._instance_id not in client.get_server_info()["active_instances"]:
            raise ValueError("Requested pipeline is not running.")

    def get_images(self,N_images):
        data = []
        with source(host=self._stream_host, port=self._stream_port, mode=SUB) as input_stream:
            input_stream.connect()
            
            for n in range(N_images):
                data.append(input_stream.receive().data.data['image'].value)
        return data

    def record_images(self,fina,N_images,dsetname='images'):
        ds = None
        with h5py.File(fina,'w') as f:
            with source(host=self._stream_host, port=self._stream_port, mode=SUB) as input_stream:

                input_stream.connect()
                
                for n in range(N_images):
                    image = input_stream.receive().data.data['image'].value
                    if not ds:
                        ds = f.create_dataset(dsetname,dtype=image.dtype, shape=(N_images,)+image.shape)
                    ds[n,:,:] = image

class FeDigitizer:
    def __init__(self,Id,elog=None):
        self.Id = Id
        self.gain = EnumWrapper(Id+'-WD-gain')
        self._bias = PV(Id+'-HV_SET')
        self.channels = [
                Id+'-BG-DATA',
                Id+'-BG-DRS_TC',
                Id+'-BG-PULSEID-valid',
                Id+'-DATA',
                Id+'-DRS_TC',
                Id+'-PULSEID-valid']

    def set_bias(self, value):
        self._bias.put(value)

    def get_bias(self):
        return self._bias.value

class DiodeDigitizer:
    def __init__(self,Id,VME_crate=None,link=None,
            ch_0=7,ch_1=8, elog=None):
        self.Id = Id
        if VME_crate:
            self.diode_0 = FeDigitizer('%s:Lnk%dCh%d'%(VME_crate,link,ch_0))
            self.diode_1 = FeDigitizer('%s:Lnk%dCh%d'%(VME_crate,link,ch_1))
        
        




class JF:
    def __init__(self, Id):
        self.writer_config = ""
        self.backend_config = ""
        self.detector_config = ""
        self.Id = Id
        self.api_address = self.Id
        self.client = DetectorIntegrationClient(self.Id)

    def reset(self):
        self.client.reset()
        pass

    def get_status(self):
        status = self.client.get_status()
        return status

    def get_config(self):
        config = self.client.get_config()
        return config

    def set_config(self, pedestal_fname = '/gpfs/sf-data/bernina/derived/p16582/JF_pedestal/pedestal_20171128_1833_res.h5', fname = "/sf/bernina/data/JF.h5", N = 1000):
        
        self.reset()
        self.detector_config = {
               "timing": "trigger",
               "exptime": 0.00001,
               "delay"  : 0.00199, # this is the magic aldo number
               "frames" : 1,
               "cycles": N}


        self.writer_config = {
              "output_file": fname,
              "process_uid": 16582,
              "process_gid": 16582,
              "dataset_name": "jungfrau/data",
              "n_messages": N}

        self.backend_config = {
              "n_frames": N,
              "gain_corrections_filename": "/sf/bernina/data/res/p16582/gains.h5",
              "gain_corrections_dataset": "gains",
              "pede_corrections_filename": pedestal_fname,
              "pede_corrections_dataset": "gains",
              "activate_corrections_preview": True}


        DetectorIntegrationClient.set_config(self,self.writer_config, self.backend_config, self.detector_config)
        pass

    def record(self,file_name,Npulses):
        self.detector_config.update(dict(cycles=Npulses))
        self.writer_config.update(dict(output_file=file_name))
        self.reset()
        DetectorIntegrationClient.set_config(self,self.writer_config, self.backend_config, self.detector_config)
        self.client.start()

    def check_running(self,time_interval=.5):
        cfg = self.get_config()
        running = False
        while not running:
            if self.get_status()['status'][-7:]=='RUNNING':
                running = True
                break
            else:
                sleep(time_interval)
        
    def check_still_running(self,time_interval=.5):
        cfg = self.get_config()
        running = True
        while running:
            if not self.get_status()['status'][-7:]=='RUNNING':
                running = False
                break
            else:
                sleep(time_interval)

    def start(self):
        self.client.start()
        print("start acquisition")
        pass

    def stop(self):
        self.client.stop()
        print("stop acquisition") 
        pass

    def config_and_start_test(self):
        self.reset()
        self.set_config()
        self.start()
        pass

    def acquire(self,file_name=None,Npulses=100):
        file_name += '_JF1p5M.h5'
        def acquire():
            self.reset()
            self.detector_config.update(dict(cycles=Npulses))
            self.writer_config.update(dict(output_file=file_name))
            self.set_config(f = file_name, N = Npulses)
            self.client.start()
            self.check_running()
            self.check_still_running()

        return Acquisition(acquire=acquire,acquisition_kwargs={'file_names':[file_name], 'Npulses':Npulses},hold=False)
        
    

    def wait_done(self):
        self.check_running()
        self.check_still_running()




def parseChannelListFile(fina):
    out = []
    with open(fina,'r') as f:
        done = False
        while not done:
           d = f.readline()
           if not d:
               done=True
           if len(d)>0:
               if not d.isspace():
                   if not d[0]=='#':
                       out.append(d.strip())
    return out
# JF client thing

class JF_BS_writer:
    def __init__(self, Id,api_address = "http://sf-daq-1:10000"):
        self._api_address = api_address 
        self.client = DetectorIntegrationClient(api_address)
        print("\nJungfrau Integration API on %s" % api_address)
        self.writer_config = {
                "output_file": "/sf/bernina/data/raw/p16582/test_data.h5", 
                "process_uid": 16582, 
                "process_gid": 16582, 
                "dataset_name": "jungfrau/data", 
                "n_messages": 100
                }
        self.backend_config = {
                "n_frames": 100, 
                "gain_corrections_filename": "/sf/bernina/data/res/p16582/gains.h5", 
                "gain_corrections_dataset": "gains", 
                "pede_corrections_filename": "/sf/bernina//data/res/p16582/JF_pedestal/pedestal_20171128_1048_res.h5", 
                "pede_corrections_dataset": "gains", 
                "activate_corrections_preview": True
                }
        self.detector_config = {
                "timing": "trigger", 
                "exptime": 0.00001, 
                "cycles": 100,
                "delay"  : 0.00199,
                "frames" : 1
                    }
        
        default_channels_list = parseChannelListFile(
                    '/sf/bernina/config/com/channel_lists/default_channel_list')
        self.bsread_config = {
                'output_file': '/sf/bernina/data/raw/p16582/test_bsread.h5', 
                'process_uid': 16582, 
                'process_gid': 16582, 
                'n_pulses':100,
                'channels': default_channels_list
                }
#        self.default_channels_list = jungfrau_utils.load_default_channel_list()

    def reset(self):
        self.client.reset()
        pass

    def get_status(self):
        return self.client.get_status()

    def get_config(self):
        config = self.client.get_config()
        return config

    def set_config(self):
        self.client.set_config(writer_config=self.writer_config, backend_config=self.backend_config, detector_config=self.detector_config, bsread_config=self.bsread_config)

#    def record(self,file_name,Npulses):
#        self.detector_config.update(dict(cycles=Npulses))
#        self.writer_config.update(dict(output_file=file_name))
#        self.reset()
#        DetectorIntegrationClient.set_config(self,self.writer_config, self.backend_config, self.detector_config)
#        self.client.start()
#
#    def check_running(self,time_interval=.5):
#        cfg = self.get_config()
#        running = False
#        while not running:
#            if self.get_status()['status'][-7:]=='RUNNING':
#                running = True
#                break
#            else:
#                sleep(time_interval)
        
    def check_still_running(self,time_interval=.5):
        cfg = self.get_config()
        running = True
        while running:
            if not self.get_status()['status'][-7:]=='RUNNING':
                running = False
                break
#            elif not self.get_status()['status'][-20:]=='BSREAD_STILL_RUNNING':
#                running = False
#                break
            else:
                sleep(time_interval)

    def start(self):
        self.client.start()
        print("start acquisition")
        pass

    def stop(self):
        self.client.stop()
        print("stop acquisition") 
        pass

    def config_and_start_test(self):
        self.reset()
        self.set_config()
        self.start()
        pass

    def wait_for_status(self,*args,**kwargs):
        return self.client.wait_for_status(*args,**kwargs)

    def acquire(self,file_name=None,Npulses=100,JF_factor=2,bsread_padding=50):
        file_name_JF = file_name + '_JF1p5M.h5'
        file_name_bsread = file_name+'.h5'
        def acquire():
            self.detector_config.update({
                'cycles':Npulses*JF_factor})
            self.writer_config.update({
                'output_file':file_name_JF,
                'n_messages':Npulses*JF_factor})
            self.backend_config.update({
                'n_frames':Npulses*JF_factor})
            self.bsread_config.update({
                'output_file':file_name_bsread,
                'n_pulses':Npulses+bsread_padding
                })
            
            self.reset()
            self.set_config()
            self.client.start()
            done = False
            while not done:
                stat = self.get_status()
                if stat['status'] =='IntegrationStatus.FINISHED':
                    done = True
                if stat['status'] == 'IntegrationStatus.BSREAD_STILL_RUNNING':
                    done = True
                if stat['status'] == 'IntegrationStatus.INITIALIZED':
                    done = True
                if stat['status'] == 'IntegrationStatus.DETECTOR_STOPPED':
                    done = True
                sleep(.1)

        return Acquisition(acquire=acquire,acquisition_kwargs={'file_names':[file_name_bsread,file_name_JF], 'Npulses':Npulses},hold=False)
        
    

    def wait_done(self):
        self.check_running()
        self.check_still_running()
