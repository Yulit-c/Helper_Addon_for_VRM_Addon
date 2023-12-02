if "bpy" in locals():
    import importlib

    reloadable_modules = [
        "preparation_logger",
        "utils_common",
        "utils_vrm_base",
        "utils_vrm0_first_person",
        "utils_vrm0_blend_shape",
        "utils_vrm0_spring",
    ]

    for module in reloadable_modules:
        if module in locals():
            importlib.reload(locals()[module])

else:
    from ..Logging import preparation_logger
    from .. import utils_common
    from .. import utils_vrm_base
    from . import utils_vrm0_first_person
    from . import utils_vrm0_blend_shape
    from . import utils_vrm0_spring


import os, time, uuid, math
import numpy as np
from typing import (
    Literal,
)
import bpy
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

# from ..addon_classes import (
# )

from ..preferences import (
    get_addon_collection_name,
)

from ..addon_classes import (
    ReferenceStringPropertyGroup,
    ReferenceBonePropertyGroup,
    ReferenceVrm0BlendShapeGroupPropertyGroup,
    ReferenceVrm0BlendShapeBindPropertyGroup,
    ReferenceVrm0MaterialValueBindPropertyGroup,
    ReferencerVrm0SecondaryAnimationColliderPropertyGroup,
    ReferenceVrm0SecondaryAnimationColliderGroupPropertyGroup,
    ReferenceVrm0SecondaryAnimationPropertyGroup,
    ReferenceVrm0SecondaryAnimationGroupPropertyGroup,
    VRMHELPER_VRM_joint_operator_property,
)

from ..property_groups import (
    VRMHELPER_SCENE_vrm0_ui_list_active_indexes,
    VRMHELPER_SCENE_vrm0_blend_shape_settings,
    VRMHELPER_WM_vrm0_blend_shape_material_list_items,
    VRMHELPER_WM_vrm0_operator_spring_collider_group_list_items,
    VRMHELPER_WM_operator_spring_bone_group_list_items,
    # ---------------------------------------------------------------------------------
    get_target_armature,
    get_target_armature_data,
    # ----------------------------------------------------------
    get_ui_vrm0_first_person_prop,
    get_ui_vrm0_blend_shape_material_prop,
    get_ui_bone_group_prop,
    get_ui_vrm0_operator_collider_group_prop,
    get_ui_vrm0_operator_spring_bone_group_prop,
    # ----------------------------------------------------------
    get_vrm0_index_root_prop,
    get_vrm0_scene_root_prop,
    get_scene_vrm0_first_person_prop,
    get_scene_vrm0_blend_shape_prop,
    get_scene_vrm0_mtoon_stored_prop,
    get_scene_vrm0_collider_group_prop,
    get_scene_vrm0_spring_bone_group_prop,
    # ---------------------------------------------------------------------------------
    get_vrm0_wm_root_prop,
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
    get_vrm_extension_property,
    evaluation_expression_morph_collection,
    evaluation_expression_material_collection,
    get_branch_root_bones_by_type,
    get_bones_for_each_branch_by_type,
    get_vrm0_extension_first_person,
    get_vrm0_extension_blend_shape,
    get_vrm0_extension_active_blend_shape_group,
    get_vrm0_extension_secondary_animation,
    get_vrm0_extension_collider_group,
    get_vrm0_extension_spring_bone_group,
    reset_shape_keys_value_in_morph_binds,
    store_mtoon_current_values,
    set_mtoon_default_values,
    is_existing_target_armature_and_mode,
    add_list_item2bone_group_list4operator,
)

from .utils_vrm0_first_person import (
    vrm0_search_same_name_mesh_annotation,
    vrm0_remove_mesh_annotation,
    vrm0_sort_mesh_annotations,
)

from .utils_vrm0_blend_shape import (
    get_active_blend_shape,
    get_ui_vrm0_blend_shape_bind_prop,
    vrm0_get_active_bind_in_ui,
    vrm0_get_active_material_value_in_ui,
    search_existing_bind_and_update,
    convert_str2color_property_type,
    search_existing_material_color_and_update,
    search_existing_material_uv_and_update,
    set_mtoon0_parameters_from_material_value,
)

from .utils_vrm0_spring import (
    remove_vrm0_collider_when_removed_collider_group,
    get_active_list_item_in_collider_group,
    remove_vrm0_collider_by_selected_object,
    vrm0_remove_collider_group_in_springs,
    vrm0_get_active_list_item_in_spring,
    vrm0_add_list_item2collider_group_list4operator,
    vrm0_add_list_item2spring_bone_group_list4operator,
    get_active_linked_collider_groups,
    get_spring_bone_group_by_comment,
    vrm0_get_active_list_item_in_linked_collider_group,
    get_empty_linked_collider_group_slot,
    gen_corresponding_collider_group_dict,
)

