if "bpy" in locals():
    import importlib

    reloadable_modules = [
        "preparation_logger",
        "addon_classes",
        "utils_common",
        "utils_vrm_base",
        "utils_first_person",
        "utils_spring",
    ]

    for module in reloadable_modules:
        if module in locals():
            importlib.reload(locals()[module])

else:
    from .Logging import preparation_logger
    from . import addon_classes
    from . import utils_common
    from . import utils_vrm_base
    from .Vrm1 import utils_vrm1_first_person
    from .Vrm1 import utils_vrm1_spring


import os
from typing import (
    Literal,
)
import bpy

from bpy.props import (
    EnumProperty,
)


from .addon_classes import (
    ConstraintTypeDict,
)

from .property_groups import (
    get_vrm1_index_root_prop,
    get_vrm1_active_index_prop,
    get_scene_vrm1_constraint_prop,
    get_ui_vrm1_first_person_prop,
    get_ui_vrm1_expression_prop,
    get_ui_vrm1_expression_morph_prop,
    get_ui_vrm1_expression_material_prop,
    get_ui_vrm1_collider_prop,
    get_ui_vrm1_collider_group_prop,
    get_ui_vrm1_spring_prop,
    get_ui_vrm1_constraint_prop,
)

from .utils_common import (
    reset_shape_keys_value,
)

from .utils_vrm_base import (
    set_new_value2index_prop,
    re_link_all_collider_object2collection,
)

from .Vrm0.utils_vrm0_first_person import (
    vrm0_add_items2annotation_ui_list,
)

from .Vrm1.utils_vrm1_first_person import (
    vrm1_add_items2annotation_ui_list,
)

from .Vrm1.utils_vrm1_expression import (
    add_items2expression_ui_list,
    add_items2expression_morph_ui_list,
    add_items2expression_material_ui_list,
)

from .Vrm1.utils_vrm1_spring import (
    # ----------------------------------------------------------
    #    Collider
    # ----------------------------------------------------------
    add_items2collider_ui_list,
    # ----------------------------------------------------------
    #    Collider Group
    # ----------------------------------------------------------
    add_items2collider_group_ui_list,
    # ----------------------------------------------------------
    #    Spring
    # ----------------------------------------------------------
    add_items2spring_ui_list,
)

