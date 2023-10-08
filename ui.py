if "bpy" in locals():
    import importlib

    reloadable_modules = [
        "preparation_logger",
        "property_groups",
        "operators",
        "utils_common",
        "utils_vrm0_first_person",
        "utils_vrm1_first_person",
        "utils_vrm1_expression",
        "utils_vrm1_spring",
        "utils_vrm1_constraint",
        "vrm1_operators",
        "vrm1_ui",
    ]

    for module in reloadable_modules:
        if module in locals():
            importlib.reload(locals()[module])

else:
    from .Logging import preparation_logger
    from . import property_groups
    from . import utils_common
    from .Vrm1 import utils_vrm1_first_person
    from .Vrm1 import utils_vrm1_expression
    from .Vrm1 import utils_vrm1_spring
    from .Vrm1 import utils_vrm1_constraint
    from . import operators
    from .Vrm1 import vrm1_operators
    from .Vrm1 import vrm1_ui

import bpy

from .addon_constants import (
    DOCUMENTATION_URL,
)


from .property_groups import (
    VRMHELPER_SCENE_basic_settings,
    get_scene_basic_prop,
    get_target_armature_data,
)

from .utils_common import (
    get_properties_to_dict,
    define_ui_list_rows,
    set_properties_to_from_dict,
)

from .utils_vrm_base import (
    get_vrm_extension_root_property,
    get_vrm_extension_property,
    is_existing_target_armature,
    check_addon_mode,
)


from .operators import (
    VRMHELPER_OT_evaluate_addon_collections,
)

from .Vrm0.vrm0_ui import (
    draw_panel_vrm0_first_person,
    draw_panel_vrm0_blend_shape,
)


