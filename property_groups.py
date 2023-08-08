if "bpy" in locals():
    import importlib

    reloadable_modules = [
        "preparation_logger",
        "preferences",
    ]

    for module in reloadable_modules:
        if module in locals():
            importlib.reload(locals()[module])

else:
    from .Logging import preparation_logger
    from . import preferences

from typing import (
    Literal,
    Optional,
    Any,
)
from pathlib import Path

import bpy

from bpy.types import (
    Context,
    PropertyGroup,
    Object,
    Material,
    Armature,
    Bone,
    PoseBone,
    Constraint,
)

from idprop.types import (
    IDPropertyGroup,
)

from bpy.props import (
    BoolProperty,
    StringProperty,
    EnumProperty,
    IntProperty,
    IntVectorProperty,
    FloatProperty,
    FloatVectorProperty,
    BoolVectorProperty,
    PointerProperty,
    CollectionProperty,
)


from .addon_constants import (
    VRM_COMPONENT_TYPES,
)

from .utils_common import (
    setting_vrm_helper_collection,
)


"""---------------------------------------------------------
------------------------------------------------------------
    Logger
------------------------------------------------------------
---------------------------------------------------------"""
from .Logging.preparation_logger import preparating_logger

logger = preparating_logger(__name__)
#######################################################


"""---------------------------------------------------------
------------------------------------------------------------
    Property Group
------------------------------------------------------------
---------------------------------------------------------"""

"""----------------------------------------------------------------------------
#    Scene
-----------------------------------------------------------------------------"""


# ----------------------------------------------------------
#    Basic Settings
# ----------------------------------------------------------
class VRMHELPER_SCENE_basic_settigs(PropertyGroup):
    """
    アドオンの基本設定を行なうプロパティ
    """

    def filtering_armature_type(self, source_object: Object) -> bool:
        """
        引数で受け取ったオブジェクトのタイプがArmatureか否かを判定する｡
        """

        if source_object.type == "ARMATURE":
            return True
        else:
            return False

    def update_addon_collection(self, context):
        setting_vrm_helper_collection()

    def update_vrm_extension_version(self, context):
        if self.tool_mode == "2":
            return None

        vrm_extension = get_target_armature_data().vrm_addon_extension
        vrm_extension.spec_version = f"{self.tool_mode}.0"

    # -----------------------------------------------------

    target_armature: PointerProperty(
        name="Target Armature",
        description="Armature to be VRM set up",
        type=Object,
        poll=filtering_armature_type,
        update=update_addon_collection,
    )

    tool_mode: EnumProperty(
        name="Tool Mode",
        description="Property for selecting the UI item to draw",
        items=(
            ("0", "0.x", "Setup VRM for version 0.x"),
            ("1", "1.x", "Setup VRM for version 1.x"),
            ("2", "Misc", "Use other utility tools."),
        ),
        default="1",
        update=update_vrm_extension_version,
    )

    sort_order_component_type = (
        "FIRST_PERSON",
        "EXPRESSION",
        "COLLIDER",
        "COLLIDER_GROUP",
        "SPRING",
        "CONSTRAINT",
    )  # UI描画時に一定の順にソートするためのコンテナ｡

    component_type: EnumProperty(
        name="Component Type",
        description="Property for selecting the UI item to draw",
        options={"ENUM_FLAG"},
        items=(
            ("FIRST_PERSON", "First Person", "Draw UI for setting First Person"),
            ("EXPRESSION", "EXPRESSION", "Draw UI for setting Expression"),
            ("COLLIDER", "Collider", "Draw UI for setting Collider"),
            ("COLLIDER_GROUP", "Collider Group", "Draw UI for setting Collider Group"),
            ("SPRING", "Spring", "Draw UI for setting Spring"),
            ("CONSTRAINT", "Constraint", "Draw UI for setting Constraint"),
        ),
        default=set(),
        update=update_addon_collection,
    )


# ----------------------------------------------------------
#    Misc Tools
# ----------------------------------------------------------
class VRMHELPER_SCENE_misc_tools_settigs(PropertyGroup):
    """
    Misc Toolsに関するプロパティ
    """

    padding_width: IntProperty(
        name="Padding Width",
        description="Width of 0 padding when renaming",
        default=2,
        min=0,
        max=10,
    )


"""---------------------------------------------------------
    VRM0 Property
---------------------------------------------------------"""


class VRMHELPER_SCENE_vrm0_root_property_group(PropertyGroup):
    """---------------------------------------------------------
    Scene階層下のVRM0用プロパティグループ群
    ---------------------------------------------------------"""


"""---------------------------------------------------------
    VRM1 Property
---------------------------------------------------------"""


# ----------------------------------------------------------
#    First Person
# ----------------------------------------------------------
class VRMHELPER_SCENE_vrm1_first_person_settigs(PropertyGroup):
    """
    First Personの設定に関するプロパティ
    """

    annotation_type: EnumProperty(
        name="First Person Type",
        description="Determine the First_Person annotation you wish to apply",
        items=(
            ("auto", "Auto", "Set the value to Auto"),
            ("both", "Both", "Set the value to Both"),
            (
                "thirdPersonOnly",
                "Third Person Only",
                "Set the value to Third Person Only",
            ),
            (
                "firstPersonOnly",
                "First Person Only",
                "Set the value to First Person Only",
            ),
        ),
        default="both",
    )


# ----------------------------------------------------------
#    Expression
# ----------------------------------------------------------
class VRMHELPER_SCENE_vrm1_expression_settigs(PropertyGroup):
    """
    Expressionの設定に関するプロパティ
    """

    editing_target: EnumProperty(
        name="Editing Targets",
        description="Select the bind to be edited",
        items=(
            ("MORPH", "Morph Target", "Edit Morph Target Bind"),
            ("MATERIAL", "Material", "Edit Material Binds"),
            # ("COLOR", "Color", "Edit Material Color Bind"),
            # ("TRANSFORM", "Texture Transform", "Edit Texture Transform Bind"),
        ),
        default="MORPH",
    )


