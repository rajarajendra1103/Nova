#include "nova_asset.h"
#include <string.h>

Asset assetLoad(const char* path, const char* type) {
    Asset a;
    strncpy(a.path, path ? path : "", 127);
    strncpy(a.type, type ? type : "generic", 31);
    a.size = 1024 * 512;
    a.isLoaded = true;
    return a;
}

Asset assetLoadModel(const char* path) {
    return assetLoad(path, "model");
}

Asset assetLoadTexture(const char* path) {
    return assetLoad(path, "texture");
}

Asset assetLoadSound(const char* path) {
    return assetLoad(path, "sound");
}

void assetFree(const char* path) {
}

void assetFreeAll(void) {
}

const char* assetUsed(void) {
    return "2.0 MB";
}
