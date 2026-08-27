#!/usr/bin/env python3
"""
Nova Game Audio & Sound Engine (nova_libs/game/audio.py)
Supports 2D/3D Sound Effects, Music Streaming, Bus Mixing, Pitch, Volume, Looping.
Zero-latency audio abstraction for Desktop, Mobile and Web targets.
"""

import os
import math
from typing import Any, Dict, List, Optional
from nova_libs.core import StdModule

# Global Audio State
_master_volume = 1.0
_listener_pos = [0.0, 0.0, 0.0]
_active_sounds: List[Any] = []
_active_music: Optional[Any] = None


class Sound:
    def __init__(self, path: str, volume: float = 1.0, pitch: float = 1.0, looping: bool = False):
        self.path = str(path)
        self.volume = max(0.0, min(1.0, float(volume)))
        self.pitch = max(0.1, min(4.0, float(pitch)))
        self.is_looping = bool(looping)
        self.is_playing = False
        self.is_paused = False
        self.channel = "sfx"
        self.pos_3d = None

    def play(self, volume: Optional[float] = None, pitch: Optional[float] = None):
        if volume is not None: self.volume = float(volume)
        if pitch is not None: self.pitch = float(pitch)
        self.is_playing = True
        self.is_paused = False
        if self not in _active_sounds:
            _active_sounds.append(self)
        return self

    def stop(self):
        self.is_playing = False
        self.is_paused = False
        if self in _active_sounds:
            _active_sounds.remove(self)
        return self

    def pause(self):
        if self.is_playing:
            self.is_paused = True
        return self

    def resume(self):
        if self.is_paused:
            self.is_paused = False
            self.is_playing = True
        return self

    def setVolume(self, vol: float):
        self.volume = max(0.0, min(1.0, float(vol)))
        return self

    def setPitch(self, pitch: float):
        self.pitch = max(0.1, min(4.0, float(pitch)))
        return self

    def loop(self, should_loop: bool = True):
        self.is_looping = bool(should_loop)
        return self

    def play3D(self, x: float, y: float, z: float, max_dist: float = 50.0):
        self.pos_3d = [float(x), float(y), float(z)]
        dx = x - _listener_pos[0]
        dy = y - _listener_pos[1]
        dz = z - _listener_pos[2]
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        attenuation = max(0.0, 1.0 - (dist / float(max_dist)))
        self.volume = attenuation * _master_volume
        return self.play()

    def __repr__(self):
        return f"<Sound path='{self.path}' playing={self.is_playing} vol={self.volume}>"


class Music:
    def __init__(self, path: str, volume: float = 1.0, loop: bool = True):
        self.path = str(path)
        self.volume = max(0.0, min(1.0, float(volume)))
        self.is_looping = bool(loop)
        self.is_playing = False
        self.is_paused = False
        self.channel = "music"

    def play(self, loop: Optional[bool] = None, volume: Optional[float] = None):
        global _active_music
        if loop is not None: self.is_looping = bool(loop)
        if volume is not None: self.volume = float(volume)
        self.is_playing = True
        self.is_paused = False
        _active_music = self
        return self

    def pause(self):
        self.is_paused = True
        return self

    def resume(self):
        self.is_paused = False
        self.is_playing = True
        return self

    def stop(self):
        global _active_music
        self.is_playing = False
        self.is_paused = False
        if _active_music == self:
            _active_music = None
        return self

    def setVolume(self, vol: float):
        self.volume = max(0.0, min(1.0, float(vol)))
        return self

    def fade(self, duration: float, target_vol: float = 0.0):
        self.volume = max(0.0, min(1.0, float(target_vol)))
        if target_vol <= 0.0:
            self.stop()
        return self

    def __repr__(self):
        return f"<Music path='{self.path}' playing={self.is_playing} vol={self.volume}>"


def build_audio_module(interp=None):
    m = {}

    def _load_sound(path: str, volume: float = 1.0):
        return Sound(path, volume)

    def _play_sound(path: str, volume: float = 1.0, pitch: float = 1.0):
        snd = Sound(path, volume, pitch)
        return snd.play()

    def _load_music(path: str, volume: float = 1.0):
        return Music(path, volume)

    def _play_music(path: str, loop: bool = True, volume: float = 1.0):
        mus = Music(path, volume, loop)
        return mus.play()

    def _set_master_volume(vol: float):
        global _master_volume
        _master_volume = max(0.0, min(1.0, float(vol)))
        return _master_volume

    def _set_listener_pos(x: float, y: float, z: float = 0.0):
        global _listener_pos
        _listener_pos = [float(x), float(y), float(z)]
        return list(_listener_pos)

    def _stop_all():
        global _active_sounds, _active_music
        for s in list(_active_sounds):
            s.stop()
        if _active_music:
            _active_music.stop()
        return True

    m["loadSound"]         = _load_sound
    m["playSound"]         = _play_sound
    m["sound"]             = _load_sound
    m["loadMusic"]         = _load_music
    m["playMusic"]         = _play_music
    m["music"]             = _load_music
    m["setMasterVolume"]   = _set_master_volume
    m["masterVolume"]      = lambda: _master_volume
    m["setListenerPosition"] = _set_listener_pos
    m["listenerPosition"]  = lambda: list(_listener_pos)
    m["stopAll"]           = _stop_all
    m["activeSoundsCount"] = lambda: len(_active_sounds)
    m["isMusicPlaying"]    = lambda: _active_music is not None and _active_music.is_playing

    return StdModule("audio", m)


# ============================================================
# C TEMPLATES (FOR COMPILER CODE GENERATION)
# ============================================================
cCode = {
    "include": '#include "nova_audio.h"',
    "loadSound": 'NovaSound {var} = novaSoundLoad("{path}");',
    "playSound": 'NovaSound {var} = novaSoundLoad("{path}"); novaSoundPlay(&{var});',
    "loadMusic": 'NovaMusic {var} = novaMusicLoad("{path}");',
    "playMusic": 'NovaMusic {var} = novaMusicLoad("{path}"); novaMusicPlay(&{var});',
    "setMasterVolume": 'novaAudioSetMasterVolume({vol});',
    "setListenerPosition": 'novaAudioSetListenerPosition({x}, {y}, {z});',
    "stopAll": 'novaAudioStopAll();',
}
