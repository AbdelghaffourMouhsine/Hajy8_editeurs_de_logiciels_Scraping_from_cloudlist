class EditeurLogiciels:
    attributes = ['index', 'name', 'tele', 'address', 'more_inf_url', 'email', 'web_site_url', 'description', 'tags', 'contact', 
                  'commercial_name', 'nos_domaines', 'linkedin', 'profiles']
    
    def __init__(self):
        for attribute in self.attributes:
            setattr(self, attribute, None)
        
    def init_from_dict(self, dict):
        for attr_name, attr_value in self.__dict__.items():
            setattr(self, attr_name, dict.get(attr_name))

    def to_dict(self):
        return self.__dict__
        
    def __str__(self):
        return str(self.to_dict())