from ..operators import (
    VRMHELPER_operator_base,
    VRMHELPER_vrm0_first_person_base,
    VRMHELPER_vrm0_blend_shape_base,
    VRMHELPER_vrm0_blend_shape_sub,
    VRMHELPER_vrm0_collider_group_base,
    VRMHELPER_vrm0_bone_group_base,
    VRMHELPER_vrm0_linked_collider_group_base,
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
    bl_description = (
        "Add a new annotation to First Person Annotation and set the selected object to that bone_name"
    )
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
        mesh_annotations = get_vrm0_extension_first_person().mesh_annotations
        annotation_type = get_scene_vrm0_first_person_prop().annotation_type

        # 選択オブジェクトの数だけMesh Annotationを追加する｡
        # 既にオブジェクトが存在する場合､Typeが異なれば値を更新､同じであれば処理をスキップする｡
        for obj in [obj for obj in context.selected_objects if filtering_mesh_type(obj)]:
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


class VRMHELPER_OT_vrm0_first_person_remove_annotation_from_list(VRMHELPER_vrm0_first_person_base):
    bl_idname = "vrm_helper.vrm0_remove_mesh_annotation_from_list"
    bl_label = "Remove Mesh Annotation from Active Item"
    bl_description = "Remove active annotation in the list from Target Armature's VRM Extension"
    vrm_mode = "0"

    """
    Target ArmatureのVRM Extensionから､リスト内で選択されているMesh Annotationを削除する｡
    """

    @classmethod
    def poll(cls, context):
        # Mesh Annotationが1つ以上存在しなければ使用不可｡
        return get_vrm0_extension_first_person().mesh_annotations

    def execute(self, context):
        # アドオンのプロパティとVRM Extensionのプロパティを取得する｡
        list_items = get_ui_vrm0_first_person_prop()
        active_item_index = get_vrm0_index_root_prop().first_person
        active_item_name = list_items[active_item_index].name

        # オブジェクトの名前に一致するMesh Annotationを走査してVRM Extensionから削除する｡
        vrm0_remove_mesh_annotation(active_item_name)

        self.offset_active_item_index(self.component_type)

        return {"FINISHED"}


class VRMHELPER_OT_vrm0_first_person_remove_annotation_from_select_objects(VRMHELPER_vrm0_first_person_base):
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
        return get_vrm0_extension_first_person().mesh_annotations

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
        return get_vrm0_extension_first_person().mesh_annotations

    def execute(self, context):
        mesh_annotations = get_vrm0_extension_first_person().mesh_annotations
        mesh_annotations.clear()

        self.offset_active_item_index(self.component_type)

        return {"FINISHED"}


"""---------------------------------------------------------
    Blend Shape
---------------------------------------------------------"""


class VRMHELPER_OT_0_blend_shape_create_blend_shape(VRMHELPER_vrm0_blend_shape_base):
    bl_idname = "vrm_helper.vrm0_blend_shape_create_blend_shape"
    bl_label = "Create Blend Shape"
    bl_description = "Create a new Blend Shape Proxy to the target armature"
    bl_options = {"UNDO"}

    def execute(self, context):
        target_armature = get_target_armature()

        bpy.ops.vrm.add_vrm0_blend_shape_group(armature_name=target_armature.name, name="Blend Shape")

        return {"FINISHED"}


class VRMHELPER_OT_0_blend_shape_remove_blend_shape(VRMHELPER_vrm0_blend_shape_base):
    bl_idname = "vrm_helper.vrm0_blend_shape_remove_blend_shape"
    bl_label = "Remove Blend_Shape"
    bl_description = "Remove the active blend_shape from the target armature"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        # ブレンドシェイプが1つ以上存在している
        blend_shapes = get_vrm0_extension_blend_shape().blend_shape_groups
        return blend_shapes

    def execute(self, context):
        target_armature = get_target_armature()
        blend_shape_master = get_vrm0_extension_blend_shape()
        target_index = blend_shape_master.active_blend_shape_group_index

        bpy.ops.vrm.remove_vrm0_blend_shape_group(
            armature_name=target_armature.name, blend_shape_group_index=target_index
        )

        return {"FINISHED"}


class VRMHELPER_OT_0_blend_shape_clear_blend_shape(VRMHELPER_vrm0_blend_shape_base):
    bl_idname = "vrm_helper.vrm_blend_shape_clear_blend_shape"
    bl_label = "Clear Custom Blend Shape"
    bl_description = "Clear all blend_shapes from the target armature"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        # ブレンドシェイプが1つ以上存在している
        blend_shapes = get_vrm0_extension_blend_shape().blend_shape_groups
        return blend_shapes

    def execute(self, context):
        blend_shape_master = get_vrm0_extension_blend_shape()
        blend_shapes = blend_shape_master.blend_shape_groups
        blend_shapes.clear()
        blend_shape_master.active_blend_shape_group_index = 0

        return {"FINISHED"}


class VRMHELPER_OT_vrm0_blend_shape_assign_blend_shape_to_scene(VRMHELPER_vrm0_blend_shape_base):
    bl_idname = "vrm_helper.vrm0_blend_shape_assign_blend_shape_to_scene"
    bl_label = "Assign Blend Shape"
    bl_description = "Active blend_shape settings are reflected on the scene"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        # ブレンドシェイプが1つ以上存在している
        blend_shapes = get_vrm0_extension_blend_shape().blend_shape_groups
        return blend_shapes

    def execute(self, context):
        os.system("cls")
        blend_shape_master = get_vrm0_extension_blend_shape()
        blend_shape_groups = blend_shape_master.blend_shape_groups
        target_index = blend_shape_master.active_blend_shape_group_index
        active_blend_shape: ReferenceVrm0BlendShapeGroupPropertyGroup = blend_shape_groups[target_index]

        # ----------------------------------------------------------
        #    Binds
        # ----------------------------------------------------------
        # アクティブエクスプレッションのBindsの全てのBindの
        # メッシュ/シェイプキーに対してウェイトを反映する｡
        # 対象メッシュは処理前に全てのシェイプキーのウェイトを0にする｡
        binds = active_blend_shape.binds
        reset_shape_keys_value_in_morph_binds(binds)

        # Bindに設定されているBlend Shapeの値を対応するShape Keyの値に代入する｡
        existing_bind_info = {}
        # Bindsに登録されている全メッシュとそれに関連付けられたシェイプキー､ウェイトを取得する｡
        for bind in binds:
            bind: ReferenceVrm0BlendShapeBindPropertyGroup = bind
            if not (mesh_object := bpy.data.objects.get(bind.mesh.mesh_object_name)):
                continue

            bind_mesh = mesh_object.data
            existing_bind_info.setdefault(bind_mesh, []).append((bind.index, bind.weight))

        # 取得したデータをシーン上に反映する｡
        for mesh, sk_info in existing_bind_info.items():
            for sk_name, sk_value in sk_info:
                sk = mesh.shape_keys.key_blocks.get(sk_name)
                sk.value = sk_value

        # ----------------------------------------------------------
        #    Material Values
        # ----------------------------------------------------------
        # Color/Transform Bindで指定されている全てのマテリアルの特定パラメーターは一度すべて初期値にセットする｡
        material_values = active_blend_shape.material_values
        existing_bind_material = set()
        #
        for value in material_values:
            value: ReferenceVrm0MaterialValueBindPropertyGroup = value
            existing_bind_material.add(value.material)

        for mat in existing_bind_material:
            if not mat:
                continue
            logger.debug(f"Reset Values : {mat.name}")
            # set_mtoon_default_values(mat)

        for mat_value in material_values:
            set_mtoon0_parameters_from_material_value(mat_value)

        return {"FINISHED"}


# ----------------------------------------------------------
#   Bind or Material Values
# ----------------------------------------------------------
class VRMHELPER_OT_vrm0_blend_shape_bind_or_material_create(VRMHELPER_vrm0_blend_shape_sub):
    bl_idname = "vrm_helper.vrm0_blend_shape_bind_or_mat_create"
    bl_label = "Create  Item"
    bl_description = "Create a Bind or Material Value to the active Blend Shape"
    bl_options = {"UNDO"}

    mode: EnumProperty(
        name="Bind or Material",
        description="Choose Operator Mode",
        items=(
            ("BIND", "Bind", "Create new Bind"),
            ("MATERIAL", "Material Value", "Create new Material Value"),
        ),
        default="BIND",
    )

    @classmethod
    def poll(cls, context):
        # アクティブなブレンドシェイプが存在する
        return get_active_blend_shape()

    def execute(self, context):
        armature_data_name = get_target_armature_data().name
        blend_shape_master = get_vrm0_extension_blend_shape()
        active_index = blend_shape_master.active_blend_shape_group_index

        match self.mode:
            case "BIND":
                bpy.ops.vrm.add_vrm0_blend_shape_bind(
                    armature_name=armature_data_name,
                    blend_shape_group_index=active_index,
                )
            case "MATERIAL":
                bpy.ops.vrm.add_vrm0_material_value_bind(
                    armature_name=armature_data_name,
                    blend_shape_group_index=active_index,
                )

        type = self.mode_dict[self.mode]
        self.offset_active_item_index(type)

        return {"FINISHED"}


class VRMHELPER_OT_vrm0_blend_shape_bind_or_material_remove(VRMHELPER_vrm0_blend_shape_sub):
    bl_idname = "vrm_helper.vrm0_blend_shape_bind_or_mat_remove"
    bl_label = "Remove  Item"
    bl_description = "Remove the active Bind or Material Value in the active Blend Shape"
    bl_options = {"UNDO"}

    mode: EnumProperty(
        name="Bind or Material",
        description="Choose Operator Mode",
        items=(
            ("BIND", "Bind", "Create new Bind"),
            ("MATERIAL", "Material Value", "Create new Material Value"),
        ),
        default="BIND",
    )

    @classmethod
    def poll(cls, context):
        # modeに応じたUI Listの要素が存在する｡
        mode = get_scene_vrm0_blend_shape_prop()
        match mode.editing_target:
            case "BIND":
                active_item = vrm0_get_active_bind_in_ui()

            case "MATERIAL":
                active_item = vrm0_get_active_material_value_in_ui()
        return active_item

    def execute(self, context):
        target_armature = get_target_armature()
        active_bind_item = vrm0_get_active_bind_in_ui()
        active_mat_value_item = vrm0_get_active_material_value_in_ui()
        blend_shape_master = get_vrm0_extension_blend_shape()
        blend_shape_index = blend_shape_master.active_blend_shape_group_index

        # TODO : アクティブ要素がラベルであればそのラベルに属する要素を全て削除｡
        #        BindやMaterial Valueであればその一つを削除する｡

        match self.mode:
            case "BIND":
                bind_index = active_bind_item.bind_index
                bpy.ops.vrm.remove_vrm0_blend_shape_bind(
                    armature_name=target_armature.name,
                    blend_shape_group_index=blend_shape_index,
                    bind_index=bind_index,
                )

            case "MATERIAL":
                value_index = active_mat_value_item.value_index
                bpy.ops.vrm.remove_vrm0_material_value_bind(
                    armature_name=target_armature.name,
                    blend_shape_group_index=blend_shape_index,
                    material_value_index=value_index,
                )

        self.offset_active_item_index(self.mode_dict[self.mode])

        return {"FINISHED"}


class VRMHELPER_OT_vrm0_blend_shape_bind_or_material_clear(VRMHELPER_vrm0_blend_shape_sub):
    bl_idname = "vrm_helper.vrm0_blend_shape_bind_or_mat_clear"
    bl_label = "Clear  Items"
    bl_description = "clear the all Binds or Material Values in the active Blend Shape"
    bl_options = {"UNDO"}

    mode: EnumProperty(
        name="Bind or Material",
        description="Choose Operator Mode",
        items=(
            ("BIND", "Bind", "Create new Bind"),
            ("MATERIAL", "Material Value", "Create new Material Value"),
        ),
        default="BIND",
    )

    @classmethod
    def poll(cls, context):
        # modeに応じたUI Listの要素が存在する｡
        mode = get_scene_vrm0_blend_shape_prop()
        match mode.editing_target:
            case "BIND":
                active_item = vrm0_get_active_bind_in_ui()

            case "MATERIAL":
                active_item = vrm0_get_active_material_value_in_ui()
        return active_item

    def execute(self, context):
        active_blend_shape = get_vrm0_extension_active_blend_shape_group()

        match self.mode:
            case "BIND":
                group = active_blend_shape.binds

            case "MATERIAL":
                group = active_blend_shape.material_values

        group.clear()
        self.offset_active_item_index(self.mode_dict[self.mode])

        return {"FINISHED"}


class VRMHELPER_OT_vrm0_blend_shape_change_bind_material(VRMHELPER_vrm0_blend_shape_sub):
    bl_idname = "vrm_helper.vrm0_blend_shape_change_bind_material"
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
        # アクティブなMaterial Valueがマテリアル名のラベルである｡
        active_value = vrm0_get_active_material_value_in_ui()
        match tuple(active_value.item_type):
            case (1, 0, 0, 0) | (1, 0, 0, 1):
                return True

    def invoke(self, context, event):
        component_type = self.mode_dict["MATERIAL"]
        self.offset_active_item_index(component_type)
        # マテリアル選択メニューポップアップ
        context.window_manager.invoke_search_popup(self)
        return {"FINISHED"}

    def execute(self, context):
        blend_shapes = get_active_blend_shape()
        mat_values = blend_shapes.material_values
        active_value = vrm0_get_active_material_value_in_ui()
        old_material_name = active_value.material_name
        old_material = bpy.data.materials.get(old_material_name)

        # ラベル名に対応するマテリアルを参照している全てのMaterial ValueのMaterialを変更する｡
        target_values = {value for value in mat_values if value.material == old_material}

        new_material = bpy.data.materials.get(self.material_name)
        for value in target_values:
            value.material = new_material

        return {"FINISHED"}


class VRMHELPER_OT_vrm0_blend_shape_store_mtoon0_parameters(VRMHELPER_vrm0_blend_shape_sub):
    bl_idname = "vrm_helper.vrm0_blend_shape_store_mtoon0_parameters"
    bl_label = "Store MToon0 Parameters"
    bl_description = "Obtains and stores the current parameters of Mtoon0"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        # 1つ以上のオブジェクトがリンクされた'VRM0 'のコレクションが存在する｡
        return (
            c := bpy.data.collections.get(get_addon_collection_name("VRM0_BLENDSHAPE_MATERIAL"))
        ) and c.all_objects

    def execute(self, context):
        os.system("cls")
        source_collection = bpy.data.collections.get(get_addon_collection_name("VRM0_BLENDSHAPE_MATERIAL"))
        mtoon0_stored_parameters = get_scene_vrm0_mtoon_stored_prop()
        mtoon0_stored_parameters.clear()

        for mat in get_all_materials_from_source_collection_objects(source_collection):
            logger.debug(f"Stored MToon0 Parameters : {mat.name}")
            new_item = mtoon0_stored_parameters.add()
            new_item.name = mat.name
            store_mtoon_current_values(new_item, mat)

        return {"FINISHED"}


class VRMHELPER_OT_vrm0_blend_shape_discard_stored_mtoon0_parameters(VRMHELPER_vrm0_blend_shape_sub):
    bl_idname = "vrm_helper.vrm0_blend_shape_discard_stored_mtoon0_parameters"
    bl_label = "Discard Stored MToon1 Parameters"
    bl_description = "Discard stored parameters of Mtoon0"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        return get_scene_vrm0_mtoon_stored_prop()

    def execute(self, context):
        get_scene_vrm0_mtoon_stored_prop().clear()
        return {"FINISHED"}


class VRMHELPER_OT_vrm0_blend_shape_restore_mtoon0_parameters(VRMHELPER_vrm0_blend_shape_sub):
    bl_idname = "vrm_helper.vrm0_blend_shape_restore_mtoon0_parameters"
    bl_label = "Restore MToon1 Parameters"
    bl_description = "Restore stored parameters of Mtoon1"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        return (
            c := bpy.data.collections.get(get_addon_collection_name("VRM0_BLENDSHAPE_MATERIAL"))
        ) and c.all_objects

    def execute(self, context):
        source_collection = bpy.data.collections.get(get_addon_collection_name("VRM0_BLENDSHAPE_MATERIAL"))

        for mat in get_all_materials_from_source_collection_objects(source_collection):
            set_mtoon_default_values(mat)

        # TODO : Lit Color以外のTexture Transformの値をLit Colorと同じにする｡

        return {"FINISHED"}


class VRMHELPER_OT_vrm0_blend_shape_set_bind_from_scene(VRMHELPER_vrm0_blend_shape_sub):
    bl_idname = "vrm_helper.vrm0_blend_shape_set_bind_from_scene"
    bl_label = "Set bind from Scene"
    bl_description = "Set Bind Bind from the shape keys of the target objects on the scene"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        # 1つ以上のオブジェクトがリンクされた'VRM0_BlendShape_Morph'のコレクションが存在する｡
        return evaluation_expression_material_collection()

    def execute(self, context):
        active_blend_shape = get_active_blend_shape()
        binds = active_blend_shape.binds
        source_collection = bpy.data.collections.get(get_addon_collection_name("VRM0_BLENDSHAPE_MORPH"))

        for obj in source_collection.all_objects:
            # オブジェクトのメッシュデータに2つ以上のキーブロックを持ったシェイプキーが存在する｡
            if not (sk := obj.data.shape_keys) and len(sk.key_blocks) <= 1:
                continue

            logger.debug(f"###\n{'':#>100}\nCurrent Processed Object : {obj.name}\n{'':#>100}")
            for shape_key in (k for k in sk.key_blocks if k != sk.reference_key):
                # objとシェイプキーのペアがMorph Target Bindに登録済みであればシェイプキーの現在の値に更新する｡
                # 値が0だった場合はBindを削除する｡
                is_existing_bind = search_existing_bind_and_update(
                    obj,
                    shape_key,
                    binds,
                )

                # objとシェイプキーのペアがBindに未登録かつシェイプキーの値が0超過であった場合は新規登録する｡
                if not is_existing_bind:
                    if shape_key.value == 0:
                        continue
                    logger.debug(f"Registered New Bind -- {obj.name} : {shape_key.name}")
                    new_bind: ReferenceVrm0BlendShapeBindPropertyGroup = binds.add()
                    new_bind.mesh.mesh_object_name = obj.name
                    new_bind.index = shape_key.name
                    new_bind.weight = shape_key.value

        self.offset_active_item_index(self.mode_dict["BIND"])

        return {"FINISHED"}


class VRMHELPER_OT_vrm0_blend_shape_set_material_value_from_scene(VRMHELPER_vrm0_blend_shape_sub):
    bl_idname = "vrm_helper.vrm0_blend_shape_set_material_value_from_scene"
    bl_label = "Set Material Bind from Scene"
    bl_description = "Set Material Value from the material of the target objects on the scene"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        # 1つ以上のオブジェクトがリンクされた'VRM0_BlendShape_Material'のコレクションが存在する｡
        return evaluation_expression_material_collection()

    def execute(self, context):
        active_blend_shape = get_active_blend_shape()
        material_values = active_blend_shape.material_values
        source_collection = bpy.data.collections.get(get_addon_collection_name("VRM0_BLENDSHAPE_MATERIAL"))

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
            #    Material Color
            # ----------------------------------------------------------
            # ソースマテリアルに設定されたMToonパラメーターに応じてMaterial Valueを登録する｡
            # 既に登録済みのマテリアル､パラメーターの組み合わせだった場合は値を更新する｡初期値に設定される場合はValueを削除する｡
            print(f"\n{'':#>50}\nRegistering Material Value(Color)\n{'':#>50}")
            mtoon_color_parameters_dict = search_existing_material_color_and_update(
                source_material, material_values
            )

            # 未登録であった場合は新規登録する｡
            for prop, values in mtoon_color_parameters_dict.items():
                if values:
                    logger.debug(f"Set Type : {prop}")
                    if len(values) < 4:
                        values.append(1.0)
                    # 新規にmaterial_valueを作成し､valueを4つ作成する｡
                    new_color_value: ReferenceVrm0MaterialValueBindPropertyGroup = material_values.add()
                    while len(new_color_value.target_value) < 4:
                        new_color_value.target_value.add()

                    # MaterialとProperty Nameの値をセットする｡
                    new_color_value.material = source_material
                    new_color_value.property_name = convert_str2color_property_type(prop)
                    # # target_valueの値をセットする｡
                    for n in range(len(new_color_value.target_value)):
                        new_color_value.target_value[n].value = values[n]
            # ----------------------------------------------------------
            #    UV Coordinate
            # ----------------------------------------------------------
            print(f"\n{'':#>50}\nRegistering Material Value(UV)\n{'':#>50}")
            mtoon_uv_parameters_dict = search_existing_material_uv_and_update(
                source_material, material_values
            )

            # 未登録であった場合は新規登録する｡
            if not mtoon_uv_parameters_dict:
                logger.debug("condition 1")
                continue

            if not any(mtoon_uv_parameters_dict.values()):
                logger.debug("condition 2")
                continue

            # 新規にmaterial_valueを作成し､valueを4つ作成する｡
            new_uv_value: ReferenceVrm0MaterialValueBindPropertyGroup = material_values.add()
            while len(new_uv_value.target_value) < 4:
                new_uv_value.target_value.add()
            prop_name = "_MainTex_ST"
            # MaterialとProperty Nameの値をセットする｡
            new_uv_value.material = source_material
            new_uv_value.property_name = prop_name
            # target_valueの値をセットする｡
            uv_scale = []
            if mtoon_uv_parameters_dict["texture_scale"]:
                uv_scale = mtoon_uv_parameters_dict["texture_scale"]
            uv_offset = []
            if mtoon_uv_parameters_dict["texture_offset"]:
                uv_offset = mtoon_uv_parameters_dict["texture_offset"]
            # value_set = mtoon_uv_parameters_dict["texture_scale"] + mtoon_uv_parameters_dict["texture_offset"]
            target_value = new_uv_value.target_value
            for n, scale_value in enumerate(uv_scale):
                target_value[n].value = scale_value

            logger.debug(uv_offset)
            for n, offset_value in enumerate(uv_offset):
                target_value[n + 2].value = offset_value

        # TODO : Lit Color以外のTexture Transformの値をLit Colorと同じにする｡

        # ---------------------------------------------------------------------------------
        self.offset_active_item_index(self.mode_dict["MATERIAL"])

        return {"FINISHED"}


class VRMHELPER_OT_vrm0_blend_shape_set_both_binds_from_scene(VRMHELPER_vrm0_blend_shape_sub):
    bl_idname = "vrm_helper.vrm0_blend_shape_set_both_binds_from_scene"
    bl_label = "Set Both Binds and Material Values from Scene"
    bl_description = "Set Binds and Material Values from the scene"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        morph_condition = evaluation_expression_morph_collection()
        mat_condition = evaluation_expression_material_collection()
        return morph_condition and mat_condition

    def execute(self, context):
        os.system("cls")
        # ----------------------------------------------------------
        #    Binds
        # ----------------------------------------------------------
        bpy.ops.vrm_helper.vrm0_blend_shape_set_bind_from_scene()

        # ----------------------------------------------------------
        #    Material Values
        # ----------------------------------------------------------
        bpy.ops.vrm_helper.vrm0_blend_shape_set_material_value_from_scene()

        return {"FINISHED"}


class VRMHELPER_OT_vrm0_blend_shape_restore_initial_parameters(VRMHELPER_vrm0_blend_shape_sub):
    bl_idname = "vrm_helper.vrm0_blend_shape_restore_initial_values"
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
        #    Bind
        # ----------------------------------------------------------
        if source_collection_morph := bpy.data.collections.get(
            get_addon_collection_name("VRM0_BLENDSHAPE_MORPH")
        ):
            for obj in {obj for obj in source_collection_morph.all_objects if obj.type == "MESH"}:
                reset_shape_keys_value(obj.data)

        # ----------------------------------------------------------
        #    Material Value
        # ----------------------------------------------------------
        if source_collection_mat := bpy.data.collections.get(
            get_addon_collection_name("VRM0_BLENDSHAPE_MATERIAL")
        ):
            # 対象コレクション内のすべてのオブジェクトが持つマテリアルにパラメーターの復元処理を行う｡
            for mat in get_all_materials_from_source_collection_objects(source_collection_mat):
                set_mtoon_default_values(mat)

            # TODO : Lit Color以外のTexture Transformの値をLit Colorと同じにする｡

        return {"FINISHED"}


"""---------------------------------------------------------
    Collider Group
---------------------------------------------------------"""


class VRMHELPER_OT_vrm0_collider_group_add_group(VRMHELPER_vrm0_collider_group_base):
    bl_idname = "vrmhelper.vrm_collider_group_add_group"
    bl_label = "Add Collider Group"
    bl_description = "Add a new VRM0 Spring Bone Collider Group"

    def execute(self, context):
        target_armature = get_target_armature()
        new_group: ReferenceVrm0SecondaryAnimationColliderGroupPropertyGroup = get_vrm_extension_property(
            "COLLIDER_GROUP"
        ).add()
        new_group.uuid = uuid.uuid4().hex
        new_group.refresh(target_armature)

        return {"FINISHED"}


class VRMHELPER_OT_vrm0_collider_group_remove_active_group(VRMHELPER_vrm0_collider_group_base):
    bl_idname = "vrmhelper.vrm0_collider_group_remove_active_group"
    bl_label = "Remove Collider Group"
    bl_description = "Remove the collider group that is active in the list."

    @classmethod
    def poll(self, context):
        # Collider Groupが存在しており､リストのアクティブアイテムがラベルではない｡
        return (ai := get_active_list_item_in_collider_group()) and (ai.item_type[2])

    def execute(self, context):
        os.system("cls")

        # アクティブアイテムのインデックスを取得する｡
        active_item = get_active_list_item_in_collider_group()
        active_index = active_item.group_index

        collider_groups = get_vrm_extension_property("COLLIDER_GROUP")
        # 対象コライダーグループを参照していたスプリングの値を更新後に対象を削除する｡その後アクティブインデックスを更新する
        remove_vrm0_collider_when_removed_collider_group(active_index)
        collider_groups.remove(active_index)
        self.offset_active_item_index(self.component_type)

        return {"FINISHED"}


class VRMHELPER_OT_vrm0_collider_group_clear_group(VRMHELPER_vrm0_collider_group_base):
    bl_idname = "vrmhelper.vrm0_collider_group_clear_group"
    bl_label = "Clear Collider Group"
    bl_description = "Clear all collider groups."

    @classmethod
    def poll(self, context):
        # Collider Groupが存在する｡
        return get_vrm_extension_property("COLLIDER_GROUP")

    def execute(self, context):
        os.system("cls")

        collider_groups = get_vrm_extension_property("COLLIDER_GROUP")
        for n, _collider_group in enumerate(collider_groups):
            remove_vrm0_collider_when_removed_collider_group(n)

        collider_groups.clear()
        get_vrm0_index_root_prop().collider_group = 0
        self.offset_active_item_index(self.component_type)

        return {"FINISHED"}


"""---------------------------------------------------------
    Collider
---------------------------------------------------------"""


class VRMHELPER_OT_vrm0_collider_group_create_active_collider(VRMHELPER_vrm0_collider_group_base):
    bl_idname = "vrmhelper.vrm0_collider_group_create_active_collider"
    bl_label = "Create a Collider"
    bl_description = "Create a new collider from selected bone"

    @classmethod
    def poll(self, context):
        # UI ListのアクティブアイテムがCollidaer GroupまたはColliderである｡
        if active_item := get_active_list_item_in_collider_group():
            return active_item.item_type[2] or active_item.item_type[3]

    def execute(self, context):
        active_item = get_active_list_item_in_collider_group()
        target_armature = get_target_armature()
        parent_bone: bpy.types.Bones = target_armature.data.bones.get(active_item.bone_name)
        if not parent_bone:
            self.report({"ERROR"}, "Appropriate parent bone name is not set for the Collidaer Group")
            return {"CANCELLED"}

        # アクティブアイテムに対応するCollider GroupをVRM Extensionから取得する｡
        ext_collider_group = get_vrm0_extension_collider_group()
        target_collider_group: ReferenceVrm0SecondaryAnimationColliderGroupPropertyGroup
        target_collider_group = ext_collider_group[active_item.group_index]
        colliders = target_collider_group.colliders

        # オブジェクトの選択を操作するためにObject Modeに移行する｡
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="DESELECT")

        # アクティブなColliderまたはCollidaer Groupに対応したボーンに対応するColliderを作成する｡
        # https://github.com/saturday06/VRM-Addon-for-Blender
        # CollidaerとなるEmptyオブジェクトを作成する｡
        collider_object = bpy.data.objects.new(
            name=f"{target_armature.name}_{parent_bone.name}_collider", object_data=None
        )
        # Empty Objectのパラメーター
        collider_object.parent = target_armature
        collider_object.parent_type = "BONE"
        collider_object.parent_bone = parent_bone.name
        collider_object.empty_display_type = "SPHERE"
        scene_cg_settings = get_scene_vrm0_collider_group_prop()
        collider_object.empty_display_size = scene_cg_settings.collider_radius
        pose_bone: bpy.types.PoseBone = target_armature.pose.bones.get(active_item.bone_name)
        mid_point = (pose_bone.tail + pose_bone.head) / 2
        collider_object.matrix_world = generate_head_collider_position(mid_point)
        # オブジェクトをコレクションにリンク
        addon_collection_dict = setting_vrm_helper_collection()
        dest_collection = addon_collection_dict["VRM0_COLLIDER"]
        link_object2collection(collider_object, dest_collection)
        # VRM Extensionのパラメーター
        colliders.add().bpy_object = collider_object
        collider_object.select_set(True)

        return {"FINISHED"}


