from UUlexer import lexer
from UUparser import Parser
from UUgenerator import Generator
from UUvirtual import SkatVirtualMachine as SVM
import UUshell
from UUerror import Error
import time

TIMECHECK = True
#def print(*x,end=''): ...

def main(src):# = input('Введите имя файла:\t')):
    #'''
    code = open(src,encoding='utf-8').read()
    if code.replace(' ','').replace('\n','') == '': return 'Файл пуст'

    tokens = lexer(code)

    
    
    
    if tokens == False: return 'Ошибка на этапе лексического анализа'
    if len(tokens) == 0: return 'Файл пуст'
    

    print('\n'.join(f'{str(i)}' for i in tokens))

    
    print(f"\n{'='*20}\nНОДЫ\n{'='*20}\n")
    
    ast = Parser(tokens,code)
    ast_err = ast.get_ast()
    
    
    
    if len(ast.errors) > 0:
        print(ast_err[0],end='')     
        return '\nОшибка на этапе синтаксического анализа'
    
    ast = ast.run()
    
    
    
    print('\n'.join(str(i) for i in ast))
    
    print(f"{'='*20}\nЩЕРБЕТ\n{'='*20}")
    code = Generator(ast,code).run()
    
    for c in range(len(code)): print(code[c])
    
    
    print(f"{'='*20}\nВЫВОД\n{'='*20}")
    '''if type(code := UUshell.compile('code.uivc')) == Error:
        return code'''
    svm = SVM(code).run()
    

    return 'Работа завершена успешно'

if __name__ == '__main__':
    start = time.time()
    print(main(src='examples/fake_moneta.uivc'))
    #print(main(src='examples/test.uivc'))
    #print(main(src='code.uivc'))
    #print(main(src='examples/all.uivc'))
    #print(main(src='examples/array.uivc'))
    #print(main(src='new_code.uivc'))
    if TIMECHECK: print(f'Программа завершилась за {time.time()-start} секунд')