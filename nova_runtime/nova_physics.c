#include "nova_physics.h"
#include <string.h>

PhysicsBody physicsBody(float mass, const char* shape, float x, float y, float z) {
    PhysicsBody b;
    b.mass = mass;
    strncpy(b.shape, shape ? shape : "box", 31);
    b.x = x; b.y = y; b.z = z;
    b.vx = 0; b.vy = 0; b.vz = 0;
    b.fx = 0; b.fy = 0; b.fz = 0;
    return b;
}

void physicsApplyForce(PhysicsBody* body, float fx, float fy, float fz) {
    if (body) {
        body->fx += fx; body->fy += fy; body->fz += fz;
    }
}

void physicsApplyImpulse(PhysicsBody* body, float ix, float iy, float iz) {
    if (body && body->mass > 0.0f) {
        body->vx += ix / body->mass;
        body->vy += iy / body->mass;
        body->vz += iz / body->mass;
    }
}

void physicsUpdate(float dt) {
    // Rigid body dynamics step
}
