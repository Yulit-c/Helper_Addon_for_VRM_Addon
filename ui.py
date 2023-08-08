if "bpy" in locals():
    import importlib

    reloadable_modules = [
        "preparation_logger",
        "property_groups",
        "operators",
        "utils_vrm1_common",
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


import os
import bpy
from bpy.types import (
    Panel,
    Menu,
    UIList,
    UILayout,
)

from .property_groups import (
    get_scene_basic_prop,
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
    VRMHELPER_OT_empty_operator,
    VRMHELPER_OT_evaluate_addon_collections,
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


def draw_spring_setting_box(result: UILayout, layout: UILayout) -> UILayout:
    """
    スプリング設定ツールをグルーピングするためのboxが存在しない場合に新たに描画する｡

    Parameters
    ----------
    result : UILayout
        描画されるboxが既に存在するかどうかを判定するための変数｡返り値を受け取る変数でもある｡

    layout : UILayout
        boxを描画する対象となるUILayout

    Returns
    -------
    UILayout
        描画されたboxレイアウト｡

    """
    if not result:
        result = layout.box()
        result.label(text="Spring Tool", icon="PHYSICS")

    return result


"""---------------------------------------------------------
------------------------------------------------------------
    Panel
------------------------------------------------------------
---------------------------------------------------------"""


class VRMHELPER_PT_Base(Panel):
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

    bl_label = "VRM Helper"
    bl_options = set()

    # ヘッダーのカスタマイズ
    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon="SETTINGS")

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
            layout.label(text="Selected Mode:")
            row = layout.row()
            row.scale_y = 1.4
            row.prop(basic_prop, "tool_mode", text=" ", expand=True)

        match basic_prop.tool_mode:
            case "1":
                layout.label(text="Selected Tool:")
                row = layout.row()
                row.scale_y = 1.4
                row.prop(basic_prop, "component_type", text=" ", expand=True)

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

        # ----------------------------------------------------------
        #    VRM1
        # ----------------------------------------------------------
        if basic_prop.tool_mode == "1":
            box_spring = None

            def get_index(element):
                return basic_prop.sort_order_component_type.index(element)

            component_types = sorted(list(basic_prop.component_type), key=get_index)

            for type in component_types:
                match type:
                    case "FIRST_PERSON":
                        box = layout.box()
                        box.label(text="First Person Tool", icon="HIDE_OFF")
                        box_sub = box.box()
                        draw_panel_vrm1_first_person(self, context, box_sub)

                    case "EXPRESSION":
                        box = layout.box()
                        box.label(text="Expression Tool", icon="SHAPEKEY_DATA")
                        box_sub = box.box()
                        draw_panel_vrm1_expression(self, context, box_sub)

                    case "COLLIDER":
                        box_spring = draw_spring_setting_box(box_spring, layout)
                        box = box_spring.box()
                        box.label(text="Collider", icon="MESH_UVSPHERE")
                        box_sub = box.box()
                        draw_panel_vrm1_collider(self, context, box_sub)

                    case "COLLIDER_GROUP":
                        box_spring = draw_spring_setting_box(box_spring, layout)
                        box = box_spring.box()
                        box.label(text="Collider Group", icon="OVERLAY")
                        box_sub = box.box()
                        draw_panel_vrm1_collider_group(self, context, box_sub)

                    case "SPRING":
                        box_spring = draw_spring_setting_box(box_spring, layout)
                        box = box_spring.box()
                        box.label(text="Joint", icon="BONE_DATA")
                        box_sub = box.box()
                        draw_panel_vrm1_spring(self, context, box_sub)

                    case "CONSTRAINT":
                        box = layout.box()
                        box.label(text="Node Constraint", icon="CONSTRAINT")
                        box_sub = box.box()
                        draw_panel_vrm1_constraint_ui_list(self, context, box_sub)
                        draw_panel_vrm1_constraint_operator(self, context, box_sub)

                if len(basic_prop.component_type) > 1:
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
