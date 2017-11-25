import pyscan
import os
import json

class ScanSimple:
    def __init__(self,adjustables,values,counterCallers,fina,basepath='',scan_info_dir=''):
        self.Nsteps = len(values)
        self.adjustables = adjustables
        self.values_todo = values
        self.values_done = []
        self.counterCallers = counterCallers
        self.fina = fina
        self.nextStep = 0
        self.basepath = basepath
        self.scan_info_dir = scan_info_dir
        self.scan_info = {'scan_parameters':
                {
                    'name':[ta.name for ta in adjustables ],
                    'Id':[ta.Id for ta in adjustables]
                    },
                'scan_values':[],
                'scan_files':[],
                'scan_step_info':[]}
        self.scan_info_filename = os.path.join(self.scan_info_dir,fina)
        self.scan_info_filename += '_scan_info.json'

    def get_filename(self,stepNo,Ndigits=4):
        fina = os.path.join(self.basepath,self.fina)
        fina += '_setp%04d.h5'%stepNo
        return fina

    def doNextStep(self,step_info=None):
        if not len(self.values_todo)>0:
            return False
        values_step = self.values_todo[0]
        ms = []
        fina = self.get_filename(self.nextStep)
        for adj,tv in zip(self.adjustables,values_step):
            ms.append(adj.changeTo(tv))
        for tm in ms:
            tm.wait()
        for ctr in self.counterCallers:
            ms.append(ctr.acquire(file_name=fina))
        for tm in ms:
            tm.wait() 
        self.values_done.append(self.values_todo.pop(0))
        self.appendScanInfo(values_step,fina,step_info=step_info)
        self.writeScanInfo()

        self.nextStep +=1
        return True

    def appendScanInfo(self,values_step,step_files=None,step_info=None):
        self.scan_info['scan_values'].append(values_step)
        self.scan_info['scan_files'].append(step_files)
        self.scan_info['scan_step_info'].append(step_info)

    def writeScanInfo(self):
        with open(self.scan_info_filename,'w') as f:
            json.dump(self.scan_info,f,indent=4,sort_keys=True)

    def scanAll(self):
        done = False
        while not done:
            done = not self.doNextStep()




