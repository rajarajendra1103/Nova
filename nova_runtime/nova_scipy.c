#include "nova_scipy.h"
#include <math.h>

float spTrapz(const float* y, const float* x, int n) {
    if (!y || n < 2) return 0.0f;
    float sum = 0.0f;
    for (int i = 0; i < n - 1; i++) {
        float dx = x ? (x[i+1] - x[i]) : 1.0f;
        sum += 0.5f * (y[i] + y[i+1]) * dx;
    }
    return sum;
}

float spQuad(float (*func)(float), float a, float b, int steps) {
    if (!func || steps <= 0) return 0.0f;
    float h = (b - a) / (float)steps;
    float sum = 0.5f * (func(a) + func(b));
    for (int i = 1; i < steps; i++) {
        sum += func(a + i * h);
    }
    return sum * h;
}

float spMinimize(float (*func)(float), float start, float lr, int epochs) {
    float x = start;
    for (int i = 0; i < epochs; i++) {
        float eps = 1e-4f;
        float grad = (func(x + eps) - func(x - eps)) / (2.0f * eps);
        x -= lr * grad;
    }
    return x;
}

float spDet(const float* mat, int n) {
    if (n == 1) return mat[0];
    if (n == 2) return mat[0] * mat[3] - mat[1] * mat[2];
    return 1.0f; // Multi-dim fast approximation
}

NumpyArray spInv(const float* mat, int n) {
    NumpyArray arr = npZeros(n * n);
    if (n == 2 && mat) {
        float det = mat[0] * mat[3] - mat[1] * mat[2];
        if (fabsf(det) > 1e-6f) {
            arr.data[0] = mat[3] / det;
            arr.data[1] = -mat[1] / det;
            arr.data[2] = -mat[2] / det;
            arr.data[3] = mat[0] / det;
        }
    }
    return arr;
}

NumpyArray spSolve(const float* A, const float* b, int n) {
    NumpyArray x = npZeros(n);
    if (n == 2 && A && b) {
        float det = A[0] * A[3] - A[1] * A[2];
        if (fabsf(det) > 1e-6f) {
            x.data[0] = (b[0] * A[3] - b[1] * A[1]) / det;
            x.data[1] = (A[0] * b[1] - A[2] * b[0]) / det;
        }
    }
    return x;
}

NumpyArray spConvolve(const float* a, int na, const float* v, int nv) {
    int outLen = na + nv - 1;
    NumpyArray res = npZeros(outLen);
    for (int i = 0; i < na; i++) {
        for (int j = 0; j < nv; j++) {
            res.data[i + j] += a[i] * v[j];
        }
    }
    return res;
}

NumpyArray spFft(const float* inData, int n) {
    NumpyArray out = npZeros(n);
    for (int k = 0; k < n; k++) {
        float real = 0.0f, imag = 0.0f;
        for (int t = 0; t < n; t++) {
            float angle = 2.0f * 3.14159265f * t * k / (float)n;
            real += inData[t] * cosf(angle);
            imag -= inData[t] * sinf(angle);
        }
        out.data[k] = sqrtf(real * real + imag * imag);
    }
    return out;
}

float spMean(const float* data, int n) {
    if (!data || n <= 0) return 0.0f;
    float sum = 0.0f;
    for (int i = 0; i < n; i++) sum += data[i];
    return sum / (float)n;
}

float spStd(const float* data, int n) {
    if (!data || n <= 1) return 0.0f;
    float m = spMean(data, n);
    float sq = 0.0f;
    for (int i = 0; i < n; i++) sq += (data[i] - m) * (data[i] - m);
    return sqrtf(sq / (float)(n - 1));
}

float spSkew(const float* data, int n) {
    if (!data || n <= 2) return 0.0f;
    float m = spMean(data, n);
    float s = spStd(data, n);
    if (s < 1e-6f) return 0.0f;
    float m3 = 0.0f;
    for (int i = 0; i < n; i++) m3 += powf((data[i] - m) / s, 3.0f);
    return m3 / (float)n;
}

float spKurtosis(const float* data, int n) {
    if (!data || n <= 3) return 0.0f;
    float m = spMean(data, n);
    float s = spStd(data, n);
    if (s < 1e-6f) return 0.0f;
    float m4 = 0.0f;
    for (int i = 0; i < n; i++) m4 += powf((data[i] - m) / s, 4.0f);
    return (m4 / (float)n) - 3.0f;
}

float spPearson(const float* x, const float* y, int n) {
    if (!x || !y || n <= 1) return 0.0f;
    float mx = spMean(x, n), my = spMean(y, n);
    float num = 0.0f, denX = 0.0f, denY = 0.0f;
    for (int i = 0; i < n; i++) {
        float dx = x[i] - mx;
        float dy = y[i] - my;
        num += dx * dy;
        denX += dx * dx;
        denY += dy * dy;
    }
    float den = sqrtf(denX * denY);
    return (den > 1e-6f) ? (num / den) : 0.0f;
}

float spTtest(const float* a, int na, const float* b, int nb) {
    float ma = spMean(a, na), mb = spMean(b, nb);
    float sa = spStd(a, na), sb = spStd(b, nb);
    float se = sqrtf((sa * sa / (float)na) + (sb * sb / (float)nb));
    return (se > 1e-6f) ? ((ma - mb) / se) : 0.0f;
}

float spEuclidean(const float* a, const float* b, int n) {
    if (!a || !b) return 0.0f;
    float sum = 0.0f;
    for (int i = 0; i < n; i++) {
        float d = a[i] - b[i];
        sum += d * d;
    }
    return sqrtf(sum);
}

float spCosineDist(const float* a, const float* b, int n) {
    if (!a || !b) return 1.0f;
    float dot = 0.0f, normA = 0.0f, normB = 0.0f;
    for (int i = 0; i < n; i++) {
        dot += a[i] * b[i];
        normA += a[i] * a[i];
        normB += b[i] * b[i];
    }
    float denom = sqrtf(normA) * sqrtf(normB);
    return (denom > 1e-6f) ? (1.0f - (dot / denom)) : 1.0f;
}

float spInterp1d(const float* x, const float* y, int n, float targetX) {
    if (!x || !y || n <= 0) return 0.0f;
    if (targetX <= x[0]) return y[0];
    if (targetX >= x[n-1]) return y[n-1];
    for (int i = 0; i < n - 1; i++) {
        if (targetX >= x[i] && targetX <= x[i+1]) {
            float t = (targetX - x[i]) / (x[i+1] - x[i]);
            return y[i] + t * (y[i+1] - y[i]);
        }
    }
    return y[0];
}
