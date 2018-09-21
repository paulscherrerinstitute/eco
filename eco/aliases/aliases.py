
class Alias:
    def __init__(self,alias,channel=None,channeltype=None):
        self.alias = alias
        self.channel = channel
        self.channeltype = channeltype
        self.children = []

    def append(self,subalias):
        assert type(subalias) is Alias, 'You can only append aliases to aliases!'
        assert not (subalias.alias in [tc.alias for tc in self.children]),\
                f'Alias {subalias.alias} exists already!'
        self.children.append(subalias)

    def get_all(self):
        aa = []
        if self.channel:
            ta = {}
            ta['alias'] = self.alias
            ta['channel'] = self.channel
            if self.channeltype:
                ta['channeltype'] = self.channeltype
            aa.append(ta)
        if self.children:
            for tc in self.children:
                taa = tc.get_all()
                for ta in taa:
                    ta['alias'] = self.alias + ta['alias']
                    aa.append(ta)

class Namespace:
    def __init__(self,namespace):
        try

