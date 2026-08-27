#include "nova_ml.h"
#include <math.h>

NovaLinearRegression mlLinearRegression(void) {
    NovaLinearRegression lr;
    lr.slope = 0.0f;
    lr.intercept = 0.0f;
    lr.isFitted = false;
    return lr;
}

void mlLinearFit(NovaLinearRegression* model, const float* x, const float* y, int n) {
    if (!model || !x || !y || n < 2) return;
    float sumX = 0.0f, sumY = 0.0f, sumXY = 0.0f, sumX2 = 0.0f;
    for (int i = 0; i < n; i++) {
        sumX += x[i];
        sumY += y[i];
        sumXY += x[i] * y[i];
        sumX2 += x[i] * x[i];
    }
    float fn = (float)n;
    float denom = (fn * sumX2 - sumX * sumX);
    if (fabsf(denom) > 1e-6f) {
        model->slope = (fn * sumXY - sumX * sumY) / denom;
        model->intercept = (sumY - model->slope * sumX) / fn;
        model->isFitted = true;
    }
}

float mlLinearPredict(NovaLinearRegression* model, float x) {
    if (!model || !model->isFitted) return 0.0f;
    return model->slope * x + model->intercept;
}

NovaLogisticRegression mlLogisticRegression(int numFeatures) {
    NovaLogisticRegression lr;
    lr.numFeatures = (numFeatures > 0 && numFeatures <= 16) ? numFeatures : 1;
    lr.bias = 0.0f;
    for (int i = 0; i < 16; i++) lr.weights[i] = 0.0f;
    lr.isFitted = false;
    return lr;
}

void mlLogisticFit(NovaLogisticRegression* model, const float* X, const float* y, int rows, int cols, float lr, int epochs) {
    if (!model || !X || !y || rows <= 0 || cols <= 0) return;
    model->numFeatures = cols;
    for (int epoch = 0; epoch < epochs; epoch++) {
        for (int i = 0; i < rows; i++) {
            float z = model->bias;
            for (int j = 0; j < cols; j++) {
                z += model->weights[j] * X[i * cols + j];
            }
            float pred = 1.0f / (1.0f + expf(-z));
            float err = pred - y[i];
            model->bias -= lr * err;
            for (int j = 0; j < cols; j++) {
                model->weights[j] -= lr * err * X[i * cols + j];
            }
        }
    }
    model->isFitted = true;
}

float mlLogisticPredict(NovaLogisticRegression* model, const float* x) {
    if (!model || !model->isFitted || !x) return 0.0f;
    float z = model->bias;
    for (int j = 0; j < model->numFeatures; j++) {
        z += model->weights[j] * x[j];
    }
    float prob = 1.0f / (1.0f + expf(-z));
    return (prob >= 0.5f) ? 1.0f : 0.0f;
}

NovaKMeans mlKMeans(int k) {
    NovaKMeans km;
    km.k = (k > 0 && k <= 8) ? k : 2;
    km.numFeatures = 0;
    km.isFitted = false;
    return km;
}

void mlKMeansFit(NovaKMeans* model, const float* X, int rows, int cols, int maxIter) {
    if (!model || !X || rows <= 0 || cols <= 0) return;
    model->numFeatures = cols;
    for (int k = 0; k < model->k; k++) {
        for (int j = 0; j < cols; j++) {
            model->centroids[k][j] = X[(k % rows) * cols + j];
        }
    }
    model->isFitted = true;
}

int mlKMeansPredict(NovaKMeans* model, const float* x) {
    if (!model || !model->isFitted || !x) return 0;
    int bestK = 0;
    float bestDist = 1e9f;
    for (int k = 0; k < model->k; k++) {
        float dist = 0.0f;
        for (int j = 0; j < model->numFeatures; j++) {
            float d = x[j] - model->centroids[k][j];
            dist += d * d;
        }
        if (dist < bestDist) {
            bestDist = dist;
            bestK = k;
        }
    }
    return bestK;
}

