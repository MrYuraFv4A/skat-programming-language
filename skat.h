#ifndef SKAT_H
#define SKAT_H
#include <stddef.h>
#include <string.h>

/*
        lexer
*/

// TokenType

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

// StringView

typedef struct StringView StringView;

struct StringView {
    const char *start;
    size_t len;
};

struct StringView svConstruct(char *str, size_t len);

// Token

typedef struct Token Token;

struct Token {
    StringView value;
    TokenType type;
    size_t line;
};

struct Token tokenConstruct(char *ptr, size_t len, TokenType type, size_t line);

// TokenArray

typedef struct TokenArray TokenArray;

struct TokenArray
{
    struct Token *data;
    size_t size;
    size_t capacity;
};

void showTokens(struct TokenArray *arr);

void freeTokens(struct TokenArray *arr);

// lexer function

struct TokenArray *lexer(char *src);

/*
        parser
*/

// Node

typedef struct Node Node;

struct Node {
    size_t line;
    enum NodeType {
        NODE_PROGRAM,
        NODE_END,
        NODE_BYTE,
        NODE_SHORT,
        NODE_INT,
        NODE_LONG,
        NODE_DOUBLE,
        NODE_UBYTE,
        NODE_USHORT,
        NODE_UINT,
        NODE_LONGDOUBLE,
        NODE_ULONG,
        NODE_CHAR,
        NODE_BINARY_OP,
        NODE_UNAR_OP,
    } type;
    union {
        //type
        struct { signed char        value; } LiteralByte;
        struct { short              value; } LiteralShort;
        struct { int                value; } LiteralInt;
        struct { long long          value; } LiteralLong;
        struct { double             value; } LiteralDouble;
        struct { unsigned char      value; } LiteralChickenburger;  //LiteralUByte;
        struct { unsigned short     value; } LiteralBigspecial;     //LiteralUShort;
        struct { unsigned int       value; } LiteralGrand;          //LiteralUInt;
        struct { long double        value; } LiteralChickencurry;   //LiteralLongDouble;
        struct { unsigned long long value; } LiteralBighit;         //LiteralULong;
        struct { char               value; } LiteralChar;
        //expr
        struct {
            TokenType op;
            Node *left;
            Node *right;
        } BinaryOp;
        struct {
            TokenType op;
            Node *operand;
        } UnarOp;
        struct {
            StringView name;
            Node *args; //values
        } Call;
        //statement
        struct {
            StringView name;
            StringView type;
        } VariableDeclaration;
        struct { //new name (args) -> type {body}
            StringView name;
            StringView type;
            Node *params; //var declarations
            Node *body;
        } FunctionDeclaration;
        struct {
            StringView name;
            StringView super; //if the method not in the name the vm will search for it in a super
        } ClassDeclaration;
        struct { Node *expr; } Return;
        struct { StringView name; } Delete;
        struct { ; } Continue;
        struct { ; } Break;
        struct { StringView module; } Connect;
        struct {
            Node *condition;
            Node *thenBranch;
            Node *elseBranch;
        } IfStatement;
        struct {
            Node *condition;
            Node *body;
        } WhileStatement;
        struct {
            StringView dest;
            Node *expr;
        } Assignment;
    } data;

    Node *next;
};

Node *nodeConstruct();

// parser

Node *parser(TokenArray *arr);
Node *handle(TokenArray *tokens, size_t index);

#endif