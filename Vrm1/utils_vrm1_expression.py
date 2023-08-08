if "bpy" in locals():
    import importlib

    reloadable_modules = [
        "preparation_logger",
        "utils_common",
        "utils_vrm_base",
    ]

    for module in reloadable_modules:
        if module in locals():
            importlib.reload(locals()[module])

else:
    from ..Logging import preparation_logger
    from .. import utils_common
    from .. import utils_vrm_base

from operator import (
    attrgetter,
)
from pprint import pprint
import bpy
from bpy.types import (
    Object,
    ShapeKey,
    Material,
    PropertyGroup,
    bpy_prop_collection,
)


from ..addon_classes import (
    ReferenceVrm1ExpressionPropertyGroup,
    ReferenceVrm1MaterialColorBindPropertyGroup,
    ReferenceVrm1TextureTransformBindPropertyGroup,
)

from ..addon_constants import (
    PRESET_EXPRESSION_NAME_DICT,
)

from ..property_groups import (
    VRMHELPER_WM_vrm1_expression_material_list_items,
    # ----------------------------------------------------------
    VRMHELPER_WM_vrm1_expression_list_items,
    get_ui_vrm1_expression_prop,
    get_ui_vrm1_expression_morph_prop,
    get_ui_vrm1_expression_material_prop,
    get_target_armature,
    get_target_armature_data,
    get_vrm1_active_index_prop,
)

from ..utils_common import (
    get_attr_from_strings,
    set_attr_from_strings,
)