class VRMHELPER_OT_vrm0_collider_group_remove_active_collider(VRMHELPER_vrm0_collider_group_base):
    bl_idname = "vrmhelper.vrm0_collider_group_remove_active_collider"
    bl_label = "Remove Active Collider"
    bl_description = "Remove the active collider in UI List"

    @classmethod
    def poll(self, context):
        # UI ListのアクティブアイテムがColliderである｡
        if active_item := get_active_list_item_in_collider_group():
            return active_item.item_type[3]

    def execute(self, context):
        # UI ListのアクティブアイテムとVRM Extensionのコライダーグループを取得する｡
        ext_collider_group = get_vrm0_extension_collider_group()
        active_item = get_active_list_item_in_collider_group()
        target_collider_group: ReferenceVrm0SecondaryAnimationColliderGroupPropertyGroup = ext_collider_group[
            active_item.group_index
        ]
        colliders = target_collider_group.colliders
        collider: ReferencerVrm0SecondaryAnimationColliderPropertyGroup = colliders[
            active_item.collider_index
        ]
        if collider.bpy_object:
            bpy.data.objects.remove(collider.bpy_object)
        colliders.remove(active_item.collider_index)
        self.offset_active_item_index(self.component_type)

        return {"FINISHED"}


class VRMHELPER_OT_vrm0_collider_group_clear_colliders(VRMHELPER_vrm0_collider_group_base):
    bl_idname = "vrmhelper.vrm0_collider_group_clear_colliders"
    bl_label = "Clear Colliders"
    bl_description = "Remove all colliders in active collider group"

    @classmethod
    def poll(self, context):
        # UI Listのアクティブアイテムがコライダーグループまたはコライダーである｡
        if active_item := get_active_list_item_in_collider_group():
            return active_item.item_type[2] or active_item.item_type[3]

    def execute(self, context):
        os.system("cls")
        # UI ListのアクティブアイテムとVRM Extensionのコライダーグループを取得する｡
        ext_collider_group = get_vrm0_extension_collider_group()
        active_item = get_active_list_item_in_collider_group()
        target_collider_group: ReferenceVrm0SecondaryAnimationColliderGroupPropertyGroup = ext_collider_group[
            active_item.group_index
        ]
        colliders = target_collider_group.colliders
        # UI Listのアクティブアイテムに対応したコライダーグループのコライダーを全て削除する｡
        # コライダーを定義しているEmptyも削除する｡
        collider: ReferencerVrm0SecondaryAnimationColliderPropertyGroup
        for collider in colliders:
            if collider.bpy_object:
                bpy.data.objects.remove(collider.bpy_object)
        colliders.clear()
        self.offset_active_item_index(self.component_type)

        return {"FINISHED"}


