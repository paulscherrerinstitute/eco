from epics import PV 

class EnumWrapper:
    def __init__(self,pvname):
        self._pv = PV(pvname)
        self.names = self.pv.enum_strs
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




class Positioner:
    def __init__(list_of_name_func_tuples):
        for name,func in list_of_name_func_tuples:
            self.__dict__[name.replace(' ','_')] = func


