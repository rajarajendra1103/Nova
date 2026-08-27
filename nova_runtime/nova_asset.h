#ifndef NOVA_ASSET_H
#define NOVA_ASSET_H

#include <stdbool.h>
#include <stddef.h>

typedef struct {
    char path[128];
    char type[32];
    size_t size;
    bool isLoaded;
} Asset;

Asset assetLoad(const char* path, const char* type);
Asset assetLoadModel(const char* path);
Asset assetLoadTexture(const char* path);
Asset assetLoadSound(const char* path);
void assetFree(const char* path);
void assetFreeAll(void);
const char* assetUsed(void);

#endif // NOVA_ASSET_H
