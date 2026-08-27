#ifndef NOVA_GAME_H
#define NOVA_GAME_H

#include <stdbool.h>

typedef struct {
    char name[64];
    float x, y, z;
} GameEntity;

typedef struct {
    char title[64];
    int width, height, fps;
    bool isRunning;
} GameApp;

GameApp gameNew(const char* title, int width, int height, int fps);
void gameRun(GameApp* app);
GameEntity gameEntity(const char* name, float x, float y, float z);
void gameEntityMove(GameEntity* ent, float dx, float dy, float dz);
float gameDt(void);
int gameFps(void);
float gameTime(void);

#endif // NOVA_GAME_H
