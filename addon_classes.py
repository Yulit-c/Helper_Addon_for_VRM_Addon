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

"""---------------------------------------------------------
    First Person
---------------------------------------------------------"""


class ReferenceVrm1FirstPersonPropertyGroup:
    pass


"""---------------------------------------------------------
    Expression
---------------------------------------------------------"""


class ReferenceVrm1ExpressionPropertyGroup:
    morph_target_binds: bpy.props.CollectionProperty()
    material_color_binds: bpy.props.CollectionProperty()
    texture_transform_binds: bpy.props.CollectionProperty()
    is_binary: bpy.types.BoolProperty

    EXPRESSION_OVERRIDE_TYPE_VALUES = []

    override_blink: bpy.types.EnumProperty
    override_look_at: bpy.types.EnumProperty
    override_mouth: bpy.types.EnumProperty

    show_expanded: bpy.types.BoolProperty
    show_expanded_morph_target_binds: bpy.types.BoolProperty
    show_expanded_material_color_binds: bpy.types.BoolProperty
    show_expanded_texture_transform_binds: bpy.types.BoolProperty


class ReferenceVrm1CustomExpressionPropertyGroup:
    custom_name: bpy.types.StringProperty
    expression: bpy.props.PointerProperty()


class ReferenceVrm1MorphTargetBindPropertyGroup:
    node: bpy.props.PointerProperty()
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


class ReferenceSpringBone1ColliderShapePropertyGroup:
    sphere: ReferenceSpringBone1ColliderShapeSpherePropertyGroup
    capsule: ReferenceSpringBone1ColliderShapeCapsulePropertyGroup


class ReferenceVrm1ColliderPropertyGroup:
    node: ReferenceBonePropertyGroup
    shape: ReferenceSpringBone1ColliderShapePropertyGroup

    show_expanded: bpy.types.BoolProperty
    shape_type: Literal["Sphere", "Capsule"]
    bpy_object: bpy.types.Object
    uuid: bpy.types.StringProperty
    search_one_time_uuid: bpy.types.StringProperty


# ----------------------------------------------------------
#    Collider Group
# ----------------------------------------------------------
class ReferenceVrm1ColliderGroupPropertyGroup:
    pass


# ----------------------------------------------------------
#    Spring
# ----------------------------------------------------------
class ReferenceVrm1SpringPropertyGroup:
    pass


"""---------------------------------------------------------
------------------------------------------------------------
    Common
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
