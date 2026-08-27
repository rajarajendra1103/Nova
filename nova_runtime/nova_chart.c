#include "nova_chart.h"
#include <stdio.h>
#include <string.h>

ChartFigure chLine(const float* yData, int size) {
    ChartFigure fig;
    strcpy(fig.type, "line");
    strcpy(fig.title, "Line Plot");
    fig.pointCount = size;
    return fig;
}

ChartFigure chBar(const char** labels, const float* values, int size) {
    ChartFigure fig;
    strcpy(fig.type, "bar");
    strcpy(fig.title, "Bar Chart");
    fig.pointCount = size;
    return fig;
}

ChartFigure chScatter(const float* xData, const float* yData, int size) {
    ChartFigure fig;
    strcpy(fig.type, "scatter");
    strcpy(fig.title, "Scatter Plot");
    fig.pointCount = size;
    return fig;
}

ChartFigure vizHeatmap(const float* matrix, int rows, int cols) {
    ChartFigure fig;
    strcpy(fig.type, "heatmap");
    strcpy(fig.title, "Heatmap Matrix");
    fig.pointCount = rows * cols;
    return fig;
}

ChartFigure vizBoxplot(const float* data, int size) {
    ChartFigure fig;
    strcpy(fig.type, "boxplot");
    strcpy(fig.title, "Statistical Boxplot");
    fig.pointCount = size;
    return fig;
}

void chShow(ChartFigure* fig) {
    if (fig) {
        printf("[Chart: %s | Type: %s | %d Points Native Rendered]\n", fig->title, fig->type, fig->pointCount);
    }
}
