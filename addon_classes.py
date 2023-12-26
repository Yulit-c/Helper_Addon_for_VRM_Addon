import bpy
from typing import (
    Literal,
    TypedDict,
    NamedTuple,
)


"""---------------------------------------------------------
------------------------------------------------------------
    VRM Addon Reference
------------------------------------------------------------
---------------------------------------------------------"""


class ReferenceStringPropertyGroup:
    value: bpy.types.StringProperty


class ReferenceMeshObjectPropertyGroup:
    mesh_object_name: bpy.types.StringProperty
    value: bpy.types.StringProperty
    bpy_object: bpy.types.Object


class ReferenceBonePropertyGroup:
    bone_name: bpy.types.StringProperty
    value: bpy.types.StringProperty
    bone_uuid: bpy.types.StringProperty
    armature_data_name: bpy.types.StringProperty
    search_one_time_uuid: bpy.types.StringProperty


"""---------------------------------------------------------
    VRM0
---------------------------------------------------------"""


# ----------------------------------------------------------
#    Meta
# ----------------------------------------------------------
class ReferenceVrm0MetaPropertyGroup:
    pass


# ----------------------------------------------------------
#    Humanoid
# ----------------------------------------------------------
class ReferenceVrm0HumanoidPropertyGroup:
    pass


# ----------------------------------------------------------
#    First Person
# ----------------------------------------------------------
class RererenceVrm0DegreeMapPropertyGroup:
    curve: list[bpy.types.FloatProperty]
    x_range: bpy.types.FloatProperty
    y_range: bpy.types.FloatProperty


class ReferenceVrm0MeshAnnotationPropertyGroup:
    mesh: ReferenceMeshObjectPropertyGroup
    first_person_flag: Literal["Auto", "FirstPersonOnly", "ThirdPersonOnly", "Both"]


class ReferenceVrm0FirstPersonPropertyGroup:
    first_person_bone: ReferenceBonePropertyGroup

    first_person_bone_offset: list[bpy.types.FloatProperty]
    mesh_annotations: bpy.types.CollectionProperty  # Vrm0MeshAnnotationPropertyGroup
    look_at_type_name_items = [
        ("Bone", "Bone", "Use bones to eye movement", "BONE_DATA", 0),
        (
            "BlendShape",
            "Blend Shape",
            "Use blend Shapes of VRM Blend Shape Proxy to eye movement.",
            "SHAPEKEY_DATA",
            1,
        ),
    ]
    LOOK_AT_TYPE_NAME_VALUES = [
        look_at_type_name_item[0] for look_at_type_name_item in look_at_type_name_items
    ]
    look_at_type_name: Literal["Bone", "BlendShape"]

    look_at_horizontal_inner: RererenceVrm0DegreeMapPropertyGroup
    look_at_horizontal_outer: RererenceVrm0DegreeMapPropertyGroup
    look_at_vertical_down: RererenceVrm0DegreeMapPropertyGroup
    look_at_vertical_up: RererenceVrm0DegreeMapPropertyGroup


# ----------------------------------------------------------
#    Blend Shape
# ----------------------------------------------------------
class ReferenceVrm0BlendShapeMasterPropertyGroup:
    blend_shape_groups: bpy.types.CollectionProperty  # Vrm0BlendShapeGroupPropertyGroup
    active_blend_shape_group_index: bpy.types.IntProperty


class ReferenceVrm0BlendShapeGroupPropertyGroup:
    preset_name_items = Literal[
        "unknown",
        "neutral",
        "a",
        "i",
        "u",
        "e",
        "o",
        "blink",
        "joy",
        "angry",
        "sorrow",
        "fun",
        "lookup",
        "lookdown",
        "lookleft",
        "lookright",
        "blink_l",
        "blink_r",
    ]
    preset_name: preset_name_items
    binds: bpy.types.CollectionProperty  # Vrm0BlendShapeBindPropertyGroup
    material_values: bpy.types.CollectionProperty  # Vrm0MaterialValueBindPropertyGroup
    is_binary: bpy.types.BoolProperty
    active_bind_index: bpy.types.IntProperty
    active_material_value_index: bpy.types.IntProperty
    preview: bpy.types.FloatProperty


class ReferenceVrm0BlendShapeBindPropertyGroup:
    mesh: ReferenceMeshObjectPropertyGroup
    index: bpy.types.StringProperty
    weight: bpy.types.FloatProperty


class ReferenceVrm0MaterialValueBindPropertyGroup:
    material: bpy.types.Material
    property_name = bpy.types.StringProperty
    target_value: bpy.types.CollectionProperty  # FloatPropertyGroup


