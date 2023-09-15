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


from ..addon_constants import (
    FIRST_PERSON_ANNOTATION_TYPES,
)

from ..property_groups import (
    get_scene_vrm0_first_person_prop,
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


def get_source_vrm1_annotation(mode: Literal["UI", "OPERATOR"]) -> list[PropertyGroup]:
    """
    コンテクストのシーン内オブジェクトの中から､VRM Extension内のFirst Personの値が
    選択されたFirst Person Ui Modeと同一のものを抽出したリストを返す｡

    Parameters
    ----------
    mode : Literal["UI", "OPERATOR"]
        UI用として要素をフィルタリングして取得するのか､オペレーター用に全ての要素を取得するのかを選択する｡

    Returns
    -------
    list[Object]
        VRM Extensionで設定されたFirst Personの値がUI Modeと同じであるオブジェクトを格納したリスト｡

    """
    # VRM ExtensionのFirst Personのプロパティと現在のUI Listのモードを取得する｡
    first_person_prop = get_scene_vrm0_first_person_prop()
    annotation_type_filter = {first_person_prop.annotation_type}
    # 選択タイプによるフィルタリングの有無｡
    if not first_person_prop.is_filtering_by_type:
        annotation_type_filter |= FIRST_PERSON_ANNOTATION_TYPES

    ext_first_person = get_vrm_extension_property("FIRST_PERSON")

    # UI Listに表示する対象オブジェクトをリストに格納する
    match mode:
        case "UI":
            source_annotation_list = [
                i
                for i in ext_first_person.mesh_annotations
                if i.type in annotation_type_filter
                and not i.node.mesh_object_name == ""
            ]
        case "OPERATOR":
            source_annotation_list = [i for i in ext_first_person.mesh_annotations]

        case _:
            source_annotation_list = []

    return source_annotation_list
