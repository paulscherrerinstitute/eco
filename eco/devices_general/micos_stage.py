from ..devices_general.motors import MotorRecord
from ..aliases import Alias, append_object_to_object


def addMotorRecordToSelf(self, name=None, Id=None):
    try:
        self.__dict__[name] = MotorRecord(Id, name=name)
        self.alias.append(self.__dict__[name].alias)
    except:
        print(f"Warning! Could not find motor {name} (Id:{Id})")

        self.Id = Id
        self.name = name
        self.alias = Alias(name)


class stage:
    def __init__(self, name=None, vonHamos_horiz_pv=None, vonHamos_vert_pv=None):
        self.name = name
        self.alias = Alias(name)
        addMotorRecordToSelf(self, Id=vonHamos_horiz_pv, name="horiz")
        addMotorRecordToSelf(self, Id=vonHamos_vert_pv, name="vert")

    def get_adjustable_positions_str(self):
        ostr = "***** VonHamos motor positions******\n"

        for tkey, item in self.__dict__.items():
            if hasattr(item, "get_current_value"):
                pos = item.get_current_value()
                ostr += "  " + tkey.ljust(17) + " : % 14g\n" % pos
        return ostr

    def __repr__(self):
        return self.get_adjustable_positions_str()