# ----------------------------------------------------------
#    Collider
# ----------------------------------------------------------
class VRMHELPER_SCENE_vrm1_collider_settigs(PropertyGroup):
    """
    Colliderの設定に関するプロパティ
    """

    def update_item2vrm1_collider(self, context):
        """
        VRM1.xのSpring Bone_Colliderのリストに登録されたBone Nameが更新された際に､
        そのボーンを親とするColliderの'node.bone_name'を更新する｡
        """

        # 無限再帰の回避｡
        if self.is_updated_link_bone[0]:
            self.is_updated_link_bone[0] = False
            return

        if self.is_updated_link_bone[1]:
            self.is_updated_link_bone[1] = False
            return

        # 'node.bone_name'が'old_bone'と同名である全てのColliderの'node.bone_name'を更新する｡
        for collider in (
            c
            for c in get_target_armature_data().vrm_addon_extension.spring_bone1.colliders
            if c.node.bone_name == self.old_bone
        ):
            collider.node.bone_name = self.link_bone
            collider.reset_bpy_object(
                bpy.context,
                get_target_armature(),
            )

            # 自身のプロパティの値を更新｡
            self.old_bone = self.link_bone

    is_updated_link_bone: BoolVectorProperty(
        name="Is Updated Link Bone",
        description="Avoid infinite recursion when updating",
        size=2,
        default=(0, 0),
    )

    collider_type: EnumProperty(
        name="Collider Type",
        description="Select the type of collider to be created",
        items=(
            ("Sphere", "Sphere", "The type of collider created becomes a sphere"),
            ("Capsule", "Capsule", "The type of collider created becomes a capsule"),
        ),
        default="Capsule",
    )

    collider_radius: FloatProperty(
        name="Collider Radius",
        description="Radius of the collider to be created",
        default=0.1,
        unit="LENGTH",
    )

    old_bone: StringProperty(
        name="Old Bone",
        description="Description",
        default="",
    )

    link_bone: StringProperty(
        name="Link Bone",
        description="Description",
        default="",
        update=update_item2vrm1_collider,
    )


# ----------------------------------------------------------
#    Collider Group
# ----------------------------------------------------------
class VRMHELPER_SCENE_vrm1_collider_group_settigs(PropertyGroup):
    """
    Collider Groupの設定に関するプロパティ
    """


# ----------------------------------------------------------
#    Spring
# ----------------------------------------------------------
class VRMHELPER_SCENE_vrm1_spring_settigs(PropertyGroup):
    """
    Springの設定に関するプロパティ
    """

    hit_radius: FloatProperty(
        name="Hit Radius",
        description="radius value of joint set by operator",
        default=0.01,
        min=0.0,
        soft_max=0.5,
    )

    stiffness: FloatProperty(
        name="Stiffness",
        description="stiffness value of joint set by operator",
        default=1.0,
        min=0.0,
        soft_max=4.0,
    )

    drag_force: FloatProperty(
        name="Drag Force",
        description="drag force value of joint set by operator",
        default=0.4,
        min=0.0,
        max=1.0,
    )

    gravity_power: FloatProperty(
        name="Gravity Power",
        description="gravity power value  of joint set by operator",
        default=0.0,
        min=0.0,
        soft_max=2.0,
    )

    gravity_dir: FloatVectorProperty(
        name="Gravity Direction",
        description="gravity direction value of joint set by operator",
        default=(0.0, 0.0, -1.0),
        size=3,
        subtype="XYZ",
    )
    # -----------------------------------------------------

    damping_ratio: FloatProperty(
        name="Damping Ratio",
        description="Descriptiondamping rate of the parameters of the joints to be created",
        default=1.0,
        min=0.01,
        max=5.0,
    )

    use_auto_joint_parametter: BoolProperty(
        name="Use Auto Joint Parameter",
        description="Whether the parameters of a new joint inherit from the parent joint or not",
        default=False,
    )


# ----------------------------------------------------------
#    Constraint
# ----------------------------------------------------------
class VRMHELPER_SCENE_vrm1_constraint_settigs(PropertyGroup):
    """
    Constraintの設定に関するプロパティ
    """

    def reset_ui_list_index(self, context):
        vrm1_index_root_prop = get_vrm1_index_root_prop()
        vrm1_index_root_prop.constraint = 0

    ############################################################
    constraint_type: EnumProperty(
        name="Constraint Type",
        description="Choose the type of train and now train to be drawn on the UI",
        items=(
            ("OBJECT", "Object", "Draw Object Constraint on the UI"),
            ("BONE", "Bone", "Draw Bone Constraint on the UI"),
        ),
        default="BONE",
        update=reset_ui_list_index,
    )


