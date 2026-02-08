from UUtoken import Token
import sys
#🥳🥳🥳🥳🥳🥳🥳

def print(*x,end='\n'): ...

#
#   Базовые классы
#

class ZeroNode:
    def __init__(self,operator):
        self.operator = operator
    def __repr__(self):
        return f'({self.operator})'
    def cool_repr(self,deep:int=0):
        return '\t'*deep+str(self.operator)

class UnarNode:
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand
    def __repr__(self):
        return f'({self.operator}:{self.operand})'
    #TODO написать cool_repr

class BinaryNode:
    def __init__(self,operator,main,secondary,line):
        self.operator = operator
        self.main = main
        self.secondary = secondary
        self.line = line
    def __repr__(self):
        return f'({self.operator}:({self.main},{self.secondary}))'

class TernaryNode:
    def __init__(self,operator,main,secondary,tertiary):
        self.operator = operator
        self.main = main
        self.secondary = secondary
        self.tertiary = tertiary
    def __repr__(self):
        return f'({self.operator}:({self.main},{self.secondary},{self.tertiary}))'

class TypeNode:
    def __init__(self,token,line:int=0):
        self.token = token
        self.line = line
    def __repr__(self):
        return f'{self.token}'

class NumberNode(TypeNode): ...

class IDNode(TypeNode): ...

class StringNode(TypeNode): ...

#
#   Классы первого порядка
#

class NESTING_END(ZeroNode):
    def __init__(self,line):
        self.operator = 'NESTING_END'
        self.line = line
    def __repr__(self):
        return f'({self.operator})'

class COMMAND(UnarNode):
    def __init__(self, command,line):
        self.operator = 'COMMAND'
        self.operand = command
        
        self.line = line

class NAMESPACE(UnarNode):
    def __init__(self, name, line):
        self.operator = 'NAMESPACE'
        self.operand = name

        self.line = line
        
class DELETE(UnarNode):
    def __init__(self, name, line):
        self.operator = 'DELETE'
        self.operand = name

        self.line = line

class IF(UnarNode):
    def __init__(self, condition,line=0):
        self.operator = 'IF'
        self.operand = condition
        
        self.line = line

class ELSE_IF(UnarNode):
    def __init__(self, condition,line=0):
        self.operator = 'ELSE_IF'
        self.operand = condition
        
        self.line = line
        
class ELSE(ZeroNode):
    def __init__(self,line=0):
        self.operator = 'ELSE'
        self.line = line
        
class CALL(BinaryNode):
    def __init__(self,func,args):
        self.operator = 'CALL'
        self.main = func
        self.secondary = args

class VAR(BinaryNode):
    def __init__(self,name,value,line):
        self.operator = 'ASSIGMENT'
        self.main = name
        self.secondary = value
        self.line = line

class VAR_DECLARATION(TernaryNode):
    def __init__(self,name,vtype,properties:dict,line):
        self.operator = 'DECLARATION'
        self.main = name
        self.secondary = vtype
        self.tertiary = properties
        self.line = line

class FUNCTION(BinaryNode):
    def __init__(self,name,args,rtype=None,line=0,public=False):
        self.operator = 'FUNCTION'
        self.main = name
        self.secondary = args
        self.rtype = rtype
        self.line = line
        self.public = public
        
class RETURN(UnarNode):
    def __init__(self,expr,line):
        self.operator = 'RETURN'
        self.operand = expr
        self.line = line

class WHILE(UnarNode):
    def __init__(self, condition,line=0):
        self.operator = 'WHILE'
        self.operand = condition
        
        self.line = line

class CONTINUE(ZeroNode):
    def __init__(self, line=0):
        self.operator = 'CONTINUE'
        
        self.line = line

class BREAK(ZeroNode):
    def __init__(self, line=0):
        self.operator = 'BREAK'
        
        self.line = line

class CONNECT(UnarNode):
    def __init__(self, module, line = 0):
        self.operator = 'CONNECT'
        self.operand = module

        self.line = line

class LIST(UnarNode):
    def __init__(self,value,line):
        self.operator = 'LIST'
        self.operand = value
        self.line = line

#
#   Логика
#