class VRMHELPER_OT_vrm0_collider_create_from_bone(VRMHELPER_vrm0_collider_group_base):
    bl_idname = "vrm_helper.vrm0_collider_create_from_bone"
    bl_label = "Create Collider"
    bl_description = "Create spring bone collider from selected bone"

    @classmethod
    def poll(cls, context):
        # Target Armatureの1ボーンを1つ以上選択していなければ使用不可｡
        return is_existing_target_armature_and_mode()

    def execute(self, context):
        os.system("cls")
        time_start = time.perf_counter()
        target_armature = get_target_armature()
        armature_data: bpy.types.Armature = target_armature.data
        collider_group = get_vrm_extension_property("COLLIDER_GROUP")
        addon_collection_dict = setting_vrm_helper_collection()
        dest_collection = addon_collection_dict["VRM0_COLLIDER"]

        # 選択ボーン全てに対してコライダーを作成してパラメーターをセットする｡
        # Target Armature.dataの'use_mirror_x'が有効の場合は処理の間は無効化する｡
        is_changed_use_mirror = False
        if armature_data.use_mirror_x:
            armature_data.use_mirror_x = False
            is_changed_use_mirror = True

        current_mode = context.mode
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="DESELECT")
        bpy.ops.object.mode_set(mode=current_mode.replace("EDIT_ARMATURE", "EDIT"))

        bones = get_selected_bone()
        for bone in bones:
            if not (pose_bone := get_pose_bone_by_name(target_armature, bone.name)):
                continue
            # コライダーグループ内に既に同じボーンを指定したグループがある場合はそのグループ内にコライダーを追加する｡
            groups = [i for i in collider_group if i.node.bone_name == bone.name]
            target_group: ReferenceVrm0SecondaryAnimationColliderGroupPropertyGroup
            if groups:
                target_group = groups[0]
            else:
                target_group = collider_group.add()
                target_group.uuid = uuid.uuid4().hex
                target_group.node.bone_name = bone.name
                target_group.refresh(target_armature)

            # 新規コライダーの作成｡
            colliders = target_group.colliders
            # https://github.com/saturday06/VRM-Addon-for-Blender
            collider_object = bpy.data.objects.new(
                name=f"{target_armature.name}_{bone.name}_collider", object_data=None
            )
            # Empty Objectのパラメーター
            collider_object.parent = target_armature
            collider_object.parent_type = "BONE"
            collider_object.parent_bone = bone.name
            collider_object.empty_display_type = "SPHERE"
            scene_cg_settings = get_scene_vrm0_collider_group_prop()
            collider_object.empty_display_size = scene_cg_settings.collider_radius
            mid_point = (pose_bone.tail + pose_bone.head) / 2
            collider_object.matrix_world = generate_head_collider_position(mid_point)
            # オブジェクトをコレクションにリンク
            link_object2collection(collider_object, dest_collection)
            # VRM Extensionのパラメーター
            collider: ReferencerVrm0SecondaryAnimationColliderPropertyGroup = colliders.add()
            collider.bpy_object = collider_object

            collider_object.select_set(True)

        # 'use_mirror_x'の値を変更していた場合は元に戻す｡
        if is_changed_use_mirror:
            armature_data.use_mirror_x = True

            # TODO : ボーンの長さに応じたコライダーの敷き詰め?

        bpy.ops.object.mode_set(mode="OBJECT")
        # TODO : 最後に作成したコライダーをリスト内のアクティブアイテムに設定する｡

        logger.debug(f"Processing Time : {time.perf_counter() - time_start:.3f} s")

        return {"FINISHED"}


