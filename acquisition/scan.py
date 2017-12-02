import pyscan
import os
import json
import numpy as np
from time import sleep

class ScanSimple:
    def __init__(self,adjustables,values,counterCallers,fina,Npulses=100,basepath='',scan_info_dir='',checker=None):
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
        self.checker = checker
        self.initial_values = []
        for adj in self.adjustables:
            tv = adj.get_current_value()
            self.initial_values.append(adj.get_current_value())
            print('Initial value of %s : %g'%(adj.name,tv))


    def get_filename(self,stepNo,Ndigits=4):
        fina = os.path.join(self.basepath,self.fina)
        fina += '_step%04d'%stepNo
        return fina

    def doNextStep(self,step_info=None,verbose=True):
        if self.checker:
            while not self.checker['checker_call'](*self.checker['args'],**self.checker['kwargs']):
                print('Condition checker is not happy, waiting for OK conditions.')
                sleep(self.checker['wait_time'])

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
        if self.checker:
            if not self.checker['checker_call'](*self.checker['args'],**self.checker['kwargs']):
                return True

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
        try:
            while not done:
                done = not self.doNextStep()
        except:
            tb = traceback.format_exc()
        else:
            tb = "No error"
        finally:
            print(tb)

    def changeToInitialValues(self):
        c = []
        for adj,iv in zip(self.adjustables,self.initial_values):
            c.append(adj.changeTo(iv))
        return c


class Scans:
    def __init__(self,data_base_dir='',scan_info_dir='',default_counters=[],checker=None):
        self.data_base_dir = data_base_dir
        self.scan_info_dir = scan_info_dir
        self._default_counters = default_counters
        self.checker = checker

    def ascan(self,adjustable,start_pos,end_pos,N_intervals,N_pulses,file_name=None,start_immediately=True):
        positions = np.linspace(start_pos,end_pos,N_intervals+1)
        values = [[tp] for tp in positions]
        s = ScanSimple([adjustable],values,self._default_counters,file_name,Npulses=N_pulses,basepath=self.data_base_dir,scan_info_dir=self.scan_info_dir,checker=self.checker)
        if start_immediately:
            s.scanAll()
        return s

    def rscan(self,adjustable,start_pos,end_pos,N_intervals,N_pulses,file_name=None,start_immediately=True):
        positions = np.linspace(start_pos,end_pos,N_intervals+1)
        current = adjustable.get_current_value()
        values = [[tp+current] for tp in positions]
        s = ScanSimple([adjustable],values,self._default_counters,file_name,Npulses=N_pulses,basepath=self.data_base_dir,scan_info_dir=self.scan_info_dir,checker=self.checker)
        if start_immediately:
            s.scanAll()
        return s

    def dscan(self,*args,**kwargs):
        print('Warning: dscan will be deprecated for rscan unless someone explains what it stands for in spec!')
        return self.rscan(*args,**kwargs)

    def ascanList(self,adjustable,posList,N_pulses,file_name=None,start_immediately=True):
        positions = posList
        values = [[tp] for tp in positions]
        s = ScanSimple([adjustable],values,self._default_counters,file_name,Npulses=N_pulses,basepath=self.data_base_dir,scan_info_dir=self.scan_info_dir,checker=self.checker)
        if start_immediately:
            s.scanAll()
        return s

