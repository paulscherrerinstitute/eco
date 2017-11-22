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

from detector_integration_api import DetectorIntegrationClient


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
        self.bias = PV(Id+'-HV_SET')
        self.channels = [
                Id+'-BG-DATA',
                Id+'-BG-DRS_TC',
                Id+'-BG-PULSEID-valid',
                Id+'-DATA',
                Id+'-DRS_TC',
                Id+'-PULSEID-valid']

    def set_bias(self, value)
        bias = PV(Id+'-HV_SET')
        bias.put(value)
        return 'Bias set to %sV'%(bias.value)

    def get_bias(self)
        return PV(Id+'-HV_SET').value

class DiodeDigitizer:
    def __init__(self,Id,VME_crate=None,link=None,
            ch_0=7,ch_1=8,
            elog=None):
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

    def set_config(self):
        self.writer_config = {'dataset_name': 'jungfrau/data','output_file': '/gpfs/sf-data/bernina/raw/p16582/Bi11_pp_delayXXPP_tests.h5','process_gid': 16582,   'process_uid': 16582, "disable_processing": False};
        self.backend_config = {"n_frames": 100000, "pede_corrections_filename": "/sf/bernina/data/res/p16582/pedestal_20171119_1027_res.h5", "pede_corrections_dataset": "gains", "gain_corrections_filename": "/sf/bernina/data/res/p16582/gains.h5", "gain_corrections_dataset": "gains", "activate_corrections_preview": True, "pede_mask_dataset": "pixel_mask"};
        self.detector_config = {"exptime": 0.0001, "cycles":20000, "timing": "trigger", "frames": 1}
        DetectorIntegrationClient.set_config(self,self.writer_config, self.backend_config, self.detector_config)
        pass

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

