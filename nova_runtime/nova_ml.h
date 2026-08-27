#ifndef NOVA_ML_H
#define NOVA_ML_H

#include <stdbool.h>
#include "nova_np.h"

// ============================================================
// NOVA ML (SCIKIT-LEARN STANDARD) C RUNTIME
// ============================================================

typedef struct {
    float slope;
    float intercept;
    bool isFitted;
} NovaLinearRegression;

typedef struct {
    float weights[16];
    float bias;
    int numFeatures;
    bool isFitted;
} NovaLogisticRegression;

typedef struct {
    int k;
    float centroids[8][16];
    int numFeatures;
    bool isFitted;
} NovaKMeans;

typedef struct {
    int k;
    float samples[64][16];
    float labels[64];
    int numSamples;
    int numFeatures;
} NovaKNN;

typedef struct {
    float mean[16];
    float std[16];
    int numFeatures;
} NovaStandardScaler;

// Models
NovaLinearRegression mlLinearRegression(void);
void mlLinearFit(NovaLinearRegression* model, const float* x, const float* y, int n);
float mlLinearPredict(NovaLinearRegression* model, float x);

NovaLogisticRegression mlLogisticRegression(int numFeatures);
void mlLogisticFit(NovaLogisticRegression* model, const float* X, const float* y, int rows, int cols, float lr, int epochs);
float mlLogisticPredict(NovaLogisticRegression* model, const float* x);

NovaKMeans mlKMeans(int k);
void mlKMeansFit(NovaKMeans* model, const float* X, int rows, int cols, int maxIter);
int mlKMeansPredict(NovaKMeans* model, const float* x);

NovaKNN mlKNN(int k);
void mlKNNFit(NovaKNN* model, const float* X, const float* y, int rows, int cols);
float mlKNNPredict(NovaKNN* model, const float* x);

// Scalers & Preprocessing
NovaStandardScaler mlStandardScaler(void);
void mlScalerFit(NovaStandardScaler* scaler, const float* X, int rows, int cols);
NumpyArray mlScalerTransform(NovaStandardScaler* scaler, const float* X, int rows, int cols);

// Metrics
float mlAccuracy(const float* yTrue, const float* yPred, int n);
float mlMse(const float* yTrue, const float* yPred, int n);
float mlR2(const float* yTrue, const float* yPred, int n);

#endif // NOVA_ML_H
