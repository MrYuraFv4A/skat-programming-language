import sys
from UUtoken import Token
from copy import deepcopy
from UUparser import *

del Parser #   По-приколу, чтоб место в памяти не занимал, лол

def print(*x,end='\n'): ...

#№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№
#   КОНСТАНТЫ
#№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№

operations_toggle = {
    '+' : 'add',
    '-' : 'remove'
}
operations = {
    '-' : 'add',
    '+' : 'remove'
}

#№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№
#   ЛОГИКА
#№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№

class Queue:
    def __init__(self):
        self.value = []
        self.reasons = []

    def add(self,x,reason = ''):
        self.value = [x] + self.value
        self.reasons = [reason] + self.reasons

    def get(self) -> any:
        return self.value.pop(), self.reasons.pop()

    def __repr__(self):
        return str(self.value)

class Stack(Queue):
    def __init__(self):
        self.value = []

    def add(self,x):
        print('\t'*8,'COND ADDED')
        self.value.append(x)
    
    def get(self) -> any:
        print('\t'*8,'COND GOT')
        return self.value.pop()


class Generator:
    def __init__(self,ast,src):
        self.ast = ast
        self.end = False
        self.code = []
        self.toggle = False
        self.src = src
        
        self.stack = Queue()
        self.nesting = Stack()
        self.temp = -1
        self.index = -1
        self.line = 0
        self.const = False

        #self.namespace = ''
        self.previndex = 0
        self.current_ast = None
        
        

        self.advance()

    def advance(self):
        self.previndex = self.index
        self.index += 1
        if self.index < len(self.ast):
            self.current_ast = self.ast[self.index]
        else:
            self.end = True
        return self.current_ast

    def get_temp(self) -> str:
        self.temp += 1
        self.stack.add(f'VAR `temp{self.temp} any',(self.line+1,self.src.split('\n')[self.line]))
        self.stack.add(f'SETNULLABLE `temp{self.temp}',(self.line+1,self.src.split('\n')[self.line]))
        return f'`temp{self.temp}'
    
    def get_call(self,expr):
        line = self.set_line(expr)
        sec = deepcopy(expr.secondary)
        args = []
        temp_int = -1
        for arg in sec:
            #print(arg,type(arg))
            if      type(arg) in (IDNode,NumberNode):          args.append(arg.token.value)
            elif    type(arg) == StringNode:                            args.append(f'"{arg.token.value}"')

            else: #epression
                temp = self.get_temp()
                temp_int = self.temp
                self.re_expr(arg,temp)
                args.append(temp)

        self.stack.add(f'CALL {expr.main.value} '+' '.join(str(i) for i in args),(line+1,self.src.split('\n')[line]))
        if temp_int != -1: self.clear_temp(temp_int)

    def format_name(self,value) -> str:
        if type(value) == Token:
            name = f'{value.value}'
        elif type(value) == str:
            name = value
        #elif '.' in str(value):   name = ' '.join(str(i) for i in str(value).split('.')[::-1])
        #elif str(value).count(' ') == 1:   name = value
        else:                              self.error(f'Ошибка на этапе семантического анализа на строке {self.line+1}. Недопустимое количество точек в имени "{name}"\n\t{self.src.split('\n')[self.line]}')
        
        return name

    def set_line(self,expr) -> int:
        #print(f'VISIT set_line, expr = {expr}, line = "',end='')
        try:
            self.line = expr.main.line
        except AttributeError:
            try:
                self.line = expr.line
            except AttributeError:
                self.line = expr.operand.line
        #print(f'{self.line}"')
        return self.line

    def clear_temp(self,stop=0) -> None:
        while self.temp  > stop - 1:
                self.stack.add(f'FREE `temp{self.temp}',(self.line+1,self.src.split('\n')[self.line]))
                self.temp -= 1
    
    def re_binop(self, name : str, op : str, cur):
        print(f'\n\tVisit re_binop: {cur} {op} {self.toggle}')
        line = self.line
        self.set_line(cur)
        name = self.format_name(name)
        if type(cur) == StringNode and cur.token.value[0] != '"': cur.token.value = f'"{cur.token.value}"'
        if type(cur) == UnarNode:
            if cur.operator.value == '!':
                print(f'\t\tVisit re_binop.UnarNode: {cur}')
                self.re_expr(cur.operand, name)
                self.stack.add(f'NOT {name}',(self.line+1,self.src.split('\n')[self.line]))
            elif cur.operator.value == '@':
                print(f'\t\tVisit re_binop.UnarNode: {cur}')
                self.re_expr(cur.operand, name)
                self.stack.add(f'OTHER {name}',(self.line,self.src.split('\n')[self.line-1]))

        elif type(cur) in (NumberNode,IDNode,StringNode):
            print(f'\t\tVisit re_binop.NumberNode: {cur}')
            if      op == '+':
                if not self.toggle: self.stack.add(f'ADD {name} {str(cur.token.value)}',(line+1,self.src.split('\n')[line]))
                else:               self.stack.add(f'REM {name} {str(cur.token.value)}',(line+1,self.src.split('\n')[line]))

            elif    op == '-':
                if not self.toggle: self.stack.add(f'REM {name} {str(cur.token.value)}',(line+1,self.src.split('\n')[line]))
                else:               self.stack.add(f'ADD {name} {str(cur.token.value)}',(line+1,self.src.split('\n')[line]))
                #self.toggle = not self.toggle

            elif    op in '*/':
                temp = self.get_temp()

                cur_op = 'ADD' if not self.toggle else 'REM'
                self.stack.add(f'{cur_op} {temp} {str(cur.token.value)}',(self.line+1,self.src.split('\n')[self.line]))
                
                #self.re_binop(temp,'+',cur)

                cur_op = 'MUL' if op == '*' else 'DIV'
                self.stack.add(f'{cur_op} {name} {temp}',(self.line+1,self.src.split('\n')[self.line]))
                del cur_op
            
            elif    op == '**':
                temp = self.get_temp()

                cur_op = 'ADD' if not self.toggle else 'REM'
                self.stack.add(f'{cur_op} {temp} {str(cur.token.value)}',(self.line+1,self.src.split('\n')[self.line]))
                
                #self.re_binop(temp,'+',cur)

                cur_op = 'EXP'
                self.stack.add(f'{cur_op} {name} {temp}',(self.line+1,self.src.split('\n')[self.line]))
                del cur_op
            
            elif op == '=':
                self.stack.add(f'EQ {name} {str(cur.token.value)}',(self.line+1,self.src.split('\n')[self.line]))
            elif op == '?':
                self.stack.add(f'INDEX {name} {str(cur.token.value)}',(self.line+1,self.src.split('\n')[self.line]))

            elif op == 'mod':
                self.stack.add(f'MOD {name} {str(cur.token.value)}',(self.line+1,self.src.split('\n')[self.line]))
            elif op == 'div':
                self.stack.add(f'IDIV {name} {str(cur.token.value)}',(self.line+1,self.src.split('\n')[self.line]))

            else:
                cur_op = self.get_op(op)
                print(op,cur_op)
                self.stack.add(f'{cur_op} {name} {str(cur.token.value)}',(self.line+1,self.src.split('\n')[self.line]))
                del cur_op
            #elif op == '!': self.stack.add(f'NOT {name}',(self.line+1,self.src.split('\n')[self.line]))

        
        elif type(cur) == BinaryNode:
            print(f'\t\tVisit re_binop.BinaryNode: {cur}')
            temp = self.get_temp()
            self.re_expr(cur, temp)
            cur_op = self.get_op(op)
            self.stack.add(f'{cur_op} {name} {temp}',(line+1,self.src.split('\n')[line]))
        
        elif type(cur) == CALL:
            print(f'\t\tVisit re_binop.CALL: {cur}')
            cur_op = self.get_op(op)
            self.get_call(cur)
            self.stack.add(f'{cur_op} {name} {cur.main.value}',(line+1,self.src.split('\n')[line]))
        
        return None

    def get_op(self,op):
        return  {
            '*' :   'MUL',
            '/' :   'DIV',
            '+' :   'ADD',
            '-' :   'REM',
            '**':   'EXP',
            '&' :   'AND',
            '|' :   'OR',
            '=':   'EQ',
            '>' :   'BIG',
            '<' :   'SMALL',
            '>=':   'BIGEQ',
            '<=' :   'SMALLEQ',
            '?' :   'INDEX',
            '@' : 'OTHER',
        }[op]

    def re_expr(self,expr,name=''):
        print(f'\n\tVisit re_expr: {expr} {name}')

        if type(expr) == StringNode:
            if expr.token.value == '':          expr.token.value = f'""'
            elif expr.token.value[0] != '"':    expr.token.value = f'"{expr.token.value}"'
        
        
        line = self.set_line(expr)
        name = self.format_name(name)
        
        
        if type(expr) == VAR:
            print(f'\t\tVisit re_expr.VAR: {name} {expr}')
            
            name = self.format_name(expr.main)

            
            if type(expr.secondary) != LIST:
                temp = self.get_temp()
                stop = self.temp
                
                self.re_expr(expr.secondary,temp)
                self.stack.add(f'SET {name} {temp}',(line+1,self.src.split('\n')[line]))
                
                if self.const:
                    self.stack.add(f'SETCONST {name}',(line+1,self.src.split('\n')[line]))
                    self.const = False
        

                self.clear_temp(stop)
            
            else:
                self.re_expr(expr.secondary,name)
                
            
            
            
        
        elif type(expr) == VAR_DECLARATION:
            print(f'\t\tVisit re_expr.VAR_DECLARATION: {expr}')
            
            name = self.format_name(expr.main)
            self.stack.add(f'VAR {name} {expr.secondary.value}',(line+1,self.src.split('\n')[line]))
            
            if expr.tertiary['const']:
                self.const = True
            if expr.tertiary['nullable']:
                self.stack.add(f'SETNULLABLE {name}',(line+1,self.src.split('\n')[line]))
            if expr.tertiary['public']:
                self.stack.add(f'SETPUBLIC {name}',(line+1,self.src.split('\n')[line]))
            
        elif type(expr) == NAMESPACE: 
            print(f'\t\tVisit re_expr.NAMESPACE: {expr}')
            #self.namespace = expr.operand.value
            self.stack.add(f'NAMESPACE {expr.operand.value}',(self.line+1,self.src.split('\n')[self.line]))
            self.nesting.add(expr)
        
        elif type(expr) == CONTINUE: 
            print(f'\t\tVisit re_expr.CONTINUE: {expr}')
            self.stack.add(f'CONTINUE',(self.line+1,self.src.split('\n')[self.line]))
        
        elif type(expr) == BREAK: 
            print(f'\t\tVisit re_expr.BREAK: {expr}')
            self.stack.add(f'BREAK',(self.line+1,self.src.split('\n')[self.line]))
        
        elif type(expr) == CONNECT:
            print(f'\t\tVisit re_expr.CONNECT: {expr}')
            self.stack.add(f'CONNECT {expr.operand.value}',(self.line+1,self.src.split('\n')[self.line]))
        
        elif type(expr) == FUNCTION:
            print(f'\t\tVisit re_expr.FUNCTION: {expr}')
            #if type(self.path[-1]) == FUNCTION: self.error(f'Ошибка на этапе семантического анализа на строке {self.line}. Запрещено объявлять функции внутри функций\n\t{self.srcself.line,(.split('\n')[self.line]}'))

            self.nesting.add(expr)
            #self.path.append(f'{expr.main.value}.mcfunction')
            
            #self.stack.add(['file','/'.join(self.path)])
            #print(self.line)
            self.stack.add(f'FUNC {expr.main} {expr.rtype} '+' '.join(t.value for t in expr.secondary),(self.line+1,self.src.split('\n')[self.line]))
        
        elif type(expr) == IF:
            self.nesting.add(expr)
            line = self.set_line(expr)

            self.re_expr(expr.operand,temp:=self.get_temp())
            self.stack.add(f'IF {temp}',(line+1,self.src.split('\n')[line]))
        
        elif type(expr) == ELSE:
            self.nesting.add(expr)
            line = self.set_line(expr)
            

            self.stack.add(f'ELSE',(line+1,self.src.split('\n')[line]))
            self.stack.add(f'PASS',(line+1,self.src.split('\n')[line]))
        
        elif type(expr) == ELSE_IF:
            self.nesting.add(expr)

            print(self.nesting.value)
            line = self.set_line(expr)
            
            self.re_expr(expr.operand,temp:=self.get_temp())
            

            self.stack.add(f'ELSE_IF {temp}',(line+1,self.src.split('\n')[line]))           
        
        elif type(expr) == NESTING_END:
            #print(self.ast[self.previndex], self.ast[self.ast.index(expr)])
            print(f'\t\tVisit re_expr.NESTING_END: {expr}')
            print(self.nesting.value)
            
            if self.nesting.value == []:
                self.error(f'Ошибка на этапе семантического анализа на строке {self.line+1}. Непарная фигурная скобка\n\t{self.src.split('\n')[self.line]}')
            
            current_nesting = self.nesting.get()
            print(type(current_nesting))
            
            if type(current_nesting) == FUNCTION:
                self.stack.add(f'END {current_nesting.operator} {current_nesting.main}',(self.line+1,self.src.split('\n')[self.line]))
                if current_nesting.public: self.stack.add(f'SETPUBLIC {current_nesting.main}',(current_nesting.line+1,self.src.split('\n')[current_nesting.line]))
            elif type(current_nesting) == NAMESPACE:
                self.stack.add(f'END {current_nesting.operator} {current_nesting.operand.value}',(self.line+1,self.src.split('\n')[self.line]))
            elif type(current_nesting) == ELSE or type(current_nesting) in (IF,ELSE_IF):# and not (self.index + 1 < len(self.ast) and type(self.ast[self.index + 1]) in (ELSE,ELSE_IF)):
                self.stack.add(f'ENDIF',(self.line+1,self.src.split('\n')[self.line]))
            elif type(current_nesting) == WHILE:
                self.stack.add(f'ENDIF',(self.line+1,self.src.split('\n')[self.line]))
                self.stack.add(f'PASS',(self.line+1,self.src.split('\n')[self.line]))
                self.stack.add(f'ELSE',(self.line+1,self.src.split('\n')[self.line]))
                self.stack.add(f'PASS',(self.line+1,self.src.split('\n')[self.line]))
                self.stack.add(f'EXITWHILE',(self.line+1,self.src.split('\n')[self.line]))
                self.stack.add(f'ENDIF',(self.line+1,self.src.split('\n')[self.line]))
                self.stack.add(f'END WHILE',(self.line+1,self.src.split('\n')[self.line]))

            del current_nesting
        
        elif type(expr) == CALL:
            self.get_call(expr)
            if name != '':
                self.stack.add(f'SET {name} {expr.main.value}',(self.line+1,self.src.split('\n')[self.line]))

        elif type(expr) == RETURN:
            print(f'\t\tVisit re_expr.RETURN: {expr}')

            line = self.set_line(expr)
            temp = self.get_temp()
            self.re_expr(expr.operand,temp)
            self.stack.add(f'RETURN {temp}',(line+1,self.src.split('\n')[line]))
        
        elif type(expr) == WHILE:
            self.nesting.add(expr)
            line = self.set_line(expr)

            self.stack.add(f'WHILE',(line+1,self.src.split('\n')[line]))    # Начало цикла
            self.re_expr(expr.operand,temp:=self.get_temp())                # Получение актуального состояния
            
            self.stack.add(f'IF {temp}',(line+1,self.src.split('\n')[line]))       # В случае  положительнго состояния

            #   Далее добавляем тело

        elif type(expr) in (NumberNode,IDNode,StringNode):
            print(f'\t\tVisit re_expr.NumberNode: {expr}')
            self.re_binop(name, '+', expr)
        
        elif type(expr) == LIST:
            print(f'\t\tVisit re_expr.LIST: {expr}')

            i = -1
            for el in expr.operand:
                i += 1
                self.stack.add(f'VAR {name}.{i} any',(line+1,self.src.split('\n')[line]))
                self.re_expr(el,f'{name}.{i}')
                if self.const:
                    self.stack.add(f'SETCONST {name}.{i}',(line+1,self.src.split('\n')[line]))

            
            self.re_binop(name, '+', expr)
        
        elif type(expr) == UnarNode:
            print(f'\t\tVisit re_expr.UnarNode: {expr}')
            self.re_binop(name, expr.operator.value, expr)
        
        elif type(expr) == BinaryNode:
            print(f'\t\tVisit re_expr.BinaryNode: {expr}')

            if expr.operator.value in '+*/':
                if expr.operator.value in '*/': self.stack.add(f'SET {name} 1',(self.line+1,self.src.split('\n')[self.line]))

                if expr.operator.value == '/':  self.re_binop(name, '*', expr.main)
                else:                           self.re_binop(name, expr.operator.value, expr.main)
                self.re_binop(name, expr.operator.value, expr.secondary)
            
            elif expr.operator.value == '**':
                #self.stack.add(f'SET {name} 1',(self.line+1,self.src.split('\n')[self.line]))
                self.re_binop(name, '+', expr.main)

                self.re_binop(name, expr.operator.value, expr.secondary)

            elif expr.operator.value == '-':
                self.re_binop(name, '+', expr.main)
                self.toggle = not self.toggle
                self.re_binop(name, '+', expr.secondary)
                self.toggle = not self.toggle
            
            elif expr.operator.value == '=':
                self.re_binop(name, '+', expr.main)
                self.re_binop(name, expr.operator.value, expr.secondary)

            elif expr.operator.value in '|&':
                
                if expr.operator.value == '&': self.stack.add(f'SET {name} 1',(self.line+1,self.src.split('\n')[self.line]))

                self.re_binop(name, expr.operator.value, expr.main)
                self.re_binop(name, expr.operator.value, expr.secondary)
            
            elif expr.operator.value in '> < >= <='.split():
                self.re_binop(name, '+', expr.main)
                

                self.re_binop(name, expr.operator.value, expr.secondary)

            elif expr.operator.value == '?': # WIP
                self.re_binop()
                self.re_binop(expr.main, '?', expr.secondary)
            
            elif expr.operator.value in {'mod','div'}:
                self.stack.add(f'SET {name} 1',(self.line+1,self.src.split('\n')[self.line]))

                
                self.re_binop(name, '*', expr.main)

                self.re_binop(name, expr.operator.value, expr.secondary)

                
                
            else:
                self.error(f'Недействительный оператор {expr.operator.value}')

    def error(self,msg):
        sys.stderr.write(msg)
        exit()
    
    def run(self):
        while not self.end:
            self.re_expr(self.current_ast)
            
            self.advance()
        
        #print(self.stack.Length)
        
        for i in range(len(self.stack.value)):
            self.code.append(self.stack.get())

        
        return self.code