class Parser:
    def __init__(self,tokens,src):
        self.tokens = tokens
        self.index = -1
        self.current_token : Token = None
        self.end = False
        self.ast = []
        self.src = src
        self.current_line = ''
        self.errors = []
        self.if_st = False
        self.types = 'int float infinity string kleene function any'.split()
        self.const = False
        self.checked = False
        self.public = False

        self.advance()
        
    def advance(self):
        self.index += 1
        if self.index < len(self.tokens):
            self.current_token = self.tokens[self.index]
            self.current_line = self.src.split('\n')[self.current_token.line]
            #while len(self.current_line) > 0 and self.current_line[0] == ' ': self.current_line = self.current_line[1:]
        else:
            self.end = True
        return self.current_token
        
    def factor(self):
        token = self.current_token
        
        if token.ttype == 'MATH' and token.value == '-':
            self.advance()
            return BinaryNode(token,NumberNode(Token('INT','0',token.line)),self.factor(),self.current_line)
        
        elif token.ttype == 'BOOL':
            if token.value == '!':
                self.advance()
                return UnarNode(token,self.factor())
            elif token.value == '@':
                self.advance()
                return UnarNode(token,self.factor())
        
        elif token.ttype in ('INT','FLOAT','ID','STRING'):
            #if token.ttype == 'ID' and token.value =='infinity': return InfinityNode()
            factor = self.current_token
            self.advance()
            return NumberNode(factor,self.current_token.line) if token.ttype in ('INT','FLOAT') else\
                   IDNode(factor,self.current_token.line)     if token.ttype == 'ID'  else\
                   StringNode(factor,self.current_token.line)# if token.ttype == 'STR' else None
        
        elif token.ttype == 'CALL':
            if self.index + 1 >= len(self.tokens):
                self.errors.append(f'Ожидалось имя на строке {self.current_token.line+1}.\n"{self.current_line}"')
                return self.errors
            #name = self.tokens[self.index+1]
            call = self.get_call()
            if (self.current_token.ttype,self.current_token.value) == ('BRACKET',')'): self.advance()
            
            return call
                
        elif token.ttype == 'BRACKET' and token.value == '(':
            self.advance()
            expr = self.expr()
            print(self.current_token)
            if self.current_token.ttype == 'BRACKET' and self.current_token.value == ')':
                self.advance()
                return expr
            else:
                self.errors.append(f'Пропущена ")" на строке {self.current_token.line+1}.\n"{self.current_line}"')
                return self.errors
        elif token.ttype == 'BRACKET' and token.value == '[':
            #print(self.current_token)
            expr = []
            line = self.current_token.line
            count = 1
            while count != 0:
                print(self.current_token)
                if self.current_token.ttype == 'BRACKET' and self.current_token.value == ']': count -= 1
                #elif self.current_token.ttype == 'BRACKET' and self.current_token.value == '[': count += 1

                if self.end and count != 0:
                    print(count)
                    self.errors.append(f'Пропущена "]" на строке {line+1}.\n"{line}"')
                    return self.errors
                
                
                self.advance()
                

                
                
                #if self.current_token.ttype == 'COMMA': self.advance()
                expr.append(self.expr())
                
                
            for i in range(len(expr)):
                if expr[i] == None:
                    expr.pop(i)
            return LIST(expr,self.current_token.line)
            
                

    def term(self):
        return self.bin_op(self.factor,['-','*','/','&','**','!','mod','div'])
    
    def expr(self):
        return self.bin_op(self.term,['+','-','|','=','$','==','>','<','>=','<=','?'])
    
    def bin_op(self,func,ops):
        line = self.current_token.line
        left = func()
        while self.current_token.value in ops:
            op_token = self.current_token
            self.advance()
            right = func()
            left = BinaryNode(op_token,left,right,line)
        return left

    def check(self):
        self.checked = True
        if self.current_token.ttype == 'ID':
            if self.current_token.value == 'public':
                self.public = True
            elif self.current_token.value == 'private':
                self.public = False
            elif self.current_token.value in 'new pls'.split():
                nullable = {'pls':True,'new':False}[self.current_token.value]
                const = False
                if self.advance().value == 'const':
                    const = True
                    self.advance()
                

                name = self.current_token.value
                self.advance()
                
#   VARIABLEs
                if self.current_token.ttype == 'COLON':
                    if self.advance().value not in self.types:
                        self.errors.append(f'VAR. Ожидался действительный тип после ":" на строке {self.current_token.line+1}.\n"{self.current_line}"')
                        return self.errors
                    vtype = self.current_token
                    if self.advance().ttype == 'BRACKET' and self.current_token.value == '[':
                        vtype.value = f'list{vtype.value}'
                        if not ( self.advance().ttype == 'BRACKET' and self.current_token.value == ']' ):
                            self.errors.append(f'VAR. Внутри квадратных скобок при объявлении массива не должно быть ничего на строке {self.current_token.line+1}.\n"{self.current_line}"')
                            return self.errors
                        self.advance()
                    self.ast.append(VAR_DECLARATION(name,vtype,{'nullable':nullable,'const':const,'public':self.public},self.current_token.line))
                    self.public = False
                    
                    
                    if self.current_token.ttype == 'ASSIGMENT':                        
                        line = self.current_token.line
                        self.advance()
                        value = self.expr()
                        self.ast.append(VAR(name,value,line))
                    if self.current_token.ttype != 'END': 
                        self.index -= 1

