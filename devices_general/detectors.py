import numpy as np
from epics import caget

_cameraArrayTypes = ['monochrome','rgb']

class CameraCA:
    def __init__(self, pvname, cameraArrayType='monochrome'):
        self.Id = pvname
        self.isBS = False
        self.px_height = None
        self.px_width = None

    def get_px_height(self):
        if not self.px_height:
            self.px_height = caget(self.Id + '.HEIGHT')
        return self.px_height

    def get_px_width(self):
        if not self.px_width:
            self.px_width = caget(self.Id + '.WIDTH')
        return self.px_width

    def get_data(self):
        pass