from .Vrm1.utils_vrm1_constraint import (
    add_items2constraint_ui_list,
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
    Operator
------------------------------------------------------------
---------------------------------------------------------"""

"""---------------------------------------------------------
    Common
---------------------------------------------------------"""


class VRMHELPER_OT_empty_operator(bpy.types.Operator):
    bl_idname = "vrmhelper.empty_operator"
    bl_label = "Empty Operator"
    bl_description = "Operator without any processing"
    bl_options = {"UNDO"}

    def execute(self, context):
        os.system("cls")
        self.report({"INFO"}, "VRM Helper")
        logger.debug("VRM Helper")
        return {"FINISHED"}


class VRMHELPER_OT_evaluate_addon_collections(bpy.types.Operator):
    bl_idname = "vrmhelper.evaluate_addon_collections"
    bl_label = "Evaluate Addon's Collections"
    bl_description = (
        "Creates a collection defined by this addon, and a defined hierarchy"
    )
    bl_options = {"UNDO"}

    def execute(self, context):
        os.system("cls")
        re_link_all_collider_object2collection()
        return {"FINISHED"}


class VRMHELPER_OT_reset_shape_keys_on_selected_objects(bpy.types.Operator):
    bl_idname = "vrmhelper.reset_shape_keys_on_selected_objects"
    bl_label = "Reset Shape Keys"
    bl_description = "Reset all shape keys on selected objects"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        for obj in [obj for obj in context.selected_objects if obj.type == "MESH"]:
            reset_shape_keys_value(obj.data)

        return {"FINISHED"}


class VRMHELPER_operator_base(bpy.types.Operator):
    """
    オペレーター用基底クラス
    """

    # vrm_mode: EnumProperty(
    #     name="VRM Version",
    #     description="Version of VRM to be edited",
    #     items=(
    #         ("0", "0.x", "Edit the VRM data of version 0.x"),
    #         ("1", "1.x", "Edit the VRM data of version 1.x"),
    #     ),
    #     # default="1",
    #     options={"HIDDEN"},
    # )

    vrm_mode: Literal[0, 1]

    bl_options = {"UNDO"}

    # -----------------------------------------------------

    def update_ui_list_prop(
        self,
        target_type: Literal[
            "FIRST_PERSON",
            "EXPRESSION",
            "EXPRESSION_MORPH",
            "EXPRESSION_MATERIAL",
            "COLLIDER",
            "COLLIDER_GROUP",
            "SPRING",
            "CONSTRAINT",
        ],
    ):
        """
        'target_type'に対応するUIリストのアイテムを全て消去した後に再登録する

        Parameters
        ----------
        target_type: Literal[
            "FIRST_PERSON",
            "EXPRESSION",
            "EXPRESSION_MORPH",
            "EXPRESSION_MATERIAL",
            "COLLIDER",
            "COLLIDER_GROUP",
            "SPRING",
            "CONSTRAINT",
        ],
            対象となるUIリストの種類

        """

        pattern = (int(self.vrm_mode), target_type)
        logger.debug(pattern)

        match pattern:
            case (0, "FIRST_PERSON"):
                vrm0_add_items2annotation_ui_list()

            case (1, "FIRST_PERSON"):
                vrm1_add_items2annotation_ui_list()

            case (1, "EXPRESSION"):
                add_items2expression_ui_list()

            case (1, "EXPRESSION_MORPH"):
                add_items2expression_morph_ui_list()

            case (1, "EXPRESSION_MATERIAL"):
                add_items2expression_material_ui_list()

            case (1, "COLLIDER"):
                add_items2collider_ui_list()

            case (1, "COLLIDER_GROUP"):
                add_items2collider_group_ui_list()

            case (1, "SPRING"):
                add_items2spring_ui_list()

            case (1, "CONSTRAINT"):
                constraint_type = get_scene_vrm1_constraint_prop().constraint_type
                add_items2constraint_ui_list(constraint_type)

    def offset_active_item_index(
        self,
        component_type: Literal[
            "FIRST_PERSON",
            "EXPRESSION",
            "EXPRESSION_MORPH",
            "EXPRESSION_MATERIAL",
            "COLLIDER",
            "COLLIDER_GROUP",
            "SPRING",
            "CONSTRAINT",
        ],
        is_add_mode: bool = False,
    ):
        """
        対象UIリストのアクティブアイテムインデックスをオフセットしてエラーを回避する｡

        Parameters
        ----------
        component_type: Literal[
            "FIRST_PERSON",
            "EXPRESSION",
            "EXPRESSION_MORPH",
            "EXPRESSION_MATERIAL",
            "COLLIDER",
            "COLLIDER_GROUP",
            "SPRING",
            'CONSTRAINT',
        ]
            対象となるUIリストの種類

        is_add_mode : bool,  --optional
        by default : False
            Trueの場合は後方にオフセットする

        """

        self.update_ui_list_prop(component_type)

        index_root_prop = get_vrm1_index_root_prop()

        # 'component_type'の種類に応じて操作する属性名を定義する｡
        match component_type:
            case "FIRST_PERSON":
                list_items = get_ui_vrm1_first_person_prop()
                attr_name = "first_person"

            case "EXPRESSION":
                list_items = get_ui_vrm1_expression_prop()
                attr_name = "expression"

            case "EXPRESSION_MORPH":
                list_items = get_ui_vrm1_expression_morph_prop()
                attr_name = "expression_morph"

            case "EXPRESSION_MATERIAL":
                list_items = get_ui_vrm1_expression_material_prop()
                attr_name = "expression_material"

            case "COLLIDER":
                list_items = get_ui_vrm1_collider_prop()
                attr_name = "collider"

            case "COLLIDER_GROUP":
                list_items = get_ui_vrm1_collider_group_prop()
                attr_name = "collider_group"

            case "SPRING":
                list_items = get_ui_vrm1_spring_prop()
                attr_name = "spring"

            case "CONSTRAINT":
                list_items = get_ui_vrm1_constraint_prop()
                attr_name = "constraint"

        # ----------------------------------------------------------
        #    後方にオフセットする場合の処理
        # ----------------------------------------------------------
        if is_add_mode:
            try:
                new_value = getattr(index_root_prop, attr_name) + 1
                setattr(index_root_prop, attr_name, new_value)

            except:
                pass

            return

        # ----------------------------------------------------------
        #    前方にオフセットする場合の処理
        # ----------------------------------------------------------

        loop_count = 0
        while True:
            # UI Listアイテムのリストが空なら中断｡
            if not list_items:
                active_index = 0
                break

            # 無限ループの回避｡
            loop_count += 1
            if loop_count > 1000:
                active_index = 0
                logger.debug("Avoiding Infinite Loops")
                break

            try:
                active_index = max(get_vrm1_active_index_prop(component_type), 0)
                active_item = list_items[active_index]
                if active_index <= 0 or active_item.name != "Blank":
                    break
                set_new_value2index_prop(index_root_prop, attr_name)

            except:
                set_new_value2index_prop(index_root_prop, attr_name)

        setattr(index_root_prop, attr_name, active_index)


"""---------------------------------------------------------
    各オペレーター用サブクラス
---------------------------------------------------------"""


class VRMHELPER_vrm0_first_person_base(VRMHELPER_operator_base):
    vrm_mode = 0
    component_type: str = "FIRST_PERSON"


class VRMHELPER_vrm1_first_person_base(VRMHELPER_operator_base):
    vrm_mode = 1
    component_type: str = "FIRST_PERSON"


class VRMHELPER_vrm1_expression_base(VRMHELPER_operator_base):
    vrm_mode = 1
    component_type: str = "EXPRESSION"


class VRMHELPER_vrm1_expression_sub_morph(VRMHELPER_operator_base):
    vrm_mode = 1
    component_type: str = "EXPRESSION_MORPH"


class VRMHELPER_vrm1_expression_sub_material(VRMHELPER_operator_base):
    vrm_mode = 1
    component_type: str = "EXPRESSION_MATERIAL"


class VRMHELPER_vrm1_collider_base(VRMHELPER_operator_base):
    vrm_mode = 1
    component_type: str = "COLLIDER"


class VRMHELPER_vrm1_collider_group_base(VRMHELPER_operator_base):
    vrm_mode = 1
    component_type: str = "COLLIDER_GROUP"


class VRMHELPER_vrm1_spring_base(VRMHELPER_operator_base):
    vrm_mode = 1
    component_type: str = "SPRING"


class VRMHELPER_vrm1_constraint_base(VRMHELPER_operator_base):
    vrm_mode = 1
    component_type: str = "CONSTRAINT"

    constraint_type_dict: ConstraintTypeDict = {
        "ROLL": "COPY_ROTATION",
        "AIM": "DAMPED_TRACK",
        "ROTATION": "COPY_ROTATION",
    }

    constraint_name_dict: ConstraintTypeDict = {
        "ROLL": "VRM Roll Constraint",
        "AIM": "VRM Aim Constraint",
        "ROTATION": "VRM Rotation Constraint",
    }


"""---------------------------------------------------------
------------------------------------------------------------
    Resiter Target
------------------------------------------------------------
---------------------------------------------------------"""
CLASSES = (
    # ----------------------------------------------------------
    #    Common
    # ----------------------------------------------------------
    # VRMHELPER_OT_empty_operator,
    VRMHELPER_OT_evaluate_addon_collections,
    VRMHELPER_OT_reset_shape_keys_on_selected_objects,
)
