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


import os, time, uuid
from pprint import pprint
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
    FloatProperty,
    FloatVectorProperty,
    EnumProperty,
)

from mathutils import (
    Vector,
)

from ..preferences import (
    get_addon_collection_name,
)

from ..property_groups import (
    get_target_armature,
    get_target_armature_data,
    # ----------------------------------------------------------
    get_ui_vrm1_first_person_prop,
    get_ui_vrm1_expression_morph_prop,
    get_ui_vrm1_expression_material_prop,
    get_ui_vrm1_collider_group_prop,
    get_ui_vrm1_operator_bone_group_prop,
    get_ui_vrm1_operator_spring_prop,
    get_ui_vrm1_constraint_prop,
    # ----------------------------------------------------------
    get_vrm1_index_root_prop,
    get_vrm1_active_index_prop,
    get_scene_vrm1_first_person_prop,
    get_scene_vrm1_constraint_prop,
    get_scene_vrm1_mtoon_stored_prop,
)

from ..utils_common import (
    filtering_mesh_type,
    link_object2collection,
    get_selected_bone,
    is_including_empty_in_selected_object,
    setting_vrm_helper_collection,
    get_all_materials_from_source_collection_objects,
    get_all_materials,
)

from ..utils_vrm_base import (
    get_vrm_extension_property,
    is_existing_target_armature_and_mode,
    get_bones_for_each_branch_by_type,
    store_mtoon1_current_values,
    set_mtoon1_default_values,
)

from .utils_vrm1_first_person import (
    search_same_name_mesh_annotation,
    remove_mesh_annotation,
    sort_mesh_annotations,
)

from .utils_vrm1_expression import (
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
    #    Collider
    # ----------------------------------------------------------
    get_pose_bone_by_name,
    generate_head_collider_position,
    generate_tail_collider_position,
    remove_vrm1_collider_by_selected_object,
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
    add_list_item2bone_group_list4operator,
    add_list_item2collider_group_list4operator,
    add_list_item2joint_list4operator,
)

from .utils_vrm1_constraint import (
    add_items2constraint_ui_list,
    detect_constrainted_and_target_element,
    set_vrm_constraint_parametters,
    detect_constraint_or_label,
    remove_existing_vrm_constraint,
)