# ----------------------------------------------------------
#    UI List
# ----------------------------------------------------------
class VRMHELPER_SCENE_vrm1_ui_list_active_indexes(PropertyGroup):
    """
    UI Listのアクティブアイテムインデックス用のIntPropertyを登録するプロパティグループ｡
    """

    def select_collider_object_by_ui_list(self, context: Context):
        """
        Spring Bone_ColliderのUIリストアクティブアイテムが更新された際に､
        アクティブアイテムインデックスに対応したシーン内オブジェクトを選択状態にする｡
        """

        if self.is_locked_update:
            return

        collider_list = get_ui_vrm1_collider_prop()
        active_index = get_vrm1_active_index_prop("COLLIDER")

        # アクティブアイテムがラベルである
        if (active_item := collider_list[active_index]).item_type[0]:
            return

        # アクティブアイテムがボーン名であればそのボーンに関連付けられた全てのコライダーを選択する｡
        colliders = (
            get_target_armature_data().vrm_addon_extension.spring_bone1.colliders
        )
        current_object_in_loop = None
        if active_item.item_type[1]:
            collider_prop = get_scene_vrm1_collider_prop()

            if collider_prop.link_bone != active_item.name:
                collider_prop.is_updated_link_bone[0] = True
                collider_prop.old_bone = active_item.name
                collider_prop.link_bone = active_item.name

            if context.mode != "OBJECT":
                return
            bpy.ops.object.select_all(action="DESELECT")
            [
                (
                    i.bpy_object.select_set(True),
                    (current_object_in_loop := i.bpy_object),
                )
                for i in colliders
                if i.node.bone_name == active_item.bone_name
            ]
            return

        if context.mode != "OBJECT":
            return

        # アクティブアイテムがコライダーであればそれを選択する｡
        bpy.ops.object.select_all(action="DESELECT")
        if active_item.item_type[2]:
            (collider := bpy.data.objects.get(active_item.collider_name)).select_set(
                True
            )
            current_object_in_loop = collider

        # アクティブアイテムがカプセルコライダーのエンドであればそれを選択する｡
        else:
            (collider := bpy.data.objects.get(active_item.collider_name)).select_set(
                True
            )
            current_object_in_loop = collider

        context.view_layer.objects.active = current_object_in_loop

    def select_constraint_by_ui_list(self, context: Context):
        # 現在のインデックスからアクティブアイテムを取得する｡
        constraint_ui_list = get_ui_vrm1_constraint_prop()
        active_index = get_vrm1_active_index_prop("CONSTRAINT")
        if len(constraint_ui_list) - 1 < active_index:
            return

        active_item: VRMHELPER_WM_vrm1_constraint_list_items = constraint_ui_list[
            active_index
        ]
        # アクティブアイテムがブランクまたはラベルの場合は何もしない｡
        if active_item.is_blank or active_item.is_label:
            return

        # アクティブアイテムがオブジェクトコンストレイントの場合
        if active_item.is_object_constraint:
            if not context.mode == "OBJECT":
                return

            # アクティブアイテムが参照しているコンストレイントが付与されたオブジェクトを選択する｡
            constrainted_object: Object = bpy.data.objects.get(active_item.name)
            context.view_layer.objects.active = constrainted_object
            bpy.ops.object.select_all(action="DESELECT")
            constrainted_object.select_set(True)

        # アクティブアイテムがボーンコンストレイントの場合
        else:
            if not context.mode == "POSE":
                return

            # アクティブアイテムが参照しているコンストレイントが付与されたポーズボーンを選択する｡
            target_armature = get_target_armature()
            pose_bones = target_armature.pose.bones
            constrainted_bone: PoseBone = pose_bones.get(active_item.name)
            target_armature.data.bones.active = constrainted_bone.bone
            bpy.ops.pose.select_all(action="DESELECT")
            constrainted_bone.bone.select = True

    # -----------------------------------------------------

    is_locked_update: BoolProperty(
        name="Is Locked Update",
        description="",
        default=False,
    )

    first_person: IntProperty(
        name="List Index of First Person",
        description="Index of active items in First Person UI List",
        default=0,
        min=0,
    )

    expression: IntProperty(
        name="List Index of Expression",
        description="Index of active items in Expression UI List",
        default=0,
        min=0,
    )
    expression_morph: IntProperty(
        name="List Index of Morph Target Bind",
        description="Index of active items in Expression Morph Target UI List",
        default=0,
        min=0,
    )
    expression_material: IntProperty(
        name="List Index of Material Bind",
        description="Index of active items in Expression Material Color UI List",
        default=0,
        min=0,
    )

    collider: IntProperty(
        name="List Index of Collider",
        description="Index of active items in Colliderin UI List",
        default=0,
        min=0,
        update=select_collider_object_by_ui_list,
    )

    collider_group: IntProperty(
        name="List Index of Collider Group",
        description="Index of active items in Collider Group UI List",
        default=0,
        min=0,
    )

    spring: IntProperty(
        name="List Index of Spring",
        description="Index of active items in Spring UI List",
        default=0,
        min=0,
    )

    constraint: IntProperty(
        name="List Index of Object Constraint",
        description="Index of active items in Object Constraint UI List",
        default=0,
        min=0,
        update=select_constraint_by_ui_list,
    )


class VRMHELPER_SCENE_vrm1_mtoon1_stored_parameters(PropertyGroup):
    material: PointerProperty(
        name="Material",
        description="Material to store parameters",
        type=Material,
    )

    texture_scale: FloatVectorProperty(
        name="Texture Scale",
        description="Scale of Litcolor, Alpha",
        default=(1.0, 1.0),
        size=2,
    )

    texture_offset: FloatVectorProperty(
        name="Texture Offset",
        description="Offset of Litcolor, Alpha",
        default=(0.0, 0.0),
        size=2,
    )

    lit_color: FloatVectorProperty(
        name="Lit_Color",
        description="Vector4 parameters for Lit Color",
        default=(1.0, 1.0, 1.0, 1.0),
        size=4,
    )

    shade_color: FloatVectorProperty(
        name="Shade_Color",
        description="Vector3 parameters for Shade Color",
        default=(1.0, 1.0, 1.0),
        size=3,
    )

    emission_color: FloatVectorProperty(
        name="Emission_Color",
        description="Vector3 parameters for Emission Color",
        default=(0.0, 0.0, 0.0),
        size=3,
    )

    matcap_color: FloatVectorProperty(
        name="Matcap_Color",
        description="Vector3 parameters for Matcap Color",
        default=(1.0, 1.0, 1.0),
        size=3,
    )

    rim_color: FloatVectorProperty(
        name="Matcap_Color",
        description="Vector3 parameters for Rim Color",
        default=(0.0, 0.0, 0.0),
        size=3,
    )

    outline_color: FloatVectorProperty(
        name="Outline_Color",
        description="Vector3 parameters for Outline Color",
        default=(0.0, 0.0, 0.0),
        size=3,
    )


