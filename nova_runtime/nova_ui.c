#include "nova_ui.h"
#include <string.h>

UIElement novaAppCreate(const char* title, int w, int h) {
    UIElement el;
    strcpy(el.tag, "app");
    strncpy(el.text, title ? title : "Nova App", 127);
    el.w = (float)w; el.h = (float)h;
    return el;
}

UIElement uiCard(void) {
    UIElement el;
    strcpy(el.tag, "card");
    strcpy(el.bg, "#1e293b");
    el.w = 400; el.h = 300;
    return el;
}

UIElement uiButton(const char* text) {
    UIElement el;
    strcpy(el.tag, "button");
    strncpy(el.text, text ? text : "Button", 127);
    strcpy(el.bg, "#3b82f6");
    strcpy(el.color, "#ffffff");
    return el;
}

UIElement uiText(const char* text) {
    UIElement el;
    strcpy(el.tag, "text");
    strncpy(el.text, text ? text : "", 127);
    strcpy(el.color, "#f8fafc");
    el.fontSize = 16;
    return el;
}

UIElement uiInput(const char* placeholder) {
    UIElement el;
    strcpy(el.tag, "input");
    strncpy(el.text, placeholder ? placeholder : "", 127);
    return el;
}

UIElement uiRow(void) {
    UIElement el;
    strcpy(el.tag, "row");
    return el;
}

UIElement uiCol(void) {
    UIElement el;
    strcpy(el.tag, "col");
    return el;
}

UIElement uiAppBar(const char* title) {
    UIElement el;
    strcpy(el.tag, "appbar");
    strncpy(el.text, title ? title : "App", 127);
    strcpy(el.bg, "#0f172a");
    strcpy(el.color, "#ffffff");
    el.h = 56;
    return el;
}

UIElement uiBottomNav(void) {
    UIElement el;
    strcpy(el.tag, "bottomnav");
    strcpy(el.bg, "#1e293b");
    el.h = 64;
    return el;
}

UIElement uiSafeArea(void) {
    UIElement el;
    strcpy(el.tag, "safearea");
    return el;
}

UIElement uiFab(const char* icon) {
    UIElement el;
    strcpy(el.tag, "fab");
    strncpy(el.text, icon ? icon : "+", 127);
    strcpy(el.bg, "#6366f1");
    strcpy(el.color, "#ffffff");
    el.w = 56; el.h = 56;
    return el;
}

UIElement uiListTile(const char* title, const char* subtitle) {
    UIElement el;
    strcpy(el.tag, "listtile");
    strncpy(el.text, title ? title : "", 127);
    return el;
}

UIElement uiSwitch(bool checked) {
    UIElement el;
    strcpy(el.tag, "switch");
    strcpy(el.bg, checked ? "#22c55e" : "#475569");
    return el;
}

UIElement uiSlider(float min, float max, float value) {
    UIElement el;
    strcpy(el.tag, "slider");
    el.w = 200;
    return el;
}

void uiAdd(UIElement* parent, UIElement* child) {
    // Fluent composition
}
