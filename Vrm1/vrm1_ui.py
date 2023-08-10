if "bpy" in locals():
    import importlib

    reloadable_modules = [
        "preparation_logger",
        "property_groups",
        "utils_common",
        "utils_vrm1_first_person",
        "utils_vrm1_expression",
        "utils_vrm1_spring",
        "utils_vrm1_constraint",
        "operators",
        "vrm1_operators",
    ]

    for module in reloadable_modules:
        if module in locals():
            importlib.reload(locals()[module])

else:
    from ..Logging import preparation_logger
    from .. import property_groups
    from .. import utils_common
    from . import utils_vrm1_first_person
    from . import utils_vrm1_expression
    from . import utils_vrm1_spring
    from . import utils_vrm1_constraint
    from .. import operators
    from . import vrm1_operators


import os
from pprint import pprint

import bpy
from bpy.types import (
    Context,
    Panel,
    Menu,
    UIList,
    UILayout,
)


from ..addon_classes import (
    VRMHELPER_UL_base,
)

from ..addon_constants import (
    JOINT_PROP_NAMES,
)

from ..property_groups import (
    VRMHELPER_SCENE_vrm1_collider_settigs,
    VRMHELPER_SCENE_vrm1_ui_list_active_indexes,
    VRMHELPER_WM_vrm1_expression_list_items,
    VRMHELPER_WM_vrm1_collider_list_items,
    VRMHELPER_WM_vrm1_constraint_list_items,
    get_vrm1_wm_root_prop,
    get_target_armature,
    get_target_armature_data,
    get_vrm1_scene_root_prop,
    get_vrm1_index_root_prop,
    get_vrm1_active_index_prop,
    get_ui_vrm1_first_person_prop,
    get_ui_vrm1_expression_prop,
    get_ui_vrm1_expression_morph_prop,
    get_ui_vrm1_expression_material_prop,
    get_ui_vrm1_collider_prop,
    get_ui_vrm1_collider_group_prop,
    get_ui_vrm1_spring_prop,
    get_ui_vrm1_constraint_prop,
)

from ..utils_common import (
    get_properties_to_dict,
    define_ui_list_rows,
    set_properties_to_from_dict,
)

from ..utils_vrm_base import (
    get_vrm_extension_root_property,
    get_vrm_extension_property,
    is_existing_target_armature,
    check_addon_mode,
)

from .utils_vrm1_first_person import (
    add_items2annotation_ui_list,
    search_same_name_mesh_annotation,
)

from .utils_vrm1_expression import (
    add_items2expression_ui_list,
    get_active_expression,
    add_items2expression_morph_ui_list,
    add_items2expression_material_ui_list,
)

from .utils_vrm1_spring import (
    get_active_list_item_in_spring,
    add_items2collider_ui_list,
    add_items2collider_group_ui_list,
    add_items2spring_ui_list,
)

from .utils_vrm1_constraint import (
    add_items2constraint_ui_list,
    draw_roll_constraint,
    draw_aim_constraint,
    draw_rotation_constraint,
)

from ..operators import (
    VRMHELPER_OT_reset_shape_keys_on_selected_objects,
)

from .vrm1_operators import (
    # ----------------------------------------------------------
    #    First Person
    # ----------------------------------------------------------
    VRMHELPER_OT_vrm1_first_person_set_annotation,
    VRMHELPER_OT_vrm1_first_person_remove_annotation_from_list,
    VRMHELPER_OT_vrm1_first_person_remove_annotation_from_select_objects,
    VRMHELPER_OT_vrm1_first_person_clear_annotation,
    # ----------------------------------------------------------
    #    Expression
    # ----------------------------------------------------------
    VRMHELPER_OT_vrm1_expression_create_custom_expression,
    VRMHELPER_OT_vrm1_expression_remove_custom_expression,
    VRMHELPER_OT_vrm1_expression_clear_custom_expression,
    # -----------------------------------------------------
    VRMHELPER_OT_vrm1_expression_morph_create_morph,
    VRMHELPER_OT_vrm1_expression_morph_remove_morph,
    VRMHELPER_OT_vrm1_expression_morph_clear_morphs,
    VRMHELPER_OT_vrm1_expression_set_morph_from_scene,
    # -----------------------------------------------------
    VRMHELPER_OT_vrm1_expression_material_create_color,
    VRMHELPER_OT_vrm1_expression_material_remove_color,
    VRMHELPER_OT_vrm1_expression_material_clear_colors,
    VRMHELPER_OT_vrm1_expression_material_create_transform,
    VRMHELPER_OT_vrm1_expression_material_remove_transform,
    VRMHELPER_OT_vrm1_expression_material_clear_transforms,
    VRMHELPER_OT_vrm1_expression_change_bind_material,
    VRMHELPER_OT_vrm1_expression_set_material_bind_from_scene,
    VRMHELPER_OT_vrm1_expression_store_mtoon1_parameters,
    VRMHELPER_OT_vrm1_expression_restore_mtoon1_parameters,
    VRMHELPER_OT_vrm1_expression_discard_stored_mtoon1_parameters,
    VRMHELPER_OT_vrm1_expression_assign_expression_to_scene,
    VRMHELPER_OT_vrm1_expression_set_both_binds_from_scene,
    VRMHELPER_OT_vrm1_expression_restore_initial_values,
    # ----------------------------------------------------------
    #    Collider
    # ----------------------------------------------------------
    VRMHELPER_OT_collider_create_from_bone,
    VRMHELPER_OT_collider_remove_from_empty,
    # ----------------------------------------------------------
    #    Collider Group
    # ----------------------------------------------------------
    VRMHELPER_OT_collider_group_add_group,
    VRMHELPER_OT_collider_group_remove_active_group,
    VRMHELPER_OT_collider_group_clear_group,
    VRMHELPER_OT_collider_group_add_collider,
    VRMHELPER_OT_collider_group_remove_collider,
    VRMHELPER_OT_collider_group_clear_collider,
    VRMHELPER_OT_collider_group_register_collider_from_bone,
    # ----------------------------------------------------------
    #    Spring
    # ----------------------------------------------------------
    VRMHELPER_OT_spring_add_spring,
    VRMHELPER_OT_spring_remove_spring,
    VRMHELPER_OT_spring_clear_spring,
    VRMHELPER_OT_spring_add_joint,
    VRMHELPER_OT_spring_remove_joint,
    VRMHELPER_OT_spring_clear_joint,
    VRMHELPER_OT_spring_add_joint_from_source,
    VRMHELPER_OT_spring_assign_parameters_to_selected_joints,
    VRMHELPER_OT_spring_add_collider_group,
    VRMHELPER_OT_spring_remove_collider_group,
    VRMHELPER_OT_spring_clear_collider_group,
    # ----------------------------------------------------------
    #    Constraint
    # ----------------------------------------------------------
    VRMHELPER_OT_constraint_add_vrm_constraint,
    VRMHELPER_OT_constraint_remove_vrm_constraint,
)