# ----------------------------------------------------------
#    Secondary Animation
# ----------------------------------------------------------
class ReferencerVrm0SecondaryAnimationColliderPropertyGroup:
    bpy_object: bpy.types.Object


class ReferenceVrm0SecondaryAnimationGroupPropertyGroup:
    comment: bpy.types.StringProperty
    stiffness: bpy.types.FloatProperty
    gravity_power: bpy.types.FloatProperty
    gravity_dir: list[bpy.types.FloatProperty]
    drag_force: bpy.types.FloatProperty
    center: ReferenceBonePropertyGroup
    hit_radius: bpy.types.FloatProperty
    bones: bpy.types.CollectionProperty  # BonePropertyGroup
    collider_groups: bpy.types.CollectionProperty  # StringPropertyGroup

    # for UI
    show_expanded: bpy.types.BoolProperty
    show_expanded_bones: bpy.types.BoolProperty
    show_expanded_collider_groups: bpy.types.BoolProperty


class ReferenceVrm0SecondaryAnimationColliderGroupPropertyGroup:
    node: ReferenceBonePropertyGroup

    # offsetとradiusはコライダー自身のデータを用いる
    colliders: bpy.types.CollectionProperty  # Vrm0SecondaryAnimationColliderPropertyGroup

    # for UI
    show_expanded: bpy.types.BoolProperty

    # for reference from Vrm0SecondaryAnimationGroupPropertyGroup
    name: bpy.types.StringProperty
    uuid: bpy.types.StringProperty


class ReferenceVrm0SecondaryAnimationPropertyGroup:
    bone_groups: bpy.types.CollectionProperty  # Vrm0SecondaryAnimationGroupPropertyGroup
    collider_groups: bpy.types.CollectionProperty  # Vrm0SecondaryAnimationColliderGroupPropertyGroup

    # for UI
    active_bone_group_index: bpy.types.IntProperty
    active_collider_group_index: bpy.types.IntProperty


# ----------------------------------------------------------
#    Root
# ----------------------------------------------------------
class ReferenceVrm0PropertyGroup:
    meta: ReferenceVrm0MetaPropertyGroup
    humanoid: ReferenceVrm0HumanoidPropertyGroup
    first_person: ReferenceVrm0FirstPersonPropertyGroup
    blend_shape_master: ReferenceVrm0BlendShapeMasterPropertyGroup
    secondary_animation: ReferenceVrm0SecondaryAnimationPropertyGroup


"""---------------------------------------------------------
    VRM1
---------------------------------------------------------"""


# ----------------------------------------------------------
#    Meta
# ----------------------------------------------------------
class ReferenceVrm1MetaPropertyGroup:
    pass


# ----------------------------------------------------------
#    Humanoid
# ----------------------------------------------------------
class ReferenceVrm1HumanoidPropertyGroup:
    pass


# ----------------------------------------------------------
#    First Person
# ----------------------------------------------------------
class ReferenceVrm1MeshAnnotationPropertyGroup:
    node: ReferenceMeshObjectPropertyGroup
    TYPE_ITEMS = Literal["auto", "both", "thirdPersonOnly", "firstPersonOnly"]
    type: TYPE_ITEMS


class ReferenceVrm1FirstPersonPropertyGroup:
    mesh_annotations: bpy.types.CollectionProperty  # Vrm1MeshAnnotationPropertyGroup


# ----------------------------------------------------------
#    Lool At
# ----------------------------------------------------------
class ReferenceVrm1LookAtPropertyGroup:
    pass


# ----------------------------------------------------------
#    Expression
# ----------------------------------------------------------


class ReferenceVrm1MorphTargetBindPropertyGroup:
    node: ReferenceMeshObjectPropertyGroup
    index: bpy.types.StringProperty
    weight: bpy.types.FloatProperty


class ReferenceVrm1MaterialColorBindPropertyGroup:
    material: bpy.types.Material
    type: Literal[
        "color",
        "shadeColor",
        "emissionColor",
        "matcapColor",
        "rimColor",
        "outlineColor",
    ]
    target_value: list[bpy.types.FloatProperty]
    target_value_as_rgb: list[bpy.types.FloatProperty]


class ReferenceVrm1TextureTransformBindPropertyGroup:
    material: bpy.types.Material
    scale: list[bpy.types.FloatProperty]
    offset: list[bpy.types.FloatProperty]


