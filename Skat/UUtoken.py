class Token:
    def __init__(self,ttype,value,line):
        self.ttype = ttype
        self.value = value
        self.line = line
    def __repr__(self):
        return f'{self.ttype}[{self.value}]'
        return f'{self.value}'