import numpy as np
from epics import caget

from cam_server import PipelineClient
from cam_server.utils import get_host_port_from_stream_address
from bsread import source, SUB


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
        

class CameraBS:
    def __init__(self,Id,elog):
        # First create the pipeline for the selected camera.
        client = PipelineClient() 

        self._instance_id, self._stream_address = \
                client.create_instance_from_config(\
                {"camera_name": Id})

        # Extract the stream host and port from the stream_address.
        self._stream_host, self._stream_port = \
                get_host_port_from_stream_address(stream_address)
        self.checkServer()

    def checkServer(self):
        # Check if your instance is running on the server.
        if self._instance_id not in client.get_server_info()["active_instances"]:
            raise ValueError("Requested pipeline is not running.")
    def get_message(self):
        # Open connection to the stream. When exiting the 'with' section, the source disconnects by itself.
        with source(host=self._stream_host, port=self._stream_port, mode=SUB) as input_stream:
            input_stream.connect()
            
            # Read one message.
            message = input_stream.receive()
            
            # Print out the received stream data - dictionary.
            # print("Dictionary with data:\n", message.data.data)
            
            # Print out the X center of mass.
            # print("X center of mass: ", message.data.data["x_center_of_mass"].value)
            return message.data