class ReferenceVrm1ExpressionPropertyGroup:
    morph_target_binds: bpy.types.CollectionProperty  # Vrm1MorphTargetBindPropertyGroup
    material_color_binds: bpy.types.CollectionProperty  # Vrm1MaterialColorBindPropertyGroup
    texture_transform_binds: bpy.types.CollectionProperty  # Vrm1TextureTransformBindPropertyGroup
    is_binary: bpy.types.BoolProperty

    EXPRESSION_OVERRIDE_TYPE_VALUES = Literal["none", "block", "blend"]

    override_blink: EXPRESSION_OVERRIDE_TYPE_VALUES
    override_look_at: EXPRESSION_OVERRIDE_TYPE_VALUES
    override_mouth: EXPRESSION_OVERRIDE_TYPE_VALUES

    show_expanded: bpy.types.BoolProperty
    show_expanded_morph_target_binds: bpy.types.BoolProperty
    show_expanded_material_color_binds: bpy.types.BoolProperty
    show_expanded_texture_transform_binds: bpy.types.BoolProperty

    frame_change_post_shape_key_updates: dict[tuple[str, str], float] = {}
    preview: bpy.types.PropertyGroup


class ReferenceVrm1ExpressionsPresetPropertyGroup:
    happy: ReferenceVrm1ExpressionPropertyGroup
    angry: ReferenceVrm1ExpressionPropertyGroup
    sad: ReferenceVrm1ExpressionPropertyGroup
    relaxed: ReferenceVrm1ExpressionPropertyGroup
    surprised: ReferenceVrm1ExpressionPropertyGroup
    neutral: ReferenceVrm1ExpressionPropertyGroup
    aa: ReferenceVrm1ExpressionPropertyGroup
    ih: ReferenceVrm1ExpressionPropertyGroup
    ou: ReferenceVrm1ExpressionPropertyGroup
    ee: ReferenceVrm1ExpressionPropertyGroup
    oh: ReferenceVrm1ExpressionPropertyGroup
    blink: ReferenceVrm1ExpressionPropertyGroup
    blink_left: ReferenceVrm1ExpressionPropertyGroup
    blink_right: ReferenceVrm1ExpressionPropertyGroup
    look_up: ReferenceVrm1ExpressionPropertyGroup
    look_down: ReferenceVrm1ExpressionPropertyGroup
    look_left: ReferenceVrm1ExpressionPropertyGroup
    look_right: ReferenceVrm1ExpressionPropertyGroup


class ReferenceVrm1CustomExpressionPropertyGroup(ReferenceVrm1ExpressionPropertyGroup):
    custom_name: bpy.types.StringProperty


class ReferenceVrm1ExpressionsPropertyGroup:
    preset: ReferenceVrm1ExpressionsPresetPropertyGroup
    custom: bpy.types.CollectionProperty  # Vrm1CustomExpressionPropertyGroup

    expression_ui_list_elements: bpy.types.CollectionProperty  # StringPropertyGroup
    active_expression_ui_list_element_index: bpy.types.IntProperty


# ----------------------------------------------------------
#    Root
# ----------------------------------------------------------
class ReferenceVrm1PropertyGroup:
    meta: ReferenceVrm1MetaPropertyGroup
    humanoid: ReferenceVrm1HumanoidPropertyGroup
    first_person: ReferenceVrm1FirstPersonPropertyGroup
    look_at: ReferenceVrm1LookAtPropertyGroup
    expressions: ReferenceVrm1ExpressionPropertyGroup


"""---------------------------------------------------------
    Spring Bone
---------------------------------------------------------"""


# ----------------------------------------------------------
#    Collider
# ----------------------------------------------------------
class ReferenceSpringBone1ColliderShapeSpherePropertyGroup:
    offset: list[bpy.types.FloatProperty]
    radius: bpy.types.FloatProperty


class ReferenceSpringBone1ColliderShapeCapsulePropertyGroup:
    offset: list[bpy.types.FloatProperty]
    radius: bpy.types.FloatProperty
    tail: list[bpy.types.FloatProperty]


class ReferenceSpringBone1ColliderPropertyGroup:
    sphere: ReferenceSpringBone1ColliderShapeSpherePropertyGroup
    capsule: ReferenceSpringBone1ColliderShapeCapsulePropertyGroup


class ReferenceVrm1ColliderPropertyGroup:
    node: ReferenceBonePropertyGroup
    shape: ReferenceSpringBone1ColliderPropertyGroup

    show_expanded: bpy.types.BoolProperty
    shape_type: Literal["Sphere", "Capsule"]
    bpy_object: bpy.types.Object
    uuid: bpy.types.StringProperty
    search_one_time_uuid: bpy.types.StringProperty


