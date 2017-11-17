from epics import PV 

class EnumWrapper:
    def __init__(self,pvname,elog=None):
        self._elog = elog
        self._pv = PV(pvname)
        self.names = self._pv.enum_strs
        #print(self.names)
        #if self.names:
        self.setters = \
                Positioner(\
                [(nam,lambda:self.set(nam))
                    for nam in self.names])

    def set(self,target):
        if type(target) is str:
            assert target in self.names,\
                    "set value need to be one of \n %s"%self.names
            self._pv.put(self.names.index(target))
        elif type(target) is int:
            assert target>0, 'set integer needs to be greater equal zero'
            assert target<len(self.names)
            self._pv.put(target)
    def get(self):
        return self._pv.get()

    def get_name(self):
        return self.names[self.get()]

    def __repr__(self):
        return self.get_name()




class Positioner:
    def __init__(self,list_of_name_func_tuples):
        for name,func in list_of_name_func_tuples:
            tname = name.replace(' ','_')\
                              .replace('.','p')
            if tname[0].isnumeric():
                tname = 'v'+tname
            self.__dict__[tname] = func


