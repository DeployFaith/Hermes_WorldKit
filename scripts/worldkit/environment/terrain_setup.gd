@tool
extends Node

## Terrain3D setup for Hermes WorldKit.
## Loads textures directly from PNG files on disk — no in-memory creation.
## This ensures Godot stores file references, not binary data.

const REGION_SIZE := 512
const TEXTURE_BASE := "res://assets/textures/terrain/"
const TERRAIN_DATA_DIR := "res://assets/terrain_data/"

const GRASS_ID := 0
const DIRT_ID := 1
const ROCK_ID := 2
const SAND_ID := 3

@export var setup_terrain: bool = false:
	set(value):
		if value and Engine.is_editor_hint():
			_setup()
		setup_terrain = false
	get:
		return false


func _ready() -> void:
	if _find_terrain_child() != null:
		return
	_setup()


func _setup() -> void:
	if not ClassDB.class_exists("Terrain3D"):
		push_warning("[WorldKitTerrain] Terrain3D not available.")
		return

	# Ensure data directory exists
	var abs_path := ProjectSettings.globalize_path(TERRAIN_DATA_DIR)
	DirAccess.make_dir_recursive_absolute(abs_path)

	var terrain = ClassDB.instantiate("Terrain3D")
	terrain.name = "Terrain3D"
	terrain.region_size = REGION_SIZE
	terrain.vertex_spacing = 1.0
	terrain.set("data_directory", TERRAIN_DATA_DIR)

	# Material
	terrain.material = ClassDB.instantiate("Terrain3DMaterial")
	terrain.material.world_background = 0
	terrain.material.auto_shader = false

	# Textures — loaded directly from PNG files on disk (no in-memory creation)
	var assets = ClassDB.instantiate("Terrain3DAssets")
	assets.set_texture(GRASS_ID, _make_ta("Grass", "grass", 0.32, 0.18))
	assets.set_texture(DIRT_ID, _make_ta("Dirt", "dirt", 0.28, 0.23))
	assets.set_texture(ROCK_ID, _make_ta("Rock", "rock", 0.22, 0.12))
	assets.set_texture(SAND_ID, _make_ta("Sand", "sand", 0.28, 0.23))
	terrain.assets = assets

	add_child(terrain, true)
	if Engine.is_editor_hint() and get_tree() != null and get_tree().edited_scene_root != null:
		terrain.owner = get_tree().edited_scene_root

	await get_tree().process_frame
	await get_tree().process_frame

	if terrain.data == null:
		push_error("[WorldKitTerrain] Terrain3D data failed to initialize.")
		return

	if not terrain.data.has_region(Vector2i.ZERO):
		var region = ClassDB.instantiate("Terrain3DRegion")
		region.region_size = REGION_SIZE
		region.vertex_spacing = 1.0
		region.location = Vector2i.ZERO
		terrain.data.add_region(region, true)

	terrain.collision_layer = 1
	terrain.collision_mask = 1
	terrain.collision_shape_size = 32
	terrain.collision_mode = 3

	print("[WorldKitTerrain] Terrain3D ready.")


func _find_terrain_child() -> Node:
	for child in get_children():
		if child.get_class() == "Terrain3D" or child.is_class("Terrain3D"):
			return child
	return null


func _make_ta(display_name: String, prefix: String, uv_scale: float, detiling: float) -> Resource:
	var ta = ClassDB.instantiate("Terrain3DTextureAsset")
	ta.name = display_name
	# load() references files on disk — Godot won't embed these
	ta.albedo_texture = load(TEXTURE_BASE + prefix + "_albedo.png")
	ta.normal_texture = load(TEXTURE_BASE + prefix + "_normal.png")
	ta.uv_scale = uv_scale
	ta.detiling_rotation = detiling
	ta.normal_depth = 0.85
	ta.ao_strength = 0.75
	ta.roughness = 0.12
	return ta
