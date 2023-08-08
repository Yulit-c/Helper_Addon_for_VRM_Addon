from typing import Literal

from .addon_classes import (
    MToon1ParameterNames,
    MToon1MaterialParameters,
)


"""---------------------------------------------------------
    VRM Component
---------------------------------------------------------"""
VRM_COMPONENT_TYPES = Literal[
    "FIRST_PERSON",
    "EXPRESSION",
    "EXPRESSION_MORPH",
    "EXPRESSION_MATERIAL",
    "COLLIDER",
    "COLLIDER_GROUP",
    "SPRING",
    "CONSTRAINT",
]

UI_LIST_CUSTOM_FILTER_TYPE = Literal[
    "FIRST_PERSON",
    "EXPRESSION",
    "EXPRESSION_MORPH",
    "EXPRESSION_MATERIAL",
    "COLLIDER",
    "COLLIDER_GROUP",
    "SPRING",
    "BONE_GROUP",
    "COLLIDER_GROUP_OPERATOR",
    "SPRING_OPERATOR",
    "CONSTRAINT",
]


"""---------------------------------------------------------
------------------------------------------------------------
    Expression
------------------------------------------------------------
---------------------------------------------------------"""
PRESET_EXPRESSION_NAME_DICT = {
    "happy": "Happy",
    "angry": "Angry",
    "sad": "Sad",
    "relaxed": "Relaxed",
    "surprised": "Suprised",
    "neutral": "Neutral",
    "aa": "Aa",
    "ih": "Ih",
    "ou": "Ou",
    "ee": "Ee",
    "oh": "Oh",
    "blink": "Blink",
    "blink_left": "Blink Left",
    "blink_right": "Blink Right",
    "look_up": "Look Up",
    "look_down": "Look Down",
    "look_left": "Look Left",
    "look_right": "Look Right",
}


"""---------------------------------------------------------
    Spring
---------------------------------------------------------"""
JOINT_PROP_NAMES = (
    "hit_radius",
    "stiffness",
    "drag_force",
    "gravity_power",
    "gravity_dir",
    "damping_ratio",
)

"""---------------------------------------------------------
    MToon
---------------------------------------------------------"""
MTOON_ATTRIBUTE_NAMES: MToon1ParameterNames = {
    "texture_scale": "pbr_metallic_roughness.base_color_texture.extensions.khr_texture_transform.scale",
    "texture_offset": "pbr_metallic_roughness.base_color_texture.extensions.khr_texture_transform.offset",
    "lit_color": "pbr_metallic_roughness.base_color_factor",
    "shade_color": "extensions.vrmc_materials_mtoon.shade_color_factor",
    "emission_color": "emissive_factor",
    "matcap_color": "extensions.vrmc_materials_mtoon.matcap_factor",
    "rim_color": "extensions.vrmc_materials_mtoon.parametric_rim_color_factor",
    "outline_color": "extensions.vrmc_materials_mtoon.outline_color_factor",
}

MTOON_DEFAULT_VALUES: MToon1MaterialParameters = {
    "texture_scale": [1.0, 1.0],
    "texture_offset": [0.0, 0.0],
    "lit_color": [1.0, 1.0, 1.0, 1.0],
    "shade_color": [1.0, 1.0, 1.0],
    "emission_color": [0.0, 0.0, 0.0],
    "matcap_color": [1.0, 1.0, 1.0],
    "rim_color": [0.0, 0.0, 0.0],
    "outline_color": [0.0, 0.0, 0.0],
}
