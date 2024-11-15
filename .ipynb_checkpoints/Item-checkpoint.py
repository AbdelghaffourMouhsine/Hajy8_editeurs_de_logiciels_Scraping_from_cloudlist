
class EditeurLogiciels:
    def __init__(self):
        self.index = None
        self.name = None
        self.tele = None
        self.address = None
        self.more_inf_url = None
        self.email = None
        self.web_site_url = None
        
    def init_from_dict(self, dict):
        self.index = dict.get('index')
        self.name = dict.get('name')
        self.tele = dict.get('tele')
        self.address = dict.get('address')
        self.more_inf_url = dict.get('more_inf_url')
        self.email = dict.get('email')
        self.web_site_url = dict.get('web_site_url')
        return self

    def to_dict(self):
        dict = {}
        dict['index'] = self.index
        dict['name'] = self.name
        dict['tele'] = self.tele
        dict['address'] = self.address
        dict['more_inf_url'] = self.more_inf_url
        dict['email'] = self.email
        dict['web_site_url'] = self.web_site_url
        
        return dict
        
    def __str__(self):
        return str(self.to_dict())
