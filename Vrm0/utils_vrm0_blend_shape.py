if "bpy" in locals():
    import importlib

    reloadable_modules = [
        "preparation_logger",
        "addon_classes",
        "addon_constants",
        "utils_common",
        "utils_vrm_base",
    ]

    for module in reloadable_modules:
        if module in locals():
            importlib.reload(locals()[module])

else:
    from ..Logging import preparation_logger
    from .. import addon_classes
    from .. import addon_constants
    from .. import utils_common
    from .. import utils_vrm_base


from typing import (
    Optional,
    Any,
)

import bpy


from ..addon_classes import (
    ReferenceVrm0BlendShapeMasterPropertyGroup,
    ReferenceVrm0BlendShapeGroupPropertyGroup,
    ReferenceVrm0BlendShapeBindPropertyGroup,
    ReferenceVrm0MaterialValueBindPropertyGroup,
)


from ..preferences import (
    get_addon_collection_name,
)

from ..property_groups import (
    VRMHELPER_WM_vrm0_blend_shape_bind_list_items,
    VRMHELPER_WM_vrm0_blend_shape_material_list_items,
    # ----------------------------------------------------------
    get_target_armature,
    get_target_armature_data,
    get_vrm0_active_index_prop,
    # ---------------------------------------------------------------------------------
    get_scene_vrm0_mtoon_stored_prop,
    get_ui_vrm0_blend_shape_bind_prop,
    get_ui_vrm0_blend_shape_material_prop,
)

from ..utils_common import (
    get_attr_from_strings,
    set_attr_from_strings,
    reset_shape_keys_value,
)

