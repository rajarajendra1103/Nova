#ifndef NOVA_AI_H
#define NOVA_AI_H

#include "nova_np.h"

typedef struct {
    numpyarray weights;
    numpyarray bias;
    char activation[16];
} denselayer;

typedef denselayer DenseLayer;

denselayer aiDense(int inFeatures, int outFeatures, const char* activation);
numpyarray aiForward(denselayer* layer, numpyarray* input);
float aiSigmoid(float x);
float aiRelu(float x);

#endif // NOVA_AI_H
