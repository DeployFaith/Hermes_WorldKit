# AGENTS.md

## Repo Identity

Hermes WorldKit is a modular Godot 4.6 framework for building 3D interactive experiences. It combines Terrain3D-powered environments, a first-person exploration controller, interaction systems, dormant building modules, and HermesOS as a core in-world computing module.

## Key Paths

- `project.godot` — Godot project config; main scene is `res://scenes/world.tscn`.
- `scenes/world.tscn` — main WorldKit 3D scene.
- `scripts/worldkit/environment/` — terrain, water, and environment setup.
- `scripts/worldkit/player/` — merged first-person controller with walking, sprinting, swimming, raycast interaction, and SceneBridge state restore.
- `scripts/worldkit/interaction/` — E-to-interact systems for doors, devices, PCs, and HermesOS transitions.
- `scripts/worldkit/building/` — dormant block/world/build HUD modules imported for future activation.
- `scripts/worldkit/objects/` — preserved interactive object scripts.
- `addons/hermes_os/` — HermesOS addon; core module for OS shell, apps, HermesUI, WorldWeb, and agent integration.
- `addons/terrain_3d/` — Terrain3D addon.

## Development Rules

- Keep WorldKit modular: prefer reusable scripts under `scripts/worldkit/` over scene-specific code.
- Use `scenes/world.tscn` as the active main scene; do not reintroduce `world_3d.tscn` as the entry point.
- Scene/script references must use the new `res://scripts/worldkit/...` paths.
- Dormant building/procgen modules should remain inactive unless explicitly re-enabled; `WorldGenerator.generate_on_ready` must stay `false` by default.
- Do not commit Godot generated files (`.godot/`, `.import/`, `*.import`). Godot will regenerate them.

## Testing

Open the project in Godot 4.6 and run the main scene. Validate terrain generation, water/environment visuals, player movement/swimming, interaction prompts, and HermesOS transitions through `SceneBridge`.
