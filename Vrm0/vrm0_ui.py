if "bpy" in locals():
    import importlib

    reloadable_modules = [
        "preparation_logger",
        "property_groups",
        "utils_common",
        "operators",
        "utils_vrm0_first_person",
        "utils_vrm0_blend_shape",
        "utils_vrm0_spring",
        "vrm0_operators",
    ]

    for module in reloadable_modules:
        if module in locals():
            importlib.reload(locals()[module])

else:
    from ..Logging import preparation_logger
    from .. import property_groups
    from .. import utils_common
    from .. import operators
    from . import utils_vrm0_first_person
    from . import utils_vrm0_blend_shape
    from . import utils_vrm0_spring
    from . import vrm0_operators


import bpy


from ..addon_classes import (
    ReferenceBonePropertyGroup,
    ReferenceVrm0BlendShapeGroupPropertyGroup,
    ReferenceVrm0BlendShapeBindPropertyGroup,
    ReferenceVrm0MaterialValueBindPropertyGroup,
    ReferencerVrm0SecondaryAnimationColliderPropertyGroup,
    ReferenceVrm0SecondaryAnimationGroupPropertyGroup,
    ReferenceVrm0SecondaryAnimationColliderGroupPropertyGroup,
    # ----------------------------------------------------------
    VRMHELPER_UL_base,
)

from ..addon_constants import (
    PRESET_BLEND_SHAPE_NAME_DICT,
    BLEND_SHAPE_ICON_DICT,
)

from ..property_groups import (
    VRMHELPER_SCENE_vrm0_blend_shape_settings,
    VRMHELPER_SCENE_vrm0_spring_settings,
    VRMHELPER_SCENE_vrm0_ui_list_active_indexes,
    # ---------------------------------------------------------------------------------
    VRMHELPER_WM_vrm0_first_person_list_items,
    VRMHELPER_WM_vrm0_blend_shape_bind_list_items,
    VRMHELPER_WM_vrm0_blend_shape_material_list_items,
    VRMHELPER_WM_vrm0_collider_group_list_items,
    VRMHELPER_WM_vrm0_spring_bone_list_items,
    VRMHELPER_WM_vrm0_spring_linked_collider_group_list_items,
    # ---------------------------------------------------------------------------------
    get_target_armature,
    get_target_armature_data,
    get_vrm0_scene_root_prop,
    get_wm_vrm0_material_value_prop,
    initialize_material_value_prop,
    get_vrm0_wm_root_prop,
    get_ui_vrm0_collider_group_prop,
    get_ui_vrm0_spring_prop,
)

from ..utils_common import (
    get_properties_to_dict,
    define_ui_list_rows,
    set_properties_to_from_dict,
)

from ..utils_vrm_base import (
    is_existing_target_armature,
    check_addon_mode,
    get_vrm_extension_root_property,
    get_vrm0_extension_blend_shape,
    get_vrm0_extension_active_blend_shape_group,
    get_vrm0_extension_secondary_animation,
    get_vrm0_extension_collider_group,
    get_vrm0_extension_spring_bone_group,
)


from .utils_vrm0_first_person import (
    vrm0_add_items2annotation_ui_list,
    vrm0_search_same_name_mesh_annotation,
)

from .utils_vrm0_blend_shape import (
    get_scene_vrm0_mtoon_stored_prop,
    vrm0_get_source_vrm0_blend_shape_bind4ui_list,
    vrm0_get_source_vrm0_blend_shape_material4ui_list,
    get_ui_vrm0_blend_shape_bind_prop,
    get_ui_vrm0_blend_shape_material_prop,
    vrm0_add_items2blend_shape_bind_ui_list,
    vrm0_add_items2blend_shape_material_ui_list,
    get_active_blend_shape,
)

from .utils_vrm0_spring import (
    vrm0_add_items2collider_group_ui_list,
    vrm0_add_items2spring_ui_list,
    vrm0_get_active_list_item_in_spring,
    vrm0_add_items2linked_collider_group_ui_list,
)


from ..operators import (
    VRMHELPER_OT_empty_operator,
    VRMHELPER_OT_reset_shape_keys_on_selected_objects,
)


