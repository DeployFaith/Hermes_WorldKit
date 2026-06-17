# Hermes WorldKit — Terrain + Water Overhaul

## Goal
Replace procedural noise terrain with AI-generated heightmap. Replace Lesus ocean shader with SSR lake shader. Result: a designed small town next to a lake instead of a random blob.

## Source Files
- Heightmap: `assets/maps/heightmap.png` (grayscale — black=lake, gray=town, white=hills)
- Biome map: `assets/maps/biome_map.png` (color — blue=water, green=grass, brown=dirt, gray=paved)
- SSR shader: `shaders/water.gdshader` (just installed from asset library)
- Current terrain: `scripts/worldkit/environment/terrain_setup.gd`
- Current water: `scripts/worldkit/environment/water_setup.gd`
- Main scene: `scenes/world.tscn`

---

## Phase 1: Terrain — Load from Heightmap + Biome Map
**File:** `scripts/worldkit/environment/terrain_setup.gd`

- [ ] Remove all procedural noise generation (`_generate_town_maps`, noise setup, etc.)
- [ ] Add `load()` for `assets/maps/heightmap.png`
- [ ] Resize/resample loaded image to 1025x1025 if needed (HEIGHTMAP_SIZE)
- [ ] Map grayscale pixel values to height: black=0.0 → TERRAIN_MIN_HEIGHT, white=1.0 → TERRAIN_MIN_HEIGHT + HEIGHT_SCALE
- [ ] Store heights in `_generated_heights` array (same format as before)
- [ ] Generate heightmap Image for Terrain3D import (FORMAT_RF, same as before)
- [ ] Add `load()` for `assets/maps/biome_map.png`
- [ ] Sample biome map colors in `_control_value_for_point()` instead of using height/slope heuristics:
  - Deep blue (#000088 range) → SAND_ID (waterbed)
  - Light blue (#4488CC range) → SAND_ID (shallow water edge)
  - Bright green (#228B22 range) → GRASS_ID
  - Dark green (#006400 range) → GRASS_ID with DIRT_ID overlay (forest floor)
  - Tan/brown (#C2B280 range) → DIRT_ID (paths/roads)
  - Gray (#808080 range) → DIRT_ID (paved/building plots)
  - Dark brown (#3B2F2F range) → ROCK_ID (hilltops)
- [ ] Keep texture loading, caching, and foliage code unchanged
- [ ] Keep `_position_player_on_terrain` and `_position_build_pad_on_terrain`
- [ ] Update cache version string to `"worldkit_heightmap_v1"`
- [ ] Keep all Terrain3D setup (collision, assets, import) unchanged
- [ ] Player spawn: find a flat area near the town center (gray zone in biome map), not hardcoded

---

## Phase 2: Water — SSR Shader for Lake
**File:** `scripts/worldkit/environment/water_setup.gd`

- [ ] Change shader preload from `lesus_water.gdshader` to `water.gdshader`
- [ ] Remove all Lesus-specific shader parameters (wave_1-8, caustic, foam, edge detection, etc.)
- [ ] Set SSR shader parameters for calm lake:
  - `color_shallow` = greenish-blue lake shallow (~0.15, 0.45, 0.4)
  - `color_deep` = dark lake deep (~0.02, 0.12, 0.18)
  - `transparency` = 0.5 (lake is more opaque than ocean)
  - `roughness` = 0.15
  - `metallic` = 0.05
  - `max_visible_depth` = 12.0
  - `wave_height_scale` = 0.03 (gentle ripples, not ocean waves)
  - `wave_noise_scale_a/b` = 20.0 (large, slow ripples)
  - `wave_time_scale_a/b` = 0.05 (slow movement)
  - `wave_normal_flatness` = 80.0 (very flat normals = calm water)
  - `surface_texture_roughness` = 0.08 (subtle surface detail)
  - `surface_texture_scale` = 0.15
  - `ssr_max_travel` = 20.0
  - `ssr_mix_strength` = 0.4 (subtle reflections for a lake)
  - `refraction_intensity` = 0.25
  - `border_color` = greenish shore color
  - `border_scale` = 1.5
- [ ] Assign `wave_a` and `wave_b` textures — reuse `assets/textures/water/normal_A.png` and `normal_B.png` as wave noise
- [ ] Assign `surface_normals_a` and `surface_normals_b` — same normal textures
- [ ] Reduce water mesh size: from 2200x2200 to ~400x400 (lake-sized, not ocean-sized)
- [ ] Reduce subdivisions: from 320 to ~80 (proportional to size)
- [ ] Position water mesh to align with the lake area in the heightmap (left/center side based on the generated images)
- [ ] Keep `_load_texture()` helper

---

## Phase 3: Scene — Update world.tscn
**File:** `scenes/world.tscn`

- [ ] Update Water node mesh: smaller PlaneMesh (400x400, 80 subdivisions)
- [ ] Update Water node position: move to align with lake in heightmap
- [ ] Remove inline ShaderMaterial sub-resource from scene (water_setup.gd creates it programmatically now)
- [ ] Remove the PlaneMesh_water sub-resource (water_setup.gd creates it programmatically)
- [ ] Verify TerrainSetup node still references correct script
- [ ] Verify Player spawn position makes sense for the new terrain

---

## Phase 4: Cleanup + Verify
- [ ] Delete or archive `shaders/lesus_water.gdshader` (no longer used)
- [ ] Verify .gitignore excludes .import files
- [ ] Run in Godot: terrain loads from images, water renders with SSR, player spawns in town
- [ ] Commit and push