from ..operators import (
    VRMHELPER_OT_empty_operator,
)


"""---------------------------------------------------------
------------------------------------------------------------
    Logger
------------------------------------------------------------
---------------------------------------------------------"""
from ..Logging.preparation_logger import preparating_logger

logger = preparating_logger(__name__)
#######################################################


"""---------------------------------------------------------
    First Person
---------------------------------------------------------"""


def draw_panel_vrm1_first_person(self, context: Context, layout: UILayout):
    """
    VRM1のFirst Personに関する設定/オペレーターを描画する
    """

    # Property Groupの取得｡
    wm_vrm1_prop = get_vrm1_wm_root_prop()
    scene_scene_vrm1_prop = get_vrm1_scene_root_prop()
    first_person_prop = scene_scene_vrm1_prop.first_person_settings

    # ----------------------------------------------------------
    #    UI描画
    # ----------------------------------------------------------
    # UI Listに表示するアイテムをコレクションプロパティに追加し､アイテム数を取得する｡
    rows = add_items2annotation_ui_list()

    row = layout.row()
    row.prop(
        first_person_prop, "is_filtering_by_type", text="Filtering by Selected Type"
    )
    row = layout.row()
    row.scale_y = 1.4
    row.prop(first_person_prop, "annotation_type", text=" ", expand=True)
    row = layout.row()
    row.template_list(
        "VRMHELPER_UL_first_person_list",
        "",
        wm_vrm1_prop,
        "first_person_list_items4custom_filter",
        scene_scene_vrm1_prop.active_indexes,
        "first_person",
        rows=define_ui_list_rows(rows),
    )
    col = row.column()
    col.operator(
        VRMHELPER_OT_vrm1_first_person_remove_annotation_from_list.bl_idname,
        text="",
        icon="REMOVE",
    )
    col.operator(
        VRMHELPER_OT_vrm1_first_person_clear_annotation.bl_idname,
        text="",
        icon="PANEL_CLOSE",
    )

    layout.separator()
    col = layout.column(align=True)
    col.operator(
        VRMHELPER_OT_vrm1_first_person_set_annotation.bl_idname,
        text="Set from Selected Objects",
        icon="IMPORT",
    )
    col.operator(
        VRMHELPER_OT_vrm1_first_person_remove_annotation_from_select_objects.bl_idname,
        text="Remove by Selected Objects",
        icon="EXPORT",
    )


class VRMHELPER_UL_first_person_list(UIList):
    """First Person Mesh Annotationを表示するUI List"""

    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        annotation = search_same_name_mesh_annotation(item.name)

        # リスト内の項目のレイアウトを定義する｡
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            sp = layout.split(align=True, factor=0.7)
            sp.label(text=annotation.node.mesh_object_name, icon="OUTLINER_OB_MESH")
            sp.prop(annotation, "type", text="")


"""---------------------------------------------------------
    Expression
---------------------------------------------------------"""