from .vrm0_operators import (
    # ----------------------------------------------------------
    #    First Person
    # ----------------------------------------------------------
    VRMHELPER_OT_vrm0_first_person_set_annotation,
    VRMHELPER_OT_vrm0_first_person_remove_annotation_from_list,
    VRMHELPER_OT_vrm0_first_person_remove_annotation_from_select_objects,
    VRMHELPER_OT_vrm0_first_person_clear_annotation,
    # ----------------------------------------------------------
    #    Blend Shape
    # ----------------------------------------------------------
    VRMHELPER_OT_0_blend_shape_create_blend_shape,
    VRMHELPER_OT_0_blend_shape_remove_blend_shape,
    VRMHELPER_OT_0_blend_shape_clear_blend_shape,
    VRMHELPER_OT_vrm0_blend_shape_assign_blend_shape_to_scene,
    VRMHELPER_OT_vrm0_blend_shape_bind_or_material_create,
    VRMHELPER_OT_vrm0_blend_shape_bind_or_material_remove,
    VRMHELPER_OT_vrm0_blend_shape_bind_or_material_clear,
    VRMHELPER_OT_vrm0_blend_shape_change_bind_material,
    VRMHELPER_OT_vrm0_blend_shape_store_mtoon0_parameters,
    VRMHELPER_OT_vrm0_blend_shape_discard_stored_mtoon0_parameters,
    VRMHELPER_OT_vrm0_blend_shape_restore_mtoon0_parameters,
    VRMHELPER_OT_vrm0_blend_shape_set_both_binds_from_scene,
    VRMHELPER_OT_vrm0_blend_shape_restore_initial_parameters,
    # ----------------------------------------------------------
    #    Collider Group
    # ----------------------------------------------------------
    VRMHELPER_OT_vrm0_collider_group_add_group,
    VRMHELPER_OT_vrm0_collider_group_remove_active_group,
    VRMHELPER_OT_vrm0_collider_group_clear_group,
    VRMHELPER_OT_vrm0_collider_group_add_collider,
    VRMHELPER_OT_vrm0_collider_group_remove_active_collider,
    VRMHELPER_OT_vrm0_collider_group_clear_colliders,
    VRMHELPER_OT_vrm0_collider_create_from_bone,
    VRMHELPER_OT_vrm0_collider_remove_from_empty,
    # ----------------------------------------------------------
    #    Spring Bone Group
    # ----------------------------------------------------------
    VRMHELPER_OT_vrm0_spring_add_bone_group,
    VRMHELPER_OT_vrm0_spring_remove_bone_group,
    VRMHELPER_OT_vrm0_spring_clear_bone_group,
    VRMHELPER_OT_vrm0_spring_add_bone,
    VRMHELPER_OT_vrm0_spring_remove_bone,
    VRMHELPER_OT_vrm0_spring_clear_bone,
    VRMHELPER_OT_vrm0_spring_add_bone_group_from_source,
    VRMHELPER_OT_vrm0_spring_remove_empty_joint_slots,
    # ----------------------------------------------------------
    #    Spring Bone Group's Collider Group
    # ----------------------------------------------------------
    VRMHELPER_OT_vrm0_spring_add_linked_collider_group,
    VRMHELPER_OT_vrm0_spring_remove_linked_collider_group,
    VRMHELPER_OT_vrm0_spring_clear_linked_collider_group,
    VRMHELPER_OT_vrm0_spring_register_linked_collider_group,
)

"""
from .vrm0_operators import (
    # ----------------------------------------------------------
    #    First Person
    # ----------------------------------------------------------
)
"""

"""---------------------------------------------------------
------------------------------------------------------------
    Logger
------------------------------------------------------------
---------------------------------------------------------"""
from ..Logging.preparation_logger import preparating_logger

logger = preparating_logger(__name__)
#######################################################

"""---------------------------------------------------------
------------------------------------------------------------
    Panel
------------------------------------------------------------
---------------------------------------------------------"""
"""---------------------------------------------------------
    First Person
---------------------------------------------------------"""


def draw_panel_vrm0_first_person(self, context, layout: bpy.types.UILayout):
    """
    VRM0のFirst Personに関する設定/オペレーターを描画する
    """

    # Property Groupの取得｡
    wm_vrm0_prop = get_vrm0_wm_root_prop()
    scene_vrm0_prop = get_vrm0_scene_root_prop()
    first_person_prop = scene_vrm0_prop.first_person_settings

    # ----------------------------------------------------------
    #    UI描画
    # ----------------------------------------------------------
    # UI Listに表示するアイテムをコレクションプロパティに追加し､アイテム数を取得する｡
    rows = vrm0_add_items2annotation_ui_list()

    row = layout.row()
    row.prop(first_person_prop, "is_filtering_by_type", text="Filtering by Selected Type")
    row = layout.row()
    row.scale_y = 1.4
    row.prop(first_person_prop, "annotation_type", text=" ", expand=True)
    row = layout.row()
    row.template_list(
        "VRMHELPER_UL_vrm0_first_person_list",
        "",
        wm_vrm0_prop,
        "first_person_list_items4custom_filter",
        scene_vrm0_prop.active_indexes,
        "first_person",
        rows=define_ui_list_rows(rows),
    )
    col = row.column()
    col.operator(
        VRMHELPER_OT_vrm0_first_person_remove_annotation_from_list.bl_idname,
        text="",
        icon="REMOVE",
    )
    col.operator(
        VRMHELPER_OT_vrm0_first_person_clear_annotation.bl_idname,
        text="",
        icon="PANEL_CLOSE",
    )

    layout.separator()
    col = layout.column(align=True)
    col.operator(
        VRMHELPER_OT_vrm0_first_person_set_annotation.bl_idname,
        text="Set from Selected Objects",
        icon="IMPORT",
    )
    col.operator(
        VRMHELPER_OT_vrm0_first_person_remove_annotation_from_select_objects.bl_idname,
        text="Remove by Selected Objects",
        icon="EXPORT",
    )


