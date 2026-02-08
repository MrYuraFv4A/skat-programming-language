from UUlexer import lexer
from UUparser import Parser
from UUgenerator import Generator
from UUerror import Error



def compile(file):
    try:
        code = open(file,encoding='utf-8').read()
    except:
        return Error('Файл не существует',file)

    if code.replace(' ','').replace('\n','') == '': return 'Файл пуст'

    tokens = lexer(code)

    if tokens == False: return Error('Ошибка на этапе лексического анализа',file)
    if len(tokens) == 0: return Error('Файл пуст',file)
        
    ast = Parser(tokens,code)
    ast_err = ast.get_ast()
    #print(ast_err)
    
    if len(ast_err) > 0: return Error('\nОшибка на этапе синтаксического анализа(shell)',file,ast_err[1],ast_err[2],ast_err[0])
    
    ast = ast.run()
    
    code = Generator(ast,code).run()
    
    return code