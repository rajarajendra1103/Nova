#include "nova_app.h"
#include <stdio.h>
#include <string.h>

void appNew(App* app, const char* title, int width, int height, int fps) {
    if (app) {
        strncpy(app->title, title ? title : "Nova App", 63);
        app->width = width > 0 ? width : 800;
        app->height = height > 0 ? height : 600;
        app->fps = fps > 0 ? fps : 120;
        app->isRunning = false;
    }
}

void appRun(App* app) {
    if (app) {
        app->isRunning = true;
        printf("[Nova Native App: '%s' | %dx%d @ %d FPS - 0ms GC Direct Native]\n",
               app->title, app->width, app->height, app->fps);
    }
}

void appScale(float factor) {
    // Dynamic responsive scale factor
}

bool appIsMobile(void) {
    return true;
}

bool appIsIOS(void) {
    #if defined(__APPLE__)
    return true;
    #else
    return false;
    #endif
}

bool appIsAndroid(void) {
    #if defined(__ANDROID__)
    return true;
    #else
    return false;
    #endif
}

void appSetOrientation(const char* orientation) {
    printf("[Nova Mobile Orientation: %s]\n", orientation ? orientation : "portrait");
}

void appHaptics(const char* type) {
    printf("[Nova Mobile Haptics: %s]\n", type ? type : "light");
}

void appVibrate(int ms) {
    printf("[Nova Mobile Vibrate: %dms]\n", ms);
}

void appStatusBar(const char* style, const char* bg) {
    printf("[Nova Mobile Status Bar: Style=%s, Bg=%s]\n", style ? style : "light-content", bg ? bg : "#000000");
}