from ..utils_vrm_base import (
    MToon1MaterialParameters,
    MTOON_ATTRIBUTE_NAMES,
    get_vrm_extension_property,
    get_mtoon_attr_name_from_bind_type,
    get_mtoon_color_current_parameters,
    get_mtoon_transform_current_parameters,
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
    Function
------------------------------------------------------------
---------------------------------------------------------"""


# ----------------------------------------------------------
#    Expressions
# ----------------------------------------------------------
def get_active_list_item_in_expression() -> (
    VRMHELPER_WM_vrm1_expression_list_items | None
):
    if expressions_list := get_ui_vrm1_expression_prop():
        return expressions_list[get_vrm1_active_index_prop("EXPRESSION")]
    else:
        return None


def get_source_vrm1_expression4ui_list() -> (
    tuple[
        dict[str, PropertyGroup],
        dict[str, PropertyGroup],
    ]
):
    """
    Target Armatureに登録されたプリセットエクスプレッションのリストと
    カスタムエクスプレションのリストを格納したタプルを返す｡

    Returns
    -------
    tuple[
        dict[str, VRM_Addon_for_Blender.editor.vrm1.property_group.Vrm1ExpressionPropertyGroup],
        dict[str, VRM_Addon_for_Blender.editor.vrm1.property_group.Vrm1ExpressionPropertyGroup],
    ]
        Target Armatureが持つプリセットエクスプレッションを格納した辞書と
        カスタムエクスプレションを格納した辞書を格納したタプル｡

    """
    expressions = get_vrm_extension_property("EXPRESSION")

    preset_expressions_dict = {}
    # UI Listに表示する対象オブジェクトをリストに格納する
    for data_name, display_name in PRESET_EXPRESSION_NAME_DICT.items():
        preset_expressions_dict[display_name] = attrgetter(data_name)(expressions)

    custom_expressions_dict = {i.custom_name: i.expression for i in expressions.custom}

    return preset_expressions_dict, custom_expressions_dict


def add_items2expression_ui_list() -> int:
    """
    Expressionの確認/設定を行なうUI Listの描画候補アイテムをコレクションプロパティに追加する｡
    UI Listのrows入力用にアイテム数を返す｡

    Returns
    -------
    int
        リストに表示するアイテム数｡

    """

    (
        preset_expressions_dict,
        custom_expressions_dict,
    ) = get_source_vrm1_expression4ui_list()

    items = get_ui_vrm1_expression_prop()
    # Pyhon標準のリストに格納した値はコレクションの全要素で共有されるので､2回目以降の処理ではリセットが必要｡
    if items:
        items[0].expressions_list.clear()
    items.clear()

    # プリセットエクスプレッションの情報を追加
    for display_name in preset_expressions_dict.keys():
        new_item = items.add()
        new_item.name = display_name

    new_item.expressions_list.extend(preset_expressions_dict.values())

    # カスタムエクスプレッションの情報を追加
    for n, custom_name in enumerate(custom_expressions_dict.keys()):
        new_item = items.add()
        new_item.name = custom_name
        new_item.custom_expression_index = n

    new_item.expressions_list.extend(custom_expressions_dict.values())

    return len(items)


# ----------------------------------------------------------
#    Morph Target
# ----------------------------------------------------------


def get_active_expression() -> ReferenceVrm1ExpressionPropertyGroup | None:
    """
    エクスプレッションリストでアクティブになっているエクスプレッションを取得する｡
    エラーになる場合はオフセットしてエラーを回避する｡

    Returns
    -------
    ReferenceVrm1ExpressionPropertyGroup
        リスト内でアクティブになっているエクスプレッションのプロパティグループ｡

    """
    active_index = get_vrm1_active_index_prop("EXPRESSION")
    if not (expressions_list := get_ui_vrm1_expression_prop()):
        return
    expressions_list = expressions_list[0].expressions_list
    if len(expressions_list) < active_index + 1:
        active_index = len(expressions_list) - 1
    active_item = expressions_list[active_index]

    return active_item


def get_source_vrm1_expression_morph4ui_list() -> (
    dict[str, list[tuple[PropertyGroup, int]]]
):
    """
    UI Listでアクティブになっているエクスプレションに登録されているMorph Target Bindの情報を取得する｡

    Returns
    -------
    dict[str, list[tuple[VrmAddon.Vrm1MorphTargetBindPropertyGroup, int]]]
        エクスプレッションに登録されたMorph Target Bindとインデックスのペアを格納したタプルのリストを
        対応するオブジェクト名をキーとして格納した辞書｡

    """

    # データ取得対象となる'morph_target_binds'から取得する｡
    active_item = get_active_expression()
    morph_target_binds_dict = {}
    for n, morph_bind in enumerate(active_item.morph_target_binds):
        morph_target_binds_dict.setdefault(morph_bind.node.mesh_object_name, []).append(
            (morph_bind, n)
        )

    return morph_target_binds_dict


def add_items2expression_morph_ui_list() -> int:
    """
    Morph Target Bindの確認/設定を行なうUI Listの描画候補アイテムをコレクションプロパティに追加する｡
    UI Listのrows入力用にアイテム数を返す｡

    Returns
    -------
    int
        リストに表示するアイテム数｡

    """

    items = get_ui_vrm1_expression_morph_prop()
    source_morph_binds_dict = get_source_vrm1_expression_morph4ui_list()
    items.clear()

    for obj_name, bind_list in source_morph_binds_dict.items():
        target_item = items.add()
        target_item.item_type[0] = True
        target_item.name = obj_name

        for bind, index in bind_list:
            target_item = items.add()
            target_item.item_type[1] = True
            target_item.name = obj_name
            target_item.shape_key_name = bind.index
            target_item.bind_index = index

    return len(items)


# Vrm1MorphTargetBindPropertyGroup
def get_same_value_existing_morph_bind(
    obj_name: str, shape_key_name: str
) -> PropertyGroup | None:
    """
    アクティブエクスプレションのMorph Target Bindの中から
    2つの引数と同じ値が設定されたものを走査して取得する｡

    Parameters
    ----------
    obj_name : str
        検索対象のオブジェクト名
    shape_key_name : str
        検索対象のシェイプキー名

    Returns
    -------
    VRM_Addon.Vrm1MorphTargetBindPropertyGroup | None
        'mesh_object_name'と'indes'の値が引数と同じMorpht Target Bind｡
        該当データがなければNone｡
    """

    for morph_bind in get_active_expression().morph_target_binds:
        if (
            morph_bind.node.mesh_object_name == obj_name
            and morph_bind.index == shape_key_name
        ):
            return morph_bind
    return None


def search_existing_morph_bind_and_update(
    source_object: Object,
    source_shape_key: ShapeKey,
    morph_target_binds: bpy_prop_collection,
) -> bool:
    """
    'morph_target_binds'内に'source_object'と'source_shape_key'のペアが登録されたMorph Bindが
    存在するか否かを走査し､存在する場合値の更新する｡値が0の場合はMorph Bindの削除を行なう｡
    また､存在したか否かの判定を返す｡

    Parameters
    ----------
    source_object : Object
        検索対象のオブジェクト
    source_shape_key : ShapeKey
        検索対象のシェイプキー
    morph_target_binds : bpy_prop_collection
        処理対象となるMorph Target Binds

    Returns
    -------
    bool
        該当するMorph Bindが存在した場合はTrue,存在しなかった場合はFalse｡
    """

    if morph_bind := get_same_value_existing_morph_bind(
        source_object.name, source_shape_key.name
    ):
        if source_shape_key.value == 0:
            logger.debug(f"Remove 0 Value morph_Bind : {morph_bind.index}")
            morph_target_binds.remove(list(morph_target_binds).index(morph_bind))

        else:
            if morph_bind.weight == source_shape_key.value:
                logger.debug(f"Same Value : {morph_bind.index} : {morph_bind.weight}")
            else:
                logger.debug(
                    f"Updated : {morph_bind.index} : {morph_bind.weight} -->> {source_shape_key.value}"
                )
                morph_bind.weight = source_shape_key.value

        return True

    return False


# ----------------------------------------------------------
#    Material
# ----------------------------------------------------------
def get_source_vrm1_expression_material4ui_list():
    """
    UI Listでアクティブになっているエクスプレションに登録されているMorph Target Bindの情報を取得する｡

    Returns
    -------
    dict[str,
        エクスプレッションに登録されたMorph Target Bindとインデックスのペアを格納したタプルのリストを
        対応するオブジェクト名をキーとして格納した辞書｡

        Memo : ReferenceVrm1MaterialColorBindPropertyGroup
               Vrm1TextureTransformBindPropertyGroup

    """

    # データ取得対象となる'morph_target_binds'から取得する｡
    active_item = get_active_expression()
    material_binds_dict = {}
    for n, color_bind in enumerate(active_item.material_color_binds):
        material_binds_dict.setdefault(color_bind.material, [[], []])[0].append((n))

    for n, transform_bind in enumerate(active_item.texture_transform_binds):
        material_binds_dict.setdefault(transform_bind.material, [[], []])[1].append((n))

    return material_binds_dict


def add_items2expression_material_ui_list() -> int:
    """
    Morph Target Bindの確認/設定を行なうUI Listの描画候補アイテムをコレクションプロパティに追加する｡
    UI Listのrows入力用にアイテム数を返す｡

    Returns
    -------
    int
        リストに表示するアイテム数｡

    """

    items = get_ui_vrm1_expression_material_prop()
    source_material_binds_dict = get_source_vrm1_expression_material4ui_list()
    items.clear()

    # マテリアル名をラベルとして関連付けられたColor/Transform Bindをグルーピングする｡
    for n, (material, bind_lists) in enumerate(source_material_binds_dict.items()):
        material_name = material.name if material else ""
        if n != 0:
            target_label = items.add()
            target_label.item_type[0] = True
            target_label.name = "Blank"

        target_label = items.add()
        target_label.item_type[0] = True
        target_label.name = material_name
        target_label.bind_material_name = material_name

        # Material Color Bindの登録する｡
        if bind_lists[0]:
            target_label = items.add()
            target_label.item_type[0] = True
            target_label.name = "Material Color"
            target_label.bind_material_name = material_name

        for index in bind_lists[0]:
            target_item = items.add()
            target_item.item_type[1] = True
            target_item.name = material_name
            target_item.bind_index = index

        # Transform Color Bindの登録する｡
        if bind_lists[1]:
            target_label = items.add()
            target_label.item_type[0] = True
            target_label.name = "Texture Transform"
            target_label.bind_material_name = material_name

        for index in bind_lists[1]:
            target_item = items.add()
            target_item.item_type[2] = True
            target_item.name = material_name
            target_item.bind_index = index

    return len(items)


def convert_str2color_bind_type(source_name: str) -> str:
    match source_name:
        case "lit_color":
            return "color"

        case "shade_color":
            return "shadeColor"

        case "emission_color":
            return "emissionColor"

        case "matcap_color":
            return "matcapColor"

        case "rim_color":
            return "rimColor"

        case "outline_color":
            return "outlineColor"


def get_same_type_material_color_bind(
    source_material: Material,
    source_type: str,
) -> PropertyGroup | None:
    """
    アクティブエクスプレションのMaterial Color Bindsの中に
    'source_material'を参照しているかつ'source_type'を指定しているものがあればそれを取得する｡

    Parameters
    ----------
    source_material : Material
        検索対象のマテリアル

    source_type: str
        検索対象のMaterial Color Bindタイプ

    Returns
    -------
    VrmAddon.Vrm1ExpressionPropertyGroup | None:
        'souce_material','source_type'と同じ値が設定されているMaterial Color Bind｡
        外胴データがなければNone｡

    """

    for color_bind in get_active_expression().material_color_binds:
        if color_bind.material == source_material and color_bind.type == source_type:
            return color_bind

    return None


def search_existing_material_color_bind_and_update(
    source_material: Material,
    material_color_binds: bpy_prop_collection,
) -> MToon1MaterialParameters:
    """
    'material_color_binds'内に'source_material'と関連付けられたColor Bindが
    存在するか否かを走査し､存在する場合値の更新する｡値が初期値の場合はColor Bindの削除を行なう｡
    また､Color Bindの新規作成判定に用いるための辞書を返す｡

    Parameters
    ----------
    source_material : Material
        検索対象のマテリアル

    material_color_binds : bpy_prop_collection
        処理対象となるMaterial Color Bind

    Returns
    -------
    MToon1MaterialParameters
        'source_material'に設定されたMToonパラメーターの値を格納した辞書｡
        MToonパラメーターが初期値の場合は値がNoneになる｡

    """

    mtoon_parameters_dict = get_mtoon_color_current_parameters(source_material)

    # 既に登録されているMaterial Color Bindがある場合は値の更新/削除を行なう｡
    for bind_type in mtoon_parameters_dict.keys():
        converted_bind_type = convert_str2color_bind_type(bind_type)
        if not (
            same_type_bind := get_same_type_material_color_bind(
                source_material, converted_bind_type
            )
        ):
            continue

        # MToonのパラメーターがデフォルト値である場合はColor Bindを削除する｡
        logger.debug(f"{same_type_bind.name} , {bind_type}")
        if not (current_value := mtoon_parameters_dict[bind_type]):
            logger.debug(f"Removed Bind -- {same_type_bind.name} : {bind_type}")
            remove_target_index = list(material_color_binds).index(same_type_bind)
            material_color_binds.remove(remove_target_index)

        # Color Bindの値を現在の値に更新する｡
        else:
            match bind_type:
                case "lit_color":
                    attr_name = "target_value"
                case _:
                    attr_name = "target_value_as_rgb"
            logger.debug(attr_name)

            target_value = getattr(same_type_bind, attr_name)
            if list(target_value) == current_value:
                logger.debug(f"Same Value : {same_type_bind}")
            else:
                logger.debug(
                    f"Updated : {source_material} : {list(target_value)} -->> {current_value}"
                )
                setattr(same_type_bind, attr_name, current_value)
            mtoon_parameters_dict[bind_type] = None

    return mtoon_parameters_dict


########################################################################################################################
def convert_str2transform_bind_type(source_name: str) -> str:
    match source_name:
        case "texture_scale":
            return "scale"

        case "texture_offset":
            return "offset"


def get_same_material_texture_transform_bind(
    source_material: Material,
) -> PropertyGroup | None:
    """
    アクティブエクスプレションのTexture Transform Bindsの中に
    'source_material'を参照しているものがあればそれを取得する｡

    Parameters
    ----------
    source_material : Material
        検索対象のマテリアル


    Returns
    -------
    VrmAddon.Vrm1TextureTransformBindPropertyGroup | None:
        参照マテリアルが'souce_material'であるTexture Transform Bind｡
        該当データがなければNone｡

    """

    for transform_bind in get_active_expression().texture_transform_binds:
        if transform_bind.material == source_material:
            return transform_bind

    return None


def search_existing_texture_transform_bind_and_update(
    source_material: Material,
    texture_transform_binds: bpy_prop_collection,
) -> MToon1MaterialParameters | None:
    """
    'texture_transform_binds'内に'source_material'と関連付けられたColor Bindが
    存在するか否かを走査し､存在する場合値の更新する｡値が初期値の場合はColor Bindの削除を行なう｡
    また､Color Bindの新規作成判定に用いるための辞書を返す｡

    Parameters
    ----------
    source_material : Material
        検索対象のマテリアル

    texture_transform_binds : bpy_prop_collection
        処理対象となるTexture Transform

    Returns
    -------
    MToon1MaterialParameters
        'source_material'に設定されたMToonパラメーターと値を格納した辞書｡
        MToonパラメーターが初期値の場合はNoneを返す｡

    """

    mtoon_parameters_dict = get_mtoon_transform_current_parameters(source_material)
    logger.debug(mtoon_parameters_dict)

    # 既に登録されているTexture Transform Bindがある場合は値の更新/削除を行なう｡
    if not (
        same_material_bind := get_same_material_texture_transform_bind(source_material)
    ):
        return mtoon_parameters_dict

    # MToonのパラメーターがデフォルト値である場合はColor Bindを削除する｡
    if not (
        mtoon_parameters_dict["texture_scale"]
        or mtoon_parameters_dict["texture_offset"]
    ):
        logger.debug(f"Remove Texture Transform Bind : {source_material.name}")
        remove_target_index = list(texture_transform_binds).index(same_material_bind)
        texture_transform_binds.remove(remove_target_index)

    # Color Bindの値を現在の値に更新する｡
    else:
        old_value = {
            "texture_scale": list(same_material_bind.scale),
            "texture_offset": list(same_material_bind.offset),
        }
        for parameter, new_value in mtoon_parameters_dict.items():
            logger.debug(old_value[parameter])
            logger.debug(new_value)
            if new_value == old_value[parameter] or new_value == None:
                logger.debug(f"Same Value : {parameter}")
                continue

            converted_parameter_name = convert_str2transform_bind_type(parameter)
            logger.debug(
                f"Updated : {converted_parameter_name} : {old_value[parameter]} -->> {new_value}"
            )
            setattr(same_material_bind, converted_parameter_name, new_value)

        mtoon_parameters_dict = None

    return mtoon_parameters_dict


def set_mtoon1_colors_from_bind(
    color_bind: ReferenceVrm1MaterialColorBindPropertyGroup,
):
    """
    引数'color_bind'で参照されているマテリアルのMToon1パラメーターにそのcolor_bindの値をセットする

    Parameters
    ----------
    color_bind : ReferenceVrm1MaterialColorBindPropertyGroup
        処理対象のマテリアルを定義しているMaterial Color Bind

    """

    if not (target_material := color_bind.material):
        return
    mtoon1 = target_material.vrm_addon_extension.mtoon1
    mtoon1_attr_name = get_mtoon_attr_name_from_bind_type(color_bind.type)

    # Lit Colorの場合とそれ以外の場合で参照する値を変更する｡
    match color_bind.type:
        case "color":
            set_value = color_bind.target_value
        case _:
            set_value = color_bind.target_value_as_rgb

    set_attr_from_strings(mtoon1, mtoon1_attr_name, set_value)


def set_mtoon1_texture_transform_from_bind(
    transform_bind: ReferenceVrm1TextureTransformBindPropertyGroup,
):
    """
    引数'transform_bind'で参照されているマテリアルのMToon1パラメーターにそのcolor_bindの値をセットする

    Parameters
    ----------
    transform_bind : ReferenceVrm1TextureTransformBindPropertyGroup
        処理対象のマテリアルを定義しているTexture Transform Bind


    """
    if not (target_material := transform_bind.material):
        return
    mtoon1 = target_material.vrm_addon_extension.mtoon1

    set_attr_from_strings(
        mtoon1, MTOON_ATTRIBUTE_NAMES["texture_scale"], transform_bind.scale
    )
    set_attr_from_strings(
        mtoon1, MTOON_ATTRIBUTE_NAMES["texture_offset"], transform_bind.offset
    )
