#ifndef NOVA_SCIPY_H
#define NOVA_SCIPY_H

#include "nova_np.h"

// ============================================================
// NOVA SCIPY C RUNTIME (Optimization, Stats, Signal, Linear Algebra)
// ============================================================

// Integration & Optimization
float spTrapz(const float* y, const float* x, int n);
float spQuad(float (*func)(float), float a, float b, int steps);
float spMinimize(float (*func)(float), float start, float lr, int epochs);

// Linear Algebra
float spDet(const float* mat, int n);
NumpyArray spInv(const float* mat, int n);
NumpyArray spSolve(const float* A, const float* b, int n);

// Signal & FFT
NumpyArray spConvolve(const float* a, int na, const float* v, int nv);
NumpyArray spFft(const float* inData, int n);

// Statistics
float spMean(const float* data, int n);
float spStd(const float* data, int n);
float spSkew(const float* data, int n);
float spKurtosis(const float* data, int n);
float spPearson(const float* x, const float* y, int n);
float spTtest(const float* a, int na, const float* b, int nb);

// Spatial & Distance
float spEuclidean(const float* a, const float* b, int n);
float spCosineDist(const float* a, const float* b, int n);

// Interpolation
float spInterp1d(const float* x, const float* y, int n, float targetX);

#endif // NOVA_SCIPY_H
