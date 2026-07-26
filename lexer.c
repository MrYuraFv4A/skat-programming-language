#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "skat.h"

struct Token tokenConstruct(char *str, size_t len, TokenType type, size_t line) {
    return (struct Token){svConstruct(str, len), type, line};
}


struct StringView svConstruct(char *str, size_t len) {
    return (struct StringView){str, len};
}


void pushToken(struct TokenArray *arr, struct Token el) {
    if (arr->size >= arr->capacity) {
        arr->capacity *= 2;
        arr->data = realloc(arr->data, arr->capacity * sizeof(struct Token));
        if (!arr->data) {
            printf("Ошибка выделения памяти для TokenArray\n");
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
    for (char *ptr = src; *ptr != '\0'; ptr++) {
        //skipping spaces, new lines, semicolons and tabs
        if (strchr(" \t;", *ptr));
        else if(*ptr == '\n') line++;

        //comments
        else if (strncmp(ptr, "//", 2)) while (!strchr("\0\n", *ptr)) ptr++;

        else if (strncmp(ptr, "/*", 2)) {
            while (!strncmp(ptr, "*/", 2)) {
                ptr++;
                if (*ptr == '\0') {
                    printf("Ошибка на этапе лексического анализа: незавершённый многострочный комментарий на строке %i", line);
                    exit(1);
                }
            }
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
            if (*(ptr + 1) == '\0' || !strchr(ops, *(ptr + 1))) {
                TokenType type;
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
                    //else
                    case '!':
                        type = ;
                        break;
                    case '@':
                        type = ;
                        break;
                    case '=':
                        type = ASSIGNMENT;
                        break;
                }
            }
        }

        //numbers
        else if (strchr(digits, *ptr)) {
            for (len = 0; *(ptr + len) != '\0' && (*(ptr + len) == '.' || strchr(digits, *(ptr + len))); len++);
            
            TokenType type = memchr(*ptr, '.', len) ? DOUBLE : INT;
            pushToken(tokens, tokenConstruct(*ptr, len, type, line));
            free(type);
        }

        //strings
        else if (*ptr == '"') {
            for (len = 0; *(ptr + len) != '\0' && *(ptr + len) != '"'; len++);
            if (*ptr == '\0') {
                printf("Ошибка на этапе лексического анализа: незавершённая строковая последовательность на строке %i. Ожидалось '\"'", line);
                exit(1);
            }
            
            TokenType type = memchr(*ptr, '.', len) ? DOUBLE : INT;
            pushToken(tokens, tokenConstruct(*ptr, len, type, line));
            free(type);
        }

        //ids
        else ;
    }

    return tokens;
}

//astrid
//Rocket - One Million