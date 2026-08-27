#include "nova_mem.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static size_t g_allocated_bytes = 0;
static int g_alloc_count = 0;

void memNoGC(void) {
    // Zero GC mode enabled
}

MemPool* memPool(int capacity, const char* name) {
    MemPool* p = (MemPool*)malloc(sizeof(MemPool));
    strncpy(p->name, name ? name : "default", 31);
    p->capacity = capacity > 0 ? capacity : 100;
    p->activeCount = 0;
    p->items = (MemPoolItem*)calloc(p->capacity, sizeof(MemPoolItem));
    for (int i = 0; i < p->capacity; i++) {
        p->items[i].id = i + 1;
        strncpy(p->items[i].type, p->name, 31);
        p->items[i].active = false;
    }
    return p;
}

MemPoolItem* memPoolGet(MemPool* pool) {
    if (!pool) return NULL;
    for (int i = 0; i < pool->capacity; i++) {
        if (!pool->items[i].active) {
            pool->items[i].active = true;
            pool->activeCount++;
            return &pool->items[i];
        }
    }
    return NULL;
}

void memPoolFree(MemPool* pool, MemPoolItem* item) {
    if (pool && item && item->active) {
        item->active = false;
        if (pool->activeCount > 0) pool->activeCount--;
    }
}

int memPoolCount(MemPool* pool) {
    return pool ? pool->activeCount : 0;
}

int memPoolTotal(MemPool* pool) {
    return pool ? pool->capacity : 0;
}

void memPoolClear(MemPool* pool) {
    if (pool && pool->items) {
        for (int i = 0; i < pool->capacity; i++) {
            pool->items[i].active = false;
        }
        pool->activeCount = 0;
    }
}

void* memAlloc(size_t bytes) {
    g_allocated_bytes += bytes;
    g_alloc_count++;
    return malloc(bytes);
}

void memFree(void* ptr) {
    if (ptr) {
        free(ptr);
        if (g_alloc_count > 0) g_alloc_count--;
    }
}

void memFreeAll(void) {
    g_allocated_bytes = 0;
    g_alloc_count = 0;
}

void* memAllocTemp(size_t bytes) {
    return malloc(bytes);
}

const char* memUsed(void) {
    static char buf[64];
    snprintf(buf, sizeof(buf), "%zu KB", g_allocated_bytes / 1024);
    return buf;
}

const char* memTotal(void) {
    return "64.0 MB";
}

int memLeaks(void) {
    return g_alloc_count;
}
