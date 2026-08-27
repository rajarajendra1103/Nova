#ifndef NOVA_INPUT_H
#define NOVA_INPUT_H

#include <stdbool.h>

bool inputKey(const char* name);
bool inputKeyDown(const char* name);
bool inputKeyUp(const char* name);
float inputMouseX(void);
float inputMouseY(void);
bool inputMouseDown(const char* button);
float inputTouchX(void);
float inputTouchY(void);
bool inputTouchDown(void);

#endif // NOVA_INPUT_H
