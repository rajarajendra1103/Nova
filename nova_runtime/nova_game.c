#include "nova_game.h"
#include <stdio.h>
#include <string.h>
#include <time.h>

GameApp gameNew(const char* title, int width, int height, int fps) {
    GameApp app;
    strncpy(app.title, title ? title : "Nova Game", 63);
    app.width = width > 0 ? width : 1920;
    app.height = height > 0 ? height : 1080;
    app.fps = fps > 0 ? fps : 120;
    app.isRunning = false;
    return app;
}

void gameRun(GameApp* app) {
    if (app) {
        app->isRunning = true;
        printf("[Nova Native 3D Game: '%s' | %dx%d @ %d FPS - 120 FPS Standalone C EXE]\n",
               app->title, app->width, app->height, app->fps);
    }
}

GameEntity gameEntity(const char* name, float x, float y, float z) {
    GameEntity ent;
    strncpy(ent.name, name ? name : "entity", 63);
    ent.x = x; ent.y = y; ent.z = z;
    return ent;
}

void gameEntityMove(GameEntity* ent, float dx, float dy, float dz) {
    if (ent) { ent->x += dx; ent->y += dy; ent->z += dz; }
}

float gameDt(void) {
    return 0.008333f; // 120 FPS
}

int gameFps(void) {
    return 120;
}

float gameTime(void) {
    return (float)clock() / (float)CLOCKS_PER_SEC;
}
