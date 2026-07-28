#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "skat.h"

struct Token tokenConstruct(char *ptr, size_t len, TokenType type, size_t line) {
    return (struct Token){svConstruct(ptr, len), type, line};
}


struct StringView svConstruct(char *str, size_t len) {
    return (struct StringView){str, len};
}


void pushToken(struct TokenArray *arr, struct Token el) {
    if (arr->size >= arr->capacity) {
        arr->capacity = arr->capacity ? arr->capacity * 2 : 4;
        arr->data = realloc(arr->data, arr->capacity * sizeof(struct Token));
        if (!arr->data) {
            printf("Ошибка выделения памяти для TokenArray\n");
            printf("%llu\n", arr->capacity);
            exit(1);
        }
    }
    arr->data[arr->size++] = el;
}

void freeTokens(struct TokenArray *arr) {
    free(arr->data);
    arr->data = NULL;
    arr->size = arr->capacity = 0;
}

void showTokens(struct TokenArray *arr) {
    for (size_t i = 0; i < arr->size; i++) {
        struct Token *token = &arr->data[i];
        char value[token->value.len + 1];
        strncpy(value, token->value.start, token->value.len);
        value[token->value.len] = '\0';
        
        printf("%-16u : %16s (%llu)\n", token->type, value, token->value.len);
    }
}

struct TokenArray *lexer(char *src) {
    struct TokenArray *tokens = malloc(sizeof(struct TokenArray));
    if (!tokens) {
        printf("Ошибка выделения памяти для tokenArray\n");
        exit(1);
    } 
    *tokens = (struct TokenArray){0};

    char *digits = "0123456789";
    char *ops = "+-*/=!@&|<>";

