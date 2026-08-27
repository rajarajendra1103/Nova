#ifndef NOVA_UI_H
#define NOVA_UI_H

#include <stdbool.h>

typedef struct {
    char tag[32];
    char text[128];
    char color[32];
    char bg[32];
    float w, h;
    int fontSize;
} UIElement;

typedef UIElement uielement;

UIElement novaAppCreate(const char* title, int w, int h);
UIElement uiCard(void);
UIElement uiButton(const char* text);
UIElement uiText(const char* text);
UIElement uiInput(const char* placeholder);
UIElement uiRow(void);
UIElement uiCol(void);
UIElement uiAppBar(const char* title);
UIElement uiBottomNav(void);
UIElement uiSafeArea(void);
UIElement uiFab(const char* icon);
UIElement uiListTile(const char* title, const char* subtitle);
UIElement uiSwitch(bool checked);
UIElement uiSlider(float min, float max, float value);
void uiAdd(UIElement* parent, UIElement* child);

#endif // NOVA_UI_H