class VRMHELPER_UL_vrm0_first_person_list(bpy.types.UIList):
    """First Person Mesh Annotationを表示するUI List"""

    def draw_item(
        self,
        context,
        layout,
        data,
        item: VRMHELPER_WM_vrm0_first_person_list_items,
        icon,
        active_data,
        active_propname,
        index,
    ):
        annotation = vrm0_search_same_name_mesh_annotation(item.name)

        # リスト内の項目のレイアウトを定義する｡
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            sp = layout.split(align=True, factor=0.7)
            sp.label(text=annotation.mesh.mesh_object_name, icon="OUTLINER_OB_MESH")
            sp.prop(annotation, "first_person_flag", text="")


"""---------------------------------------------------------
    Blend Shape
---------------------------------------------------------"""


def draw_panel_vrm0_blend_shape(self, context, layout: bpy.types.UILayout):
    """
    VRM0のBlend Shapeに関する設定/オペレーターを描画する
    """

    # Property Groupの取得｡
    wm_vrm0_prop = get_vrm0_wm_root_prop()
    scene_vrm0_prop = get_vrm0_scene_root_prop()
    active_indexes: VRMHELPER_SCENE_vrm0_ui_list_active_indexes = scene_vrm0_prop.active_indexes
    blend_shape_prop: VRMHELPER_SCENE_vrm0_blend_shape_settings = scene_vrm0_prop.blend_shape_settings
    blend_shape_master = get_vrm0_extension_blend_shape()
    blend_shapes = blend_shape_master.blend_shape_groups
    active_blend_shape = get_active_blend_shape()

    # UI Listに表示するアイテムをコレクションプロパティに追加し､アイテム数を取得する｡
    rows = len(blend_shapes)

    # ----------------------------------------------------------
    #    登録されているBlend Shapeのリスト描画
    # ----------------------------------------------------------
    row = layout.row()
    row.template_list(
        "VRMHELPER_UL_vrm0_blend_shape_list",
        "",
        blend_shape_master,
        "blend_shape_groups",
        blend_shape_master,
        "active_blend_shape_group_index",
        rows=define_ui_list_rows(rows),
    )

    col_list = row.column(align=True)
    # col_list.separator(factor=0.5)
    col_list.operator(VRMHELPER_OT_0_blend_shape_create_blend_shape.bl_idname, text="", icon="ADD")
    col_list.operator(VRMHELPER_OT_0_blend_shape_remove_blend_shape.bl_idname, text="", icon="REMOVE")
    col_list.operator(
        VRMHELPER_OT_0_blend_shape_clear_blend_shape.bl_idname,
        text="",
        icon="PANEL_CLOSE",
    )
    layout.operator(
        VRMHELPER_OT_vrm0_blend_shape_assign_blend_shape_to_scene.bl_idname,
        text="Assign Active Blen Shape",
    )

    # ----------------------------------------------------------
    #    選択された編集対象のリストとオペレーターを描画
    # ----------------------------------------------------------
    box = layout.box()
    box.label(text="Editing Target:")
    row = box.row(align=True)
    row.prop(blend_shape_prop, "editing_target", text=" ", expand=True)

    match blend_shape_prop.editing_target:
        ######################################
        # Binds
        ######################################
        case "BIND":
            rows = vrm0_add_items2blend_shape_bind_ui_list()
            row = box.row(align=True)
            row.template_list(
                "VRMHELPER_UL_vrm0_blend_shape_bind_list",
                "",
                wm_vrm0_prop,
                "blend_shape_bind_list_items4custom_filter",
                active_indexes,
                "blend_shape_bind",
                rows=define_ui_list_rows(rows),
            )

            # アクティブアイテムのBind設定用フォーム
            if binds := get_ui_vrm0_blend_shape_bind_prop():
                current_index = active_indexes.blend_shape_bind
                active_item: VRMHELPER_WM_vrm0_blend_shape_bind_list_items = binds[current_index]
                if active_item:
                    if active_item.item_type[1]:
                        active_bind = active_blend_shape.binds[active_item.bind_index]
                        box_bind_mesh = box.box()
                        col_box_bind_mesh = box_bind_mesh.column(align=True)
                        col_box_bind_mesh.label(text="Active Bind's Mesh:")
                        col_box_bind_mesh.prop_search(
                            active_bind.mesh,
                            "mesh_object_name",
                            context.scene.vrm_addon_extension,
                            "mesh_object_names",
                            text="",
                            icon="OUTLINER_OB_MESH",
                        )

        ######################################
        # Material Value
        ######################################
        case "MATERIAL":
            rows = vrm0_add_items2blend_shape_material_ui_list()
            row = box.row(align=True)
            row.template_list(
                "VRMHELPER_UL_vrm0_blend_shape_material_list",
                "",
                wm_vrm0_prop,
                "blend_shape_material_list_items4custom_filter",
                active_indexes,
                "blend_shape_material",
                rows=define_ui_list_rows(rows),
            )

            # アクティブなMaterial ValueのTarget Material設定用フォーム
            if binds := get_ui_vrm0_blend_shape_material_prop():
                current_index = active_indexes.blend_shape_material
                active_item: VRMHELPER_WM_vrm0_blend_shape_material_list_items = binds[current_index]

                # アクティブアイテムが 'Blank'以外のラベル､Material Color, UV Coordinateであるかを判定する｡
                if active_item:
                    if active_item.value_index > -1:
                        active_material_value = active_blend_shape.material_values[active_item.value_index]
                    match tuple(active_item.item_type):
                        case (1, 0, 0, 0) | (
                            1,
                            0,
                            0,
                            1,
                        ) if active_item.name != "Blank":  # Label Exclude 'Blank'
                            box_bind_material = box.box()
                            box_bind_material.label(text=f"Binded Material : {active_item.name}")
                            box_bind_material.operator(
                                VRMHELPER_OT_vrm0_blend_shape_change_bind_material.bl_idname,
                                text="Change Bind Material",
                                icon="MATERIAL",
                            )

                        case (0, 1, 0, 0) | (0, 1, 0, 0) | (0, 0, 1, 0) | (0, 0, 0, 1):
                            box_bind_material = box.box()
                            col_box_bind_material = box_bind_material.column(align=True)
                            col_box_bind_material.label(text="Active Bind's Material:")
                            col_box_bind_material.prop_search(
                                active_material_value,
                                "material",
                                bpy.data,
                                "materials",
                                text="",
                                icon="MATERIAL",
                            )

    # 'Blank'のラベル以外であれば追加のプロパティを描画する｡
    editing_target = blend_shape_prop.editing_target
    col_button = row.column(align=True)
    op = col_button.operator(
        VRMHELPER_OT_vrm0_blend_shape_bind_or_material_create.bl_idname,
        text="",
        icon="ADD",
    )
    op.mode = editing_target
    op = col_button.operator(
        VRMHELPER_OT_vrm0_blend_shape_bind_or_material_remove.bl_idname,
        text="",
        icon="REMOVE",
    )
    op.mode = editing_target
    op = col_button.operator(
        VRMHELPER_OT_vrm0_blend_shape_bind_or_material_clear.bl_idname,
        text="",
        icon="PANEL_CLOSE",
    )
    op.mode = editing_target

    # オペレーターの描画
    box.separator()
    box_op_mtoon = box.box()
    col = box_op_mtoon.column(align=True)
    col.scale_y = 1.2
    col.operator(
        VRMHELPER_OT_vrm0_blend_shape_store_mtoon0_parameters.bl_idname,
        text="Store MToon Current Values",
        icon="IMPORT",
    )
    col.operator(
        VRMHELPER_OT_vrm0_blend_shape_discard_stored_mtoon0_parameters.bl_idname,
        text="Discard stored MToon Values",
        icon="EXPORT",
    )

    box_op_bottom = box.box()
    col = box_op_bottom.column(align=True)
    col.scale_y = 1.2
    col.operator(
        VRMHELPER_OT_vrm0_blend_shape_set_both_binds_from_scene.bl_idname,
        text="Set Binds from Scene",
    )

    col = box_op_bottom.column(align=True)
    col.scale_y = 1.2
    col.operator(
        VRMHELPER_OT_reset_shape_keys_on_selected_objects.bl_idname,
        text="Reset Shape Kye on Selected",
        icon="SHAPEKEY_DATA",
    )
    col.operator(
        VRMHELPER_OT_vrm0_blend_shape_restore_mtoon0_parameters.bl_idname,
        text="Restore MToon Initial Values",
        icon="NODE_MATERIAL",
    )
    col.operator(
        VRMHELPER_OT_vrm0_blend_shape_restore_initial_parameters.bl_idname,
        text="Reset Bind's All Values",
        icon="RECOVER_LAST",
    )


