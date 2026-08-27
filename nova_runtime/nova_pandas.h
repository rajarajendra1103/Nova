#ifndef NOVA_PANDAS_H
#define NOVA_PANDAS_H


typedef struct {
    char name[32];
    float* data;
    int size;
} novaseries;

typedef novaseries NovaSeries;

typedef struct {
    char columns[16][32];
    int colCount;
    int rowCount;
} novadataframe;

typedef novadataframe NovaDataFrame;

novadataframe pdDF(void);
novadataframe pdReadCsv(const char* path);
void pdShowDF(const novadataframe* df);
void pdAddCol(novadataframe* df, const char* name, const float* data, int size);
float pdColMean(const novadataframe* df, const char* name);
float pdColSum(const novadataframe* df, const char* name);
const char* pdShape(const novadataframe* df);

#endif // NOVA_PANDAS_H
