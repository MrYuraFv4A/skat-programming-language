from UUtoken import Token

#lexer
def lexer(src):
    d = {
        '>' : '>',
        '<' : '<',
        '&' : '&',
        '|' : '|',
        '!' : '!',
        '@' : '@',
    }
    tokens = []
    i = 0
    line = 0
    while i < len(src):
        if src[i] == '\n':
            line += 1

        #SPACEs
        if src[i] in '\t ':
            pass

        #CONTINUATION
        elif src[i] == '\\':
            while src[i] in '\\\n':
                i += 1
                if src[i] == '\n':
                    line += 1
            continue
            #tokens.append(Token('CONTINUATION','BACKSLASH',line))

        #COMMENTs
        elif src[i] == '/' and i + 1< len(src) and src[i+1] == '/':
            while i < len(src) and src[i] != '\n':
                i += 1
            line += 1 
        
        elif src[i] == '/' and i + 1< len(src) and src[i+1] == '*':
            preline = line
            i += 2
            while i + 1 < len(src) and  not (src[i] == '*' and src[i+1] == '/'):
                if src[i] == '\n':
                    line += 1
                i += 1
                if i + 1 == len(src):
                    print(f'\nОШИБКА: незакрытый многострочный комментарий на строке {preline+1}\n{preline+1}\t{src.split('\n')[preline]}')
                    return False
            i += 1

        #END
        elif src[i] in '\n;':
            if len(tokens) > 0 and tokens[-1].ttype != 'END' and not (tokens[-1].ttype == 'BRACKET' and tokens[-1].value in '{}') and i + 1 < len(src) and src[i+1] != '{': ############################ end
                tokens.append(Token('END',{';':'SEMICOLON','\n':'NEWLINE'}[src[i]],line))
            else:
                pass
        #COLON
        elif src[i] == ':':
            tokens.append(Token('COLON',':',line))

        #INDEX
        elif src[i] == '?':
            tokens.append(Token('INDEX','?',line))

        #CALL
        elif src[i] == '$':
            tokens.append(Token('CALL','$',line))
        
        #BRACKETs
        elif src[i] in '(){}[]':
            tokens.append(Token('BRACKET',src[i],line))
        
        #SYMBOLs
        elif src[i] == ',':
            tokens.append(Token('COMMA',',',line))

        elif src[i] == '.':
            tokens.append(Token('DOT','.',line))

        #NUMBERs
        elif src[i] in '0123456789': ################################### int
            is_ternary = False
            is_binary = False
            buffer = src[i]
            i += 1
            while i < len(src) and src[i] in '0123456789.tb':
                buffer += src[i]
                if buffer == '0t':
                    is_ternary = True
                    buffer = ''
                elif buffer == '0b':
                    is_binary = True
                    buffer = ''
                i += 1
            if buffer.count('.') > 1:
                print('#'*32,f'\n#\tОШИБКА: при определении числовых значений символ "."(точка) может быть использован только 1 раз\n\t{src.split('\n')[line]}','#'*32)
                return False
            if is_ternary:
                for dig in buffer:
                    if dig not in '012.':
                        print('#'*32,f'\n#\tОШИБКА: недействительное троичное число\n\t{src.split('\n')[line]}','#'*32)
                        return False
                
                fractional = 0
                if len(buffer.split('.')) > 1:
                    exp = 0
                    for dig in buffer.split('.')[1]:
                        exp -= 1
                        fractional += int(dig,3) * 3 ** exp

                buffer = str( int(buffer.split('.')[0],3) + fractional )
            elif is_binary:
                for dig in buffer:
                    if dig not in '01.':
                        print('#'*32,f'\n#\tОШИБКА: недействительное двоичное число\n\t{src.split('\n')[line]}','#'*32)
                        return False
                
                fractional = 0
                if len(buffer.split('.')) > 1:
                    exp = 0
                    for dig in buffer.split('.')[1]:
                        exp -= 1
                        fractional += int(dig,2) * 2 ** exp

                buffer = str( int(buffer.split('.')[0],2) + fractional)
            if '.' not in buffer:
                tokens.append(Token('INT',buffer,line))
            else:
                tokens.append(Token('FLOAT',buffer,line))
            i -= 1
        
        #STRINGs
        elif src[i] == '"':
            i += 1
            buffer = ''
            while i < len(src) and src[i] != '"':
                buffer += src[i]
                i += 1
            tokens.append(Token('STRING',buffer,line))

        #MATH OPs
        elif src[i] in '+-*/':
            #if i + 1 < len(src) and src[i+1] == src[i]:
            #    i += 1
            #    src[i]*=2

            #el
            if i + 1 < len(src) and src[i] == '-' and src[i+1] == '>':
                tokens.append(Token('ARROW','->',line))
                i += 1

            elif i + 1 < len(src) and src[i] == src[i+1]:
                if src[i] in '+-':
                    tokens.append(Token('ASSIGMENT',src[i] + '=',line))
                    tokens.append(Token('INT','1',line))
                elif src[i] == '*':
                    tokens.append(Token('MATH',src[i] * 2,line))
                else:
                    print(f'\n#\tОШИБКА: неизвестный оператор {src[i] + src[i+1]}\n\t{src.split('\n')[line]}')
                    return False
                i += 1

            elif i + 1 < len(src) and src[i+1] == '=':
                if src[i] not in '+-*/':
                    print(f'\n#\tОШИБКА: неизвестный оператор {src[i] + src[i+1]}\n\t{src.split('\n')[line]}')
                    return False
                tokens.append(Token('ASSIGMENT',src[i] + '=',line))
                i += 1

            else:
                tokens.append(Token('MATH',src[i],line))

        #ASSIGMENT
        elif src[i] == '=':
            if i + 1 < len(src) and src[i+1] == src[i]:
                i += 1
                tokens.append(Token('BOOL',src[i],line))
            else:
                tokens.append(Token('ASSIGMENT',src[i],line))
        #BOOLEAN OPs
        elif src[i] in '<>&|!@':
            if i + 1 < len(src) and src[i+1] == '=':
                tokens.append(Token('BOOL',src[i]+'=',line))
                i += 1
            elif i + 1 < len(src) and src[i] == '<' and src[i+1] == '-':
                tokens.append(Token('ARROW','<-',line))
                i += 1
            else:
                tokens.append(Token('BOOL',d[src[i]],line))
        elif src[i] == '`':
            print(f'\n#\tОШИБКА: недействительный символ "`"\n\t{src.split('\n')[line]}')
            return False
        #IDs
        else:
            buffer = '' 
            while i < len(src) and src[i] not in '(){}[],+-*/=@&|!^;:<>"\'`  \t\n?':
                buffer += src[i]
                
                i += 1
            
            if '%' in buffer and (buffer[0] != '%' or buffer.count('%') > 1):
                print(f'\n#\tОШИБКА: для получения адреса переменной используйте символ "%" 1 раз, вплотную перед именем\n\t{src.split('\n')[line]}')
                return False
            
            if buffer in {'mod','div'}:
                tokens.append(Token('MATH',buffer,line))
                continue

            tokens.append(Token('ID',buffer,line))
            i -= 1
        
        i += 1
    if len(tokens) != 0 and tokens[-1].ttype != 'END': tokens.append(Token('END','end of program',line))
    return tokens