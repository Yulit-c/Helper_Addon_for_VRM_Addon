if "bpy" in locals():
    import importlib

    reloadable_modules = [
        "preparation_logger",
        "utils_common",
        "utils_vrm_base",
        "utils_vrm1_first_person",
        "utils_vrm1_expression",
        "utils_vrm1_spring",
        "utils_vrm1_constraint",
        "operators",
    ]

    for module in reloadable_modules:
        if module in locals():
            importlib.reload(locals()[module])

else:
    from ..Logging import preparation_logger
    from .. import utils_common
    from .. import utils_vrm_base
    from . import utils_vrm1_first_person
    from . import utils_vrm1_expression
    from . import utils_vrm1_spring
    from . import utils_vrm1_constraint
    from . import vrm1_operators


import os, math, time, uuid
from typing import (
    Literal,
)
import bpy
from bpy.types import (
    Material,
    Object,
    PoseBone,
    CopyRotationConstraint,
    DampedTrackConstraint,
)
from bpy.props import (
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    EnumProperty,
)

from mathutils import (
    Vector,
)

from ..addon_classes import (
    ReferenceVrm1TextureTransformBindPropertyGroup,
    ReferenceVrm1ColliderPropertyGroup,
    ReferenceVrm1ColliderGroupPropertyGroup,
    ReferenceSpringBone1ColliderReferencePropertyGroup,
    ReferenceSpringBone1SpringPropertyGroup,
    ReferenceSpringBone1JointPropertyGroup,
    VRMHELPER_VRM_joint_operator_property,
)

from ..preferences import (
    get_addon_collection_name,
)

from ..property_groups import (
    VRMHELPER_WM_vrm1_constraint_list_items,
    # ---------------------------------------------------------------------------------
    get_target_armature,
    get_target_armature_data,
    # ---------------------------------------------------------------------------------
    get_ui_vrm1_first_person_prop,
    get_ui_vrm1_expression_prop,
    get_ui_vrm1_expression_morph_prop,
    get_ui_vrm1_expression_material_prop,
    get_ui_bone_group_prop,
    get_ui_vrm1_operator_collider_group_prop,
    get_ui_vrm1_operator_spring_prop,
    get_ui_vrm1_constraint_prop,
    # ---------------------------------------------------------------------------------
    get_vrm1_index_root_prop,
    get_vrm1_active_index_prop,
    get_scene_vrm1_first_person_prop,
    get_scene_vrm1_spring_prop,
    get_scene_vrm1_constraint_prop,
    get_scene_vrm1_mtoon_stored_prop,
)

from ..utils_common import (
    filtering_mesh_type,
    link_object2collection,
    get_active_bone,
    get_selected_bone,
    get_selected_bone_names,
    get_pose_bone_by_name,
    generate_head_collider_position,
    generate_tail_collider_position,
    filtering_empty_from_selected_objects,
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
    reset_shape_keys_value_in_morph_binds,
    store_mtoon_current_values,
    set_mtoon_default_values,
    re_link_all_collider_object2collection,
    add_list_item2bone_group_list4operator,
)

from .utils_vrm1_first_person import (
    vrm1_search_same_name_mesh_annotation,
    vrm1_remove_mesh_annotation,
    vrm1_sort_mesh_annotations,
)

from .utils_vrm1_expression import (
    vrm1_add_items2expression_ui_list,
    get_active_list_item_in_expression,
    get_active_expression,
    search_existing_morph_bind_and_update,
    convert_str2color_bind_type,
    search_existing_material_color_bind_and_update,
    convert_str2transform_bind_type,
    search_existing_texture_transform_bind_and_update,
    set_mtoon1_colors_from_bind,
    set_mtoon1_texture_transform_from_bind,
)

from .utils_vrm1_spring import (
    # ----------------------------------------------------------
    #    Collidaer
    # ----------------------------------------------------------
    remove_vrm1_collider_by_selected_object,
    get_ui_list_index_from_collider_component,
    # ----------------------------------------------------------
    #    Collider Group
    # ----------------------------------------------------------
    get_active_list_item_in_collider_group,
    get_operator_target_collider_group,
    # ----------------------------------------------------------
    #    Spring
    # ----------------------------------------------------------
    get_active_list_item_in_spring,
    remove_vrm1_spring_collider_group_when_removed_collider_group,
    vrm1_add_list_item2collider_group_list4operator,
    vrm1_add_list_item2joint_list4operator,
)

from .utils_vrm1_constraint import (
    vrm1_add_items2constraint_ui_list,
    detect_constrainted_and_target_element,
    set_vrm_constraint_parametters,
    detect_constraint_or_label,
    remove_existing_vrm_constraint,
)

