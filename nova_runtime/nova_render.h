#ifndef NOVA_RENDER_H
#define NOVA_RENDER_H


typedef struct {
    char path[128];
    int vertexCount;
    int triangleCount;
} Mesh;

typedef struct {
    char path[128];
    int id;
} Texture;

typedef struct {
    char shader[32];
    char color[32];
    float metallic;
    float roughness;
} Material;

typedef struct {
    Mesh mesh;
    Material material;
    float x, y, z;
    float rx, ry, rz;
    float sx, sy, sz;
} RenderEntity;

typedef struct {
    char path[128];
    float x, y;
    float w, h;
} Sprite;

typedef struct {
    float fov;
    float x, y, z;
    float targetX, targetY, targetZ;
} Camera;

typedef struct {
    int width;
    int height;
    char title[128];
} RenderWindow;

RenderWindow renderWindow(int w, int h, const char* title);
Mesh renderMesh(const char* path);
Texture renderTexture(const char* path);
Material renderMaterial(const char* color, const char* shader, float metallic, float roughness);
RenderEntity renderEntity(Mesh mesh, Material mat);
void renderEntityPos(RenderEntity* ent, float x, float y, float z);
void renderEntityMove(RenderEntity* ent, float dx, float dy, float dz);

Sprite renderSprite(const char* path);
void renderSpritePos(Sprite* sp, float x, float y);
void renderSpriteSize(Sprite* sp, float w, float h);

Camera renderCamera(float fov, float x, float y, float z);

void renderClear(const char* color);
void renderDraw(RenderEntity* ent, Camera* cam);
void renderDraw2D(Sprite* sp);
void renderPresent(void);

#endif // NOVA_RENDER_H
