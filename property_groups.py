if "bpy" in locals():
    import importlib

    reloadable_modules = [
        "preparation_logger",
        "addon_constants",
        "preferences",
    ]

    for module in reloadable_modules:
        if module in locals():
            importlib.reload(locals()[module])

else:
    from .Logging import preparation_logger
    from . import addon_constants
    from . import preferences

from typing import (
    Literal,
    Optional,
    Any,
)
from pathlib import Path

import bpy


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


from .addon_classes import (
    ReferenceVrm1ExpressionPropertyGroup,
    ReferenceVrm1CustomExpressionPropertyGroup,
    ReferenceVrm1ColliderPropertyGroup,
)

from .addon_constants import (
    VRM0_COMPONENT_TYPES,
    VRM1_COMPONENT_TYPES,
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
class VRMHELPER_SCENE_basic_settings(bpy.types.PropertyGroup):
    """
    アドオンの基本設定を行なうプロパティ
    """

    def filtering_armature_type(self, source_object: bpy.types.Object) -> bool:
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
        type=bpy.types.Object,
        poll=filtering_armature_type,
        update=update_addon_collection,
    )

    tool_mode_items = (
        ("0", "0.x", "Setup VRM for version 0.x", 0),
        ("1", "1.x", "Setup VRM for version 1.x", 1),
        # ("2", "Misc", "Use other utility tools.", 2),
    )

    tool_mode: EnumProperty(
        name="Tool Mode",
        description="Property for selecting the UI item to draw",
        items=tool_mode_items,
        default=1,
        update=update_vrm_extension_version,
    )

    vrm0_sort_order_component_type = (
        "META",
        "HUMANOID",
        "FIRST_PERSON",
        "LOOK_AT",
        "BLEND_SHAPE",
        "COLLIDER_GROUP",
        "BONE_GROUP",
    )  # UI描画時に一定の順にソートするためのキー｡

    vrm1_sort_order_component_type = (
        "META",
        "HUMANOID",
        "FIRST_PERSON",
        "LOOK_AT",
        "EXPRESSION",
        "CONSTRAINT",
        "COLLIDER",
        "COLLIDER_GROUP",
        "SPRING",
    )  # UI描画時に一定の順にソートするためのキー｡

    vrm0_component_type_items = [
        ("FIRST_PERSON", "First Person", "Draw UI for setting First Person"),
        ("BLEND_SHAPE", "Blend Shape", "Draw UI for setting Blend Shape"),
        ("COLLIDER_GROUP", "Collider Group", "Draw UI for setting Collider Group"),
        ("BONE_GROUP", "Spring Bone Group", "Draw UI for setting Spring Bone Group"),
    ]

    vrm0_component_type: EnumProperty(
        name="Vrm0 Component Type",
        description="Property for selecting the UI item to draw",
        options={"ENUM_FLAG"},
        items=vrm0_component_type_items,
        default=set(),
        update=update_addon_collection,
    )

    vrm1_component_type_items = [
        ("FIRST_PERSON", "First Person", "Draw UI for setting First Person"),
        ("EXPRESSION", "Expression", "Draw UI for setting Expression"),
        ("CONSTRAINT", "Constraint", "Draw UI for setting Constraint"),
        ("COLLIDER", "Collider", "Draw UI for setting Collider"),
        ("COLLIDER_GROUP", "Collider Group", "Draw UI for setting Collider Group"),
        ("SPRING", "Spring", "Draw UI for setting Spring"),
    ]

    vrm1_component_type: EnumProperty(
        name="VRM1 Component Type",
        description="Property for selecting the UI item to draw",
        options={"ENUM_FLAG"},
        items=vrm1_component_type_items,
        default=set(),
        update=update_addon_collection,
    )


# ----------------------------------------------------------
#    Misc Tools
# ----------------------------------------------------------
class VRMHELPER_SCENE_misc_tools_settings(bpy.types.PropertyGroup):
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


# ----------------------------------------------------------
#    First Person
# ----------------------------------------------------------
class VRMHELPER_SCENE_vrm0_first_person_settings(bpy.types.PropertyGroup):
    """
    First Personの設定に関するプロパティ
    """

    annotation_type: EnumProperty(
        name="First Person Type",
        description="Determine the First_Person annotation you wish to apply",
        items=(
            (
                "Auto",
                "Auto",
                "Set the value to Auto",
            ),
            (
                "Both",
                "Both",
                "Set the value to Both",
            ),
            (
                "ThirdPersonOnly",
                "Third Person Only",
                "Set the value to Third Person Only",
            ),
            (
                "FirstPersonOnly",
                "First Person Only",
                "Set the value to First Person Only",
            ),
        ),
        default="Both",
    )

    is_filtering_by_type: BoolProperty(
        name="Filtering by Selected Type",
        description="Filters the display of the list according to the currently selected mode",
        default=True,
    )


# ----------------------------------------------------------
#    Blend Shape
# ----------------------------------------------------------
class VRMHELPER_SCENE_vrm0_blend_shape_settings(bpy.types.PropertyGroup):
    """
    Expressionの設定に関するプロパティ
    """

    editing_target: EnumProperty(
        name="Editing Targets",
        description="Select the bind to be edited",
        items=(
            ("BIND", "Bind", "Edit Binds"),
            ("MATERIAL", "Material", "Edit Material Binds"),
        ),
        default="BIND",
    )


class VRMHELPER_SCENE_vrm0_mtoon0_stored_parameters(bpy.types.PropertyGroup):
    material: PointerProperty(
        name="Material",
        description="Material stored parameters",
        type=bpy.types.Material,
    )

    color: FloatVectorProperty(
        name="Color",
        description="MToon0 Color",
        default=(1.0, 1.0, 1.0, 1.0),
        size=4,
    )

    shade_color: FloatVectorProperty(
        name="Shade Color",
        description="MToon0 Shade Color",
        default=(1.0, 1.0, 1.0),
        size=3,
    )

    rim_color: FloatVectorProperty(
        name="RIm Color",
        description="MToon0 Rim Color",
        default=(0.0, 0.0, 0.0),
        size=3,
    )
    emission_color: FloatVectorProperty(
        name="Emission Color",
        description="MToon0 Emission Color",
        default=(0.0, 0.0, 0.0),
        size=3,
    )
    outline_color: FloatVectorProperty(
        name="Outline Color",
        description="MToon0 Outline Color",
        default=(0.0, 0.0, 0.0),
        size=3,
    )

    texture_scale: FloatVectorProperty(
        name="Texture Scale",
        description="MToon0 Texture Scale",
        default=(1.0, 1.0),
        size=2,
    )

    texture_offset: FloatVectorProperty(
        name="Texture Offset",
        description="MToon0 Texture Offset",
        default=(0.0, 0.0),
        size=2,
    )


# ----------------------------------------------------------
#    Collider Group
# ----------------------------------------------------------
class VRMHELPER_SCENE_vrm0_collider_group_settings(bpy.types.PropertyGroup):
    """
    Collider Groupの設定に関するプロパティ
    """


# ----------------------------------------------------------
#    Spring Bone Groups
# ----------------------------------------------------------
class VRMHELPER_SCENE_vrm0_spring_settings(bpy.types.PropertyGroup):
    """
    Spring Bone Groupsの設定に関するプロパティ
    """


