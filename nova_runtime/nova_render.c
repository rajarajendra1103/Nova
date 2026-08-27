#include "nova_render.h"
#include <string.h>

static int g_draw_calls = 0;
static int g_triangles = 0;

RenderWindow renderWindow(int w, int h, const char* title) {
    RenderWindow win;
    win.width = w; win.height = h;
    strncpy(win.title, title ? title : "Nova Window", 127);
    return win;
}

Mesh renderMesh(const char* path) {
    Mesh m;
    strncpy(m.path, path ? path : "cube", 127);
    m.vertexCount = 1024;
    m.triangleCount = 512;
    return m;
}

Texture renderTexture(const char* path) {
    Texture t;
    strncpy(t.path, path ? path : "default.png", 127);
    t.id = 1;
    return t;
}

Material renderMaterial(const char* color, const char* shader, float metallic, float roughness) {
    Material mat;
    strncpy(mat.color, color ? color : "white", 31);
    strncpy(mat.shader, shader ? shader : "pbr", 31);
    mat.metallic = metallic;
    mat.roughness = roughness;
    return mat;
}

RenderEntity renderEntity(Mesh mesh, Material mat) {
    RenderEntity ent;
    ent.mesh = mesh;
    ent.material = mat;
    ent.x = 0; ent.y = 0; ent.z = 0;
    ent.rx = 0; ent.ry = 0; ent.rz = 0;
    ent.sx = 1; ent.sy = 1; ent.sz = 1;
    return ent;
}

void renderEntityPos(RenderEntity* ent, float x, float y, float z) {
    if (ent) { ent->x = x; ent->y = y; ent->z = z; }
}

void renderEntityMove(RenderEntity* ent, float dx, float dy, float dz) {
    if (ent) { ent->x += dx; ent->y += dy; ent->z += dz; }
}

Sprite renderSprite(const char* path) {
    Sprite sp;
    strncpy(sp.path, path ? path : "sprite.png", 127);
    sp.x = 0; sp.y = 0;
    sp.w = 64; sp.h = 64;
    return sp;
}

void renderSpritePos(Sprite* sp, float x, float y) {
    if (sp) { sp->x = x; sp->y = y; }
}

void renderSpriteSize(Sprite* sp, float w, float h) {
    if (sp) { sp->w = w; sp->h = h; }
}

Camera renderCamera(float fov, float x, float y, float z) {
    Camera cam;
    cam.fov = fov;
    cam.x = x; cam.y = y; cam.z = z;
    cam.targetX = 0; cam.targetY = 0; cam.targetZ = 0;
    return cam;
}

void renderClear(const char* color) {
    g_draw_calls = 0;
    g_triangles = 0;
}

void renderDraw(RenderEntity* ent, Camera* cam) {
    g_draw_calls++;
    if (ent) g_triangles += ent->mesh.triangleCount;
}

void renderDraw2D(Sprite* sp) {
    g_draw_calls++;
    g_triangles += 2;
}

void renderPresent(void) {
    // Direct Vulkan / GPU Swapchain Present
}