class VRMHELPER_SCENE_vrm1_root_property_group(PropertyGroup):
    """---------------------------------------------------------
    Scene階層下のVRM1用プロパティグループ群
    ---------------------------------------------------------"""

    first_person_settings: PointerProperty(
        name="First_Person Settings",
        description="Group of properties for First_Person Annotation Settings",
        type=VRMHELPER_SCENE_vrm1_first_person_settigs,
    )

    expression_settings: PointerProperty(
        name="Expression Annotation Settings",
        description="Group of properties for Expression Settings",
        type=VRMHELPER_SCENE_vrm1_expression_settigs,
    )

    collider_settings: PointerProperty(
        name="Collider Settings",
        description="Group of properties for Collider Settings",
        type=VRMHELPER_SCENE_vrm1_collider_settigs,
    )

    collider_group_settings: PointerProperty(
        name="Spring Bone Collider Settings",
        description="Group of properties for Spring Bone Collider Settings",
        type=VRMHELPER_SCENE_vrm1_collider_group_settigs,
    )

    spring_settings: PointerProperty(
        name="Spring Bone Settings",
        description="Group of properties for Spring Bone Settings",
        type=VRMHELPER_SCENE_vrm1_spring_settigs,
    )

    constraint_settings: PointerProperty(
        name="Constraint Settings",
        description="Group of properties for Constraint Settings",
        type=VRMHELPER_SCENE_vrm1_constraint_settigs,
    )

    active_indexes: PointerProperty(
        name="Active Item Indexes",
        description="Used to define the active item index of UI Lists",
        type=VRMHELPER_SCENE_vrm1_ui_list_active_indexes,
    )

    mtoon1_stored_parameters: CollectionProperty(
        name="MToon1 Stored Parameters",
        description="Allows  MToon1 parameters of the target material to be saved and restored as default values",
        type=VRMHELPER_SCENE_vrm1_mtoon1_stored_parameters,
    )


# """---------------------------------------------------------
# ------------------------------------------------------------
#     Scene Root Property Group
# ------------------------------------------------------------
# ---------------------------------------------------------"""
class VRMHELPER_SCENE_root_property_group(PropertyGroup):
    """---------------------------------------------------------
        Scene階層下へのグルーピング用Property Group
    ---------------------------------------------------------"""

    basic_settings: PointerProperty(
        name="Basic Settings",
        description="Group of properties for Basic Tool Settings",
        type=VRMHELPER_SCENE_basic_settigs,
    )

    misc_settings: PointerProperty(
        name="Misc Settings",
        description="Misc Tools Settings",
        type=VRMHELPER_SCENE_misc_tools_settigs,
    )

    vrm0_props: PointerProperty(
        name="VRM0 Properties",
        description="Scene's Properties for VRM0",
        type=VRMHELPER_SCENE_vrm0_root_property_group,
    )

    vrm1_props: PointerProperty(
        name="VRM1 Properties",
        description="Scene's Properties for VRM1",
        type=VRMHELPER_SCENE_vrm1_root_property_group,
    )


"""---------------------------------------------------------
    Window Manager
---------------------------------------------------------"""
"""---------------------------------------------------------
    VRM0 Property
---------------------------------------------------------"""


class VRMHELPER_WM_vrm0_root_property_group(PropertyGroup):
    """---------------------------------------------------------
    WindowManager階層下のVRM0用プロパティグループ群
    ---------------------------------------------------------"""


"""---------------------------------------------------------
    VRM1 Property
---------------------------------------------------------"""


# ----------------------------------------------------------
#    First Person
# ----------------------------------------------------------
class VRMHELPER_WM_vrm1_first_person_list_items(PropertyGroup):
    """
    First Person設定･確認用UI Listに表示する候補アイテム｡
    """


# ----------------------------------------------------------
#    Expression
# ----------------------------------------------------------
class VRMHELPER_WM_vrm1_expression_list_items(PropertyGroup):
    """
    Expression設定･確認用UI Listに表示する候補アイテム｡
    """

    expressions_list: list[IDPropertyGroup] = []  # 全エクスプレッションを格納したリスト

    custom_expression_index: IntProperty(
        name="Custom Expression Index",
        description="If item is a custom expression, it has a value greater than or equal to 0",
        default=-1,
        min=-1,
    )


class VRMHELPER_WM_vrm1_expression_morph_list_items(PropertyGroup):
    """
    ExpressionのMorph Target設定･確認用UI Listに表示する候補アイテム｡
    """

    item_type: BoolVectorProperty(
        name="Item Type",
        description="[0]: is_label, [1]: is_shape_key",
        size=2,
    )

    bind_index: IntProperty(
        name="Item Index",
        description="Index of item in VRM extension compornent",
        default=0,
    )

    shape_key_name: StringProperty(
        name="Shape Key",
        description="Shape key registered in BindDescription",
        default="",
    )


class VRMHELPER_WM_vrm1_expression_material_list_items(PropertyGroup):
    """
    ExpressionのMaterial Color/TextureTransform Bind設定･確認用UI Listに表示する候補アイテム｡
    """

    item_type: BoolVectorProperty(
        name="Item Type",
        description="[0]: is_label, [1]: is_color, [2]: is_texture_transform",
        size=3,
    )

    bind_index: IntProperty(
        name="Item Index",
        description="Index of item in VRM extension compornent",
        default=0,
    )

    bind_material_name: StringProperty(
        name="Bind Material Name",
        description="Material name of material bind",
        default="",
    )


