#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <locale.h>
#include "skat.h"

char *open();

int main() {
    setlocale(LC_ALL, "ru_RU.UTF-8");
    printf("Начало работы\n");

    char *src = open();

    struct TokenArray *tokens = lexer(src);
    freeTokens(tokens);
    
    //printf("%s\n", src);
    return 0;
}

char *open() {
    char fileName[256];
    char *src = "";
    /*if (!fgets(fileName, sizeof(fileName), stdin)) {
        fprintf(stderr, "Ошибка на этапе получения имени файла\n");
        return NULL;
    }*/
    
    strcpy(fileName, "./code.uivc");
    FILE *file = fopen(fileName, "r");
    fseek(file, 0, SEEK_END);
    size_t size = ftell(file);
    rewind(file);
    if (size == 0) {
        printf("Пустной файл\n");
        fclose(file);
        exit(1);
    }
    src = (char *)malloc(size + 1);
    if (!src) {
        fclose(file);
        printf("Недостаточно памяти для открытия файла\n");
        exit(1);
    }
    size_t bytes_read = fread(src, 1, size, file);
    src[bytes_read] = '\0';
    fclose(file);

    return src;
}