# ----------------------------------------------------------
#    for UI List
# ----------------------------------------------------------
class VRMHELPER_SCENE_vrm0_ui_list_active_indexes(bpy.types.PropertyGroup):
    """
    UI Listのアクティブアイテムインデックス用のIntPropertyを登録するプロパティグループ｡
    """

    # def update_active_collider_radius(
    #     self,
    #     collider_prop: VRMHELPER_SCENE_vrm1_collider_settings,
    #     collider: ReferenceVrm1ColliderPropertyGroup,
    # ):
    #     """
    #     'collider_prop'の'active_collider_radius'の値を'collider'のタイプに応じた
    #     'radius'と同じ値にセットする｡

    #     Parameters
    #     ----------
    #     collider_prop : VRMHELPER_SCENE_vrm1_collider_settings
    #         プロパティ更新の対象となるプロパティグループ

    #     collider : ReferenceVrm1ColliderPropertyGroup
    #         'radius'の参照元となるVRM AddonのColliderプロパティ

    #     """
    #     match detect_collider_shape_type(collider.shape_type):
    #         case -1:
    #             return
    #         case 0:
    #             source_radius = collider.shape.sphere.radius
    #         case 1:
    #             source_radius = collider.shape.capsule.radius

    #     collider_prop.active_collider_radius = source_radius

    def select_collider_object_by_ui_list(self, context):
        """
        Spring Bone_ColliderのUIリストアクティブアイテムが更新された際に､
        アクティブアイテムインデックスに対応したシーン内オブジェクトを選択状態にする｡
        また､アクティブコライダーの半径を'Active Collider Radius'に反映する｡
        """

        if self.is_locked_update:
            return

        if context.mode != "OBJECT":
            return

        collider_prop = get_scene_vrm1_collider_prop()
        collider_list = get_ui_vrm1_collider_prop()
        active_index = get_vrm1_active_index_prop("COLLIDER")
        active_item = collider_list[active_index]
        vrm_extension = get_target_armature_data().vrm_addon_extension
        colliders = vrm_extension.spring_bone1.colliders

        current_object_in_loop = None
        collider_prop.is_updated_collider_raduis = True

        match tuple(active_item.item_type):
            # アクティブアイテムがラベルである
            case (1, 0, 0, 0):
                return

            # アクティブアイテムがボーン名であればそのボーンに関連付けられた全てのコライダーを選択する｡
            case (0, 1, 0, 0):
                if collider_prop.link_bone != active_item.name:
                    collider_prop.is_updated_link_bone[0] = True
                    collider_prop.old_bone = active_item.name
                    collider_prop.link_bone = active_item.name

                if not collider_prop.is_additive_selecting:
                    bpy.ops.object.select_all(action="DESELECT")

                [
                    (
                        i.bpy_object.select_set(True),
                        (current_object_in_loop := i.bpy_object),
                    )
                    for i in colliders
                    if i.node.bone_name == active_item.bone_name
                ]

            # アクティブアイテムがコライダーであればそれを選択する｡
            case (0, 0, 1, 0):
                if collider := find_collider_from_empty_name(colliders, active_item.collider_name):
                    self.update_active_collider_radius(collider_prop, collider)

                if collider := bpy.data.objects.get(active_item.collider_name):
                    if not collider_prop.is_additive_selecting:
                        bpy.ops.object.select_all(action="DESELECT")
                    collider.select_set(True)
                    current_object_in_loop = collider

            # アクティブアイテムがカプセルコライダーのエンドであればそれを選択する｡
            case (0, 0, 0, 1):
                if collider := find_collider_from_empty_name(colliders, active_item.collider_name):
                    self.update_active_collider_radius(collider_prop, collider)

                if collider_object := bpy.data.objects.get(active_item.collider_name):
                    if not collider_prop.is_additive_selecting:
                        bpy.ops.object.select_all(action="DESELECT")
                    collider_object.select_set(True)
                    current_object_in_loop = collider_object

        collider_prop.is_updated_collider_raduis = False

        # 最後に取得されたコライダーオブジェクトをアクティブオブジェクトに設定する｡
        context.view_layer.objects.active = current_object_in_loop

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

    blend_shape: IntProperty(
        name="List Index of Blend_Shape",
        description="Index of active items in blend_shape UI List",
        default=0,
        min=0,
    )
    blend_shape_bind: IntProperty(
        name="List Index of Morph Target Bind",
        description="Index of active items in Blend Shape Morph Target UI List",
        default=0,
        min=0,
    )
    blend_shape_material: IntProperty(
        name="List Index of Material Bind",
        description="Index of active items in Blend Shape Material Color UI List",
        default=0,
        min=0,
    )

    collider_group: IntProperty(
        name="List Index of Collider Group",
        description="Index of active items in Collider Group UI List",
        default=0,
        min=0,
    )

    bone_group: IntProperty(
        name="List Index of Spring",
        description="Index of active items in Spring UI List",
        default=0,
        min=0,
    )

    linked_collider_group: IntProperty(
        name="List Index of Linked Collider Group",
        description="Index of active items in Linked Collider Group UI List",
        default=0,
        min=0,
    )


# ----------------------------------------------------------
#    VRM0 Root Property
# ----------------------------------------------------------
class VRMHELPER_SCENE_vrm0_root_property_group(bpy.types.PropertyGroup):
    """---------------------------------------------------------
    Scene階層下のVRM0用プロパティグループ群
    ---------------------------------------------------------"""

    first_person_settings: PointerProperty(
        name="First_Person Settings",
        description="Group of properties for First_Person Annotation Settings",
        type=VRMHELPER_SCENE_vrm0_first_person_settings,
    )

    blend_shape_settings: PointerProperty(
        name="Blend Shape Settings",
        description="Group of properties for Blend Shape Settings",
        type=VRMHELPER_SCENE_vrm0_blend_shape_settings,
    )

    mtoon0_stored_parameters: CollectionProperty(
        name="MToon0 Stored Parameters",
        description="Allows  MToon0 parameters of the target material to be saved and restored as default values",
        type=VRMHELPER_SCENE_vrm0_mtoon0_stored_parameters,
    )

    collider_group_settings: PointerProperty(
        name="Collider Group Settings",
        description="Group of properties for Collider Group Settings",
        type=VRMHELPER_SCENE_vrm0_collider_group_settings,
    )

    spring_settings: PointerProperty(
        name="Spring Bone Group Settings",
        description="Group of properties for Spring Bone Group Settings",
        type=VRMHELPER_SCENE_vrm0_spring_settings,
    )

    active_indexes: PointerProperty(
        name="Active Item Indexes",
        description="Used to define the active item index of UI Lists",
        type=VRMHELPER_SCENE_vrm0_ui_list_active_indexes,
    )


"""---------------------------------------------------------
    VRM1 Property
---------------------------------------------------------"""