def draw_panel_vrm1_expression(self, context: Context, layout: UILayout):
    """
    VRM1のExpressionに関する設定/オペレーターを描画する
    """

    # Property Groupの取得｡
    wm_vrm1_prop = get_vrm1_wm_root_prop()
    scene_scene_vrm1_prop = get_vrm1_scene_root_prop()
    active_indexes = scene_scene_vrm1_prop.active_indexes
    expression_prop = scene_scene_vrm1_prop.expression_settings

    # UI Listに表示するアイテムをコレクションプロパティに追加し､アイテム数を取得する｡
    rows = add_items2expression_ui_list()

    # ----------------------------------------------------------
    #    登録されているExpressionのリスト描画
    # ----------------------------------------------------------
    row = layout.row()
    row.template_list(
        "VRMHELPER_UL_expression_list",
        "",
        wm_vrm1_prop,
        "expression_list_items4custom_filter",
        active_indexes,
        "expression",
        rows=define_ui_list_rows(rows),
    )
    col = row.column(align=True)
    col.separator(factor=0.5)
    col.operator(
        VRMHELPER_OT_vrm1_expression_create_custom_expression.bl_idname,
        text="",
        icon="ADD",
    )
    col.operator(
        VRMHELPER_OT_vrm1_expression_remove_custom_expression.bl_idname,
        text="",
        icon="REMOVE",
    )
    col.operator(
        VRMHELPER_OT_vrm1_expression_clear_custom_expression.bl_idname,
        text="",
        icon="PANEL_CLOSE",
    )

    layout.operator(
        VRMHELPER_OT_vrm1_expression_assign_expression_to_scene.bl_idname,
        text="Assign Active Expression",
    )

    # ----------------------------------------------------------
    #    選択された編集対象のリストとオペレーターを描画
    # ----------------------------------------------------------
    box = layout.box()
    box.label(text="Editing Target:")
    row = box.row(align=True)
    row.prop(expression_prop, "editing_target", text=" ", expand=True)

    ######################################
    # Morph Target Bind
    ######################################
    if expression_prop.editing_target == "MORPH":
        rows = add_items2expression_morph_ui_list()
        row = box.row(align=True)
        row.template_list(
            "VRMHELPER_UL_expressin_morph_list",
            "",
            wm_vrm1_prop,
            "expression_morph_list_items4custom_filter",
            active_indexes,
            "expression_morph",
            rows=define_ui_list_rows(rows),
        )

        col = row.column()
        col.separator(factor=0.55)
        col.operator(
            VRMHELPER_OT_vrm1_expression_morph_create_morph.bl_idname,
            text="",
            icon="ADD",
        )
        col.operator(
            VRMHELPER_OT_vrm1_expression_morph_remove_morph.bl_idname,
            text="",
            icon="REMOVE",
        )
        col.operator(
            VRMHELPER_OT_vrm1_expression_morph_clear_morphs.bl_idname,
            text="",
            icon="PANEL_CLOSE",
        )

        # アクティブアイテムのMorph Target設定用フォーム
        if morph_target_binds := get_ui_vrm1_expression_morph_prop():
            current_index = active_indexes.expression_morph
            active_bind = morph_target_binds[current_index]

            if active_bind.item_type[1]:
                active_expression_binds = get_active_expression().morph_target_binds
                source_bind = active_expression_binds[active_bind.bind_index]
                box_bind_mesh = box.box()
                col_box_bind_mesh = box_bind_mesh.column(align=True)
                col_box_bind_mesh.label(text="Active Bind's Mesh:")
                col_box_bind_mesh.prop_search(
                    source_bind.node,
                    "mesh_object_name",
                    context.scene.vrm_addon_extension,
                    "mesh_object_names",
                    text="",
                    icon="OUTLINER_OB_MESH",
                )

    ##################################
    # Material Bind
    ##################################
    if expression_prop.editing_target == "MATERIAL":
        rows = add_items2expression_material_ui_list()
        row = box.row(align=True)
        row.template_list(
            "VRMHELPER_UL_expressin_material_list",
            "",
            wm_vrm1_prop,
            "expression_material_list_items4custom_filter",
            active_indexes,
            "expression_material",
            rows=define_ui_list_rows(rows),
        )

        col = row.column(align=True)
        col.label(text="", icon="COLOR")
        col.operator(
            VRMHELPER_OT_vrm1_expression_material_create_color.bl_idname,
            text="",
            icon="ADD",
        )
        col.operator(
            VRMHELPER_OT_vrm1_expression_material_remove_color.bl_idname,
            text="",
            icon="REMOVE",
        )
        col.operator(
            VRMHELPER_OT_vrm1_expression_material_clear_colors.bl_idname,
            text="",
            icon="PANEL_CLOSE",
        )

        col.separator(factor=2.0)
        col.label(text="", icon="TEXTURE")
        col.operator(
            VRMHELPER_OT_vrm1_expression_material_create_transform.bl_idname,
            text="",
            icon="ADD",
        )
        col.operator(
            VRMHELPER_OT_vrm1_expression_material_remove_transform.bl_idname,
            text="",
            icon="REMOVE",
        )
        col.operator(
            VRMHELPER_OT_vrm1_expression_material_clear_transforms.bl_idname,
            text="",
            icon="PANEL_CLOSE",
        )

        # アクティブなMaterial BindsのTarget Material設定用フォーム
        if material_binds_list := get_ui_vrm1_expression_material_prop():
            current_index = active_indexes.expression_material
            active_item = material_binds_list[current_index]

            # アクティブアイテムが 'Blank'以外のラベル､Color Bind､Transform Bindであるかを判定する｡
            match tuple(active_item.item_type):
                case (1, 0, 0) if active_item.name != "Blank":  # Label Exclude 'Blank'
                    ui_draw_flag = "Material"

                case (0, 1, 0):  # Material Color Bind
                    ui_draw_flag = "Material_Color_Bind"
                    active_expression_binds = (
                        get_active_expression().material_color_binds
                    )

                case (0, 0, 1):  # Texture Transfor Bind
                    ui_draw_flag = "Texture_Transform_Bind"
                    active_expression_binds = (
                        get_active_expression().texture_transform_binds
                    )

                case _:  # 'Blank' Label
                    ui_draw_flag = None

            # 'Blank'のラベル以外であれば追加のプロパティを描画する｡
            match ui_draw_flag:
                case "Material":
                    box_bind_material = box.box()
                    box_bind_material.label(
                        text=f"Binded Material : {active_item.bind_material_name}"
                    )
                    box_bind_material.operator(
                        VRMHELPER_OT_vrm1_expression_change_bind_material.bl_idname,
                        text="Change Bind Material",
                        icon="MATERIAL",
                    )

                case "Material_Color_Bind" | "Texture_Transform_Bind":
                    source_bind = active_expression_binds[active_item.bind_index]
                    box_bind_material = box.box()
                    col_box_bind_material = box_bind_material.column(align=True)
                    col_box_bind_material.label(text="Active Bind's Material:")
                    col_box_bind_material.prop_search(
                        source_bind,
                        "material",
                        bpy.data,
                        "materials",
                        text="",
                        icon="MATERIAL",
                    )

    # オペレーターの描画
    box.separator()
    box_op_mtoon = box.box()
    col = box_op_mtoon.column(align=True)
    col.scale_y = 1.2
    col.operator(
        VRMHELPER_OT_vrm1_expression_store_mtoon1_parameters.bl_idname,
        text="Store MToon Current Value",
        icon="IMPORT",
    )
    col.operator(
        VRMHELPER_OT_vrm1_expression_discard_stored_mtoon1_parameters.bl_idname,
        text="Discard stored MToon Value",
        icon="EXPORT",
    )

    box_op_bottom = box.box()
    col = box_op_bottom.column(align=True)
    col.scale_y = 1.2
    col.operator(
        VRMHELPER_OT_vrm1_expression_set_both_binds_from_scene.bl_idname,
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
        VRMHELPER_OT_vrm1_expression_restore_mtoon1_parameters.bl_idname,
        text="Restore MToon Initial Values",
        icon="NODE_MATERIAL",
    )
    col.operator(
        VRMHELPER_OT_vrm1_expression_restore_initial_values.bl_idname,
        text="Reset Bind's All Values",
        icon="RECOVER_LAST",
    )


