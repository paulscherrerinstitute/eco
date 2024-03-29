from ..epics.adjustable import AdjustablePvEnum


class AramisMode:
    def __init__(self, name=None):
        self.name = name
        self.switch = AdjustablePvEnum("SAROP-ARAMIS:BEAMLINE_SP", name="switch")
        self.alvra = AdjustablePvEnum("SAROP11-ARAMIS:MODE_SP", name="alvra")
        self.bernina = AdjustablePvEnum("SAROP21-ARAMIS:MODE_SP", name="bernina")

    def status(self):
        s = "Aramis mode\n"
        s += f"Mirror switch to {self.switch.get_current_value().name}\n"
        s += f"Alvra in {self.alvra.get_current_value().name} mode\n"
        s += f"Bernina in {self.bernina.get_current_value().name} mode"
        return s

    def __repr__(self):
        return self.status()
