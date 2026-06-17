extends MeshInstance3D
class_name WorldKitWaterSetup

const WATER_SHADER := preload("res://shaders/lesus_water.gdshader")
const FOAM_TEXTURE_PATH := "res://assets/textures/water/foam_albedo.png"
const NORMAL_A_PATH := "res://assets/textures/water/normal_A.png"
const NORMAL_B_PATH := "res://assets/textures/water/normal_B.png"
const UV_SAMPLER_PATH := "res://assets/textures/water/uv_example.png"
const CAUSTICS_PATH := "res://assets/textures/water/caustic.png"

@export var water_size: float = 2200.0
@export var subdivisions: int = 320
@export var waterline_height: float = 0.0

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
	position.y = waterline_height

func _setup_material() -> void:
	if get_surface_override_material(0) != null:
		return
	var mat := ShaderMaterial.new()
	mat.shader = WATER_SHADER
	mat.set_shader_parameter("wave_1", Vector4(0.3, 4.0, 0.025, 0.9))
	mat.set_shader_parameter("wave_2", Vector4(-0.26, -0.19, 0.004, 0.65))
	mat.set_shader_parameter("wave_3", Vector4(-7.67, 5.63, 0.012, 0.8))
	mat.set_shader_parameter("wave_4", Vector4(-0.42, -1.63, 0.01, 0.7))
	mat.set_shader_parameter("wave_5", Vector4(1.66, 0.07, 0.014, 1.2))
	mat.set_shader_parameter("wave_6", Vector4(1.2, 1.14, 0.004, 0.75))
	mat.set_shader_parameter("wave_7", Vector4(-1.6, 7.3, 0.01, 1.05))
	mat.set_shader_parameter("wave_8", Vector4(-0.42, -1.63, 0.012, 1.1))
	mat.set_shader_parameter("time_factor", 7.5)
	mat.set_shader_parameter("noise_zoom", 1.25)
	mat.set_shader_parameter("noise_amp", 0.035)
	mat.set_shader_parameter("base_water_color", Color(0.08, 0.55, 0.7, 1.0))
	mat.set_shader_parameter("fresnel_water_color", Color(0.62, 0.95, 1.0, 1.0))
	mat.set_shader_parameter("deep_water_color", Color(0.01, 0.08, 0.22, 0.92))
	mat.set_shader_parameter("shallow_water_color", Color(0.28, 0.88, 0.9, 0.62))
	mat.set_shader_parameter("beers_law", 0.34)
	mat.set_shader_parameter("depth_offset", -0.75)
	mat.set_shader_parameter("near", 7.0)
	mat.set_shader_parameter("far", 10000.0)
	mat.set_shader_parameter("waterline_height", waterline_height)
	mat.set_shader_parameter("underwater_discard_margin", 0.08)
	mat.set_shader_parameter("edge_texture_scale", 1.35)
	mat.set_shader_parameter("edge_texture_offset", 0.35)
	mat.set_shader_parameter("edge_texture_speed", 0.025)
	mat.set_shader_parameter("edge_foam_intensity", 2.4)
	mat.set_shader_parameter("edge_fade_start", -0.35)
	mat.set_shader_parameter("edge_fade_end", 2.25)
	mat.set_shader_parameter("edge_foam_texture", _load_texture(FOAM_TEXTURE_PATH))
	mat.set_shader_parameter("peak_height_threshold", 1.35)
	mat.set_shader_parameter("peak_color", Vector3(1.0, 1.0, 1.0))
	mat.set_shader_parameter("peak_intensity", 0.25)
	mat.set_shader_parameter("foam_texture", _load_texture(FOAM_TEXTURE_PATH))
	mat.set_shader_parameter("foam_intensity", 0.18)
	mat.set_shader_parameter("foam_scale", 0.55)
	mat.set_shader_parameter("metallic", 0.15)
	mat.set_shader_parameter("roughness", 0.035)
	mat.set_shader_parameter("uv_scale_text_a", 0.08)
	mat.set_shader_parameter("uv_speed_text_a", Vector2(0.055, 0.035))
	mat.set_shader_parameter("uv_scale_text_b", 0.35)
	mat.set_shader_parameter("uv_speed_text_b", Vector2(-0.025, 0.018))
	mat.set_shader_parameter("normal_strength", 0.42)
	mat.set_shader_parameter("uv_sampler_scale", 0.18)
	mat.set_shader_parameter("blend_factor", 0.32)
	mat.set_shader_parameter("perturbation_strength", 0.85)
	mat.set_shader_parameter("perturbation_time", 0.22)
	mat.set_shader_parameter("normalmap_a", _load_texture(NORMAL_A_PATH))
	mat.set_shader_parameter("normalmap_b", _load_texture(NORMAL_B_PATH))
	mat.set_shader_parameter("uv_sampler", _load_texture(UV_SAMPLER_PATH))
	mat.set_shader_parameter("caustic_sampler", _load_texture(CAUSTICS_PATH))
	mat.set_shader_parameter("num_caustic_layers", 16.0)
	mat.set_shader_parameter("caustic_distortion_strength", 0.0015)
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
