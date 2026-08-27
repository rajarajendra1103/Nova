#ifndef NOVA_PHYSICS_H
#define NOVA_PHYSICS_H


typedef struct {
    float mass;
    char shape[32];
    float x, y, z;
    float vx, vy, vz;
    float fx, fy, fz;
} PhysicsBody;

PhysicsBody physicsBody(float mass, const char* shape, float x, float y, float z);
void physicsApplyForce(PhysicsBody* body, float fx, float fy, float fz);
void physicsApplyImpulse(PhysicsBody* body, float ix, float iy, float iz);
void physicsUpdate(float dt);

#endif // NOVA_PHYSICS_H
