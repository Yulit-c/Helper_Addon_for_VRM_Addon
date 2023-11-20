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
from typing import (
    Literal,
    Optional,
)
import bpy
from bpy.types import (
    PropertyGroup,
)


# from ..addon_constants import (
#     VRM0_FIRST_PERSON_ANNOTATION_TYPES,
# )

from ..addon_classes import (
    ReferenceStringPropertyGroup,
    ReferenceBonePropertyGroup,
    ReferencerVrm0SecondaryAnimationColliderPropertyGroup,
    ReferenceVrm0SecondaryAnimationGroupPropertyGroup,
    ReferenceVrm0SecondaryAnimationColliderGroupPropertyGroup,
    ReferenceVrm0SecondaryAnimationPropertyGroup,
)

from ..preferences import get_addon_preferences

from ..property_groups import (
    VRMHELPER_WM_vrm0_collider_group_list_items,
    VRMHELPER_WM_vrm0_spring_bone_list_items,
    VRMHELPER_WM_vrm0_operator_spring_collider_group_list_items,
    VRMHELPER_WM_vrm0_operator_spring_bone_group_list_items,
    VRMHELPER_WM_vrm0_spring_linked_collider_group_list_items,
    get_target_armature,
    get_target_armature_data,
    get_ui_vrm0_collider_group_prop,
    get_ui_vrm0_spring_prop,
    get_ui_bone_group_prop,
    get_ui_vrm0_linked_collider_group_prop,
    get_ui_vrm0_operator_collider_group_prop,
    get_ui_vrm0_operator_spring_bone_group_prop,
    get_vrm0_active_index_prop,
)

from ..utils_common import (
    get_parent_count,
)

