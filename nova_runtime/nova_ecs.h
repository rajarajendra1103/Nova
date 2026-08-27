#ifndef NOVA_ECS_H
#define NOVA_ECS_H

#include <stdbool.h>

// ============================================================
// ENTITY COMPONENT SYSTEM (ECS) TYPES
// ============================================================
typedef struct {
    int id;
    bool isAlive;
} NovaEntity;

typedef struct {
    int entityCount;
    int nextId;
} NovaWorld;

typedef struct {
    int count;
    int entityIds[64];
} NovaEntityList;

// ECS API
NovaWorld novaWorldNew(void);
NovaEntity novaWorldCreateEntity(NovaWorld* world);
void novaWorldDestroyEntity(NovaWorld* world, int entityId);
void novaEntityAddComponent(NovaWorld* world, int entityId, const char* compName, const char* compData);
NovaEntityList novaWorldQuery(NovaWorld* world, const char* compName);
void novaWorldTick(NovaWorld* world, float dt);

#endif // NOVA_ECS_H
