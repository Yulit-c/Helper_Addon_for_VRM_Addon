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
    BlendShapeCandidateUIList,
)


from ..preferences import (
    get_addon_collection_name,
)

from ..property_groups import (
    VRMHELPER_WM_vrm0_blend_shape_material_list_items,
    # ----------------------------------------------------------
    VRMHELPER_WM_vrm0_blend_shape_list_items,
    get_target_armature,
    get_target_armature_data,
    get_vrm0_active_index_prop,
    get_ui_vrm0_blend_shape_prop,
)

from ..utils_common import (
    get_attr_from_strings,
    set_attr_from_strings,
    reset_shape_keys_value,
)

from ..utils_vrm_base import (
    MToon1MaterialParameters,
    MTOON1_ATTRIBUTE_NAMES,
    get_vrm0_extension_property_blend_shape,
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


def get_source_vrm0_blend_shape4ui_list() -> (
    list[ReferenceVrm0BlendShapeGroupPropertyGroup]
):
    """
    Target Armatureに登録されたブレンドシェイプ･プロキシーのリストを返す｡

    Returns
    -------
    list[ReferenceVrm0BlendShapeGroupPropertyGroup]
        取得された全プロキシーを格納したリスト｡
    """

    blend_shape_master = get_vrm0_extension_property_blend_shape()
    blend_shape_groups = list(blend_shape_master.blend_shape_groups)
    return blend_shape_groups


def add_items2blend_shapes_ui_list() -> int:
    """
    Blend Shapeの確認/設定を行なうUI Listの描画候補アイテムをコレクションプロパティに追加する｡
    UI Listのrows入力用にアイテム数を返す｡

    Returns
    -------
    int
        リストに表示するアイテム数｡
    """

    blend_shapes = get_source_vrm0_blend_shape4ui_list()

    items = get_ui_vrm0_blend_shape_prop()
    items.clear()

    # Blend Shapeの情報を追加
    for blend_shape in blend_shapes:
        bs: ReferenceVrm0BlendShapeGroupPropertyGroup = blend_shape
        new_item: VRMHELPER_WM_vrm0_blend_shape_list_items = items.add()
        new_item.name = bs.name
        new_item.preset_name = bs.preset_name
        new_item.has_morph_bind = bool(bs.binds)
        new_item.has_material_bind = bool(bs.material_values)

    return len(items)
