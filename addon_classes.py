import bpy
from typing import (
    Literal,
    TypedDict,
    NamedTuple,
)


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
    UI List
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


"""---------------------------------------------------------
    VRM Addon Reference
---------------------------------------------------------"""


class ReferenceVrm1FirstPersonPropertyGroup:
    pass


class ReferenceVrm1ExpressionPropertyGroup:
    morph_target_binds: bpy.props.CollectionProperty()
    material_color_binds: bpy.props.CollectionProperty()
    texture_transform_binds: bpy.props.CollectionProperty()
    is_binary: bpy.props.BoolProperty()

    EXPRESSION_OVERRIDE_TYPE_VALUES = []

    override_blink: bpy.props.EnumProperty()
    override_look_at: bpy.props.EnumProperty()
    override_mouth: bpy.props.EnumProperty()

    show_expanded: bpy.props.BoolProperty()
    show_expanded_morph_target_binds: bpy.props.BoolProperty()
    show_expanded_material_color_binds: bpy.props.BoolProperty()
    show_expanded_texture_transform_binds: bpy.props.BoolProperty()


class ReferenceVrm1MaterialColorBindPropertyGroup:
    material: bpy.props.PointerProperty()
    type: Literal[
        "color",
        "shadeColor",
        "emissionColor",
        "matcapColor",
        "rimColor",
        "outlineColor",
    ]
    target_value: bpy.props.FloatVectorProperty()


class ReferenceVrm1TextureTransformBindPropertyGroup:
    material: bpy.props.PointerProperty()
    scale: bpy.props.FloatVectorProperty()
    offset: bpy.props.FloatVectorProperty()


class ReferenceVrm1ColliderPropertyGroup:
    node: bpy.props.PointerProperty()
    shape: bpy.props.PointerProperty()

    show_expanded: bpy.props.BoolProperty()

    shape_type: Literal["Sphere", "Capsule"]

    bpy_object: bpy.props.PointerProperty()

    uuid: bpy.props.StringProperty
    search_one_time_uuid: bpy.props.StringProperty()


class ReferenceVrm1ColliderGroupPropertyGroup:
    pass


class ReferenceVrm1SpringPropertyGroup:
    pass