    size_t len; //buf это срез src длинной len начиная с ptr
    size_t line = 1;
    TokenType type;
    char op[4];
    for (char *ptr = src; *ptr != '\0'; ptr++) {
        //skipping spaces, new lines, semicolons and tabs
        if (strchr(" \t;", *ptr));
        else if(*ptr == '\n') line++;

        //comments "\\"
        else if (0 == strncmp(ptr, "\\\\", 2)) while (!strchr("\0\n", *ptr)) ptr++;

        else if (0 == strncmp(ptr, "\\*", 2)) {
            while (strncmp(ptr, "*\\", 2)) {
                ptr++;
                if (*ptr == '\0') {
                    printf("Ошибка на этапе лексического анализа: незавершённый многострочный комментарий на линии %llu", line);
                    exit(1);
                }
            }
            ptr++;
        }

        //colon
        else if (*ptr == ':') pushToken(tokens, tokenConstruct(NULL, 0, COLON, line));

        //call
        else if (*ptr == '$') pushToken(tokens, tokenConstruct(NULL, 0, CALL, line));

        //brackets
        else if (*ptr == '(') pushToken(tokens, tokenConstruct(NULL, 0, L_BRACKET, line));
        else if (*ptr == ')') pushToken(tokens, tokenConstruct(NULL, 0, R_BRACKET, line));
        else if (*ptr == '{') pushToken(tokens, tokenConstruct(NULL, 0, L_CURLY_BRACKET, line));
        else if (*ptr == '}') pushToken(tokens, tokenConstruct(NULL, 0, R_CURLY_BRACKET, line));
        else if (*ptr == '[') pushToken(tokens, tokenConstruct(NULL, 0, L_SQUARE_BRACKET, line));
        else if (*ptr == ']') pushToken(tokens, tokenConstruct(NULL, 0, R_SQUARE_BRACKET, line));

        //commas
        else if (*ptr == '.') pushToken(tokens, tokenConstruct(NULL, 0, COMMA, line));

        //ops
        else if (strchr(ops, *ptr)) {
            //single-char ops
            if (*(ptr + 1) == '\0' || !strchr(ops, *(ptr + 1))) {
                singleCharOperatorHandle:
                    switch (*ptr) {
                        //math
                        case '+':
                            type = PLUS;
                            break;
                        case '-':
                            type = MINUS;
                            break;
                        case '*':
                            type = MULTIPLICATION;
                            break;
                        case '/':
                            type = DIVISION;
                            break;
                        //logical
                        case '!':
                            type = NOT;
                            break;
                        case '@':
                            type = OTHER;
                            break;
                        case '&':
                            type = AND;
                            break;
                        case '|':
                            type = OR;
                            break;
                        case '^':
                            type = XOR;
                            break;
                        //comparison
                        case '>':
                            type = BIGGER;
                            break;
                        case '<':
                            type = LESS;
                            break;
                        //assignment
                        case '=':
                            type = ASSIGNMENT;
                            break;
                    }
                pushToken(tokens, tokenConstruct(NULL, 0, type, line));
                continue;
            } else if ((*(ptr + 2) == '\0' || !strchr(ops, *(ptr + 2)))) {
                //two-char ops
                twoCharOperatorHandle:
                    strncpy(op, ptr, 2);
                    op[2] = '\0';
                    if (0 == strcmp("**", op)) type = EXPONENTIATION;
                    else if (0 == strcmp("//", op)) type = ROOTEXTRACTION;
                    else if (0 == strcmp("++", op)) type = INCREMENT;
                    else if (0 == strcmp("--", op)) type = DECREMENT;
                    else if (0 == strcmp("+=", op) || 0 == strcmp("-=", op) || 0 == strcmp("*=", op) || 0 == strcmp("/=", op)) {
                        type = ASSIGNMENT;
                        pushToken(tokens, tokenConstruct(ptr, 2, type, line));
                        ptr++;
                        continue;
                    } else if (0 == strcmp("->", op) || 0 == strcmp("<-", op)) {
                        type = ARROW;
                        pushToken(tokens, tokenConstruct(ptr, 2, type, line));
                        ptr++;
                        continue;
                    } else if (0 == strcmp(">=", op)) {
                        type = BIGGER_OR_EQUAL;
                        pushToken(tokens, tokenConstruct(NULL, 0, type, line));
                        ptr++;
                        continue;
                    } else if (0 == strcmp("<=", op)) {
                        type = LESS_OR_EQUAL;
                        pushToken(tokens, tokenConstruct(NULL, 0, type, line));
                        ptr++;
                        continue;
                    } else goto singleCharOperatorHandle; //два разных оператора

                pushToken(tokens, tokenConstruct(NULL, 0, type, line));
                ptr++;
            } else {
                //three-character ops
                strncpy(op, ptr, 3);
                op[3] = '\0';
                if (0 == strcmp("**=", op) || 0 == strcmp("//=", op)) {
                    type = ASSIGNMENT;
                    pushToken(tokens, tokenConstruct(ptr, 3, type, line));
                    ptr += 2;
                    continue;
                } else goto twoCharOperatorHandle;

                ptr += 2;
            }
        }

        //numbers
        else if (strchr(digits, *ptr)) {
            for (len = 0; *(ptr + len) != '\0' && (*(ptr + len) == '.' || strchr(digits, *(ptr + len))); len++);
            
            type = INT;
            for (size_t i, count = 0; i < len; i++) if (*(ptr + i) == '.') {
                count++;
                if (count) type = DOUBLE;
                if (count > 1) {
                    char num[len + 1];
                    strncpy(num, ptr, len);
                    num[len] = '\0';

                    printf("Ошибка на этапе лексического анализа: недействительное число %s на линии %llu. Слишком много точек", num, line);
                    exit(1);
                }
            }

            
            pushToken(tokens, tokenConstruct(ptr, len, type, line));
            ptr += len;
        }

        //strings
        else if (*ptr == '"') {
            for (len = 1; *(ptr + len) != '\0' &&*(ptr + len) != '"'; len ++);
            if (*ptr == '\0') {
                printf("Ошибка на этапе лексического анализа: незавершённая строковая последовательность на линии %llu. Ожидалась \"", line);
                exit(1);
            }
            
            type = STRING;
            pushToken(tokens, tokenConstruct(ptr + 1, len - 1, type, line));
            ptr += len;
        }

        //ids
        else {
            for (len = 0; *(ptr + len) != '\0' && !(strchr(digits, *(ptr + len)) || strchr(ops, *(ptr + len)) || strchr(" \t\n.,()[]{};:\"\'", *(ptr + len))); len++);

            char buf[len + 1];
            strncpy(buf, ptr, len);
            buf[len] = '\0';
            if (strncmp("mod", ptr, 3))
            
            type = ID;
            pushToken(tokens, tokenConstruct(ptr, len, type, line));
            ptr += len;
        };
    }

    return tokens;
}

//astrid
//Rocket - One Million