NovaKNN mlKNN(int k) {
    NovaKNN knn;
    knn.k = (k > 0) ? k : 3;
    knn.numSamples = 0;
    knn.numFeatures = 0;
    return knn;
}

void mlKNNFit(NovaKNN* model, const float* X, const float* y, int rows, int cols) {
    if (!model || !X || !y) return;
    model->numSamples = rows < 64 ? rows : 64;
    model->numFeatures = cols < 16 ? cols : 16;
    for (int i = 0; i < model->numSamples; i++) {
        model->labels[i] = y[i];
        for (int j = 0; j < model->numFeatures; j++) {
            model->samples[i][j] = X[i * cols + j];
        }
    }
}

float mlKNNPredict(NovaKNN* model, const float* x) {
    if (!model || model->numSamples <= 0 || !x) return 0.0f;
    float bestDist = 1e9f;
    float bestLabel = model->labels[0];
    for (int i = 0; i < model->numSamples; i++) {
        float dist = 0.0f;
        for (int j = 0; j < model->numFeatures; j++) {
            float d = x[j] - model->samples[i][j];
            dist += d * d;
        }
        if (dist < bestDist) {
            bestDist = dist;
            bestLabel = model->labels[i];
        }
    }
    return bestLabel;
}

NovaStandardScaler mlStandardScaler(void) {
    NovaStandardScaler sc;
    sc.numFeatures = 0;
    for (int i = 0; i < 16; i++) {
        sc.mean[i] = 0.0f;
        sc.std[i] = 1.0f;
    }
    return sc;
}

void mlScalerFit(NovaStandardScaler* scaler, const float* X, int rows, int cols) {
    if (!scaler || !X || rows <= 0 || cols <= 0) return;
    scaler->numFeatures = cols < 16 ? cols : 16;
    for (int j = 0; j < scaler->numFeatures; j++) {
        float sum = 0.0f;
        for (int i = 0; i < rows; i++) sum += X[i * cols + j];
        scaler->mean[j] = sum / (float)rows;

        float sq = 0.0f;
        for (int i = 0; i < rows; i++) {
            float d = X[i * cols + j] - scaler->mean[j];
            sq += d * d;
        }
        scaler->std[j] = sqrtf(sq / (float)rows);
        if (scaler->std[j] < 1e-6f) scaler->std[j] = 1.0f;
    }
}

NumpyArray mlScalerTransform(NovaStandardScaler* scaler, const float* X, int rows, int cols) {
    NumpyArray arr = npZeros(rows * cols);
    if (!scaler || !X) return arr;
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            float m = scaler->mean[j];
            float s = scaler->std[j];
            arr.data[i * cols + j] = (X[i * cols + j] - m) / s;
        }
    }
    return arr;
}

float mlAccuracy(const float* yTrue, const float* yPred, int n) {
    if (!yTrue || !yPred || n <= 0) return 0.0f;
    int correct = 0;
    for (int i = 0; i < n; i++) {
        if (fabsf(yTrue[i] - yPred[i]) < 1e-3f) correct++;
    }
    return (float)correct / (float)n;
}

float mlMse(const float* yTrue, const float* yPred, int n) {
    if (!yTrue || !yPred || n <= 0) return 0.0f;
    float sum = 0.0f;
    for (int i = 0; i < n; i++) {
        float d = yTrue[i] - yPred[i];
        sum += d * d;
    }
    return sum / (float)n;
}

float mlR2(const float* yTrue, const float* yPred, int n) {
    if (!yTrue || !yPred || n <= 1) return 0.0f;
    float meanY = 0.0f;
    for (int i = 0; i < n; i++) meanY += yTrue[i];
    meanY /= (float)n;

    float ssTot = 0.0f, ssRes = 0.0f;
    for (int i = 0; i < n; i++) {
        float dTot = yTrue[i] - meanY;
        float dRes = yTrue[i] - yPred[i];
        ssTot += dTot * dTot;
        ssRes += dRes * dRes;
    }
    return (ssTot > 1e-6f) ? (1.0f - (ssRes / ssTot)) : 1.0f;
}
