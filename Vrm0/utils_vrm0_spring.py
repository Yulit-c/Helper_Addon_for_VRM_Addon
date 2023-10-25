if "bpy" in locals():
    import importlib

    reloadable_modules = [
        "preparation_logger",
        "addon_constants",
        "utils_common",
    ]

    for module in reloadable_modules:
        if module in locals():
            importlib.reload(locals()[module])

else:
    from ..Logging import preparation_logger
    from .. import addon_constants
    from .. import utils_common

import re
from typing import Literal
import bpy
from bpy.types import (
    PropertyGroup,
)


# from ..addon_constants import (
#     VRM0_FIRST_PERSON_ANNOTATION_TYPES,
# )

from ..addon_classes import (
    ReferenceVrm0SecondaryAnimationGroupPropertyGroup,
    ReferenceVrm0SecondaryAnimationColliderGroupPropertyGroup,
    ReferenceVrm0SecondaryAnimationPropertyGroup,
)

from ..property_groups import (
    get_target_armature,
    get_target_armature_data,
    get_ui_vrm0_collider_group_prop,
    get_ui_vrm0_spring_prop,
)

from ..utils_vrm_base import (
    get_vrm_extension_property,
)


"""----------------------------------------------------
    Logger
-----------------------------------------------------"""
from ..Logging.preparation_logger import preparating_logger

logger = preparating_logger(__name__)
#######################################################


"""---------------------------------------------------------
    Function
---------------------------------------------------------"""


# ----------------------------------------------------------
#    Collider Groups
# ----------------------------------------------------------
def get_source_vrm0_collider_groups() -> (
    dict[str, list[tuple[int, ReferenceVrm0SecondaryAnimationColliderGroupPropertyGroup]]]
):
    """
    Target ArmatureのVRM Extension内のVRM1のコライダーと対応ボーンの情報を格納した辞書を返す｡

    Returns
    -------
    dict[str, list[tuple[int, ReferenceVrm1ColliderPropertyGroup]]]
        コライダーとインデックスを格納したタプルのリストを､対応するボーン名をキーとして格納した辞書｡

    """

    # VRM ExtensionのCollidersを取得する
    cojllider_groups = get_vrm_extension_property("COLLIDER_GROUP")

    # VRM1のSpring Bone Colliderをリストに格納して返す｡
    collider_groups_dict = {}
    for n, collider_group in enumerate(cojllider_groups):
        collider_group: ReferenceVrm0SecondaryAnimationColliderGroupPropertyGroup = collider_group
        collider_groups_dict.setdefault(collider_group.node.bone_name, [])
        # n : vrm extension cojllider_groups内でのインデックス｡
        collider_groups_dict[collider_group.node.bone_name].append((n, collider_group))

    sort_order = [i.name for i in get_target_armature_data().bones if i.name in collider_groups_dict.keys()]

    def get_index(element):
        if element[0] == "":
            result = -1
        else:
            result = sort_order.index(element[0])
        return result

    sorted_collider_groups = dict(sorted(collider_groups_dict.items(), key=get_index))

    return sorted_collider_groups


def add_items2collider_group_ui_list() -> int:
    """
    VRM0のSpring Bone_Collider Groupの確認/設定を行なうUI Listの描画候補アイテムをコレクションプロパティに追加する｡
    UI Listのrows入力用にアイテム数を返す｡

    Returns
    -------
    int
        リストに表示するアイテム数｡

    """

    # wm_prop = get_addon_prop_group("WM")
    # items = wm_prop.collider_list_items4custom_filter
    items = get_ui_vrm0_collider_group_prop()

    source_collider_dict = get_source_vrm0_collider_groups()
    bones = get_target_armature_data().bones

    # コレクションプロパティの初期化処理｡
    items.clear()