class VRMHELPER_OT_vrm0_collider_remove_from_empty(VRMHELPER_vrm0_collider_group_base):
    bl_idname = "vrm_helper.vrm0_collider_remove_from_empty"
    bl_label = "Remove Collider"
    bl_description = "Remove spring bone collider from selected empty object"

    @classmethod
    def poll(cls, context):
        # 選択オブジェクトにEmptyが含まれていなければ使用不可｡
        return filtering_empty_from_selected_objects()

    def execute(self, context):
        # 処理中はプロパティのアップデートのコールバック関数をロックする｡
        index_prop = get_vrm0_index_root_prop()
        index_prop.is_locked_update = True

        collider_groups = get_vrm0_extension_collider_group()
        # 選択Emptyオブジェクトのうち､コライダーとして登録されているものがあればコライダー設定とともに削除する｡
        logger.debug("Remove Collider & Empty Object")
        for obj in filtering_empty_from_selected_objects():
            logger.debug(obj.name)
            target_collider_group = remove_vrm0_collider_by_selected_object(obj)
            if not target_collider_group:
                continue
            target_collider_group_name = target_collider_group.name
            if not target_collider_group.colliders:
                index = list(collider_groups).index(target_collider_group)
                collider_groups.remove(index)

                # スプリング内で削除したコライダーグループが参照されていればそれを取り除く｡
                vrm0_remove_collider_group_in_springs(target_collider_group_name)

        # アクティブインデックスをオフセットしてエラーを回避する｡
        self.offset_active_item_index(self.component_type)
        # self.offset_active_item_index("COLLIDER_GROUP")
        # self.offset_active_item_index("SPRING")
        index_prop.is_locked_update = False

        return {"FINISHED"}


"""---------------------------------------------------------
    Spring Bone Group
---------------------------------------------------------"""


class VRMHELPER_OT_vrm0_spring_add_bone_group(VRMHELPER_vrm0_bone_group_base):
    bl_idname = "vrmhelper.vrm0_spring_add_bone_group"
    bl_label = "Add Bone Group"
    bl_description = "Add a new VRM0 Spring Bone Group"

    def execute(self, context):
        bone_groups = get_vrm0_extension_spring_bone_group()
        new_spring = bone_groups.add()
        new_spring.comment = "New Bone Group"

        return {"FINISHED"}


