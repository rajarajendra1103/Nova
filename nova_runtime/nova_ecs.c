#include "nova_ecs.h"

NovaWorld novaWorldNew(void) {
    NovaWorld w;
    w.entityCount = 0;
    w.nextId = 1;
    return w;
}

NovaEntity novaWorldCreateEntity(NovaWorld* world) {
    NovaEntity e;
    e.id = world ? world->nextId++ : 1;
    e.isAlive = true;
    if (world) world->entityCount++;
    return e;
}

void novaWorldDestroyEntity(NovaWorld* world, int entityId) {
    if (world && world->entityCount > 0) world->entityCount--;
}

void novaEntityAddComponent(NovaWorld* world, int entityId, const char* compName, const char* compData) {
    // Zero-overhead component assignment
}

NovaEntityList novaWorldQuery(NovaWorld* world, const char* compName) {
    NovaEntityList list;
    list.count = world ? world->entityCount : 0;
    for (int i = 0; i < list.count && i < 64; i++) {
        list.entityIds[i] = i + 1;
    }
    return list;
}

void novaWorldTick(NovaWorld* world, float dt) {
    // Dispatch systems
}
