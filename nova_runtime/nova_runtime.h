#ifndef NOVA_RUNTIME_H
#define NOVA_RUNTIME_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <time.h>

#ifdef _WIN32
#include <windows.h>
#endif

// ============================================================
// CORE TYPES & STRINGS
// ============================================================
typedef struct {
    char* data;
    size_t len;
} novastring;

typedef novastring NovaString;

static inline NovaString novaStr(const char* s) {
    NovaString ns;
    ns.data = strdup(s ? s : "");
    ns.len = strlen(ns.data);
    return ns;
}

static inline void novaShowStr(const char* s) {
    printf("%s\n", s);
}

static inline void novaShowInt(long long n) {
    printf("%lld\n", n);
}

static inline void novaShowFloat(double f) {
    printf("%g\n", f);
}

static inline void novaShowBool(bool b) {
    printf("%s\n", b ? "true" : "false");
}

#endif // NOVA_RUNTIME_H