class VRMHELPER_OT_vrm0_spring_remove_bone_group(VRMHELPER_vrm0_bone_group_base):
    bl_idname = "vrmhelper.vrm0_spring_remove_bone_group"
    bl_label = "Remove Bone Group"
    bl_description = "Remove the active VRM0 Spring Bone Group"

    @classmethod
    def poll(cls, context):
        # UIリストのアイテムが存在し､アクティブアイテムがブランク以外である｡
        if not (active_item := vrm0_get_active_list_item_in_spring()):
            return False

        match tuple(active_item.item_type):
            case (1, 0, 0):
                return False
            case _:
                return True

    def execute(self, context):
        active_item = vrm0_get_active_list_item_in_spring()
        bone_groups = get_vrm0_extension_spring_bone_group()
        target_index = active_item.item_indexes[0]
        bone_groups.remove(target_index)

        self.offset_active_item_index(self.component_type)

        return {"FINISHED"}


class VRMHELPER_OT_vrm0_spring_clear_bone_group(VRMHELPER_vrm0_bone_group_base):
    bl_idname = "vrmhelper.vrm0_spring_clear_bone_group"
    bl_label = "Clear Bone Group"
    bl_description = "Clear the active VRM0 Spring Bone Group"

    @classmethod
    def poll(cls, context):
        # UIリストのアイテムが一つ以上存在する｡
        return vrm0_get_active_list_item_in_spring()

    def execute(self, context):
        bone_groups = get_vrm0_extension_spring_bone_group()
        bone_groups.clear()
        get_vrm0_index_root_prop().bone_group = 0

        return {"FINISHED"}


class VRMHELPER_OT_vrm0_spring_add_bone(VRMHELPER_vrm0_bone_group_base):
    bl_idname = "vrmhelper.vrm0_spring_add_bone"
    bl_label = "Add Bone"
    bl_description = "Add a new VRM0 Spring Bone on Active Bone Group"

    @classmethod
    def poll(cls, context):
        # UIリストのアクティブアイテムがボーングループまたはボーンである｡
        if not (active_item := vrm0_get_active_list_item_in_spring()):
            return
        match tuple(active_item.item_type):
            case (0, 1, 0) | (0, 0, 1):
                return True

    def execute(self, context):
        target_armature = get_target_armature()
        # UIリストのアクティブアイテムに対応したボーングループの'bones'に要素を新規作成する｡
        active_item = vrm0_get_active_list_item_in_spring()
        target_index = active_item.item_indexes[0]
        bone_groups = get_vrm0_extension_spring_bone_group()
        active_bone_group: ReferenceVrm0SecondaryAnimationGroupPropertyGroup = bone_groups[target_index]
        bones = active_bone_group.bones
        new_bone: ReferenceBonePropertyGroup = bones.add()
        # アクティブボーンまたはポーズボーンがあればそのボーンを作成した'bone'にセットする｡
        match context.mode:
            case "POSE":
                if active_bone := context.active_pose_bone:
                    new_bone.bone_name = active_bone.name
            case "EDIT_ARMATURE":
                if active_bone := context.active_bone:
                    new_bone.bone_name = active_bone.name

        return {"FINISHED"}


class VRMHELPER_OT_vrm0_spring_remove_bone(VRMHELPER_vrm0_bone_group_base):
    bl_idname = "vrmhelper.vrm0_spring_remove_bone"
    bl_label = "Remove Bone"
    bl_description = "Remove the active VRM0 Spring Bone on Bone Group"

    @classmethod
    def poll(cls, context):
        # アクティブアイテムがボーンである｡
        if not (active_item := vrm0_get_active_list_item_in_spring()):
            return
        match tuple(active_item.item_type):
            case (0, 0, 1):
                return True

    def execute(self, context):
        active_item = vrm0_get_active_list_item_in_spring()
        bone_groups = get_vrm0_extension_spring_bone_group()
        target_group_index = active_item.item_indexes[0]
        active_bone_group: ReferenceVrm0SecondaryAnimationGroupPropertyGroup = bone_groups[target_group_index]
        bones = active_bone_group.bones
        target_bone_index = active_item.item_indexes[1]
        bones.remove(target_bone_index)

        self.offset_active_item_index(self.component_type)

        return {"FINISHED"}


class VRMHELPER_OT_vrm0_spring_clear_bone(VRMHELPER_vrm0_bone_group_base):
    bl_idname = "vrmhelper.vrm0_spring_clear_bone"
    bl_label = "Clear Bone"
    bl_description = "Clear all VRM0 Spring Bone on Bone Group"

    @classmethod
    def poll(cls, context):
        # アクティブアイテムがラベル以外であり､アクティブボーングループにボーンが1つ以上存在する｡
        if not (active_item := vrm0_get_active_list_item_in_spring()):
            return
        match tuple(active_item.item_type):
            case (1, 0, 0):
                return

        bone_groups = get_vrm0_extension_spring_bone_group()
        active_bone_group: ReferenceVrm0SecondaryAnimationGroupPropertyGroup
        active_bone_group = bone_groups[active_item.item_indexes[0]]
        return active_bone_group.bones

    def execute(self, context):
        active_item = vrm0_get_active_list_item_in_spring()
        bone_groups = get_vrm0_extension_spring_bone_group()
        active_bone_group: ReferenceVrm0SecondaryAnimationGroupPropertyGroup
        active_bone_group = bone_groups[active_item.item_indexes[0]]
        active_bone_group.bones.clear()

        self.offset_active_item_index(self.component_type)

        return {"FINISHED"}


