# Hermes WorldKit — Import Plan

## New Repo
- Local: `/home/kyle/Create/repos/hermes-agent/Hermes_WorldKit/`
- Upstream: `https://github.com/DeployFaith/Hermes_WorldKit.git`
- Engine: Godot 4.6, Forward Plus, Jolt Physics

## Source Repos
- **Hermesverse**: `/home/kyle/Create/repos/hermes-agent/Hermesverse/`
- **Hermes_OS**: `/home/kyle/Create/repos/hermes-agent/Hermes_OS/`

---

## Import Map

### From Hermesverse — Addons

| Source | Destination | Notes |
|--------|-------------|-------|
| `addons/terrain_3d/` | `addons/terrain_3d/` | Terrain3D v1.0.2 addon, full copy |

### From Hermesverse — Assets

| Source | Destination | Notes |
|--------|-------------|-------|
| `assets/textures/terrain/` | `assets/textures/terrain/` | PBR terrain textures (grass, dirt, rock, sand — albedo, normal, roughness) |
| `assets/textures/water/` | `assets/textures/water/` | Lesus water textures (foam, normals, caustics, UV sampler) |
| `assets/models/nature/` | `assets/models/nature/` | KayKit Forest Nature Pack (trees, bushes, rocks — gltf + bin + textures) |

### From Hermesverse — Shaders

| Source | Destination | Notes |
|--------|-------------|-------|
| `shaders/lesus_water.gdshader` | `shaders/lesus_water.gdshader` | Lesus water shader |

### From Hermesverse — Scripts (refactored into worldkit/ structure)

| Source | Destination | Notes |
|--------|-------------|-------|
| `scripts/testing/terrain3d_test_setup.gd` | `scripts/worldkit/environment/terrain_setup.gd` | Refactored: town parameters instead of island |
| `scripts/testing/terrain3d_test_player.gd` | `scripts/worldkit/player/player_controller.gd` | Merged with interaction raycast from main scene player |
| `scripts/world_3d/interaction_system.gd` | `scripts/worldkit/interaction/interaction_system.gd` | Kept as-is, paths updated |
| `scripts/world_3d/block_library.gd` | `scripts/worldkit/building/block_library.gd` | Dormant module |
| `scripts/world_3d/block_world.gd` | `scripts/worldkit/building/block_world.gd` | Dormant module |
| `scripts/world_3d/placement_controller.gd` | `scripts/worldkit/building/placement_controller.gd` | Dormant module |
| `scripts/world_3d/world_generator.gd` | `scripts/worldkit/building/world_generator.gd` | Dormant module |
| `scripts/world_3d/world_3d_hud.gd` | `scripts/worldkit/building/world_3d_hud.gd` | Dormant module |
| `scripts/world_3d/room_builder.gd` | `scripts/worldkit/building/room_builder.gd` | Dormant module |
| `scripts/world_3d/hallway_builder.gd` | `scripts/worldkit/building/hallway_builder.gd` | Dormant module |
| `scripts/world_3d/smart_lamp_block.gd` | `scripts/worldkit/building/smart_lamp_block.gd` | Dormant module |
| `scripts/world_3d/items/build_item.gd` | `scripts/worldkit/building/items/build_item.gd` | Dormant module |
| `scripts/core/scene_bridge.gd` | `scripts/core/scene_bridge.gd` | Core autoload, kept as-is |
| `scripts/core/home_device_controller.gd` | `scripts/core/home_device_controller.gd` | Core autoload, kept as-is |

### From Hermesverse — Objects & Scenes (kept for later use)

| Source | Destination | Notes |
|--------|-------------|-------|
| `scripts/world_3d/objects/` | `scripts/worldkit/objects/` | All object scripts (doors, devices, interactable, monitor, desktop_preview) |
| `scenes/objects/` | `scenes/objects/` | All object scenes (furniture, doors, decor, devices, computer) |
| `scenes/room.tscn` | `scenes/room.tscn` | Room scene |
| `scenes/world_3d_hud.tscn` | `scenes/worldkit/world_3d_hud.tscn` | Build HUD scene |
| `scenes/desktop_preview.tscn` | `scenes/desktop_preview.tscn` | Desktop preview scene |

### From Hermesverse — Preserved for reference (not active)

