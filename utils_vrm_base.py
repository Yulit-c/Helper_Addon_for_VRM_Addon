if "bpy" in locals():
    import importlib

    reloadable_modules = [
        "Logging.preparation_logger",
    ]

    for module in reloadable_modules:
        if module in locals():
            importlib.reload(locals()[module])
            print(f"reloaded {module}")

else:
    from .Logging import preparation_logger

import re

from operator import (
    attrgetter,
)
from pprint import (
    pprint,
)
from typing import (
    Literal,
    Optional,
    Any,
)
import bpy
from bpy.types import (
    Object,
    Bone,
    Material,
    PropertyGroup,
    bpy_prop_array,
    CopyRotationConstraint,
    DampedTrackConstraint,
)


from .addon_classes import (
    ReferenceVrm0FirstPersonPropertyGroup,
    ReferenceVrm0BlendShapeMasterPropertyGroup,
    ReferenceVrm0BlendShapeGroupPropertyGroup,
    ReferenceVrm0SecondaryAnimationPropertyGroup,
    ReferenceVrm0SecondaryAnimationColliderGroupPropertyGroup,
    ReferenceVrm0SecondaryAnimationPropertyGroup,
    # ----------------------------------------------------------
    MToonMaterialParameters,
    ReferenceVrm1FirstPersonPropertyGroup,
    ReferenceVrm1ExpressionPropertyGroup,
    ReferenceVrm1MaterialColorBindPropertyGroup,
    ReferenceVrm1ExpressionsPropertyGroup,
    ReferenceVrm1ColliderPropertyGroup,
    ReferenceVrm1ColliderGroupPropertyGroup,
    ReferenceSpringBone1SpringPropertyGroup,
    ReferenceVrm0PropertyGroup,
    ReferenceVrm1PropertyGroup,
    ReferenceSpringBone1SpringBonePropertyGroup,
    ReferenceNodeConstraint1NodeConstraintPropertyGroup,
    ReferenceVrmAddonArmatureExtensionPropertyGroup,
)

from .addon_constants import (
    MTOON0_ATTRIBUTE_NAMES,
    MTOON1_ATTRIBUTE_NAMES,
    MTOON0_DEFAULT_VALUES,
    MTOON1_DEFAULT_VALUES,
)


from .preferences import get_addon_preferences


from .property_groups import (
    VRMHELPER_SCENE_vrm0_mtoon0_stored_parameters,
    VRMHELPER_SCENE_vrm1_ui_list_active_indexes,
    VRMHELPER_SCENE_vrm1_mtoon1_stored_parameters,
    VRMHELPER_WM_operator_spring_bone_group_list_items,
    get_scene_basic_prop,
    get_target_armature,
    get_target_armature_data,
    get_ui_bone_group_prop,
    get_scene_vrm0_mtoon_stored_prop,
    get_scene_vrm1_mtoon_stored_prop,
)

