class EditeurLogiciels:
    attributes = ['index', 'name', 'tele', 'address', 'more_inf_url', 'email', 'web_site_url', 'description', 'tags', 'contact', 
                  'commercial_name', 'nos_domaines', 'linkedin', 'profiles', 'linkedin_about_info', 'about téléphone','about taille de l’entreprise',
                  'about page vérifiée', 'about site web','about spécialisations','about secteur','about siège social','about fondée en','about company_size',
                  'about vue d’ensemble', 'min_size', 'max_size', 'profile_name', 'profile_description', 'profile_url']
    
    def __init__(self, dict=None):
        for attribute in self.attributes:
            setattr(self, attribute, None)
        if dict:
            for attr_name, attr_value in self.__dict__.items():
                setattr(self, attr_name, dict.get(attr_name))
            
    def init_from_dict(self, dict):
        for attr_name, attr_value in self.__dict__.items():
            setattr(self, attr_name, dict.get(attr_name))

    def to_dict(self):
        return self.__dict__
        
    def __str__(self):
        return str(self.to_dict())
