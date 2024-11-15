
class EditeurLogiciels:
    def __init__(self):
        self.index = None
        self.name = None
        self.tele = None
        self.address = None
        self.more_inf_url = None
        
    def init_from_dict(self, dict):
        self.index = dict.get('index')
        self.name = dict.get('name')
        self.tele = dict.get('tele')
        self.address = dict.get('address')
        self.more_inf_url = dict.get('more_inf_url')

    def to_dict(self):
        dict = {}
        dict['index'] = self.index
        dict['name'] = self.name
        dict['tele'] = self.tele
        dict['address'] = self.address
        dict['more_inf_url'] = self.more_inf_url
        return dict
        
    def __str__(self):
        return self.to_dict()
