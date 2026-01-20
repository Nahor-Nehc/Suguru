
class Stack:
    def __init__(self):
        self.stack = []
    
    def __getitem__(self, i):
        return self.stack.__getitem__(i)
    
    def pop(self, index):
        return self.stack.pop(index)
    
    