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
    Any,
    Literal,
    Iterator,
    TypedDict,
    NamedTuple,
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

from mathutils import (
    Color,
)

from .property_groups import (
    ReferenceVrm1MaterialColorBindPropertyGroup,
    ReferenceVrm1ColliderPropertyGroup,
    # ----------------------------------------------------------
    VRMHELPER_SCENE_vrm1_mtoon1_stored_parameters,
    get_addon_prop_group,
    get_target_armature,
    get_target_armature_data,
    get_ui_list_prop4custom_filter,
)

from .utils_common import (
    get_attr_from_strings,
    set_attr_from_strings,
    get_selected_bone,
    get_bones_for_each_branch_from_source_bones,
    unlink_object_from_all_collections,
    setting_vrm_helper_collection,
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
    Class
------------------------------------------------------------
---------------------------------------------------------"""


class MToon1ParameterNames(TypedDict):
    texture_scale: str
    texture_offset: str
    lit_color: str
    shade_color: str
    emission_color: str
    matcap_color: str
    rim_color: str
    outline_color: str


class MToon1MaterialParameters(TypedDict, total=False):
    texture_scale: list[float]
    texture_offset: list[float]
    lit_color: list[float]
    shade_color: list[float]
    emission_color: list[float]
    matcap_color: list[float]
    rim_color: list[float]
    outline_color: list[float]


class VrmRollConstraint:
    pass


class VrmAimConstraint:
    pass


class VrmRotationConstraint:
    pass


class CandidateConstraitProperties(NamedTuple):
    type: VrmAimConstraint | VrmAimConstraint | VrmRotationConstraint  # VRMコンストレイントの種類
    element: Object | Bone  # コンストレイントがアタッチされたデータ
    index: int  # elementが持つコンストレイントスタックにおける対象コンストレイントのインデックス
    is_circular_dependency: bool  # 循環依存関係が生じていることを示すフラグ
    constraint: CopyRotationConstraint | DampedTrackConstraint  # 'element'にアタッチされたコンストレイント


class ConstraintTypeDict(TypedDict):
    ROLL: str
    AIM: str
    ROTATION: str


"""---------------------------------------------------------
------------------------------------------------------------
    Constant
------------------------------------------------------------
---------------------------------------------------------"""
MTOON_ATTRIBUTE_NAMES: MToon1ParameterNames = {
    "texture_scale": "pbr_metallic_roughness.base_color_texture.extensions.khr_texture_transform.scale",
    "texture_offset": "pbr_metallic_roughness.base_color_texture.extensions.khr_texture_transform.offset",
    "lit_color": "pbr_metallic_roughness.base_color_factor",
    "shade_color": "extensions.vrmc_materials_mtoon.shade_color_factor",
    "emission_color": "emissive_factor",
    "matcap_color": "extensions.vrmc_materials_mtoon.matcap_factor",
    "rim_color": "extensions.vrmc_materials_mtoon.parametric_rim_color_factor",
    "outline_color": "extensions.vrmc_materials_mtoon.outline_color_factor",
}

MTOON_DEFAULT_VALUES: MToon1MaterialParameters = {
    "texture_scale": [1.0, 1.0],
    "texture_offset": [0.0, 0.0],
    "lit_color": [1.0, 1.0, 1.0, 1.0],
    "shade_color": [1.0, 1.0, 1.0],
    "emission_color": [0.0, 0.0, 0.0],
    "matcap_color": [1.0, 1.0, 1.0],
    "rim_color": [0.0, 0.0, 0.0],
    "outline_color": [0.0, 0.0, 0.0],
}


"""---------------------------------------------------------
------------------------------------------------------------
    Function
------------------------------------------------------------
---------------------------------------------------------"""


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

    bone_group_collection = get_ui_list_prop4custom_filter("BONE_GROUP")

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
    basic_prop = get_addon_prop_group("BASIC")

    return basic_prop.tool_mode


def get_vrm_extension_root_property(
    target: Literal["SPRING1"] | None = None,
) -> PropertyGroup:
    """
    選択されているUI Modeに対応したバージョンのVRM Extensionのルートプロパティを取得する｡

    Parameters
    ----------
    target : str | None,  --optional
        VRM1のSpring Boneのプロパティを取得する場合は'SPRING1'を指定する｡
        by default : None

    Returns
    -------
    PropertyGroup
        選択されているUI Modeに応じてVRM ExtensionのProperty Groupのルートを取得する｡

    """
    target_armature = get_target_armature_data()

    if target is None:
        if check_addon_mode() == "0":
            vrm_extension = target_armature.vrm_addon_extension.vrm0

        if check_addon_mode() == "1":
            vrm_extension = target_armature.vrm_addon_extension.vrm1

    if target == "SPRING1":
        vrm_extension = target_armature.vrm_addon_extension.spring_bone1

    return vrm_extension


def get_vrm_extension_property(
    type: Literal[
        "FIRST_PERSON",
        "EXPRESSION",
        "SPRING",
        "COLLIDER",
        "COLLIDER_GROUP",
    ]
) -> ReferenceVrm1ColliderPropertyGroup | PropertyGroup:
    """
    Target ArmatureのVRM Extensionの中から引数で指定したProperty Groupを取得する｡

    Parameters
    ----------
    type : type: Literal[
        "FIRST_PERSON",
        "EXPRESSION",
        'SPRING'
        "COLLIDER",
        'COLLIDER_GROUP'

    ]

    Returns
    -------
    VrmAddonVrmAddonArmatureExtensionPropertyGroup
        VRM Addon定義のPropertyGroupのうち､引数で指定したもの

    """

    # Spring Bone関連のプロパティでない場合｡
    if any([type == "FIRST_PERSON", type == "EXPRESSION"]):
        vrm_extension = get_vrm_extension_root_property()

        if type == "FIRST_PERSON":
            return vrm_extension.first_person

        if type == "EXPRESSION":
            if check_addon_mode() == "0":
                return vrm_extension.blend_shape_master.blend_shape_groups

            if check_addon_mode() == "1":
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
    target_armature = get_addon_prop_group("BASIC").target_armature.data
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
            mtoon1_attr_name = MTOON_ATTRIBUTE_NAMES["lit_color"]

        case "shadeColor" | "shade_color":
            mtoon1_attr_name = MTOON_ATTRIBUTE_NAMES["shade_color"]

        case "emissionColor" | "emission_color":
            mtoon1_attr_name = MTOON_ATTRIBUTE_NAMES["emission_color"]

        case "matcapColor" | "matcap_color":
            mtoon1_attr_name = MTOON_ATTRIBUTE_NAMES["matcap_color"]

        case "rimColor" | "rim_color":
            mtoon1_attr_name = MTOON_ATTRIBUTE_NAMES["rim_color"]

        case "outlineColor" | "outline_color":
            mtoon1_attr_name = MTOON_ATTRIBUTE_NAMES["outline_color"]

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
        mtoon1_attr_name = MTOON_ATTRIBUTE_NAMES[name]
        value = attrgetter(mtoon1_attr_name)(mtoon1)

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
        i for i in get_addon_prop_group("MTOON1") if i.material == source_material
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
        default_texture_scale = MTOON_DEFAULT_VALUES["texture_scale"]
        default_texture_offset = MTOON_DEFAULT_VALUES["texture_offset"]
        default_lit_factor = MTOON_DEFAULT_VALUES["lit_color"]
        default_shade_factor = MTOON_DEFAULT_VALUES["shade_color"]
        default_emissive_factor = MTOON_DEFAULT_VALUES["emission_color"]
        default_matcap_factor = MTOON_DEFAULT_VALUES["matcap_color"]
        default_rim_factor = MTOON_DEFAULT_VALUES["rim_color"]
        default_outline_factor = MTOON_DEFAULT_VALUES["outline_color"]

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
        get_attr_from_strings(mtoon1, MTOON_ATTRIBUTE_NAMES["lit_color"])
    )
    current_shade_factor = list(
        get_attr_from_strings(mtoon1, MTOON_ATTRIBUTE_NAMES["shade_color"])
    )
    current_emissive_factor = list(
        get_attr_from_strings(mtoon1, MTOON_ATTRIBUTE_NAMES["emission_color"])
    )
    current_matcap_factor = list(
        get_attr_from_strings(mtoon1, MTOON_ATTRIBUTE_NAMES["matcap_color"])
    )
    current_rim_factor = list(
        get_attr_from_strings(mtoon1, MTOON_ATTRIBUTE_NAMES["rim_color"])
    )
    current_outline_factor = list(
        get_attr_from_strings(mtoon1, MTOON_ATTRIBUTE_NAMES["outline_color"])
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
        get_attr_from_strings(mtoon1, MTOON_ATTRIBUTE_NAMES["texture_offset"])
    )
    current_texture_scale = list(
        get_attr_from_strings(mtoon1, MTOON_ATTRIBUTE_NAMES["texture_scale"])
    )
    #####################################################################################################
    # デフォルト値と現在の値を比較して変化している場合はその値を取得する｡
    texture_offset = (
        current_texture_offset
        if current_texture_offset != default_value_dict["texture_offset"]
        else None
    )

    texture_scale = (
        current_texture_scale
        if current_texture_scale != default_value_dict["texture_scale"]
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
    ) in MTOON_ATTRIBUTE_NAMES.items():
        default_value = MTOON_DEFAULT_VALUES.get(parameter_name)
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

    stored_material_dict = {i.material: i for i in get_addon_prop_group("MTOON1")}
    source_patameters = stored_material_dict.get(target_material)

    mtoon1 = target_material.vrm_addon_extension.mtoon1
    for stored_parameter_name, mtoon1_attr_name in MTOON_ATTRIBUTE_NAMES.items():
        if source_patameters:
            value = source_patameters.get(stored_parameter_name)
            logger.debug(f"Restore Stored Values : {target_material.name}")
            set_attr_from_strings(mtoon1, mtoon1_attr_name, value)
        else:
            logger.debug(f"Return to Default Values : {target_material.name}")
            return_default_values_of_mtoon1_properties(target_material)


def get_all_collider_objects_from_scene() -> list[Object]:
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
    addon_collection_dict = setting_vrm_helper_collection()
    vrm1_collider_collection = addon_collection_dict["VRM1_Collider"]
    collider_objects = get_all_collider_objects_from_scene()
    pprint(collider_objects)

    for obj in collider_objects:
        unlink_object_from_all_collections(obj)
        vrm1_collider_collection.objects.link(obj)