# ----------------------------------------------------------
#    First Person
# ----------------------------------------------------------
class VRMHELPER_SCENE_vrm1_first_person_settings(bpy.types.PropertyGroup):
    """
    First Personの設定に関するプロパティ
    """

    annotation_type: EnumProperty(
        name="First Person Type",
        description="Determine the First_Person annotation you wish to apply",
        items=(
            (
                "auto",
                "Auto",
                "Set the value to Auto",
            ),
            (
                "both",
                "Both",
                "Set the value to Both",
            ),
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

    is_filtering_by_type: BoolProperty(
        name="Filtering by Selected Type",
        description="Filters the display of the list according to the currently selected mode",
        default=True,
    )


# ----------------------------------------------------------
#    Expression
# ----------------------------------------------------------
class VRMHELPER_SCENE_vrm1_expression_settings(bpy.types.PropertyGroup):
    """
    Expressionの設定に関するプロパティ
    """

    editing_target: EnumProperty(
        name="Editing Targets",
        description="Select the bind to be edited",
        items=(
            ("MORPH", "Morph Target", "Edit Morph Target Bind"),
            ("MATERIAL", "Material", "Edit Material Binds"),
        ),
        default="MORPH",
    )


# ----------------------------------------------------------
#    Collider
# ----------------------------------------------------------
class VRMHELPER_SCENE_vrm1_collider_settings(bpy.types.PropertyGroup):
    """
    Colliderの設定に関するプロパティ
    """

    def update_item2vrm1_collider(self, context: bpy.types.Context):
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

    def update_active_and_selected_collider_radius(self, context: bpy.types.Context):
        """
        値が変更された際にリスト内のアクティブコライダー及び選択されたEmptyオブジェクトに対応したコライダーの
        半径に同じ値を適応する｡
        """

        if self.is_updated_collider_raduis:
            return

        target_armature_data = get_target_armature_data()
        vrm_extension = target_armature_data.vrm_addon_extension
        colliders = vrm_extension.spring_bone1.colliders

        collider_list = get_ui_vrm1_collider_prop()
        active_index = get_vrm1_active_index_prop("COLLIDER")
        try:
            active_collider: VRMHELPER_WM_vrm1_collider_list_items = collider_list[active_index]
        except:
            return

        # 選択オブジェクト中のEmptyとアクティブコライダーに対応するEmptyオブジェクトの名前の集合｡
        collider_names = {i.name for i in context.selected_objects if i.type == "EMPTY"}
        collider_names.add(active_collider.collider_name)

        is_target_collider = (
            None,
            None,
        )  # [0]: Sphere or Collider Head [1]: Collidaer End
        for collider in colliders:
            collider: ReferenceVrm1ColliderPropertyGroup = collider

            match detect_collider_shape_type(collider.shape_type):
                case -1:  # Invailed
                    continue

                case 0:  # Sphere Collider
                    if not collider.bpy_object.name in collider_names:
                        continue
                    collider.shape.sphere.radius = self.active_collider_radius

                case 1:  # Capsule Collider
                    object_names = {
                        collider.bpy_object.name,
                        collider.bpy_object.children[0].name,
                    }
                    if not object_names & collider_names:
                        continue
                    collider.shape.capsule.radius = self.active_collider_radius

    # ---------------------------------------------------------------------------------

    is_updated_link_bone: BoolVectorProperty(
        name="Is Updated Link Bone",
        description="Avoid infinite recursion when updating",
        size=2,
        default=(0, 0),
    )

    is_updated_collider_raduis: BoolProperty(
        name="Locked Active Collider Radius",
        description="Update callback functions are locked while this flag is on",
        default=False,
    )

    is_additive_selecting: BoolProperty(
        name="Is Additive Selecting",
        description="Whether to unselect the selected object when updating the active item in the list",
        default=False,
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
        default=0.05,
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

    active_collider_radius: FloatProperty(
        name="Active Collider Radius",
        description="Change the radius of the active collider in the listing",
        default=0.05,
        min=0.0001,
        unit="LENGTH",
        update=update_active_and_selected_collider_radius,
    )


# ----------------------------------------------------------
#    Collider Group
# ----------------------------------------------------------
class VRMHELPER_SCENE_vrm1_collider_group_settings(bpy.types.PropertyGroup):
    """
    Collider Groupの設定に関するプロパティ
    """


# ----------------------------------------------------------
#    Spring
# ----------------------------------------------------------
class VRMHELPER_SCENE_vrm1_spring_settings(bpy.types.PropertyGroup):
    """
    Springの設定に関するプロパティ
    """

    hit_radius: FloatProperty(
        name="Hit Radius",
        description="radius value of joint set by operator",
        default=0.01,
        min=0.0,
        soft_max=0.5,
        precision=3,
    )

    stiffness: FloatProperty(
        name="stiffness",
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

    is_expand_operator_parameters: BoolProperty(
        name="Is Expand Operator Parameters",
        description="Select whether to display operator parameters.",
        default=True,
    )

    filter_of_adjusting_target_filter: StringProperty(
        name="Filter of Adjusting Target",
        description="Filter springs adjusting parameters",
        default="",
    )


# ----------------------------------------------------------
#    Constraint
# ----------------------------------------------------------
class VRMHELPER_SCENE_vrm1_constraint_settings(bpy.types.PropertyGroup):
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
class VRMHELPER_SCENE_vrm1_ui_list_active_indexes(bpy.types.PropertyGroup):
    """
    UI Listのアクティブアイテムインデックス用のIntPropertyを登録するプロパティグループ｡
    """

    def update_active_collider_radius(
        self,
        collider_prop: VRMHELPER_SCENE_vrm1_collider_settings,
        collider: ReferenceVrm1ColliderPropertyGroup,
    ):
        """
        'collider_prop'の'active_collider_radius'の値を'collider'のタイプに応じた
        'radius'と同じ値にセットする｡

        Parameters
        ----------
        collider_prop : VRMHELPER_SCENE_vrm1_collider_settings
            プロパティ更新の対象となるプロパティグループ

        collider : ReferenceVrm1ColliderPropertyGroup
            'radius'の参照元となるVRM AddonのColliderプロパティ

        """
        match detect_collider_shape_type(collider.shape_type):
            case -1:
                return
            case 0:
                source_radius = collider.shape.sphere.radius
            case 1:
                source_radius = collider.shape.capsule.radius

        collider_prop.active_collider_radius = source_radius

    def select_collider_object_by_ui_list(self, context):
        """
        Spring Bone_ColliderのUIリストアクティブアイテムが更新された際に､
        アクティブアイテムインデックスに対応したシーン内オブジェクトを選択状態にする｡
        また､アクティブコライダーの半径を'Active Collider Radius'に反映する｡
        """

        if self.is_locked_update:
            return

        if context.mode != "OBJECT":
            return

        collider_prop = get_scene_vrm1_collider_prop()
        collider_list = get_ui_vrm1_collider_prop()
        active_index = get_vrm1_active_index_prop("COLLIDER")
        active_item = collider_list[active_index]
        vrm_extension = get_target_armature_data().vrm_addon_extension
        colliders = vrm_extension.spring_bone1.colliders

        current_object_in_loop = None
        collider_prop.is_updated_collider_raduis = True

        match tuple(active_item.item_type):
            # アクティブアイテムがラベルである
            case (1, 0, 0, 0):
                return

            # アクティブアイテムがボーン名であればそのボーンに関連付けられた全てのコライダーを選択する｡
            case (0, 1, 0, 0):
                if collider_prop.link_bone != active_item.name:
                    collider_prop.is_updated_link_bone[0] = True
                    collider_prop.old_bone = active_item.name
                    collider_prop.link_bone = active_item.name

                if not collider_prop.is_additive_selecting:
                    bpy.ops.object.select_all(action="DESELECT")

                [
                    (
                        i.bpy_object.select_set(True),
                        (current_object_in_loop := i.bpy_object),
                    )
                    for i in colliders
                    if i.node.bone_name == active_item.bone_name
                ]

            # アクティブアイテムがコライダーであればそれを選択する｡
            case (0, 0, 1, 0):
                if collider := find_collider_from_empty_name(colliders, active_item.collider_name):
                    self.update_active_collider_radius(collider_prop, collider)

                if collider := bpy.data.objects.get(active_item.collider_name):
                    if not collider_prop.is_additive_selecting:
                        bpy.ops.object.select_all(action="DESELECT")
                    collider.select_set(True)
                    current_object_in_loop = collider

            # アクティブアイテムがカプセルコライダーのエンドであればそれを選択する｡
            case (0, 0, 0, 1):
                if collider := find_collider_from_empty_name(colliders, active_item.collider_name):
                    self.update_active_collider_radius(collider_prop, collider)

                if collider_object := bpy.data.objects.get(active_item.collider_name):
                    if not collider_prop.is_additive_selecting:
                        bpy.ops.object.select_all(action="DESELECT")
                    collider_object.select_set(True)
                    current_object_in_loop = collider_object

        collider_prop.is_updated_collider_raduis = False

        # 最後に取得されたコライダーオブジェクトをアクティブオブジェクトに設定する｡
        context.view_layer.objects.active = current_object_in_loop

    def select_constraint_by_ui_list(self, context):
        """
        Node ConstraintのUIリストアクティブアイテムが更新された際に､
        アクティブアイテムインデックスに対応したコンストレイントを持つ要素を可能なら選択状態にする｡
        """
        # 現在のインデックスからアクティブアイテムを取得する｡
        constraint_ui_list = get_ui_vrm1_constraint_prop()
        active_index = get_vrm1_active_index_prop("CONSTRAINT")
        if len(constraint_ui_list) - 1 < active_index:
            return

        active_item: VRMHELPER_WM_vrm1_constraint_list_items = constraint_ui_list[active_index]
        # アクティブアイテムがブランクまたはラベルの場合は何もしない｡
        if active_item.is_blank or active_item.is_label:
            return

        # アクティブアイテムがオブジェクトコンストレイントの場合
        if active_item.is_object_constraint:
            if not context.mode == "OBJECT":
                return

            # アクティブアイテムが参照しているコンストレイントが付与されたオブジェクトを選択する｡
            constrainted_object: bpy.types.Object = bpy.data.objects.get(active_item.name)
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
            constrainted_bone: bpy.types.PoseBone = pose_bones.get(active_item.name)
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


class VRMHELPER_SCENE_vrm1_mtoon1_stored_parameters(bpy.types.PropertyGroup):
    material: PointerProperty(
        name="Material",
        description="Material to store parameters",
        type=bpy.types.Material,
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


class VRMHELPER_SCENE_vrm1_root_property_group(bpy.types.PropertyGroup):
    """---------------------------------------------------------
    Scene階層下のVRM1用プロパティグループ群
    ---------------------------------------------------------"""

    first_person_settings: PointerProperty(
        name="First_Person Settings",
        description="Group of properties for First_Person Annotation Settings",
        type=VRMHELPER_SCENE_vrm1_first_person_settings,
    )

    expression_settings: PointerProperty(
        name="Expression Annotation Settings",
        description="Group of properties for Expression Settings",
        type=VRMHELPER_SCENE_vrm1_expression_settings,
    )

    collider_settings: PointerProperty(
        name="Collider Settings",
        description="Group of properties for Collider Settings",
        type=VRMHELPER_SCENE_vrm1_collider_settings,
    )

    collider_group_settings: PointerProperty(
        name="Spring Bone Collider Settings",
        description="Group of properties for Spring Bone Collider Settings",
        type=VRMHELPER_SCENE_vrm1_collider_group_settings,
    )

    spring_settings: PointerProperty(
        name="Spring Bone Settings",
        description="Group of properties for Spring Bone Settings",
        type=VRMHELPER_SCENE_vrm1_spring_settings,
    )

    constraint_settings: PointerProperty(
        name="Constraint Settings",
        description="Group of properties for Constraint Settings",
        type=VRMHELPER_SCENE_vrm1_constraint_settings,
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
class VRMHELPER_SCENE_root_property_group(bpy.types.PropertyGroup):
    """---------------------------------------------------------
        Scene階層下へのグルーピング用Property Group
    ---------------------------------------------------------"""

    basic_settings: PointerProperty(
        name="Basic Settings",
        description="Group of properties for Basic Tool Settings",
        type=VRMHELPER_SCENE_basic_settings,
    )

    misc_settings: PointerProperty(
        name="Misc Settings",
        description="Misc Tools Settings",
        type=VRMHELPER_SCENE_misc_tools_settings,
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
------------------------------------------------------------
    Window Manager
------------------------------------------------------------
---------------------------------------------------------"""
"""---------------------------------------------------------
    Common Property
---------------------------------------------------------"""


class VRMHELPER_WM_operator_spring_bone_group_list_items(bpy.types.PropertyGroup):
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


"""---------------------------------------------------------
    VRM0 Property
---------------------------------------------------------"""


# ----------------------------------------------------------
#    First Person
# ----------------------------------------------------------
class VRMHELPER_WM_vrm0_first_person_list_items(bpy.types.PropertyGroup):
    """
    First Person設定･確認用UI Listに表示する候補アイテム｡
    """


# ----------------------------------------------------------
#    Blend_Shape
# ----------------------------------------------------------


class VRMHELPER_WM_vrm0_blend_shape_bind_list_items(bpy.types.PropertyGroup):
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


class VRMHELPER_WM_vrm0_blend_shape_material_list_items(bpy.types.PropertyGroup):
    """
    Blend Shape ProxyのMaterial Color/TextureTransform Bind設定･確認用UI Listに表示する候補アイテム｡
    """

    def update_material_value_color(self, context):
        """
        material_colorの値が変更された際に､対応するColor系のMaterial Valueの値に反映する｡
        """
        if self.is_locked_color:
            return

        target_armature_data = get_target_armature_data()
        blend_shape_master = target_armature_data.vrm_addon_extension.vrm0.blend_shape_master
        blend_shape_groups = blend_shape_master.blend_shape_groups
        material_values = blend_shape_groups[
            blend_shape_master.active_blend_shape_group_index
        ].material_values
        active_material_value = material_values[self.value_index]
        target_value = active_material_value.target_value

        while len(target_value) < 4:
            target_value.add()

        for n, value in enumerate(self.material_color):
            try:
                target_value[n].value = value
            except:
                pass

    def update_uv_scale(self, context):
        """
        uv_scaleの値が変更された際に､対応するUV Coordinate系のUV Scale部分の値に反映する｡
        """
        if self.is_locked_uv_scale:
            self.is_locked_uv_scale = False
            return

        target_armature_data = get_target_armature_data()
        blend_shape_master = target_armature_data.vrm_addon_extension.vrm0.blend_shape_master
        blend_shape_groups = blend_shape_master.blend_shape_groups
        material_values = blend_shape_groups[
            blend_shape_master.active_blend_shape_group_index
        ].material_values
        active_material_value = material_values[self.value_index]
        target_value = active_material_value.target_value

        while len(target_value) < 4:
            target_value.add()

        for n, value in enumerate(self.uv_scale):
            try:
                target_value[n].value = value
            except:
                pass

    def update_uv_offset(self, context):
        """
        uv_offsetの値が変更された際に､対応するUV Coordinate系のUV Offset部分の値に反映する｡
        """
        if self.is_locked_uv_offset:
            self.is_locked_uv_offset = False
            return

        target_armature_data = get_target_armature_data()
        blend_shape_master = target_armature_data.vrm_addon_extension.vrm0.blend_shape_master
        blend_shape_groups = blend_shape_master.blend_shape_groups
        material_values = blend_shape_groups[
            blend_shape_master.active_blend_shape_group_index
        ].material_values
        active_material_value = material_values[self.value_index]
        target_value = active_material_value.target_value

        while len(target_value) < 4:
            target_value.add()

        for n, value in enumerate(self.uv_offset):
            try:
                target_value[n + 2].value = value
            except:
                pass

    # ---------------------------------------------------------------------------------

    is_locked_color: BoolProperty(
        name="Is Locked Color",
        description="Lock updating callback for material color",
        default=False,
    )

    is_locked_uv_scale: BoolProperty(
        name="Is Locked UV Scale",
        description="Lock updating callback for UV Scale",
        default=False,
    )

    is_locked_uv_offset: BoolProperty(
        name="Is Locked UV Offset",
        description="Lock updating callback for UV Offset",
        default=False,
    )

    item_type: BoolVectorProperty(
        name="Item Type",
        description="[0]: is_label, [1]: Material Color [2]: UV Coordinate, [3]: Undefined",
        size=4,
    )

    value_index: IntProperty(
        name="Item Index",
        description="Index of item in VRM extension compornent",
        default=-1,
    )

    material_name: StringProperty(
        name="Material name",
        description="Referenced Material Name",
        default="",
    )

    material_type: EnumProperty(
        name="Material Type",
        description="MToon or GLTF",
        items=(
            ("MTOON", "MToon", "This item is MToon Material"),
            ("GLTF", "GLTF", "This item is GLTF Material"),
            ("NONE", "None", "This item is not assigned material"),
        ),
        default="GLTF",
    )

    material_color: FloatVectorProperty(
        name="Material Color",
        description="Material Color of Material Value",
        default=(0.0, 0.0, 0.0, 1.0),
        size=4,
        subtype="COLOR",
        min=0,
        max=1,
        update=update_material_value_color,
    )

    uv_scale: FloatVectorProperty(
        name="UV Scale",
        description="UV Scale of Material Value",
        default=(1.0, 1.0),
        size=2,
        update=update_uv_scale,
    )

    uv_offset: FloatVectorProperty(
        name="UV Offset",
        description="UV Offset of Material Value",
        default=(0.0, 0.0),
        size=2,
        update=update_uv_offset,
    )

    prop_dict = {
        "MTOON": "mtoon_props",
        "GLTF": "gltf_props",
        "NONE": "none_props",
    }


class VRMHELPER_WM_vrm0_material_value_prop_names(bpy.types.PropertyGroup):
    property_name: StringProperty(
        name="Property Name",
        description="Description",
        default="your text",
    )

    gltf_props: CollectionProperty(
        name="GLTF Props",
        description="Names of GlTF Material Property Names",
        type=bpy.types.PropertyGroup,
    )

    mtoon_props: CollectionProperty(
        name="MToon Props",
        description="Names of MToon Material Property Names",
        type=bpy.types.PropertyGroup,
    )

    none_props: CollectionProperty(
        name="None Props",
        description="This item is not assigned material",
        type=bpy.types.PropertyGroup,
    )

    gltf_property_names = [
        "_Color",
        "_MainTex_ST",
        "_MainTex_ST_S",
        "_MainTex_ST_T",
        "_MetallicGlossMap_ST",
        "_MetallicGlossMap_ST_S",
        "_MetallicGlossMap_ST_T",
        "_BumpMap_ST",
        "_BumpMap_ST_S",
        "_BumpMap_ST_T",
        "_ParallaxMap_ST",
        "_ParallaxMap_ST_S",
        "_ParallaxMap_ST_T",
        "_OcclusionMap_ST",
        "_OcclusionMap_ST_S",
        "_OcclusionMap_ST_T",
        "_EmissionColor",
        "_EmissionMap_ST",
        "_EmissionMap_ST_S",
        "_EmissionMap_ST_T",
        "_DetailMask_ST",
        "_DetailMask_ST_S",
        "_DetailMask_ST_T",
        "_DetailAlbedoMap_ST",
        "_DetailAlbedoMap_ST_S",
        "_DetailAlbedoMap_ST_T",
        "_DetailNormalMap_ST",
        "_DetailNormalMap_ST_S",
        "_DetailNormalMap_ST_T",
    ]

    mtoon0_property_names = [
        "_Color",
        "_ShadeColor",
        "_MainTex_ST",
        "_MainTex_ST_S",
        "_MainTex_ST_T",
        "_ShadeTexture_ST",
        "_ShadeTexture_ST_S",
        "_ShadeTexture_ST_T",
        "_BumpMap_ST",
        "_BumpMap_ST_S",
        "_BumpMap_ST_T",
        "_ReceiveShadowTexture_ST",
        "_ReceiveShadowTexture_ST_S",
        "_ReceiveShadowTexture_ST_T",
        "_ShadingGradeTexture_ST",
        "_ShadingGradeTexture_ST_S",
        "_ShadingGradeTexture_ST_T",
        "_RimColor",
        "_RimTexture_ST",
        "_RimTexture_ST_S",
        "_RimTexture_ST_T",
        "_SphereAdd_ST",
        "_SphereAdd_ST_S",
        "_SphereAdd_ST_T",
        "_EmissionColor",
        "_EmissionMap_ST",
        "_EmissionMap_ST_S",
        "_EmissionMap_ST_T",
        "_OutlineWidthTexture_ST",
        "_OutlineWidthTexture_ST_S",
        "_OutlineWidthTexture_ST_T",
        "_OutlineColor",
        "_UvAnimMaskTexture_ST",
        "_UvAnimMaskTexture_ST_S",
        "_UvAnimMaskTexture_ST_T",
    ]


# ----------------------------------------------------------
#    Spring Bone
# ----------------------------------------------------------
class VRMHELPER_WM_vrm0_collider_group_list_items(bpy.types.PropertyGroup):
    """
    Collider Group設定･確認用UI Listに表示する候補アイテム｡
    """

    is_locked_bone_name: BoolProperty(
        name="Is Locked Bone Name",
        description="Prevents infinite recursion when bone is renamed",
        default=True,
    )

    item_type: BoolVectorProperty(
        name="Item Type",
        description="[0]: is_label, [1]: is_bone ,[2]: is_collider_group, [3]: is_collider",
        size=4,
        default=(0, 0, 0, 0),
    )

    bone_name: StringProperty(
        name="Bone Name",
        description="Parent bone name of collider object",
        default="",
    )

    group_name: StringProperty(
        name="String Property",
        description="Name of Collder Group",
        default="",
    )

    collider_name: StringProperty(
        name="Collider Name",
        description="Name of collider object",
        default="",
    )

    parent_count: IntProperty(
        name="Parent Count",
        description="Parent count of bone",
        default=0,
    )

    group_index: IntProperty(
        name="Item Index",
        description="Index of item in Collider Group in VRM Extension",
        default=0,
    )

    collider_index: IntProperty(
        name="Item Index",
        description="Index of item in Collider in VRM Extension",
        default=0,
    )


class VRMHELPER_WM_vrm0_spring_bone_list_items(bpy.types.PropertyGroup):
    """
    Spring Bone Group設定･確認用UI Listに表示する候補アイテム｡
    """

    item_type: BoolVectorProperty(
        name="Item Type",
        description="[0]: is_label, [1]: is_Bone_Group [2]: is_Bone",
        size=3,
        default=(0, 0, 0),
    )

    item_name: StringProperty(
        name="Item Name",
        description="Name of the springs component registered in the VRM extension",
        default="",
    )

    item_indexes: IntVectorProperty(
        name="Item Indexes",
        description="Indexes of item in VRM extension compornent.[0]:Bone Groups, [1]:Bone",
        size=2,
        default=(0, 0),
        min=0,
    )


class VRMHELPER_WM_vrm0_spring_linked_collider_group_list_items(bpy.types.PropertyGroup):
    """
    Spring Bone GroupにリンクされたCollider Group設定･確認用UI Listに表示する候補アイテム｡
    """

    item_type: BoolVectorProperty(
        name="Item Type",
        description="[0]: is_label, [1]: is_Bone_Group [2]: is_Bone",
        size=3,
        default=(0, 0, 0),
    )

    item_name: StringProperty(
        name="Item Name",
        description="Name of the springs component registered in the VRM extension",
        default="",
    )

    item_indexes: IntVectorProperty(
        name="Item Indexes",
        description="Indexes of item in VRM extension compornent.[0]:Bone Group, [1]:Collider Group",
        size=2,
        default=(0, 0),
        min=0,
    )


class VRMHELPER_WM_vrm0_operator_spring_collider_group_list_items(bpy.types.PropertyGroup):
    is_target: BoolProperty(
        name="Is Target",
        description="This is the target group of the operator",
        default=False,
    )

    bone_name: StringProperty(
        name="Bone Name",
        description="Parent Bone Name defined vrm extension",
        default="",
    )

    group_index: IntProperty(
        name="Group Index",
        description="Index in Collider Group",
        default=0,
    )


class VRMHELPER_WM_vrm0_operator_spring_bone_group_list_items(bpy.types.PropertyGroup):
    is_target: BoolProperty(
        name="Is Target",
        description="This is the target group of the operator",
        default=False,
    )

    group_index: IntProperty(
        name="Group Index",
        description="Index in Spring Bone Group",
        default=0,
    )


class VRMHELPER_WM_vrm0_root_property_group(bpy.types.PropertyGroup):
    """---------------------------------------------------------
    WindowManager階層下のVRM0用プロパティグループ群
    ---------------------------------------------------------"""

    first_person_list_items4custom_filter: CollectionProperty(
        name="Candidate First Person List Items",
        description="Elements registered with this collection property are displayed in the UI List",
        type=VRMHELPER_WM_vrm0_first_person_list_items,
    )

    blend_shape_bind_list_items4custom_filter: CollectionProperty(
        name="Candidate Blend Shape Morph Target Bind List Items",
        description="Elements registered with this collection property are displayed in the UI List",
        type=VRMHELPER_WM_vrm0_blend_shape_bind_list_items,
    )

    material_value_prop: PointerProperty(
        name="Material Value prop",
        description="Group of Material Value Property Name",
        type=VRMHELPER_WM_vrm0_material_value_prop_names,
    )

    blend_shape_material_list_items4custom_filter: CollectionProperty(
        name="Candidate Blend Shape Material Bind List Items",
        description="Elements registered with this collection property are displayed in the UI List",
        type=VRMHELPER_WM_vrm0_blend_shape_material_list_items,
    )

    collider_group_list_items4custom_filter: CollectionProperty(
        name="Candidate Collider Group List Items",
        description="Elements registered with this collection property are displayed in the UI List",
        type=VRMHELPER_WM_vrm0_collider_group_list_items,
    )

    spring_bone_list_items4custom_filter: CollectionProperty(
        name="Candidate Spring Bone List Items",
        description="Elements registered with this collection property are displayed in the UI List",
        type=VRMHELPER_WM_vrm0_spring_bone_list_items,
    )

    linked_collider_group_list_items4custom_filter: CollectionProperty(
        name="Candidate Linked Collider Group List Items",
        description="Elements registered with this collection property are displayed in the UI List",
        type=VRMHELPER_WM_vrm0_spring_linked_collider_group_list_items,
    )

    collider_group_list4operator: CollectionProperty(
        name="Operator's Target Collider Group",
        description="Target collider group collection for operators",
        type=VRMHELPER_WM_vrm0_operator_spring_collider_group_list_items,
    )

    spring_bone_group_list4operator: CollectionProperty(
        name="Operator's Target Spring Bone Group",
        description="Target spring bone group collection for operators",
        type=VRMHELPER_WM_vrm0_operator_spring_bone_group_list_items,
    )


"""---------------------------------------------------------
    VRM1 Property
---------------------------------------------------------"""


# ----------------------------------------------------------
#    First Person
# ----------------------------------------------------------
class VRMHELPER_WM_vrm1_first_person_list_items(bpy.types.PropertyGroup):
    """
    First Person設定･確認用UI Listに表示する候補アイテム｡
    """


# ----------------------------------------------------------
#    Expression
# ----------------------------------------------------------
class VRMHELPER_WM_vrm1_expression_list_items(bpy.types.PropertyGroup):
    """
    Expression設定･確認用UI Listに表示する候補アイテム｡
    """

    expressions_list: list[
        ReferenceVrm1ExpressionPropertyGroup | ReferenceVrm1CustomExpressionPropertyGroup
    ] = []  # 全エクスプレッションを格納したリスト

    has_morph_bind: BoolProperty(
        name="Has Morph Bind",
        description="This Expression has one or more Morph Binds",
        default=False,
    )

    has_material_bind: BoolProperty(
        name="Has Material Bind",
        description="This Expression has one or more Color or Texture Transform Binds",
        default=False,
    )

    expression_index: IntVectorProperty(
        name="Expression Index",
        description="Description",
        default=(-1, -1),
        size=2,
        min=-1,
    )


class VRMHELPER_WM_vrm1_expression_morph_list_items(bpy.types.PropertyGroup):
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


class VRMHELPER_WM_vrm1_expression_material_list_items(bpy.types.PropertyGroup):
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
class VRMHELPER_WM_vrm1_collider_list_items(bpy.types.PropertyGroup):
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
        type=bpy.types.Object,
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
class VRMHELPER_WM_vrm1_collider_group_list_items(bpy.types.PropertyGroup):
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
        description=("Name of the collider group component registered in the VRM Extension"),
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
class VRMHELPER_WM_vrm1_spring_list_items(bpy.types.PropertyGroup):
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


class VRMHELPER_WM_vrm1_operator_spring_collider_group_list_items(bpy.types.PropertyGroup):
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


class VRMHELPER_WM_vrm1_operator_spring_list_items(bpy.types.PropertyGroup):
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
class VRMHELPER_WM_vrm1_constraint_properties(bpy.types.PropertyGroup):
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
                source_constraint = target_object.constraints[active_item.constraint_index]

            case "BONE":
                target_armature = get_target_armature()
                target_bone = target_armature.pose.bones.get(active_item.name)
                source_constraint = target_bone.constraints[active_item.constraint_index]

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


class VRMHELPER_WM_vrm1_constraint_list_items(bpy.types.PropertyGroup):
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


class VRMHELPER_WM_vrm1_root_property_group(bpy.types.PropertyGroup):
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

    collider_group_list4operator: CollectionProperty(
        name="Operator's Target Collider Group",
        description="Target collider group collection for operators",
        type=VRMHELPER_WM_vrm1_operator_spring_collider_group_list_items,
    )

    spring_list4operator: CollectionProperty(
        name="Operator's Target Springs",
        description="Target springs collection for operators",
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
        type=VRMHELPER_WM_vrm1_constraint_properties,
    )


class VRMHELPER_WM_root_property_group(bpy.types.PropertyGroup):
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

    bone_group_list4operator: CollectionProperty(
        name="Operator's Target Bone Group",
        description="Collection for storing the operator's target bone group",
        type=VRMHELPER_WM_operator_spring_bone_group_list_items,
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


def get_scene_basic_prop() -> VRMHELPER_SCENE_basic_settings:
    scene_root_prop = get_scene_prop_root()
    scene_basic_prop = scene_root_prop.basic_settings
    return scene_basic_prop


def get_target_armature() -> Optional[bpy.types.Object]:
    """
    Basic Prop階層下のTarget Armatureに登録されたArmature Objectを返す｡

    Returns
    -------
    Optional[Object]
        Target Armatureに登録されたオブジェクト｡

    """

    if target_armature := get_scene_basic_prop().target_armature:
        return target_armature


def get_target_armature_data() -> Optional[bpy.types.Armature]:
    """
    Basic Prop階層下のTarget Armatureに登録されたArmature ObjectにリンクされたObject Dataを返す｡

    Returns
    -------
    Optional[Armature]
        Target ArmatureにリンクされたData Object

    """

    if target_armature := get_target_armature():
        return target_armature.data


def get_scene_misc_prop() -> VRMHELPER_SCENE_misc_tools_settings:
    scene_root_prop = get_scene_prop_root()
    scene_misc_prop = scene_root_prop.misc_settings
    return scene_misc_prop


def get_ui_bone_group_prop() -> bpy.types.bpy_prop_collection:
    """VRMHELPER_WM_operator_spring_bone_group_list_items"""
    wm_root_prop = get_wm_prop_root()
    bone_group_filter = wm_root_prop.bone_group_list4operator
    return bone_group_filter


"""---------------------------------------------------------
    Get VRM0 Property Group
---------------------------------------------------------"""


# ----------------------------------------------------------
#    Scene
# ----------------------------------------------------------
def get_vrm0_scene_root_prop() -> VRMHELPER_SCENE_vrm0_root_property_group:
    scene_root_prop = get_scene_prop_root()
    vrm0_scene_root_property = scene_root_prop.vrm0_props
    return vrm0_scene_root_property


def get_vrm0_index_root_prop() -> VRMHELPER_SCENE_vrm0_ui_list_active_indexes:
    vrm0_root_property = get_vrm0_scene_root_prop()
    vrm0_index_root_prop = vrm0_root_property.active_indexes
    return vrm0_index_root_prop


def get_scene_vrm0_first_person_prop() -> VRMHELPER_SCENE_vrm0_first_person_settings:
    scene_vrm0_prop = get_vrm0_scene_root_prop()
    first_person_prop = scene_vrm0_prop.first_person_settings
    return first_person_prop


def get_scene_vrm0_blend_shape_prop() -> VRMHELPER_SCENE_vrm0_blend_shape_settings:
    scene_vrm0_prop = get_vrm0_scene_root_prop()
    blend_shape_prop = scene_vrm0_prop.blend_shape_settings
    return blend_shape_prop


def get_scene_vrm0_mtoon_stored_prop() -> VRMHELPER_SCENE_vrm0_mtoon0_stored_parameters:
    scene_vrm0_prop = get_vrm0_scene_root_prop()
    mtoon_prop = scene_vrm0_prop.mtoon0_stored_parameters
    return mtoon_prop


# ----------------------------------------------------------
#    Window Manager
# ----------------------------------------------------------
def get_vrm0_wm_root_prop() -> VRMHELPER_WM_vrm0_root_property_group:
    wm_root_prop = get_wm_prop_root()
    vrm0_wm_root_prop = wm_root_prop.vrm0_props

    return vrm0_wm_root_prop


def get_ui_vrm0_first_person_prop() -> (
    bpy.types.CollectionProperty
):  # VRMHELPER_WM_vrm0_first_person_list_items
    wm_vrm0_root_prop = get_vrm0_wm_root_prop()
    first_person_filter = wm_vrm0_root_prop.first_person_list_items4custom_filter
    return first_person_filter


def get_ui_vrm0_blend_shape_bind_prop() -> (
    bpy.types.CollectionProperty  # VRMHELPER_WM_vrm0_blend_shape_bind_list_items
):
    wm_vrm0_root_prop = get_vrm0_wm_root_prop()
    binds_filter = wm_vrm0_root_prop.blend_shape_bind_list_items4custom_filter
    return binds_filter


def get_ui_vrm0_blend_shape_material_prop() -> (
    bpy.types.CollectionProperty  # VRMHELPER_WM_vrm0_blend_shape_material_list_items
):
    wm_vrm0_root_prop = get_vrm0_wm_root_prop()
    material_filter = wm_vrm0_root_prop.blend_shape_material_list_items4custom_filter
    return material_filter


def get_wm_vrm0_material_value_prop() -> VRMHELPER_WM_vrm0_material_value_prop_names:
    wm_vrm0_prop = get_vrm0_wm_root_prop()
    material_value_prop = wm_vrm0_prop.material_value_prop
    return material_value_prop


def initialize_material_value_prop():
    material_value_prop = get_wm_vrm0_material_value_prop()
    gltf = material_value_prop.gltf_props
    gltf.clear()
    gltf_prop_names = material_value_prop.gltf_property_names
    for name in gltf_prop_names:
        target_item: bpy.types.PropertyGroup = gltf.add()
        target_item.name = name

    mtoon = material_value_prop.mtoon_props
    mtoon.clear()
    mtoon_prop_names = material_value_prop.mtoon0_property_names
    for name in mtoon_prop_names:
        target_item: bpy.types.PropertyGroup = mtoon.add()
        target_item.name = name


def get_ui_vrm0_collider_group_prop() -> bpy.types.CollectionProperty:
    """VRMHELPER_WM_vrm0_collider_group_list_items"""
    wm_vrm0_root_prop = get_vrm0_wm_root_prop()
    collider_group_filter = wm_vrm0_root_prop.collider_group_list_items4custom_filter
    return collider_group_filter


def get_ui_vrm0_spring_prop() -> bpy.types.CollectionProperty:
    """VRMHELPER_WM_vrm0_spring_bone_list_items"""
    wm_vrm0_root_prop = get_vrm0_wm_root_prop()
    spring_bone_filter = wm_vrm0_root_prop.spring_bone_list_items4custom_filter
    return spring_bone_filter


def get_ui_vrm0_linked_collider_group_prop() -> bpy.types.CollectionProperty:
    """VRMHELPER_WM_vrm0_spring_linked_collider_group_list_items"""
    wm_vrm0_root_prop = get_vrm0_wm_root_prop()
    linked_collider_group_filter = wm_vrm0_root_prop.linked_collider_group_list_items4custom_filter
    return linked_collider_group_filter


def get_ui_vrm0_operator_collider_group_prop() -> bpy.types.bpy_prop_collection:
    """VRMHELPER_WM_vrm0_operator_spring_collider_group_list_items"""
    wm_vrm0_root_prop = get_vrm0_wm_root_prop()
    collider_group_filter = wm_vrm0_root_prop.collider_group_list4operator
    return collider_group_filter


def get_ui_vrm0_operator_spring_bone_group_prop() -> bpy.types.bpy_prop_collection:
    """VRMHELPER_WM_vrm0_operator_spring_bone_group_list_items"""
    wm_vrm0_root_prop = get_vrm0_wm_root_prop()
    spring_filter = wm_vrm0_root_prop.spring_bone_group_list4operator
    return spring_filter


def get_vrm0_active_index_prop(component_type: VRM0_COMPONENT_TYPES) -> int:
    """
    引数'type'に対応したアクティブインデックスのプロパティを
    'VRMHELPER_SCENE_vrm0_ui_list_active_indexes'から取得する｡

    Parameters
    ----------
    component_type: VRM1_COMPONENT_TYPES
        UI Listアクティブインデックスを取得したいVRMコンポーネントの種類｡

    Returns
    -------
    int
        取得されたアクティブアイテムのインデックス｡

    """
    vrm0_index_prop = get_vrm0_index_root_prop()

    match component_type:
        case "FIRST_PERSON":
            list_items = get_ui_vrm0_first_person_prop()
            index = vrm0_index_prop.first_person

        case "blend_shape_bind":
            list_items = get_ui_vrm0_blend_shape_bind_prop()
            index = vrm0_index_prop.blend_shape_bind

        case "BLEND_SHAPE_MATERIAL":
            list_items = get_ui_vrm0_blend_shape_material_prop()
            index = vrm0_index_prop.blend_shape_material

        case "COLLIDER_GROUP":
            list_items = get_ui_vrm0_collider_group_prop()
            index = vrm0_index_prop.collider_group

        case "BONE_GROUP":
            list_items = get_ui_vrm0_spring_prop()
            index = vrm0_index_prop.bone_group

    active_index = evaluation_active_index_prop(list_items, index)
    return active_index


"""---------------------------------------------------------
    Get VRM1 Property Group
---------------------------------------------------------"""


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


def get_vrm1_active_index_prop(component_type: VRM1_COMPONENT_TYPES) -> int:
    """
    引数'type'に対応したアクティブインデックスのプロパティを
    'VRMHELPER_SCENE_vrm1_ui_list_active_indexes'から取得する｡

    Parameters
    ----------
    component_type: VRM1_COMPONENT_TYPES
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


def get_scene_vrm1_first_person_prop() -> VRMHELPER_SCENE_vrm1_first_person_settings:
    scene_vrm1_prop = get_vrm1_scene_root_prop()
    first_person_prop = scene_vrm1_prop.first_person_settings
    return first_person_prop


def get_scene_vrm1_expression_prop() -> VRMHELPER_SCENE_vrm1_expression_settings:
    scene_vrm1_prop = get_vrm1_scene_root_prop()
    expression_prop = scene_vrm1_prop.expression_settings
    return expression_prop


def get_scene_vrm1_collider_prop() -> VRMHELPER_SCENE_vrm1_collider_settings:
    scene_vrm1_prop = get_vrm1_scene_root_prop()
    collider_prop = scene_vrm1_prop.collider_settings
    return collider_prop


def detect_collider_shape_type(shape_type: str) -> int:
    """
    引数'shape_type'に応じてint型のステータスを返す｡

    Parameters
    ----------
    shape_type : str
        判定を行なうコライダーのシェイプタイプ｡

    Returns
    -------
    int
        コライダーのシェイプに応じたステータス｡
        -1 : Error
         0 : Sphere
         1 : Capsule

    """
    match shape_type:
        case "Sphere":
            return 0

        case "Capsule":
            return 1

        case _:
            logger.debug("Invailed Shape Type")
            return -1


def find_collider_from_empty_name(
    colliders: Any, empty_name: str
) -> Optional[ReferenceVrm1ColliderPropertyGroup]:
    """
    'colliders'で受け取ったVRM Addonのコライダーコレクションプロパティグループのうち､
    参照オブジェクトの名前が引数'empty_name'と一致するものを判定してそれを返す｡

    Parameters
    ----------
    colliders : Any
        処理対象のColliderコレクションプロパティ｡

    empty_name : str
        判定のソースとなる文字列

    Returns
    -------
    Optional[ReferenceVrm1ColliderPropertyGroup]
        名前が一致したコライダーが存在すればそれを返す｡
    """

    if not (temp := [i for i in colliders if i.bpy_object.name == empty_name]):
        return

    collider = temp[0]
    return collider


def get_scene_vrm1_collider_group_prop() -> VRMHELPER_SCENE_vrm1_collider_group_settings:
    scene_vrm1_prop = get_vrm1_scene_root_prop()
    collider_group_prop = scene_vrm1_prop.collider_group_settings
    return collider_group_prop


def get_scene_vrm1_spring_prop() -> VRMHELPER_SCENE_vrm1_spring_settings:
    scene_vrm1_prop = get_vrm1_scene_root_prop()
    spring_prop = scene_vrm1_prop.spring_settings
    return spring_prop


def get_scene_vrm1_constraint_prop() -> VRMHELPER_SCENE_vrm1_constraint_settings:
    scene_vrm1_prop = get_vrm1_scene_root_prop()
    constraint_prop = scene_vrm1_prop.constraint_settings
    return constraint_prop


def get_scene_vrm1_mtoon_stored_prop() -> VRMHELPER_SCENE_vrm1_mtoon1_stored_parameters:
    scene_vrm1_prop = get_vrm1_scene_root_prop()
    mtoon_stored_prop = scene_vrm1_prop.mtoon1_stored_parameters
    return mtoon_stored_prop


# ----------------------------------------------------------
#    Window Manager
# ----------------------------------------------------------
def get_vrm1_wm_root_prop() -> VRMHELPER_WM_vrm1_root_property_group:
    wm_root_prop = get_wm_prop_root()
    vrm1_wm_root_prop = wm_root_prop.vrm1_props

    return vrm1_wm_root_prop


def get_wm_vrm1_constraint_prop() -> VRMHELPER_WM_vrm1_constraint_properties:
    wm_vrm1_prop = get_vrm1_wm_root_prop()
    constraint_prop = wm_vrm1_prop.constraint_prop
    return constraint_prop


def get_ui_vrm1_first_person_prop() -> (
    bpy.types.bpy_prop_collection
):  # VRMHELPER_WM_vrm1_first_person_list_items
    wm_vrm1_root_prop = get_vrm1_wm_root_prop()
    first_person_filter = wm_vrm1_root_prop.first_person_list_items4custom_filter
    return first_person_filter


def get_ui_vrm1_expression_prop() -> bpy.types.bpy_prop_collection:  # VRMHELPER_WM_vrm1_expression_list_items
    wm_vrm1_root_prop = get_vrm1_wm_root_prop()
    expression_filter = wm_vrm1_root_prop.expression_list_items4custom_filter
    return expression_filter


def get_ui_vrm1_expression_morph_prop() -> (
    bpy.types.bpy_prop_collection
):  # VRMHELPER_WM_vrm1_expression_morph_list_items
    wm_vrm1_root_prop = get_vrm1_wm_root_prop()
    expression_morph_filter = wm_vrm1_root_prop.expression_morph_list_items4custom_filter
    return expression_morph_filter


def get_ui_vrm1_expression_material_prop() -> (
    bpy.types.bpy_prop_collection
):  # VRMHELPER_WM_vrm1_expression_material_list_items
    wm_vrm1_root_prop = get_vrm1_wm_root_prop()
    expression_material_filter = wm_vrm1_root_prop.expression_material_list_items4custom_filter
    return expression_material_filter


def get_ui_vrm1_collider_prop() -> bpy.types.bpy_prop_collection:  # VRMHELPER_WM_vrm1_collider_list_items
    wm_vrm1_root_prop = get_vrm1_wm_root_prop()
    collider_filter = wm_vrm1_root_prop.collider_list_items4custom_filter
    return collider_filter


def get_ui_vrm1_collider_group_prop() -> (
    bpy.types.bpy_prop_collection
):  # VRMHELPER_WM_vrm1_collider_group_list_items
    wm_vrm1_root_prop = get_vrm1_wm_root_prop()
    collider_group_filter = wm_vrm1_root_prop.collider_group_list_items4custom_filter
    return collider_group_filter


def get_ui_vrm1_spring_prop() -> bpy.types.bpy_prop_collection:  # VRMHELPER_WM_vrm1_spring_list_items
    wm_vrm1_root_prop = get_vrm1_wm_root_prop()
    spring_filter = wm_vrm1_root_prop.spring_list_items4custom_filter
    return spring_filter


def get_ui_vrm1_operator_collider_group_prop() -> (
    bpy.types.bpy_prop_collection
):  # VRMHELPER_WM_vrm1_operator_spring_collider_group_list_items
    wm_vrm1_root_prop = get_vrm1_wm_root_prop()
    collider_group_filter = wm_vrm1_root_prop.collider_group_list4operator
    return collider_group_filter


def get_ui_vrm1_operator_spring_prop() -> (
    bpy.types.bpy_prop_collection
):  # VRMHELPER_WM_vrm1_operator_spring_list_items
    wm_vrm1_root_prop = get_vrm1_wm_root_prop()
    spring_filter = wm_vrm1_root_prop.spring_list4operator
    return spring_filter


def get_ui_vrm1_constraint_prop() -> bpy.types.bpy_prop_collection:  # VRMHELPER_WM_vrm1_constraint_list_items
    wm_vrm1_root_prop = get_vrm1_wm_root_prop()
    constraint_filter = wm_vrm1_root_prop.constraint_list_items4custom_filter
    return constraint_filter


"""---------------------------------------------------------
------------------------------------------------------------
    Resiter Target
------------------------------------------------------------
---------------------------------------------------------"""
CLASSES = (
    # ----------------------------------------------------------
    #    Scene
    # ----------------------------------------------------------
    VRMHELPER_SCENE_basic_settings,
    VRMHELPER_SCENE_misc_tools_settings,
    # ---------------------------------------------------------------------------------
    VRMHELPER_SCENE_vrm0_first_person_settings,
    VRMHELPER_SCENE_vrm0_blend_shape_settings,
    VRMHELPER_SCENE_vrm0_mtoon0_stored_parameters,
    VRMHELPER_SCENE_vrm0_collider_group_settings,
    VRMHELPER_SCENE_vrm0_spring_settings,
    VRMHELPER_SCENE_vrm0_ui_list_active_indexes,
    VRMHELPER_SCENE_vrm0_root_property_group,
    # ---------------------------------------------------------------------------------
    VRMHELPER_SCENE_vrm1_first_person_settings,
    VRMHELPER_SCENE_vrm1_expression_settings,
    VRMHELPER_SCENE_vrm1_collider_settings,
    VRMHELPER_SCENE_vrm1_collider_group_settings,
    VRMHELPER_SCENE_vrm1_spring_settings,
    VRMHELPER_SCENE_vrm1_constraint_settings,
    VRMHELPER_SCENE_vrm1_ui_list_active_indexes,
    VRMHELPER_SCENE_vrm1_mtoon1_stored_parameters,
    VRMHELPER_SCENE_vrm1_root_property_group,
    # ---------------------------------------------------------------------------------
    VRMHELPER_SCENE_root_property_group,
    # ----------------------------------------------------------
    #    Window Manager
    # ----------------------------------------------------------
    VRMHELPER_WM_operator_spring_bone_group_list_items,
    # ---------------------------------------------------------------------------------
    VRMHELPER_WM_vrm0_first_person_list_items,
    VRMHELPER_WM_vrm0_blend_shape_bind_list_items,
    VRMHELPER_WM_vrm0_blend_shape_material_list_items,
    VRMHELPER_WM_vrm0_material_value_prop_names,
    VRMHELPER_WM_vrm0_collider_group_list_items,
    VRMHELPER_WM_vrm0_spring_bone_list_items,
    VRMHELPER_WM_vrm0_spring_linked_collider_group_list_items,
    VRMHELPER_WM_vrm0_operator_spring_collider_group_list_items,
    VRMHELPER_WM_vrm0_operator_spring_bone_group_list_items,
    VRMHELPER_WM_vrm0_root_property_group,
    # ---------------------------------------------------------------------------------
    VRMHELPER_WM_vrm1_first_person_list_items,
    VRMHELPER_WM_vrm1_expression_list_items,
    VRMHELPER_WM_vrm1_expression_morph_list_items,
    VRMHELPER_WM_vrm1_expression_material_list_items,
    VRMHELPER_WM_vrm1_collider_list_items,
    VRMHELPER_WM_vrm1_collider_group_list_items,
    VRMHELPER_WM_vrm1_spring_list_items,
    VRMHELPER_WM_vrm1_operator_spring_collider_group_list_items,
    VRMHELPER_WM_vrm1_operator_spring_list_items,
    VRMHELPER_WM_vrm1_constraint_properties,
    VRMHELPER_WM_vrm1_constraint_list_items,
    VRMHELPER_WM_vrm1_root_property_group,
    # ---------------------------------------------------------------------------------
    VRMHELPER_WM_root_property_group,
)