class VRMHELPER_UL_expression_list(UIList):
    """Expressionを表示するUI List"""

    def draw_item(
        self,
        context,
        layout: UILayout,
        data,
        item: VRMHELPER_WM_vrm1_expression_list_items,
        icon,
        active_data,
        active_propname,
        index,
    ):
        expression = item.expressions_list[index]

        # プリセットエクスプレッションの場合はlabel､カスタムの場合はpropで描画する
        sp = layout.split(factor=0.25)
        row = sp.row(align=True)
        if item.custom_expression_index < 0:
            row.label(text=item.name)
        else:
            custom_expression = get_vrm_extension_property("EXPRESSION").custom[
                item.custom_expression_index
            ]
            row.prop(custom_expression, "custom_name", text="", emboss=False)

        # 各種バインドを持つ場合はアイコンを描画する｡
        sp = sp.split(factor=0.15)
        row = sp.row(align=False)
        row.alignment = "RIGHT"

        if item.has_morph_bind:
            row.label(text="", icon="MESH_DATA")
        else:
            row.label(text="")

        if item.has_material_bind:
            row.label(text="", icon="MATERIAL")
        else:
            row.label(text="")

        # エクスプレッションが持つ各パラメーターの描画
        row = sp.row(align=True)
        row.alignment = "RIGHT"
        row.prop(expression, "is_binary", text="", icon="IPO_CONSTANT")
        row.prop(expression, "override_blink", text="", icon="HIDE_ON")
        row.prop(expression, "override_look_at", text="", icon="VIS_SEL_11")
        row.prop(expression, "override_mouth", text="", icon="MESH_TORUS")


class VRMHELPER_UL_expressin_morph_list(UIList):
    """Morph Target Bindsを表示するUI List"""

    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        row = layout.row(align=True)
        # Morph Target Bindが関連付けられているオブジェクト名のラベル
        if item.item_type[0]:
            row.label(text=item.name, icon="OUTLINER_OB_MESH")
            return

        # Morph Target Bindの各プロパティを描画する
        active_expression_binds = get_active_expression().morph_target_binds
        source_bind = active_expression_binds[item.bind_index]
        if item.item_type[1]:
            row.separator(factor=3.0)
            sp = row.split(factor=0.65)
            if not source_bind.node.mesh_object_name or not (
                target_object := bpy.data.objects.get(item.name).data.shape_keys
            ):
                sp.label(text="No ShapeKeys", icon="SHAPEKEY_DATA")
            else:
                sp.prop_search(
                    source_bind,
                    "index",
                    target_object,
                    "key_blocks",
                    text="",
                )
                sp.prop(source_bind, "weight", slider=True)


class VRMHELPER_UL_expressin_material_list(UIList, VRMHELPER_UL_base):
    """Material Color/TextureTransform Bindsを表示するUI List"""

    def draw_item(
        self,
        context,
        layout: UILayout,
        data,
        item,
        icon,
        active_data,
        active_propname,
        index,
    ):
        row = layout.row(align=True)
        separator_facator = 2.5
        # ラベルの描画
        if item.item_type[0]:
            label_icon = "MATERIAL"
            if item.name == "Material Color":
                row.separator(factor=separator_facator)
                label_icon = "COLOR"

            if item.name == "Texture Transform":
                row.separator(factor=separator_facator)
                label_icon = "TEXTURE"

            if item.name == "Blank":
                return

            row.label(text=item.name, icon=label_icon)
            return

        # Material Bindの各プロパティを描画する
        active_expression = get_active_expression()
        # Mateiral Color Bindの場合
        self.add_blank_labels(row, 3)
        if item.item_type[1]:
            mat_color_binds = active_expression.material_color_binds
            source_color_bind = mat_color_binds[item.bind_index]
            row.prop(source_color_bind, "type", text="")

            # Color BindのタイプがLit ColorであればRGBA､それ以外ならRGBで描画する｡
            if source_color_bind.type == "color":
                source_prop = "target_value"
            else:
                source_prop = "target_value_as_rgb"
            row.prop(source_color_bind, source_prop, text="")

        # Texture Transform Bindの場合
        if item.item_type[2]:
            tex_transform_binds = active_expression.texture_transform_binds
            source_tex_transform_bind = tex_transform_binds[item.bind_index]
            row.prop(source_tex_transform_bind, "scale", text="")
            row.prop(source_tex_transform_bind, "offset", text="")


