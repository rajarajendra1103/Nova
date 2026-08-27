#include "nova_anim.h"
#include <stdio.h>
#include <string.h>

NovaSkeleton novaSkeletonNew(const char* rootName) {
    NovaSkeleton s;
    strncpy(s.rootName, rootName ? rootName : "root", 31);
    s.boneCount = 1;
    return s;
}

NovaAnimClip novaAnimClipNew(const char* name, float duration, bool isLooping) {
    NovaAnimClip c;
    strncpy(c.name, name ? name : "clip", 31);
    c.duration = duration > 0.0f ? duration : 1.0f;
    c.isLooping = isLooping;
    return c;
}

NovaStateMachine novaStateMachineNew(void) {
    NovaStateMachine sm;
    strcpy(sm.currentState, "idle");
    sm.currentTime = 0.0f;
    sm.blendWeight = 1.0f;
    return sm;
}

void novaAnimPlay(NovaStateMachine* sm, const char* stateName) {
    if (sm) {
        strncpy(sm->currentState, stateName ? stateName : "idle", 31);
        sm->currentTime = 0.0f;
        printf("[Nova Animation State] Transitioned to '%s'\n", sm->currentState);
    }
}

void novaAnimUpdate(NovaStateMachine* sm, float dt) {
    if (sm) {
        sm->currentTime += dt;
    }
}

NovaTween novaTweenNew(float duration) {
    NovaTween t;
    t.duration = duration > 0.0f ? duration : 1.0f;
    t.elapsed = 0.0f;
    t.isFinished = false;
    return t;
}