#   FUNCTIONs  
                else:
                    args = []
                    rtype = 'null'
                    
                    if self.current_token.ttype != 'ASSIGMENT':
                        if self.current_token.ttype == 'BRACKET' and self.current_token.value == '(':
                            while not (self.current_token.ttype == 'BRACKET' and self.current_token.value == ')'):
                                self.advance()
                                #print(self.current_token)
                                if self.current_token.ttype == 'ID':
                                    args.append(self.current_token)
                                elif self.current_token.ttype == 'BRACKET' and self.current_token.value == ')':
                                    break
                                

                            if self.advance().ttype == 'ARROW' and self.current_token.value == '->':
                                if self.advance().ttype != 'ID':
                                    self.errors.append(f'FUNCTION. Ожидался действительный тип после "->" на строке {self.current_token.line+1}.\n"{self.current_line}"')
                                rtype = self.current_token.value
                                self.advance()
                            self.advance()

                        elif self.current_token.ttype == 'ARROW':
                            while not self.current_token.ttype == 'ASSIGMENT':
                                if self.current_token.ttype == 'ID':
                                    args.append(self.current_token)

                                elif self.current_token.ttype == 'ARROW' and self.current_token.value == '->':
                                    if self.advance().ttype != 'ID':
                                        self.errors.append(f'FUNCTION. Ожидался действительный тип после "->" на строке {self.current_token.line+1}.\n"{self.current_line}"')
                                    rtype = self.current_token.value
                                self.advance()

                                if self.current_token.value == '{':
                                    self.errors.append(f'FUNCTION. Ожидалось "=", но получено "{self.current_token.value}" на строке {self.current_token.line+1}.\n"{self.current_line}"')
                                    return self.errors
                        
                    # аргументы определяются верно :)
                    if self.current_token.ttype == 'ASSIGMENT': self.advance()
                    if not (self.current_token.ttype == 'BRACKET' and self.current_token.value == '{'):
                        
                        self.errors.append(str('FUNCTION. Ожидалось "{", но получено ' + f'"{self.current_token.value}"'+' на строке '+str(self.current_token.line+1)+f'\n{self.current_line}'))
                        return self.errors
                    self.ast.append(FUNCTION(name,args,rtype,self.current_token.line,self.public))
                    self.public = False
                    

#   DELETE
            elif self.current_token.value in ('delete','reset'):
                name = self.advance()
                if self.advance().ttype != 'END':
                    self.errors.append(f'DELETE. Ожидалось ";" или ничего на строке {self.current_token.line+1}.\n{self.current_line}')
                    return self.errors
                self.ast.append(DELETE(name,self.current_token.line))

#   NAMESPACEs
            elif self.current_token.value in {'namespace','object'}:
                name = self.advance()
                self.ast.append(NAMESPACE(name,self.current_token.line))

#   COMTINUEs
            elif self.current_token.value == 'continue':
                self.ast.append(CONTINUE(self.current_token.line))

#   BREAKs
            elif self.current_token.value in {'breakdance','breakcore','break','stop'}:
                self.ast.append(BREAK(self.current_token.line))

#   RETURNs
            elif self.current_token.value == 'return':
                line = self.current_token.line
                self.advance()
                self.ast.append(RETURN(self.expr(),line))
#   CONNECTs
            elif self.current_token.value == 'connect':
                line = self.current_token.line
                self.advance()
                self.ast.append(CONNECT(self.current_token,line))
                                                        
#   IF-STATEMENTs
            elif self.current_token.value == 'if':
                token = self.current_token
                if self.advance().value != '(':
                    self.errors.append(f'IF-STATEMENT. Ожидалось "(" на строке {self.current_token.line+1}:\n{self.current_line}')
                    return self.errors

                conditions = self.expr()
                
                    
                        
                if self.current_token.value == '{':
                    self.errors.append(f'IF-STATEMENT. Ожидалось "run" на строке {self.current_token.line+1}:\n{self.current_line}')
                    return self.errors
                
                if self.advance().ttype == 'CALL':
                    self.if_st = True
                elif self.current_token.value != '{':
                    self.errors.append(str('IF-STATEMENT. Ожидалось "{" на строке '+str(self.current_token.line+1)+f'\n{self.current_line}'))
                    return self.errors
                
                self.ast.append(IF(conditions,token.line))

            elif self.current_token.value == 'else':
                token = self.advance()
                if token.value == 'if':
                    
                    if self.advance().value != '(':
                        self.errors(f'IF-STATEMENT. Ожидалось "(" на строке {self.current_token.line+1}:\n{self.current_line}')

                    conditions = self.expr()
                    

                    if self.current_token.value != 'run':
                        self.errors.append(str(f'IF-STATEMENT. Ожидалось "run", но получено {self.current_token.value} на строке '+str(self.current_token.line+1)+f'\n{self.current_line}'))

                    self.advance()

                    if self.current_token.ttype == 'CALL':
                        self.if_st = True
                    elif self.current_token.value != '{':
                        self.errors.append(str('IF-STATEMENT. Ожидалось "{" на строке '+str(self.current_token.line+1)+f'\n{self.current_line}'))
                        return self.errors
                    
                    self.ast.append(ELSE_IF(conditions,token.line))
                else:
                    self.ast.append(ELSE(token.line))