"""---------------------------------------------------------
    Collider
---------------------------------------------------------"""


def draw_panel_vrm1_collider(self, context: Context, layout: UILayout):
    """
    VRM1のColliderに関する設定/オペレーターを描画する
    """

    # Property Groupの取得｡
    wm_vrm1_prop = get_vrm1_wm_root_prop()
    scene_vrm1_prop = get_vrm1_scene_root_prop()
    # active_index = get_vrm1_active_index_prop("COLLIDER")
    active_index = scene_vrm1_prop.active_indexes.collider
    collider_prop: VRMHELPER_SCENE_vrm1_collider_settigs = (
        scene_vrm1_prop.collider_settings
    )

    # UI描画
    layout.prop(collider_prop, "is_additive_selecting")

    # UI Listに表示するアイテムをコレクションプロパティに追加し､アイテム数を取得する｡
    rows = add_items2collider_ui_list()

    row = layout.row()
    row.template_list(
        "VRMHELPER_UL_vrm1_collider_list",
        "",
        wm_vrm1_prop,
        "collider_list_items4custom_filter",
        scene_vrm1_prop.active_indexes,
        "collider",
        rows=define_ui_list_rows(rows),
    )
    row = layout.row()
    row.prop(collider_prop, "collider_type", text=" ", expand=True)
    row = layout.row()
    row.prop(collider_prop, "collider_radius", text="Generated Collider Radius")
    row = layout.row()

    op = row.operator(VRMHELPER_OT_collider_create_from_bone.bl_idname)
    op.collider_type = collider_prop.collider_type
    op.collider_radius = collider_prop.collider_radius

    op = row.operator(VRMHELPER_OT_collider_remove_from_empty.bl_idname)

    # アクティブアイテムがボーン名である場合はプロパティを表示する｡
    if items_list := get_ui_vrm1_collider_prop():
        active_item: VRMHELPER_WM_vrm1_collider_list_items = items_list[active_index]
        layout.separator()
        box = layout.box()
        row = box.row(align=True)

        match tuple(active_item.item_type):
            case (0, 1, 0, 0):
                row.prop_search(
                    collider_prop,
                    "link_bone",
                    get_target_armature_data(),
                    "bones",
                    text="Parent Bone",
                )

            case (0, 0, 1, 0) | (0, 0, 0, 1):
                match active_item.collider_type:
                    case "SPHERE":
                        collider_icon = "SPHERE"
                    case "CAPSULE" | "CAPSULE_END":
                        collider_icon = "META_CAPSULE"

                row.label(text="Selected Collider:")
                row.prop(active_item, "collider_name", text="", icon=collider_icon)
                row = box.row(align=True)
                # row.label(text="Collider Radius")
                row.prop(
                    collider_prop,
                    "active_collider_radius",
                    text="Active Collider Radius",
                )

    # アクティブアイテムがコライダーの場合はEmptyのサイズを表示する


class VRMHELPER_UL_vrm1_collider_list(UIList, VRMHELPER_UL_base):
    """Vrm1のSpring Bone Colliderを表示するUI List"""

    def draw_item(
        self,
        context,
        layout,
        data,
        item: VRMHELPER_WM_vrm1_collider_list_items,
        icon,
        active_data,
        active_propname,
        index,
    ):
        # リスト内の項目のレイアウトを定義する｡
        row = layout.row(align=True)

        # ラベルにArmature名を表示｡
        if item.item_type[0]:
            row.label(
                text=get_target_armature_data().name, icon="OUTLINER_DATA_ARMATURE"
            )

        # 親ボーン名の描画
        if item.item_type[1]:
            self.add_blank_labels(row, item.parent_count)
            row.label(text=item.bone_name, icon="BONE_DATA")
            return

        # Colliderの描画｡
        if not (colliders := get_vrm_extension_property("COLLIDER")):
            return

        collider = colliders[item.item_index]
        match item.collider_type:
            case "SPHERE":
                collider_icon = "SPHERE"

            case "CAPSULE" | "CAPSULE_END":
                collider_icon = "META_CAPSULE"

        # ColliderがSphereあるいはCapsuleのHeadの場合｡
        if item.item_type[2]:
            self.add_blank_labels(row, item.parent_count + 1)
            if collider.bpy_object:
                row.prop(
                    collider.bpy_object,
                    "name",
                    text="",
                    icon=collider_icon,
                    emboss=False,
                )
            else:
                row.prop(collider, "bpy_object", text="", icon=collider_icon)
            return

        # ColliderがCapsuleのEndであれば一段インデントを設ける｡
        if item.item_type[3]:
            self.add_blank_labels(row, item.parent_count + 2)
            if collider.bpy_object:
                row.prop(
                    collider.bpy_object.children[0],
                    "name",
                    text="",
                    icon=collider_icon,
                    emboss=False,
                )
            else:
                row.prop(collider, "bpy_object", text="", icon=collider_icon)
            return


"""---------------------------------------------------------
    Collider Group
---------------------------------------------------------"""


