import pyscan
import os
import json
import numpy as np

class ScanSimple:
    def __init__(self,adjustables,values,counterCallers,fina,Npulses=100,basepath='',scan_info_dir=''):
        self.Nsteps = len(values)
        self.pulses_per_step = Npulses
        self.adjustables = adjustables
        self.values_todo = values
        self.values_done = []
        self.readbacks = []
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
                'scan_readbacks':[],
                'scan_files':[],
                'scan_step_info':[]}
        self.scan_info_filename = os.path.join(self.scan_info_dir,fina)
        self.scan_info_filename += '_scan_info.json'

    def get_filename(self,stepNo,Ndigits=4):
        fina = os.path.join(self.basepath,self.fina)
        fina += '_step%04d'%stepNo
        return fina

    def doNextStep(self,step_info=None,verbose=True):
        if not len(self.values_todo)>0:
            return False
        values_step = self.values_todo[0]
        if verbose:
            print('Starting scan step %d of %d'%(self.nextStep+1,len(self.values_todo)+len(self.values_done)))
        ms = []
        fina = self.get_filename(self.nextStep)
        for adj,tv in zip(self.adjustables,values_step):
            ms.append(adj.changeTo(tv))
        for tm in ms:
            tm.wait()
        readbacks_step = []
        for adj in self.adjustables:
            readbacks_step.append(adj.get_current_value())
        if verbose:
            print('Moved variables, now starting acquisition')
        filenames = []
        acs = []
        for ctr in self.counterCallers:
            acq = ctr.acquire(file_name=fina,Npulses=self.pulses_per_step)
            filenames.extend(acq.file_names)
            acs.append(acq)
        for ta in acs:
            ta.wait()
        if verbose:
            print('Done with acquisition')
        self.values_done.append(self.values_todo.pop(0))
        self.readbacks.append(readbacks_step)
        self.appendScanInfo(values_step,readbacks_step,step_files=filenames,step_info=step_info)
        self.writeScanInfo()

        self.nextStep +=1
        return True

    def appendScanInfo(self,values_step,readbacks_step,step_files=None,step_info=None):
        self.scan_info['scan_values'].append(values_step)
        self.scan_info['scan_readbacks'].append(readbacks_step)
        self.scan_info['scan_files'].append(step_files)
        self.scan_info['scan_step_info'].append(step_info)

    def writeScanInfo(self):
        with open(self.scan_info_filename,'w') as f:
            json.dump(self.scan_info,f,indent=4,sort_keys=True)

    def scanAll(self):
        done = False
        while not done:
            done = not self.doNextStep()


class Scans:
    def __init__(self,data_base_dir='',scan_info_dir='',default_counters=[]):
        self.data_base_dir = data_base_dir
        self.scan_info_dir = scan_info_dir
        self._default_counters = default_counters

    def ascan(self,adjustable,start_pos,end_pos,N_intervals,N_pulses,file_name=None,start_immediately=True):
        positions = np.linspace(start_pos,end_pos,N_intervals+1)
        values = [[tp] for tp in positions]
        s = ScanSimple([adjustable],values,self._default_counters,file_name,Npulses=100,basepath=self.data_base_dir,scan_info_dir=self.scan_info_dir)
        if start_immediately:
            s.scanAll()
        return s


