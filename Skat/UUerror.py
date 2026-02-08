class Error:
    def __init__(self,errorType,file='',lineNumber=0,lineString='',msg=''):
        self.errorType = errorType
        self.file = file
        self.lineNumber = lineNumber
        self.lineString = lineString
        self.msg = msg
    def __repr__(self):
        return  f'{self.errorType} в файле "{self.file}" на строке {self.lineNumber}\n{self.lineString}\n{self.msg}' if self.msg != '' else\
                f'{self.errorType}. "{self.file}"'