def draw_panel_vrm1_collider_group(self, context: Context, layout: UILayout):
    """
    VRM1のCollider Groupに関する設定/オペレーターを描画する
    """

    # Property Groupの取得｡
    wm_vrm1_prop = get_vrm1_wm_root_prop()
    scene_vrm1_prop = get_vrm1_scene_root_prop()

    # UI描画
    row = layout.row()
    mode = check_addon_mode()

    if mode == "0":
        row.label(text=self.selected_tool_mode(mode))

    if mode == "1":
        # UI Listに表示するアイテムをコレクションプロパティに追加し､アイテム数を取得する｡
        rows = add_items2collider_group_ui_list()
        row.template_list(
            "VRMHELPER_UL_vrm1_collider_group_list",
            "",
            wm_vrm1_prop,
            "collider_group_list_items4custom_filter",
            scene_vrm1_prop.active_indexes,
            "collider_group",
            rows=define_ui_list_rows(rows),
        )
        # UI List右に描画
        col = row.column(align=True)
        col.label(icon="OVERLAY")
        col.operator(
            VRMHELPER_OT_collider_group_add_group.bl_idname, text="", icon="ADD"
        )
        col.operator(
            VRMHELPER_OT_collider_group_remove_active_group.bl_idname,
            text="",
            icon="REMOVE",
        )
        col.operator(
            VRMHELPER_OT_collider_group_clear_group.bl_idname,
            text="",
            icon="PANEL_CLOSE",
        )
        col.separator(factor=2.0)
        col.label(icon="MESH_UVSPHERE")
        col.operator(
            VRMHELPER_OT_collider_group_add_collider.bl_idname, text="", icon="ADD"
        )
        col.operator(
            VRMHELPER_OT_collider_group_remove_collider.bl_idname,
            text="",
            icon="REMOVE",
        )
        col.operator(
            VRMHELPER_OT_collider_group_clear_collider.bl_idname,
            text="",
            icon="PANEL_CLOSE",
        )

        # UI List下に描画
        row = layout.row(align=True)
        row.operator(VRMHELPER_OT_collider_group_register_collider_from_bone.bl_idname)


class VRMHELPER_UL_vrm1_collider_group_list(UIList):
    """Vrm1のSpring Bone Collider Groupを表示するUI List"""

    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        row = layout.row(align=True)

        # ラベルの描画｡
        if item.item_type[0]:
            row.label(text="")
            return

        spring1 = get_vrm_extension_root_property("SPRING1")
        # Collider Groupの描画｡
        if item.item_type[1]:
            row.prop(
                spring1.collider_groups[item.item_indexes[0]],
                "vrm_name",
                text="",
                icon="OVERLAY",
                emboss=False,
            )
            return

        # Colliderの描画｡
        if item.item_type[2]:
            row.separator(factor=2.0)
            row.prop_search(
                spring1.collider_groups[item.item_indexes[0]].colliders[
                    item.item_indexes[1]
                ],
                "collider_name",
                spring1,
                "colliders",
                text="",
                icon="MESH_UVSPHERE",
            )


"""---------------------------------------------------------
    Spring
---------------------------------------------------------"""