class VRMHELPER_OT_vrm0_spring_add_bone_group_from_source(
    VRMHELPER_vrm0_bone_group_base, VRMHELPER_VRM_joint_operator_property
):
    bl_idname = "vrmhelper.vrm0_spring_create_bone_group_from_selected"
    bl_label = "Create Bone Group"
    bl_description = "Create spring bone_groups from selected bones or bone groups"

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
        default=10,
    )

    width: IntProperty(
        name="Width",
        description="Width per element displayed in popup UI",
        default=300,
    )

    # -----------------------------------------------------
    def invoke(self, context, event):
        logger.debug(f"Operator Mode : {self.source_type}")
        match self.source_type:
            case "SELECT":
                vrm0_add_list_item2collider_group_list4operator()
                return context.window_manager.invoke_props_dialog(self, width=self.width * 4)

            case "BONE_GROUP":
                add_list_item2bone_group_list4operator()
                vrm0_add_list_item2collider_group_list4operator()
                # Target Armatureにボーングループが存在しなければキャンセル｡
                length_bg = 0
                if not (bone_groups := get_ui_bone_group_prop()):
                    self.report({"INFO"}, "Bone group does not exist in Target Armature")
                    return {"CANCELLED"}
                length_bg = len(bone_groups)
                # Collider Groupが存在していればその数を取得する｡
                length_cg = 0
                if collider_groups := get_vrm0_extension_collider_group():
                    length_cg = len(collider_groups)

                length = max(length_bg, length_cg)
                width_popup = math.ceil(length / self.rows_property) * self.width
                return context.window_manager.invoke_props_dialog(self, width=width_popup)
            case _:
                return {"CANCELLED"}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row_root = box.row(align=False)

        # 処理対象のボーングループを選択するエリア｡
        if self.source_type == "BONE_GROUP":
            bone_group_collection = get_ui_bone_group_prop()
            anchor_layout = row_root.column(align=True)
            box_sub = anchor_layout.box()
            box_sub.label(text="Target Bone Group")
            row_bg_root = box_sub.row()
            bone_group: VRMHELPER_WM_operator_spring_bone_group_list_items
            for n, bone_group in enumerate(bone_group_collection):
                if n % self.rows_property == 0:
                    col = row_bg_root.column()
                row_sub_bg = col.row(align=True)
                row_sub_bg.prop(bone_group, "is_target", text=bone_group.name)

        # 処理対象のコライダーグループを選択するエリア｡
        collider_group_collection = get_ui_vrm0_operator_collider_group_prop()
        anchor_layout = row_root.column(align=True)
        if self.source_type == "BONE_GROUP":
            anchor_layout = anchor_layout.box()
        anchor_layout.label(text="Target Collider Group")
        row_cg_root = anchor_layout.row()
        collider_group: VRMHELPER_WM_vrm0_operator_spring_collider_group_list_items
        for n, collider_group in enumerate(collider_group_collection):
            if n % self.rows_property == 0:
                col = row_cg_root.column()
            row_sub_cg = col.row(align=True)
            row_sub_cg.prop(collider_group, "is_target", text=collider_group.bone_name)

    def execute(self, context):
        if self.source_type == "SELECT":
            if not context.mode in {"POSE", "EDIT_ARMATURE"}:
                self.report({"ERROR"}, "The current mode must be Pose or Edit Armature.")
                return {"CANCELLED"}

        if not (branch_root_bones := get_branch_root_bones_by_type(self.source_type, get_target_armature())):
            self.report({"INFO"}, "No root bone was detected")
            return {"CANCELLED"}

        # ポーズボーンに割り当てられているBone Group Index毎にボーンをグループ分けする｡
        spring_settings = get_scene_vrm0_spring_bone_group_prop()
        collider_group_list = get_ui_vrm0_operator_collider_group_prop()
        target_armature = get_target_armature()
        pose = target_armature.pose
        target_bones_dict: dict[str, list[bpy.types.Bone]] = {}
        for root_bone in branch_root_bones:
            pose_bone: bpy.types.PoseBone = pose.bones.get(root_bone.name)
            bone_group_index = -1
            if pose_bone.bone_group:
                bone_group_index = pose_bone.bone_group_index
            target_bones_dict.setdefault(bone_group_index, []).append(root_bone)

        # グループ分けされたボーンリストとボーンをSpring Bone GroupとBoneに登録する｡
        for group_index, root_bones in target_bones_dict.items():
            bone_group_name = "Not Assighned Bone Group"
            pose_bone: bpy.types.PoseBone = pose.bones.get(root_bones[0].name)
            if pose_bone.bone_group:
                source_bone_group = pose.bone_groups[group_index]
                bone_group_name = source_bone_group.name
            spring_bone_groups = get_vrm0_extension_spring_bone_group()
            registered_bones = {bone.bone_name for group in spring_bone_groups for bone in group.bones}

            # group_name毎にスプリングボーングループを作成する｡
            target_group: ReferenceVrm0SecondaryAnimationGroupPropertyGroup
            if target_group := get_spring_bone_group_by_comment(bone_group_name):
                logger.debug(f"Already Registered Group : {bone_group_name}")

            else:  # Spring Bone Groupの作成とパラメーター適用
                target_group = spring_bone_groups.add()
                target_group.comment = bone_group_name
                target_group.stiffness = spring_settings.stiffness
                target_group.drag_force = spring_settings.drag_force
                target_group.hit_radius = spring_settings.hit_radius
                target_group.gravity_power = spring_settings.gravity_power
                target_group.gravity_dir = spring_settings.gravity_dir

            # カテゴリーに属するルートボーンをスプリングボーンに登録する｡
            for bone in root_bones:
                # 既にいずれかのスプリングボーングループに登録されているボーンの場合はスキップする｡
                if bone.name in registered_bones:
                    logger.debug(f"Already Registered Bone : {bone.name}")
                    continue
                new_bone: ReferenceBonePropertyGroup = target_group.bones.add()
                new_bone.bone_name = bone.name

            # 対象に設定したコライダーグループをスプリングボーングループに登録する｡
            collider_groups = target_group.collider_groups
            candidate_collider_group: VRMHELPER_WM_vrm0_operator_spring_collider_group_list_items

            registered_collider_groups = [cg.name for cg in target_group.collider_groups]
            for candidate_collider_group in collider_group_list:
                if not candidate_collider_group.is_target:
                    continue

                # 既に登録され当ているコライダーグループはスキップする｡
                if candidate_collider_group.name in registered_collider_groups:
                    logger.debug(f"Already Registered Collider Group : {candidate_collider_group.bone_name}")
                    continue
                new_collider_group: ReferenceStringPropertyGroup = collider_groups.add()
                new_collider_group.value = candidate_collider_group.name

            print("\n")

        return {"FINISHED"}


class VRMHELPER_OT_vrm0_spring_assign_parameters_to_bone_group(
    VRMHELPER_vrm0_bone_group_base, VRMHELPER_VRM_joint_operator_property
):
    bl_idname = "vrmhelper.vrm0_spring_assign_parameters_to_bone_group"
    bl_label = "Assign Spring Bone Group Parameters"
    bl_description = "Assing Parameters to selected Spring Bone Group"

    # ----------------------------------------------------------
    #    Property
    # ----------------------------------------------------------
    source_type: EnumProperty(
        name="Source Type",
        description="Description",
        items=(
            ("SINGLE", "Single", "Works only on active Spring Bone Group"),
            ("MULTIPLE", "Multiple", "Works only on selected Spring Bone Group"),
        ),
        default="SINGLE",
    )

    set_parameters: BoolProperty(
        name="Set Parameters",
        description="Select whether to apply joint parameters",
        default=False,
    )

    rows_property: IntProperty(
        name="Rows Property",
        description="Number of properties displayed per column",
        default=12,
    )

    width: IntProperty(
        name="Width",
        description="Width per element displayed in popup UI",
        default=300,
    )

    spg_collection = None
    cg_collection = None

    # -----------------------------------------------------

    def invoke(self, context, event):
        os.system("cls")
        logger.debug(f"Operator Mode : {self.source_type}")
        # 処理対象指定用UIリストの要素を更新する｡
        vrm0_add_list_item2spring_bone_group_list4operator()
        vrm0_add_list_item2collider_group_list4operator()
        match self.source_type:
            case "SINGLE":
                if not (active_item := vrm0_get_active_list_item_in_spring()):
                    self.report({"ERROR"}, "No Existing Any Spring Bone Group")
                    return {"CANCELLED"}

                active_indexes = active_item.item_indexes
                for spg in get_ui_vrm0_operator_spring_bone_group_prop():
                    if spg.group_index != active_indexes[0]:
                        spg.is_target = False
                return context.window_manager.invoke_props_dialog(self, width=self.width * 4)

            case "MULTIPLE":
                # Spring Bone Groupが1つも存在しなければキャンセル｡
                if not (spring_bone_groups := get_ui_vrm0_operator_spring_bone_group_prop()):
                    self.report({"ERROR"}, "No Existing Any Spring Bone Group")
                    return {"CANCELLED"}

                length_sbg = len(spring_bone_groups)
                # Collider Groupが存在していればその数を取得する｡
                length_cg = 0
                if collider_groups := get_vrm_extension_property("COLLIDER_GROUP"):
                    length_cg = len(collider_groups)

                length = max(length_sbg, length_cg)
                width_popup = math.ceil(length / self.rows_property) * self.width
                return context.window_manager.invoke_props_dialog(self, width=width_popup)

            case _:
                self.report({"ERROR"}, f"Invalid Argument :  source_type -- {self.source_type}")
                return {"CANCELLED"}

    def draw(self, context):
        self.spg_collection = get_ui_vrm0_operator_spring_bone_group_prop()
        self.cg_collection = get_ui_vrm0_operator_collider_group_prop()

        if not (self.spg_collection and self.cg_collection):
            self.report({"ERROR"}, "Neither Spring Bone Group nor Collider Group is selected")
            return

        # フィルターワードに従ってスプリングの中から対象候補を抽出する｡
        spring_settings = get_scene_vrm0_spring_bone_group_prop()
        if filter_strings := spring_settings.filter_of_adjusting_target_filter:
            self.spg_collection = [i for i in self.spg_collection if filter_strings in i.name]
        # ----------------------------------------------------------
        #    UIの描画
        # ----------------------------------------------------------
        layout = self.layout
        box = layout.box()
        # パラメーター変更の可否を選択するプロパティ
        box.prop(self, "set_parameters")
        row = box.row(align=True)
        # 処理対象のSpringを選択するエリア(Multiple Modeのみ)
        if self.source_type == "MULTIPLE":
            anchor_layout = row.column(align=True)
            anchor_layout.label(text="Target Spring Bone Group")
            box_sub = anchor_layout.box()
            row_root = box_sub.row()
            for n, spg in enumerate(self.spg_collection):
                if n % self.rows_property == 0:
                    col = row_root.column()
                row_sub = col.row(align=True)
                row_sub.prop(spg, "is_target", text=spg.name)

        # 処理対象のCollider Groupを選択するエリア
        anchor_layout = row.column(align=True)
        anchor_layout.label(text="Target Collider Group")
        box_sub = anchor_layout.box()
        row_root = box_sub.row()
        for n, cg in enumerate(self.cg_collection):
            if n % self.rows_property == 0:
                col = row_root.column()
            row_sub = col.row(align=True)
            row_sub.prop(cg, "is_target", text=cg.bone_name)

    def execute(self, context):
        # フィルターワードに従ってスプリングの中から対象候補を抽出する｡
        spring_settings = get_scene_vrm0_spring_bone_group_prop()
        springs_filter_list = []
        if filter_strings := spring_settings.filter_of_adjusting_target_filter:
            springs_filter_list = [i.name for i in self.spg_collection if filter_strings in i.name]

        # ターゲットに設定されたSpring Bone GroupにUI上で設定したパラメーターを適用する｡
        spg: ReferenceVrm0SecondaryAnimationGroupPropertyGroup
        for spg, filter in zip(get_vrm0_extension_spring_bone_group(), self.spg_collection):
            # フィルターワードを含まないグループはスキップする｡
            if springs_filter_list and not spg.comment in springs_filter_list:
                logger.debug(f"Skip : Not include filter words in the name -- {spg.comment}")
                continue

            # ポップアップUIでターゲットに指定しなかったグループはスキップする｡
            if not filter.is_target:
                logger.debug(f"Skip ; Is not Target -- {spg.comment}")
                continue

            logger.debug(f"Target Spring Bone Group : {spg.comment}")
            # パラメーターを適用する場合はUI上で設定したプロパティの値を適用する｡
            if self.set_parameters:
                spg.stiffiness = spring_settings.stiffness
                spg.drag_force = spring_settings.drag_force
                spg.hit_radius = spring_settings.hit_radius
                spg.gravity_power = spring_settings.gravity_power
                spg.gravity_dir[0] = spring_settings.gravity_dir[0]
                spg.gravity_dir[1] = spring_settings.gravity_dir[1]
                spg.gravity_dir[2] = spring_settings.gravity_dir[2]

            # ポップアップUIでターゲットに指定したCollider Groupoがあれば登録する｡
            # TODO : 登録前に空のスロットを削除する｡
            registered_cg = [i.value for i in spg.collider_groups]
            for cg in self.cg_collection:
                if not cg.is_target:
                    continue
                if cg.name in registered_cg:
                    continue
                spg.collider_groups.add().value = cg.name

        return {"FINISHED"}