"""---------------------------------------------------------
    Secondary Animation
---------------------------------------------------------"""


def draw_panel_vrm0_collider_group(self, context, layout: bpy.types.UILayout):
    """
    VRM0のCollider Groupsに関する設定/オペレーターを描画する
    """

    # Property Groupの取得｡
    wm_vrm0_prop = get_vrm0_wm_root_prop()
    scene_vrm0_prop = get_vrm0_scene_root_prop()
    cg_prop = scene_vrm0_prop.collider_group_settings
    active_indexes: VRMHELPER_SCENE_vrm0_ui_list_active_indexes = scene_vrm0_prop.active_indexes

    # UI Listに表示するアイテムをコレクションプロパティに追加し､アイテム数を取得する｡
    rows = vrm0_add_items2collider_group_ui_list()

    # ----------------------------------------------------------
    #    登録されているCollider Groupのリスト描画
    # ----------------------------------------------------------
    layout.prop(cg_prop, "is_additive_selecting", text="Additive Select")
    row = layout.row()
    row.template_list(
        VRMHELPER_UL_vrm0_collider_group_list.__name__,
        "",
        wm_vrm0_prop,
        "collider_group_list_items4custom_filter",
        scene_vrm0_prop.active_indexes,
        "collider_group",
        rows=define_ui_list_rows(rows),
    )

    col_list = row.column(align=True)
    # コライダーグループの作成/削除を行うオペレーター
    col_list.label(text="", icon="OVERLAY")
    col_list.operator(VRMHELPER_OT_vrm0_collider_group_add_group.bl_idname, text="", icon="ADD")
    col_list.operator(VRMHELPER_OT_vrm0_collider_group_remove_active_group.bl_idname, text="", icon="REMOVE")
    col_list.operator(VRMHELPER_OT_vrm0_collider_group_clear_group.bl_idname, text="", icon="PANEL_CLOSE")
    # ---------------------------------------------------------------------------------
    # コライダーの削除を行うオペレーター
    col_list.separator(factor=2.0)
    col_list.label(text="", icon="MESH_UVSPHERE")
    col_list.operator(VRMHELPER_OT_vrm0_collider_group_add_collider.bl_idname, text="", icon="ADD")
    col_list.operator(
        VRMHELPER_OT_vrm0_collider_group_remove_active_collider.bl_idname, text="", icon="REMOVE"
    )
    col_list.operator(VRMHELPER_OT_vrm0_collider_group_clear_colliders.bl_idname, text="", icon="PANEL_CLOSE")

    box_operator_prop = layout.box()
    box_operator_prop.prop(cg_prop, "creating_collider_radius")

    if items_list := get_ui_vrm0_collider_group_prop():
        box = layout.box()

        active_item: VRMHELPER_WM_vrm0_collider_group_list_items = items_list[active_indexes.collider_group]
        match tuple(active_item.item_type):
            case (1, 0, 0, 0):
                pass
            case (0, 1, 0, 0):
                box_prop = box.box()
                box_prop.prop(cg_prop, "active_collider_radius", text="Active Collider Radius")
            case (0, 0, 1, 0):
                box_prop = box.box()
                target_armature_data = get_target_armature_data()
                collider_groups = get_vrm0_extension_collider_group()
                active_collider_group: ReferenceVrm0SecondaryAnimationColliderGroupPropertyGroup = (
                    collider_groups[active_item.group_index]
                )
                box_prop.prop_search(
                    active_collider_group.node,
                    "bone_name",
                    target_armature_data,
                    "bones",
                    text="Parent Bone",
                )
                box_prop.prop(cg_prop, "active_collider_radius", text="Active Collider Radius")

            case (0, 0, 0, 1):
                box_prop = box.box()
                collider_groups = get_vrm0_extension_collider_group()
                active_collider_group = collider_groups[active_item.group_index]
                active_collider: ReferencerVrm0SecondaryAnimationColliderPropertyGroup = (
                    active_collider_group.colliders[active_item.collider_index]
                )
                box_prop.label(text="Active Collider's Parameters")
                box_prop.prop(active_collider.bpy_object, "location", text="Location")
                # box_prop.prop(active_collider.bpy_object, "empty_display_size", text="Collider Size")
                box_prop.prop(cg_prop, "active_collider_radius", text="Active Collider Radius")

        box_op = box.box()
        op = box_op.operator(VRMHELPER_OT_vrm0_collider_create_from_bone.bl_idname)
        op.collider_radius = 0.08
        box_op.operator(VRMHELPER_OT_vrm0_collider_remove_from_empty.bl_idname)