from ..operators import (
    VRMHELPER_operator_base,
    VRMHELPER_first_person_base,
    VRMHELPER_expression_base,
    VRMHELPER_expression_sub_morph,
    VRMHELPER_expression_sub_material,
    VRMHELPER_collider_base,
    VRMHELPER_collider_group_base,
    VRMHELPER_spring_base,
    VRMHELPER_constraint_base,
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
------------------------------------------------------------
    Class
------------------------------------------------------------
---------------------------------------------------------"""


class VRMHELPER_VRM1_joint_property:
    """
    ジョイント用オペレータープロパティーを持たせた基底クラス｡
    """

    hit_radius: FloatProperty(
        name="Hit Radius",
        description="radius value of joint set by operator",
        default=0.01,
        min=0.0,
        soft_max=0.5,
        options={"HIDDEN"},
    )

    stiffness: FloatProperty(
        name="Stiffness",
        description="stiffness value of joint set by operator",
        default=1.0,
        min=0.0,
        soft_max=4.0,
        options={"HIDDEN"},
    )

    drag_force: FloatProperty(
        name="Drag Force",
        description="drag force value of joint set by operator",
        default=0.5,
        min=0.0,
        max=1.0,
        options={"HIDDEN"},
    )

    gravity_power: FloatProperty(
        name="Gravity Power",
        description="gravity power value  of joint set by operator",
        default=0.0,
        min=0.0,
        soft_max=2.0,
        options={"HIDDEN"},
    )

    gravity_dir: FloatVectorProperty(
        name="Gravity Direction",
        description="gravity direction value of joint set by operator",
        default=(0.0, 0.0, -1.0),
        size=3,
        subtype="XYZ",
        options={"HIDDEN"},
    )

    damping_ratio: FloatProperty(
        name="Damping Ratio",
        description="Descriptiondamping rate of the parameters of the joints to be created",
        default=1.0,
        min=0.01,
    )


"""---------------------------------------------------------
    First Person
---------------------------------------------------------"""


class VRMHELPER_OT_vrm1_first_person_set_annotation(VRMHELPER_first_person_base):
    bl_idname = "vrm_helper.set_mesh_annotation"
    bl_label = "Set Mesh Annotation"
    bl_description = "Add a new annotation to First Person Annotation and set the selected object to that bone_name"

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
        for obj in [
            obj for obj in context.selected_objects if filtering_mesh_type(obj)
        ]:
            if annotation := search_same_name_mesh_annotation(obj.name):
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
        sort_mesh_annotations()

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_first_person_remove_annotation_from_list(
    VRMHELPER_first_person_base
):
    bl_idname = "vrm_helper.remove_mesh_annotation_from_list"
    bl_label = "Remove Mesh Annotation from Active Item"
    bl_description = (
        "Remove active annotation in the list from Target Armature's VRM Extension"
    )

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
        remove_mesh_annotation(active_item_name)

        self.offset_active_item_index(self.component_type)

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_first_person_remove_annotation_from_select_objects(
    VRMHELPER_first_person_base
):
    bl_idname = "vrm_helper.remove_mesh_annotation"
    bl_label = "Remove by Selected Objects"
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
            remove_mesh_annotation(obj.name)

        self.offset_active_item_index(self.component_type)

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_first_person_clear_annotation(VRMHELPER_first_person_base):
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
class VRMHELPER_OT_vrm1_expression_create_custom_expression(VRMHELPER_expression_base):
    bl_idname = "vrm_helper.vrm1_expression_create_custom_expression"
    bl_label = "Create Custom Expression"
    bl_description = "Create a new custom expression to the target armature"
    bl_options = {"UNDO"}

    def execute(self, context):
        custom_expressions = get_vrm_extension_property("EXPRESSION").custom
        new_item = custom_expressions.add()
        new_item.custom_name = "custom_expression"

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_expression_remove_custom_expression(VRMHELPER_expression_base):
    bl_idname = "vrm_helper.vrm1_expression_remove_custom_expression"
    bl_label = "Remove Custom Expression"
    bl_description = "Remove the active custom expression from the target armature"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        # アクティブアイテムがカスタムエクスプレッションである
        return (
            active_item := get_active_list_item_in_expression()
        ) and not active_item.custom_expression_index < 0

    def execute(self, context):
        custom_expressions = get_vrm_extension_property("EXPRESSION").custom
        active_item = get_active_list_item_in_expression()
        custom_expressions.remove(active_item.custom_expression_index)

        self.offset_active_item_index(self.component_type)

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_expression_clear_custom_expression(VRMHELPER_expression_base):
    bl_idname = "vrm_helper.vrm1_expression_clear_custom_expression"
    bl_label = "Clear Custom Expression"
    bl_description = "Clear all custom expressions from the target armature"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        # Expressionsにカスタムエクスプレッションが1つ以上存在している
        return get_vrm_extension_property("EXPRESSION").custom

    def execute(self, context):
        custom_expressions = get_vrm_extension_property("EXPRESSION").custom
        custom_expressions.clear()

        self.offset_active_item_index(self.component_type)

        return {"FINISHED"}


# ----------------------------------------------------------
#    Morph Target
# ----------------------------------------------------------
class VRMHELPER_OT_vrm1_expression_morph_create_morph(VRMHELPER_expression_sub_morph):
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


class VRMHELPER_OT_vrm1_expression_morph_remove_morph(VRMHELPER_expression_sub_morph):
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


class VRMHELPER_OT_vrm1_expression_morph_clear_morphs(VRMHELPER_expression_sub_morph):
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


class VRMHELPER_OT_vrm1_expression_set_morph_from_scene(VRMHELPER_expression_sub_morph):
    bl_idname = "vrm_helper.vrm1_expression_set_morph_from_scene"
    bl_label = "Set Morph Target from Scene"
    bl_description = (
        "Set Morph Target Bind from the shape keys of the target objects on the scene"
    )
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        # 1つ以上のオブジェクトがリンクされた'VRM1 Expression'のコレクションが存在する｡
        return (
            c := bpy.data.collections.get(
                get_addon_collection_name("VRM1_EXPRESSION_MORPH")
            )
        ) and c.all_objects

    def execute(self, context):
        morph_target_binds = get_active_expression().morph_target_binds
        source_collection = bpy.data.collections.get(
            get_addon_collection_name("VRM1_EXPRESSION_MORPH")
        )

        for obj in source_collection.all_objects:
            # オブジェクトのメッシュデータに2つ以上のキーブロックを持ったシェイプキーが存在する｡
            if not (sk := obj.data.shape_keys) and len(sk.key_blocks) <= 1:
                continue

            logger.debug(
                f"###\n{'':#>100}\nCurrent Processed Object : {obj.name}\n{'':#>100}"
            )
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
                    logger.debug(
                        f"Registered New Bind -- {obj.name} : {shape_key.name}"
                    )
                    new_morph_bind = morph_target_binds.add()
                    new_morph_bind.node.mesh_object_name = obj.name
                    new_morph_bind.index = shape_key.name
                    new_morph_bind.weight = shape_key.value

        self.offset_active_item_index(self.component_type)

        return {"FINISHED"}


# ----------------------------------------------------------
#    Material Color & Texture Transform
# ----------------------------------------------------------
class VRMHELPER_OT_vrm1_expression_material_create_color(
    VRMHELPER_expression_sub_material
):
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


class VRMHELPER_OT_vrm1_expression_material_remove_color(
    VRMHELPER_expression_sub_material
):
    bl_idname = "vrm_helper.vrm1_expression_material_remove_color"
    bl_label = "Remove Material Color Bind"
    bl_description = "Remove the active material color bind from the active expression"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        # アクティブアイテムがMaterial Colorである
        if materials := get_ui_vrm1_expression_material_prop():
            return materials[
                get_vrm1_active_index_prop("EXPRESSION_MATERIAL")
            ].item_type[1]

    def execute(self, context):
        materials = get_ui_vrm1_expression_material_prop()
        active_item = materials[get_vrm1_active_index_prop("EXPRESSION_MATERIAL")]

        material_color_binds = get_active_expression().material_color_binds
        material_color_binds.remove(active_item.bind_index)

        self.offset_active_item_index(self.component_type)

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_expression_material_clear_colors(
    VRMHELPER_expression_sub_material
):
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


class VRMHELPER_OT_vrm1_expression_material_create_transform(
    VRMHELPER_expression_sub_material
):
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


class VRMHELPER_OT_vrm1_expression_material_remove_transform(
    VRMHELPER_expression_sub_material
):
    bl_idname = "vrm_helper.vrm1_expression_material_remove_transform"
    bl_label = "Remove Material Color Bind"
    bl_description = (
        "Remove the active texture transform bind from the active expression"
    )
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        # アクティブアイテムがMaterial Colorである
        if materials := get_ui_vrm1_expression_material_prop():
            return materials[
                get_vrm1_active_index_prop("EXPRESSION_MATERIAL")
            ].item_type[2]

    def execute(self, context):
        materials = get_ui_vrm1_expression_material_prop()
        active_item = materials[get_vrm1_active_index_prop("EXPRESSION_MATERIAL")]

        texture_transform_binds = get_active_expression().texture_transform_binds
        texture_transform_binds.remove(active_item.bind_index)

        self.offset_active_item_index(self.component_type)

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_expression_material_clear_transforms(
    VRMHELPER_expression_sub_material
):
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


class VRMHELPER_OT_vrm1_expression_set_material_bind_from_scene(
    VRMHELPER_expression_sub_material
):
    bl_idname = "vrm_helper.vrm1_expression_set_material_bind_from_scene"
    bl_label = "Set Material Bind from Scene"
    bl_description = (
        "Set Material Bind from the shape keys of the target objects on the scene"
    )
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        # 1つ以上のオブジェクトがリンクされた'VRM1 Expression'のコレクションが存在する｡
        return (
            c := bpy.data.collections.get(
                get_addon_collection_name("VRM1_EXPRESSION_MATERIAL")
            )
        ) and c.all_objects

    def execute(self, context):
        os.system("cls")

        active_expression = get_active_expression()
        material_color_binds = active_expression.material_color_binds
        texture_transform_binds = active_expression.texture_transform_binds
        source_collection = bpy.data.collections.get(
            get_addon_collection_name("VRM1_EXPRESSION_MATERIAL")
        )

        # ソースとなるマテリアルを取得する｡
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
            mtoon_color_parameters_dict = (
                search_existing_material_color_bind_and_update(
                    source_material, material_color_binds
                )
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
            mtoon_transform_parameters_dict = (
                search_existing_texture_transform_bind_and_update(
                    source_material, texture_transform_binds
                )
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
                    converted_parameter_name = convert_str2transform_bind_type(
                        parameter
                    )
                    logger.debug(
                        f"Set Parameter : {converted_parameter_name} -- {value}"
                    )
                    new_transform_bind.material = source_material
                    setattr(new_transform_bind, converted_parameter_name, value)
        # TODO : Lit Color以外のTexture Transformの値をLit Colorと同じにする｡

        # ----------------------------------------------------------
        self.offset_active_item_index("EXPRESSION_MATERIAL")

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_expression_restore_mtoon1_parameters(
    VRMHELPER_expression_sub_material
):
    bl_idname = "vrm_helper.vrm1_expression_restore_mtoon1_parameters"
    bl_label = "Store MToon1 Parameters"
    bl_description = "Restore stored parameters of Mtoon1"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        return (
            c := bpy.data.collections.get(
                get_addon_collection_name("VRM1_EXPRESSION_MATERIAL")
            )
        ) and c.all_objects

    def execute(self, context):
        source_collection = bpy.data.collections.get(
            get_addon_collection_name("VRM1_EXPRESSION_MATERIAL")
        )
        for mat in get_all_materials_from_source_collection_objects(source_collection):
            set_mtoon1_default_values(mat)

        # TODO : Lit Color以外のTexture Transformの値をLit Colorと同じにする｡

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_expression_discard_stored_mtoon1_parameters(
    VRMHELPER_expression_sub_material
):
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


class VRMHELPER_OT_vrm1_expression_store_mtoon1_parameters(
    VRMHELPER_expression_sub_material
):
    bl_idname = "vrm_helper.vrm1_expression_store_mtoon1_parameters"
    bl_label = "Store MToon1 Parameters"
    bl_description = "Obtains and stores the current parameters of Mtoon1"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        # 1つ以上のオブジェクトがリンクされた'VRM1 Expression'のコレクションが存在する｡
        return (
            c := bpy.data.collections.get(
                get_addon_collection_name("VRM1_EXPRESSION_MATERIAL")
            )
        ) and c.all_objects

    def execute(self, context):
        os.system("cls")
        source_collection = bpy.data.collections.get(
            get_addon_collection_name("VRM1_EXPRESSION_MATERIAL")
        )
        mtoon1_stored_parameters = get_scene_vrm1_mtoon_stored_prop()
        mtoon1_stored_parameters.clear()

        for mat in get_all_materials_from_source_collection_objects(source_collection):
            logger.debug(f"Stored MToon1 Parameters : {mat.name}")
            new_item = mtoon1_stored_parameters.add()
            new_item.name = mat.name
            store_mtoon1_current_values(new_item, mat)

        return {"FINISHED"}


class VRMHELPER_OT_vrm1_expression_assign_expression_to_scene(
    VRMHELPER_expression_sub_material
):
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
        if existing_bind_mesh := {
            bpy.data.objects.get(bind.node.mesh_object_name).data
            for bind in morph_target_binds
        }:
            for mesh in existing_bind_mesh:
                key_blocks = mesh.shape_keys.key_blocks
                for key in key_blocks:
                    key.value = 0.0

        existing_bind_info = {}
        for bind in morph_target_binds:
            existing_bind_info.setdefault(
                bpy.data.objects.get(bind.node.mesh_object_name).data, []
            ).append((bind.index, bind.weight))
        for mesh, sk_info in existing_bind_info.items():
            for sk_name, sk_value in sk_info:
                sk = mesh.shape_keys.key_blocks.get(sk_name)
                sk.value = sk_value

        # Color/Transform Bindで指定されている全てのマテリアルの特定パラメーターは一度すべて初期値にセットする｡
        if existing_bind_material := {
            bind.material for bind in material_color_binds
        } | {bind.material for bind in texture_transform_binds}:
            for mat in existing_bind_material:
                if not mat:
                    continue
                logger.debug(f"Reset Values : {mat.name}")
                set_mtoon1_default_values(mat)

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


class VRMHELPER_OT_vrm1_expression_change_bind_material(
    VRMHELPER_expression_sub_material
):
    bl_idname = "vrm_helper.vrm1_expression_change_bind_material"
    bl_label = "Change Bind Material"
    bl_description = "Change the material of the active binding"
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
            bind
            for bind in active_expression.material_color_binds
            if bind.material == old_bind_material
        }
        target_transform_bind_binds = {
            bind
            for bind in active_expression.texture_transform_binds
            if bind.material == old_bind_material
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


"""---------------------------------------------------------
    Spring Bone
---------------------------------------------------------"""


# ----------------------------------------------------------
#    Collider
# ----------------------------------------------------------
class VRMHELPER_OT_collider_create_from_bone(VRMHELPER_collider_base):
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
        colliders = get_vrm_extension_property("COLLIDER")
        addon_collection_dict = setting_vrm_helper_collection()
        dest_collection = addon_collection_dict["VRM1_COLLIDER"]

        # 選択ボーン全てに対してコライダーを作成してパラメーターをセットする｡
        # Target Armature.dataの'use_mirror_x'が有効の場合は処理の間は無効化する｡
        is_changed_use_mirror = False
        if target_armature.data.use_mirror_x:
            target_armature.data.use_mirror_x = False
            is_changed_use_mirror = True

        # bones = context.selected_bones if context.selected_bones else context.selected_pose_bones
        bones = get_selected_bone(target_armature.data)
        for bone in bones:
            bone = get_pose_bone_by_name(bone.name)
            new_item = colliders.add()
            new_item.uuid = uuid.uuid4().hex

            # コライダーのタイプ､半径､位置を設定
            new_item.shape_type = self.collider_type
            new_item.node.bone_name = bone.name

            if self.collider_type == "Sphere":
                new_item.shape.sphere.radius = self.collider_radius
                collider_object = new_item.bpy_object
                link_object2collection(collider_object, dest_collection)

            if self.collider_type == "Capsule":
                # コライダーオブジェクトの作成･初期化｡
                new_item.reset_bpy_object(context, target_armature)
                new_item.shape.capsule.radius = self.collider_radius

                # コライダーオブジェクトの位置設定｡
                collider_head = new_item.bpy_object
                collider_tail = new_item.bpy_object.children[0]
                collider_head.matrix_world = generate_head_collider_position(bone.head)
                collider_head.rotation_euler = Vector((0, 0, 0))
                collider_tail.matrix_basis = generate_tail_collider_position(
                    bone, bone.tail
                )

                # コライダーオブジェクトを対象コレクションにリンクする｡
                link_object2collection(collider_head, dest_collection)
                link_object2collection(collider_tail, dest_collection)

        # 'use_mirror_x'の値を変更していた場合は元に戻す｡
        if is_changed_use_mirror:
            target_armature.data.use_mirror_x = True

        logger.debug(f"Processing Time : {time.perf_counter() - time_start:.3f} s")
        return {"FINISHED"}


class VRMHELPER_OT_collider_remove_from_empty(VRMHELPER_collider_base):
    bl_idname = "vrm_helper.vrm1_collider_remove_from_empty"
    bl_label = "Remove Collider"
    bl_description = "Remove spring bone collider from selected empty"

    @classmethod
    def poll(cls, context):
        # 選択オブジェクトにEmptyが含まれていなければ使用不可｡
        return is_including_empty_in_selected_object()

    def execute(self, context):
        # 処理中はプロパティのアップデートのコールバック関数をロックする｡
        index_prop = get_vrm1_index_root_prop()
        index_prop.is_locked_update = True

        for obj in [obj for obj in context.selected_objects if obj.type == "EMPTY"]:
            remove_vrm1_collider_by_selected_object(obj)

        # アクティブインデックスをオフセットしてエラーを回避する｡
        self.offset_active_item_index(self.component_type)
        self.offset_active_item_index("COLLIDER_GROUP")
        self.offset_active_item_index("SPRING")
        index_prop.is_locked_update = False

        return {"FINISHED"}


# ----------------------------------------------------------
#    Collider Group
# ----------------------------------------------------------
class VRMHELPER_OT_collider_group_add_group(VRMHELPER_collider_group_base):
    bl_idname = "vrmhelper.vrm1_collider_group_add_group"
    bl_label = "Add Collider Group"
    bl_description = "Add a new VRM1 Spring BoneCollider Group"

    def execute(self, context):
        new_group = get_vrm_extension_property("COLLIDER_GROUP").add()
        new_group.vrm_name = "New Collider Group"
        new_group.uuid = uuid.uuid4().hex

        return {"FINISHED"}


class VRMHELPER_OT_collider_group_remove_active_group(VRMHELPER_collider_group_base):
    bl_idname = "vrmhelper.vrm1_collider_group_remove_active_group"
    bl_label = "Remove Collider Group"
    bl_description = "Deletes the collider group that is active in the list."

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

        # 対象コライダーグループを参照していたスプリングの値を更新後に対象を削除する｡その後アクティブインデックスを
        remove_vrm1_spring_collider_group_when_removed_collider_group(
            collider_groups[active_indexes[0]].name
        )
        collider_groups.remove(active_indexes[0])
        self.offset_active_item_index(self.component_type)

        return {"FINISHED"}


class VRMHELPER_OT_collider_group_clear_group(VRMHELPER_collider_group_base):
    bl_idname = "vrmhelper.vrm1_collider_group_clear_group"
    bl_label = "Clear Collider Group"
    bl_description = "Clear all collider groups."

    @classmethod
    def poll(self, context):
        # Collider Groupが存在する｡
        return get_vrm_extension_property("COLLIDER_GROUP")

    def execute(self, context):
        os.system("cls")

        for collider_group in (
            collider_groups := get_vrm_extension_property("COLLIDER_GROUP")
        ):
            remove_vrm1_spring_collider_group_when_removed_collider_group(
                collider_group.name
            )

        collider_groups.clear()
        get_vrm1_index_root_prop().collider_group = 0
        self.offset_active_item_index("SPRING")

        return {"FINISHED"}


"""---------------------------------------------------------
    TODO : Move(Up, Down) Operator
---------------------------------------------------------"""


class VRMHELPER_OT_collider_group_add_collider(VRMHELPER_collider_group_base):
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


class VRMHELPER_OT_collider_group_remove_collider(VRMHELPER_collider_group_base):
    bl_idname = "vrmhelper.vrm1_collider_group_remove_collider"
    bl_label = "Remove Collider"
    bl_description = "Remove the active collider from group"

    @classmethod
    def poll(self, context):
        # アクティブアイテムがColliderである｡
        return (ai := get_active_list_item_in_collider_group()) and ai.item_type[2]

    def execute(self, context):
        active_indexes = get_active_list_item_in_collider_group().item_indexes
        get_vrm_extension_property("COLLIDER_GROUP")[
            active_indexes[0]
        ].colliders.remove(active_indexes[1])

        get_vrm1_index_root_prop().collider_group -= 1

        return {"FINISHED"}


class VRMHELPER_OT_collider_group_clear_collider(VRMHELPER_collider_group_base):
    bl_idname = "vrmhelper.vrm1_collider_group_clear_collider"
    bl_label = "Clear Collider"
    bl_description = "Remove all colliders linked to the active group"

    @classmethod
    def poll(self, context):
        # アクティブアイテムがCollider GroupかつそのグループにColliderが存在する｡
        return (
            (active_item := get_active_list_item_in_collider_group())
            and not (active_item.item_type[0])
            and get_vrm_extension_property("COLLIDER_GROUP")[
                active_item.item_indexes[0]
            ].colliders
        )

    def execute(self, context):
        os.system("cls")
        active_indexes = get_active_list_item_in_collider_group().item_indexes
        get_vrm_extension_property("COLLIDER_GROUP")[
            active_indexes[0]
        ].colliders.clear()

        self.offset_active_item_index(self.component_type)

        return {"FINISHED"}


class VRMHELPER_OT_collider_group_register_collider_from_bone(VRMHELPER_operator_base):
    bl_idname = "vrmhelper.vrm1_collider_group_register_collider_from_bone"
    bl_label = "Create From Bone"
    bl_description = "Registers the colliders linked to the selected bone to the active collider group"

    # TODO : Collider Groupが1つも存在しない場合は新たにグループを作成してそれを対象にする｡

    @classmethod
    def poll(cls, context):
        # Target Armatureのボーンが1つ以上選択されており､リストのアクティブアイテムがCollider Groupである｡
        return (
            is_existing_target_armature_and_mode()
            and (active_item := get_active_list_item_in_collider_group())
            and active_item.item_type[1]
        )

    def execute(self, context):
        # アクティブなコライダーグループを取得する｡
        active_group = get_active_list_item_in_collider_group()
        collider_group = get_vrm_extension_property("COLLIDER_GROUP")
        target_group_colliders = collider_group[active_group.item_indexes[0]].colliders
        existing_collider_names = [i.name for i in target_group_colliders]

        # 選択されたボーンの名前を'node.bone_name'とする全てのコライダーを取得する｡
        bone_names = [i.name for i in get_selected_bone(get_target_armature_data())]
        if context.mode == "EDIT_ARMATURE":
            bpy.ops.object.posemode_toggle()

        source_colliders = (
            i.name
            for i in get_vrm_extension_property("COLLIDER")
            if i.node.bone_name in bone_names and not i.name in existing_collider_names
        )

        # 取得したコライダーをアクティブなコライダーグループに登録する｡
        # 値が空のグループが存在する場合､そちらに値を代入する｡
        for collider_name in source_colliders:
            if empty_item := [i for i in target_group_colliders if not i.collider_name]:
                empty_item[0].collider_name = collider_name

            else:
                new_item = target_group_colliders.add()
                new_item.collider_name = collider_name

        return {"FINISHED"}


# ----------------------------------------------------------
#    Spring
# ----------------------------------------------------------
class VRMHELPER_OT_spring_add_spring(VRMHELPER_spring_base):
    bl_idname = "vrmhelper.vrm1_spring_add_spring"
    bl_label = "Add Spring"
    bl_description = "Add a new VRM1 Spring"

    def execute(self, context):
        new_spring = get_vrm_extension_property("SPRING").add()
        new_spring.vrm_name = "New Spring"

        return {"FINISHED"}


class VRMHELPER_OT_spring_remove_spring(VRMHELPER_spring_base):
    bl_idname = "vrmhelper.vrm1_spring_remove_spring"
    bl_label = "Add Spring"
    bl_description = "Remove active spring from spring"

    @classmethod
    def poll(self, context):
        return (active_item := get_active_list_item_in_spring()) and active_item.name

    def execute(self, context):
        # アクティブアイテムのインデックスを取得する｡
        active_item = get_active_list_item_in_spring()
        active_indexes = active_item.item_indexes

        spring = get_vrm_extension_property("SPRING")

        spring.remove(active_indexes[0])
        self.offset_active_item_index(self.component_type)

        return {"FINISHED"}


class VRMHELPER_OT_spring_clear_spring(VRMHELPER_spring_base):
    bl_idname = "vrmhelper.vrm1_spring_clear_spring"
    bl_label = "Clear Spring"
    bl_description = "Remove all springs from spring"

    def execute(self, context):
        get_vrm_extension_property("SPRING").clear()
        get_vrm1_index_root_prop().spring = 0

        return {"FINISHED"}


# -----------------------------------------------------


class VRMHELPER_OT_spring_add_joint(
    VRMHELPER_spring_base, VRMHELPER_VRM1_joint_property
):
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
            two_previous_bone = target_armature.bones.get(
                two_previous_joint.node.bone_name
            )
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


class VRMHELPER_OT_spring_remove_joint(VRMHELPER_spring_base):
    bl_idname = "vrmhelper.vrm1_spring_remove_joint"
    bl_label = "Remove Joint"
    bl_description = "Remove active joint from spring"

    @classmethod
    def poll(self, context):
        # アクティブアイテムがジョイントである
        return (
            active_item := get_active_list_item_in_spring()
        ) and active_item.item_type[2]

    def execute(self, context):
        active_indexes = get_active_list_item_in_spring().item_indexes
        get_vrm_extension_property("SPRING")[active_indexes[0]].joints.remove(
            active_indexes[1]
        )
        get_vrm1_index_root_prop().spring -= 1

        return {"FINISHED"}


class VRMHELPER_OT_spring_clear_joint(VRMHELPER_spring_base):
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


class VRMHELPER_OT_spring_add_joint_from_source(
    VRMHELPER_spring_base, VRMHELPER_VRM1_joint_property
):
    bl_idname = "vrmhelper.vrm1_spring_create_joint_from_selected"
    bl_label = "Create Joint"
    bl_description = "Create spring joints from selected bones"

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
    # -----------------------------------------------------

    def invoke(self, context, event):
        if self.source_type == "SELECT":
            add_list_item2collider_group_list4operator()
            return context.window_manager.invoke_props_dialog(self, width=360)

        add_list_item2bone_group_list4operator()
        add_list_item2collider_group_list4operator()
        return context.window_manager.invoke_props_dialog(self, width=360)

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        collider_group_collection = get_ui_vrm1_collider_group_prop()

        # 処理対象のボーングループを選択するエリア｡
        if self.source_type == "BONE_GROUP":
            bone_group_collection = get_ui_vrm1_operator_bone_group_prop()
            anchor_layout = row.column(align=True)
            box_sub = anchor_layout.box()
            box_sub.label(text="Target Bone Group")
            for group in bone_group_collection:
                row_sub = box_sub.row(align=True)
                row_sub.prop(group, "is_target", text=group.name)

        # 処理対象のコライダーグループを選択するエリア｡
        anchor_layout = row.column(align=True)
        if self.source_type == "BONE_GROUP":
            anchor_layout = anchor_layout.box()
        anchor_layout.label(text="Target Bone Group")
        for group in collider_group_collection:
            row_sub = anchor_layout.row(align=True)
            row_sub.prop(group, "is_target", text=group.vrm_name)

    def execute(self, context):
        os.system("cls")

        # # 処理対象となるボーンを､枝毎にグルーピングされた状態で取得する｡
        if not (
            target_bones := get_bones_for_each_branch_by_type(
                self.source_type, get_target_armature()
            )
        ):
            return {"CANCELLED"}

        springs = get_vrm_extension_property("SPRING")
        spring_and_joint_dicts = [
            {spring: [joint for joint in spring.joints]} for spring in springs
        ]

        # 取得したボーンのリストから枝毎にスプリングを作成し､そのスプリングに対してジョイントを登録する｡
        for branch in target_bones:
            damping = 1.0

            # 枝に含まれているボーンがいずれかのスプリングに登録されている場合はそのスプリングのジョインツに追記する｡
            target_joints = None
            for dict in spring_and_joint_dicts:
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
                if group.name in [
                    i.collider_group_name for i in target_collider_groups
                ]:
                    logger.debug(f"Already Registered : {group.vrm_name}")
                    continue
                target_group = target_collider_groups.add()
                target_group.collider_group_name = group.name

        return {"FINISHED"}


class VRMHELPER_OT_spring_assign_parameters_to_selected_joints(
    VRMHELPER_spring_base, VRMHELPER_VRM1_joint_property
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
    # -----------------------------------------------------

    def invoke(self, context, event):
        os.system("cls")

        add_list_item2joint_list4operator()
        if self.source_type == "MULTIPLE":
            return context.window_manager.invoke_props_dialog(self)

        # 'source_type'が'SINGLE'の場合はアクティブなスプリングのみをターゲットに設定する｡
        active_indexes = get_active_list_item_in_spring().item_indexes
        for spring in get_ui_vrm1_operator_spring_prop():
            if spring.spring_index != active_indexes[0]:
                spring.is_target = False

        return self.execute(context)

    def draw(self, context):
        spring_collection = get_ui_vrm1_operator_spring_prop()
        layout = self.layout
        box = layout.box()
        box.label(text="Target Spring")
        box.separator(factor=0.1)
        for spring in spring_collection:
            row = box.row(align=True)
            row.prop(spring, "is_target", text=spring.name)

    def execute(self, context):
        springs = get_vrm_extension_property("SPRING")
        springs_filter_list = get_ui_vrm1_operator_spring_prop()

        # ターゲットに設定されたスプリング毎に､登録されたジョイントに減衰率を加味しつつ値を適用する｡
        for spring, filter in zip(springs, springs_filter_list):
            if not filter.is_target:
                logger.debug(f"Skip : {spring.vrm_name}")
                continue

            damping = 1.0
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


# -----------------------------------------------------


class VRMHELPER_OT_spring_add_collider_group(VRMHELPER_spring_base):
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
        collider_groups = get_vrm_extension_property("SPRING")[
            active_indexes[0]
        ].collider_groups
        collider_groups.add()

        return {"FINISHED"}


class VRMHELPER_OT_spring_remove_collider_group(VRMHELPER_spring_base):
    bl_idname = "vrmhelper.vrm1_spring_remove_collider_group"
    bl_label = "Remove Collider Group"
    bl_description = "Remove active collider group from spring"

    @classmethod
    def poll(self, context):
        # アクティブアイテムがコライダーグループである｡
        return (
            active_item := get_active_list_item_in_spring()
        ) and active_item.item_type[3]

    def execute(self, context):
        active_indexes = get_active_list_item_in_spring().item_indexes
        get_vrm_extension_property("SPRING")[active_indexes[0]].collider_groups.remove(
            active_indexes[2]
        )
        get_vrm1_index_root_prop().spring -= 1

        return {"FINISHED"}


class VRMHELPER_OT_spring_clear_collider_group(VRMHELPER_spring_base):
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


class VRMHELPER_OT_constraint_add_vrm_constraint(VRMHELPER_constraint_base):
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

        logger.debug(
            f"\n{'':#>100}\n{type(constrainted_element)} & {type(target_element)}"
        )
        logger.debug(f"Constrainted : {constrainted_element.name}")
        logger.debug(f"Traget : {target_element.name}\n{'':#>100}\n")

        # 'constraint_type'に対応するコンストレイントを作成する｡
        constraint_type = self.constraint_type_dict[self.constraint_type]
        constraint_name = self.constraint_name_dict[self.constraint_type]

        constraints = constrainted_element.constraints
        # 既にVRMコンストレイントが存在する場合は削除する｡
        remove_existing_vrm_constraint(constraints)

        new_constraint: CopyRotationConstraint | DampedTrackConstraint = (
            constraints.new(constraint_type)
        )
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
        add_items2constraint_ui_list(current_ui_constraint_type)
        constraint_collection = get_ui_vrm1_constraint_prop()
        target_constraint_index = None

        for n, props in enumerate(constraint_collection):
            if props.constraint_name == new_constraint.name:
                target_constraint_index = n
                break

        if target_constraint_index:
            index_root_prop = get_vrm1_index_root_prop()
            index_root_prop.constraint = target_constraint_index

        return {"FINISHED"}


class VRMHELPER_OT_constraint_remove_vrm_constraint(VRMHELPER_constraint_base):
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
    VRMHELPER_OT_vrm1_expression_set_material_bind_from_scene,
    VRMHELPER_OT_vrm1_expression_store_mtoon1_parameters,
    VRMHELPER_OT_vrm1_expression_restore_mtoon1_parameters,
    VRMHELPER_OT_vrm1_expression_discard_stored_mtoon1_parameters,
    VRMHELPER_OT_vrm1_expression_assign_expression_to_scene,
    VRMHELPER_OT_vrm1_expression_change_bind_material,
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