class VRMHELPER_OT_vrm0_spring_add_linked_collider_group(VRMHELPER_vrm0_linked_collider_group_base):
    bl_idname = "vrmhelper.vrm_spring_add_linked_collider_group"
    bl_label = "Add Linked Collider Group"
    bl_description = "Add a new VRM0 Spring Bone's Collider Group"

    def execute(self, context):
        target_collider_groups = get_active_linked_collider_groups()
        target_cg: ReferenceStringPropertyGroup

        active_bone = get_active_bone()
        # 現在のモードに応じて選択ボーンを取得する｡
        selected_bone_names = get_selected_bone_names()

        # アクティブボーンが存在しない又は選択ボーンになっていない場合は空のスロットを追加する｡
        if not (active_bone and active_bone.name in selected_bone_names):
            target_collider_groups.add()
            return {"FINISHED"}

        # アクティブボーンに対応するCollider Groupが存在しない場合は空のスロットを追加する｡
        collider_groups = get_vrm0_extension_collider_group()
        corresponding_cg_dict = gen_corresponding_collider_group_dict(collider_groups, selected_bone_names)
        if not (corresponding_cg_list := corresponding_cg_dict.get(active_bone.name)):
            target_collider_groups.add()
            return {"FINISHED"}

        # 既に登録済みのCollider Groupである場合はスキップする｡
        registerd_colliders = [i.value for i in target_collider_groups]
        corresponding_collider = corresponding_cg_list[0]
        if corresponding_collider.name in registerd_colliders:
            self.report(
                {"INFO"},
                f"The Collider Group corresponding to Active Bone has already been registered : {active_bone.name}.",
            )
            target_collider_groups.add()
        else:
            self.report(
                {"INFO"}, f"Registered the Collider Group corresponding to Active Bone : {active_bone.name}"
            )
            # Collider Groupを参照していないスロットがあればそちらを優先してターゲットとする｡
            if not (target_cg := get_empty_linked_collider_group_slot(target_collider_groups)):
                target_cg = target_collider_groups.add()
            target_cg.value = corresponding_collider.name

        return {"FINISHED"}


class VRMHELPER_OT_vrm0_spring_remove_linked_collider_group(VRMHELPER_vrm0_linked_collider_group_base):
    bl_idname = "vrmhelper.vrm0_spring_remove_linked_collider_group"
    bl_label = "Remove Linked Collider Group"
    bl_description = "Remove the linked collider group that is active in the list"

    @classmethod
    def poll(self, context):
        # リンクされたCollider Groupが1つ以上存在する｡
        return get_active_linked_collider_groups()

    def execute(self, context):
        self.report({"INFO"}, "Remove the Active Linked Collider Group")
        target_collider_groups = get_active_linked_collider_groups()
        active_list_item = vrm0_get_active_list_item_in_linked_collider_group()
        target_index = active_list_item.item_indexes[1]
        target_collider_groups.remove(target_index)

        self.offset_active_item_index(self.component_type)

        return {"FINISHED"}


class VRMHELPER_OT_vrm0_spring_clear_linked_collider_group(VRMHELPER_vrm0_linked_collider_group_base):
    bl_idname = "vrmhelper.vrm0_spring_clear_linked_collider_group"
    bl_label = "Clear Linked Collider Group"
    bl_description = "Clear all linked collider groups"

    @classmethod
    def poll(self, context):
        # リンクされたCollider Groupが1つ以上存在する｡
        return get_active_linked_collider_groups()

    def execute(self, context):
        self.report({"INFO"}, "Registered Linked Collider Group")
        target_collider_groups = get_active_linked_collider_groups()
        target_collider_groups.clear()

        self.offset_active_item_index(self.component_type)

        return {"FINISHED"}


class VRMHELPER_OT_vrm0_spring_register_linked_collider_group(VRMHELPER_vrm0_linked_collider_group_base):
    bl_idname = "vrmhelper.vrm0_spring_register_linked_collider_group"
    bl_label = "Register Linked Collider Group"
    bl_description = "Register linked collider groups from Selected Bone"

    def execute(self, context):
        if not (selected_bone_names := get_selected_bone_names()):
            self.report({"ERROR"}, "Selected bone does not exist")
            return {"CANCELLED"}

        self.report({"INFO"}, "RegisteredLinked Collider Group from Selected Bone")
        target_collider_groups = get_active_linked_collider_groups()
        registerd_colliders = [i.value for i in target_collider_groups]
        collider_groups = get_vrm0_extension_collider_group()
        corresponding_cg_dict = gen_corresponding_collider_group_dict(collider_groups, selected_bone_names)

        for bone_name in selected_bone_names:
            # ボーン名に対応するCollider Groupが存在しなければスキップする｡
            if not (corresponding_cg_list := corresponding_cg_dict.get(bone_name)):
                logger.debug(f"Bone with no corresponding Collider Group : {bone_name}")
                continue

            # ボーン名に対応するCollider GroupをSpring Bone Groupに登録する｡
            for cg in corresponding_cg_list:
                # 既に登録済みのCollider Groupである場合はスキップする｡
                if cg.name in registerd_colliders:
                    logger.debug(f"The Collider Group corresponding already been registered : {cg.name}.")
                    continue

                # Collider Groupを参照していないスロットがあればそちらを優先してターゲットとする｡
                if not (target_cg := get_empty_linked_collider_group_slot(target_collider_groups)):
                    target_cg = target_collider_groups.add()
                target_cg.value = cg.name

        return {"FINISHED"}


# TODO : Collider Groupを登録するポップアップUIで全選択/全解除/反転のオペレーターが欲しい｡

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
    VRMHELPER_OT_vrm0_blend_shape_set_bind_from_scene,
    VRMHELPER_OT_vrm0_blend_shape_set_material_value_from_scene,
    VRMHELPER_OT_vrm0_blend_shape_set_both_binds_from_scene,
    VRMHELPER_OT_vrm0_blend_shape_restore_initial_parameters,
    # ----------------------------------------------------------
    #    Collider Group
    # ----------------------------------------------------------
    VRMHELPER_OT_vrm0_collider_group_add_group,
    VRMHELPER_OT_vrm0_collider_group_remove_active_group,
    VRMHELPER_OT_vrm0_collider_group_clear_group,
    VRMHELPER_OT_vrm0_collider_group_create_active_collider,
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
    VRMHELPER_OT_vrm0_spring_assign_parameters_to_bone_group,
    # ----------------------------------------------------------
    #    Spring Bone Group's Collider Group
    # ----------------------------------------------------------
    VRMHELPER_OT_vrm0_spring_add_linked_collider_group,
    VRMHELPER_OT_vrm0_spring_remove_linked_collider_group,
    VRMHELPER_OT_vrm0_spring_clear_linked_collider_group,
    VRMHELPER_OT_vrm0_spring_register_linked_collider_group,
)
