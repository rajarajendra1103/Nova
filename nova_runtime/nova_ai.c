#include "nova_ai.h"
#include <string.h>
#include <math.h>
#include <stddef.h>

DenseLayer aiDense(int inFeatures, int outFeatures, const char* activation) {
    DenseLayer l;
    l.weights = npRand(inFeatures * outFeatures);
    l.bias = npZeros(outFeatures);
    strncpy(l.activation, activation ? activation : "relu", 15);
    return l;
}

float aiSigmoid(float x) {
    return 1.0f / (1.0f + expf(-x));
}

float aiRelu(float x) {
    return x > 0.0f ? x : 0.0f;
}

NumpyArray aiForward(DenseLayer* layer, NumpyArray* input) {
    if (!layer || !input) return npArray(NULL, 0);
    int out_sz = layer->bias.size;
    NumpyArray output = npZeros(out_sz);
    int in_sz = input->size;

    for (int j = 0; j < out_sz; j++) {
        float sum = layer->bias.data[j];
        for (int i = 0; i < in_sz; i++) {
            sum += input->data[i] * layer->weights.data[j * in_sz + i];
        }
        if (strcmp(layer->activation, "sigmoid") == 0) {
            output.data[j] = aiSigmoid(sum);
        } else {
            output.data[j] = aiRelu(sum);
        }
    }
    return output;
}