def draw_panel_vrm1_spring(self, context: Context, layout: UILayout):
    """
    VRM1のSpringに関する設定/オペレーターを描画する
    """

    # Property Groupの取得｡
    wm_vrm1_prop = get_vrm1_wm_root_prop()
    scene_vrm1_prop = get_vrm1_scene_root_prop()
    spring_settings = scene_vrm1_prop.spring_settings
    joint_properties = get_properties_to_dict(spring_settings, JOINT_PROP_NAMES)

    # UI描画
    row = layout.row()
    mode = check_addon_mode()

    if mode == "0":
        row.label(text=self.selected_tool_mode(mode))

    if mode == "1":
        # UI Listに表示するアイテムをコレクションプロパティに追加し､アイテム数を取得する｡
        rows = add_items2spring_ui_list()

        row.template_list(
            "VRMHELPER_UL_vrm1_spring_list",
            "",
            wm_vrm1_prop,
            "spring_list_items4custom_filter",
            scene_vrm1_prop.active_indexes,
            "spring",
            rows=define_ui_list_rows(rows, max_length=20),
        )

        col_side = row.column(align=True)
        col_side.label(icon="PHYSICS")

        # スプリングの作成/削除に関するオペレーター
        col_side.operator(VRMHELPER_OT_spring_add_spring.bl_idname, text="", icon="ADD")
        col_side.operator(
            VRMHELPER_OT_spring_remove_spring.bl_idname, text="", icon="REMOVE"
        )
        col_side.operator(
            VRMHELPER_OT_spring_clear_spring.bl_idname, text="", icon="PANEL_CLOSE"
        )
        col_side.separator(factor=2.0)

        # UI Listのアクティブアイテムのタイプに応じて追加の項目を描画する｡
        if (active_item := get_active_list_item_in_spring()) and active_item.name:
            spring = get_vrm_extension_property("SPRING")[active_item.item_indexes[0]]
            box = layout.box()

            # スプリング全体の設定用プロパティ
            target_armature = get_target_armature_data()
            box.prop(spring, "vrm_name", text="Selected Spring", icon="DOT")
            box.prop_search(
                spring.center,
                "bone_name",
                target_armature,
                "bones",
                text="Center",
            )

            # アクティブアイテムがJointの場合｡
            if active_item.item_type[2] or active_item.name == "Joint":
                col_side.label(icon="BONE_DATA")

                # ジョイント作成/削除に関するオペレーター
                op = col_side.operator(
                    VRMHELPER_OT_spring_add_joint.bl_idname, text="", icon="ADD"
                )
                set_properties_to_from_dict(op, joint_properties)
                op.use_auto_joint_parametter = spring_settings.use_auto_joint_parametter

                col_side.operator(
                    VRMHELPER_OT_spring_remove_joint.bl_idname, text="", icon="REMOVE"
                )
                col_side.operator(
                    VRMHELPER_OT_spring_clear_joint.bl_idname,
                    text="",
                    icon="PANEL_CLOSE",
                )
                row = col_side.row(align=True)
                row.alignment = "CENTER"
                row.prop(spring_settings, "use_auto_joint_parametter", text="")

                box_sub = box.box()
                # アクティブアイテムの調整用プロパティ
                if active_item.item_type[2]:
                    joint = spring.joints[active_item.item_indexes[1]]
                    box_3rd = box_sub.box()
                    box_3rd.prop_search(
                        joint.node,
                        "bone_name",
                        target_armature,
                        "bones",
                        text="Selected Joint",
                    )
                    box_sub.prop(joint, "hit_radius", slider=True)
                    box_sub.prop(joint, "stiffness", slider=True)
                    box_sub.prop(joint, "drag_force", slider=True)
                    box_sub.prop(joint, "gravity_power", slider=True)
                    box_sub.prop(joint, "gravity_dir")

                # ジョイント作成用/調整用プロパティ､オペレーター
                if active_item.name == "Joint":
                    box_sub.label(text="Operator Settings")
                    box_sub.prop(spring_settings, "hit_radius", slider=True)
                    box_sub.prop(spring_settings, "stiffness", slider=True)
                    box_sub.prop(spring_settings, "drag_force", slider=True)
                    box_sub.prop(spring_settings, "gravity_power", slider=True)
                    box_sub.prop(spring_settings, "gravity_dir")
                    box_sub.separator(factor=0.5)
                    box_sub.prop(spring_settings, "damping_ratio", slider=True)

            # アクティブアイテムがCollider Groupの場合｡
            if active_item.item_type[3] or active_item.name == "Collider Group":
                col_side.label(icon="OVERLAY")
                col_side.operator(
                    VRMHELPER_OT_spring_add_collider_group.bl_idname,
                    text="",
                    icon="ADD",
                )
                col_side.operator(
                    VRMHELPER_OT_spring_remove_collider_group.bl_idname,
                    text="",
                    icon="REMOVE",
                )
                col_side.operator(
                    VRMHELPER_OT_spring_clear_collider_group.bl_idname,
                    text="",
                    icon="PANEL_CLOSE",
                )

                # コライダーグループの設定用オペレーター
                box_sub = box.box()
                box_sub.operator(
                    VRMHELPER_OT_empty_operator.bl_idname, text="Set Collider Group"
                )

        # ----------------------------------------------------------
        #    ジョイントの自動作成｡
        # ----------------------------------------------------------
        box = layout.box()
        col = box.column(align=True)
        op = col.operator(
            VRMHELPER_OT_spring_add_joint_from_source.bl_idname,
            text="Create from Selected",
        )
        set_properties_to_from_dict(op, joint_properties)

        op = col.operator(
            VRMHELPER_OT_spring_add_joint_from_source.bl_idname,
            text="Create from Bone Group",
        )
        set_properties_to_from_dict(op, joint_properties)
        op.source_type = "BONE_GROUP"

        # ----------------------------------------------------------
        #    既存ジョイントのパラメーター調整
        # ----------------------------------------------------------
        col.separator()
        op = col.operator(
            VRMHELPER_OT_spring_assign_parameters_to_selected_joints.bl_idname,
            text="Adust Active Joint",
        )
        op.source_type = "SINGLE"
        set_properties_to_from_dict(op, joint_properties)

        op = col.operator(
            VRMHELPER_OT_spring_assign_parameters_to_selected_joints.bl_idname,
            text="Adjust Selected Joint",
        )
        set_properties_to_from_dict(op, joint_properties)
        op.source_type = "MULTIPLE"


# TODO : ジョイント調整パラメーターの表示条件変更｡
# TODO : コンテクストの情報に基づき使用できないオペレーターをグレーアウトさせる｡


class VRMHELPER_UL_vrm1_spring_list(UIList, VRMHELPER_UL_base):
    """
    Vrm1のSpring Bone Springを表示するUI List
    """

    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        row = layout.row(align=True)

        # ラベルの描画
        if item.item_type[0]:
            if not item.name:
                row.label(text="")
                return

            label_icon = "OVERLAY"
            if item.name == "Joint":
                label_icon = "BONE_DATA"
            row.separator(factor=2.0)
            row.label(text=item.name, icon=label_icon)
            return

        spring = get_vrm_extension_property("SPRING")
        # Springの描画
        if item.item_type[1]:
            row.label(text="", icon="DOT")
            row.prop(spring[item.item_indexes[0]], "vrm_name", text="")
            return

        # Jointの描画
        if item.item_type[2]:
            armature = get_target_armature_data()
            self.add_blank_labels(row, 2)
            row.prop_search(
                spring[item.item_indexes[0]].joints[item.item_indexes[1]].node,
                "bone_name",
                armature,
                "bones",
                text="",
                icon="BONE_DATA",
            )
            return

        # Collider Groupの描画
        if item.item_type[3]:
            spring1 = get_vrm_extension_root_property("SPRING1")
            self.add_blank_labels(row, 2)
            row.prop_search(
                spring[item.item_indexes[0]].collider_groups[item.item_indexes[2]],
                "collider_group_name",
                spring1,
                "collider_groups",
                text="",
                icon="OVERLAY",
            )
            return


