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


from operator import (
    attrgetter,
)
from pprint import (
    pprint,
)
from typing import (
    Literal,
    Optional,
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
    ReferenceVrm0BlendShapeMasterPropertyGroup,
    # ----------------------------------------------------------
    MToon1MaterialParameters,
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
    MTOON1_ATTRIBUTE_NAMES,
    MTOON1_DEFAULT_VALUES,
)

from .property_groups import (
    VRMHELPER_SCENE_vrm1_ui_list_active_indexes,
    VRMHELPER_SCENE_vrm1_mtoon1_stored_parameters,
    get_scene_basic_prop,
    get_target_armature,
    get_target_armature_data,
    get_ui_vrm1_operator_bone_group_prop,
    get_scene_vrm1_mtoon_stored_prop,
)

from .utils_common import (
    get_attr_from_strings,
    set_attr_from_strings,
    get_selected_bone,
    get_bones_for_each_branch_from_source_bones,
    unlink_object_from_all_collections,
    setting_vrm_helper_collection,
    get_addon_collection_name,
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
    # 1つ以上のオブジェクトがリンクされた'VRM1 Expression Morph'のコレクションが
    # 存在するか否かを判定する｡

    Returns
    -------
    bool
        条件を満たしていればTrue､そうでなければFalseを返す｡
    """

    if collection_mat := bpy.data.collections.get(
        get_addon_collection_name("VRM1_EXPRESSION_MORPH")
    ):
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

    if collection_mat := bpy.data.collections.get(
        get_addon_collection_name("VRM1_EXPRESSION_MATERIAL")
    ):
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
    指定したBone Groupに属するボーンを'target_armature'から取得する｡

    Parameters
    ----------
    target_armature : Object
        処理対象となるArmature Object

    Returns
    -------
    list[Bone]
        取得したボーンを格納したリスト｡

    """

    bone_group_collection = get_ui_vrm1_operator_bone_group_prop()

    target_group_index_list = [
        i.group_index for i in bone_group_collection if i.is_target
    ]
    target_bone_list = [
        bone
        for (bone, pose_bone) in zip(
            target_armature.data.bones, target_armature.pose.bones
        )
        if pose_bone.bone_group
        and pose_bone.bone_group_index in target_group_index_list
    ]

    return target_bone_list


def get_bones_for_each_branch_by_type(
    source_type: Literal["SELECT", "BONE_GROUP"],
    target_armature: Object,
) -> list[Bone]:
    """
    'source_type'で指定したソースから枝毎にグルーピングされたボーンを取得する｡

    Parameters
    ----------
    source_type : Literal["SELECT", "BONE_GROUP"]
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
        source_bones = get_selected_bone(target_armature.data)

    if source_type == "BONE_GROUP":
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


def get_vrm_extension_all_root_property() -> (
    Optional[ReferenceVrmAddonArmatureExtensionPropertyGroup]
):
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
    target: Literal["VRM", "SPRING1", "CONSTRAINT"],
) -> (
    ReferenceVrm0PropertyGroup
    | ReferenceVrm1PropertyGroup
    | ReferenceSpringBone1SpringBonePropertyGroup
    | ReferenceNodeConstraint1NodeConstraintPropertyGroup
):
    """
    選択されているUI Modeに対応したバージョンのVRM Extensionのルートプロパティを取得する｡

    Parameters
    ----------
    target: Literal["VRM", "SPRING1","CONSTRAINT"]
        取得したいプロパティグループの種類を指定する｡

    Returns
    -------
    PropertyGroup
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

        case "SPRING1":
            vrm_property = vrm_extension.spring_bone1

    return vrm_property


"""---------------------------------------------------------
    Cnndidaete Replacing
---------------------------------------------------------"""


# ----------------------------------------------------------
#    VRM0
# ----------------------------------------------------------
def get_vrm0_extension_root_property() -> ReferenceVrm1PropertyGroup:
    vrm_all_root = get_vrm_extension_all_root_property()
    vrm0_root = vrm_all_root.vrm0
    return vrm0_root


def get_vrm0_extension_property_blend_shape() -> (
    ReferenceVrm0BlendShapeMasterPropertyGroup
):
    vrm0_extension = get_vrm0_extension_root_property()
    vrm0_blend_shapes = vrm0_extension.blend_shapes
    return vrm0_blend_shapes


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
) -> (
    ReferenceVrm1FirstPersonPropertyGroup
    | ReferenceVrm1ExpressionPropertyGroup
    | ReferenceVrm1ColliderPropertyGroup
    | ReferenceVrm1ColliderGroupPropertyGroup
    | ReferenceSpringBone1SpringPropertyGroup
):
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
    VrmAddonVrmAddonArmatureExtensionPropertyGroup
        VRM Addon定義のPropertyGroupのうち､引数で指定したもの

    """

    # Spring Bone関連のプロパティでない場合｡
    if type in {"FIRST_PERSON", "BLEND_SHAPE", "EXPRESSION"}:
        vrm_extension = get_vrm_extension_root_property("VRM")
        match type:
            case "FIRST_PERSON":
                return vrm_extension.first_person

            case "BLEND_SHAPE":
                return vrm_extension.blend_shape_master.blend_shape_groups

            case "EXPRESSION":
                return vrm_extension.expressions

    # Spring Bone関連のプロパティである場合｡
    else:
        vrm_extension = get_vrm_extension_root_property(target="SPRING1")
        if type == "COLLIDER":
            if check_addon_mode() == "0":
                return

            if check_addon_mode() == "1":
                colliders: ReferenceVrm1ColliderPropertyGroup = vrm_extension.colliders
                return colliders

        if type == "COLLIDER_GROUP":
            if check_addon_mode() == "0":
                return

            if check_addon_mode() == "1":
                return vrm_extension.collider_groups

        if type == "SPRING":
            if check_addon_mode() == "0":
                return

            if check_addon_mode() == "1":
                return vrm_extension.springs


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


def get_mtoon_attr_name_from_bind_type(
    color_bind_type: Literal[
        "color",
        "shadeColor",
        "emissionColor",
        "matcapColor",
        "rimColor",
        "outlineColor",
    ],
) -> str | None:
    """
    引数'color_bind_type'に対応したMToo1属性名を返す｡

    Parameters
    ----------
    color_bind_type: Literal[
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
    str|None
        取得された属性名｡

    """

    mtoon1_attr_name = None
    match color_bind_type:
        case "color" | "lit_color":
            mtoon1_attr_name = MTOON1_ATTRIBUTE_NAMES["lit_color"]

        case "shadeColor" | "shade_color":
            mtoon1_attr_name = MTOON1_ATTRIBUTE_NAMES["shade_color"]

        case "emissionColor" | "emission_color":
            mtoon1_attr_name = MTOON1_ATTRIBUTE_NAMES["emission_color"]

        case "matcapColor" | "matcap_color":
            mtoon1_attr_name = MTOON1_ATTRIBUTE_NAMES["matcap_color"]

        case "rimColor" | "rim_color":
            mtoon1_attr_name = MTOON1_ATTRIBUTE_NAMES["rim_color"]

        case "outlineColor" | "outline_color":
            mtoon1_attr_name = MTOON1_ATTRIBUTE_NAMES["outline_color"]

    return mtoon1_attr_name

    pass


def store_mtoon1_current_values(
    target_item: VRMHELPER_SCENE_vrm1_mtoon1_stored_parameters,
    source_material: Material,
):
    """
    Scene階層下にあるMToon1のパラメーター保存用コレクションプロパティに登録されたアイテムに
    "source_material"が持つMToon1パラメーターを保存して復元できるようにする｡｡

    Parameters
    ----------
    target_item : VRMHELPER_SCENE_vrm1_mtoon1_stored_parameters
        処理対象となるコレクションプロパティのアイテム

    source_material : Material
        値が保存されるマテリアル｡

    """
    stored_parameter_names = list(target_item.__annotations__.keys())
    stored_parameter_names.remove("material")
    target_item.material = source_material
    mtoon1 = source_material.vrm_addon_extension.mtoon1

    for name in stored_parameter_names:
        mtoon1_attr_name = MTOON1_ATTRIBUTE_NAMES[name]
        value = attrgetter(mtoon1_attr_name)(mtoon1)
        # value = [abs(i) for i in value]

        setattr(target_item, name, value)


def get_mtoon1_default_values(
    source_material: Material,
) -> MToon1MaterialParameters:
    """
    'source_material'の保存済みデフォルト値を取得する｡保存データが存在しない場合は
    MToonマテリアルが定義したデフォルト値を取得して辞書として返す｡

    Parameters
    ----------
    source_material : Material
        処理対象のマテリアル

    Returns
    -------
    MToon1MaterialParameters
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

    obtained_default_parameters: MToon1MaterialParameters = {
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
) -> MToon1MaterialParameters:
    """
    'source_material'の現在のMToonパラメーターからMaterial Colorの値を取得して辞書として返す｡
    保存済みのパラメーターと比較して変化がない場合は保存済みのパラメーターを返す｡

    Parameters
    ----------
    source_material : Material
        処理対象のマテリアル

    Returns
    -------
    MToon1MaterialParameters
        取得したパラメーターとパラメーター名のペアを格納した辞書｡

    """

    mtoon1 = source_material.vrm_addon_extension.mtoon1

    # 保存済みのMToo1パラメーターが存在すれば取得する｡
    default_value_dict = get_mtoon1_default_values(source_material)

    # 各パラメーターの現在の値(FloatVector)をリストとして取得する｡
    current_lit_factor = list(
        get_attr_from_strings(mtoon1, MTOON1_ATTRIBUTE_NAMES["lit_color"])
    )
    current_shade_factor = list(
        get_attr_from_strings(mtoon1, MTOON1_ATTRIBUTE_NAMES["shade_color"])
    )
    current_emissive_factor = list(
        get_attr_from_strings(mtoon1, MTOON1_ATTRIBUTE_NAMES["emission_color"])
    )
    current_matcap_factor = list(
        get_attr_from_strings(mtoon1, MTOON1_ATTRIBUTE_NAMES["matcap_color"])
    )
    current_rim_factor = list(
        get_attr_from_strings(mtoon1, MTOON1_ATTRIBUTE_NAMES["rim_color"])
    )
    current_outline_factor = list(
        get_attr_from_strings(mtoon1, MTOON1_ATTRIBUTE_NAMES["outline_color"])
    )
    #####################################################################################################

    # デフォルト値と現在の値を比較して変化している場合はその値を取得する｡
    color_factor = (
        current_lit_factor
        if current_lit_factor != default_value_dict["lit_color"]
        else None
    )

    shade_color_factor = (
        current_shade_factor
        if current_shade_factor != default_value_dict["shade_color"]
        else None
    )

    emissive_color_factor = (
        current_emissive_factor
        if current_emissive_factor != default_value_dict["emission_color"]
        else None
    )
    matcap_color_factor = (
        current_matcap_factor
        if current_matcap_factor != default_value_dict["matcap_color"]
        else None
    )

    rim_color_factor = (
        current_rim_factor
        if current_rim_factor != default_value_dict["rim_color"]
        else None
    )

    outline_color_factor = (
        current_outline_factor
        if current_outline_factor != default_value_dict["outline_color"]
        else None
    )
    #####################################################################################################

    obtained_mtoon1_color_parameters: MToon1MaterialParameters = {
        "lit_color": color_factor,
        "shade_color": shade_color_factor,
        "emission_color": emissive_color_factor,
        "matcap_color": matcap_color_factor,
        "rim_color": rim_color_factor,
        "outline_color": outline_color_factor,
    }

    return obtained_mtoon1_color_parameters


def get_mtoon_transform_current_parameters(
    source_material: Material,
) -> MToon1MaterialParameters:
    """
    'source_material'の現在のMToonパラメーターからTexture Transformの値を取得して辞書として返す｡
    保存済みのパラメーターと比較して変化がない場合は保存済みのパラメーターを返す｡

    Parameters
    ----------
    source_material : Material
        処理対象のマテリアル

    Returns
    -------
    MToon1MaterialParameters
        取得したパラメーターとパラメーター名のペアを格納した辞書｡

    """

    mtoon1 = source_material.vrm_addon_extension.mtoon1

    # 保存済みのMToo1パラメーターが存在すれば取得する｡
    default_value_dict = get_mtoon1_default_values(source_material)

    # 各パラメーターの現在の値(FloatVector)をリストとして取得する｡
    current_texture_offset = list(
        get_attr_from_strings(mtoon1, MTOON1_ATTRIBUTE_NAMES["texture_offset"])
    )
    # current_texture_offset = [abs(i) for i in current_texture_offset]
    current_texture_scale = list(
        get_attr_from_strings(mtoon1, MTOON1_ATTRIBUTE_NAMES["texture_scale"])
    )
    #####################################################################################################
    # デフォルト値と現在の値を比較して変化している場合はその値を取得する｡
    default_offset = default_value_dict["texture_offset"]
    texture_offset = (
        current_texture_offset
        if current_texture_offset != default_offset
        # else default_offset
        else None
    )
    default_scale = default_value_dict["texture_scale"]
    texture_scale = (
        current_texture_scale
        if current_texture_scale != default_scale
        # else default_scale
        else None
    )
    #####################################################################################################

    obtained_mtoon1_transform_parameters: MToon1MaterialParameters = {
        "texture_scale": texture_scale,
        "texture_offset": texture_offset,
    }

    return obtained_mtoon1_transform_parameters


def return_default_values_of_mtoon1_properties(target_material: Material):
    mtoon1 = target_material.vrm_addon_extension.mtoon1

    for (
        parameter_name,
        attr_name,
    ) in MTOON1_ATTRIBUTE_NAMES.items():
        default_value = MTOON1_DEFAULT_VALUES.get(parameter_name)
        set_attr_from_strings(mtoon1, attr_name, default_value)


def set_mtoon1_default_values(target_material: Material):
    """
    コレクションプロパティに保存された値を用いて､"targett_material"のMToon1パラメーターを復元する｡
    保存された値がない場合は規定のデフォルト値を復元する｡

    Parameters
    ----------
    target_material : Material
        処理対象となるマテリアル｡

    """
    if not target_material:
        return

    stored_material_dict = {i.material: i for i in get_scene_vrm1_mtoon_stored_prop()}
    source_patameters = stored_material_dict.get(target_material)

    mtoon1 = target_material.vrm_addon_extension.mtoon1
    for stored_parameter_name, mtoon1_attr_name in MTOON1_ATTRIBUTE_NAMES.items():
        if source_patameters:
            value = source_patameters.get(stored_parameter_name)
            logger.debug(f"Restore Stored Values : {target_material.name}")
            set_attr_from_strings(mtoon1, mtoon1_attr_name, value)
        else:
            logger.debug(f"Return to Default Values : {target_material.name}")
            return_default_values_of_mtoon1_properties(target_material)


def get_all_collider_objects_from_scene() -> list[Object]:
    """
    Target ArmatureのVRM Extensionに登録された全てのコライダーオブジェクトのリストを返す｡

    Returns
    -------
    list[Object]
        コライダーを定義するEmpty Objectのリスト｡

    """
    # Target ArmatureのVRM Extensionに定義された全コライダーオブジェクトを取得する｡
    colliders = get_vrm_extension_property("COLLIDER")
    collider_object_list = []
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
