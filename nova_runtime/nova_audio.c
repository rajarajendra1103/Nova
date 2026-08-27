#include "nova_audio.h"
#include <stdio.h>
#include <string.h>
#include <math.h>

static float g_masterVolume = 1.0f;
static float g_listenerX = 0.0f, g_listenerY = 0.0f, g_listenerZ = 0.0f;

void novaAudioInit(void) {
    printf("[Nova Audio Engine: Initialized (Low-Latency Audio Stream)]\n");
}

NovaSound novaSoundLoad(const char* path) {
    NovaSound s;
    strncpy(s.path, path ? path : "sound.wav", 127);
    s.volume = 1.0f;
    s.pitch = 1.0f;
    s.isPlaying = false;
    s.isLooping = false;
    return s;
}

void novaSoundPlay(NovaSound* sound) {
    if (sound) {
        sound->isPlaying = true;
        printf("[Nova Sound Play] '%s' @ vol=%.2f, pitch=%.2f\n", sound->path, sound->volume * g_masterVolume, sound->pitch);
    }
}

void novaSoundStop(NovaSound* sound) {
    if (sound) sound->isPlaying = false;
}

void novaSoundSetVolume(NovaSound* sound, float vol) {
    if (sound) sound->volume = vol;
}

void novaSoundSetPitch(NovaSound* sound, float pitch) {
    if (sound) sound->pitch = pitch;
}

void novaSoundPlay3D(NovaSound* sound, float x, float y, float z) {
    if (sound) {
        float dx = x - g_listenerX;
        float dy = y - g_listenerY;
        float dz = z - g_listenerZ;
        float dist = sqrtf(dx*dx + dy*dy + dz*dz);
        float att = 1.0f - (dist / 50.0f);
        if (att < 0.0f) att = 0.0f;
        sound->volume = att;
        novaSoundPlay(sound);
    }
}

NovaMusic novaMusicLoad(const char* path) {
    NovaMusic m;
    strncpy(m.path, path ? path : "music.mp3", 127);
    m.volume = 1.0f;
    m.isPlaying = false;
    m.isLooping = true;
    return m;
}

void novaMusicPlay(NovaMusic* music) {
    if (music) {
        music->isPlaying = true;
        printf("[Nova Music Stream] Playing '%s' (Loop: %s)\n", music->path, music->isLooping ? "true" : "false");
    }
}

void novaMusicPause(NovaMusic* music) {
    if (music) music->isPlaying = false;
}

void novaMusicStop(NovaMusic* music) {
    if (music) music->isPlaying = false;
}

void novaMusicSetVolume(NovaMusic* music, float vol) {
    if (music) music->volume = vol;
}

void novaAudioSetMasterVolume(float vol) {
    g_masterVolume = vol;
}

void novaAudioSetListenerPosition(float x, float y, float z) {
    g_listenerX = x; g_listenerY = y; g_listenerZ = z;
}

void novaAudioStopAll(void) {
    printf("[Nova Audio: Stopped all active channels]\n");
}
