import pyscan

class ScanSimple:
    def __init__(self,adjustables,values,counterCallers,fina):
        self.Nsteps = len(values)
        self.adjustables = adjustables
        self.values_todo = values
        self.values_done = None
        self.counterCallers = counterCallers
        self.fina = fina
        self.nextStep = 0

    def doNextStep(self):
        values_step = self.values_todo[0]
        ms = []
        for adj,tv in zip(self.adjustables,values_step):
            ms.append(adj.changeTo(tv))
        for tm in ms:
            tm.wait()
        for ctr in self.counterCallers:
            ms.append(ctr.acquire(file_name=fina))
        for tm in ms:
            tm.wait()  

