if "bpy" in locals():
    import importlib

    reloadable_modules = [
        "preparation_logger",
        "property_groups",
        "utils_common",
        "operators",
        "utils_vrm0_first_person",
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
    from . import vrm0_operators


import bpy


from ..addon_classes import (
    ReferenceVrm1ExpressionPropertyGroup,
    # ----------------------------------------------------------
    VRMHELPER_UL_base,
)

from ..addon_constants import (
    PRESET_BLEND_SHAPE_NAME_DICT,
)

from ..property_groups import (
    VRMHELPER_WM_vrm0_first_person_list_items,
    VRMHELPER_WM_vrm0_blend_shape_list_items,
    # ----------------------------------------------------------    get_target_armature,
    get_target_armature,
    get_target_armature_data,
    get_vrm0_scene_root_prop,
    get_vrm0_wm_root_prop,
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


from .utils_vrm0_first_person import (
    vrm0_add_items2annotation_ui_list,
    vrm0_search_same_name_mesh_annotation,
)

from .utils_vrm0_blend_shape import (
    get_source_vrm0_blend_shape4ui_list,
)


from ..operators import (
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
    row.prop(
        first_person_prop, "is_filtering_by_type", text="Filtering by Selected Type"
    )
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


def draw_panel_vrm0_blend_shape(self, context, layout: bpy.types.UILayout):
    """
    VRM1のExpressionに関する設定/オペレーターを描画する
    """

    # Property Groupの取得｡
    target_armature = get_target_armature()
    wm_vrm0_prop = get_vrm0_wm_root_prop()
    scene_vrm0_prop = get_vrm0_scene_root_prop()
    active_indexes = scene_vrm0_prop.active_indexes
    blend_shape_prop = scene_vrm0_prop.blend_shape_settings
    blend_shapes = get_source_vrm0_blend_shape4ui_list()

    # UI Listに表示するアイテムをコレクションプロパティに追加し､アイテム数を取得する｡
    rows = len(blend_shapes)

    # ----------------------------------------------------------
    #    登録されているExpressionのリスト描画
    # ----------------------------------------------------------
    row = layout.row()
    row.template_list(
        "VRMHELPER_UL_expression_list",
        "",
        wm_vrm0_prop,
        "expression_list_items4custom_filter",
        active_indexes,
        "expression",
        rows=define_ui_list_rows(rows),
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


class VRMHELPER_UL_expression_list(bpy.types.UIList):
    """Expressionを表示するUI List"""

    def draw_item(
        self,
        context,
        layout: bpy.types.UILayout,
        data,
        item: VRMHELPER_WM_vrm0_blend_shape_list_items,
        icon,
        active_data,
        active_propname,
        index,
    ):
        sp = layout.split(factor=0.4)
        row = sp.row(align=True)

        # アイコンの描画


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
)
