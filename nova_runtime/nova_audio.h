#ifndef NOVA_AUDIO_H
#define NOVA_AUDIO_H

#include <stdbool.h>

// ============================================================
// AUDIO & SOUND TYPES
// ============================================================
typedef struct {
    char path[128];
    float volume;
    float pitch;
    bool isPlaying;
    bool isLooping;
} NovaSound;

typedef struct {
    char path[128];
    float volume;
    bool isPlaying;
    bool isLooping;
} NovaMusic;

// Audio API Functions
void novaAudioInit(void);
NovaSound novaSoundLoad(const char* path);
void novaSoundPlay(NovaSound* sound);
void novaSoundStop(NovaSound* sound);
void novaSoundSetVolume(NovaSound* sound, float vol);
void novaSoundSetPitch(NovaSound* sound, float pitch);
void novaSoundPlay3D(NovaSound* sound, float x, float y, float z);

NovaMusic novaMusicLoad(const char* path);
void novaMusicPlay(NovaMusic* music);
void novaMusicPause(NovaMusic* music);
void novaMusicStop(NovaMusic* music);
void novaMusicSetVolume(NovaMusic* music, float vol);

void novaAudioSetMasterVolume(float vol);
void novaAudioSetListenerPosition(float x, float y, float z);
void novaAudioStopAll(void);

#endif // NOVA_AUDIO_H
