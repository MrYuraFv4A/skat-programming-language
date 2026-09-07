#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "skat.h"

Node *nodeConstruct() {
    Node *node = malloc(sizeof(Node));
    return node;
}

#define currentToken tokens->data[index]

/*
char *strdup(const char *ptr, size_t len) {
    char *str = malloc(sizeof(char) * (len + 1));
    if (!str) return NULL;
    memcpy(str, ptr, len);
    str[len] = '\0';
    return str;
}
*/

void *svTransformInt(const char *ptr, size_t len) {
    unsigned char size = 10;
    char buffer[size + 1];
    if (len > size) {
        printf("Ошибка: братик, твоё число %.*s слишком большое для типа %s, оно не поместится, мгнх~ >~< !\n", (int)len, ptr, "int");
        exit(1);
    }
    memcpy(buffer, ptr, len);
    buffer[len] = '\0';

    char *endptr;

    long *l = malloc(sizeof(long));
    *l = strtol(buffer, &endptr, 10);

    return (int *)l;
}

void *svTransformLong(const char *ptr, size_t len) {
    unsigned char size = 20;
    char buffer[size + 1];
    if (len > size) {
        printf("Ошибка: братик, твоё число %.*s слишком большое для типа %s, оно не поместится, мгнх~ >~< !\n", (int)len, ptr, "long");
        exit(1);
    }
    memcpy(buffer, ptr, len);
    buffer[len] = '\0';

    char *endptr;

    long long *l = malloc(sizeof(long long));
    *l = strtol(buffer, &endptr, 10);

    return (long long *)l;
}

Node *parser(TokenArray *tokens) {
    Node *currentNode = nodeConstruct();
    currentNode->type = NODE_PROGRAM;
    for (size_t index = 0; index < tokens->size; index++) {
        currentNode->next = handle(tokens, index);
        currentNode = currentNode->next;
    }

    return currentNode;
}

Node *handle(TokenArray *tokens, size_t index) {
    Node *node = nodeConstruct();
    switch (currentToken.type) {
        case (INT):
            printf("INT\n");
            node->type = NODE_INT;
            node->line = currentToken.line;
            
            node->data.LiteralInt.value = *(int *)svTransformInt(currentToken.value.start, currentToken.value.len);
            //printf("there: %d\n", node->data.LiteralInt.value); /*мб до vm хранить unsigned + unarOp*/
            break;
        case (LONG):
            printf("LONG\n");
            node->type = NODE_LONG;
            node->line = currentToken.line;
            
            node->data.LiteralLong.value = *(long long *)svTransformLong(currentToken.value.start, currentToken.value.len);
            break;
        case (GMP):
            /*
            printf("GMP\n");
            node->type = NODE_GMP;
            node->line = currentToken.line;
            
            node->data.LiteralGMP.value = *(int *)svTransformInt(currentToken.value.start, currentToken.value.len);
            //printf("there: %d\n", node->data.LiteralInt.value);
            */
            break;
        default:
            printf("Неожиданный тип: %i\n", tokens->data[index].type);
            break;
    }
    return node;
}