# ----------------------------------------------------------
#    Collider Group
# ----------------------------------------------------------
class ReferenceVrm1ColliderGroupPropertyGroup:
    vrm_name: bpy.types.StringProperty
    colliders: bpy.types.CollectionProperty  # ReferenceSpringBone1ColliderReferencePropertyGroup
    show_expanded: bpy.types.BoolProperty
    uuid: bpy.types.StringProperty
    search_one_time_uuid: bpy.types.StringProperty


class ReferenceSpringBone1ColliderReferencePropertyGroup:
    collider_name: bpy.types.StringProperty
    collider_uuid: bpy.types.StringProperty
    search_one_time_uuid: bpy.types.StringProperty


# ----------------------------------------------------------
#    Spring
# ----------------------------------------------------------
class ReferenceSpringBone1SpringAnimationStatePropertyGroup:
    use_center_space: bpy.types.BoolProperty
    previous_center_world_translation: list[bpy.types.FloatProperty]


class ReferenceSpringBone1JointPropertyGroup:
    node: ReferenceBonePropertyGroup
    hit_radius: bpy.types.FloatProperty
    stiffness: bpy.types.FloatProperty
    gravity_power: bpy.types.FloatProperty
    gravity_dir: list[bpy.types.FloatProperty]
    drag_force: bpy.types.FloatProperty
    animation_state: ReferenceSpringBone1SpringAnimationStatePropertyGroup
    show_expanded: bpy.types.BoolProperty


class ReferenceSpringBone1ColliderGroupPropertyGroup:
    collider_group_name: bpy.types.StringProperty
    collider_group_uuid: bpy.types.StringProperty
    search_one_time_uuid: bpy.types.StringProperty


class ReferenceSpringBone1SpringPropertyGroup:
    vrm_name: bpy.types.StringProperty
    joints: bpy.types.CollectionProperty  # SpringBone1JointPropertyGroup
    collider_groups: bpy.types.CollectionProperty  # SpringBone1ColliderGroupPropertyGroup
    center: ReferenceBonePropertyGroup

    show_expanded: bpy.types.BoolProperty
    show_expanded_bones: bpy.types.BoolProperty
    show_expanded_collider_groups: bpy.types.BoolProperty
    animation_state: ReferenceSpringBone1SpringAnimationStatePropertyGroup


# ----------------------------------------------------------
#    Root
# ----------------------------------------------------------
class ReferenceSpringBone1SpringBonePropertyGroup:
    colliders: bpy.types.CollectionProperty  # Vrm1ColliderPropertyGroup
    collider_groups: bpy.types.CollectionProperty  # SpringBone1ColliderGroupPropertyGroup
    springs: bpy.types.CollectionProperty  # SpringBone1SpringPropertyGroup

    enable_animation: bpy.types.BoolProperty

    # for UI
    show_expanded_colliders: bpy.types.BoolProperty
    show_expanded_collider_groups: bpy.types.BoolProperty
    show_expanded_springs: bpy.types.BoolProperty


"""---------------------------------------------------------
    Node Constraint
---------------------------------------------------------"""


class ReferenceNodeConstraint1NodeConstraintPropertyGroup:
    # for UI
    show_expanded_roll_constraints: bpy.types.BoolProperty
    show_expanded_aim_constraints: bpy.types.BoolProperty
    show_expanded_rotation_constraints: bpy.types.BoolProperty


"""---------------------------------------------------------
    Root Overall
---------------------------------------------------------"""


class ReferenceVrmAddonArmatureExtensionPropertyGroup:
    addon_version: list[
        bpy.types.IntProperty,
        bpy.types.IntProperty,
        bpy.types.IntProperty,
    ]
    vrm0: ReferenceVrm0PropertyGroup
    vrm1: ReferenceVrm1PropertyGroup
    spring_bone1: ReferenceSpringBone1SpringBonePropertyGroup
    node_constraint1: ReferenceNodeConstraint1NodeConstraintPropertyGroup
    armature_data_name: bpy.types.StringProperty

    SPEC_VERSION_ITEMS = Literal["0.0", "1.0"]
    spec_version: SPEC_VERSION_ITEMS


# ----------------------------------------------------------
# ----------------------------------------------------------
# ----------------------------------------------------------
# ----------------------------------------------------------
# ----------------------------------------------------------
"""---------------------------------------------------------
------------------------------------------------------------
    For This Addon
------------------------------------------------------------
---------------------------------------------------------"""