def draw_panel_vrm0_spring(self, context, layout: bpy.types.UILayout):
    """
    VRM0のSpring Bone Group に関する設定/オペレーターを描画する
    """
    # Property Groupの取得｡
    target_armature = get_target_armature()
    wm_vrm0_prop = get_vrm0_wm_root_prop()
    scene_vrm0_prop = get_vrm0_scene_root_prop()
    active_indexes: VRMHELPER_SCENE_vrm0_ui_list_active_indexes = scene_vrm0_prop.active_indexes
    spring_prop: VRMHELPER_SCENE_vrm0_spring_settings = scene_vrm0_prop.spring_settings

    # UI Listに表示するアイテムをコレクションプロパティに追加し､アイテム数を取得する｡
    rows = vrm0_add_items2spring_ui_list()

    # ----------------------------------------------------------
    #    登録されているBlend Shapeのリスト描画
    # ----------------------------------------------------------
    row = layout.row()
    row.template_list(
        VRMHELPER_UL_vrm0_spring_list.__name__,
        "",
        wm_vrm0_prop,
        "spring_bone_list_items4custom_filter",
        scene_vrm0_prop.active_indexes,
        "bone_group",
        rows=define_ui_list_rows(rows),
    )

    # ボーンの作成/削除を行うオペレーター
    col_list = row.column(align=True)
    col_list.label(text="", icon="GROUP_BONE")
    col_list.operator(VRMHELPER_OT_vrm0_spring_add_bone_group.bl_idname, text="", icon="ADD")
    col_list.operator(VRMHELPER_OT_vrm0_spring_remove_bone_group.bl_idname, text="", icon="REMOVE")
    col_list.operator(VRMHELPER_OT_vrm0_spring_clear_bone_group.bl_idname, text="", icon="PANEL_CLOSE")
    col_list.separator(factor=2.0)
    col_list.label(text="", icon="BONE_DATA")
    col_list.operator(VRMHELPER_OT_vrm0_spring_add_bone.bl_idname, text="", icon="ADD")
    col_list.operator(VRMHELPER_OT_vrm0_spring_remove_bone.bl_idname, text="", icon="REMOVE")
    col_list.operator(VRMHELPER_OT_vrm0_spring_clear_bone.bl_idname, text="", icon="PANEL_CLOSE")

    layout.operator(VRMHELPER_OT_vrm0_spring_remove_empty_joint_slots.bl_idname)

    box = layout.box()
    if active_item := vrm0_get_active_list_item_in_spring():
        bone_groups = get_vrm0_extension_spring_bone_group()
        bone_group: ReferenceVrm0SecondaryAnimationGroupPropertyGroup = bone_groups[
            active_item.item_indexes[0]
        ]

        row = box.row()
        row.scale_y = 1.2
        row.label(text=f"Active Bone Group Parameters")
        box.prop(bone_group, "comment", icon="BOOKMARKS")
        box.prop_search(
            bone_group.center,
            "bone_name",
            target_armature.data,
            "bones",
            text="Center",
            icon="PIVOT_MEDIAN",
        )
        # TODO : Stiffnessに修正されたら対応する｡
        box.prop(bone_group, "stiffiness", text="stiffness")
        box.prop(bone_group, "drag_force", text="Drag Force")
        box.prop(bone_group, "hit_radius", text="Hit Radius")
        box.prop(bone_group, "gravity_dir", text="Gravity Dir")
        box.prop(bone_group, "gravity_power", text="Gravity Power")

    box_ope = layout.box()
    op: VRMHELPER_OT_vrm0_spring_add_bone_group_from_source
    op = box_ope.operator(
        VRMHELPER_OT_vrm0_spring_add_bone_group_from_source.bl_idname,
        text="Create From Selected Bones",
        icon="BONE_DATA",
    )
    op.source_type = "SELECT"
    op = box_ope.operator(
        VRMHELPER_OT_vrm0_spring_add_bone_group_from_source.bl_idname,
        text="Create From Bone Group",
        icon="GROUP_BONE",
    )
    op.source_type = "BONE_GROUP"

    # Bone GroupにリンクされたCollider Groupのリストを描画｡
    if (rows := vrm0_add_items2linked_collider_group_ui_list()) != None:
        # UIリストでアクティブなBone Groupを取得する｡
        active_bone_group = vrm0_get_active_list_item_in_spring()
        bone_group_name = active_bone_group.bone_group_name
        layout.separator(factor=1.0)
        box_cg = layout.box()
        # リンクされているSpring Bone GroupのCommentを表示する｡
        row = box_cg.row()
        row.scale_y = 1.4
        row.label(text=f"Selected Bone Group : {bone_group_name}", icon="BOOKMARKS")

        # Linked Collider Groupのリストを表示する｡
        row = box_cg.row()
        row.template_list(
            VRMHELPER_UL_vrm0_linked_collider_grouplist.__name__,
            "",
            wm_vrm0_prop,
            "linked_collider_group_list_items4custom_filter",
            scene_vrm0_prop.active_indexes,
            "linked_collider_group",
            rows=define_ui_list_rows(rows),
        )
        # Linked Collider Groupの作成/削除用オペレーター
        col_list = row.column(align=True)
        col_list.label(text="", icon="OVERLAY")
        col_list.operator(VRMHELPER_OT_vrm0_spring_add_linked_collider_group.bl_idname, text="", icon="ADD")
        col_list.operator(
            VRMHELPER_OT_vrm0_spring_remove_linked_collider_group.bl_idname, text="", icon="REMOVE"
        )
        col_list.operator(
            VRMHELPER_OT_vrm0_spring_clear_linked_collider_group.bl_idname, text="", icon="PANEL_CLOSE"
        )
        box_cg.separator(factor=2.0)
        box_cg.operator(
            VRMHELPER_OT_vrm0_spring_register_linked_collider_group.bl_idname,
            text="Register from Selected Bone",
        )


