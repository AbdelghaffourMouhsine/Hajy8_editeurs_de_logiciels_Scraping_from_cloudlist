import pandas as pd
import os

class ItemStorage:
    def __init__(self, file_path=None, value=None):
        self.file_path = file_path
        
        self.columns = ['index', 'name', 'tele', 'address', 'more_inf_url', 'email', 'web_site_url']
        
         # Create the DataFrame with 'columns' if the file doesn't exist
        if not os.path.isfile(self.file_path):
            self.data = pd.DataFrame(columns=self.columns)
            self.data.to_csv(self.file_path, index=False, encoding='utf-8-sig')
        else:
            self.data = pd.read_csv(self.file_path, encoding='utf-8-sig')
        
        # Insert the value if provided
        if value:
            if isinstance(value, list):
                self.insert_items(value)
            else:
                self.insert_item(value)

    def insert_item(self, item):
        data = item.to_dict()
        # Assume data is a dictionary with keys 'key_words', 'category', 'description'
        new_data = pd.DataFrame([data], columns=self.columns)
        self.data = pd.concat([self.data, new_data], ignore_index=True)
        self.data.to_csv(self.file_path, index=False, encoding='utf-8-sig')
        
    def insert_items(self, items):
        # Assume items is a list of dictionaries, where each dictionary represents a row
        items = [item.to_dict() for item in items]
        new_data = pd.DataFrame(items, columns=self.columns)
        self.data = pd.concat([self.data, new_data], ignore_index=True)
        self.data.to_csv(self.file_path, index=False, encoding='utf-8-sig')

    def get_list_of_dicts(self):
        return self.data.to_dict(orient='records')