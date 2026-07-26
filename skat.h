#ifndef SKAT_H
#define SKAT_H
#include <stddef.h>
#include <string.h>
typedef enum {
    END,
    COLON,
    CALL,
    L_BRACKET,
    R_BRACKET,
    L_CURLY_BRACKET,
    R_CURLY_BRACKET,
    L_SQUARE_BRACKET,
    R_SQUARE_BRACKET,
    COMMA,
    INT,
    DOUBLE,
    PLUS,
    MINUS,
    MULTIPLICATION,
    DIVISION,
    ASSIGNMENT
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

struct Token tokenConstruct(char *str, size_t len, TokenType type, size_t line);

struct TokenArray
{
    struct Token *data;
    size_t size;
    size_t capacity;
};
void freeTokens(struct TokenArray *arr);
struct TokenArray *lexer(char *src);
#endif