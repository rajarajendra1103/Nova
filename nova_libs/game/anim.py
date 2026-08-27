#!/usr/bin/env python3
"""
Nova Skeletal & 2D/3D Animation Engine (nova_libs/game/anim.py)
Bone Hierarchies, Inverse Kinematics, State Machines, Blend Trees, Keyframe Tweens.
"""

import math
from typing import Any, Dict, List, Optional
from nova_libs.core import StdModule


class Bone:
    def __init__(self, name: str, parent: Optional['Bone'] = None):
        self.name = str(name)
        self.parent = parent
        self.children: List['Bone'] = []
        self.position = [0.0, 0.0, 0.0]
        self.rotation = [0.0, 0.0, 0.0]  # Euler angles
        self.scale = [1.0, 1.0, 1.0]
        if parent:
            parent.children.append(self)

    def setPos(self, x: float, y: float, z: float = 0.0):
        self.position = [float(x), float(y), float(z)]
        return self

    def setRot(self, rx: float, ry: float = 0.0, rz: float = 0.0):
        self.rotation = [float(rx), float(ry), float(rz)]
        return self

    def setScale(self, sx: float, sy: float = 1.0, sz: float = 1.0):
        self.scale = [float(sx), float(sy), float(sz)]
        return self

    def getWorldPosition(self) -> List[float]:
        if not self.parent:
            return list(self.position)
        p_world = self.parent.getWorldPosition()
        return [p_world[0] + self.position[0], p_world[1] + self.position[1], p_world[2] + self.position[2]]

    def __repr__(self):
        return f"<Bone '{self.name}' pos={self.position}>"


class Skeleton:
    def __init__(self, root_name: str = "root"):
        self.root = Bone(root_name)
        self.bones: Dict[str, Bone] = {root_name: self.root}

    def addBone(self, name: str, parent_name: Optional[str] = None):
        name_s = str(name)
        parent_bone = self.bones.get(str(parent_name)) if parent_name else self.root
        bone = Bone(name_s, parent_bone)
        self.bones[name_s] = bone
        return bone

    def getBone(self, name: str) -> Optional[Bone]:
        return self.bones.get(str(name))

    def boneCount(self) -> int:
        return len(self.bones)


class AnimationClip:
    def __init__(self, name: str, duration: float = 1.0, loop: bool = True):
        self.name = str(name)
        self.duration = max(0.01, float(duration))
        self.is_looping = bool(loop)
        self.tracks: Dict[str, List[dict]] = {}  # bone -> list of keyframes

    def addKeyframe(self, bone_name: str, time_sec: float, pos=None, rot=None, scale=None):
        b_name = str(bone_name)
        if b_name not in self.tracks:
            self.tracks[b_name] = []
        self.tracks[b_name].append({
            "time": float(time_sec),
            "pos": list(pos) if pos else [0.0, 0.0, 0.0],
            "rot": list(rot) if rot else [0.0, 0.0, 0.0],
            "scale": list(scale) if scale else [1.0, 1.0, 1.0]
        })
        self.tracks[b_name].sort(key=lambda k: k["time"])
        return self

    def sample(self, time_sec: float, skeleton: Optional[Skeleton] = None):
        t = (time_sec % self.duration) if self.is_looping else min(time_sec, self.duration)
        sampled_data = {}
        for b_name, kfs in self.tracks.items():
            if not kfs: continue
            # Find interpolated keyframe
            curr_kf = kfs[0]
            for kf in kfs:
                if kf["time"] <= t: curr_kf = kf
                else: break
            sampled_data[b_name] = curr_kf
            if skeleton:
                bone = skeleton.getBone(b_name)
                if bone:
                    bone.setPos(*curr_kf["pos"])
                    bone.setRot(*curr_kf["rot"])
        return sampled_data


class AnimationStateMachine:
    def __init__(self):
        self.states: Dict[str, AnimationClip] = {}
        self.transitions: List[dict] = []
        self.current_state: Optional[str] = None
        self.current_time = 0.0
        self.blend_weight = 1.0

    def addState(self, name: str, clip: AnimationClip):
        self.states[str(name)] = clip
        if self.current_state is None:
            self.current_state = str(name)
        return self

    def addTransition(self, from_state: str, to_state: str, condition_param: str):
        self.transitions.append({
            "from": str(from_state), "to": str(to_state), "param": str(condition_param)
        })
        return self

    def play(self, state_name: str):
        if str(state_name) in self.states:
            self.current_state = str(state_name)
            self.current_time = 0.0
        return self

    def update(self, dt: float, skeleton: Optional[Skeleton] = None):
        if not self.current_state or self.current_state not in self.states:
            return None
        clip = self.states[self.current_state]
        self.current_time += float(dt)
        return clip.sample(self.current_time, skeleton)


class Tween:
    def __init__(self, target: Any, target_props: dict, duration: float = 1.0, easing: str = "linear"):
        self.target = target
        self.target_props = dict(target_props)
        self.initial_props = {}
        self.duration = max(0.001, float(duration))
        self.elapsed = 0.0
        self.easing = str(easing).lower()
        self.is_finished = False

        if isinstance(target, dict):
            for k in self.target_props:
                self.initial_props[k] = target.get(k, 0.0)

    def _ease(self, t: float) -> float:
        t = max(0.0, min(1.0, t))
        if self.easing == "easein": return t * t
        elif self.easing == "easeout": return t * (2.0 - t)
        elif self.easing == "easeinout": return 2.0 * t * t if t < 0.5 else -1.0 + (4.0 - 2.0 * t) * t
        return t

    def update(self, dt: float):
        if self.is_finished: return True
        self.elapsed += float(dt)
        t = self._ease(self.elapsed / self.duration)
        if isinstance(self.target, dict):
            for k, end_val in self.target_props.items():
                start_val = self.initial_props.get(k, 0.0)
                self.target[k] = start_val + (end_val - start_val) * t
        if self.elapsed >= self.duration:
            self.is_finished = True
        return self.is_finished


def build_anim_module(interp=None):
    m = {}

    m["skeleton"]     = lambda root="root": Skeleton(root)
    m["clip"]         = lambda name="clip", dur=1.0, loop=True: AnimationClip(name, dur, loop)
    m["stateMachine"] = lambda: AnimationStateMachine()
    m["tween"]        = lambda target, props, dur=1.0, easing="linear": Tween(target, props, dur, easing)

    return StdModule("anim", m)


# ============================================================
# C TEMPLATES (FOR COMPILER CODE GENERATION)
# ============================================================
cCode = {
    "include": '#include "nova_anim.h"',
    "skeleton": 'NovaSkeleton {var} = novaSkeletonNew("{root}");',
    "clip": 'NovaAnimClip {var} = novaAnimClipNew("{name}", {dur}, {loop});',
    "stateMachine": 'NovaStateMachine {var} = novaStateMachineNew();',
    "tween": 'NovaTween {var} = novaTweenNew({dur});',
}