#   WHILE
            elif self.current_token.value == 'while':
                token = self.current_token
                if self.advance().value != '(':
                    self.errors.append(f'WHILE. Ожидалось "(" на строке {self.current_token.line+1}:\n{self.current_line}')
                    return self.errors

                conditions = self.expr()
                
                    
                        
                if self.current_token.value == '{':
                    self.errors.append(f'WHILE. Ожидалось "run" на строке {self.current_token.line+1}:\n{self.current_line}')
                    return self.errors
                
                if self.advance().ttype == 'CALL':
                    self.if_st = True
                elif self.current_token.value != '{':
                    self.errors.append(str('WHILE. Ожидалось "{" на строке '+str(self.current_token.line+1)+f'\n{self.current_line}'))
                    return self.errors
                
                self.ast.append(WHILE(conditions,token.line))       

#   VARIABLEs
            else:
                name = self.current_token
                line = self.current_token.line
                if self.advance().ttype == 'ASSIGMENT':
                    assigment = self.current_token
                    self.advance()
                    if assigment.value == '=':
                        value = self.expr()
                        self.ast.append(VAR(name,value,line))
                    elif assigment.value in ('+=','-=','*=','/='):
                        op = assigment.value[0]
                        self.tokens = self.tokens[:self.index] + [name,Token('MATH',op,line)] + self.tokens[self.index:]
                        self.index -= 1
                        print(self.advance())
                        value = self.expr()
                        self.ast.append(VAR(name,value,line))
                else:
                    self.errors.append(f'ASSIGMENT. Ожидалось "=" на строке {self.current_token.line+1}:\n{self.current_line}')
                    return self.errors
#   NESTING MINUS
        elif self.current_token.ttype == 'BRACKET' and self.current_token.value == '}':
            self.ast.append(NESTING_END(self.current_token.line))

        elif self.current_token.ttype == 'END' and self.if_st:
            self.ast.append(NESTING_END(self.current_token.line))
            self.if_st = False

#   CALL
        elif self.current_token.ttype == 'CALL':
            self.ast.append(self.get_call())
        
        

            
        '''
#   MINECRAFT COMMANDs
        elif self.current_token.ttype == 'COMMAND':
            self.ast.append(COMMAND(self.current_token.value,self.current_token.line))
        '''

        self.advance()
        if not self.end:
            self.check()
    
    def get_call(self):
        #index = self.index
        name = self.advance()
        
        if name.ttype != 'ID':
            self.errors.append(f'CALL. Ожидалось действительное имя на строке {self.current_token.line+1}.\n{self.current_line}')
            return self.errors
        token = self.advance()
        
        args = []
        #   без аргументов
        if token.ttype == 'END':
            
            ret = CALL(name,[])
            self.index -= 1
        else:
            # с аргументами
            if token.ttype == 'BRACKET' and token.value == '(':
                self.advance()
                while not (self.current_token.ttype == 'BRACKET' and self.current_token.value == ')'):
                    arg = self.expr()
                    #self.advance()
                    if arg != None: args.append(arg)
                    
                    
                    if self.current_token.ttype == 'END':   break
                    elif self.current_token.ttype == 'COMMA': self.advance()
                    #if self.current_token.ttype != 'COMMA':
                    #    args.append(self.current_token)
                    
                    
                #self.advance()
        
            elif self.current_token.ttype == 'ARROW':
                self.advance() # <-
                
                while not self.current_token.ttype == 'END':
                    
                    args.append(self.expr())
                    if self.current_token.ttype == 'COMMA': self.advance()
            
            #self.tokens = self.tokens[:self.index+1] + [Token('END',';',self.current_token.line)] + self.tokens[self.index+1:]
            
            ret = CALL(name,args)
            #self.index = index

        
        
        return ret
            

    def get_ast(self) -> list:
        if not self.checked: self.check()
        if len(self.errors) > 0:
            return [self.errors[0],self.current_token.line,self.current_line]
        else:
            return []
    
    def run(self):
        if not self.checked: self.check()
        return self.ast