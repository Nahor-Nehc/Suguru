

class State:
    def __init__(self, displaying:str,):
        self.displaying = displaying
        self.data = dict()
        
    def __getitem__(self, i):
        if i in self.data.keys():
            return self.data[i]
        else:
            raise ValueError(
                i, "is not in the list of data stored:", self.data.keys())
    
    def __setitem__(self, key, value):
        if key in self.data.keys():
            self.data[key] = value
        else:
            raise ValueError(
                key, "is not in the list of data stored:", self.data.keys())
    
    def create_data_keys(self, *keys):
        for key in keys:
            self.data.update({key: None})
    
    def get_data(self):
        return self.data