# ----------------------------------------------------------
#    Collider
# ----------------------------------------------------------
class VRMHELPER_WM_vrm1_collider_list_items(PropertyGroup):
    """
    Collider設定･確認用UI Listに表示する候補アイテム｡
    """

    is_updated_bone_name: BoolProperty(
        name="Is Changed Bone Name",
        description="Prevents infinite recursion when bone is renamed",
        default=True,
    )

    item_type: BoolVectorProperty(
        name="Item Type",
        description="[0]: is_label, [1]: is_bone, [2]:is_collider , [3]: is_child_end",
        size=4,
        default=(0, 0, 0, 0),
    )

    bone_name: StringProperty(
        name="Bone Name",
        description="Parent bone name of collider object",
        default="",
    )

    collider_name: StringProperty(
        name="Collider Name",
        description="Name of collider object",
        default="",
    )

    collider_object: PointerProperty(
        name="Collider Object",
        description="Empty Object that defines vrm spring collider",
        type=Object,
    )

    collider_type: EnumProperty(
        name="Collider Type",
        description="Type of VRM Spring Collider",
        items=(
            ("SPHERE", "Sphere", "Sphere Collider"),
            ("CAPSULE", "Capsule", "Capsule Collidear"),
            ("CAPSULE_END", "Capsule End", "Capsule Collidear End"),
        ),
        default="SPHERE",
    )

    parent_count: IntProperty(
        name="Parent Count",
        description="Parent count of bone",
        default=0,
    )

    item_index: IntProperty(
        name="Item Index",
        description="Index of item in VRM extension compornent",
        default=0,
    )


# ----------------------------------------------------------
#    Collider Group
# ----------------------------------------------------------
class VRMHELPER_WM_vrm1_collider_group_list_items(PropertyGroup):
    """
    Collider Group設定･確認用UI Listに表示する候補アイテム｡
    """

    item_type: BoolVectorProperty(
        name="Item Type",
        description="[0]: is_label,[1]: is_collider_group, [2]: is_collider",
        size=3,
        default=(0, 0, 0),
    )

    item_name: StringProperty(
        name="Collider Group Name",
        description=(
            "Name of the collider group component registered in the VRM Extension"
        ),
        default="",
    )

    item_indexes: IntVectorProperty(
        name="Item Index",
        description="Indexes of item in VRM extension compornent.[0]:Collider Groups, [1]:Collider",
        size=2,
        default=(0, 0),
        min=0,
    )


# ----------------------------------------------------------
#    Spring
# ----------------------------------------------------------
class VRMHELPER_WM_vrm1_spring_list_items(PropertyGroup):
    """
    Spring Bone設定･確認用UI Listに表示する候補アイテム｡
    """

    item_type: BoolVectorProperty(
        name="Item Type",
        description="[0]: is_label, [1]: is_spring, [2]: is_joint, [3]: is_collider_group",
        size=4,
        default=(0, 0, 0, 0),
    )

    item_name: StringProperty(
        name="Item Name",
        description="Name of the springs component registered in the VRM extension",
        default="",
    )

    item_indexes: IntVectorProperty(
        name="Item Indexes",
        description="Indexes of item in VRM extension compornent.[0]:Springs, [1]:Joints, [2]:Collider Groups",
        size=3,
        default=(0, 0, 0),
        min=0,
    )


class VRMHELPER_WM_vrm1_operator_spring_bone_group_list_items(PropertyGroup):
    is_target: BoolProperty(
        name="Is Target",
        description="This is the target group of the operator",
        default=False,
    )

    group_index: IntProperty(
        name="Bone Group Index",
        description="Stores the index of the bone group",
        default=0,
    )


class VRMHELPER_WM_vrm1_operator_spring_collider_group_list_items(PropertyGroup):
    is_target: BoolProperty(
        name="Is Target",
        description="This is the target group of the operator",
        default=False,
    )

    vrm_name: StringProperty(
        name="VRM Name",
        description="vrm_name property defined vrm extension",
        default="",
    )


class VRMHELPER_WM_vrm1_operator_spring_list_items(PropertyGroup):
    is_target: BoolProperty(
        name="Is Target",
        description="This is the target group of the operator",
        default=False,
    )

    spring_index: IntProperty(
        name="Spring Index",
        description="Index in Springs",
        default=0,
    )


# ----------------------------------------------------------
#    Constraint
# ----------------------------------------------------------
class VRMHELPER_WM_vrm1_constraint_property(PropertyGroup):
    def update_constraint_axis(self, context):
        if self.is_locked_update:
            return

        constraint_list = get_ui_vrm1_constraint_prop()
        selected_type = get_scene_vrm1_constraint_prop().constraint_type
        active_index = get_vrm1_active_index_prop("CONSTRAINT")
        active_item = constraint_list[active_index]

        match selected_type:
            case "OBJECT":
                active_item = constraint_list[active_index]
                target_object = bpy.data.objects.get(active_item.name)
                source_constraint = target_object.constraints[
                    active_item.constraint_index
                ]

            case "BONE":
                target_armature = get_target_armature()
                target_bone = target_armature.pose.bones.get(active_item.name)
                source_constraint = target_bone.constraints[
                    active_item.constraint_index
                ]

        source_constraint.use_x = False
        source_constraint.use_y = False
        source_constraint.use_z = False

        attr_name = f"use_{self.axis.lower()}"
        setattr(source_constraint, attr_name, True)

    ############################################################

    is_locked_update: BoolProperty(
        name="Property Name",
        description="Description",
        default=True,
    )

    axis: EnumProperty(
        name="Axis",
        description="Copy Rotation Axis",
        items=(
            ("X", "X", "Use_X"),
            ("Y", "Y", "Use_Y"),
            ("Z", "Z", "Use_Z"),
        ),
        default="X",
        update=update_constraint_axis,
    )


class VRMHELPER_WM_vrm1_constraint_list_items(PropertyGroup):
    """
    Node Constraint設定･確認用UI Listに表示する候補アイテム｡
    """

    is_blank: BoolProperty(
        name="Is Blank",
        description="This Item is Blank",
        default=False,
    )

    is_label: BoolProperty(
        name="Is Label",
        description="This Item is Label",
        default=False,
    )

    constraint_name: StringProperty(
        name="Constraint Name",
        description="Name of constraint",
        default="",
    )

    constraint_type: IntProperty(
        name="Constraint_Type",
        description="0: roll_constraint, 1: aim_constraint, 2: rotation_constraint",
        default=0,
    )

    is_object_constraint: BoolProperty(
        name="Is Object Constraint",
        description="This item is object constraint",
        default=False,
    )

    is_circular_dependency: BoolProperty(
        name="Is Circular Dependency",
        description="This constraint has circlular dependency",
        default=False,
    )

    constraint_index: IntProperty(
        name="Constraint Index",
        description="Index of the target constraint in the constraint stack",
        default=0,
    )


