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
    First Person
---------------------------------------------------------"""
FIRST_PERSON_ANNOTATION_TYPES = {
    "auto",
    "both",
    "thirdPersonOnly",
    "firstPersonOnly",
}


"""---------------------------------------------------------
    Expression
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

EXPRESSION_ICON_DICT = {
    "happy": "HEART",
    "angry": "ORPHAN_DATA",
    "sad": "MOD_FLUIDSIM",
    "relaxed": "LIGHT_SUN",
    "surprised": "LIGHT_SUN",
    "neutral": "VIEW_ORTHO",
    "aa": "EVENT_A",
    "ih": "EVENT_I",
    "ou": "EVENT_U",
    "ee": "EVENT_E",
    "oh": "EVENT_O",
    "blink": "HIDE_ON",
    "blink_left": "HIDE_ON",
    "blink_right": "HIDE_ON",
    "look_up": "ANCHOR_TOP",
    "look_down": "ANCHOR_BOTTOM",
    "look_left": "ANCHOR_RIGHT",
    "look_right": "ANCHOR_LEFT",
    "custom": "SHAPEKEY_DATA",
}

EXPRESSION_OPTION_ICON = {
    "none": "REMOVE",
    "block": "FAKE_USER_ON",
    "blend": "GP_MULTIFRAME_EDITING",
}

MOVE_UP_CUSTOM_EXPRESSION_OPS_NAME = "vrm.move_up_vrm1_expressions_custom_expression"
MOVE_DOWN_CUSTOM_EXPRESSION_OPS_NAME = (
    "vrm.move_down_vrm1_expressions_custom_expression"
)

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