from .Vrm1.vrm1_ui import (
    draw_panel_vrm1_first_person,
    draw_panel_vrm1_expression,
    draw_panel_vrm1_collider,
    draw_panel_vrm1_collider_group,
    draw_panel_vrm1_spring,
    draw_panel_vrm1_constraint_ui_list,
    draw_panel_vrm1_constraint_operator,
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
    Function
------------------------------------------------------------
---------------------------------------------------------"""


def draw_spring_setting_box(
    target_box: bpy.types.UILayout,
    layout: bpy.types.UILayout,
    basic_prop: VRMHELPER_SCENE_basic_settings,
) -> bpy.types.UILayout:
    """
    スプリング設定ツールをグルーピングするためのboxが存在しない場合に新たに描画する｡

    Parameters
    ----------
    target_box : UILayout
        描画されるboxが既に存在するかどうかを判定するための変数｡返り値を受け取る変数でもある｡

    layout : UILayout
        boxを描画する対象となるUILayout

    basic_prop:VRMHELPER_SCENE_basic_settings
        アドオンの基本設定を行なうプロパティグループ｡

    Returns
    -------
    UILayout
        描画されたboxレイアウト｡

    """

    target_armature_data = basic_prop.target_armature.data
    vrm_extension = target_armature_data.vrm_addon_extension

    if not target_box:
        target_box = layout.box()
        target_box.label(text="Spring Tool", icon="PHYSICS")
        target_box.prop(vrm_extension.spring_bone1, "enable_animation")

    return target_box


"""---------------------------------------------------------
------------------------------------------------------------
    Panel
------------------------------------------------------------
---------------------------------------------------------"""


class VRMHELPER_PT_Base(bpy.types.Panel):
    """パネル用リストの基底クラス"""

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "VRMH"
    bl_options = {"DEFAULT_CLOSED"}

    def selected_tool_mode(self, vrm_mode: int) -> str:
        """
        'UI Mode'のEnumの選択状況に応じて文字列を出力する｡

        Parameters
        ----------
        mode : int
            'Ui Mode'のEnumPropertyで選択された項目をintに変換したもの

        Returns
        -------
        str
            引数'mode'に応じて出力された文字列

        """
        match vrm_mode:
            case "0":
                result = "Current Mode : 0.x"

            case "1":
                result = "Current Mode : 1.x"

            case "2":
                result = "Current Mode : Misc"

        return result


### -----------------------------------------------------


"""---------------------------------------------------------
    Basic Settings
---------------------------------------------------------"""


class VRMHELPER_PT_ui_basic_settings(VRMHELPER_PT_Base):
    """アドオンの基本設定を行なうパネル"""

    bl_label = ""
    bl_options = set()

    # ヘッダーのカスタマイズ
    def draw_header(self, context):
        layout = self.layout
        layout.label(text="VRM Helper", icon="SETTINGS")
        row = layout.row(align=True)
        row.alignment = "RIGHT"
        row.operator("wm.url_open", text="", icon="HELP").url = DOCUMENTATION_URL

    # パネルの項目の描画
    def draw(self, context):
        # Property Groupの取得｡
        basic_prop = get_scene_basic_prop()

        # UI描画
        layout = self.layout

        box = layout.box()
        box.label(text="Target Armature:")
        box.prop(
            basic_prop,
            "target_armature",
            text="",
            icon="OUTLINER_OB_ARMATURE",
        )

        # Target Armatureが選択されていれば追加設定が可能｡
        if is_existing_target_armature():
            layout.label(text="Addon Mode:")
            row = layout.row()
            row.scale_y = 1.4
            row.prop(basic_prop, "tool_mode", text=" ", expand=True)

        layout.separator()
        layout.operator(VRMHELPER_OT_evaluate_addon_collections.bl_idname)


# -----------------------------------------------------
"""---------------------------------------------------------
    Each tools
---------------------------------------------------------"""


class VRMHELPER_PT_ui_each_tools(VRMHELPER_PT_Base):
    """選択されたツールのUIを描画するパネル"""

    bl_label = "Tools"

    @classmethod
    def poll(cls, context):
        return is_existing_target_armature()

    # ヘッダーのカスタマイズ
    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon="TOOL_SETTINGS")

    # パネルの項目の描画
    def draw(self, context):
        # プロパティグループの取得
        basic_prop = get_scene_basic_prop()

        # UIの描画
        layout = self.layout

        match basic_prop.tool_mode:
            # ----------------------------------------------------------
            #    VRM0
            # ----------------------------------------------------------
            case "0":
                layout.label(text="Edit Target:")
                columns = 3

                grid = layout.grid_flow(row_major=True, align=True, columns=columns)
                grid.prop(basic_prop, "vrm0_component_type", text=" ")

                def get_index(element):
                    return basic_prop.vrm0_sort_order_component_type.index(element)

                component_types = sorted(
                    list(basic_prop.vrm0_component_type), key=get_index
                )

                box_spring = None
                for type in component_types:
                    match type:
                        case "FIRST_PERSON":
                            box = layout.box()
                            box.label(text="First Person Tools", icon="HIDE_OFF")
                            box_sub = box.box()
                            draw_panel_vrm0_first_person(self, context, box_sub)

                        case "BLEND_SHAPE":
                            box = layout.box()
                            box.label(text="Blend Shape Tools", icon="SHAPEKEY_DATA")
                            box_sub = box.box()
                            draw_panel_vrm0_blend_shape(self, context, box_sub)

                        case "COLLIDER_GROUP":
                            box_spring = draw_spring_setting_box(
                                box_spring, layout, basic_prop
                            )
                            box = box_spring.box()
                            box.label(text="Collider Group Tools", icon="OVERLAY")
                            box_sub = box.box()
                            # draw_panel_vrm1_collider_group(self, context, box_sub)

                        case "SPRING":
                            box_spring = draw_spring_setting_box(
                                box_spring, layout, basic_prop
                            )
                            box = box_spring.box()
                            box.label(text="Spring Bone Tools", icon="BONE_DATA")
                            box_sub = box.box()
                            # draw_panel_vrm1_spring(self, context, box_sub)

                    if len(basic_prop.vrm1_component_type) > 1:
                        layout.separator(factor=0.25)

            # ----------------------------------------------------------
            #    VRM1
            # ----------------------------------------------------------
            case "1":
                layout.label(text="Edit Target:")
                columns = 3

                grid = layout.grid_flow(row_major=True, align=True, columns=columns)
                grid.prop(basic_prop, "vrm1_component_type", text=" ")

                def get_index(element):
                    return basic_prop.vrm1_sort_order_component_type.index(element)

                component_types = sorted(
                    list(basic_prop.vrm1_component_type), key=get_index
                )

                box_spring = None
                for type in component_types:
                    match type:
                        case "FIRST_PERSON":
                            box = layout.box()
                            box.label(text="First Person Tools", icon="HIDE_OFF")
                            box_sub = box.box()
                            draw_panel_vrm1_first_person(self, context, box_sub)

                        case "EXPRESSION":
                            box = layout.box()
                            box.label(text="Expression Tools", icon="SHAPEKEY_DATA")
                            box_sub = box.box()
                            draw_panel_vrm1_expression(self, context, box_sub)

                        case "COLLIDER":
                            box_spring = draw_spring_setting_box(
                                box_spring, layout, basic_prop
                            )
                            box = box_spring.box()
                            box.label(text="Collider Tools", icon="MESH_UVSPHERE")
                            box_sub = box.box()
                            draw_panel_vrm1_collider(self, context, box_sub)

                        case "COLLIDER_GROUP":
                            box_spring = draw_spring_setting_box(
                                box_spring, layout, basic_prop
                            )
                            box = box_spring.box()
                            box.label(text="Collider Group Tools", icon="OVERLAY")
                            box_sub = box.box()
                            draw_panel_vrm1_collider_group(self, context, box_sub)

                        case "SPRING":
                            box_spring = draw_spring_setting_box(
                                box_spring, layout, basic_prop
                            )
                            box = box_spring.box()
                            box.label(text="Joint Tools", icon="BONE_DATA")
                            box_sub = box.box()
                            draw_panel_vrm1_spring(self, context, box_sub)

                        case "CONSTRAINT":
                            box = layout.box()
                            box.label(text="Node Constraint Tools", icon="CONSTRAINT")
                            box_sub = box.box()
                            draw_panel_vrm1_constraint_ui_list(self, context, box_sub)
                            draw_panel_vrm1_constraint_operator(self, context, box_sub)

                    if len(basic_prop.vrm1_component_type) > 1:
                        layout.separator(factor=0.25)


"""---------------------------------------------------------
------------------------------------------------------------
    Resiter Target
------------------------------------------------------------
---------------------------------------------------------"""
CLASSES = (
    # ----------------------------------------------------------
    #    UI
    # ----------------------------------------------------------
    VRMHELPER_PT_ui_basic_settings,
    VRMHELPER_PT_ui_each_tools,
)
