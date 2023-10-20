if "bpy" in locals():
    import importlib

    reloadable_modules = [
        "preparation_logger",
        "utils_common",
        "utils_vrm_base",
        "utils_vrm0_first_person",
        "utils_vrm0_blend_shape",
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

from ..addon_classes import (
    ReferenceVrm0BlendShapeGroupPropertyGroup,
    ReferenceVrm0BlendShapeBindPropertyGroup,
    ReferenceVrm0MaterialValueBindPropertyGroup,
)

from ..property_groups import (
    VRMHELPER_SCENE_vrm0_ui_list_active_indexes,
    VRMHELPER_SCENE_vrm0_blend_shape_settings,
    VRMHELPER_WM_vrm0_blend_shape_material_list_items,
    # ---------------------------------------------------------------------------------
    get_target_armature,
    get_target_armature_data,
    get_vrm0_wm_root_prop,
    get_vrm0_scene_root_prop,
    get_scene_vrm0_blend_shape_prop,
    get_scene_vrm0_mtoon_stored_prop,
    # ----------------------------------------------------------
    get_ui_vrm0_first_person_prop,
    get_ui_vrm0_blend_shape_material_prop,
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
    get_vrm0_extension_property_first_person,
    get_vrm0_extension_property_blend_shape,
    get_vrm0_extension_active_blend_shape_group,
    reset_shape_keys_value_in_morph_binds,
    store_mtoon_current_values,
    set_mtoon_default_values,
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
)

from ..operators import (
    VRMHELPER_operator_base,
    VRMHELPER_vrm0_first_person_base,
    VRMHELPER_vrm0_blend_shape_base,
    VRMHELPER_vrm0_blend_shape_sub,
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
        mesh_annotations = get_vrm0_extension_property_first_person().mesh_annotations
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
        return get_vrm0_extension_property_first_person().mesh_annotations

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
        return get_vrm0_extension_property_first_person().mesh_annotations

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
        return get_vrm0_extension_property_first_person().mesh_annotations

    def execute(self, context):
        mesh_annotations = get_vrm0_extension_property_first_person().mesh_annotations
        mesh_annotations.clear()

        self.offset_active_item_index(self.component_type)

        return {"FINISHED"}


class VRMHELPER_OT_0_blend_shape_create_blend_shape(VRMHELPER_vrm0_blend_shape_base):
    bl_idname = "vrm_helper.vrm0_blend_shape_create_blend_shape"
    bl_label = "Create Blend Shape"
    bl_description = "Create a new Blend Shape Proxy to the target armature"
    bl_options = {"UNDO"}

    def execute(self, context):
        target_armature = get_target_armature()

        bpy.ops.vrm.add_vrm0_blend_shape_group(armature_name=target_armature.name, name="new")

        return {"FINISHED"}


class VRMHELPER_OT_0_blend_shape_remove_blend_shape(VRMHELPER_vrm0_blend_shape_base):
    bl_idname = "vrm_helper.vrm0_blend_shape_remove_blend_shape"
    bl_label = "Remove Blend_Shape"
    bl_description = "Remove the active blend_shape from the target armature"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        # ブレンドシェイプが1つ以上存在している
        blend_shapes = get_vrm0_extension_property_blend_shape().blend_shape_groups
        return blend_shapes

    def execute(self, context):
        target_armature = get_target_armature()
        blend_shape_master = get_vrm0_extension_property_blend_shape()
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
        blend_shapes = get_vrm0_extension_property_blend_shape().blend_shape_groups
        return blend_shapes

    def execute(self, context):
        blend_shape_master = get_vrm0_extension_property_blend_shape()
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
        blend_shapes = get_vrm0_extension_property_blend_shape().blend_shape_groups
        return blend_shapes

    def execute(self, context):
        blend_shape_master = get_vrm0_extension_property_blend_shape()
        blend_shape_groups = blend_shape_master.blend_shape_groups
        target_index = blend_shape_master.active_blend_shape_group_index
        active_blend_shape: ReferenceVrm0BlendShapeGroupPropertyGroup = blend_shape_groups[target_index]

        # ----------------------------------------------------------
        #    Morph Target Binds
        # ----------------------------------------------------------
        # アクティブエクスプレッションのMorpth Target Bindsの全てのBindの
        # メッシュ/シェイプキーに対してウェイトを反映する｡
        # 対象メッシュは処理前に全てのシェイプキーのウェイトを0にする｡
        morph_binds = active_blend_shape.binds
        reset_shape_keys_value_in_morph_binds(morph_binds)

        # Morph Target Bindに設定されているBlend Shapeの値を対応するShape Keyの値に代入する｡
        existing_bind_info = {}
        # Bindsに登録されている全メッシュとそれに関連付けられたシェイプキー､ウェイトを取得する｡
        for bind in morph_binds:
            bind: ReferenceVrm0BlendShapeBindPropertyGroup = bind
            bind_mesh = bpy.data.objects.get(bind.mesh.mesh_object_name).data
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
            # TODO : Material Valueの設定
            # set_mtoon_default_values(mat)

        return {"FINISHED"}


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
        blend_shape_master = get_vrm0_extension_property_blend_shape()
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
        blend_shape_master = get_vrm0_extension_property_blend_shape()
        blend_shape_index = blend_shape_master.active_blend_shape_group_index
        active_blend_shape: ReferenceVrm0BlendShapeGroupPropertyGroup = blend_shape_master.blend_shape_groups[
            blend_shape_index
        ]
        # TODO : アクティブ要素がラベルであればそのラベルに属する要素を全て削除｡
        #        BindやMaterial Valueであればその一つを削除する｡

        match self.mode:
            case "BIND":
                bind_index = active_blend_shape.active_bind_index
                bpy.ops.vrm.remove_vrm0_blend_shape_bind(
                    armature_name=target_armature.name,
                    blend_shape_group_index=blend_shape_index,
                    bind_index=bind_index,
                )

            case "MATERIAL":
                value_index = active_blend_shape.active_material_value_index
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


class VRMHELPER_OT_vrm0_blend_shape_set_both_binds_from_scene(VRMHELPER_vrm0_blend_shape_sub):
    bl_idname = "vrm_helper.vrm0_blend_shape_set_both_binds_from_scene"
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
        active_blend_shape = get_active_blend_shape()
        # ----------------------------------------------------------
        #    Binds
        # ----------------------------------------------------------
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

        # ----------------------------------------------------------
        #    Material Values
        # ----------------------------------------------------------
        aaaaaa

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
)