"""---------------------------------------------------------
    Constraint
---------------------------------------------------------"""


def draw_panel_vrm1_constraint_ui_list(self, context: Context, layout: UILayout):
    """
    VRM1のObject Constraintに関するUI Listを描画する
    """

    # Property Groupの取得｡
    wm_vrm1_prop = get_vrm1_wm_root_prop()
    scene_vrm1_prop = get_vrm1_scene_root_prop()
    constraint_prop = scene_vrm1_prop.constraint_settings

    # ----------------------------------------------------------
    #    UI描画
    # ----------------------------------------------------------
    # UI Listに表示するアイテムをコレクションプロパティに追加し､アイテム数を取得する｡
    row = layout.row()
    row.scale_y = 1.3
    row.prop(constraint_prop, "constraint_type", text=" ", expand=True)

    rows = add_items2constraint_ui_list(constraint_prop.constraint_type)
    row = layout.row()
    row.template_list(
        "VRMHELPER_UL_vrm1_constraint_list",
        "",
        wm_vrm1_prop,
        "constraint_list_items4custom_filter",
        scene_vrm1_prop.active_indexes,
        "constraint",
        rows=define_ui_list_rows(rows),
    )

    constraint_list = wm_vrm1_prop.constraint_list_items4custom_filter
    active_index = get_vrm1_index_root_prop().constraint
    active_item = None
    if constraint_list:
        active_item: VRMHELPER_WM_vrm1_constraint_list_items = constraint_list[
            active_index
        ]

    # UI Listが空であれば処理終了｡
    if not active_item:
        return

    col = layout.column()
    box_prop = col.box()

    # アクティブアイテムがラベルである場合はオペレーター使用不可｡
    if active_item.is_label:
        col.enabled = False

    # アクティブアイテムのプロパティの描画｡
    else:
        if active_item.is_circular_dependency:
            box_prop.label(text="Detected Circular Constraint!", icon="ERROR")
            box_prop.separator()
        match constraint_prop.constraint_type:
            case "OBJECT":
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

        match active_item.constraint_type:
            case 0:
                draw_roll_constraint(box_prop, source_constraint)
            case 1:
                draw_aim_constraint(box_prop, source_constraint)
            case 2:
                draw_rotation_constraint(box_prop, source_constraint)


def draw_panel_vrm1_constraint_operator(self, context: Context, layout: UILayout):
    """
    VRM1のObject Constraintに関するUI Listを描画する
    """
    col = layout.column()
    op_roll = col.operator(
        VRMHELPER_OT_constraint_add_vrm_constraint.bl_idname,
        text="Create Roll Constraint",
    )
    op_roll.constraint_type = "ROLL"

    op_aim = col.operator(
        VRMHELPER_OT_constraint_add_vrm_constraint.bl_idname,
        text="Create Aim Constraint",
    )
    op_aim.constraint_type = "AIM"

    op_rot = col.operator(
        VRMHELPER_OT_constraint_add_vrm_constraint.bl_idname,
        text="Create Rotation Constraint",
    )
    op_rot.constraint_type = "ROTATION"

    layout.separator()
    layout.operator(
        VRMHELPER_OT_constraint_remove_vrm_constraint.bl_idname, icon="REMOVE"
    )


class VRMHELPER_UL_vrm1_constraint_list(UIList, VRMHELPER_UL_base):
    """Node Constraintを表示するUI List"""

    def draw_item(
        self,
        context,
        layout: UILayout,
        data,
        item: VRMHELPER_WM_vrm1_constraint_list_items,
        icon,
        active_data,
        active_propname,
        index,
    ):
        # リスト内の項目のレイアウトを定義する｡
        row = layout.row(align=True)

        # ブランクの描画
        if item.is_blank:
            row.label(text="")
            return

        # ラベルの描画
        if item.is_label:
            match item.constraint_type:
                case 0:
                    label_text = "Roll Constraint"
                    label_icon = "CON_ROTLIKE"

                case 1:
                    label_text = "Aim Constrait"
                    label_icon = "CON_TRACKTO"

                case 2:
                    label_text = "Rotation Constraint"
                    label_icon = "FILE_REFRESH"

            row.label(text=label_text, icon=label_icon)
            return

        # コンストレイントの描画
        if item.is_object_constraint:
            item_icon = "OBJECT_DATA"
        else:
            item_icon = "BONE_DATA"

        # 循環依存関係がある場合はアラートを表示する｡
        if item.is_circular_dependency:
            self.add_blank_labels(row, 1)
            row.label(text="", icon="ERROR")

        else:
            self.add_blank_labels(row, 2)

        row.label(text=item.name, icon=item_icon)
        row.label(text=item.constraint_name, icon="CONSTRAINT")


"""---------------------------------------------------------
------------------------------------------------------------
    Resiter Target
------------------------------------------------------------
---------------------------------------------------------"""
CLASSES = (
    # ----------------------------------------------------------
    #    UI List
    # ----------------------------------------------------------
    VRMHELPER_UL_first_person_list,
    VRMHELPER_UL_expression_list,
    VRMHELPER_UL_expressin_morph_list,
    VRMHELPER_UL_expressin_material_list,
    VRMHELPER_UL_vrm1_collider_list,
    VRMHELPER_UL_vrm1_collider_group_list,
    VRMHELPER_UL_vrm1_spring_list,
    VRMHELPER_UL_vrm1_constraint_list,
)