from ..utils_vrm_base import (
    get_vrm0_extension_property_blend_shape,
    serach_vrm_shader_node,
    check_vrm_material_mode,
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


def get_active_blend_shape() -> Optional[ReferenceVrm0BlendShapeGroupPropertyGroup]:
    blend_shape_master = get_vrm0_extension_property_blend_shape()
    active_index = blend_shape_master.active_blend_shape_group_index
    if not (blend_shape_groups := blend_shape_master.blend_shape_groups):
        return

    active_blend_shape = blend_shape_groups[active_index]
    return active_blend_shape


# ----------------------------------------------------------
#    Binds
# ----------------------------------------------------------
def vrm0_get_source_vrm0_blend_shape_bind4ui_list() -> (
    dict[str, list[tuple[ReferenceVrm0BlendShapeBindPropertyGroup, int]]]
):
    """
    UI Listでアクティブになっているブレンドシェイプに登録されているBindsの情報を取得する｡

    Returns
    -------
    dict[str, list[tuple[ReferenceVrm0BlendShapeBindPropertyGroup, int]]]
        ブレンドシェイプに登録されたBindとインデックスのペアを格納したタプルのリストを
        対応するオブジェクト名をキーとして格納した辞書｡

    """

    # データ取得対象となる'morph_target_binds'から取得する｡
    active_item = get_active_blend_shape()
    binds_dict = {}
    for n, bind in enumerate(active_item.binds):
        bind: ReferenceVrm0BlendShapeBindPropertyGroup = bind
        binds_dict.setdefault(bind.mesh.mesh_object_name, []).append((bind, n))

    return binds_dict


def vrm0_add_items2blend_shape_bind_ui_list() -> int:
    """
    Bindsの確認/設定を行なうUI Listの描画候補アイテムをコレクションプロパティに追加する｡
    UI Listのrows入力用にアイテム数を返す｡

    Returns
    -------
    int
        リストに表示するアイテム数｡

    """

    items = get_ui_vrm0_blend_shape_bind_prop()
    source_binds_dict = vrm0_get_source_vrm0_blend_shape_bind4ui_list()
    items.clear()

    for obj_name, bind_info in source_binds_dict.items():
        target_item: VRMHELPER_WM_vrm0_blend_shape_bind_list_items = items.add()
        target_item.item_type[0] = True
        target_item.name = obj_name

        for bind, index in bind_info:
            target_item: VRMHELPER_WM_vrm0_blend_shape_bind_list_items = items.add()
            target_item.item_type[1] = True
            target_item.name = obj_name
            target_item.shape_key_name = bind.index
            target_item.bind_index = index

    return len(items)


def vrm0_get_active_bind_in_ui() -> Optional[VRMHELPER_WM_vrm0_blend_shape_bind_list_items]:
    """
    BindsのUI List内でアクティブになっている要素を返す｡UI Listがからの場合はNoneを返す

    Returns
    -------
    Optional[VRMHELPER_WM_vrm0_blend_shape_bind_list_items]
        UI List内のアクティブ要素､またはNone

    """
    if not (bind_ui_list := get_ui_vrm0_blend_shape_bind_prop()):
        return

    active_index = get_vrm0_active_index_prop("blend_shape_bind")
    active_bind = bind_ui_list[active_index]
    return active_bind


# ----------------------------------------------------------
#    Material
# ----------------------------------------------------------
def vrm0_get_source_vrm0_blend_shape_material4ui_list() -> (
    dict[str, list[tuple[ReferenceVrm0MaterialValueBindPropertyGroup, int]]]
):
    """
    UI Listでアクティブになっているブレンドシェイプに登録されているMaterial Valuesの情報を取得する｡

    Returns
    -------
    dict[str, list[tuple[ReferenceVrm0MaterialValueBindPropertyGroup, int]]]
        ブレンドシェイプに登録されたMaterial Valuesとインデックスのペアを格納したタプルのリストを
        対応するオブジェクト名をキーとして格納した辞書｡


    """

    # データ取得対象となる'morph_target_binds'から取得する｡
    active_blend_shape = get_active_blend_shape()
    material_value_dict = {}
    for n, mat_value in enumerate(active_blend_shape.material_values):
        mat_value: ReferenceVrm0MaterialValueBindPropertyGroup = mat_value
        material = mat_value.material if mat_value.material else "Non Selected"
        # material = mat_value.material
        material_value_dict.setdefault(material, []).append((mat_value, n))

    return material_value_dict


def vrm0_add_items2blend_shape_material_ui_list() -> int:
    """
    Material Valueの確認/設定を行なうUI Listの描画候補アイテムをコレクションプロパティに追加する｡
    UI Listのrows入力用にアイテム数を返す｡

    Returns
    -------
    int
        リストに表示するアイテム数｡

    """

    items = get_ui_vrm0_blend_shape_material_prop()
    source_material_value_dict = vrm0_get_source_vrm0_blend_shape_material4ui_list()
    items.clear()

    # マテリアル名をラベルとして関連付けられたMaterial Valueをグルーピングする｡
    for n, value_info in enumerate(source_material_value_dict.items()):
        material, value_list = value_info
        mat_value: ReferenceVrm0MaterialValueBindPropertyGroup = value_list[0]

        # 先頭でない場合は空白行挿入
        if n != 0:
            target_label: VRMHELPER_WM_vrm0_blend_shape_material_list_items = items.add()
            target_label.item_type[0] = True
            target_label.name = "Blank"

        # マテリアルが参照されていない場合は専用のラベル
        if isinstance(material, bpy.types.Material):
            label_name = material.name
            material_name = material.name
            item_type = (1, 0, 0, 0)
        else:
            label_name = "Not Selected"
            material_name = ""
            item_type = (1, 0, 0, 1)

        # マテリアル毎のグルーピング用ラベルの登録
        target_label = items.add()
        target_label.item_type = tuple(map(bool, item_type))
        target_label.name = label_name
        target_label.material_name = material_name

        # マテリアル毎に紐付けられているMaterial Valueの登録をする｡
        for mat_value, index in value_list:
            mat_value: ReferenceVrm0MaterialValueBindPropertyGroup = mat_value
            target_item: VRMHELPER_WM_vrm0_blend_shape_material_list_items = items.add()
            target_item.value_index = index
            target_item.material_name = material_name

            # UI List用アイテム登録の間はUpdateコールバックをロックする｡
            target_item.is_locked_color = True
            target_item.is_locked_uv_scale = True
            target_item.is_locked_uv_offset = True

            # マテリアルがMToonである場合はタグ付け
            target_item.material_type = check_vrm_material_mode(mat_value.material)

            # マテリアルが参照されていない場合のタグ付け
            if item_type[3]:
                target_item.material_type = "NONE"
                target_item.item_type[3] = True
                continue

            try:
                # Material Colorの場合のタグ付け
                if "Color" in mat_value.property_name:
                    target_item.item_type[1] = True
                    target_item.name = "Color"
                    source_color = (
                        mat_value.target_value[0].value,
                        mat_value.target_value[1].value,
                        mat_value.target_value[2].value,
                        mat_value.target_value[3].value,
                    )
                    target_item.material_color = source_color

                # UV Coordinateの場合のタグ付け7
                else:
                    target_item.item_type[2] = True
                    target_item.name = "UV"
                    source_scale = (
                        mat_value.target_value[0].value,
                        mat_value.target_value[1].value,
                    )
                    target_item.uv_scale = source_scale

                    source_offset = (
                        mat_value.target_value[2].value,
                        mat_value.target_value[3].value,
                    )
                    target_item.uv_offset = source_offset

            except:
                pass

            target_item.is_locked_color = False
            target_item.is_locked_uv_scale = False
            target_item.is_locked_uv_offset = False

    return len(items)


# ----------------------------------------------------------
#    Bind
# ----------------------------------------------------------
def get_same_value_existing_bind(
    obj_name: str, shape_key_name: str
) -> Optional[ReferenceVrm0BlendShapeBindPropertyGroup]:
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
    Optional[ReferenceVrm1MorphTargetBindPropertyGroup]
        'mesh_object_name'と'indes'の値が引数と同じMorpht Target Bind｡
        該当データがなければNone｡
    """

    active_blend_shape = get_active_blend_shape()
    for bind in active_blend_shape.binds:
        bind: ReferenceVrm0BlendShapeBindPropertyGroup = bind
        if bind.mesh.mesh_object_name == obj_name and bind.index == shape_key_name:
            return bind
    return None


def search_existing_bind_and_update(
    source_object: bpy.types.Object,
    source_shape_key: bpy.types.ShapeKey,
    binds: bpy.types.bpy_prop_collection,
) -> bool:
    """
    'binds'内に'source_object'と'source_shape_key'のペアが登録されたBindが
    存在するか否かを走査し､存在する場合値の更新する｡値が0の場合はBindの削除を行なう｡
    また､存在したか否かの判定を返す｡

    Parameters
    ----------
    source_object : Object
        検索対象のオブジェクト
    source_shape_key : ShapeKey
        検索対象のシェイプキー
    binds : bpy_prop_collection
        処理対象となるBinds

    Returns
    -------
    bool
        該当するMorph Bindが存在した場合はTrue,存在しなかった場合はFalse｡
    """

    if morph_bind := get_same_value_existing_bind(source_object.name, source_shape_key.name):
        if source_shape_key.value == 0:
            logger.debug(f"Remove 0 Value morph_Bind : {morph_bind.index}")
            binds.remove(list(binds).index(morph_bind))

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


def vrm0_get_active_material_value_in_ui() -> Optional[VRMHELPER_WM_vrm0_blend_shape_material_list_items]:
    """
    Material ValueのUI List内でアクティブになっている要素を返す｡UI Listがからの場合はNoneを返す

    Returns
    -------
    Optional[VRMHELPER_WM_vrm0_blend_shape_material_list_items]
        UI List内のアクティブ要素､またはNone
    """

    if not (material_value_ui_list := get_ui_vrm0_blend_shape_material_prop()):
        return

    active_index = get_vrm0_active_index_prop("BLEND_SHAPE_MATERIAL")
    active_value = material_value_ui_list[active_index]
    return active_value
