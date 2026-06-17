# Hermes WorldKit

Hermes WorldKit is a Godot 4.6 modular framework for building 3D interactive experiences with HermesOS embedded as a core in-world module.

## Features

- Terrain3D-based town terrain generation with a flatter buildable center and gentle hills.
- Lesus-style water shader setup and coastal/lake-edge water visuals.
- First-person player controller with walk, sprint, jump, swim, underwater visuals, interaction raycast, and SceneBridge state restore.
- Interaction system for doors, devices, PCs, and HermesOS transitions.
- Preserved dormant building modules for future block placement/build-mode work.
- HermesOS addon imported as a project module.

## Project Entry Point

The active main scene is:

```text
res://scenes/world.tscn
```

`project.godot` points to this scene via `run/main_scene`.

## Repository Layout

```text
addons/terrain_3d/             Terrain3D addon
addons/hermes_os/              HermesOS addon
assets/textures/terrain/       Terrain PBR textures
assets/textures/water/         Water textures
assets/models/nature/          KayKit nature assets
scenes/world.tscn              Main WorldKit scene
scenes/worldkit/               Preserved WorldKit scenes/HUD
scripts/core/                  SceneBridge and device controller autoloads
scripts/worldkit/              WorldKit runtime modules
scripts/archived/              Archived legacy procgen modules
```

## Running

Open the directory in Godot 4.6 and press **F5**. Godot will regenerate import metadata on first open.