class VRMHELPER_WM_vrm1_root_property_group(PropertyGroup):
    """---------------------------------------------------------
    WindowManager階層下のVRM1用プロパティグループ群
    ---------------------------------------------------------"""

    first_person_list_items4custom_filter: CollectionProperty(
        name="Candidate First Person List Items",
        description="Elements registered with this collection property are displayed in the UI List",
        type=VRMHELPER_WM_vrm1_first_person_list_items,
    )

    expression_list_items4custom_filter: CollectionProperty(
        name="Candidate Expression List Items",
        description="Elements registered with this collection property are displayed in the UI List",
        type=VRMHELPER_WM_vrm1_expression_list_items,
    )

    expression_morph_list_items4custom_filter: CollectionProperty(
        name="Candidate Expression Morph Target Bind List Items",
        description="Elements registered with this collection property are displayed in the UI List",
        type=VRMHELPER_WM_vrm1_expression_morph_list_items,
    )

    expression_material_list_items4custom_filter: CollectionProperty(
        name="Candidate Expression Material Bind List Items",
        description="Elements registered with this collection property are displayed in the UI List",
        type=VRMHELPER_WM_vrm1_expression_material_list_items,
    )

    collider_list_items4custom_filter: CollectionProperty(
        name="Candidate Collider List Items",
        description="Elements registered with this collection property are displayed in the UI List",
        type=VRMHELPER_WM_vrm1_collider_list_items,
    )

    collider_group_list_items4custom_filter: CollectionProperty(
        name="Candidate Collider Group List Items",
        description="Elements registered with this collection property are displayed in the UI List",
        type=VRMHELPER_WM_vrm1_collider_group_list_items,
    )

    spring_list_items4custom_filter: CollectionProperty(
        name="Candidate Spring List Items",
        description="Elements registered with this collection property are displayed in the UI List",
        type=VRMHELPER_WM_vrm1_spring_list_items,
    )

    bone_group_list4operator: CollectionProperty(
        name="Operator's Target Bone Group",
        description="Collection for storing the operator's target bone group",
        type=VRMHELPER_WM_vrm1_operator_spring_bone_group_list_items,
    )

    collider_group_list4operator: CollectionProperty(
        name="Operator's Target Collider Group",
        description="Collection for storing the operator's target collider group",
        type=VRMHELPER_WM_vrm1_operator_spring_collider_group_list_items,
    )

    spring_list4operator: CollectionProperty(
        name="Operator's Target Collider Group",
        description="Collection for storing the operator's target joint",
        type=VRMHELPER_WM_vrm1_operator_spring_list_items,
    )

    constraint_list_items4custom_filter: CollectionProperty(
        name="Candidate Constraint List Items",
        description="Elements registered with this collection property are displayed in the UI List",
        type=VRMHELPER_WM_vrm1_constraint_list_items,
    )

    constraint_prop: PointerProperty(
        name="Constraint Prop",
        description="Properties of Constraints",
        type=VRMHELPER_WM_vrm1_constraint_property,
    )


class VRMHELPER_WM_root_property_group(PropertyGroup):
    """---------------------------------------------------------
        Window Manager階層下へのグルーピング用Property Group
    ---------------------------------------------------------"""

    vrm0_props: PointerProperty(
        name="VRM0 Properties",
        description="WindowManager's Properties for VRM0",
        type=VRMHELPER_WM_vrm0_root_property_group,
    )

    vrm1_props: PointerProperty(
        name="VRM1 Properties",
        description="WindowManager's Properties for VRM1",
        type=VRMHELPER_WM_vrm1_root_property_group,
    )


"""---------------------------------------------------------
------------------------------------------------------------
    Function
------------------------------------------------------------
---------------------------------------------------------"""
"""---------------------------------------------------------
    Common
---------------------------------------------------------"""


def evaluation_active_index_prop(
    source_list: Any,
    active_index: int,
) -> int:
    """
    UI Listアクティブインデックスの値がUi Listの幅を超えていないかどうかを評価する｡
    超えている場合はアクティブインデックスをリストの幅と同値として扱う｡

    Parameters
    ----------
    source_list : Any
        対象となるUI List用のCollection Property

    active_index : int
        処理対象のアクティブインデックス

    Returns
    -------
    int
        処理結果として返すインデックスの値

    """

    length = max(len(source_list) - 1, 0)
    if length < active_index:
        active_index = length
    return active_index


"""---------------------------------------------------------
    Get Common Property Group
---------------------------------------------------------"""


def get_wm_prop_root() -> VRMHELPER_WM_root_property_group:
    wm_root_prop = bpy.context.window_manager.vrm_helper
    return wm_root_prop


def get_scene_prop_root() -> VRMHELPER_SCENE_root_property_group:
    scene_root_prop = bpy.context.scene.vrm_helper
    return scene_root_prop


def get_scene_basic_prop() -> VRMHELPER_SCENE_basic_settigs:
    scene_root_prop = get_scene_prop_root()
    scene_basic_prop = scene_root_prop.basic_settings
    return scene_basic_prop


def get_target_armature() -> Optional[Object]:
    """
    Basic Prop階層下のTarget Armatureに登録されたArmature Objectを返す｡

    Returns
    -------
    Optional[Object]
        Target Armatureに登録されたオブジェクト｡

    """

    if target_armature := get_scene_basic_prop().target_armature:
        return target_armature


