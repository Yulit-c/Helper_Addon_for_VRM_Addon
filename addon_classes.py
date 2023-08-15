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


class ReferenceVRM1MeshObjectPropertyGroup:
    mesh_object_name: bpy.types.StringProperty
    value: bpy.types.StringProperty
    bpy_object: bpy.types.Object


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
class ReferenceVrm0FirstPersonPropertyGroup:
    pass


# ----------------------------------------------------------
#    Blend Shape
# ----------------------------------------------------------
class ReferenceVrm0BlendShapeMasterPropertyGroup:
    pass


# ----------------------------------------------------------
#    Secondary Animation
# ----------------------------------------------------------
class ReferenceVrm0SecondaryAnimationPropertyGroup:
    pass


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
    node: ReferenceVRM1MeshObjectPropertyGroup
    TYPE_ITEMS = Literal["auto", "both", "thirdPersonOnly", "firstPersonOnly"]
    type: TYPE_ITEMS


class ReferenceVrm1FirstPersonPropertyGroup:
    mesh_annotations: bpy.types.CollectionProperty  # ReferenceVrm1MeshAnnotationPropertyGroup


# ----------------------------------------------------------
#    Lool At
# ----------------------------------------------------------
class ReferenceVrm1LookAtPropertyGroup:
    pass


# ----------------------------------------------------------
#    Expression
# ----------------------------------------------------------


class ReferenceVrm1MorphTargetBindPropertyGroup:
    node: ReferenceVRM1MeshObjectPropertyGroup
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


class ReferenceVrm1TextureTransformBindPropertyGroup:
    material: bpy.types.Material
    scale: list[bpy.types.FloatProperty]
    offset: list[bpy.types.FloatProperty]


class ReferenceVrm1ExpressionPropertyGroup:
    morph_target_binds: bpy.types.CollectionProperty  # ReferenceVrm1MorphTargetBindPropertyGroup
    material_color_binds: bpy.types.CollectionProperty  # ReferenceVrm1MaterialColorBindPropertyGroup
    texture_transform_binds: bpy.types.CollectionProperty  # ReferenceVrm1TextureTransformBindPropertyGroup
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
    custom: bpy.types.CollectionProperty  # ReferenceVrm1CustomExpressionPropertyGroup

    expression_ui_list_elements: bpy.types.CollectionProperty  # ReferenceStringPropertyGroup
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


class ReferenceBonePropertyGroup:
    bone_name: bpy.types.StringProperty
    value: bpy.types.StringProperty
    bone_uuid: bpy.types.StringProperty
    armature_data_name: bpy.types.StringProperty
    search_one_time_uuid: bpy.types.StringProperty


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
    colliders: bpy.types.CollectionProperty  # ReferenceVrm1ColliderPropertyGroup
    show_expanded: bpy.types.BoolProperty
    uuid: bpy.types.StringProperty
    search_one_time_uuid: bpy.types.StringProperty


# ----------------------------------------------------------
#    Spring
# ----------------------------------------------------------
class ReferenceSpringBone1JointPropertyGroup:
    node: ReferenceBonePropertyGroup
    hit_radius: bpy.types.FloatProperty
    stiffness: bpy.types.FloatProperty
    gravity_power: bpy.types.FloatProperty


class ReferenceSpringBone1ColliderGroupPropertyGroup:
    collider_group_name: bpy.types.StringProperty
    collider_group_uuid: bpy.types.StringProperty
    search_one_time_uuid: bpy.types.StringProperty


class ReferenceSpringBone1SpringAnimationStatePropertyGroup:
    use_center_space: bpy.types.BoolProperty
    previous_center_world_translation: list[bpy.types.FloatProperty]


class ReferenceSpringBone1SpringPropertyGroup:
    vrm_name: bpy.types.StringProperty
    joints: bpy.types.CollectionProperty  # ReferenceSpringBone1JointPropertyGroup
    collider_groups: bpy.types.CollectionProperty  # ReferenceSpringBone1ColliderGroupPropertyGroup
    center: ReferenceBonePropertyGroup

    show_expanded: bpy.types.BoolProperty
    show_expanded_bones: bpy.types.BoolProperty
    show_expanded_collider_groups: bpy.types.BoolProperty
    animation_state: ReferenceSpringBone1SpringAnimationStatePropertyGroup


# ----------------------------------------------------------
#    Root
# ----------------------------------------------------------
class ReferenceSpringBone1SpringBonePropertyGroup:
    colliders: bpy.types.CollectionProperty  # ReferenceSpringBone1ColliderPropertyGroup
    collider_groups: bpy.types.CollectionProperty  # ReferenceSpringBone1ColliderGroupPropertyGroup
    springs: bpy.types.CollectionProperty  # ReferenceSpringBone1SpringPropertyGroup

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

    def add_blank_labels(
        self, layout: bpy.types.UILayout, count: int, factor: float = 2.0
    ):
        iteration_count = 0
        while iteration_count != count:
            layout.separator(factor=factor)
            iteration_count += 1


"""---------------------------------------------------------
    Operator
---------------------------------------------------------"""
class VRMHELPER_VRM1_joint_property:
    """
    ジョイント用オペレータープロパティーをフィールドとする基底クラス｡
    """

    hit_radius: bpy.types.FloatProperty(
        name="Hit Radius",
        description="radius value of joint set by operator",
        default=0.01,
        min=0.0,
        soft_max=0.5,
        options={"HIDDEN"},
    )

    stiffness: bpy.types.FloatProperty(
        name="Stiffness",
        description="stiffness value of joint set by operator",
        default=1.0,
        min=0.0,
        soft_max=4.0,
        options={"HIDDEN"},
    )

    drag_force: bpy.types.FloatProperty(
        name="Drag Force",
        description="drag force value of joint set by operator",
        default=0.5,
        min=0.0,
        max=1.0,
        options={"HIDDEN"},
    )

    gravity_power: bpy.types.FloatProperty(
        name="Gravity Power",
        description="gravity power value  of joint set by operator",
        default=0.0,
        min=0.0,
        soft_max=2.0,
        options={"HIDDEN"},
    )

    gravity_dir: bpy.types.FloatVectorProperty(
        name="Gravity Direction",
        description="gravity direction value of joint set by operator",
        default=(0.0, 0.0, -1.0),
        size=3,
        subtype="XYZ",
        options={"HIDDEN"},
    )

    damping_ratio: bpy.types.FloatProperty(
        name="Damping Ratio",
        description="Descriptiondamping rate of the parameters of the joints to be created",
        default=1.0,
        min=0.01,
    )



"""---------------------------------------------------------
    MToon
---------------------------------------------------------"""


class MToon1ParameterNames(TypedDict):
    texture_scale: str
    texture_offset: str
    lit_color: str
    shade_color: str
    emission_color: str
    matcap_color: str
    rim_color: str
    outline_color: str


class MToon1MaterialParameters(TypedDict, total=False):
    texture_scale: list[float]
    texture_offset: list[float]
    lit_color: list[float]
    shade_color: list[float]
    emission_color: list[float]
    matcap_color: list[float]
    rim_color: list[float]
    outline_color: list[float]


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