class VRMHelper_Addon_Collection_Dict(TypedDict):
    ROOT: bpy.types.Collection
    VRM0_Root: bpy.types.Collection
    VRM0_COLLIDER: bpy.types.Collection
    VRM0_BLEND_SHAPE_MORPH: bpy.types.Collection
    VRM0_BLEND_SHAPE_MATERIAL: bpy.types.Collection
    VRM1_Root: bpy.types.Collection
    VRM1_COLLIDER: bpy.types.Collection
    VRM1_EXPRESSION_MORPH: bpy.types.Collection
    VRM1_EXPRESSION_MATERIAL: bpy.types.Collection


"""---------------------------------------------------------
    UI
---------------------------------------------------------"""


class VRMHELPER_UL_base:
    """
    UI List用基底クラス
    """

    def add_blank_labels(self, layout: bpy.types.UILayout, count: int, factor: float = 2.0):
        iteration_count = 0
        while iteration_count != count:
            layout.separator(factor=factor)
            iteration_count += 1


"""---------------------------------------------------------
    Operator
---------------------------------------------------------"""


class VRMHELPER_VRM_joint_operator_property:
    """
    ジョイント用オペレータープロパティーをフィールドとする基底クラス｡
    """

    hit_radius: bpy.props.FloatProperty(
        name="Hit Radius",
        description="radius value of joint set by operator",
        default=0.01,
        min=0.0,
        soft_max=0.5,
        options={"HIDDEN"},
    )

    stiffness: bpy.props.FloatProperty(
        name="stiffness",
        description="stiffness value of joint set by operator",
        default=1.0,
        min=0.0,
        soft_max=4.0,
        options={"HIDDEN"},
    )

    drag_force: bpy.props.FloatProperty(
        name="Drag Force",
        description="drag force value of joint set by operator",
        default=0.5,
        min=0.0,
        max=1.0,
        options={"HIDDEN"},
    )

    gravity_power: bpy.props.FloatProperty(
        name="Gravity Power",
        description="gravity power value  of joint set by operator",
        default=0.0,
        min=0.0,
        soft_max=2.0,
        options={"HIDDEN"},
    )

    gravity_dir: bpy.props.FloatVectorProperty(
        name="Gravity Direction",
        description="gravity direction value of joint set by operator",
        default=(0.0, 0.0, -1.0),
        size=3,
        subtype="XYZ",
        options={"HIDDEN"},
    )

    damping_ratio: bpy.props.FloatProperty(
        name="Damping Ratio",
        description="Descriptiondamping rate of the parameters of the joints to be created",
        default=1.0,
        min=0.01,
    )


"""---------------------------------------------------------
    MToon
---------------------------------------------------------"""


class MToon0ParameterNames(TypedDict):
    texture_scale: str
    texture_offset: str
    color: str
    shade_color: str
    emission_color: str
    rim_color: str
    outline_color: str


class MToon1ParameterNames(TypedDict):
    texture_scale: str
    texture_offset: str
    lit_color: str
    shade_color: str
    emission_color: str
    matcap_color: str
    rim_color: str
    outline_color: str


class MToonMaterialParameters(TypedDict, total=False):
    texture_scale: list[float]
    texture_offset: list[float]
    color: list[float]
    lit_color: list[float]
    shade_color: list[float]
    emission_color: list[float]
    matcap_color: list[float]
    rim_color: list[float]
    outline_color: list[float]


"""---------------------------------------------------------
    Blend Shape
---------------------------------------------------------"""


class BlendShapeModeDict(TypedDict):
    BIND: str
    MATERIAL: str


"""---------------------------------------------------------
    Expression
---------------------------------------------------------"""


class ExpressionCandidateUIList(TypedDict, total=False):
    name: str
    preset_expression: ReferenceVrm1ExpressionPropertyGroup
    custom_expression: ReferenceVrm1CustomExpressionPropertyGroup
    has_morph_bind: bool
    has_material_bind: bool


"""---------------------------------------------------------
    Constraint
---------------------------------------------------------"""


class VrmRollConstraint:
    pass


class VrmAimConstraint:
    pass


class VrmRotationConstraint:
    pass


class CandidateConstraitProperties(NamedTuple):
    type: VrmAimConstraint | VrmAimConstraint | VrmRotationConstraint  # VRMコンストレイントの種類
    element: bpy.types.Object | bpy.types.Bone  # コンストレイントがアタッチされたデータ
    index: int  # elementが持つコンストレイントスタックにおける対象コンストレイントのインデックス
    is_circular_dependency: bool  # 循環依存関係が生じていることを示すフラグ
    constraint: bpy.types.CopyRotationConstraint | bpy.types.DampedTrackConstraint  # 'element'にアタッチされたコンストレイント


class ConstraintTypeDict(TypedDict):
    ROLL: str
    AIM: str
    ROTATION: str