def get_target_armature_data() -> Optional[Armature]:
    """
    Basic Prop階層下のTarget Armatureに登録されたArmature ObjectにリンクされたObject Dataを返す｡

    Returns
    -------
    Optional[Armature]
        Target ArmatureにリンクされたData Object

    """

    if target_armature := get_target_armature():
        return target_armature.data


def get_scene_misc_prop() -> VRMHELPER_SCENE_misc_tools_settigs:
    scene_root_prop = get_scene_prop_root()
    scene_misc_prop = scene_root_prop.misc_settings
    return scene_misc_prop


"""---------------------------------------------------------
    Get VRM0 Property Group
---------------------------------------------------------"""


def get_vrm0_scene_root_prop() -> VRMHELPER_SCENE_vrm0_root_property_group:
    scene_root_prop = get_scene_prop_root()
    vrm0_scene_root_property = scene_root_prop.vrm0_props
    return vrm0_scene_root_property


def get_vrm0_wm_root_prop() -> VRMHELPER_WM_vrm0_root_property_group:
    wm_root_prop = get_wm_prop_root()
    vrm0_wm_root_prop = wm_root_prop.vrm0_props

    return vrm0_wm_root_prop


"""---------------------------------------------------------
    Get VRM1 Property Group
---------------------------------------------------------"""


# ----------------------------------------------------------
#    Window Manager
# ----------------------------------------------------------
def get_vrm1_wm_root_prop() -> VRMHELPER_WM_vrm1_root_property_group:
    wm_root_prop = get_wm_prop_root()
    vrm1_wm_root_prop = wm_root_prop.vrm1_props

    return vrm1_wm_root_prop


def get_wm_vrm1_constraint_prop() -> VRMHELPER_WM_vrm1_constraint_property:
    wm_vrm1_prop = get_vrm1_wm_root_prop()
    constraint_prop = wm_vrm1_prop.constraint_prop
    return constraint_prop


def get_ui_vrm1_first_person_prop() -> VRMHELPER_WM_vrm1_first_person_list_items:
    wm_vrm1_root_prop = get_vrm1_wm_root_prop()
    first_person_filter = wm_vrm1_root_prop.first_person_list_items4custom_filter
    return first_person_filter


def get_ui_vrm1_expression_prop() -> VRMHELPER_WM_vrm1_expression_list_items:
    wm_vrm1_root_prop = get_vrm1_wm_root_prop()
    expression_filter = wm_vrm1_root_prop.expression_list_items4custom_filter
    return expression_filter


def get_ui_vrm1_expression_morph_prop() -> (
    VRMHELPER_WM_vrm1_expression_morph_list_items
):
    wm_vrm1_root_prop = get_vrm1_wm_root_prop()
    expression_morph_filter = (
        wm_vrm1_root_prop.expression_morph_list_items4custom_filter
    )
    return expression_morph_filter


def get_ui_vrm1_expression_material_prop() -> (
    VRMHELPER_WM_vrm1_expression_material_list_items
):
    wm_vrm1_root_prop = get_vrm1_wm_root_prop()
    expression_material_filter = (
        wm_vrm1_root_prop.expression_material_list_items4custom_filter
    )
    return expression_material_filter


def get_ui_vrm1_collider_prop() -> VRMHELPER_WM_vrm1_collider_list_items:
    wm_vrm1_root_prop = get_vrm1_wm_root_prop()
    collider_filter = wm_vrm1_root_prop.collider_list_items4custom_filter
    return collider_filter


def get_ui_vrm1_collider_group_prop() -> VRMHELPER_WM_vrm1_collider_group_list_items:
    wm_vrm1_root_prop = get_vrm1_wm_root_prop()
    collider_group_filter = wm_vrm1_root_prop.collider_group_list_items4custom_filter
    return collider_group_filter


def get_ui_vrm1_spring_prop() -> VRMHELPER_WM_vrm1_spring_list_items:
    wm_vrm1_root_prop = get_vrm1_wm_root_prop()
    spring_filter = wm_vrm1_root_prop.spring_list_items4custom_filter
    return spring_filter


def get_ui_vrm1_operator_bone_group_prop() -> (
    VRMHELPER_WM_vrm1_operator_spring_bone_group_list_items
):
    wm_vrm1_root_prop = get_vrm1_wm_root_prop()
    bone_group_filter = wm_vrm1_root_prop.bone_group_list4operator
    return bone_group_filter


def get_ui_vrm1_operator_collider_group_prop() -> (
    VRMHELPER_WM_vrm1_operator_spring_collider_group_list_items
):
    wm_vrm1_root_prop = get_vrm1_wm_root_prop()
    collider_group_filter = wm_vrm1_root_prop.collider_group_list4operator
    return collider_group_filter


def get_ui_vrm1_operator_spring_prop() -> VRMHELPER_WM_vrm1_operator_spring_list_items:
    wm_vrm1_root_prop = get_vrm1_wm_root_prop()
    spring_filter = wm_vrm1_root_prop.spring_list4operator
    return spring_filter


def get_ui_vrm1_constraint_prop() -> VRMHELPER_WM_vrm1_constraint_list_items:
    wm_vrm1_root_prop = get_vrm1_wm_root_prop()
    constraint_filter = wm_vrm1_root_prop.constraint_list_items4custom_filter
    return constraint_filter


# ----------------------------------------------------------
#    Scene
# ----------------------------------------------------------
def get_vrm1_scene_root_prop() -> VRMHELPER_SCENE_vrm1_root_property_group:
    scene_root_prop = get_scene_prop_root()
    vrm1_scene_root_property = scene_root_prop.vrm1_props
    return vrm1_scene_root_property


def get_vrm1_index_root_prop() -> VRMHELPER_SCENE_vrm1_ui_list_active_indexes:
    vrm1_root_property = get_vrm1_scene_root_prop()
    vrm1_index_root_prop = vrm1_root_property.active_indexes
    return vrm1_index_root_prop