"""---------------------------------------------------------
------------------------------------------------------------
    Ui List
------------------------------------------------------------
---------------------------------------------------------"""


class VRMHELPER_UL_vrm0_blend_shape_list(bpy.types.UIList):
    """Blend Shapeを表示するUI List"""

    def draw_item(
        self,
        context,
        layout: bpy.types.UILayout,
        data,
        item: ReferenceVrm0BlendShapeGroupPropertyGroup,
        icon,
        active_data,
        active_propname,
        index,
    ):
        sp = layout.split(factor=0.4)

        # アイコンと名前の描画
        row = sp.row(align=True)
        row.alignment = "LEFT"
        row.prop(item, "name", text="", emboss=False)
        row.label(text=" / ")
        row.prop(item, "preset_name", text="")

        # 各種バインドが存在する場合にアイコンを描画
        row_parameters = sp.row(align=False)
        row_parameters.alignment = "RIGHT"
        row_bind = row_parameters.row(align=True)
        row_bind.alignment = "RIGHT"

        if item.binds:
            row_bind.label(text="", icon="MESH_DATA")
        else:
            row_bind.label(text="")

        if item.material_values:
            row_bind.label(text="", icon="MATERIAL")
        else:
            row_bind.label(text="")

        # Blend Shapeが持つ各パラメーターの描画
        row_binary = row_parameters.row(align=True)
        row_binary.prop(item, "is_binary", icon="IPO_CONSTANT", icon_only=True)

        row_preview = row_parameters.row(align=True)
        row_preview.prop(item, "preview", text="Preview")


