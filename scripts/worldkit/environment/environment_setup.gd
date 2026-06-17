extends WorldEnvironment
class_name WorldKitEnvironmentSetup

func _ready() -> void:
	if environment == null:
		environment = create_worldkit_environment()
	_apply_sun_defaults()

static func create_worldkit_environment() -> Environment:
	var sky_mat := ProceduralSkyMaterial.new()
	sky_mat.sky_top_color = Color(0.27, 0.56, 0.96, 1.0)
	sky_mat.sky_horizon_color = Color(0.82, 0.9, 0.98, 1.0)
	sky_mat.sky_curve = 0.12
	sky_mat.sky_energy_multiplier = 1.18
	sky_mat.ground_bottom_color = Color(0.34, 0.5, 0.68, 1.0)
	sky_mat.ground_horizon_color = Color(0.86, 0.9, 0.88, 1.0)
	sky_mat.ground_curve = 0.1

	var sky := Sky.new()
	sky.sky_material = sky_mat

	var env := Environment.new()
	env.background_mode = Environment.BG_SKY
	env.sky = sky
	env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	env.ambient_light_color = Color(0.78, 0.84, 0.9, 1.0)
	env.ambient_light_sky_contribution = 0.32
	env.ambient_light_energy = 0.24
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.tonemap_exposure = 1.02
	env.tonemap_white = 1.45
	env.ssao_enabled = true
	env.ssao_radius = 1.25
	env.ssao_intensity = 0.82
	env.fog_enabled = true
	env.fog_light_color = Color(0.93, 0.86, 0.74, 1.0)
	env.fog_light_energy = 0.24
	env.fog_sun_scatter = 0.18
	env.fog_density = 0.006
	env.fog_aerial_perspective = 0.62
	env.fog_sky_affect = 0.28
	return env

func _apply_sun_defaults() -> void:
	var sun := get_parent().get_node_or_null("DirectionalLight3D") as DirectionalLight3D
	if sun == null:
		return
	sun.light_color = Color(1.0, 0.91, 0.74, 1.0)
	sun.light_energy = 1.35
	sun.light_angular_distance = 0.22
	sun.shadow_enabled = true
	sun.shadow_bias = 0.035
	sun.shadow_normal_bias = 0.75
	sun.shadow_blur = 0.35
	sun.directional_shadow_blend_splits = true
	sun.directional_shadow_max_distance = 900.0