from ..utils_vrm_base import (
    get_vrm_extension_property,
    get_vrm0_extension_collider_group,
    get_vrm0_extension_spring_bone_group,
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
    Target ArmatureのVRM Extension内のVRM0のコライダーグループと対応ボーンの情報を格納した辞書を返す｡

    Returns
    -------
    dict[str, list[tuple[int, ReferenceVrm1ColliderPropertyGroup]]]
        コライダーグループとインデックスを格納したタプルのリストを､対応するボーン名をキーとして格納した辞書｡

    """

    # VRM ExtensionのCollidersを取得する
    collider_groups = get_vrm_extension_property("COLLIDER_GROUP")

    # VRM1のSpring Bone Colliderをリストに格納して返す｡
    collider_groups_dict = {}
    collider_group: ReferenceVrm0SecondaryAnimationColliderGroupPropertyGroup
    for n, collider_group in enumerate(collider_groups):
        collider_groups_dict.setdefault(collider_group.node.bone_name, [])
        # n : vrm extension collider_groups内でのインデックス｡
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


def vrm0_add_items2collider_group_ui_list() -> int:
    """
    VRM0のSpring Bone_Collider Groupの確認/設定を行なうUI Listの描画候補アイテムをコレクションプロパティに追加する｡
    UI Listのrows入力用にアイテム数を返す｡

    Returns
    -------
    int
        リストに表示するアイテム数｡

    """

    items = get_ui_vrm0_collider_group_prop()

    source_collider_dict = get_source_vrm0_collider_groups()
    target_armature_data = get_target_armature_data()
    bones = target_armature_data.bones

    # コレクションプロパティの初期化処理｡
    items.clear()

    # コレクションプロパティに先頭ラベル(Armature名表示用)とColliderの各情報を追加する｡
    label: VRMHELPER_WM_vrm0_collider_group_list_items = items.add()
    label.item_type[0] = True
    label.name = target_armature_data.name

    for k, v in source_collider_dict.items():
        new_item: VRMHELPER_WM_vrm0_collider_group_list_items = items.add()
        new_item.item_type[1] = True
        # ボーン名が空文字であれば次のキーに移行｡
        if not k:
            parent_count = 0
            new_item.bone_name = "Not Defined"
            new_item.name = ""
        else:
            new_item.name = k
            new_item.bone_name = k
            _, parent_count = get_parent_count(bones[k], 0)
            new_item.parent_count = (parent_count := parent_count + 1)

        # コライダーグループをコレクションプロパティに追加する｡
        group: ReferenceVrm0SecondaryAnimationColliderGroupPropertyGroup
        for n, group in v:
            new_group: VRMHELPER_WM_vrm0_collider_group_list_items = items.add()
            new_group.name = f"{k} {group.name}"
            new_group.group_name = group.name
            new_group.item_type[2] = True
            new_group.bone_name = k
            new_group.group_index = n
            new_group.parent_count = parent_count + 1

            # コライダーグループに関連付けられたコライダーを登録する｡
            collider: ReferencerVrm0SecondaryAnimationColliderPropertyGroup
            for m, collider in enumerate(group.colliders):
                new_collider: VRMHELPER_WM_vrm0_collider_group_list_items = items.add()
                new_collider.item_type[3] = True
                new_collider.bone_name = k
                if collider.bpy_object:
                    new_collider.collider_name = collider.bpy_object.name
                else:
                    new_collider.collider_name = "Not Defined"

                new_collider.group_index = n
                new_collider.collider_index = m
                new_collider.name = f"{k} {collider.bpy_object.name}"
                new_collider.parent_count = parent_count + 2

    return len(items)


def remove_vrm0_collider_when_removed_collider_group(collider_group_index: int):
    """
    VRM0のコライダーグループが削除される時に､それを参照しているコライダーオブジェクト(Empty Object)を削除する｡

    Parameters
    ----------
    collider_group_index : int
        削除されるコライダーグループのインデックス｡

    """

    collider_groups = get_vrm_extension_property("COLLIDER_GROUP")
    target_group: ReferenceVrm0SecondaryAnimationColliderGroupPropertyGroup = collider_groups[
        collider_group_index
    ]
    for collider in target_group.colliders:
        collider: ReferencerVrm0SecondaryAnimationColliderPropertyGroup = collider
        if not (collider_object := bpy.data.objects.get(collider.bpy_object.name)):
            continue
        bpy.data.objects.remove(collider_object)


def get_active_list_item_in_collider_group() -> Optional[VRMHELPER_WM_vrm0_collider_group_list_items]:
    """
    UIリストのアクティブインデックスに対応したコライダーグループを取得する｡

    Returns
    -------
    Optional[VRMHELPER_WM_vrm0_collider_group_list_items]
        取得されたコライダーグループ｡取得できなければNone｡

    """
    if collider_group_list := get_ui_vrm0_collider_group_prop():
        return collider_group_list[get_vrm0_active_index_prop("COLLIDER_GROUP")]
    else:
        return None


def remove_vrm0_collider_by_selected_object(
    source_object: bpy.types.Object,
) -> Optional[ReferenceVrm0SecondaryAnimationColliderGroupPropertyGroup]:
    """
    VRM0 collider_group内にある､引数'collider_object'と同一のオブジェクトが登録されたコライダを消去する｡

    Parameters
    ----------
    source_object : Object
        削除対象となるオブジェクト名｡

    Returns
    -------
    Optional[ReferenceVrm0SecondaryAnimationColliderGroupPropertyGroup]
        この関数内でコライダーが削除されたコライダーグループ｡

    """

    collider_group = get_vrm_extension_property("COLLIDER_GROUP")
    target_group = None
    target_collider = None

    # 全コライダーグループの中から'source_object'に対応するコライダーを取得する｡
    group: ReferenceVrm0SecondaryAnimationColliderGroupPropertyGroup
    for group in collider_group:
        collider: ReferencerVrm0SecondaryAnimationColliderPropertyGroup
        for n, collider in enumerate(group.colliders):
            if collider.bpy_object == source_object:
                target_group = group
                target_collider = collider
                index = n
    if not target_collider:
        return

    # 取得したコライダーとエンプティオブジェクトを削除する｡
    target_group.colliders.remove(index)
    bpy.data.objects.remove(source_object, do_unlink=True)

    return target_group


def vrm0_remove_collider_group_in_springs(
    removed_collider_group_name: str,
):
    bone_groups = get_vrm_extension_property("SPRING")

    bone_group: ReferenceVrm0SecondaryAnimationGroupPropertyGroup
    for bone_group in bone_groups:
        collider_group: ReferenceStringPropertyGroup
        for collider_group in bone_group.collider_groups:
            if collider_group.value == removed_collider_group_name:
                index = list(bone_group.collider_groups).index(collider_group)
                bone_group.collider_groups.remove(index)


# ----------------------------------------------------------
#    Spring Bone Group
# ----------------------------------------------------------
def get_source_vrm0_springs() -> tuple[ReferenceVrm0SecondaryAnimationGroupPropertyGroup]:
    # VRM ExtensionのSpring Bone Groupsを取得する
    ext_bone_groups = get_vrm_extension_property("SPRING")

    # VRM1のSpring Bone Groupsをリストに格納して返す｡
    bone_groups = tuple(ext_bone_groups)

    return bone_groups


def vrm0_add_items2spring_ui_list() -> int:
    """
    VRM0のSpring Bone_Groupの確認/設定を行なうUI Listの描画候補アイテムをコレクションプロパティに追加する｡
    UI Listのrows入力用にアイテム数を返す｡

    Returns
    -------
    int
        リストに表示するアイテム数｡
    """
    bone_groups = get_source_vrm0_springs()
    items = get_ui_vrm0_spring_prop()

    # コレクションプロパティの初期化処理｡
    items.clear()

    for n, bone_group in enumerate(bone_groups):
        comment = bone_group.comment
        if n > 0:
            # 2つ目以降のアイテムの場合はブランク行を追加する｡
            new_label: VRMHELPER_WM_vrm0_spring_bone_list_items = items.add()
            new_label.item_type[0] = True
            new_label.name = comment
            new_label.item_name = ""
            new_label.item_indexes = (0, 0)

        # 登録されているBone Groupを追加する｡
        new_group: VRMHELPER_WM_vrm0_spring_bone_list_items = items.add()
        new_group.item_type[1] = True
        new_group.name = comment
        new_group.item_name = comment
        new_group.bone_group_name = comment
        new_group.item_indexes = (n, 0)

        # 登録されているBoneをアイテムに追加する｡
        bone: ReferenceBonePropertyGroup
        for m, bone in enumerate(bone_group.bones):
            new_bone: VRMHELPER_WM_vrm0_spring_bone_list_items = items.add()
            new_bone.item_type[2] = True
            new_bone.name = f"{comment} {bone.bone_name}"
            new_bone.item_name = bone.bone_name
            new_bone.bone_group_name = comment
            new_bone.item_indexes = (n, m)

    return len(items)


def vrm0_get_active_list_item_in_spring() -> Optional[VRMHELPER_WM_vrm0_spring_bone_list_items]:
    """
    UIリストのアクティブインデックスに対応したスプリングボーングループを取得する｡

    Returns
    -------
    Optional[VRMHELPER_WM_vrm0_spring_bone_list_items]
        取得されたスプリングボーングループ｡取得できなければNone｡

    """
    if bone_group_list := get_ui_vrm0_spring_prop():
        return bone_group_list[get_vrm0_active_index_prop("BONE_GROUP")]
    return None


def get_source_vrm0_linked_collider_groups() -> tuple[int, bpy.types.bpy_prop_collection]:
    """
    Target ArmatureのVRM Extension内のVRM0Spring Bone Groupに登録されたCollider Groupを取得する｡

    Returns
    -------
    tuple[int, bpy.types.bpy_prop_collection]
        UIリストでアクティブになSporing Bone GroupのインデックスとSpring Bone Groupにリンクされた
        Collider Groupのコレクションを格納したタプル｡

    """

    # UIリスト上のアクティブアイテムを取得する｡
    if not (active_item := vrm0_get_active_list_item_in_spring()):
        return

    # アクティブアイテムがラベルである場合はNoneを返す｡
    if active_item.item_type[0]:
        return

    # アクティブアイテムがBone Group/Boneである場合はリンクされたCollider Groupsを取得する｡
    source_index = active_item.item_indexes[0]
    spring_bone_groups = get_vrm0_extension_spring_bone_group()
    source_bone_group: ReferenceVrm0SecondaryAnimationGroupPropertyGroup
    source_bone_group = spring_bone_groups[source_index]
    linked_collider_groups = source_bone_group.collider_groups

    return (source_index, linked_collider_groups)


def vrm0_add_items2linked_collider_group_ui_list() -> int:
    """
    VRM0のSpring Bone_Groupの確認/設定を行なうUI Listの描画候補アイテムをコレクションプロパティに追加する｡
    UI Listのrows入力用にアイテム数を返す｡

    Returns
    -------
    int
        リストに表示するアイテム数｡
    """

    # UIリストに登録する候補のデータを取得して展開する｡
    if not (linked_collider_groups := get_source_vrm0_linked_collider_groups()):
        return
    source_index, collider_groups = linked_collider_groups

    items = get_ui_vrm0_linked_collider_group_prop()
    # コレクションプロパティの初期化処理｡
    items.clear()

    # 全てのCollider Groupをアイテムとして追加する｡
    new_cg: VRMHELPER_WM_vrm0_spring_linked_collider_group_list_items
    cg: ReferenceStringPropertyGroup
    for n, cg in enumerate(collider_groups):
        new_cg = items.add()
        new_cg.item_type[1] = True
        new_cg.name = cg.value
        new_cg.item_indexes[0] = source_index
        new_cg.item_indexes[1] = n

    return len(items)


def get_active_linked_collider_groups() -> Optional[bpy.types.bpy_prop_collection]:
    """
    UIリストでアクティブになっているSpring Bone GroupまたはBoneに対応するCollider Groupsを取得する｡

    Returns
    -------
    Optional[bpy.types.bpy_prop_collection]
        取得されたCollider Groups｡アクティブアイテムがラベルの場合はNoneを返す｡

    """
    active_list_item = vrm0_get_active_list_item_in_spring()
    if active_list_item.item_indexes[0]:
        return

    bone_groups = get_vrm0_extension_spring_bone_group()
    source_bone_group: ReferenceVrm0SecondaryAnimationGroupPropertyGroup
    source_bone_group = bone_groups[active_list_item.item_indexes[0]]
    source_collider_group = source_bone_group.collider_groups[active_list_item.item_indexes[1]]

    return source_collider_group


def vrm0_get_active_list_item_in_linked_collider_group() -> (
    Optional[VRMHELPER_WM_vrm0_spring_linked_collider_group_list_items]
):
    """
    UIリストのアクティブインデックスに対応する､Spring Bone Group内Collider Groupを取得する｡

    Returns
    -------
    Optional[VRMHELPER_WM_vrm0_spring_bone_list_items]
        取得されたCollider Group｡取得できなければNone｡

    """
    if linked_cg_list := get_ui_vrm0_linked_collider_group_prop():
        return linked_cg_list[get_vrm0_active_index_prop("LINKED_CG")]
    return None


# ----------------------------------------------------------
#    For Operator
# ----------------------------------------------------------
def vrm0_add_list_item2collider_group_list4operator():
    """
    オペレーターの処理対象コライダーグループを定義するためのコレクションプロパティにアイテムを登録する｡
    """

    collider_group_collection = get_ui_vrm0_operator_collider_group_prop()
    collider_group_collection.clear()
    group: ReferenceVrm0SecondaryAnimationColliderGroupPropertyGroup
    for n, group in enumerate(get_vrm_extension_property("COLLIDER_GROUP")):
        new_item: VRMHELPER_WM_vrm0_operator_spring_collider_group_list_items
        new_item = collider_group_collection.add()
        new_item.name = group.name
        new_item.bone_name = group.node.bone_name
        new_item.name = group.name
        new_item.group_index = n
        new_item.is_target = True


def vrm0_add_list_item2bone_group_list4operator():
    """
    オペレーターの処理対象ボーングループを定義するためのコレクションプロパティにアイテムを登録する｡
    """

    spring_bone_group_collection = get_ui_vrm0_operator_spring_bone_group_prop()
    spring_bone_group_collection.clear()
    spring_bone_group: ReferenceVrm0SecondaryAnimationGroupPropertyGroup
    for n, spring_bone_group in enumerate(get_vrm_extension_property("SPRING")):
        new_item: VRMHELPER_WM_vrm0_operator_spring_bone_group_list_items
        new_item = spring_bone_group_collection.add()
        new_item.name = spring_bone_group.comment
        new_item.group_index = n
        new_item.is_target = True


def get_spring_bone_group_by_comment(
    comment: str,
) -> Optional[ReferenceVrm0SecondaryAnimationGroupPropertyGroup]:
    result = None
    spring_bone_groups = get_vrm0_extension_spring_bone_group()
    spring_bone_group = [i for i in spring_bone_groups if i.comment == comment]
    if spring_bone_group:
        result = spring_bone_group[0]

    return result