class VRMHELPER_UL_vrm0_blend_shape_bind_list(bpy.types.UIList):
    """Bindsを表示するUI List"""

    def draw_item(
        self,
        context,
        layout: bpy.types.UILayout,
        data,
        item: VRMHELPER_WM_vrm0_blend_shape_bind_list_items,
        icon,
        active_data,
        active_propname,
        index,
    ):
        row = layout.row(align=True)
        # Morph Target Bindが関連付けられているオブジェクト名のラベル
        if item.item_type[0]:
            row.label(text=item.name, icon="OUTLINER_OB_MESH")
            return

        # Morph Target Bindの各プロパティを描画する
        blend_shape_master = get_vrm0_extension_blend_shape()
        blend_shape_groups = blend_shape_master.blend_shape_groups
        active_index = blend_shape_master.active_blend_shape_group_index
        active_blend_shape_binds = blend_shape_groups[active_index].binds
        source_bind: ReferenceVrm0BlendShapeBindPropertyGroup = active_blend_shape_binds[item.bind_index]
        if item.item_type[1]:
            row.separator(factor=3.0)
            sp = row.split(factor=0.65)
            if not source_bind.mesh.mesh_object_name or not (
                target_object := bpy.data.objects.get(item.name).data.shape_keys
            ):
                sp.label(text="No ShapeKeys", icon="SHAPEKEY_DATA")
            else:
                sp_sub = sp.split(factor=0.9)
                sp_sub.prop_search(
                    source_bind,
                    "index",
                    target_object,
                    "key_blocks",
                    text="",
                )
                sp.prop(source_bind, "weight", slider=True)


class VRMHELPER_UL_vrm0_blend_shape_material_list(bpy.types.UIList, VRMHELPER_UL_base):
    """Material Valueを表示するUI List"""

    def draw_item(
        self,
        context,
        layout: bpy.types.UILayout,
        data,
        item: VRMHELPER_WM_vrm0_blend_shape_material_list_items,
        icon,
        active_data,
        active_propname,
        index,
    ):
        row = layout.row(align=True)

        # ラベルあるいはMaterial Valueの各プロパティを描画する
        active_blend_shape = get_vrm0_extension_active_blend_shape_group()
        material_values = active_blend_shape.material_values
        self.add_blank_labels(row, 3)
        mat_value: ReferenceVrm0MaterialValueBindPropertyGroup = material_values[item.value_index]

        initialize_material_value_prop()
        property_names = get_wm_vrm0_material_value_prop()

        # prop_searchの参照先プロパティーグループの定義｡
        gltf_or_mtoon = item.prop_dict[item.material_type]

        match tuple(item.item_type):
            case (1, 0, 0, 0) | (1, 0, 0, 1):
                match item.name:
                    case "Blank":
                        pass
                    case _:
                        row.label(text=item.name, icon="MATERIAL")
                return

            case (0, 1, 0, 0):
                prop_icon = "COLOR"
            case (0, 0, 1, 0):
                prop_icon = "TEXTURE"
            case (0, 0, 0, 1):
                prop_icon = "BLANK1"

        sp_prop = row.split(factor=0.5)
        sp_prop.prop_search(
            mat_value,
            "property_name",
            property_names,
            gltf_or_mtoon,
            text="",
            icon=prop_icon,
            results_are_suggestions=True,
        )

        row_prop = sp_prop.row()
        match tuple(item.item_type):
            case (0, 1, 0, 0):
                row_prop.prop(item, "material_color", text="")
            case (0, 0, 1, 0):
                row_prop.prop(item, "uv_scale", text="")
                row_prop.prop(item, "uv_offset", text="")


