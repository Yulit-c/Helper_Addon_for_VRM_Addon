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
    get_scene_vrm1_first_person_prop,
    get_ui_vrm1_first_person_prop,
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


def vrm1_get_source_annotation(mode: Literal["UI", "OPERATOR"]) -> list[PropertyGroup]:
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
    first_person_prop = get_scene_vrm1_first_person_prop()
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


def vrm1_add_items2annotation_ui_list() -> int:
    """
    First Personの確認/設定を行なうUI Listの描画候補アイテムをコレクションプロパティに追加する｡
    UI Listのrows入力用にアイテム数を返す｡

    Returns
    -------
    int
        リストに表示するアイテム数｡

    """
    items = get_ui_vrm1_first_person_prop()

    # Current Sceneに存在するオブジェクトから対象オブジェクトを取得する｡
    source_annotation_list = vrm1_get_source_annotation("UI")

    # コレクションプロパティの初期化処理｡
    items.clear()

    for annotation in source_annotation_list:
        new_item = items.add()
        new_item.name = annotation.node.mesh_object_name

    return len(source_annotation_list)


def vrm1_search_same_name_mesh_annotation(object_name: str) -> PropertyGroup:
    """
    引数で受け取ったオブジェクト名と一致するMesh AnnotationをTarget ArmatureのVRM Extensionから取得する。

    Parameters
    ----------
    object_name : str
        検索対象となるオブジェクト名｡

    Returns
    -------
    PropertyGroup
        VRM Extensionから取得されたオブジェクト名と一致したMesh Annotation｡

    """
    if annotations := [
        i
        for i in vrm1_get_source_annotation("OPERATOR")
        if i.node.mesh_object_name == object_name
    ]:
        return annotations[0]


def vrm1_remove_mesh_annotation(source_object_name: str):
    """
    引数で受け取ったオブジェクト名を用いてUI List内のアクティブアイテムインデックスを取得してそのアクティブアイテムを削除する｡

    Parameters
    ----------
    source_object_name : str
        インデックスを取得したいアイテムの名前｡

    """
    mesh_annotations = get_vrm_extension_property("FIRST_PERSON").mesh_annotations
    try:
        mesh_annotations.remove(
            [i.node.mesh_object_name for i in mesh_annotations].index(
                source_object_name
            )
        )
        logger.debug(f"Remove Mesh Annotation : {source_object_name}")
    except:
        pass


def vrm1_sort_mesh_annotations():
    """
    現在のMesh Annotationsの状態を取得した後に'type'->'node.mesh_object_name'の順にソートする｡
    その際重複したオブジェクトは除外される｡

    """
    # 現在のMesh Annotationsの状態を取得した後にリストをソートする｡
    mesh_annotations = get_vrm_extension_property("FIRST_PERSON").mesh_annotations
    seen = []
    current_annotations_list = [
        (i.node.mesh_object_name, i.type)
        for i in mesh_annotations
        if i.node.mesh_object_name not in seen
        and not seen.append(i.node.mesh_object_name)
    ]
    current_annotations_list.sort(key=lambda x: (x[1], x[0]))

    # 一旦要素をクリアした後にソート済みのリストから再登録する｡
    mesh_annotations.clear()
    for name, type in current_annotations_list:
        new_item = mesh_annotations.add()
        new_item.node.mesh_object_name = name
        new_item.type = type
