#include "nova_np.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

NumpyArray npArray(const float* data, int size) {
    NumpyArray arr;
    arr.size = size;
    arr.ndim = 1;
    arr.shape[0] = size;
    arr.data = (float*)malloc(sizeof(float) * size);
    if (data) {
        memcpy(arr.data, data, sizeof(float) * size);
    }
    return arr;
}

NumpyArray npZeros(int size) {
    NumpyArray arr = npArray(NULL, size);
    memset(arr.data, 0, sizeof(float) * size);
    return arr;
}

NumpyArray npOnes(int size) {
    NumpyArray arr = npArray(NULL, size);
    for (int i = 0; i < size; i++) arr.data[i] = 1.0f;
    return arr;
}

NumpyArray npRand(int size) {
    NumpyArray arr = npArray(NULL, size);
    for (int i = 0; i < size; i++) {
        arr.data[i] = (float)rand() / (float)RAND_MAX;
    }
    return arr;
}

float npMean(NumpyArray* arr) {
    if (!arr || arr->size == 0) return 0.0f;
    return npSum(arr) / (float)arr->size;
}

float npSum(NumpyArray* arr) {
    if (!arr || arr->size == 0) return 0.0f;
    float s = 0.0f;
    for (int i = 0; i < arr->size; i++) s += arr->data[i];
    return s;
}

float npMax(NumpyArray* arr) {
    if (!arr || arr->size == 0) return 0.0f;
    float m = arr->data[0];
    for (int i = 1; i < arr->size; i++) if (arr->data[i] > m) m = arr->data[i];
    return m;
}

float npMin(NumpyArray* arr) {
    if (!arr || arr->size == 0) return 0.0f;
    float m = arr->data[0];
    for (int i = 1; i < arr->size; i++) if (arr->data[i] < m) m = arr->data[i];
    return m;
}

float npStd(NumpyArray* arr) {
    if (!arr || arr->size == 0) return 0.0f;
    float mean = npMean(arr);
    float sum_sq = 0.0f;
    for (int i = 0; i < arr->size; i++) {
        float diff = arr->data[i] - mean;
        sum_sq += diff * diff;
    }
    return sqrtf(sum_sq / (float)arr->size);
}

NumpyArray npAdd(NumpyArray* a, NumpyArray* b) {
    int sz = (a && b) ? (a->size < b->size ? a->size : b->size) : 0;
    NumpyArray res = npArray(NULL, sz);
    for (int i = 0; i < sz; i++) res.data[i] = a->data[i] + b->data[i];
    return res;
}

NumpyArray npMul(NumpyArray* a, float scalar) {
    if (!a) return npArray(NULL, 0);
    NumpyArray res = npArray(NULL, a->size);
    for (int i = 0; i < a->size; i++) res.data[i] = a->data[i] * scalar;
    return res;
}

NumpyArray npReshape(NumpyArray* a, int rows, int cols) {
    NumpyArray res = npArray(a->data, a->size);
    res.ndim = 2;
    res.shape[0] = rows;
    res.shape[1] = cols;
    return res;
}

void npFree(NumpyArray* arr) {
    if (arr && arr->data) {
        free(arr->data);
        arr->data = NULL;
        arr->size = 0;
    }
}

void npPrint(const NumpyArray* arr) {
    if (!arr || !arr->data || arr->size == 0) {
        printf("[]\n");
        return;
    }
    printf("[");
    for (int i = 0; i < arr->size; i++) {
        printf("%g%s", arr->data[i], (i + 1 < arr->size) ? ", " : "");
    }
    printf("]\n");
}

const char* npShapeStr(const NumpyArray* arr) {
    static char buf[64];
    if (!arr) return "[0]";
    if (arr->ndim == 2) {
        snprintf(buf, sizeof(buf), "[%d, %d]", arr->shape[0], arr->shape[1]);
    } else {
        snprintf(buf, sizeof(buf), "[%d]", arr->size);
    }
    return buf;
}