class VRMHELPER_UL_vrm0_collider_group_list(bpy.types.UIList, VRMHELPER_UL_base):
    """Vrm0のSpring Bone Collider Groupを表示するUI List"""

    def draw_item(
        self,
        context,
        layout: bpy.types.UILayout,
        data,
        item: VRMHELPER_WM_vrm0_collider_group_list_items,
        icon,
        active_data,
        active_propname,
        index,
    ):
        row = layout.row(align=True)
        target_armature = get_target_armature()

        # ラベルの描画｡
        match tuple(item.item_type):
            case (1, 0, 0, 0):
                row.label(text=target_armature.data.name, icon="OUTLINER_DATA_ARMATURE")
                return

            # リンクされたボーン名を表示するラベル(グルーピング用)
            case (0, 1, 0, 0):
                self.add_blank_labels(row, item.parent_count)
                row.label(text=item.bone_name, icon="BONE_DATA")
                return

            # コライダーグループを表示
            case (0, 0, 1, 0):
                self.add_blank_labels(row, item.parent_count + 1)
                row.label(text=item.group_name, icon="OVERLAY")
                return

            # コライダーグループに登録されたコライダー
            case (0, 0, 0, 1):
                self.add_blank_labels(row, item.parent_count + 2)
                if collider_object := bpy.data.objects.get(item.collider_name):
                    sp = row.split(factor=0.75)
                    sp.prop(collider_object, "name", text="", icon="MESH_UVSPHERE", emboss=False)
                    sp.prop(collider_object, "empty_display_size", text="")
                else:
                    row.label(text=item.collider_name, icon="DOT")
                return


class VRMHELPER_UL_vrm0_spring_list(bpy.types.UIList, VRMHELPER_UL_base):
    """
    Vrm0のSpring Bone Groupを表示するUI List
    """

    def draw_item(
        self,
        context,
        layout: bpy.types.UILayout,
        data,
        item: VRMHELPER_WM_vrm0_spring_bone_list_items,
        icon,
        active_data,
        active_propname,
        index,
    ):
        row = layout.row(align=True)
        bone_groups = get_vrm0_extension_spring_bone_group()
        target_armature_data = get_target_armature_data()

        # ラベルの描画
        bone_group: ReferenceVrm0SecondaryAnimationGroupPropertyGroup
        bone_group = bone_groups[item.item_indexes[0]]
        match tuple(item.item_type):
            case (1, 0, 0):
                row.label(text="")

            case (0, 1, 0):
                row.label(text="", icon="BOOKMARKS")
                row.prop(bone_group, "comment", text="", emboss=False)

            case (0, 0, 1):
                self.add_blank_labels(row, 2)
                bone: ReferenceBonePropertyGroup
                bone = bone_group.bones[item.item_indexes[1]]
                row.prop_search(
                    bone,
                    "bone_name",
                    target_armature_data,
                    "bones",
                    text="",
                )


class VRMHELPER_UL_vrm0_linked_collider_grouplist(bpy.types.UIList, VRMHELPER_UL_base):
    """
    Vrm0のSpring Bone GroupにリンクされたCollider Groupを表示するUI List
    """

    def draw_item(
        self,
        context,
        layout: bpy.types.UILayout,
        data,
        item: VRMHELPER_WM_vrm0_spring_linked_collider_group_list_items,
        icon,
        active_data,
        active_propname,
        index,
    ):
        row = layout.row(align=True)
        target_armature_data = get_target_armature_data()

        # ソースのSpring Bone GroupとリンクされたCollider Groupsを取得する｡
        secondary_animation = get_vrm0_extension_secondary_animation()
        bone_groups = secondary_animation.bone_groups
        source_bone_group: ReferenceVrm0SecondaryAnimationGroupPropertyGroup
        source_bone_group = bone_groups[item.item_indexes[0]]
        source_collider_group = source_bone_group.collider_groups[item.item_indexes[1]]
        self.add_blank_labels(row, 2)
        row.prop_search(
            source_collider_group,
            "value",
            secondary_animation,
            "collider_groups",
            text="",
            icon="MESH_UVSPHERE",
        )


"""---------------------------------------------------------
------------------------------------------------------------
    Resiter Target
------------------------------------------------------------
---------------------------------------------------------"""
CLASSES = (
    # ----------------------------------------------------------
    #    UI List
    # ----------------------------------------------------------
    VRMHELPER_UL_vrm0_first_person_list,
    VRMHELPER_UL_vrm0_blend_shape_list,
    VRMHELPER_UL_vrm0_blend_shape_bind_list,
    VRMHELPER_UL_vrm0_blend_shape_material_list,
    VRMHELPER_UL_vrm0_collider_group_list,
    VRMHELPER_UL_vrm0_spring_list,
    VRMHELPER_UL_vrm0_linked_collider_grouplist,
)