| Source | Destination | Notes |
|--------|-------------|-------|
| `scenes/testing/terrain3d_test.tscn` | `scenes/testing/terrain3d_test.tscn` | Reference scene |
| `scripts/testing/terrain3d_test_setup.gd` | `scripts/testing/terrain3d_test_setup.gd` | Original, before refactoring |
| `scripts/testing/terrain3d_test_player.gd` | `scripts/testing/terrain3d_test_player.gd` | Original, before refactoring |
| `scripts/world_3d/procgen/` | `scripts/archived/procgen/` | Old low-poly terrain system (archived) |
| `scripts/world_3d/room_controller.gd` | `scripts/archived/room_controller.gd` | Old room controller (stub) |

### From Hermes_OS

| Source | Destination | Notes |
|--------|-------------|-------|
| `addons/hermes_os/` | `addons/hermes_os/` | Full HermesOS addon (OS shell, apps, HermesUI, WorldWeb, agent gateway, godot_wry) |

### New Files to Create

| File | Purpose |
|------|---------|
| `project.godot` | New project config: WorldKit autoloads, display, physics, plugins |
| `scenes/world.tscn` | Main game scene with Terrain3D, water, environment, player, dormant building |
| `scripts/worldkit/environment/water_setup.gd` | Water mesh + Lesus shader instantiation |
| `scripts/worldkit/environment/environment_setup.gd` | Sky, fog, SSAO, tonemap, sun config |
| `icon.svg` | Project icon (can use Hermesverse icon or new one) |
| `.gitignore` | Godot gitignore |
| `AGENTS.md` | Repo guide for AI agents |
| `README.md` | Basic project readme |

---

## Execution Order

1. **Create project.godot** — engine config, autoloads, plugins, display settings
2. **Copy addons** — terrain_3d and hermes_os (binary copy, no modifications)
3. **Copy assets** — textures, models (binary copy)
4. **Copy shaders** — lesus_water.gdshader
5. **Copy & reorganize scripts** — into worldkit/ structure
6. **Create new scripts** — water_setup.gd, environment_setup.gd
7. **Build scenes/world.tscn** — the main game scene
8. **Copy preserved scenes** — objects, room, HUD, testing
9. **Archive old scripts** — procgen/ into archived/
10. **Create .gitignore, AGENTS.md, README.md**
11. **Initial commit & push**

---

## project.godot Config

```ini
[application]
config/name="Hermes WorldKit"
run/main_scene="res://scenes/world.tscn"
config/features=PackedStringArray("4.6", "Forward Plus")

[autoload]
SceneBridge="*res://scripts/core/scene_bridge.gd"
HomeDeviceController="*res://scripts/core/home_device_controller.gd"
HermesOSKernel="*res://addons/hermes_os/scripts/hermes/hermes_os_kernel.gd"
McpInteractionServer="*res://addons/hermes_os/scripts/hermes/mcp_interaction_server.gd"

[display]
window/size/viewport_width=1920
window/size/viewport_height=1080
window/size/mode=3
window/stretch/mode="canvas_items"
window/stretch/aspect="expand"
window/size/min_width=800
window/size/min_height=450

[editor_plugins]
enabled=PackedStringArray("res://addons/hermes_os/plugin.cfg", "res://addons/terrain_3d/plugin.cfg")

[physics]
3d/physics_engine="Jolt Physics"

[rendering]
rendering_device/driver.windows="d3d12"
```

---

## Scene Tree for scenes/world.tscn

```
World (Node3D)
├── TerrainSetup (Node) — scripts/worldkit/environment/terrain_setup.gd
├── Water (MeshInstance3D) — 2200x2200 plane, Lesus shader material
├── DirectionalLight3D — warm sun, shadows
├── WorldEnvironment — procedural sky, SSAO, fog, tonemap
├── Player (CharacterBody3D) — scripts/worldkit/player/player_controller.gd
│   ├── CollisionShape3D (capsule)
│   └── Camera3D
│       └── RayCast3D (interaction)
├── InteractionSystem (Node) — scripts/worldkit/interaction/interaction_system.gd
├── BlockLibrary (Node) — DORMANT
├── BlockWorld (Node3D) — DORMANT
├── PlacementController (Node) — DORMANT
├── HUD (CanvasLayer) — DORMANT
├── WorldGenerator (Node) — DORMANT
└── Room (Node3D) — preserved for future use
```
