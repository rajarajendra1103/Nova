#ifndef NOVA_MEM_H
#define NOVA_MEM_H

#include <stdbool.h>
#include <stddef.h>

typedef struct MemPoolItem {
    int id;
    char type[32];
    bool active;
    float x, y, z;
    float vx, vy, vz;
} MemPoolItem;

typedef struct {
    char name[32];
    int capacity;
    int activeCount;
    MemPoolItem* items;
} MemPool;

void memNoGC(void);
MemPool* memPool(int capacity, const char* name);
MemPoolItem* memPoolGet(MemPool* pool);
void memPoolFree(MemPool* pool, MemPoolItem* item);
int memPoolCount(MemPool* pool);
int memPoolTotal(MemPool* pool);
void memPoolClear(MemPool* pool);

void* memAlloc(size_t bytes);
void memFree(void* ptr);
void memFreeAll(void);
void* memAllocTemp(size_t bytes);
const char* memUsed(void);
const char* memTotal(void);
int memLeaks(void);

#endif // NOVA_MEM_H
