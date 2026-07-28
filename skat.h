#ifndef SKAT_H
#define SKAT_H
#include <stddef.h>
#include <string.h>
typedef enum {
    //eoc
    END,
    //type assignment
    COLON,
    //function
    CALL,
    //brackets
    L_BRACKET,
    R_BRACKET,
    L_CURLY_BRACKET,
    R_CURLY_BRACKET,
    L_SQUARE_BRACKET,
    R_SQUARE_BRACKET,
    //enumexpr
    COMMA,
    //type
    INT,
    DOUBLE,
    STRING,
    ID,
    //op    math
    PLUS,
    MINUS,
    MULTIPLICATION,
    DIVISION,
    DIV, //int div
    MOD,
    EXPONENTIATION,
    ROOTEXTRACTION,
    INCREMENT,
    DECREMENT,
    //      var
    ASSIGNMENT,
    //      logical
    NOT,
    OTHER,
    AND,
    OR,
    XOR,
    //      comparison
    EQUALITY,
    BIGGER,
    LESS,
    BIGGER_OR_EQUAL,
    LESS_OR_EQUAL,
    //      functional
    ARROW,
} TokenType;

struct StringView {
    const char *start;
    size_t len;
};

struct StringView svConstruct(char *str, size_t len);

struct Token
{
    struct StringView value;
    TokenType type;
    size_t line;
};

struct Token tokenConstruct(char *ptr, size_t len, TokenType type, size_t line);

struct TokenArray
{
    struct Token *data;
    size_t size;
    size_t capacity;
};

void showTokens(struct TokenArray *arr);

void freeTokens(struct TokenArray *arr);

struct TokenArray *lexer(char *src);

#endif