if "bpy" in locals():
    import importlib

    reloadable_modules = [
        "preparation_logger",
        "utils_common",
        "utils_vrm_base",
        "utils_vrm0_first_person",
    ]

    for module in reloadable_modules:
        if module in locals():
            importlib.reload(locals()[module])

else:
    from ..Logging import preparation_logger
    from .. import utils_common
    from .. import utils_vrm_base


import os, time, uuid
from pprint import pprint
from typing import (
    Literal,
)
import bpy
from bpy.props import (
    BoolProperty,
    FloatProperty,
    FloatVectorProperty,
    EnumProperty,
)

from mathutils import (
    Vector,
)

# from ..addon_classes import (
# )

from ..preferences import (
    get_addon_collection_name,
)

from ..property_groups import (
    VRMHELPER_WM_vrm1_constraint_list_items,
    # ---------------------------------------------------------------------------------
    get_target_armature,
    get_target_armature_data,
    # ----------------------------------------------------------
    get_ui_vrm0_first_person_prop,
    # ----------------------------------------------------------
    get_vrm0_index_root_prop,
    get_scene_vrm0_first_person_prop,
)

from ..utils_common import (
    filtering_mesh_type,
    link_object2collection,
    get_selected_bone,
    is_including_empty_in_selected_object,
    setting_vrm_helper_collection,
    get_all_materials_from_source_collection_objects,
    get_all_materials,
    reset_shape_keys_value,
)

from ..utils_vrm_base import (
    evaluation_expression_morph_collection,
    evaluation_expression_material_collection,
    get_vrm_extension_property,
    get_vrm1_extension_property_expression,
    is_existing_target_armature_and_mode,
    get_bones_for_each_branch_by_type,
    store_mtoon1_current_values,
    set_mtoon1_default_values,
    re_link_all_collider_object2collection,
)

from .utils_vrm0_first_person import (
    vrm0_search_same_name_mesh_annotation,
    vrm0_remove_mesh_annotation,
    vrm0_sort_mesh_annotations,
)

