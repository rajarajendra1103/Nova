#ifndef NOVA_ANIM_H
#define NOVA_ANIM_H

#include <stdbool.h>

// ============================================================
// SKELETAL & 2D/3D ANIMATION TYPES
// ============================================================
typedef struct {
    char name[32];
    float posX, posY, posZ;
    float rotX, rotY, rotZ;
    float scaleX, scaleY, scaleZ;
} NovaBone;

typedef struct {
    char rootName[32];
    int boneCount;
} NovaSkeleton;

typedef struct {
    char name[32];
    float duration;
    bool isLooping;
} NovaAnimClip;

typedef struct {
    char currentState[32];
    float currentTime;
    float blendWeight;
} NovaStateMachine;

typedef struct {
    float duration;
    float elapsed;
    bool isFinished;
} NovaTween;

// Animation API
NovaSkeleton novaSkeletonNew(const char* rootName);
NovaAnimClip novaAnimClipNew(const char* name, float duration, bool isLooping);
NovaStateMachine novaStateMachineNew(void);
void novaAnimPlay(NovaStateMachine* sm, const char* stateName);
void novaAnimUpdate(NovaStateMachine* sm, float dt);
NovaTween novaTweenNew(float duration);

#endif // NOVA_ANIM_H
