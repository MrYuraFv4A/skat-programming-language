#   Виртуальная машина "Щербет"
#   языка Skat
#   
#   Индивидуальный проект Кузнецова Юрия
#   Ученика 11Г класса
#
#   2025 - 2026 учебный год

import sys
from pprint import pprint
from copy import deepcopy
from time import sleep
from UUgenerator import Stack
from UUerror import Error
import UUshell
from UUerror import Error
from datetime import datetime
from re import match


#
#   Классы и ассеты
#

class stdio:
    def write(msg):
        sys.stdout.write(str(msg).replace('\\n','\n').replace('\\t','\t'))
    def printv(msg):
        #sys.stdout.write('SVMout : ')
        sys.stdout.write(str(msg).replace('\\n','\n').replace('\\t','\t')+'\n')

def pprint(*x): ...

def print(*x,end=''): ...

def sleep(x): ...

logFile = open('log.txt','a',encoding='utf-8')
logFile.write('\n'*3+str(datetime.now().time())+'\n')

def log(msg):
    logFile.write(str(msg)+'\n')

#
#   Логика
#

class SkatVirtualMachine:
    def __init__(self,src:str):
        self.commands = []
        for i in src:
            self.commands.append((self.split(i[0]),i[1][0],i[1][1]))
        self.current_command = ''

        self.memory = {}
        self.globals = {}
        self.namespace = [] #fullname
        self.namespaces = []
        self.types = 'int float NAN string kleene function prototype'.split()
        self.conditions = Stack()

        self.end = False
        self.index = -1
        
        self.stdvars()
        self.advance()
    
    def stdvars(self):
        self.memory = {
            'in' : {
                'type': 'function',
                'value':input,
                'rtype':'string',
                'return':None,
                'const':True,
                'nullable':False,
                'public':True,
                'namespace': []
            },
            'out' : {
                'type': 'function',
                'value':stdio.write,
                'rtype':'null',
                'return':None,
                'const':True,
                'nullable':True,
                'public':True,
                'namespace': []
            },
            'err' : {
                'type': 'function',
                'value':sys.stderr.write,
                'return':None,
                'rtype':'null',
                'const':True,
                'nullable':False,
                'public':True,
                'namespace': []
            },
            'console.printv' : {
                'type': 'function',
                'value':stdio.printv,
                'return':None,
                'rtype':'null',
                'const':True,
                'nullable':True,
                'public':True,
                'namespace': ['console']
            },
            'true': {
                'type': 'kleene',
                'value':1,
                'const':True,
                'nullable':False,
                'public':True,
                'namespace': []
            },
            'false' : {
                'type': 'kleene',
                'value':-1,
                'const':True,
                'nullable':False,
                'public':True,
                'namespace': []
            },
            'maybe' : {
                'type': 'kleene',
                'value':0,
                'const':True,
                'nullable':False,
                'public':True,
                'namespace': []
            },
            'null' : {
                'type': 'null',
                'value': 0,
                'const': True,
                'nullable': True,
                'public': True,
                'namespace': []
            },
            'infinity': {
                'type': 'infinity',
                'value': 'infinity',
                'const': True,
                'nullable': True,
                'public': True,
                'namespace': []
            },
            'infinityNegative': {
                'type': 'infinity',
                'value': 'infinityNegative',
                'const': True,
                'nullable': True,
                'public': True,
                'namespace': []
            },
            'to.String': {
                'type': 'prototype',
                'rtype': 'string',
                'args': ['ptr', 'any'],
                'body': [[['TYPE','ptr', 'string'],0,''],[['RETURN', 'ptr'],0,''],[['END', 'FUNCTION', 'to.String'],0,'']], #ЗДЕСЬ МОГУТ БЫТЬ КАКИЕ-ТО ПРОБЛЕМЫ
                'namespace': ['to'],
                'public': True,
                'value' : None
            },
            'to.Int': {
                'type': 'prototype',
                'rtype': 'string',
                'args': ['ptr', 'any'],
                'body': [[['TYPE', 'ptr', 'int'],0,''],[['RETURN', 'ptr'],0,''],[['END', 'FUNCTION', 'to.Int'],0,'']], #ЗДЕСЬ МОГУТ БЫТЬ КАКИЕ-ТО ПРОБЛЕМЫ
                'namespace': ['to'],
                'public': True,
                'value' : None
            },
            'copy': {
                'type': 'function',
                'value':input,
                'const':True,
                'nullable':False,
                'public':True,
                #'namespace': []
            }
        }

    def split(self,command):
        splitted = []
        i = -1
        buffer = ''
        while i + 1 < len(command):
            i += 1
            if command[i] == ' ':
                splitted.append(buffer)
                buffer = ''
            elif command[i] == '"':
                i += 1
                while command[i] != '"':
                    buffer += command[i]
                    i += 1
                splitted.append(f'"{buffer}"')
                buffer = ''
            else:
                buffer += command[i]
        if buffer != '':
            splitted.append(buffer)
        return splitted
    
    def advance(self):
        if self.end:
            exit()

        self.index += 1
        if self.index < len(self.commands):
            self.current_command = self.commands[self.index]
            #print(self.reason,self.current_command)
        else:
            self.end = True
        return self.current_command

    def set_quotes(self,string : str):
        if string == '':    string = '""'
        elif string[0] != '"':    string = f'"{string}"'
        return string

    def get_value(self,var,command=None,namespace=[]):
        if command == None: command = self.current_command
        var = str(var)
        namespace = self.split_list(deepcopy(namespace))

        print(f'getting value from {var}')
        

        if var[0] == '"':
            return var[1:-1]
        elif var[0] in '0123456789' or var[0] == '-':
            if '.' in var:
                return float(var)
            else:
                return int(var)
        else: # vars
            while True:
                if not '.'.join(namespace+[var]) in self.memory.keys():
                    try:
                        #print(namespace,var)
                        namespace.pop()
                        continue
                    except IndexError:
                        return var #интерпретируем как строку
                        #pprint(self.memory)
                        self.error(command,f'[код 181]. Переменная "{var}" не существует в текущем контексте')

                if not self.is_public(deepcopy(namespace),var):
                    self.error(command,f'[код 181]. {var} не является публичной переменной')

                if self.memory['.'.join(namespace+[var])]['type'] in ('function','prototype'):
                    #print(self.memory['.'.join(namespace+[var])])
                    if self.memory['.'.join(namespace+[var])]['return'] != None:
                        
                        ret = self.get_value(self.memory['.'.join(namespace+[var])]['return'])
                        #print('\n\n\n'+ret)
                        self.memory['.'.join(namespace+[var])]['return'] = None
                    else:
                        self.error(command,f'[код 181]. Функция "{var}" не имеет значения')
                        ret = self.memory['.'.join(namespace+[var])]
                else:
                    try:
                        ret = self.memory['.'.join(namespace+[var])]['value']
                        log('ret '+'.'.join(namespace+[var])+' '+str(ret))
                        if self.memory['.'.join(namespace+[var])]['type'] == 'any' and self.get_type(ret,command,deepcopy(namespace)) == 'string' and ret[0] == '"':
                            ret = ret[1:-1]
                    except KeyError:
                        self.error(command,f'[код 181]. {var} не')
                
                return ret
                    
    def get_type(self,value,command=None,namespace=[]):
        if command == None: command = self.current_command
        value = str(value)
        namespace = self.split_list(deepcopy(namespace))
        
        print(f'getting type from {value}')
        print(namespace,value)
        
        if '"' in value:
            return 'string'
        elif value[0] in '0123456789' or value[0] == '-':
            if '.' in value:
                return 'float'
            else:
                return 'int'
        else:
            while True:
                if not '.'.join(namespace+[value]) in self.memory.keys():
                    try:
                        log(namespace+[value])
                        namespace.pop()
                        continue
                    except IndexError:
                        pprint(self.memory)
                        self.error(command,f'[код 220]. Переменная "{value}" не существует в текущем контексте')

                if not self.is_public(deepcopy(namespace),value):
                    self.error(command,f'{value} не является публичной переменной')

                if self.memory['.'.join(namespace+[value])]['type'] in ('function','prototype'):
                    if self.memory['.'.join(namespace+[value])]['return'] != None:
                        val = self.memory['.'.join(namespace+[value])]['return']
                    else:
                        return self.memory['.'.join(namespace+[value])]['type']
                else:
                    #val = self.memory['.'.join(namespace+[value])]['value']
                    if self.memory['.'.join(namespace+[value])]['type'] != 'any':
                        return self.memory['.'.join(namespace+[value])]['type']
                    else:
                        val = self.memory['.'.join(namespace+[value])]['value']


                inner_value = val
                if self.memory['.'.join(namespace+[value])]['type'] == 'string':    inner_value = self.set_quotes(inner_value)
                return self.get_type(inner_value,command,namespace=deepcopy(namespace))
                    
    def get_var(self,namespace : list,vtype : str) -> dict:
        return {
            'type':vtype,
            'value':None,
            'const':False,
            'nullable':False,
            'public':False,
            'return':None,
            'namespace':namespace[:-1]
        }
    
    def is_public(self,namespace,name):
        return  self.memory['.'.join(namespace+[name])]['public'] or\
                '.'.join(namespace) in '.'.join(self.memory['.'.join(namespace+[name])]['namespace'])

    def copy_func(self,func,namespace=[]):
        namespace = self.split_list(namespace)
        while not '.'.join(namespace+[func]) in self.memory.keys():
            try:
                namespace.pop()
            except IndexError:
                self.error(self.current_command,f'Переменная "{func}" не существует в текущем контексте')
        else:
            if not self.is_public(deepcopy(namespace),func):
                self.error(self.current_command,f'{func} не является публичной переменной')
        namespace.append(func)

        return self.memory['.'.join(namespace)]

    def listsToList(self,l:list) -> list:
        ret = []
        for i in l:
            if type(i) == list:
                i = self.listsToList(i)
                ret += i
            else:
                ret += [i]
        return ret

    def split_list(self,l:list) -> list:
        ret = []
        if l != []:
            for i in l:
                if '.' in i:
                    i = i.split('.')
                ret.append(i)
            if type(ret[0]) == list:
                ret = ret[0]
        return self.listsToList(ret)

    def handler(self,command=None,namespace=[],name=''):
        if self.end:
            exit(0)

        if command == None:
            command = self.current_command
        if namespace == []:
            namespace = deepcopy(self.namespace)
        
        print(namespace,*command)

        #print('\t' + '\n\t'.join(str(i) for i in self.commands))
        #print(namespace,'\t'.join(command[0]))

        if command != []:
            try:
                if command[0][0] == 'RETURN':
                    self.RETURN(*command,namespace=deepcopy(namespace),func_name=name)
                else:
                    eval(f'self.{command[0][0]}(*command,namespace=deepcopy(namespace))')
            except KeyboardInterrupt:
                self.error(command, 'Пользователь прервал исполнение.')

        

    def CONNECT(self,*command,namespace=[]):
        print('CONNECTING',command[0][1])

        module = []
        
        if type(compile := UUshell.compile(command[0][1])) == Error:
            self.error(command,compile)

        for i in compile:
            module.append((self.split(i[0]),i[1][0],i[1][1]))
        
        self.commands = self.commands[:self.index+1] + module + self.commands[self.index+1:]

        print('CONNECTED',command[0][1])

    def VAR(self,*command,namespace=[]):
        namespace.append(command[0][1])

        vtype = command[0][2]
        self.memory['.'.join(namespace)] = self.get_var(namespace,vtype)

        print('.'.join(namespace))

    def set_condition(self,condition:str,command,namespace=[]):
        name = command[0][1]

        namespace.append(name)
        
        self.memory['.'.join(namespace)][condition] = True

    def SETCONST(self,*command,namespace=[]):    self.set_condition('const',command,namespace)
        
    def SETNULLABLE(self,*command,namespace=[]): self.set_condition('nullable',command,namespace)
    
    def SETPUBLIC(self,*command,namespace=[]):   self.set_condition('public',command,namespace)

    def TYPE(self,*command,namespace=[]):
        #TYPE {var} {type}
        var = command[0][1]

        while not '.'.join(namespace+[var]) in self.memory.keys():
            try:
                namespace.pop()
            except IndexError:
                self.error(command,f'Переменная "{var}" не существует в текущем контексте')
        else:
            if not self.is_public(deepcopy(namespace),var):
                self.error(command,f'{var} не является публичной переменной')
        namespace.append(var)

        if (to_type := command[0][2]) not in self.types:    self.error(command,f'Тип {to_type} не существует')

        
        value = self.get_value(var,command,deepcopy(namespace))
        cur_type = self.get_type(var,command,namespace=deepcopy(namespace))
        
        
        def to(value):
            if to_type == 'kleene':
                if cur_type == 'string':    return {'true':1,'false':-1,'maybe':0}[value]
                elif cur_type == 'int':     return value
                else: self.error(command,f'Невозможно привести тип {cur_type} к {to_type}')
            elif to_type == 'string':
                if cur_type == 'kleene':
                    return {1: 'true',-1: 'false',0: 'maybe'}
                else:
                    return str(value)
            elif to_type == 'int':
                if type(value) == str and '"' in value: value = value[1:-1]
                return int(value)
            elif to_type == 'float':
                return float(value)
        
        try:
            self.memory['.'.join(namespace)]['value'] = to(value)
        except ValueError as err:
            sys.stdout.write(str(err))
            self.error(command,f'Невозможно привести тип {cur_type} к {to_type}')
            

    def FUNC(self,*command,namespace=[]):
        namespace.append(command[0][1])
        name = command[0][1]
        rtype = command[0][2]
        args = command[0][3::]
        body = []
        
        while self.advance()[0] != ['END','FUNCTION',name]:
            body.append(self.current_command)
        body.append(self.current_command)
        

        self.memory['.'.join(namespace)] = {
            'type': 'prototype',
            'rtype':rtype,
            'args':args,
            'body':body,
            'namespace':namespace[:-1],
            'public': False,
            #'value' : ...,
            'return' : None,
            'nullable' : True
        }
        namespace.pop()
        #if command[0][1] == 'main': self.commands += [[['CALL','.'.join(namespace)+'.main','in','out','err'],command[1],command[2]]]

    def RETURN(self,*command,namespace=[],func_name=[]):
        print('RETURNING'*10)
        func_name = '.'.join(func_name)
        func = self.memory[func_name]
        
        vtype = self.get_type(command[0][1],command,namespace=deepcopy(namespace))
        value = self.get_value(command[0][1],namespace=deepcopy(namespace))
        
        if  vtype == 'null' and not func['nullable']:
            self.error(command,f'Функция {func_name} не допускает значения null')

        if  func['rtype'] != 'any' and\
            func['rtype'] != vtype and\
            func['rtype'] != 'kleene' and vtype != 'int' and value not in (-1,0,1):
            self.error(command,f'Тип возвращаемого значения функции({func['rtype']}) не согласуется с типом значения({vtype})')
        
        if vtype == 'string':   value = self.set_quotes(value)

        self.memory[func_name]['return'] = value

        print('\n\n\n\t\t\treturned',self.memory[func_name]['return'])
    
    def CALL(self,*command,namespace = []):

        namespace = self.split_list(namespace)
        namespace_maternal = deepcopy(namespace)
        args = command[0][2::]
        var = command[0][1]

        #def search

        while not '.'.join(namespace+[var]) in self.memory.keys():
            try:
                namespace.pop()
            except IndexError:
                self.error(command,f'Переменная "{var}" не существует в текущем контексте')
        else:
            if not self.is_public(deepcopy(namespace),var):
                self.error(command,f'{var} не является публичной переменной')
        
        namespace.append(var)

        

        if self.memory['.'.join(namespace)]['type'] == 'function':
            values = [self.get_value(i,command,namespace=deepcopy(namespace_maternal)) for i in args]
            for i in range(len(args)):
                if values[i] == None:
                    self.error(command,f'Значение аргумента "{args[i]}" неопределено')
            self.memory['.'.join(namespace)]['return'] = self.memory['.'.join(namespace)]['value'](*values)
            
            if self.memory['.'.join(namespace)]['rtype'] == 'string':
                self.memory['.'.join(namespace)]['return'] = self.set_quotes(self.memory['.'.join(namespace)]['return'])

            elif self.memory['.'.join(namespace)]['rtype'] == 'kleene':
                try:
                    self.memory['.'.join(namespace)]['return'] = {'true' : 1, 1 : 1, 'false' : -1, -1 : -1, 'maybe' : 0, 0 : 0}[self.memory['.'.join(namespace)]['return']]
                except KeyError:
                    self.error(command,f'Функция вернула недействительное значнеие, ожидалось -1, 0, 1 или true, false, maybe; но получено {self.memory['.'.join(namespace)]['return']}')
        
        else:
            ii = 0
            func_args = self.memory['.'.join(namespace)]['args']
            for i in range(0,len(func_args),2):
                self.memory['.'.join(namespace_maternal+[func_args[i]])] = self.get_var(namespace+[func_args[i]],func_args[i+1])
                self.memory['.'.join(namespace_maternal+[func_args[i]])]['value'] = self.get_value(args[ii],namespace=deepcopy(namespace_maternal))
                self.memory['.'.join(namespace_maternal+[func_args[i]])]['public'] = True
                print('.'.join(namespace_maternal+[func_args[i]]),self.memory['.'.join(namespace_maternal+[func_args[i]])])
                #self.memory['.'.join(namespace+[func_args[i]])] = self.get_var(namespace+[func_args[i]],func_args[i+1])
                #self.memory['.'.join(namespace+[func_args[i]])]['value'] = self.get_value(args[ii],command,namespace=deepcopy(namespace_maternal))
                #self.memory['.'.join(namespace+[func_args[i]])]['public'] = True
                #print('.'.join(namespace+[func_args[i]]),self.memory['.'.join(namespace+[func_args[i]])])
                #self.memory['.'.join(namespace+[func_args[i]])]['namespace']
                ii += 1
            del ii

            #self.commands.pop(self.index)
            
            
            self.commands = self.commands[:self.index+1] + self.memory['.'.join(namespace)]['body'] + self.commands[self.index+1:]
            

            #stdio.write('\n'*3)
            #print(namespace)
            #sleep(4)

            #print('\n'*3,'\n'.join('\t'.join(c[0]) for c in self.commands),'\n'*3)
            log(namespace)
            while not(self.advance()[0] == ['END','FUNCTION','.'.join(namespace)]): #опять чё-то в вызовах не работает
                self.handler(self.current_command,deepcopy(namespace_maternal+[var]),deepcopy(namespace)) #вот тут говна нахерачил
                #self.handler(self.current_command,deepcopy(namespace),deepcopy(namespace)) #вот тут говна нахерачил
                sleep(0.05)
            self.free_auto(deepcopy(namespace))
        
    def WHILE(self,*command,namespace=[]):
        backup_line = self.index
        current_index = len(self.conditions.value)
        while True:
            com = self.advance()
            #print(f'\tСейчас исполняется {self.current_command}')
            
            if com[0] == ['BREAK']:
                self.skip('EXITWHILE')
                com = self.current_command
                

            if com[0] == ['EXITWHILE']:
                print('\t'*40+'ВЫХОД ИЗ ЦИКЛА')
                #self.advance()
                break

            if com[0] in [['END','WHILE'],['CONTINUE']]:
                self.index = backup_line
                while len(self.conditions.value) != current_index: self.conditions.get()
                continue

            self.handler(com,deepcopy(namespace)) # НИКОГДА НЕЛЬЗЯ ЗАБЫВАТЬ ДОБАВЛЯТЬ deepcopy(namespace) !!!
            #sleep(0.2)
        #self.advance()
    
    def CONTINUE(self,*command,namespace=[]): ...#self.conditions.get()

    def BREAK(self,*command,namespace=[]): ...#self.conditions.get()
    
    def EXITWHILE(self,*command,namespace=[]): ... #self.advance()
        
    def FREE(self,*command,namespace=[]):
        namespace = self.split_list(namespace)
        var = command[0][1]
        #pprint(namespace+[var])
        while not '.'.join(namespace+[var]) in self.memory.keys():
            try:
                namespace.pop()
            except IndexError:
                self.error(command,f'Переменная "{var}" не существует в текущем контексте')
                return None
        
        if not self.is_public(deepcopy(namespace),var):
            self.error(command,f'{var} не является публичной переменной')
        
        namespace.append(var)

        #print('\t\t\t\t freeing ' + '.'.join(namespace))

        del self.memory['.'.join(namespace)]
    
    def PASS(self,*command,namespace=[]): ...

    def free_auto(self, namespace=[]):
        for var in (keys:=deepcopy(set(self.memory.keys()))):
            if '`' in var or var == '.'.join(namespace): continue
            if match(f'^{'.'.join(namespace)}\..*',var):
                print(var,namespace,match(r'^.*',var))
                del self.memory[var]
                #log(var+' была удалена')
        pprint(self.memory)

    def END(self,*command,namespace=[]):
        try:
            if command[0][1] == 'NAMESPACE':
                self.namespace.pop()


            elif command[0][1] == 'WHILE':
                ...#self.conditions.get()
                
        except IndexError:
            self.error(command, "")

    def NAMESPACE(self,*command,namespace=[]):
        self.namespace.append(command[0][1])
        self.namespaces.append(command[0][1])

    def skip(self,*checkfor):   #Поправить скип
            level = 1
            waitfor = ['IF','ELSE_IF','ELSE'] if 'ENDIF' in checkfor else ['WHILE']
            while level > 0:
                self.advance()
                print('\tskipping\t\t',self.current_command[0])
                if self.current_command[0][0] in waitfor:
                    level += 1
                elif self.current_command[0][0] in checkfor:
                    level -= 1

            '''
            while self.advance()[0][0] not in checkfor:
                print('\tskipping\t\t',self.current_command[0])
                if self.current_command[0][0] in ['IF','ELSE_IF','ELSE']:
                    self.skip('ENDIF')
                    if self.commands[self.index + 1][0][0] not in ['IF','ELSE_IF','ELSE']:
                        self.advance()
                    print('\tskipping after endif\t\t',self.current_command[0])
                    #if self.current_command[0][0] in ['IF','ELSE_IF','ELSE']: self.index -= 2
                    #print('\t'*4,self.commands[self.index+1])
            '''


    def IF(self,*command,namespace=[]):
        namespace = self.split_list(namespace)

        if (condition := self.get_value(command[0][1],command,deepcopy(namespace))) not in (-1,0,1):    self.error(command,f'Ожидался тип kleene, но получен {self.get_type(command[0][1],namespace)}')

        print(condition)
        
        self.conditions.add(condition)
        if condition != 1:
            self.skip('ENDIF')
        
        print('\t',self.current_command[0])

    def ELSE_IF(self,*command,namespace=[]):
        print('ELSE IF')
        try:
            prev_condtition = self.conditions.get()
        except IndexError:
            self.error(command,'Вы можете использовать "else if" только в составе условного выражния после "if"')

        if prev_condtition == 1:
            self.conditions.add(1)
            self.skip('ENDIF')
                
        else:
            if (condition := self.get_value(command[0][1],command,deepcopy(namespace))) not in (-1,0,1):    self.error(command,f'Ожидался тип kleene, но получен {self.get_type(command[0][1],command,deepcopy(namespace))}')

            print(condition)
            
            self.conditions.add(condition)
            if condition != 1:
                self.skip('ENDIF')
                    
    def ELSE(self,*command,namespace=[]):
        print('ELSE')

        try:
            prev_condtition = self.conditions.get()

        except IndexError:
            self.error(command,'Вы можете использовать "else" только в составе условного выражения после "if"')

        if prev_condtition == 1:
            #self.conditions.add(1)

            self.skip('ENDIF') #else идёт последним
                
    def ENDIF(self,*command,namespace=[]): ...#self.conditions.get()

    def operate(self,op,command,namespace=[]):
        namespace = self.split_list(namespace)
        namespace_maternal = deepcopy(namespace)

        var = command[0][1]

        while not '.'.join(namespace+[var]) in self.memory.keys():
            try:
                namespace.pop()
            except IndexError:
                self.error(command,f'Переменная "{var}" не существует в текущем контексте')
        else:
            if not self.is_public(deepcopy(namespace),var):
                self.error(command,f'{var} не является публичной переменной')
        namespace.append(var)

        if self.memory['.'.join(namespace)]['const'] == True:   self.error(self.current_command,f'Переменная {var} не может быть изменена так как является константой')

        value_type = self.get_type(command[0][2],command,namespace=deepcopy(namespace_maternal))
        if self.memory['.'.join(namespace)]['value'] == None:
            if self.memory['.'.join(namespace)]['type'] == 'any':
                self.memory['.'.join(namespace)]['type'] = value_type
            
            if self.memory['.'.join(namespace)]['type'] == 'prototype' and op == '+':
                self.memory['.'.join(namespace)] = self.copy_func(command[0][2],deepcopy(namespace_maternal))
                self.memory['.'.join(namespace)]['namespace'] = namespace
                return "Попа муравья"
            
            self.memory['.'.join(namespace)]['value'] = {
                'string': '""',
                'int':0,
                'float':0.0,
                'kleene':0,
                'infinity':0,
                'null':'null'
            }[self.memory['.'.join(namespace)]['type']]

        value = self.memory['.'.join(namespace)]['value']
        value_sec = self.get_value(command[0][2],namespace=deepcopy(namespace_maternal))

        value_type = self.memory['.'.join(namespace)]['type']
        value_sec_type = self.get_type(command[0][2],namespace=deepcopy(namespace_maternal))

        if value_type == 'string':
            value = self.set_quotes(value)
        if value_sec_type == 'string':
            value_sec = self.set_quotes(value_sec)
        

        value = self.get_value(value,namespace=deepcopy(namespace))
        #value_sec = self.get_value(command[0][2],namespace=deepcopy(namespace_maternal))
        value_sec = self.get_value(value_sec,command,deepcopy(namespace_maternal))

        if value_sec_type == 'prototype':
            value_sec_type = self.get_type(value_sec)

        try:
            if 'infinity' in (value_type, value_sec_type) and op not in ['&','|','^','==']:
                if value_type not in ('int','float','infinity'):
                    raise TypeError

                print('operate with infinity')
                var_namespace = self.memory['.'.join(namespace)]['namespace']
                var_isconst = self.memory['.'.join(namespace)]['const']

                if op in ['+','*','**']:   self.memory['.'.join(namespace)] = self.memory[value_sec]

                elif op == '-': self.memory['.'.join(namespace)] = self.memory[
                        {'infinity':'infinityNegative',
                        'infinityNegative':'infinity'}[value_sec]
                    ]
                    
                elif op == '/': self.memory['.'.join(namespace)]['value'] = 0

                self.memory['.'.join(namespace)]['namespace'] = var_namespace
                self.memory['.'.join(namespace)]['const'] = var_isconst
                return 'operate with infinity'

            if op == '+':   self.memory['.'.join(namespace)]['value'] = value + value_sec
            elif op == '-': self.memory['.'.join(namespace)]['value'] = value - value_sec
            elif op == '*': self.memory['.'.join(namespace)]['value'] = value * value_sec
            elif op == '/':
                if (value_sec := self.get_value(command[0][2],namespace=deepcopy(namespace))) == 0:
                    self.memory['.'.join(namespace)]['value'] = self.memory['infinity']['value']
                else:
                    self.memory['.'.join(namespace)]['value'] = value / value_sec
            elif op == '//':
                if (value_sec := self.get_value(command[0][2],namespace=deepcopy(namespace))) == 0:
                    self.memory['.'.join(namespace)]['value'] = self.memory['infinity']['value']
                else:
                    self.memory['.'.join(namespace)]['value'] = value // value_sec
            elif op == '%':
                if (value_sec := self.get_value(command[0][2],namespace=deepcopy(namespace))) == 0:
                    self.memory['.'.join(namespace)]['value'] = self.memory['infinity']['value']
                else:
                    self.memory['.'.join(namespace)]['value'] = value % value_sec
            
            elif op == '**': self.memory['.'.join(namespace)]['value'] = value ** value_sec
            elif op in '&|':
                if (val_sec_type := self.get_type(command[0][2],command,namespace=deepcopy(namespace))) not in ('kleene','int') and value_sec not in (-1,0,1):
                    #print(value_sec,val_sec_type)
                    self.error(command,f'Ожидался тип kleene, но получен {val_sec_type}')
                
                if op == '|':   self.memory['.'.join(namespace)]['value'] = max(value,value_sec)
                elif op == '&': self.memory['.'.join(namespace)]['value'] = min(value,value_sec)
            elif op == '==':
                self.memory['.'.join(namespace)]['value'] = {True:1,False:-1}[value == value_sec]
                
                print('.'.join(namespace),end = ' : ')
                pprint(self.memory['.'.join(namespace)])
            elif op in '> < >= <='.split():
                print('\t\t\tBIG',value,value_sec)
                self.memory['.'.join(namespace)]['value'] = {True:1,False:-1}[eval(f'value {op} value_sec')]
                
        except TypeError as er:
            print(er)
            self.error(command,f'Невозможно провесити операцию "{op}" над типами {value_type} и {value_sec_type}')
        

    def ADD(self,*command,namespace=[]): self.operate('+',command,namespace=deepcopy(namespace))
        
    def REM(self,*command,namespace=[]): self.operate('-',command,namespace=deepcopy(namespace))
        
    def MUL(self,*command,namespace=[]): self.operate('*',command,namespace=deepcopy(namespace))
        
    def DIV(self,*command,namespace=[]): self.operate('/',command,namespace=deepcopy(namespace))

    def IDIV(self,*command,namespace=[]): self.operate('//',command,namespace=deepcopy(namespace))

    def MOD(self,*command,namespace=[]): self.operate('%',command,namespace=deepcopy(namespace))
    
    def EXP(self,*command,namespace=[]): self.operate('**',command,namespace=deepcopy(namespace))

    def SET(self,*command,namespace=[]):
        namespace = self.split_list(namespace)
        namespace_maternal = deepcopy(namespace)

        var = command[0][1]

        while not '.'.join(namespace+[var]) in self.memory.keys():
            try:
                namespace.pop()
            except IndexError:
                self.error(command,f'Переменная "{var}" не существует в текущем контексте')
        else:
            if not self.is_public(deepcopy(namespace),var):
                self.error(command,f'{var} не является публичной переменной')
        namespace.append(var)

        sec = command[0][2]#self.set_quotes(command[0][2])
        
        value_type = self.get_type(sec,command,namespace=deepcopy(namespace_maternal))
        if  value_type == 'null' and not self.memory['.'.join(namespace)]['nullable']:
            self.error(command,f'Переменная {command[0][1]} не допускает значения null')

        if self.memory['.'.join(namespace)]['const'] == True:   self.error(self.current_command,f'Переменная "{command[0][1]}" не может быть изменена так как является константой')

        if value_type == 'prototype':
            self.memory['.'.join(namespace)] = self.copy_func(command[0][2],deepcopy(namespace_maternal))
            self.memory['.'.join(namespace)]['namespace'] = namespace
            self.memory['.'.join(namespace)]['body'][-1][0][2] = var
            return "Popa"

        value = self.get_value(command[0][2],namespace=deepcopy(namespace_maternal))
        print('\nval'*5,value)
        print(self.memory['.'.join(namespace)]['type'])

        if  (cur_type:=self.memory['.'.join(namespace)]['type']) != 'any' and\
            cur_type != value_type and\
            cur_type != 'kleene' and value_type != 'int' and value not in (-1,0,1) and\
            not (cur_type == 'float' and value_type == 'infinity') and\
            not '`' in var:
            self.error(command,f'Тип переменной {var}({self.memory['.'.join(namespace)]['type']}) не согласуется с типом значения({value_type})')
        
        if cur_type == 'any' and value_type == 'string':
            value = self.set_quotes(value) #f'"{value}"'
            
        
        self.memory['.'.join(namespace)]['value'] = value
        
        if value_type == 'infinity':    self.memory['.'.join(namespace)]['type'] = 'infinity'
    
    def AND(self,*command,namespace=[]):    self.operate('&',command,deepcopy(namespace))

    def OR(self,*command,namespace=[]):     self.operate('|',command,deepcopy(namespace))

    def EQ(self,*command,namespace=[]):     self.operate('==',command,deepcopy(namespace))

    def BIG(self,*command,namespace=[]):     self.operate('>',command,deepcopy(namespace))

    def SMALL(self,*command,namespace=[]):     self.operate('<',command,deepcopy(namespace))
    
    def BIGEQ(self,*command,namespace=[]):     self.operate('>=',command,deepcopy(namespace))

    def SMALLEQ(self,*command,namespace=[]):     self.operate('<=',command,deepcopy(namespace))

    def NOT(self,*command,namespace=[]):
        var = command[0][1]

        while not '.'.join(namespace+[var]) in self.memory.keys():
            try:
                namespace.pop()
            except IndexError:
                self.error(command,f'Переменная "{var}" не существует в текущем контексте')
        else:
            if not (self.memory['.'.join(namespace+[var])]['public'] or namespace == self.memory['.'.join(namespace+[var])]['namespace']):
                self.error(command,f'{var} не является публичной переменной')
        namespace.append(var)

        self.memory['.'.join(namespace)]['value'] = -1 *  self.memory['.'.join(namespace)]['value']
    
    def OTHER(self,*command,namespace=[]):
        var = command[0][1]

        while not '.'.join(namespace+[var]) in self.memory.keys():
            try:
                namespace.pop()
            except IndexError:
                self.error(command,f'Переменная "{var}" не существует в текущем контексте')
        else:
            if not (self.memory['.'.join(namespace+[var])]['public'] or namespace == self.memory['.'.join(namespace+[var])]['namespace']):
                self.error(command,f'{var} не является публичной переменной')
        namespace.append(var)

        if self.memory['.'.join(namespace)]['value'] in {-1,0,1}:
            self.memory['.'.join(namespace)]['value'] = {
                0 : 1,
                1 : -1,
                -1 : 0
            }[ self.memory['.'.join(namespace)]['value'] ]
        else:
            self.error(command,f'Оператор @ можно использовать только с kleene-значениями')

        #log('\t\t'+str({0 : 1, 1 : -1, -1 : 0}[ self.memory['.'.join(namespace)]['value'] ]))
    

    def INDEX(self,*command,namespace=[]):
        #INDEX to from index
        ...

    def get_memory(self):
        for key in self.memory.keys():
            print(key,': ',self.memory[key])
    
    def error(self,command,msg:str) -> None:
        if type(msg) == Error:
            sys.stdout.write(str(msg))
        else:
            sys.stdout.write(f'\nОшибка интерпретации на строке {command[1]}. {msg}\n{command[2]}')
        sys.exit(1)

    def run(self):
        while not self.end:
            self.handler()
            self.advance()
            pprint(self.memory)
        logFile.close()
            