from ..operators import (
    VRMHELPER_operator_base,
    VRMHELPER_vrm0_first_person_base,
    # VRMHELPER_vrm0_expression_base,
    # VRMHELPER_vrm0_expression_sub_morph,
    # VRMHELPER_vrm0_expression_sub_material,
    # VRMHELPER_vrm0_collider_base,
    # VRMHELPER_vrm0_collider_group_base,
    # VRMHELPER_vrm0_spring_base,
    # VRMHELPER_vrm0_constraint_base,
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


class VRMHELPER_OT_vrm0_first_person_set_annotation(VRMHELPER_vrm0_first_person_base):
    bl_idname = "vrm_helper.vrm0_set_mesh_annotation"
    bl_label = "Set VRM0 Mesh Annotation"
    bl_description = "Add a new annotation to First Person Annotation and set the selected object to that bone_name"
    vrm_mode = "0"

    """
    選択されたオブジェクトをTarget ArmatureのVRM First Person Mesh Annotationに設定する｡
    Mesh Annotationのタイプは現在の描画モードの値が適用される｡
    """

    @classmethod
    def poll(cls, context):
        # 選択オブジェクト内にMeshタイプのオブジェクトが含まれていなければ使用不可｡
        return [obj for obj in context.selected_objects if filtering_mesh_type(obj)]

    def execute(self, context):
        mesh_annotations = get_vrm_extension_property("FIRST_PERSON").mesh_annotations
        annotation_type = get_scene_vrm0_first_person_prop().annotation_type

        # 選択オブジェクトの数だけMesh Annotationを追加する｡
        # 既にオブジェクトが存在する場合､Typeが異なれば値を更新､同じであれば処理をスキップする｡
        for obj in [
            obj for obj in context.selected_objects if filtering_mesh_type(obj)
        ]:
            if annotation := vrm0_search_same_name_mesh_annotation(obj.name):
                logger.debug(annotation.mesh.mesh_object_name)
                if annotation.first_person_flag == annotation_type:
                    continue
                annotation.first_person_flag = annotation_type
                continue

            else:
                new_item = mesh_annotations.add()
                new_item.mesh.mesh_object_name = obj.name
                new_item.first_person_flag = annotation_type

        # 登録された Mesh Annotationをタイプ毎に纏めてソートする｡
        vrm0_sort_mesh_annotations()

        return {"FINISHED"}


class VRMHELPER_OT_vrm0_first_person_remove_annotation_from_list(
    VRMHELPER_vrm0_first_person_base
):
    bl_idname = "vrm_helper.vrm0_remove_mesh_annotation_from_list"
    bl_label = "Remove Mesh Annotation from Active Item"
    bl_description = (
        "Remove active annotation in the list from Target Armature's VRM Extension"
    )
    vrm_mode = "0"

    """
    Target ArmatureのVRM Extensionから､リスト内で選択されているMesh Annotationを削除する｡
    """

    @classmethod
    def poll(cls, context):
        # Mesh Annotationが1つ以上存在しなければ使用不可｡
        return get_vrm_extension_property("FIRST_PERSON").mesh_annotations

    def execute(self, context):
        # アドオンのプロパティとVRM Extensionのプロパティを取得する｡
        list_items = get_ui_vrm0_first_person_prop()
        active_item_index = get_vrm0_index_root_prop().first_person
        active_item_name = list_items[active_item_index].name

        # オブジェクトの名前に一致するMesh Annotationを走査してVRM Extensionから削除する｡
        vrm0_remove_mesh_annotation(active_item_name)

        self.offset_active_item_index(self.component_type)

        return {"FINISHED"}


class VRMHELPER_OT_vrm0_first_person_remove_annotation_from_select_objects(
    VRMHELPER_vrm0_first_person_base
):
    bl_idname = "vrm_helper.vrm0_remove_mesh_annotation"
    bl_label = "Remove  Mesh Annotation by Selected Objects"
    bl_description = "Remove Mesh Annotations corresponding to selected objects from the VRM Extension"
    vrm_mode = "0"

    """
    Target ArmatureのVRM Extensionから､選択オブジェクトに対応したMesh Annotationを削除する｡
    """

    @classmethod
    def poll(cls, context):
        # Mesh Annotationが1つ以上存在しなければ使用不可｡
        return get_vrm_extension_property("FIRST_PERSON").mesh_annotations

    def execute(self, context):
        # アドオンのプロパティとVRM Extensionのプロパティを取得する｡

        # 選択オブジェクトの名前に一致するMesh Annotationを走査してVRM Extensionから削除する｡
        for obj in context.selected_objects:
            vrm0_remove_mesh_annotation(obj.name)

        self.offset_active_item_index(self.component_type)

        return {"FINISHED"}


class VRMHELPER_OT_vrm0_first_person_clear_annotation(VRMHELPER_vrm0_first_person_base):
    bl_idname = "vrm_helper.vrm0_clear_mesh_annotation"
    bl_label = "Clear Mesh Annotation"
    bl_description = "Remove all Mesh Annotations in Target Armature"
    vrm_mode = "0"

    """
    Target Armature内のVRM Extensionに設定された全てのMesh Annotationを削除する｡
    """

    @classmethod
    def poll(cls, context):
        # Mesh Annotationが1つ以上存在しなければ使用不可｡
        return get_vrm_extension_property("FIRST_PERSON").mesh_annotations

    def execute(self, context):
        mesh_annotations = get_vrm_extension_property("FIRST_PERSON").mesh_annotations
        mesh_annotations.clear()

        self.offset_active_item_index(self.component_type)

        return {"FINISHED"}


"""---------------------------------------------------------
------------------------------------------------------------
    Resiter Target
------------------------------------------------------------
---------------------------------------------------------"""
CLASSES = (
    # ----------------------------------------------------------
    #    Common
    # ----------------------------------------------------------
    # ----------------------------------------------------------
    #    First Perxon
    # --------------------------------------------==========================--------------
    VRMHELPER_OT_vrm0_first_person_set_annotation,
    VRMHELPER_OT_vrm0_first_person_remove_annotation_from_list,
    VRMHELPER_OT_vrm0_first_person_remove_annotation_from_select_objects,
    VRMHELPER_OT_vrm0_first_person_clear_annotation,
)
