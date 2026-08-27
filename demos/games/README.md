# 🎮 Nova Games & Game Engine Demos

This directory contains full, working Nova game demos showcasing 2D/3D GPU rendering, rigid-body physics, 3D audio, multiplayer networking, skeletal animation, and ECS.

---

## 📁 Demo Files & Features

| File | Description | Key Modules |
| :--- | :--- | :--- |
| [`test_game_engine_advanced.nova`](./test_game_engine_advanced.nova) | **Advanced Game Engine**: 3D Positional Audio, Multiplayer UDP host & RPCs, Skeletal Bone Animation & State Machines, Entity Component System (ECS). | `audio`, `net`, `anim`, `ecs` |
| [`test_v2_game_unified.nova`](./test_v2_game_unified.nova) | **2D & 3D Core Game Engine**: Direct GPU rendering, PBR materials, 2D sprites, physics bodies & gravity, keyboard/mouse input, and memory pooling. | `game`, `render`, `physics`, `input`, `asset`, `mem` |
| [`mygame.nova`](./mygame.nova) | **Full 3D Action RPG Showcase**: 3D hero entity with camera control, AI neural network inference, and 120 FPS game loop. | `game`, `render`, `ai`, `numpy`, `mem` |

---

## 🚀 How to Run

### Run with the Nova Interpreter:
```powershell
# 1. Advanced Game Systems (Audio, Multiplayer, Skeletal Anim, ECS)
python nova_interpreter.py demos/games/test_game_engine_advanced.nova

# 2. Core 2D/3D Engine & Physics
python nova_interpreter.py demos/games/test_v2_game_unified.nova

# 3. Full 3D Game & AI Showcase
python nova_interpreter.py demos/games/mygame.nova
```

### Compile to Standalone Native Binary:
```powershell
python nova_compiler.py demos/games/test_game_engine_advanced.nova
python nova_compiler.py demos/games/mygame.nova
```
