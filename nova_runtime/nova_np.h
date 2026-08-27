#ifndef NOVA_NP_H
#define NOVA_NP_H


typedef struct {
    float* data;
    int size;
    int shape[4];
    int ndim;
} numpyarray;

typedef numpyarray NumpyArray;

numpyarray npArray(const float* data, int size);
numpyarray npZeros(int size);
numpyarray npOnes(int size);
numpyarray npRand(int size);
float npMean(numpyarray* arr);
float npSum(numpyarray* arr);
float npMax(numpyarray* arr);
float npMin(numpyarray* arr);
float npStd(numpyarray* arr);
numpyarray npAdd(numpyarray* a, numpyarray* b);
numpyarray npMul(numpyarray* a, float scalar);
numpyarray npReshape(numpyarray* a, int rows, int cols);
void npFree(numpyarray* arr);
void npPrint(const numpyarray* arr);
const char* npShapeStr(const numpyarray* arr);

#endif // NOVA_NP_H