from .utils_common import (
    get_attr_from_strings,
    set_attr_from_strings,
    get_selected_bone,
    get_branch_root_bone,
    get_bones_for_each_branch_from_source_bones,
    unlink_object_from_all_collections,
    setting_vrm_helper_collection,
    get_addon_collection_name,
    reset_shape_keys_value,
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


def evaluation_expression_morph_collection() -> bool:
    """
    # 1つ以上のオブジェクトがリンクされた'VRM0 BlendShape ','VRM1 Expression Morph'のコレクションが
    # 存在するか否かを判定する｡

    Returns
    -------
    bool
        条件を満たしていればTrue､そうでなければFalseを返す｡
    """

    addon_mode = check_addon_mode()

    match addon_mode:
        case "0":
            source_collection_name = get_addon_collection_name("VRM0_BLENDSHAPE_MORPH")
        case "1":
            source_collection_name = get_addon_collection_name("VRM1_EXPRESSION_MORPH")
        case "2":
            return False

    if collection_mat := bpy.data.collections.get(source_collection_name):
        if collection_mat.all_objects:
            return True

    return False


def evaluation_expression_material_collection() -> bool:
    """
    # 1つ以上のオブジェクトがリンクされた'VRM1 Expression Material'のコレクションが
    # 存在するか否かを判定する｡

    Returns
    -------
    bool
        条件を満たしていればTrue､そうでなければFalseを返す｡
    """

    addon_mode = check_addon_mode()

    match addon_mode:
        case "0":
            source_collection_name = get_addon_collection_name("VRM0_BLENDSHAPE_MATERIAL")
        case "1":
            source_collection_name = get_addon_collection_name("VRM1_EXPRESSION_MATERIAL")
        case "2":
            return False

    if collection_mat := bpy.data.collections.get(source_collection_name):
        if collection_mat.all_objects:
            return True

    return False


def set_new_value2index_prop(
    index_root_prop: VRMHELPER_SCENE_vrm1_ui_list_active_indexes,
    attr_name: str,
):
    new_value = getattr(index_root_prop, attr_name) - 1
    setattr(index_root_prop, attr_name, new_value)


def get_bones_from_bone_groups(target_armature: Object) -> list[Bone]:
    """
    指定したBone GroupまたはBone Collectionに属するボーンを'target_armature'から取得する｡

    Parameters
    ----------
    target_armature : Object
        処理対象となるArmature Object

    Returns
    -------
    list[Bone]
        取得したボーンを格納したリスト｡

    """

    bone_group_collection = get_ui_bone_group_prop()

    bl_ver = bpy.app.version
    if bl_ver < (4, 0, 0):
        target_group_index_list = [i.group_index for i in bone_group_collection if i.is_target]
        target_bone_list = [
            bone
            for (bone, pose_bone) in zip(target_armature.data.bones, target_armature.pose.bones)
            if pose_bone.bone_group and pose_bone.bone_group_index in target_group_index_list
        ]

    elif bl_ver >= (4, 0, 0):
        target_coll_name_list = [i.name for i in bone_group_collection if i.is_target]
        target_bone_list = [
            bone
            for coll in target_armature.data.collections
            for bone in coll.bones
            if coll.name in target_coll_name_list
        ]

    return target_bone_list


def get_branch_root_bones_by_type(
    source_type: Literal["SELECT", "MULTIPLE"],
    target_armature: Object,
) -> list[Bone]:
    """
    'source_type'に応じて選択ボーンまたはBone Group(Bone Collection)内の房のルートボーンを取得する

    Parameters
    ----------
    source_type : Literal["SELECT", "MULTIPLE"]
        ボーン取得元となるデータ

    target_armature : Object
        処理対象のArmature Object

    Returns
    -------
    list[Bone]
        取得された房ルートボーンのリスト

    """

    target_armature = get_target_armature()
    match source_type:
        case "SELECT":
            source_bones = get_selected_bone()
        case "MULTIPLE":
            source_bones = get_bones_from_bone_groups(target_armature)

    branch_root_bones = list({get_branch_root_bone(i) for i in source_bones})
    sort_order = [i.name for i in target_armature.data.bones if i in branch_root_bones]
    branch_root_bones.sort(key=lambda x: sort_order.index(x.name))

    return branch_root_bones


def get_bones_for_each_branch_by_type(
    source_type: Literal["SELECT", "MULTIPLE"],
    target_armature: Object,
) -> list[Bone]:
    """
    'source_type'で指定したソースから枝毎にグルーピングされたボーンを取得する｡

    Parameters
    ----------
    source_type : Literal["SELECT", "MULTIPLE"]
        ボーンを取得する対象を指定する｡

    target_armature : _type_
        ボーンの取得基となるArmature Object｡

    Returns
    -------
    list[Bone]
        取得されたボーンを枝毎に格納したリスト全てを格納したリスト｡

    """

    target_armature = get_target_armature()
    if source_type == "SELECT":
        source_bones = get_selected_bone()

    if source_type == "MULTIPLE":
        source_bones = get_bones_from_bone_groups(target_armature)

    return get_bones_for_each_branch_from_source_bones(target_armature, source_bones)


def is_existing_target_armature() -> bool:
    """
    Target Armatureが選択されているかどうかを判定する｡

    Returns
    -------
    bool
        Target Armatureが選択されていればTrueを返す｡選択されていなければFalseを返す｡

    """

    if get_target_armature_data():
        return True
    else:
        return False


def check_addon_mode() -> str:
    """
    アドオンのProperty Group中のUI Modeの値を返す｡

    Returns
    -------
    str
        "0" : vrm ver 0.x
        "1" : vrm ver 1.x
        "2" : Misc Tools

    """
    basic_prop = get_scene_basic_prop()

    return basic_prop.tool_mode


def get_vrm_extension_all_root_property() -> Optional[ReferenceVrmAddonArmatureExtensionPropertyGroup]:
    """
    Target Armatureに登録されているVRM Addonの全体のルートプロパティを取得する｡

    Returns
    -------
    Optional[ReferenceVrmAddonArmatureExtensionPropertyGroup]
        Armatureに登録されたVRM Addonプロパティの最上階層｡
        Target Armatureが指定されていなければNone

    """
    if not (target_armature := get_target_armature_data()):
        return

    return target_armature.vrm_addon_extension


def get_vrm_extension_root_property(
    target: Literal["VRM", "SECONDARY", "SPRING1", "CONSTRAINT"],
) -> (
    ReferenceVrm0PropertyGroup
    | ReferenceVrm1PropertyGroup
    | ReferenceVrm0SecondaryAnimationPropertyGroup
    | ReferenceSpringBone1SpringBonePropertyGroup
):
    """
    選択されているUI Modeに対応したバージョンのVRM Extensionのルートプロパティを取得する｡

    Parameters
    ----------
    target: Literal["VRM", "SECONDARY", "SPRING1", "CONSTRAINT"]
        取得したいプロパティグループの種類を指定する｡

    Returns
    -------
    bpy.types.bpy_prop_collection
        選択されているUI Modeに応じてVRM ExtensionのProperty Groupのルートを取得する｡

    """
    if not (vrm_extension := get_vrm_extension_all_root_property()):
        return

    match target:
        case "VRM":
            match check_addon_mode():
                case "0":
                    vrm_property = vrm_extension.vrm0

                case "1":
                    vrm_property = vrm_extension.vrm1

        case "SECONDARY":
            vrm_property = vrm_extension.vrm0.secondary_animation

        case "SPRING1":
            vrm_property = vrm_extension.spring_bone1

    return vrm_property


"""---------------------------------------------------------
    Cnndidaete Replacing Get Extension Property
---------------------------------------------------------"""


# ----------------------------------------------------------
#    VRM0
# ----------------------------------------------------------
def get_vrm0_extension_root_property() -> ReferenceVrm0PropertyGroup:
    vrm_all_root = get_vrm_extension_all_root_property()
    vrm0_root = vrm_all_root.vrm0
    return vrm0_root


def get_vrm0_extension_first_person() -> ReferenceVrm0FirstPersonPropertyGroup:
    vrm0_extension = get_vrm0_extension_root_property()
    vrm0_first_person = vrm0_extension.first_person
    return vrm0_first_person


def get_vrm0_extension_blend_shape() -> ReferenceVrm0BlendShapeMasterPropertyGroup:
    vrm0_extension = get_vrm0_extension_root_property()
    vrm0_blend_shapes = vrm0_extension.blend_shape_master
    return vrm0_blend_shapes


def get_vrm0_extension_active_blend_shape_group() -> ReferenceVrm0BlendShapeGroupPropertyGroup:
    vrm0_blend_shape_master = get_vrm0_extension_blend_shape()
    active_blend_shape = vrm0_blend_shape_master.blend_shape_groups[
        vrm0_blend_shape_master.active_blend_shape_group_index
    ]
    return active_blend_shape


def get_vrm0_extension_secondary_animation() -> ReferenceVrm0SecondaryAnimationPropertyGroup:
    vrm0_extension = get_vrm0_extension_root_property()
    vrm_secondary = vrm0_extension.secondary_animation

    return vrm_secondary


def get_vrm0_extension_collider_group() -> (
    bpy.types.bpy_prop_collection
):  # ReferenceVrm0SecondaryAnimationColliderGroupPropertyGroup
    vrm_secondary = get_vrm0_extension_secondary_animation()
    vrm0_collider_group = vrm_secondary.collider_groups
    return vrm0_collider_group


def get_vrm0_extension_spring_bone_group() -> bpy.types.bpy_prop_collection:
    """ReferenceVrm0SecondaryAnimationGroupPropertyGroup"""
    vrm_secondary = get_vrm0_extension_secondary_animation()
    vrm0_bone_groups = vrm_secondary.bone_groups
    return vrm0_bone_groups


# ----------------------------------------------------------
#    VRM1
# ----------------------------------------------------------
def get_vrm1_extension_root_property() -> ReferenceVrm1PropertyGroup:
    vrm_all_root = get_vrm_extension_all_root_property()
    vrm1_root = vrm_all_root.vrm1
    return vrm1_root


def get_vrm1_extension_property_expression() -> ReferenceVrm1ExpressionsPropertyGroup:
    vrm1_extension = get_vrm1_extension_root_property()
    vrm1_expressions = vrm1_extension.expressions
    return vrm1_expressions


def get_vrm1_extension_collider() -> ReferenceVrm1ColliderPropertyGroup:
    vrm_springs = get_vrm_extension_all_root_property().spring_bone1
    collider_prop = vrm_springs.colliders
    return collider_prop


def get_vrm1_extension_collider_group() -> ReferenceVrm1ColliderGroupPropertyGroup:
    vrm_springs = get_vrm_extension_all_root_property().spring_bone1
    cg_prop = vrm_springs.collider_groups
    return cg_prop


def get_vrm1_extension_spring() -> ReferenceSpringBone1SpringPropertyGroup:
    vrm_springs = get_vrm_extension_all_root_property().spring_bone1
    spring_prop = vrm_springs.springs
    return spring_prop


"""-------------------------------------------------------"""


def get_vrm_extension_property(
    type: Literal[
        "FIRST_PERSON",
        "BLEND_SHAPE",
        "EXPRESSION",
        "COLLIDER",
        "COLLIDER_GROUP",
        "SPRING",
    ]
) -> bpy.types.bpy_prop_collection:
    """
    Target ArmatureのVRM Extensionの中から引数で指定したProperty Groupを取得する｡

    Parameters
    ----------
    type : type: Literal[
        "FIRST_PERSON",
        "BLEND_SHAPE",
        "EXPRESSION",
        "COLLIDER",
        'COLLIDER_GROUP'
        'SPRING'

    ]

    Returns
    -------
    bpy.types.bpy_prop_collection
        VRM Addon定義のPropertyGroupのうち､引数で指定したもの

    """

    vrm_extension = get_vrm_extension_root_property("VRM")
    match check_addon_mode():
        case "0":
            vrm_secondary = get_vrm_extension_root_property("SECONDARY")
            match type:
                case "FIRST_PERSON":
                    return vrm_extension.first_person

                case "BLEND_SHAPE":
                    return vrm_extension.blend_shape_master

                case "COLLIDER_GROUP":
                    return vrm_secondary.collider_groups

                case "SPRING":
                    return vrm_secondary.bone_groups

        case "1":
            vrm_springs = get_vrm_extension_root_property("SPRING1")

            match type:
                case "FIRST_PERSON":
                    return vrm_extension.first_person

                case "EXPRESSION":
                    return vrm_extension.expressions

                case "COLLIDER":
                    return vrm_springs.colliders

                case "COLLIDER_GROUP":
                    return vrm_springs.collider_groups

                case "SPRING":
                    return vrm_springs.springs


def is_existing_target_armature_and_mode() -> bool:
    """
    2つの条件を満たしているか否かを判定する｡
    - アクティブオブジェクトがTarget Armatureである｡
    - Edit BoneかPose Boneが1つ以上選択されている｡

    Returns
    -------
    bool
        2つの条件を満たしている場合はTrue､それ以外はFalseが返る｡
    """

    context = bpy.context
    target_armature = get_scene_basic_prop().target_armature.data
    # アクティブオブジェクトのオブジェクトデータがTarget Armatureである｡
    if (context.active_object) and (not context.active_object.data == target_armature):
        return False

    # 1つ以上のボーンが選択状態である｡
    if not (context.selected_bones or context.selected_pose_bones):
        return False

    return True


def reset_shape_keys_value_in_morph_binds(source_morph_binds: Any):
    """
    'source_morph_binds'内に登録されているオブジェクトに存在する全てのシェイプキーの値を0にセットする｡

    Parameters
    ----------
    source_morph_binds : Any
        処理対象のMorph Target Binds

    """

    addon_mode = check_addon_mode()

    match addon_mode:
        case "0":
            bind_object_names = {bind.mesh.mesh_object_name for bind in source_morph_binds}
        case "1":
            bind_object_names = {bind.node.mesh_object_name for bind in source_morph_binds}

    for object_name in bind_object_names:
        if target_object := bpy.data.objects.get(object_name):
            reset_shape_keys_value(target_object.data)


def get_mtoon_attr_name_from_property_type(
    property_type: Literal[
        "_Color",
        "_ShadeColor",
        "_RimColor",
        "_EmissionColor",
        "_OutlineColor",
        "color",
        "shadeColor",
        "emissionColor",
        "matcapColor",
        "rimColor",
        "outlineColor",
    ],
) -> Optional[str]:
    """
    引数'property_type'に対応したMToo1属性名を返す｡

    Parameters
    ----------
    property_type: Literal[
        "_Color",
        "_ShadeColor",
        "_RimColor",
        "_EmissionColor",
        "_OutlineColor",
        "color",
        "shadeColor",
        "emissionColor",
        "matcapColor",
        "rimColor",
        "outlineColor",
    ]
        取得する値を定義するための文字列｡

    Returns
    -------
    Optional[str]:
        取得された属性名｡

    """

    mtoon_attr_name = None
    match property_type:
        case "_Color":
            mtoon_attr_name = MTOON0_ATTRIBUTE_NAMES["color"]
        case "_ShadeColor":
            mtoon_attr_name = MTOON0_ATTRIBUTE_NAMES["shade_color"]
        case "_RimColor":
            mtoon_attr_name = MTOON0_ATTRIBUTE_NAMES["rim_color"]
        case "_EmissionColor":
            mtoon_attr_name = MTOON0_ATTRIBUTE_NAMES["emission_color"]
        case "_OutlineColor":
            mtoon_attr_name = MTOON0_ATTRIBUTE_NAMES["outline_color"]
        # ---------------------------------------------------------------------------------
        case "color" | "lit_color":
            mtoon_attr_name = MTOON1_ATTRIBUTE_NAMES["lit_color"]

        case "shadeColor" | "shade_color":
            mtoon_attr_name = MTOON1_ATTRIBUTE_NAMES["shade_color"]

        case "emissionColor" | "emission_color":
            mtoon_attr_name = MTOON1_ATTRIBUTE_NAMES["emission_color"]

        case "matcapColor" | "matcap_color":
            mtoon_attr_name = MTOON1_ATTRIBUTE_NAMES["matcap_color"]

        case "rimColor" | "rim_color":
            mtoon_attr_name = MTOON1_ATTRIBUTE_NAMES["rim_color"]

        case "outlineColor" | "outline_color":
            mtoon_attr_name = MTOON1_ATTRIBUTE_NAMES["outline_color"]

    return mtoon_attr_name


def store_mtoon_current_values(
    target_item: VRMHELPER_SCENE_vrm0_mtoon0_stored_parameters
    | VRMHELPER_SCENE_vrm1_mtoon1_stored_parameters,
    source_material: Material,
):
    """
    Scene階層下にあるMToonのパラメーター保存用コレクションプロパティに登録されたアイテムに
    "source_material"が持つMToon1パラメーターを保存して復元できるようにする｡｡

    Parameters
    ----------
    target_item : VRMHELPER_SCENE_vrm1_mtoon1_stored_parameters|VRMHELPER_SCENE_vrm0_mtoon0_stored_parameters,
        処理対象となるコレクションプロパティのアイテム

    source_material : Material
        値が保存されるマテリアル｡

    """
    stored_parameter_names = list(target_item.__annotations__.keys())
    stored_parameter_names.remove("material")
    target_item.material = source_material
    mtoon = source_material.vrm_addon_extension.mtoon1
    current_mode = check_addon_mode()

    for name in stored_parameter_names:
        match current_mode:
            case "0":
                mtoon0_attr_name = MTOON0_ATTRIBUTE_NAMES[name]
                value = attrgetter(mtoon0_attr_name)(mtoon)

            case "1":
                mtoon1_attr_name = MTOON1_ATTRIBUTE_NAMES[name]
                value = attrgetter(mtoon1_attr_name)(mtoon)
                # value = [abs(i) for i in value]

        setattr(target_item, name, value)


def get_mtoon0_default_values(
    source_material: Material,
) -> MToonMaterialParameters:
    """
    'source_material'の保存済みMToon0デフォルト値を取得する｡保存データが存在しない場合は
    MToonマテリアルが定義したデフォルト値を取得して辞書として返す｡

    Parameters
    ----------
    source_material : Material
        処理対象のマテリアル

    Returns
    -------
    MToonMaterialParameters
        取得したパラメーターとパラメーター名のペアを格納した辞書｡

    """

    stored_mtoon_parameters = None
    if stored_mtoon1_parameters_list := [
        i for i in get_scene_vrm0_mtoon_stored_prop() if i.material == source_material
    ]:
        stored_mtoon_parameters: VRMHELPER_SCENE_vrm0_mtoon0_stored_parameters = (
            stored_mtoon1_parameters_list[0]
        )

    if stored_mtoon_parameters:
        default_texture_scale = stored_mtoon_parameters.texture_scale
        default_texture_offset = stored_mtoon_parameters.texture_offset
        default_color_factor = stored_mtoon_parameters.color
        default_shade_factor = stored_mtoon_parameters.shade_color
        default_emissive_factor = stored_mtoon_parameters.emission_color
        default_rim_factor = stored_mtoon_parameters.rim_color
        default_outline_factor = stored_mtoon_parameters.outline_color

    else:
        default_texture_scale = MTOON0_DEFAULT_VALUES["texture_scale"]
        default_texture_offset = MTOON0_DEFAULT_VALUES["texture_offset"]
        default_color_factor = MTOON0_DEFAULT_VALUES["color"]
        default_shade_factor = MTOON0_DEFAULT_VALUES["shade_color"]
        default_emissive_factor = MTOON0_DEFAULT_VALUES["emission_color"]
        default_rim_factor = MTOON0_DEFAULT_VALUES["rim_color"]
        default_outline_factor = MTOON0_DEFAULT_VALUES["outline_color"]

    obtained_default_parameters: MToonMaterialParameters = {
        "texture_scale": list(default_texture_scale),
        "texture_offset": list(default_texture_offset),
        "color": list(default_color_factor),
        "shade_color": list(default_shade_factor),
        "emission_color": list(default_emissive_factor),
        "rim_color": list(default_rim_factor),
        "outline_color": list(default_outline_factor),
    }

    return obtained_default_parameters


def get_mtoon1_default_values(
    source_material: Material,
) -> MToonMaterialParameters:
    """
    'source_material'の保存済みMToon1デフォルト値を取得する｡保存データが存在しない場合は
    MToonマテリアルが定義したデフォルト値を取得して辞書として返す｡

    Parameters
    ----------
    source_material : Material
        処理対象のマテリアル

    Returns
    -------
    MToonMaterialParameters
        取得したパラメーターとパラメーター名のペアを格納した辞書｡

    """

    stored_mtoon_parameters = None
    if stored_mtoon1_parameters_list := [
        i for i in get_scene_vrm1_mtoon_stored_prop() if i.material == source_material
    ]:
        stored_mtoon_parameters: VRMHELPER_SCENE_vrm1_mtoon1_stored_parameters = (
            stored_mtoon1_parameters_list[0]
        )

    if stored_mtoon_parameters:
        default_texture_scale = stored_mtoon_parameters.texture_scale
        default_texture_offset = stored_mtoon_parameters.texture_offset
        default_lit_factor = stored_mtoon_parameters.lit_color
        default_shade_factor = stored_mtoon_parameters.shade_color
        default_emissive_factor = stored_mtoon_parameters.emission_color
        default_matcap_factor = stored_mtoon_parameters.matcap_color
        default_rim_factor = stored_mtoon_parameters.rim_color
        default_outline_factor = stored_mtoon_parameters.outline_color

    else:
        default_texture_scale = MTOON1_DEFAULT_VALUES["texture_scale"]
        default_texture_offset = MTOON1_DEFAULT_VALUES["texture_offset"]
        default_lit_factor = MTOON1_DEFAULT_VALUES["lit_color"]
        default_shade_factor = MTOON1_DEFAULT_VALUES["shade_color"]
        default_emissive_factor = MTOON1_DEFAULT_VALUES["emission_color"]
        default_matcap_factor = MTOON1_DEFAULT_VALUES["matcap_color"]
        default_rim_factor = MTOON1_DEFAULT_VALUES["rim_color"]
        default_outline_factor = MTOON1_DEFAULT_VALUES["outline_color"]

    obtained_default_parameters: MToonMaterialParameters = {
        "texture_scale": list(default_texture_scale),
        "texture_offset": list(default_texture_offset),
        "lit_color": list(default_lit_factor),
        "shade_color": list(default_shade_factor),
        "emission_color": list(default_emissive_factor),
        "matcap_color": list(default_matcap_factor),
        "rim_color": list(default_rim_factor),
        "outline_color": list(default_outline_factor),
    }

    return obtained_default_parameters


def get_mtoon_color_current_parameters(
    source_material: Material,
) -> MToonMaterialParameters:
    """
    'source_material'の現在のMToonパラメーターからMaterial Colorの値を取得して辞書として返す｡
    保存済みのパラメーターと比較して変化がない場合は保存済みのパラメーターを返す｡

    Parameters
    ----------
    source_material : Material
        処理対象のマテリアル

    Returns
    -------
    MToonMaterialParameters
        取得したパラメーターとパラメーター名のペアを格納した辞書｡

    """

    mtoon1 = source_material.vrm_addon_extension.mtoon1
    match check_addon_mode():
        case "0":
            # 保存済みのMToo1パラメーターが存在すれば取得する｡
            mtoon0_default_value_dict = get_mtoon0_default_values(source_material)

            # 各パラメーターの現在の値(FloatVector)をリストとして取得する｡
            mtoon0_current_color_factor = list(get_attr_from_strings(mtoon1, MTOON0_ATTRIBUTE_NAMES["color"]))
            mtoon0_current_shade_factor = list(
                get_attr_from_strings(mtoon1, MTOON1_ATTRIBUTE_NAMES["shade_color"])
            )
            mtoon0_current_emissive_factor = list(
                get_attr_from_strings(mtoon1, MTOON1_ATTRIBUTE_NAMES["emission_color"])
            )
            mtoon0_current_rim_factor = list(
                get_attr_from_strings(mtoon1, MTOON1_ATTRIBUTE_NAMES["rim_color"])
            )
            mtoon0_current_outline_factor = list(
                get_attr_from_strings(mtoon1, MTOON1_ATTRIBUTE_NAMES["outline_color"])
            )

            # デフォルト値と現在の値を比較して変化している場合はその値を取得する｡
            mtoon0_color_factor = (
                mtoon0_current_color_factor
                if mtoon0_current_color_factor != mtoon0_default_value_dict["color"]
                else None
            )
            mtoon0_shade_color_factor = (
                mtoon0_current_shade_factor
                if mtoon0_current_shade_factor != mtoon0_default_value_dict["shade_color"]
                else None
            )
            mtoon0_emissive_color_factor = (
                mtoon0_current_emissive_factor
                if mtoon0_current_emissive_factor != mtoon0_default_value_dict["emission_color"]
                else None
            )
            mtoon0_rim_color_factor = (
                mtoon0_current_rim_factor
                if mtoon0_current_rim_factor != mtoon0_default_value_dict["rim_color"]
                else None
            )
            mtoon0_outline_color_factor = (
                mtoon0_current_outline_factor
                if mtoon0_current_outline_factor != mtoon0_default_value_dict["outline_color"]
                else None
            )

            # 取得した各パラメーターを格納した辞書を作成する｡
            obtained_mtoon0_color_parameters: MToonMaterialParameters = {
                "color": mtoon0_color_factor,
                "shade_color": mtoon0_shade_color_factor,
                "emission_color": mtoon0_emissive_color_factor,
                "rim_color": mtoon0_rim_color_factor,
                "outline_color": mtoon0_outline_color_factor,
            }
            return obtained_mtoon0_color_parameters

        case "1":
            # 保存済みのMToo1パラメーターが存在すれば取得する｡
            mtoon1_default_value_dict = get_mtoon1_default_values(source_material)

            # 各パラメーターの現在の値(FloatVector)をリストとして取得する｡
            mtoon1_current_lit_factor = list(
                get_attr_from_strings(mtoon1, MTOON1_ATTRIBUTE_NAMES["lit_color"])
            )
            mtoon1_current_shade_factor = list(
                get_attr_from_strings(mtoon1, MTOON1_ATTRIBUTE_NAMES["shade_color"])
            )
            mtoon1_current_emissive_factor = list(
                get_attr_from_strings(mtoon1, MTOON1_ATTRIBUTE_NAMES["emission_color"])
            )
            mtoon1_current_matcap_factor = list(
                get_attr_from_strings(mtoon1, MTOON1_ATTRIBUTE_NAMES["matcap_color"])
            )
            mtoon1_current_rim_factor = list(
                get_attr_from_strings(mtoon1, MTOON1_ATTRIBUTE_NAMES["rim_color"])
            )
            mtoon1_current_outline_factor = list(
                get_attr_from_strings(mtoon1, MTOON1_ATTRIBUTE_NAMES["outline_color"])
            )

            # デフォルト値と現在の値を比較して変化している場合はその値を取得する｡
            mtoon1_lit_color_factor = (
                mtoon1_current_lit_factor
                if mtoon1_current_lit_factor != mtoon1_default_value_dict["lit_color"]
                else None
            )

            mtoon1_shade_color_factor = (
                mtoon1_current_shade_factor
                if mtoon1_current_shade_factor != mtoon1_default_value_dict["shade_color"]
                else None
            )

            mtoon1_emissive_color_factor = (
                mtoon1_current_emissive_factor
                if mtoon1_current_emissive_factor != mtoon1_default_value_dict["emission_color"]
                else None
            )
            mtoon1_matcap_color_factor = (
                mtoon1_current_matcap_factor
                if mtoon1_current_matcap_factor != mtoon1_default_value_dict["matcap_color"]
                else None
            )

            mtoon1_rim_color_factor = (
                mtoon1_current_rim_factor
                if mtoon1_current_rim_factor != mtoon1_default_value_dict["rim_color"]
                else None
            )

            mtoon1_outline_color_factor = (
                mtoon1_current_outline_factor
                if mtoon1_current_outline_factor != mtoon1_default_value_dict["outline_color"]
                else None
            )

            # 取得した各パラメーターを格納した辞書を作成する｡
            obtained_mtoon1_color_parameters: MToonMaterialParameters = {
                "lit_color": mtoon1_lit_color_factor,
                "shade_color": mtoon1_shade_color_factor,
                "emission_color": mtoon1_emissive_color_factor,
                "matcap_color": mtoon1_matcap_color_factor,
                "rim_color": mtoon1_rim_color_factor,
                "outline_color": mtoon1_outline_color_factor,
            }

            return obtained_mtoon1_color_parameters


def get_mtoon_uv_transform_current_parameters(
    source_material: Material,
) -> MToonMaterialParameters:
    """
    'source_material'の現在のMToonパラメーターからTexture Transformの値を取得して辞書として返す｡
    保存済みのパラメーターと比較して変化がない場合は保存済みのパラメーターを返す｡

    Parameters
    ----------
    source_material : Material
        処理対象のマテリアル

    Returns
    -------
    MToonMaterialParameters
        取得したパラメーターとパラメーター名のペアを格納した辞書｡

    """

    mtoon_ext = source_material.vrm_addon_extension.mtoon1

    match check_addon_mode():
        case "0":
            # 保存済みのMToo1パラメーターが存在すれば取得する｡
            mtoon0_default_offset_dict = get_mtoon0_default_values(source_material)

            # 各パラメーターの現在の値(FloatVector)をリストとして取得する｡
            mtoon0_current_texture_scale = list(
                get_attr_from_strings(mtoon_ext, MTOON0_ATTRIBUTE_NAMES["texture_scale"])
            )
            mtoon0_current_texture_offset = list(
                get_attr_from_strings(mtoon_ext, MTOON0_ATTRIBUTE_NAMES["texture_offset"])
            )
            #####################################################################################################
            # デフォルト値と現在の値を比較して変化している場合はその値を取得する｡
            mtoon0_default_scale = mtoon0_default_offset_dict["texture_scale"]
            mtoon0_texture_scale = (
                mtoon0_current_texture_scale if mtoon0_current_texture_scale != mtoon0_default_scale else None
            )
            mtoon0_default_offset = mtoon0_default_offset_dict["texture_offset"]
            mtoon0_texture_offset = (
                mtoon0_current_texture_offset
                if mtoon0_current_texture_offset != mtoon0_default_offset
                else None
            )
            #####################################################################################################

            obtained_mtoon0_transform_parameters: MToonMaterialParameters = {
                "texture_scale": mtoon0_texture_scale,
                "texture_offset": mtoon0_texture_offset,
            }

            return obtained_mtoon0_transform_parameters

        case "1":
            # 保存済みのMToo1パラメーターが存在すれば取得する｡
            mtoon1_default_offset_dict = get_mtoon1_default_values(source_material)

            # 各パラメーターの現在の値(FloatVector)をリストとして取得する｡
            mtoon1_current_texture_scale = list(
                get_attr_from_strings(mtoon_ext, MTOON1_ATTRIBUTE_NAMES["texture_scale"])
            )
            mtoon1_current_texture_offset = list(
                get_attr_from_strings(mtoon_ext, MTOON1_ATTRIBUTE_NAMES["texture_offset"])
            )
            #####################################################################################################
            # デフォルト値と現在の値を比較して変化している場合はその値を取得する｡
            mtoon1_default_scale = mtoon1_default_offset_dict["texture_scale"]
            mtoon1_texture_scale = (
                mtoon1_current_texture_scale if mtoon1_current_texture_scale != mtoon1_default_scale else None
            )
            mtoon1_default_offset = mtoon1_default_offset_dict["texture_offset"]
            mtoon1_texture_offset = (
                mtoon1_current_texture_offset
                if mtoon1_current_texture_offset != mtoon1_default_offset
                else None
            )
            #####################################################################################################

            obtained_mtoon1_transform_parameters: MToonMaterialParameters = {
                "texture_scale": mtoon1_texture_scale,
                "texture_offset": mtoon1_texture_offset,
            }

            return obtained_mtoon1_transform_parameters


def return_default_values_of_mtoon_properties(target_material: Material):
    mtoon1 = target_material.vrm_addon_extension.mtoon1
    addon_mode = check_addon_mode()
    match addon_mode:
        case "0":
            attr_dict = MTOON0_ATTRIBUTE_NAMES
            value_dict = MTOON0_DEFAULT_VALUES
        case "1":
            attr_dict = MTOON1_ATTRIBUTE_NAMES
            value_dict = MTOON1_DEFAULT_VALUES

    for parameter_name, attr_name in attr_dict.items():
        default_value = value_dict.get(parameter_name)
        set_attr_from_strings(mtoon1, attr_name, default_value)


def set_mtoon_default_values(target_material: Material):
    """
    コレクションプロパティに保存された値を用いて､"targett_material"のMToonパラメーターを復元する｡
    保存された値がない場合は規定のデフォルト値を復元する｡

    Parameters
    ----------
    target_material : Material
        処理対象となるマテリアル｡

    """
    if not target_material:
        return

    addon_mode = check_addon_mode()
    match addon_mode:
        case "0":
            attr_dict = MTOON0_ATTRIBUTE_NAMES
            stored_prop = get_scene_vrm0_mtoon_stored_prop()
        case "1":
            attr_dict = MTOON1_ATTRIBUTE_NAMES
            stored_prop = get_scene_vrm1_mtoon_stored_prop()

    stored_material_dict = {i.material: i for i in stored_prop}
    source_patameters = stored_material_dict.get(target_material)

    mtoon_ext = target_material.vrm_addon_extension.mtoon1
    for stored_parameter_name, mtoon_attr_name in attr_dict.items():
        if source_patameters and (value := source_patameters.get(stored_parameter_name)):
            # value = source_patameters.get(stored_parameter_name)
            logger.debug(f"Restore Stored Values : {target_material.name}")
            if stored_parameter_name in {"texture_scale", "texture_offset"}:
                for k, v in MTOON1_ATTRIBUTE_NAMES.items():
                    if not (re.search(r"scale|offset", k)):
                        continue
                    set_attr_from_strings(mtoon_ext, v, value)
            else:
                set_attr_from_strings(mtoon_ext, mtoon_attr_name, value)

        else:
            logger.debug(f"Return to Default Values : {target_material.name}")
            return_default_values_of_mtoon_properties(target_material)


# https://github.com/saturday06/VRM-Addon-for-Blender
def serach_vrm_shader_node(
    material: bpy.types.Material,
) -> Optional[bpy.types.ShaderNodeGroup]:
    if not material.node_tree or not material.node_tree.nodes:
        return None
    for node in material.node_tree.nodes:
        if not isinstance(node, bpy.types.ShaderNodeOutputMaterial):
            continue
        surface = node.inputs.get("Surface")
        if not surface:
            continue
        links = surface.links
        if not links:
            continue
        link = links[0]
        group_node = link.from_node
        if not isinstance(group_node, bpy.types.ShaderNodeGroup):
            continue
        if "SHADER" not in group_node.node_tree:
            continue
        return group_node

    return None


def check_vrm_material_mode(
    material: bpy.types.Material,
) -> Literal["GLTF", "MTOON", "NONE"]:
    """
    引数"material"がVRM Extensionにおいてどのタイプのマテリアルとして扱われるかをチェックする｡


    Parameters
    ----------
    material: bpy.types.Material
        処理対象のマテリアル｡

    Returns
    -------
    Literal["GLTF", "MTOON", "NONE"]
        マテリアルの設定に応じたタイプを文字列として返す｡

    """

    if not material:
        return "NONE"

    mat_vrm_ext = material.vrm_addon_extension
    if mat_vrm_ext != None:
        if mat_vrm_ext.mtoon1.enabled:
            return "MTOON"

    if vrm_node := serach_vrm_shader_node(material):
        if vrm_node.node_tree["SHADER"] == "MToon_unversioned":
            return "MTOON"

    return "GLTF"


def get_all_collider_objects_from_scene() -> list[Object]:
    """
    Target ArmatureのVRM Extensionに登録された全てのコライダーオブジェクトのリストを返す｡

    Returns
    -------
    list[Object]
        コライダーを定義するEmpty Objectのリスト｡

    """
    # Target ArmatureのVRM Extensionに定義された全コライダーオブジェクトを取得する｡
    collider_object_list = []
    if not (colliders := get_vrm_extension_property("COLLIDER")):
        return collider_object_list

    for collider in colliders:
        empty_object = collider.bpy_object
        if not empty_object:
            continue

        collider_object_list.append(empty_object)

        # コライダータイプがCapsuleであれば子オブジェクトもリストに追加する｡
        if children := empty_object.children:
            collider_object_list.append(children[0])

    return collider_object_list


def re_link_all_collider_object2collection():
    """
    アドオンが定義するコレクション構造を構成した上で､
    定義されている全てのコライダーオブジェクトを対応するコレクションにリンクさせる｡
    """

    addon_collection_dict = setting_vrm_helper_collection()
    if not get_target_armature():
        return

    vrm1_collider_collection = addon_collection_dict["VRM1_COLLIDER"]
    collider_objects = get_all_collider_objects_from_scene()

    for obj in collider_objects:
        unlink_object_from_all_collections(obj)
        vrm1_collider_collection.objects.link(obj)


def add_list_item2bone_group_list4operator():
    """
    オペレーターの処理対象ボーングループを定義するためのコレクションプロパティにアイテムを登録する｡
    """

    addon_pref = get_addon_preferences()
    filtering_word = addon_pref.bone_group_filter_name

    bone_group_collection = get_ui_bone_group_prop()
    bone_group_collection.clear()

    # Blender 4.0以降はBone GroupはBone Colledtionに統合されているため､データ取得元を分岐
    if bpy.app.version < (4, 0, 0):
        source_group = get_target_armature().pose.bone_groups
    else:
        source_group = get_target_armature_data().collections

    for n, group in enumerate(source_group):
        new_item: VRMHELPER_WM_operator_spring_bone_group_list_items = bone_group_collection.add()
        new_item.name = group.name
        new_item.group_index = n
        # Bone Groupの名前に'filter_word'が含まれる場合は初期値をTrueにする｡
        if filtering_word in group.name:
            new_item.is_target = True
