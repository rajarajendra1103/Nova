#ifndef NOVA_APP_H
#define NOVA_APP_H

#include <stdbool.h>

typedef struct {
    char title[64];
    int width;
    int height;
    int fps;
    bool isRunning;
} App;

void appNew(App* app, const char* title, int width, int height, int fps);
void appRun(App* app);
void appScale(float factor);
bool appIsMobile(void);
bool appIsIOS(void);
bool appIsAndroid(void);
void appSetOrientation(const char* orientation);
void appHaptics(const char* type);
void appVibrate(int ms);
void appStatusBar(const char* style, const char* bg);

#endif // NOVA_APP_H
