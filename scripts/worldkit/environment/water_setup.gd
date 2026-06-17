extends MeshInstance3D
class_name WorldKitWaterSetup

const WATER_SHADER := preload("res://shaders/water.gdshader")
const NORMAL_A_PATH := "res://assets/textures/water/normal_A.png"
const NORMAL_B_PATH := "res://assets/textures/water/normal_B.png"

@export var water_size: float = 400.0
@export var subdivisions: int = 80
@export var water_height: float = 0.0
@export var water_x_offset: float = -125.0
@export var water_z_offset: float = 0.0

func _ready() -> void:
	_setup_mesh()
	_setup_material()

func _setup_mesh() -> void:
	if mesh == null:
		var plane := PlaneMesh.new()
		plane.size = Vector2(water_size, water_size)
		plane.subdivide_width = subdivisions
		plane.subdivide_depth = subdivisions
		mesh = plane
	cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	position = Vector3(water_x_offset, water_height, water_z_offset)

func _setup_material() -> void:
	if get_surface_override_material(0) != null:
		return
	var mat := ShaderMaterial.new()
	mat.shader = WATER_SHADER

	var normal_a := _load_texture(NORMAL_A_PATH)
	var normal_b := _load_texture(NORMAL_B_PATH)

	mat.set_shader_parameter("color_shallow", Vector3(0.15, 0.45, 0.40))
	mat.set_shader_parameter("color_deep", Vector3(0.02, 0.12, 0.18))
	mat.set_shader_parameter("transparency", 0.5)
	mat.set_shader_parameter("metallic", 0.05)
	mat.set_shader_parameter("roughness", 0.15)
	mat.set_shader_parameter("max_visible_depth", 12.0)

	mat.set_shader_parameter("wave_a", normal_a)
	mat.set_shader_parameter("wave_b", normal_b)
	mat.set_shader_parameter("wave_move_direction_a", Vector2(-0.3, 0.1))
	mat.set_shader_parameter("wave_move_direction_b", Vector2(0.1, 0.4))
	mat.set_shader_parameter("wave_noise_scale_a", 20.0)
	mat.set_shader_parameter("wave_noise_scale_b", 25.0)
	mat.set_shader_parameter("wave_time_scale_a", 0.05)
	mat.set_shader_parameter("wave_time_scale_b", 0.04)
	mat.set_shader_parameter("wave_height_scale", 0.03)
	mat.set_shader_parameter("wave_normal_flatness", 80.0)

	mat.set_shader_parameter("surface_normals_a", normal_a)
	mat.set_shader_parameter("surface_normals_b", normal_b)
	mat.set_shader_parameter("surface_normals_move_direction_a", Vector2(-0.2, 0.1))
	mat.set_shader_parameter("surface_normals_move_direction_b", Vector2(0.1, 0.3))
	mat.set_shader_parameter("surface_texture_roughness", 0.08)
	mat.set_shader_parameter("surface_texture_scale", 0.15)
	mat.set_shader_parameter("surface_texture_time_scale", 0.03)

	mat.set_shader_parameter("ssr_resolution", 1.0)
	mat.set_shader_parameter("ssr_max_travel", 20.0)
	mat.set_shader_parameter("ssr_max_diff", 4.0)
	mat.set_shader_parameter("ssr_mix_strength", 0.4)
	mat.set_shader_parameter("ssr_screen_border_fadeout", 0.3)
	mat.set_shader_parameter("refraction_intensity", 0.25)

	mat.set_shader_parameter("border_color", Vector3(0.2, 0.35, 0.25))
	mat.set_shader_parameter("border_scale", 1.5)
	mat.set_shader_parameter("border_near", 0.5)
	mat.set_shader_parameter("border_far", 300.0)

	set_surface_override_material(0, mat)

func _load_texture(path: String) -> Texture2D:
	if ResourceLoader.exists(path):
		var imported := load(path)
		if imported is Texture2D:
			return imported
	var image := Image.new()
	if image.load(ProjectSettings.globalize_path(path)) != OK:
		push_warning("[WorldKitWater] Failed to load texture: %s" % path)
		return null
	return ImageTexture.create_from_image(image)