from ..operators import (
    VRMHELPER_operator_base,
    VRMHELPER_vrm1_first_person_base,
    VRMHELPER_vrm1_expression_base,
    VRMHELPER_vrm1_expression_sub_morph,
    VRMHELPER_vrm1_expression_sub_material,
    VRMHELPER_vrm1_collider_base,
    VRMHELPER_vrm1_collider_group_base,
    VRMHELPER_vrm1_spring_base,
    VRMHELPER_vrm1_constraint_base,
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


class VRMHELPER_OT_vrm1_first_person_set_annotation(VRMHELPER_vrm1_first_person_base):
    bl_idname = "vrm_helper.set_mesh_annotation_1"
    bl_label = "Set VRM1 Mesh Annotation"
    bl_description = (
        "Add a new annotation to First Person Annotation and set the selected object to that bone_name"
    )

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
        annotation_type = get_scene_vrm1_first_person_prop().annotation_type

        # 選択オブジェクトの数だけMesh Annotationを追加する｡
        # 既にオブジェクトが存在する場合､Typeが異なれば値を更新､同じであれば処理をスキップする｡
        for obj in [obj for obj in context.selected_objects if filtering_mesh_type(obj)]:
            if annotation := vrm1_search_same_name_mesh_annotation(obj.name):
                logger.debug(annotation.node.mesh_object_name)
                if annotation.type == annotation_type:
                    continue
                annotation.type = annotation_type
                continue

            else:
                new_item = mesh_annotations.add()
                new_item.node.mesh_object_name = obj.name
                new_item.type = annotation_type

        # 登録された Mesh Annotationをタイプ毎に纏めてソートする｡
        vrm1_sort_mesh_annotations()

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_first_person_remove_annotation_from_list(VRMHELPER_vrm1_first_person_base):
    bl_idname = "vrm_helper.vrm1_remove_mesh_annotation_from_list"
    bl_label = "Remove Mesh Annotation from Active Item"
    bl_description = "Remove active annotation in the list from Target Armature's VRM Extension"

    """
    Target ArmatureのVRM Extensionから､リスト内で選択されているMesh Annotationを削除する｡
    """

    @classmethod
    def poll(cls, context):
        # Mesh Annotationが1つ以上存在しなければ使用不可｡
        return get_vrm_extension_property("FIRST_PERSON").mesh_annotations

    def execute(self, context):
        # アドオンのプロパティとVRM Extensionのプロパティを取得する｡
        list_items = get_ui_vrm1_first_person_prop()
        active_item_index = get_vrm1_index_root_prop().first_person
        active_item_name = list_items[active_item_index].name

        # オブジェクトの名前に一致するMesh Annotationを走査してVRM Extensionから削除する｡
        vrm1_remove_mesh_annotation(active_item_name)

        self.offset_active_item_index(self.component_type)

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_first_person_remove_annotation_from_select_objects(VRMHELPER_vrm1_first_person_base):
    bl_idname = "vrm_helper.vrm1_remove_mesh_annotation"
    bl_label = "Remove  Mesh Annotation by Selected Objects"
    bl_description = "Remove Mesh Annotations corresponding to selected objects from the VRM Extension"

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
            vrm1_remove_mesh_annotation(obj.name)

        self.offset_active_item_index(self.component_type)

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_first_person_clear_annotation(VRMHELPER_vrm1_first_person_base):
    bl_idname = "vrm_helper.clear_mesh_annotation"
    bl_label = "Clear Mesh Annotation"
    bl_description = "Remove all Mesh Annotations in Target Armature"

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
    Expression
---------------------------------------------------------"""


# ----------------------------------------------------------
#    Expressions
# ----------------------------------------------------------
class VRMHELPER_OT_vrm1_expression_create_custom_expression(VRMHELPER_vrm1_expression_base):
    bl_idname = "vrm_helper.vrm1_expression_create_custom_expression"
    bl_label = "Create Custom Expression"
    bl_description = "Create a new custom expression to the target armature"
    bl_options = {"UNDO"}

    def execute(self, context):
        vrm1_expresions = get_vrm1_extension_property_expression()
        custom_expressions = vrm1_expresions.custom
        new_item = custom_expressions.add()
        new_item.custom_name = "custom_expression"

        # VRM Addon側のUI Listを更新する｡
        bpy.ops.vrm.update_vrm1_expression_ui_list_elements()

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_expression_remove_custom_expression(VRMHELPER_vrm1_expression_base):
    bl_idname = "vrm_helper.vrm1_expression_remove_custom_expression"
    bl_label = "Remove Custom Expression"
    bl_description = "Remove the active custom expression from the target armature"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        # アクティブアイテムがカスタムエクスプレッションである
        return (active_item := get_active_list_item_in_expression()) and not active_item.expression_index[
            1
        ] < 0

    def execute(self, context):
        vrm1_expresions = get_vrm1_extension_property_expression()
        custom_expressions = vrm1_expresions.custom
        active_item = get_active_list_item_in_expression()
        custom_expressions.remove(active_item.expression_index[1])

        self.offset_active_item_index(self.component_type)

        # VRM Addon側のUI Listを更新する｡
        bpy.ops.vrm.update_vrm1_expression_ui_list_elements()

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_expression_clear_custom_expression(VRMHELPER_vrm1_expression_base):
    bl_idname = "vrm_helper.vrm1_expression_clear_custom_expression"
    bl_label = "Clear Custom Expression"
    bl_description = "Clear all custom expressions from the target armature"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        # Expressionsにカスタムエクスプレッションが1つ以上存在している
        vrm1_expresions = get_vrm1_extension_property_expression()
        custom_expressions = vrm1_expresions.custom
        return custom_expressions

    def execute(self, context):
        vrm1_expresions = get_vrm1_extension_property_expression()
        custom_expressions = vrm1_expresions.custom
        custom_expressions.clear()

        self.offset_active_item_index(self.component_type)

        # VRM Addon側のUI Listを更新する｡
        bpy.ops.vrm.update_vrm1_expression_ui_list_elements()

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_expression_move_custom_expression(VRMHELPER_vrm1_expression_base):
    bl_idname = "vrm_helper.vrm1_expression_move_custom_expression"
    bl_label = "Move Custom Expression"
    bl_description = "Reorder active custom expression"
    bl_options = {"UNDO"}

    move_direction: EnumProperty(
        name="Move Direction",
        description="Choose whether to move it up or down.",
        items=(
            ("UP", "Up", "Move active custom expression up"),
            ("DOWN", "Down", "Move active custom expression down"),
        ),
        default="UP",
    )

    @classmethod
    def poll(cls, context):
        # アクティブアイテムがカスタムエクスプレッションである
        return (active_item := get_active_list_item_in_expression()) and not active_item.expression_index[
            1
        ] < 0

    def execute(self, context):
        active_expression = get_active_expression()
        stored_expression_name = active_expression.custom_name
        target_armature = get_target_armature()

        # Custom Expressionを移動する
        match self.move_direction:
            case "UP":
                bpy.ops.vrm.move_up_vrm1_expressions_custom_expression(
                    armature_name=target_armature.name,
                    custom_expression_name=stored_expression_name,
                )

            case "DOWN":
                bpy.ops.vrm.move_down_vrm1_expressions_custom_expression(
                    armature_name=target_armature.name,
                    custom_expression_name=stored_expression_name,
                )

        # Expressionリストの更新
        vrm1_add_items2expression_ui_list()
        expressions_list = get_ui_vrm1_expression_prop()
        for n, expression in enumerate(expressions_list):
            if expression.name == stored_expression_name:
                index_prop = get_vrm1_index_root_prop()
                index_prop.expression = n

        return {"FINISHED"}


# ----------------------------------------------------------
#    Morph Target
# ----------------------------------------------------------
class VRMHELPER_OT_vrm1_expression_morph_create_morph(VRMHELPER_vrm1_expression_sub_morph):
    bl_idname = "vrm_helper.vrm1_expression_morph_create_morph"
    bl_label = "Create Morph Target Bind"
    bl_description = "Create a new morph target bind to the active expression"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        # アクティブなエクスプレッションが存在する
        return get_active_expression()

    def execute(self, context):
        morph_target_binds = get_active_expression().morph_target_binds

        new_morph_bind = morph_target_binds.add()
        # アクティブオブジェクトが選択状態であれば追加したMorph Targetにバインドする｡
        if not all(
            (
                (active_object := context.active_object) in context.selected_objects,
                active_object.type == "MESH",
            )
        ):
            return {"FINISHED"}

        new_morph_bind.node.mesh_object_name = context.object.name
        # アクティブオブジェクトのメッシュにシェイプキーが存在する｡
        if not (sk := active_object.data.shape_keys):
            return {"FINISHED"}

        # アクティブシェイプキーがリファレンスではない｡
        if (
            active_shape_key := active_object.active_shape_key
        ) == sk.reference_key:  # or active_shape_key.value == 0:
            return {"FINISHED"}

        # アクティブオブジェクト/シェイプキーのペアがMorph Target Bindに登録済みであればシェイプキーの現在の値に更新する｡
        # 作成した'new_morph_bind'は削除する｡
        is_existing_bind = search_existing_morph_bind_and_update(
            active_object, active_shape_key, morph_target_binds
        )

        if is_existing_bind:
            morph_target_binds.remove(len(morph_target_binds) - 1)
            self.offset_active_item_index("EXPRESSION_MORPH")
            return {"FINISHED"}

        if not active_shape_key.value == 0:
            new_morph_bind.index = active_shape_key.name
            new_morph_bind.weight = active_shape_key.value

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_expression_morph_remove_morph(VRMHELPER_vrm1_expression_sub_morph):
    bl_idname = "vrm_helper.vrm1_expression_morph_remove_morph"
    bl_label = "Remove Morph Target Bind"
    bl_description = "Remove the active morph target bind from the active expression"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        # アクティブアイテムがシェイプキーである
        if morphs := get_ui_vrm1_expression_morph_prop():
            return morphs[get_vrm1_active_index_prop("EXPRESSION_MORPH")].item_type[1]

    def execute(self, context):
        morphs = get_ui_vrm1_expression_morph_prop()
        active_item = morphs[get_vrm1_active_index_prop("EXPRESSION_MORPH")]

        morph_target_binds = get_active_expression().morph_target_binds
        morph_target_binds.remove(active_item.bind_index)

        self.offset_active_item_index(self.component_type)

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_expression_morph_clear_morphs(VRMHELPER_vrm1_expression_sub_morph):
    bl_idname = "vrm_helper.vrm1_expression_morph_clear_morphs"
    bl_label = "Clear Morph Target Binds"
    bl_description = "Clear all morph target binds from the active expression"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        if active_expression := get_active_expression():
            return active_expression.morph_target_binds

    def execute(self, context):
        get_active_expression().morph_target_binds.clear()
        get_vrm1_index_root_prop().expression_morph = 0

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_expression_set_morph_from_scene(VRMHELPER_vrm1_expression_sub_morph):
    bl_idname = "vrm_helper.vrm1_expression_set_morph_from_scene"
    bl_label = "Set Morph Target from Scene"
    bl_description = "Set Morph Target Bind from the shape keys of the target objects on the scene"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        # 1つ以上のオブジェクトがリンクされた'VRM1 Expression Morph'のコレクションが存在する｡
        return evaluation_expression_morph_collection()

    def execute(self, context):
        morph_target_binds = get_active_expression().morph_target_binds
        source_collection = bpy.data.collections.get(get_addon_collection_name("VRM1_EXPRESSION_MORPH"))

        for obj in source_collection.all_objects:
            # オブジェクトのメッシュデータに2つ以上のキーブロックを持ったシェイプキーが存在する｡
            if not (sk := obj.data.shape_keys) and len(sk.key_blocks) <= 1:
                continue

            logger.debug(f"###\n{'':#>100}\nCurrent Processed Object : {obj.name}\n{'':#>100}")
            for shape_key in (k for k in sk.key_blocks if k != sk.reference_key):
                # objとシェイプキーのペアがMorph Target Bindに登録済みであればシェイプキーの現在の値に更新する｡
                # 値が0だった場合はBindを削除する｡
                is_existing_bind = search_existing_morph_bind_and_update(
                    obj,
                    shape_key,
                    morph_target_binds,
                )

                # objとシェイプキーのペアがBindに未登録かつシェイプキーの値が0超過であった場合は新規登録する｡
                if not is_existing_bind:
                    if shape_key.value == 0:
                        continue
                    logger.debug(f"Registered New Bind -- {obj.name} : {shape_key.name}")
                    new_morph_bind = morph_target_binds.add()
                    new_morph_bind.node.mesh_object_name = obj.name
                    new_morph_bind.index = shape_key.name
                    new_morph_bind.weight = shape_key.value

        self.offset_active_item_index(self.component_type)

        return {"FINISHED"}


# ----------------------------------------------------------
#    Material Color & Texture Transform
# ----------------------------------------------------------


class VRMHELPER_OT_vrm1_expression_change_bind_material(VRMHELPER_vrm1_expression_sub_material):
    bl_idname = "vrm_helper.vrm1_expression_change_bind_material"
    bl_label = "Change Bind Material"
    bl_description = "Change the material of the active bind"
    bl_options = {"UNDO"}
    bl_property = "material_name"

    material_name: EnumProperty(
        name="Target Material",
        description="Materials to be applied for binding",
        items=get_all_materials,
    )

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        self.offset_active_item_index(self.component_type)
        # マテリアル選択メニューポップアップ
        context.window_manager.invoke_search_popup(self)
        return {"FINISHED"}

    def execute(self, context):
        material_binds_list = get_ui_vrm1_expression_material_prop()
        current_index = get_vrm1_index_root_prop().expression_material
        active_item = material_binds_list[current_index]
        old_bind_material = bpy.data.materials.get(active_item.bind_material_name)
        new_bind_material = bpy.data.materials.get(self.material_name)

        active_expression = get_active_expression()
        # アクティブアイテムが'Material Label', 'Color Bind', 'Transform Bind'のいずれであるかに応じて
        # 処理対象のグループを決定する｡

        # Material Labelの場合
        target_material_color_binds = {
            bind for bind in active_expression.material_color_binds if bind.material == old_bind_material
        }
        target_transform_bind_binds = {
            bind for bind in active_expression.texture_transform_binds if bind.material == old_bind_material
        }
        match active_item.name:
            case "Material Color":
                target_binds = target_material_color_binds

            case "Texture Transform":
                target_binds = target_transform_bind_binds

            case _:
                target_binds = target_material_color_binds | target_transform_bind_binds

        for bind in target_binds:
            bind.material = new_bind_material
            logger.debug(f"{bind} -->> {new_bind_material.name}")

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_expression_material_create_color(VRMHELPER_vrm1_expression_sub_material):
    bl_idname = "vrm_helper.vrm1_expression_material_create_color"
    bl_label = "Create Material Color Bind"
    bl_description = "Create a new material color bind to the active expression"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        # アクティブなエクスプレッションが存在する
        return get_active_expression()

    def execute(self, context):
        material_color_binds = get_active_expression().material_color_binds
        new_item = material_color_binds.add()

        if (
            (obj_act := context.active_object)
            and obj_act in context.selected_objects
            and obj_act.material_slots
        ):
            new_item.material = obj_act.active_material

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_expression_material_remove_color(VRMHELPER_vrm1_expression_sub_material):
    bl_idname = "vrm_helper.vrm1_expression_material_remove_color"
    bl_label = "Remove Material Color Bind"
    bl_description = "Remove the active material color bind from the active expression"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        # アクティブアイテムがMaterial Colorである
        if materials := get_ui_vrm1_expression_material_prop():
            return materials[get_vrm1_active_index_prop("EXPRESSION_MATERIAL")].item_type[1]

    def execute(self, context):
        materials = get_ui_vrm1_expression_material_prop()
        active_item = materials[get_vrm1_active_index_prop("EXPRESSION_MATERIAL")]

        material_color_binds = get_active_expression().material_color_binds
        material_color_binds.remove(active_item.bind_index)

        self.offset_active_item_index(self.component_type)

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_expression_material_clear_colors(VRMHELPER_vrm1_expression_sub_material):
    bl_idname = "vrm_helper.vrm1_expression_material_clear_colors"
    bl_label = "Clear Morph Target Binds"
    bl_description = "Clear all morph target binds from the active expression"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        # アクティブエクスプレッションにMaterial Color Bindが存在している
        if active_expression := get_active_expression():
            return active_expression.material_color_binds

    def execute(self, context):
        get_active_expression().material_color_binds.clear()
        self.offset_active_item_index(self.component_type)

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_expression_material_create_transform(VRMHELPER_vrm1_expression_sub_material):
    bl_idname = "vrm_helper.vrm1_expression_material_create_transform"
    bl_label = "Create Material Color Bind"
    bl_description = "Create a new texture transform bind to the active expression"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        # アクティブなエクスプレッションが存在する
        return get_active_expression()

    def execute(self, context):
        texture_transform_binds = get_active_expression().texture_transform_binds
        new_item = texture_transform_binds.add()

        if (
            (obj_act := context.active_object)
            and obj_act in context.selected_objects
            and obj_act.material_slots
        ):
            new_item.material = obj_act.active_material

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_expression_material_remove_transform(VRMHELPER_vrm1_expression_sub_material):
    bl_idname = "vrm_helper.vrm1_expression_material_remove_transform"
    bl_label = "Remove Material Color Bind"
    bl_description = "Remove the active texture transform bind from the active expression"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        # アクティブアイテムがMaterial Colorである
        if materials := get_ui_vrm1_expression_material_prop():
            return materials[get_vrm1_active_index_prop("EXPRESSION_MATERIAL")].item_type[2]

    def execute(self, context):
        materials = get_ui_vrm1_expression_material_prop()
        active_item = materials[get_vrm1_active_index_prop("EXPRESSION_MATERIAL")]

        texture_transform_binds = get_active_expression().texture_transform_binds
        texture_transform_binds.remove(active_item.bind_index)

        self.offset_active_item_index(self.component_type)

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_expression_material_clear_transforms(VRMHELPER_vrm1_expression_sub_material):
    bl_idname = "vrm_helper.vrm1_expression_material_clear_transforms"
    bl_label = "Clear Morph Target Binds"
    bl_description = "Clear all texture transform binds from the active expression"
    bl_options = {"UNDO"}

    @classmethod
    # アクティブエクスプレッションにテクスチャトランスフォームバインドが存在している
    def poll(cls, context):
        if active_expression := get_active_expression():
            return active_expression.texture_transform_binds

    def execute(self, context):
        get_active_expression().texture_transform_binds.clear()
        self.offset_active_item_index(self.component_type)

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_expression_set_material_bind_from_scene(VRMHELPER_vrm1_expression_sub_material):
    bl_idname = "vrm_helper.vrm1_expression_set_material_bind_from_scene"
    bl_label = "Set Material Bind from Scene"
    bl_description = "Set Material Bind from the material of the target objects on the scene"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        # 1つ以上のオブジェクトがリンクされた'VRM1 Expression Material'のコレクションが存在する｡
        return evaluation_expression_material_collection()

    def execute(self, context):
        os.system("cls")

        active_expression = get_active_expression()
        material_color_binds = active_expression.material_color_binds
        texture_transform_binds = active_expression.texture_transform_binds
        source_collection = bpy.data.collections.get(get_addon_collection_name("VRM1_EXPRESSION_MATERIAL"))

        # ソースとなるマテリアルを取得する(MToon指定されているもののみ)｡
        source_materials = {
            slot.material
            for obj in source_collection.all_objects
            for slot in obj.material_slots
            if slot.material and slot.material.vrm_addon_extension.mtoon1.enabled
        }

        def get_index(element):
            return list(bpy.data.materials).index(element)

        source_materials = sorted(list(source_materials), key=get_index)

        for source_material in source_materials:
            logger.debug("\n\n")
            logger.debug(source_material.name)
            # ----------------------------------------------------------
            #    Material Color Bindに対する処理
            # ----------------------------------------------------------
            # ソースマテリアルに設定されたMToonパラメーターに応じてMaterial Color Bindを登録する｡
            # 既に登録済みのマテリアル､パラメーターの組み合わせだった場合は値を更新する｡初期値に設定される場合はバインドを削除する｡
            print(f"\n{'':#>50}\nMaterial Color Bind Process\n{'':#>50}")
            mtoon_color_parameters_dict = search_existing_material_color_bind_and_update(
                source_material, material_color_binds
            )

            # 未登録であった場合は新規登録する｡
            for type, value in mtoon_color_parameters_dict.items():
                if value:
                    logger.debug(f"Set Type : {type}")
                    if len(value) < 4:
                        value.append(1.0)
                    new_color_bind = material_color_binds.add()
                    new_color_bind.material = source_material
                    new_color_bind.type = convert_str2color_bind_type(type)
                    new_color_bind.target_value = value

            # ----------------------------------------------------------
            #    Texture Transform Bindに対する処理
            # ----------------------------------------------------------
            # ソースマテリアルに設定されたMToonパラメーターに応じてTexture Transform Bindを登録する｡
            # 既に登録済みのマテリアル､パラメーターの組み合わせだった場合は値を更新する｡初期値に設定される場合はバインドを削除する｡
            print(f"\n{'':#>50}\nTexture Transform Bind Process\n{'':#>50}")
            mtoon_transform_parameters_dict = search_existing_texture_transform_bind_and_update(
                source_material, texture_transform_binds
            )

            # 未登録であった場合は新規登録する｡
            if not mtoon_transform_parameters_dict:
                logger.debug("condition 1")
                continue

            if not any(mtoon_transform_parameters_dict.values()):
                logger.debug("condition 2")
                continue

            new_transform_bind: ReferenceVrm1TextureTransformBindPropertyGroup = texture_transform_binds.add()
            for parameter, value in mtoon_transform_parameters_dict.items():
                if value:
                    converted_parameter_name = convert_str2transform_bind_type(parameter)
                    logger.debug(f"Set Parameter : {converted_parameter_name} -- {value}")
                    new_transform_bind.material = source_material
                    setattr(new_transform_bind, converted_parameter_name, value)
        # TODO : Lit Color以外のTexture Transformの値をLit Colorと同じにする｡

        # ----------------------------------------------------------
        self.offset_active_item_index("EXPRESSION_MATERIAL")

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_expression_store_mtoon1_parameters(VRMHELPER_vrm1_expression_sub_material):
    bl_idname = "vrm_helper.vrm1_expression_store_mtoon1_parameters"
    bl_label = "Store MToon1 Parameters"
    bl_description = "Obtains and stores the current parameters of Mtoon1"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        # 1つ以上のオブジェクトがリンクされた'VRM1 Expression'のコレクションが存在する｡
        return (
            c := bpy.data.collections.get(get_addon_collection_name("VRM1_EXPRESSION_MATERIAL"))
        ) and c.all_objects

    def execute(self, context):
        os.system("cls")
        source_collection = bpy.data.collections.get(get_addon_collection_name("VRM1_EXPRESSION_MATERIAL"))
        mtoon1_stored_parameters = get_scene_vrm1_mtoon_stored_prop()
        mtoon1_stored_parameters.clear()

        for mat in get_all_materials_from_source_collection_objects(source_collection):
            logger.debug(f"Stored MToon1 Parameters : {mat.name}")
            new_item = mtoon1_stored_parameters.add()
            new_item.name = mat.name
            store_mtoon_current_values(new_item, mat)

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_expression_discard_stored_mtoon1_parameters(VRMHELPER_vrm1_expression_sub_material):
    bl_idname = "vrm_helper.vrm1_expression_discard_stored_mtoon1_parameters"
    bl_label = "Discard Stored MToon1 Parameters"
    bl_description = "Discard stored parameters of Mtoon1"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        return get_scene_vrm1_mtoon_stored_prop()

    def execute(self, context):
        get_scene_vrm1_mtoon_stored_prop().clear()
        return {"FINISHED"}


class VRMHELPER_OT_vrm1_expression_restore_mtoon1_parameters(VRMHELPER_vrm1_expression_sub_material):
    bl_idname = "vrm_helper.vrm1_expression_restore_mtoon1_parameters"
    bl_label = "Restore MToon1 Parameters"
    bl_description = "Restore stored parameters of Mtoon1"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        return (
            c := bpy.data.collections.get(get_addon_collection_name("VRM1_EXPRESSION_MATERIAL"))
        ) and c.all_objects

    def execute(self, context):
        source_collection = bpy.data.collections.get(get_addon_collection_name("VRM1_EXPRESSION_MATERIAL"))

        for mat in get_all_materials_from_source_collection_objects(source_collection):
            set_mtoon_default_values(mat)

        # TODO : Lit Color以外のTexture Transformの値をLit Colorと同じにする｡

        return {"FINISHED"}


# ----------------------------------------------------------
#    Morph & Material Binds
# ----------------------------------------------------------
class VRMHELPER_OT_vrm1_expression_set_both_binds_from_scene(VRMHELPER_vrm1_expression_sub_material):
    bl_idname = "vrm_helper.vrm1_expression_set_both_binds_from_scene"
    bl_label = "Set Both Binds from Scene"
    bl_description = "Set Morph/Material Binds from the scene"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        morph_condition = evaluation_expression_morph_collection()
        mat_condition = evaluation_expression_morph_collection()
        return morph_condition and mat_condition

    def execute(self, context):
        os.system("cls")
        active_expression = get_active_expression()
        # ----------------------------------------------------------
        #    Morph Target Bind
        # ----------------------------------------------------------
        morph_target_binds = active_expression.morph_target_binds
        source_collection = bpy.data.collections.get(get_addon_collection_name("VRM1_EXPRESSION_MORPH"))

        for obj in source_collection.all_objects:
            # オブジェクトのメッシュデータに2つ以上のキーブロックを持ったシェイプキーが存在する｡
            if not (sk := obj.data.shape_keys) and len(sk.key_blocks) <= 1:
                continue

            logger.debug(f"###\n{'':#>100}\nCurrent Processed Object : {obj.name}\n{'':#>100}")
            for shape_key in (k for k in sk.key_blocks if k != sk.reference_key):
                # objとシェイプキーのペアがMorph Target Bindに登録済みであればシェイプキーの現在の値に更新する｡
                # 値が0だった場合はBindを削除する｡
                is_existing_bind = search_existing_morph_bind_and_update(
                    obj,
                    shape_key,
                    morph_target_binds,
                )

                # objとシェイプキーのペアがBindに未登録かつシェイプキーの値が0超過であった場合は新規登録する｡
                if not is_existing_bind:
                    if shape_key.value == 0:
                        continue
                    logger.debug(f"Registered New Bind -- {obj.name} : {shape_key.name}")
                    new_morph_bind = morph_target_binds.add()
                    new_morph_bind.node.mesh_object_name = obj.name
                    new_morph_bind.index = shape_key.name
                    new_morph_bind.weight = shape_key.value

        self.offset_active_item_index(self.component_type)

        # ----------------------------------------------------------
        #    Material Color Bind & Texture Transform Bind
        # ----------------------------------------------------------

        material_color_binds = active_expression.material_color_binds
        texture_transform_binds = active_expression.texture_transform_binds
        source_collection_mat = bpy.data.collections.get(
            get_addon_collection_name("VRM1_EXPRESSION_MATERIAL")
        )

        # ソースとなるマテリアルを取得する｡
        source_materials = {
            slot.material
            for obj in source_collection_mat.all_objects
            for slot in obj.material_slots
            if slot.material and slot.material.vrm_addon_extension.mtoon1.enabled
        }

        def get_index(element):
            return list(bpy.data.materials).index(element)

        source_materials = sorted(list(source_materials), key=get_index)
        for source_material in source_materials:
            logger.debug("\n\n")
            logger.debug(source_material.name)
            # ----------------------------------------------------------
            #    Material Color Bindに対する処理
            # ----------------------------------------------------------
            # ソースマテリアルに設定されたMToonパラメーターに応じてMaterial Color Bindを登録する｡
            # 既に登録済みのマテリアル､パラメーターの組み合わせだった場合は値を更新する｡初期値に設定される場合はバインドを削除する｡
            print(f"\n{'':#>50}\nMaterial Color Bind Process\n{'':#>50}")
            mtoon_color_parameters_dict = search_existing_material_color_bind_and_update(
                source_material, material_color_binds
            )

            # 未登録であった場合は新規登録する｡
            for type, value in mtoon_color_parameters_dict.items():
                if value:
                    logger.debug(f"Set Type : {type}")
                    if len(value) < 4:
                        value.append(1.0)
                    new_color_bind = material_color_binds.add()
                    new_color_bind.material = source_material
                    new_color_bind.type = convert_str2color_bind_type(type)
                    new_color_bind.target_value = value

            # ----------------------------------------------------------
            #    Texture Transform Bindに対する処理
            # ----------------------------------------------------------
            # ソースマテリアルに設定されたMToonパラメーターに応じてTexture Transform Bindを登録する｡
            # 既に登録済みのマテリアル､パラメーターの組み合わせだった場合は値を更新する｡初期値に設定される場合はバインドを削除する｡
            print(f"\n{'':#>50}\nTexture Transform Bind Process\n{'':#>50}")
            mtoon_transform_parameters_dict = search_existing_texture_transform_bind_and_update(
                source_material, texture_transform_binds
            )

            # 未登録であった場合は新規登録する｡
            if not mtoon_transform_parameters_dict:
                logger.debug("condition 1")
                continue

            if not any(mtoon_transform_parameters_dict.values()):
                logger.debug("condition 2")
                continue

            new_transform_bind = texture_transform_binds.add()
            for parameter, value in mtoon_transform_parameters_dict.items():
                if value:
                    converted_parameter_name = convert_str2transform_bind_type(parameter)
                    logger.debug(f"Set Parameter : {converted_parameter_name} -- {value}")

                    new_transform_bind.material = source_material
                    setattr(new_transform_bind, converted_parameter_name, value)
        # TODO : Lit Color以外のTexture Transformの値をLit Colorと同じにする｡

        # ----------------------------------------------------------
        self.offset_active_item_index("EXPRESSION_MATERIAL")

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_expression_restore_initial_parameters(VRMHELPER_vrm1_expression_sub_material):
    bl_idname = "vrm_helper.vrm1_expression_restore_initial_values"
    bl_label = "Restore Initial State"
    bl_description = "Restore Mesh and Material to their initial state"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        morph_condition = evaluation_expression_morph_collection()
        mat_condition = evaluation_expression_material_collection()
        return morph_condition or mat_condition

    def execute(self, context):
        # ----------------------------------------------------------
        #    Morph Target Bind
        # ----------------------------------------------------------
        if source_collection_morph := bpy.data.collections.get(
            get_addon_collection_name("VRM1_EXPRESSION_MORPH")
        ):
            for obj in {obj for obj in source_collection_morph.all_objects if obj.type == "MESH"}:
                reset_shape_keys_value(obj.data)

        # ----------------------------------------------------------
        #    Material Color Bind & Texture Transform Bind
        # ----------------------------------------------------------
        if source_collection_mat := bpy.data.collections.get(
            get_addon_collection_name("VRM1_EXPRESSION_MATERIAL")
        ):
            # 対象コレクション内のすべてのオブジェクトが持つマテリアルにパラメーターの復元処理を行う｡
            for mat in get_all_materials_from_source_collection_objects(source_collection_mat):
                set_mtoon_default_values(mat)

            # TODO : Lit Color以外のTexture Transformの値をLit Colorと同じにする｡

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_expression_assign_expression_to_scene(VRMHELPER_vrm1_expression_sub_material):
    bl_idname = "vrm_helper.vrm1_expression_assign_expression_to_scene"
    bl_label = "Assign Expression"
    bl_description = "Active expression settings are reflected on the scene"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        # TODO : いずれかのバインドが1つ以上存在する｡
        return True

    def execute(self, context):
        # アクティブエクスプレッションと各Bindsを取得する｡
        active_expression = get_active_expression()
        morph_target_binds = active_expression.morph_target_binds
        material_color_binds = active_expression.material_color_binds
        texture_transform_binds = active_expression.texture_transform_binds

        # ----------------------------------------------------------
        #    Morph Target Binds
        # ----------------------------------------------------------
        # アクティブエクスプレッションのMorpth Target Bindsの全てのBindの
        # メッシュ/シェイプキーに対してウェイトを反映する｡
        # 対象メッシュは処理前に全てのシェイプキーのウェイトを0にする｡
        reset_shape_keys_value_in_morph_binds(morph_target_binds)

        # Morph Target Bindに設定されているBlend Shapeの値を対応するShape Keyの値に代入する｡
        existing_bind_info = {}
        for bind in morph_target_binds:
            if not (reference_object := bpy.data.objects.get(bind.node.mesh_object_name)):
                continue
            bind_mesh = reference_object.data
            existing_bind_info.setdefault(bind_mesh, []).append((bind.index, bind.weight))

        for mesh, sk_info in existing_bind_info.items():
            for sk_name, sk_value in sk_info:
                if sk := mesh.shape_keys.key_blocks.get(sk_name):
                    sk.value = sk_value

        # Color/Transform Bindで指定されている全てのマテリアルの特定パラメーターは一度すべて初期値にセットする｡
        if existing_bind_material := {bind.material for bind in material_color_binds} | {
            bind.material for bind in texture_transform_binds
        }:
            for mat in existing_bind_material:
                if not mat:
                    continue
                logger.debug(f"Reset Values : {mat.name}")
                set_mtoon_default_values(mat)

        expression_material_collection = bpy.data.collections.get(
            get_addon_collection_name("VRM1_EXPRESSION_MATERIAL")
        )
        if expression_material_collection.all_objects:
            bpy.ops.vrm_helper.vrm1_expression_restore_mtoon1_parameters()
            # ----------------------------------------------------------
            #    Material Color Binds
            # ----------------------------------------------------------
            # アクティブエクスプレッションのMaterial Color Bindsの全てのBindの
            # Materialに対してパラメーターを反映する｡
            for color_bind in material_color_binds:
                set_mtoon1_colors_from_bind(color_bind)

            # ----------------------------------------------------------
            #    Texture Transform Binds
            # ----------------------------------------------------------
            # アクティブエクスプレッションのTexture Transform Bindsの全てのBindの
            # Materialに対してパラメーターを反映する｡
            for transform_bind in texture_transform_binds:
                set_mtoon1_texture_transform_from_bind(transform_bind)

            # TODO : Lit Color以外のTexture Transformの値をLit Colorと同じにする｡

        return {"FINISHED"}


"""---------------------------------------------------------
    Spring Bone
---------------------------------------------------------"""


# ----------------------------------------------------------
#    Collider
# ----------------------------------------------------------
class VRMHELPER_OT_vrm1_collider_create_from_bone(VRMHELPER_vrm1_collider_base):
    bl_idname = "vrm_helper.vrm1_collider_create_from_bone"
    bl_label = "Create Collider"
    bl_description = "Create spring bone collider from selected bone"

    collider_type: EnumProperty(
        name="Collider Type",
        description="Type of collider to be created",
        items=(
            ("Sphere", "Sphere", "The type of collider created becomes a sphere"),
            ("Capsule", "Capsule", "The type of collider created becomes a capsule"),
        ),
        default="Capsule",
        options={"HIDDEN"},
    )

    collider_radius: FloatProperty(
        name="Collider Radius",
        description="Radius of the collider to be created",
        default=0.05,
        unit="LENGTH",
        options={"HIDDEN"},
    )

    @classmethod
    def poll(cls, context):
        # Target Armatureの1ボーンを1つ以上選択していなければ使用不可｡
        return is_existing_target_armature_and_mode()

    def execute(self, context):
        os.system("cls")
        time_start = time.perf_counter()
        target_armature = get_target_armature()
        armature_data: bpy.types.Armature = target_armature.data
        colliders = get_vrm_extension_property("COLLIDER")
        addon_collection_dict = setting_vrm_helper_collection()
        dest_collection = addon_collection_dict["VRM1_COLLIDER"]

        # 処理中はプロパティのアップデートのコールバック関数をロックする｡
        index_prop = get_vrm1_index_root_prop()
        index_prop.is_locked_update = True

        # 選択ボーン全てに対してコライダーを作成してパラメーターをセットする｡
        # Target Armature.dataの'use_mirror_x'が有効の場合は処理の間は無効化する｡
        is_changed_use_mirror = False
        if armature_data.use_mirror_x:
            armature_data.use_mirror_x = False
            is_changed_use_mirror = True

        # bones = context.selected_bones if context.selected_bones else context.selected_pose_bones
        bones = get_selected_bone()
        for bone in bones:
            pose_bone = get_pose_bone_by_name(target_armature, bone.name)
            new_item: ReferenceVrm1ColliderPropertyGroup = colliders.add()
            new_item.uuid = uuid.uuid4().hex

            # コライダーのタイプ､半径､位置を設定
            new_item.shape_type = self.collider_type
            new_item.node.bone_name = pose_bone.name

            if self.collider_type == "Sphere":
                new_item.shape.sphere.radius = self.collider_radius
                collider_object = new_item.bpy_object
                mid_point = (pose_bone.tail + pose_bone.head) / 2
                collider_object.matrix_world = generate_head_collider_position(mid_point)
                # コライダーオブジェクトを対象コレクションにリンクする｡
                link_object2collection(collider_object, dest_collection)
                # コライダーオブジェクトを選択状態およびアクティブオブジェクトに設定する｡
                collider_object.select_set(True)
                bpy.context.view_layer.objects.active = collider_object

            if self.collider_type == "Capsule":
                # コライダーオブジェクトの作成･初期化｡
                new_item.reset_bpy_object(context, target_armature)
                new_item.shape.capsule.radius = self.collider_radius

                # コライダーオブジェクトの位置設定｡
                collider_head: bpy.types.Object = new_item.bpy_object
                collider_tail: bpy.types.Object = new_item.bpy_object.children[0]
                collider_head.matrix_world = generate_head_collider_position(pose_bone.head)
                collider_head.rotation_euler = Vector((0, 0, 0))
                collider_tail.matrix_basis = generate_tail_collider_position(
                    target_armature, pose_bone, pose_bone.tail
                )
                # コライダーオブジェクトを対象コレクションにリンクする｡
                re_link_all_collider_object2collection()
                # コライダーオブジェクトを選択状態およびアクティブオブジェクトに設定する｡
                collider_head.select_set(True)
                context.view_layer.objects.active = collider_head

        # 'use_mirror_x'の値を変更していた場合は元に戻す｡
        if is_changed_use_mirror:
            armature_data.use_mirror_x = True

        # Object Modeに移行してArmature Objectの選択を解除する｡
        bpy.ops.object.mode_set(mode="OBJECT")
        target_armature.select_set(False)

        # 最後に作成したコライダーをリスト内のアクティブアイテムに設定する｡
        if updated_active_index := get_ui_list_index_from_collider_component(new_item):
            index_prop.collider = updated_active_index
        index_prop.is_locked_update = False

        logger.debug(f"Processing Time : {time.perf_counter() - time_start:.3f} s")
        return {"FINISHED"}


class VRMHELPER_OT_vrm1_collider_remove_from_empty(VRMHELPER_vrm1_collider_base):
    bl_idname = "vrm_helper.vrm1_collider_remove_from_empty"
    bl_label = "Remove Collider"
    bl_description = "Remove spring bone collider from selected empty object"

    @classmethod
    def poll(cls, context):
        # 選択オブジェクトにEmptyが含まれていなければ使用不可｡
        return filtering_empty_from_selected_objects()

    def execute(self, context):
        # 処理中はプロパティのアップデートのコールバック関数をロックする｡
        index_prop = get_vrm1_index_root_prop()
        index_prop.is_locked_update = True

        # 選択Emptyオブジェクトのうち､コライダーとして登録されているものがあればコライダー設定とともに削除する｡
        logger.debug("Remove Collider & Empty Object")
        for obj in filtering_empty_from_selected_objects():
            remove_vrm1_collider_by_selected_object(obj)

        # アクティブインデックスをオフセットしてエラーを回避する｡
        logger.debug("Offset UI List Index : Collider")
        self.offset_active_item_index(self.component_type)
        logger.debug("Offset UI List Index : Collider Group")
        self.offset_active_item_index("COLLIDER_GROUP")
        logger.debug("Offset UI List Index : Spring")
        self.offset_active_item_index("SPRING")
        index_prop.is_locked_update = False

        return {"FINISHED"}


# ----------------------------------------------------------
#    Collider Group
# ----------------------------------------------------------
class VRMHELPER_OT_vrm1_collider_group_add_group(VRMHELPER_vrm1_collider_group_base):
    bl_idname = "vrmhelper.vrm1_collider_group_add_group"
    bl_label = "Add Collider Group"
    bl_description = "Add a new VRM1 Spring Bone Collider Group"

    def execute(self, context):
        new_group = get_vrm_extension_property("COLLIDER_GROUP").add()
        new_group.vrm_name = "New Collider Group"
        new_group.uuid = uuid.uuid4().hex

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_collider_group_remove_active_group(VRMHELPER_vrm1_collider_group_base):
    bl_idname = "vrmhelper.vrm1_collider_group_remove_active_group"
    bl_label = "Remove Collider Group"
    bl_description = "Remove the collider group that is active in the list."

    @classmethod
    def poll(self, context):
        # Collider Groupが存在しており､リストのアクティブアイテムがラベルではない｡
        return (ai := get_active_list_item_in_collider_group()) and (ai.item_type[1])

    def execute(self, context):
        os.system("cls")

        # アクティブアイテムのインデックスを取得する｡
        active_item = get_active_list_item_in_collider_group()
        active_indexes = active_item.item_indexes

        collider_groups = get_vrm_extension_property("COLLIDER_GROUP")

        # 対象コライダーグループを参照していたスプリングの値を更新後に対象を削除する｡その後アクティブインデックスを更新する｡
        remove_vrm1_spring_collider_group_when_removed_collider_group(collider_groups[active_indexes[0]].name)
        collider_groups.remove(active_indexes[0])
        self.offset_active_item_index(self.component_type)

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_collider_group_clear_group(VRMHELPER_vrm1_collider_group_base):
    bl_idname = "vrmhelper.vrm1_collider_group_clear_group"
    bl_label = "Clear Collider Group"
    bl_description = "Clear all collider groups."

    @classmethod
    def poll(self, context):
        # Collider Groupが存在する｡
        return get_vrm_extension_property("COLLIDER_GROUP")

    def execute(self, context):
        os.system("cls")

        for collider_group in (collider_groups := get_vrm_extension_property("COLLIDER_GROUP")):
            remove_vrm1_spring_collider_group_when_removed_collider_group(collider_group.name)

        collider_groups.clear()
        get_vrm1_index_root_prop().collider_group = 0
        self.offset_active_item_index("SPRING")

        return {"FINISHED"}


"""---------------------------------------------------------
    TODO : Move(Up, Down) Operator
---------------------------------------------------------"""


class VRMHELPER_OT_vrm1_collider_group_add_collider(VRMHELPER_vrm1_collider_group_base):
    bl_idname = "vrmhelper.vrm1_collider_group_add_collider"
    bl_label = "Add Collider"
    bl_description = "Add a new collider to the active group"

    @classmethod
    def poll(self, context):
        # アクティブアイテムがラベル以外である｡
        return (ai := get_active_list_item_in_collider_group()) and not ai.item_type[0]

    def execute(self, context):
        os.system("cls")
        active_indexes = get_active_list_item_in_collider_group().item_indexes
        get_vrm_extension_property("COLLIDER_GROUP")[active_indexes[0]].colliders.add()

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_collider_group_remove_collider(VRMHELPER_vrm1_collider_group_base):
    bl_idname = "vrmhelper.vrm1_collider_group_remove_collider"
    bl_label = "Remove Collider"
    bl_description = "Remove the active collider from group"

    @classmethod
    def poll(self, context):
        # アクティブアイテムがColliderである｡
        return (ai := get_active_list_item_in_collider_group()) and ai.item_type[2]

    def execute(self, context):
        active_indexes = get_active_list_item_in_collider_group().item_indexes
        get_vrm_extension_property("COLLIDER_GROUP")[active_indexes[0]].colliders.remove(active_indexes[1])

        get_vrm1_index_root_prop().collider_group -= 1

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_collider_group_clear_collider(VRMHELPER_vrm1_collider_group_base):
    bl_idname = "vrmhelper.vrm1_collider_group_clear_collider"
    bl_label = "Clear Collider"
    bl_description = "Remove all colliders linked to the active group"

    @classmethod
    def poll(self, context):
        # アクティブアイテムがCollider GroupかつそのグループにColliderが存在する｡
        return (
            (active_item := get_active_list_item_in_collider_group())
            and not (active_item.item_type[0])
            and get_vrm_extension_property("COLLIDER_GROUP")[active_item.item_indexes[0]].colliders
        )

    def execute(self, context):
        os.system("cls")
        active_indexes = get_active_list_item_in_collider_group().item_indexes
        get_vrm_extension_property("COLLIDER_GROUP")[active_indexes[0]].colliders.clear()

        self.offset_active_item_index(self.component_type)

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_collider_group_register_collider_from_bone(VRMHELPER_operator_base):
    bl_idname = "vrmhelper.vrm1_collider_group_register_collider_from_bone"
    bl_label = "Create from Bone"
    bl_description = "Registers the colliders linked to the selected bone to the active collider group"

    @classmethod
    def poll(cls, context):
        # Target Armatureのボーンが1つ以上選択されている｡
        return is_existing_target_armature_and_mode()

    def execute(self, context):
        active_group = get_active_list_item_in_collider_group()
        colliders = get_vrm_extension_property("COLLIDER")
        collider_group = get_vrm_extension_property("COLLIDER_GROUP")
        if collider_group:
            # アクティブなコライダーグループを取得する｡
            target_group: ReferenceVrm1ColliderGroupPropertyGroup = collider_group[
                active_group.item_indexes[0]
            ]
            target_group_colliders = target_group.colliders
        else:
            # Collider Groupが1つも存在しない場合は新たにグループを作成する｡
            new_group: ReferenceVrm1ColliderGroupPropertyGroup = collider_group.add()
            new_group.vrm_name = "New Collider Group"
            new_group.uuid = uuid.uuid4().hex
            target_group_colliders = new_group.colliders

        # 選択されたボーンの名前を'node.bone_name'で参照している､全てのコライダーを取得する｡
        # 選択ボーンの名前を取得する
        bone_names_of_selected_bone: set[str] = set(get_selected_bone_names())

        # 登録済みコライダーグループからボーン名のセットを取得する｡
        registered_colliders = {i.collider_uuid for i in target_group_colliders}
        bone_names_of_existing_colliders: set[str] = {
            i.node.bone_name for i in colliders if i.uuid in registered_colliders
        }

        registrable_names = bone_names_of_selected_bone - bone_names_of_existing_colliders
        if context.mode == "EDIT_ARMATURE":
            bpy.ops.object.posemode_toggle()

        # 1つのボーンにつき1つのコライダーのみを登録する｡登録済みのコライダーは登録しない｡
        exist_names = set()
        source_collider_names = set()
        for i in colliders:
            if i.node.bone_name in exist_names or not i.node.bone_name in registrable_names:
                continue
            exist_names.add(i.node.bone_name)
            source_collider_names.add(i.name)

        # 取得したコライダーをアクティブなコライダーグループに登録する｡
        # 空のグループが存在する場合､そちらに値を代入する｡
        for collider_name in source_collider_names:
            if empty_item := [i for i in target_group_colliders if not i.collider_name]:
                empty_item[0].collider_name = collider_name

            else:
                target_group_colliders.add().collider_name = collider_name

        return {"FINISHED"}


# ----------------------------------------------------------
#    Spring
# ----------------------------------------------------------
class VRMHELPER_OT_vrm1_spring_add_spring(VRMHELPER_vrm1_spring_base):
    bl_idname = "vrmhelper.vrm1_spring_add_spring"
    bl_label = "Add Spring"
    bl_description = "Add a new VRM1 Spring"

    def execute(self, context):
        new_spring = get_vrm_extension_property("SPRING").add()
        new_spring.vrm_name = "New Spring"

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_spring_remove_spring(VRMHELPER_vrm1_spring_base):
    bl_idname = "vrmhelper.vrm1_spring_remove_spring"
    bl_label = "Add Spring"
    bl_description = "Remove the active spring from spring"

    @classmethod
    def poll(self, context):
        # UIリストのアイテムが存在し､アクティブアイテムがブランク以外である｡
        return (active_item := get_active_list_item_in_spring()) and active_item.name

    def execute(self, context):
        # アクティブアイテムのインデックスを取得する｡
        active_item = get_active_list_item_in_spring()
        active_indexes = active_item.item_indexes

        spring = get_vrm_extension_property("SPRING")

        spring.remove(active_indexes[0])
        self.offset_active_item_index(self.component_type)

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_spring_clear_spring(VRMHELPER_vrm1_spring_base):
    bl_idname = "vrmhelper.vrm1_spring_clear_spring"
    bl_label = "Clear Spring"
    bl_description = "Remove all springs from spring"

    def execute(self, context):
        get_vrm_extension_property("SPRING").clear()
        get_vrm1_index_root_prop().spring = 0

        return {"FINISHED"}


# -----------------------------------------------------


class VRMHELPER_OT_vrm1_spring_add_joint(VRMHELPER_vrm1_spring_base, VRMHELPER_VRM_joint_operator_property):
    bl_idname = "vrmhelper.vrm1_spring_add_joint"
    bl_label = "Add Joint"
    bl_description = "Add a new joint to the active spring"

    # ----------------------------------------------------------
    #    Property
    # ----------------------------------------------------------
    use_auto_joint_parametter: BoolProperty(
        name="Use Auto Joint Parameter",
        description="Whether the parameters of a newly created joint inherit from the parent joint or not",
        default=False,
        options={"HIDDEN"},
    )

    # -----------------------------------------------------

    @classmethod
    def poll(self, context):
        # アクティブアイテムがジョイントまたはジョイントのラベルである｡
        return (active_item := get_active_list_item_in_spring()) and (
            active_item.item_type[2] or active_item.name == "Joint"
        )

    def execute(self, context):
        target_armature = get_target_armature_data()
        active_indexes = get_active_list_item_in_spring().item_indexes
        joints = get_vrm_extension_property("SPRING")[active_indexes[0]].joints
        new_joint = joints.add()

        # 可能であれば2個前のジョイントの情報を取得し､新しく作成したジョイントの値を自動で設定する｡
        try:
            two_previous_joint = joints[-3]
            two_previous_bone = target_armature.bones.get(two_previous_joint.node.bone_name)
            previous_joint = joints[-2]
            previous_bone = target_armature.bones.get(previous_joint.node.bone_name)
            if previous_bone.parent == two_previous_bone:
                new_joint.node.bone_name = previous_bone.children[0].name

            # 'assign_from_parent_joint'がTrueであれば親ボーンのジョイントからパラメーターを引き継ぐ｡
            if self.use_auto_joint_parametter:
                new_joint.hit_radius = previous_joint.hit_radius
                new_joint.stiffness = previous_joint.stiffness
                new_joint.drag_force = previous_joint.drag_force
                new_joint.gravity_power = previous_joint.gravity_power
                new_joint.gravity_dir = previous_joint.gravity_dir

                return {"FINISHED"}

            else:
                raise Exception

        except:
            new_joint.hit_radius = self.hit_radius
            new_joint.stiffness = self.stiffness
            new_joint.drag_force = self.drag_force
            new_joint.gravity_power = self.gravity_power
            new_joint.gravity_dir = self.gravity_dir

            return {"FINISHED"}


class VRMHELPER_OT_vrm1_spring_remove_joint(VRMHELPER_vrm1_spring_base):
    bl_idname = "vrmhelper.vrm1_spring_remove_joint"
    bl_label = "Remove Joint"
    bl_description = "Remove active joint from spring"

    @classmethod
    def poll(self, context):
        # アクティブアイテムがジョイントである
        return (active_item := get_active_list_item_in_spring()) and active_item.item_type[2]

    def execute(self, context):
        active_indexes = get_active_list_item_in_spring().item_indexes
        get_vrm_extension_property("SPRING")[active_indexes[0]].joints.remove(active_indexes[1])
        get_vrm1_index_root_prop().spring -= 1

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_spring_clear_joint(VRMHELPER_vrm1_spring_base):
    bl_idname = "vrmhelper.spring_clear_joint"
    bl_label = "Clear Joint"
    bl_description = "Remove all joints from spring"

    @classmethod
    def poll(self, context):
        # アクティブアイテムがジョイント､またはジョイントのラベルでありジョイントが存在する｡
        if active_indexes := get_active_list_item_in_spring().item_indexes:
            return (
                get_vrm_extension_property("SPRING")[active_indexes[0]].joints
                and (active_item := get_active_list_item_in_spring())
                and (active_item.item_type[2] or active_item.name == "Joint")
            )

    def execute(self, context):
        active_indexes = get_active_list_item_in_spring().item_indexes
        get_vrm_extension_property("SPRING")[active_indexes[0]].joints.clear()
        self.offset_active_item_index(self.component_type)

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_spring_add_joint_from_source(
    VRMHELPER_vrm1_spring_base, VRMHELPER_VRM_joint_operator_property
):
    bl_idname = "vrmhelper.vrm1_spring_create_joint_from_selected"
    bl_label = "Create Joint"
    bl_description = "Create spring joints from selected bones or bone groups"

    # ----------------------------------------------------------
    #    Property
    # ----------------------------------------------------------
    source_type: EnumProperty(
        name="Source Type",
        description="Description",
        items=(
            ("SELECT", "Selected Bone", "Get source from selected bones"),
            ("BONE_GROUP", "Bone Group", "Get source from bone groups"),
        ),
        default="SELECT",
    )

    rows_property: IntProperty(
        name="Rows Property",
        description="Number of properties displayed per column",
        default=12,
    )
    # -----------------------------------------------------

    def invoke(self, context, event):
        match self.source_type:
            case "SELECT":
                vrm1_add_list_item2collider_group_list4operator()
                return context.window_manager.invoke_props_dialog(self, width=360)

            case "BONE_GROUP":
                add_list_item2bone_group_list4operator()
                vrm1_add_list_item2collider_group_list4operator()
                if not (bone_groups := get_ui_bone_group_prop()):
                    self.report({"INFO"}, "Bone group does not exist in Target Armature")
                    return {"CANCELLED"}
                width_popup = math.ceil(len(bone_groups) / self.rows_property) * 240
                return context.window_manager.invoke_props_dialog(self, width=width_popup)

            case _:
                return {"CANCELLED"}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)

        # 処理対象のボーングループを選択するエリア｡
        if self.source_type == "BONE_GROUP":
            bone_group_collection = get_ui_bone_group_prop()
            anchor_layout = row.column(align=True)
            box_sub = anchor_layout.box()
            box_sub.label(text="Target Bone Group")
            row_root = box_sub.row()
            for n, group in enumerate(bone_group_collection):
                if n % self.rows_property == 0:
                    col = row_root.column()
                row_sub = col.row(align=True)
                row_sub.prop(group, "is_target", text=group.name)

        # 処理対象のコライダーグループを選択するエリア｡
        anchor_layout = row.column(align=True)
        if self.source_type == "BONE_GROUP":
            anchor_layout = anchor_layout.box()
        anchor_layout.label(text="Target Collider Group")
        collider_group_collection = get_ui_vrm1_operator_collider_group_prop()
        for group in collider_group_collection:
            row_sub = anchor_layout.row(align=True)
            row_sub.prop(group, "is_target", text=group.vrm_name)

    def execute(self, context):
        os.system("cls")

        # # 処理対象となるボーンを､枝毎にグルーピングされた状態で取得する｡
        if not (target_bones := get_bones_for_each_branch_by_type(self.source_type, get_target_armature())):
            return {"CANCELLED"}

        springs = get_vrm_extension_property("SPRING")
        spring_and_joint_dicts = [{spring: [joint for joint in spring.joints]} for spring in springs]

        # 取得したボーンのリストから枝毎にスプリングを作成し､そのスプリングに対してジョイントを登録する｡
        for branch in target_bones:
            damping = 1.0

            # 枝に含まれているボーンがいずれかのスプリングに登録されている場合はそのスプリングのジョインツに追記する｡
            target_joints = None
            for dict in spring_and_joint_dicts:
                spring: ReferenceSpringBone1SpringPropertyGroup
                for spring, joints in dict.items():
                    if {i.name for i in branch} & {i.node.bone_name for i in joints}:
                        target_joints = spring.joints

            # いずれのスプリングにも登録されていない場合は新規スプリングを作成する｡
            if not target_joints:
                spring = springs.add()
                spring.vrm_name = branch[0].name
                target_joints = spring.joints

            # 枝に含まれているボーンを枝毎に別のグループとして､対象のスプリングのジョイントに登録する｡
            for bone in branch:
                if bone.name in [i.node.bone_name for i in target_joints]:
                    logger.debug(f"Already Registered : {bone.name}")
                    continue
                # ボーンが登録されていないジョイントが存在する場合､そちらに値を代入する｡
                logger.debug(f"Source Bone : {bone.name}")
                target_item: ReferenceSpringBone1JointPropertyGroup
                if empty_item := [i for i in target_joints if not i.node.bone_name]:
                    target_item = empty_item[0]
                else:
                    target_item = target_joints.add()

                target_item.node.bone_name = bone.name
                target_item.hit_radius = self.hit_radius
                target_item.stiffness = self.stiffness * damping
                target_item.drag_force = self.drag_force * damping
                target_item.gravity_power = self.gravity_power
                target_item.gravity_dir[0] = self.gravity_dir[0]
                target_item.gravity_dir[1] = self.gravity_dir[1]
                target_item.gravity_dir[2] = self.gravity_dir[2]

                damping *= self.damping_ratio

            # スプリング毎にコライダーグループの設定を行なう｡
            source_collider_groups = [
                i
                for i in get_vrm_extension_property("COLLIDER_GROUP")
                if i.name in get_operator_target_collider_group()
            ]
            target_collider_groups = spring.collider_groups
            for group in source_collider_groups:
                if group.name in [i.collider_group_name for i in target_collider_groups]:
                    logger.debug(f"Already Registered : {group.vrm_name}")
                    continue
                target_group = target_collider_groups.add()
                target_group.collider_group_name = group.name

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_spring_assign_parameters_to_joints(
    VRMHELPER_vrm1_spring_base, VRMHELPER_VRM_joint_operator_property
):
    bl_idname = "vrmhelper.vrm1_spring_assign_parameters_to_selected_joints"
    bl_label = "Assign Joints Parameters"
    bl_description = "Create spring joints from selected bones"

    # ----------------------------------------------------------
    #    Property
    # ----------------------------------------------------------
    source_type: EnumProperty(
        name="Source Type",
        description="Description",
        items=(
            ("SINGLE", "Single", "Works only on active joints"),
            ("MULTIPLE", "Multiple", "Works only on selected joints"),
        ),
        default="SINGLE",
    )

    rows_property: IntProperty(
        name="Rows Property",
        description="Number of properties displayed per column",
        default=12,
    )

    # -----------------------------------------------------

    def invoke(self, context, event):
        os.system("cls")

        vrm1_add_list_item2joint_list4operator()
        vrm1_add_list_item2collider_group_list4operator()
        match self.source_type:
            case "MULTIPLE":
                spring_collection = get_ui_vrm1_operator_spring_prop()
                # フィルターワードに従ってスプリングの中から対象候補を抽出する｡
                spring_settings = get_scene_vrm1_spring_prop()
                if filter_strings := spring_settings.filter_of_adjusting_target_filter:
                    spring_collection = [i for i in spring_collection if filter_strings in i.name]
                width_popup = math.ceil(len(spring_collection) / self.rows_property) * 240
                return context.window_manager.invoke_props_dialog(self, width=width_popup)

            case "SINGLE":
                # 'source_type'が'SINGLE'の場合はアクティブなスプリングのみをターゲットに設定する｡
                active_indexes = get_active_list_item_in_spring().item_indexes
                for spring in get_ui_vrm1_operator_spring_prop():
                    if spring.spring_index != active_indexes[0]:
                        spring.is_target = False
                return self.execute(context)

    def draw(self, context):
        # 処理対象のボーングループを選択するエリア｡
        # if self.source_type == "BONE_GROUP":
        #     bone_group_collection = get_ui_bone_group_prop()
        #     anchor_layout = row.column(align=True)
        #     box_sub = anchor_layout.box()
        #     box_sub.label(text="Target Bone Group")
        #     row_root = box_sub.row()
        #     for n, group in enumerate(bone_group_collection):
        #         if n % self.rows_property == 0:
        #             col = row_root.column()
        #         row_sub = col.row(align=True)
        #         row_sub.prop(group, "is_target", text=group.name)

        spring_collection = get_ui_vrm1_operator_spring_prop()
        collider_group_collection = get_ui_vrm1_operator_collider_group_prop()

        # フィルターワードに従ってスプリングの中から対象候補を抽出する｡
        spring_settings = get_scene_vrm1_spring_prop()
        if filter_strings := spring_settings.filter_of_adjusting_target_filter:
            spring_collection = [i for i in spring_collection if filter_strings in i.name]
        # UIの描画
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        anchor_layout = row.column(align=True)
        anchor_layout.label(text="Target Spring")
        box_sub = anchor_layout.box()
        box_sub.separator(factor=0.1)
        row = box_sub.row()
        row_root = box_sub.row()
        for n, spring in enumerate(spring_collection):
            if n % self.rows_property == 0:
                col = row_root.column()
            row_sub = col.row(align=True)
            row_sub.prop(spring, "is_target", text=spring.name)

        # 処理対象のコライダーグループを選択するエリア｡
        anchor_layout = row.column(align=True)
        anchor_layout.label(text="Target Collider Group")
        for group in collider_group_collection:
            row_sub = anchor_layout.row(align=True)
            row_sub.prop(group, "is_target", text=group.vrm_name)

    def execute(self, context):
        # TODO : 処理内でターゲットのCollider Groupを追加する｡
        springs = get_vrm_extension_property("SPRING")
        springs_collection = get_ui_vrm1_operator_spring_prop()

        # フィルターワードに従ってスプリングの中から対象候補を抽出する｡
        spring_settings = get_scene_vrm1_spring_prop()
        springs_filter_list = []
        if filter_strings := spring_settings.filter_of_adjusting_target_filter:
            springs_filter_list = [i.name for i in springs_collection if filter_strings in i.name]

        # ターゲットに設定されたスプリング毎に､登録されたジョイントに減衰率を加味しつつ値を適用する｡
        spring: ReferenceSpringBone1SpringPropertyGroup
        for spring, filter in zip(springs, springs_collection):
            if springs_filter_list and not spring.vrm_name in springs_filter_list:
                logger.debug(f"Skip 0 : {spring.vrm_name}")
                continue

            if not filter.is_target:
                logger.debug(f"Skip 1 : {spring.vrm_name}")
                continue

            damping = 1.0
            joint: ReferenceSpringBone1JointPropertyGroup
            for joint in spring.joints:
                joint.hit_radius = self.hit_radius
                joint.stiffness = self.stiffness * damping
                joint.drag_force = self.drag_force * damping
                joint.gravity_power = self.gravity_power
                joint.gravity_dir[0] = self.gravity_dir[0]
                joint.gravity_dir[1] = self.gravity_dir[1]
                joint.gravity_dir[2] = self.gravity_dir[2]

                damping *= self.damping_ratio

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_spring_pick_radius_from_active_bone(
    VRMHELPER_vrm1_spring_base, VRMHELPER_VRM_joint_operator_property
):
    bl_idname = "vrmhelper.vrm1_spring_pick_radius_from_active_bone"
    bl_label = "Pick Radius from Active Bone"
    bl_description = "Get the hit radius of the spring bone joint corresponding to the active bone and reflect it in the parameters on the UI"

    def execute(self, context):
        spring_prop = get_scene_vrm1_spring_prop()
        spring_prop.is_updated_hit_radius = True  # コールバック無効化

        # アクティブボーンni対応するスプリングボーンジョイントを取得する
        if not (active_bone := get_active_bone()):
            self.report({"ERROR"}, f"Active bone does not exist")
            return {"CANCELLED"}

        springs = get_vrm_extension_property("SPRING")
        if not (
            corresponding_joint := [
                j for i in springs for j in i.joints if j.node.bone_name == active_bone.name
            ]
        ):
            self.report({"INFO"}, f"No corresponding Spring Bone Joint exists")
            return {"CANCELLED"}

        corresponding_joint: ReferenceSpringBone1JointPropertyGroup = corresponding_joint[0]
        active_bone_radius = corresponding_joint.hit_radius
        spring_prop.active_bone_hit_radius = active_bone_radius

        self.report({"INFO"}, f"Obtained Hit Radius : ;{active_bone_radius}")
        spring_prop.is_updated_hit_radius = False  # コールバック無効化を解除
        return {"FINISHED"}


# -----------------------------------------------------


class VRMHELPER_OT_vrm1_spring_add_collider_group(VRMHELPER_vrm1_spring_base):
    bl_idname = "vrmhelper.vrm1_spring_add_collider_group"
    bl_label = "Add Collider Group"
    bl_description = "Add a new collider group to the active spring"

    @classmethod
    def poll(self, context):
        # アクティブアイテムがコライダーグループまたはコライダーグループのラベルである｡
        return (active_item := get_active_list_item_in_spring()) and (
            active_item.item_type[3] or active_item.name == "Collider Group"
        )

    def execute(self, context):
        active_indexes = get_active_list_item_in_spring().item_indexes
        collider_groups = get_vrm_extension_property("SPRING")[active_indexes[0]].collider_groups
        collider_groups.add()

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_spring_remove_collider_group(VRMHELPER_vrm1_spring_base):
    bl_idname = "vrmhelper.vrm1_spring_remove_collider_group"
    bl_label = "Remove Collider Group"
    bl_description = "Remove active collider group from spring"

    @classmethod
    def poll(self, context):
        # アクティブアイテムがコライダーグループである｡
        return (active_item := get_active_list_item_in_spring()) and active_item.item_type[3]

    def execute(self, context):
        active_indexes = get_active_list_item_in_spring().item_indexes
        get_vrm_extension_property("SPRING")[active_indexes[0]].collider_groups.remove(active_indexes[2])
        get_vrm1_index_root_prop().spring -= 1

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_spring_clear_collider_group(VRMHELPER_vrm1_spring_base):
    bl_idname = "vrmhelper.vrm1_spring_clear_collider_group"
    bl_label = "Clear Collider Group"
    bl_description = "Remove all collider groups from spring"

    @classmethod
    def poll(self, context):
        # アクティブアイテムがコライダーグループ､またはコライダーグループのラベルでありコライダーグループが存在する｡
        if active_indexes := get_active_list_item_in_spring().item_indexes:
            return (
                get_vrm_extension_property("SPRING")[active_indexes[0]].collider_groups
                and (active_item := get_active_list_item_in_spring())
                and (active_item.item_type[3] or active_item.name == "Collider Group")
            )

    def execute(self, context):
        active_indexes = get_active_list_item_in_spring().item_indexes
        get_vrm_extension_property("SPRING")[active_indexes[0]].collider_groups.clear()
        self.offset_active_item_index(self.component_type)

        return {"FINISHED"}


"""---------------------------------------------------------
    Constrait
---------------------------------------------------------"""


class VRMHELPER_OT_vrm1_constraint_add_vrm_constraint(VRMHELPER_vrm1_constraint_base):
    bl_idname = "vrmhelper.vrm1_constraint_add"
    bl_label = "Add Constraint"
    bl_description = "Create a VRM constraint of the specified type"
    bl_options = {"UNDO"}

    constraint_type: EnumProperty(
        name="Constraint Type",
        description="Define the type of constraint to be created",
        items=(
            ("ROLL", "Roll Constraint", "Create a roll constraint"),
            ("AIM", "Aim Constraint", "Create a aim constraint"),
            ("ROTATION", "Rotation Constraint", "Create a rotation constraint"),
        ),
        default="ROLL",
    )

    @classmethod
    def poll(cls, context):
        # カレントモードがObject/Poseモードである
        if not context.mode in {"OBJECT", "POSE"}:
            return False

        return all(detect_constrainted_and_target_element())

    def execute(self, context):
        os.system("cls")
        constraint_prop = get_scene_vrm1_constraint_prop()
        target_armature = get_target_armature()

        # 対象がオブジェクトとボーンのいずれであるかを検知する｡
        constrainted_element, target_element = detect_constrainted_and_target_element()
        if not constrainted_element:
            self.report({"ERROR"}, "Inappropriate active or target object")
            return {"FINISHED"}

        logger.debug(f"\n{'':#>100}\n{type(constrainted_element)} & {type(target_element)}")
        logger.debug(f"Constrainted : {constrainted_element.name}")
        logger.debug(f"Traget : {target_element.name}\n{'':#>100}\n")

        # 'constraint_type'に対応するコンストレイントを作成する｡
        constraint_type = self.constraint_type_dict[self.constraint_type]
        constraint_name = self.constraint_name_dict[self.constraint_type]

        constraints = constrainted_element.constraints
        # 既にVRMコンストレイントが存在する場合は削除する｡
        remove_existing_vrm_constraint(constraints)

        new_constraint: CopyRotationConstraint | DampedTrackConstraint = constraints.new(constraint_type)
        # Target Object, Subtargetを設定する｡
        match target_element:
            case PoseBone():
                new_constraint.target = target_armature
                new_constraint.subtarget = target_element.name

            case Object():
                new_constraint.target = target_element

        new_constraint.name = constraint_name

        # 各種VRMコンストレイントに応じたパラメーターを設定する｡
        set_vrm_constraint_parametters(new_constraint, self.constraint_type)

        # 作成されたコンストレイントが優先して検出されるようにコンストレイントスタックの先頭に移動する｡
        new_constraint_index = list(constraints).index(new_constraint)
        constraints.move(new_constraint_index, 0)

        # 作成されたコンストレイントがリスト内のアクティブアイテムになるようにUI Listインデックスを調整する｡
        current_ui_constraint_type = constraint_prop.constraint_type
        vrm1_add_items2constraint_ui_list(current_ui_constraint_type)
        constraint_collection = get_ui_vrm1_constraint_prop()
        target_constraint_index = 0

        for n, props in enumerate(constraint_collection):
            list_item: VRMHELPER_WM_vrm1_constraint_list_items = props
            if (
                constrainted_element.name == list_item.name
                and list_item.constraint_name == new_constraint.name
            ):
                target_constraint_index = n
                break

        if target_constraint_index:
            index_root_prop = get_vrm1_index_root_prop()
            index_root_prop.constraint = target_constraint_index

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_constraint_remove_vrm_constraint(VRMHELPER_vrm1_constraint_base):
    bl_idname = "vrmhelper.vrm1_constraint_remove"
    bl_label = "Remove Constraint"
    bl_description = "Remove the selected VRM constraint in UI List"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        return detect_constraint_or_label()

    def execute(self, context):
        os.system("cls")
        # アクティブインデックスからアクティブアイテムを取得する｡
        active_item = detect_constraint_or_label()

        # アクティブコンストレイントがオブジェクトの場合
        if active_item.is_object_constraint:
            constrainted_element = bpy.data.objects.get(active_item.name)

        # アクティブコンストレイントがボーンの場合
        else:
            target_armature = get_target_armature()
            constrainted_element = target_armature.pose.bones.get(active_item.name)

        # アクティブアイテムが参照しているコンストレイントを取得する｡
        constraints = constrainted_element.constraints
        remove_target = constraints.get(active_item.constraint_name)

        # 取得したコンストレイントを削除する｡
        constraints.remove(remove_target)

        # リストのアクティブインデックスをオフセットする｡
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
    VRMHELPER_OT_vrm1_expression_move_custom_expression,
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
    VRMHELPER_OT_vrm1_expression_restore_initial_parameters,
    # ----------------------------------------------------------
    #    Collider
    # ----------------------------------------------------------
    VRMHELPER_OT_vrm1_collider_create_from_bone,
    VRMHELPER_OT_vrm1_collider_remove_from_empty,
    # ----------------------------------------------------------
    #    Collider Group
    # ----------------------------------------------------------
    VRMHELPER_OT_vrm1_collider_group_add_group,
    VRMHELPER_OT_vrm1_collider_group_remove_active_group,
    VRMHELPER_OT_vrm1_collider_group_clear_group,
    VRMHELPER_OT_vrm1_collider_group_add_collider,
    VRMHELPER_OT_vrm1_collider_group_remove_collider,
    VRMHELPER_OT_vrm1_collider_group_clear_collider,
    VRMHELPER_OT_vrm1_collider_group_register_collider_from_bone,
    # ----------------------------------------------------------
    #    Spring
    # ----------------------------------------------------------
    VRMHELPER_OT_vrm1_spring_add_spring,
    VRMHELPER_OT_vrm1_spring_remove_spring,
    VRMHELPER_OT_vrm1_spring_clear_spring,
    VRMHELPER_OT_vrm1_spring_add_joint,
    VRMHELPER_OT_vrm1_spring_remove_joint,
    VRMHELPER_OT_vrm1_spring_clear_joint,
    VRMHELPER_OT_vrm1_spring_add_joint_from_source,
    VRMHELPER_OT_vrm1_spring_assign_parameters_to_joints,
    VRMHELPER_OT_vrm1_spring_pick_radius_from_active_bone,
    VRMHELPER_OT_vrm1_spring_add_collider_group,
    VRMHELPER_OT_vrm1_spring_remove_collider_group,
    VRMHELPER_OT_vrm1_spring_clear_collider_group,
    # ----------------------------------------------------------
    #    Constraint
    # ----------------------------------------------------------
    VRMHELPER_OT_vrm1_constraint_add_vrm_constraint,
    VRMHELPER_OT_vrm1_constraint_remove_vrm_constraint,
)