def get_vrm1_active_index_prop(component_type: VRM_COMPONENT_TYPES) -> int:
    """
    引数'type'に対応したアクティブインデックスのプロパティを
    'VRMHELPER_SCENE_vrm1_ui_list_active_indexes'から取得する｡

    Parameters
    ----------
    component_type: VRM_COMPONENT_TYPES
        UI Listアクティブインデックスを取得したいVRMコンポーネントの種類｡

    Returns
    -------
    int
        取得されたアクティブアイテムのインデックス｡

    """
    vrm1_index_prop = get_vrm1_index_root_prop()

    match component_type:
        case "FIRST_PERSON":
            list_items = get_ui_vrm1_first_person_prop()
            index = vrm1_index_prop.first_person

        case "EXPRESSION":
            list_items = get_ui_vrm1_expression_prop()
            index = vrm1_index_prop.expression

        case "EXPRESSION_MORPH":
            list_items = get_ui_vrm1_expression_morph_prop()
            index = vrm1_index_prop.expression_morph

        case "EXPRESSION_MATERIAL":
            list_items = get_ui_vrm1_expression_material_prop()
            index = vrm1_index_prop.expression_material

        case "COLLIDER":
            list_items = get_ui_vrm1_collider_prop()
            index = vrm1_index_prop.collider

        case "COLLIDER_GROUP":
            list_items = get_ui_vrm1_collider_group_prop()
            index = vrm1_index_prop.collider_group

        case "SPRING":
            list_items = get_ui_vrm1_spring_prop()
            index = vrm1_index_prop.spring

        case "CONSTRAINT":
            list_items = get_ui_vrm1_constraint_prop()
            index = vrm1_index_prop.constraint

    active_index = evaluation_active_index_prop(list_items, index)
    return active_index


def get_scene_vrm1_first_person_prop() -> VRMHELPER_SCENE_vrm1_first_person_settigs:
    scene_vrm1_prop = get_vrm1_scene_root_prop()
    first_person_prop = scene_vrm1_prop.first_person_settings
    return first_person_prop


def get_scene_vrm1_expression_prop() -> VRMHELPER_SCENE_vrm1_expression_settigs:
    scene_vrm1_prop = get_vrm1_scene_root_prop()
    expression_prop = scene_vrm1_prop.expression_settings
    return expression_prop


def get_scene_vrm1_collider_prop() -> VRMHELPER_SCENE_vrm1_collider_settigs:
    scene_vrm1_prop = get_vrm1_scene_root_prop()
    collider_prop = scene_vrm1_prop.collider_settings
    return collider_prop


def get_scene_vrm1_collider_group_prop() -> VRMHELPER_SCENE_vrm1_collider_group_settigs:
    scene_vrm1_prop = get_vrm1_scene_root_prop()
    collider_group_prop = scene_vrm1_prop.collider_group_settings
    return collider_group_prop


def get_scene_vrm1_spring_prop() -> VRMHELPER_SCENE_vrm1_spring_settigs:
    scene_vrm1_prop = get_vrm1_scene_root_prop()
    spring_prop = scene_vrm1_prop.spring_settings
    return spring_prop


def get_scene_vrm1_constraint_prop() -> VRMHELPER_SCENE_vrm1_constraint_settigs:
    scene_vrm1_prop = get_vrm1_scene_root_prop()
    constraint_prop = scene_vrm1_prop.constraint_settings
    return constraint_prop


def get_scene_vrm1_mtoon_stored_prop() -> VRMHELPER_SCENE_vrm1_mtoon1_stored_parameters:
    scene_vrm1_prop = get_vrm1_scene_root_prop()
    mtoon_stored_prop = scene_vrm1_prop.mtoon1_stored_parameters
    return mtoon_stored_prop


"""---------------------------------------------------------
------------------------------------------------------------
    Resiter Target
------------------------------------------------------------
---------------------------------------------------------"""
CLASSES = (
    # ----------------------------------------------------------
    #    Scene
    # ----------------------------------------------------------
    VRMHELPER_SCENE_basic_settigs,
    VRMHELPER_SCENE_misc_tools_settigs,
    VRMHELPER_SCENE_vrm0_root_property_group,
    VRMHELPER_SCENE_vrm1_first_person_settigs,
    VRMHELPER_SCENE_vrm1_expression_settigs,
    VRMHELPER_SCENE_vrm1_collider_settigs,
    VRMHELPER_SCENE_vrm1_collider_group_settigs,
    VRMHELPER_SCENE_vrm1_spring_settigs,
    VRMHELPER_SCENE_vrm1_constraint_settigs,
    VRMHELPER_SCENE_vrm1_ui_list_active_indexes,
    VRMHELPER_SCENE_vrm1_mtoon1_stored_parameters,
    VRMHELPER_SCENE_vrm1_root_property_group,
    VRMHELPER_SCENE_root_property_group,
    # ----------------------------------------------------------
    #    Window Manager
    # ----------------------------------------------------------
    VRMHELPER_WM_vrm0_root_property_group,
    VRMHELPER_WM_vrm1_first_person_list_items,
    VRMHELPER_WM_vrm1_expression_list_items,
    VRMHELPER_WM_vrm1_expression_morph_list_items,
    VRMHELPER_WM_vrm1_expression_material_list_items,
    VRMHELPER_WM_vrm1_collider_list_items,
    VRMHELPER_WM_vrm1_collider_group_list_items,
    VRMHELPER_WM_vrm1_spring_list_items,
    VRMHELPER_WM_vrm1_operator_spring_bone_group_list_items,
    VRMHELPER_WM_vrm1_operator_spring_collider_group_list_items,
    VRMHELPER_WM_vrm1_operator_spring_list_items,
    VRMHELPER_WM_vrm1_constraint_property,
    VRMHELPER_WM_vrm1_constraint_list_items,
    VRMHELPER_WM_vrm1_root_property_group,
    VRMHELPER_WM_root_property_group,
)
