#ifndef NOVA_CHART_H
#define NOVA_CHART_H


typedef struct {
    char type[32];
    char title[64];
    int pointCount;
} ChartFigure;

ChartFigure chLine(const float* yData, int size);
ChartFigure chBar(const char** labels, const float* values, int size);
ChartFigure chScatter(const float* xData, const float* yData, int size);
ChartFigure vizHeatmap(const float* matrix, int rows, int cols);
ChartFigure vizBoxplot(const float* data, int size);
void chShow(ChartFigure* fig);

#endif // NOVA_CHART_H
