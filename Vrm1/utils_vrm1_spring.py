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


from pprint import pprint

from typing import (
    Optional,
    Literal,
    Generator,
    Any,
)
import bpy
from bpy.types import (
    Object,
    PoseBone,
    PropertyGroup,
)
from mathutils import (
    Vector,
    Matrix,
)

from ..addon_classes import (
    ReferenceVrm1ColliderPropertyGroup,
    ReferenceVrm1ColliderGroupPropertyGroup,
    ReferenceVrm1SpringPropertyGroup,
)

from ..preferences import (
    get_addon_preferences,
)

from ..property_groups import (
    VRMHELPER_WM_vrm1_collider_list_items,
    VRMHELPER_WM_vrm1_collider_group_list_items,
    VRMHELPER_WM_vrm1_spring_list_items,
    get_ui_vrm1_collider_prop,
    get_ui_vrm1_collider_group_prop,
    get_ui_vrm1_operator_collider_group_prop,
    get_ui_vrm1_spring_prop,
    get_ui_vrm1_operator_bone_group_prop,
    get_ui_vrm1_operator_spring_prop,
    # ----------------------------------------------------------
    get_target_armature,
    get_target_armature_data,
    get_vrm1_active_index_prop,
)


from ..utils_common import (
    get_parent_count,
)

from ..utils_vrm_base import (
    get_vrm_extension_property,
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


"""---------------------------------------------------------
    Common
---------------------------------------------------------"""


def get_pose_bone_by_name(bone_name: str) -> PoseBone:
    return get_target_armature().pose.bones[bone_name]


"""---------------------------------------------------------
    Collider
---------------------------------------------------------"""


def get_source_vrm1_colliders() -> (
    dict[str, list[tuple[int, ReferenceVrm1ColliderPropertyGroup]]]
):
    """
    Target ArmatureのVRM Extension内のVRM1のコライダーと対応ボーンの情報を格納した辞書を返す｡

    Returns
    -------
    dict[str, list[tuple[int, ReferenceVrm1ColliderPropertyGroup]]]
        コライダーとインデックスを格納したタプルのリストを､対応するボーン名をキーとして格納した辞書｡

    """

    # VRM ExtensionのCollidersを取得する
    colliders = get_vrm_extension_property("COLLIDER")

    # VRM1のSpring Bone Colliderをリストに格納して返す｡
    colliders_dict = {}
    for n, collider in enumerate(colliders):
        colliders_dict.setdefault(collider.node.bone_name, [])
        colliders_dict[collider.node.bone_name].append((n, collider))

    sort_order = [
        i.name
        for i in get_target_armature_data().bones
        if i.name in colliders_dict.keys()
    ]

    def get_index(element):
        if element[0] == "":
            result = -1
        else:
            result = sort_order.index(element[0])
        return result

    sorted_colliders = dict(sorted(colliders_dict.items(), key=get_index))
    # sorted_colliders = dict(sorted(colliders_dict.items(), key=lambda x: sort_order.index(x[0])))

    return sorted_colliders


def add_items2collider_ui_list() -> int:
    """
    VRM1のSpring Bone_Colliderの確認/設定を行なうUI Listの描画候補アイテムをコレクションプロパティに追加する｡
    UI Listのrows入力用にアイテム数を返す｡

    Returns
    -------
    int
        リストに表示するアイテム数｡

    """

    # wm_prop = get_addon_prop_group("WM")
    # items = wm_prop.collider_list_items4custom_filter
    items = get_ui_vrm1_collider_prop()

    source_collider_dict = get_source_vrm1_colliders()
    bones = get_target_armature_data().bones

    # コレクションプロパティの初期化処理｡
    items.clear()

    # コレクションプロパティに先頭ラベルとColliderの各情報を追加する｡
    label = items.add()
    label.item_type[0] = True
    for k in source_collider_dict.keys():
        # ボーン名をコレクションプロパティに追加する｡
        new_item: VRMHELPER_WM_vrm1_collider_list_items = items.add()
        new_item.item_type[1] = True
        # colliderの'node.bone_name'が空文字であれば次のキーに移行｡
        if not k:
            continue
        new_item.name = k
        new_item.bone_name = k
        _, parent_count = get_parent_count(bones[k], 0)
        new_item.parent_count = (parent_count := parent_count + 1)

        # コライダーをコレクションプロパティに追加する｡
        for n, collider in source_collider_dict[k]:
            object_name = collider.bpy_object.name if collider.bpy_object else ""
            new_item = items.add()
            new_item.item_type[2] = True
            new_item.name = f"{k} {object_name}"
            new_item.bone_name = k
            new_item.collider_name = object_name
            new_item.collider_object = collider.bpy_object
            new_item.collider_type = collider.shape_type.upper()
            new_item.parent_count = parent_count + 1
            new_item.item_index = n
            # タイプがカプセルであれば子Emptyオブジェクトもコレクションプロパティに追加する｡
            if collider.shape_type == "Capsule":
                child_object_name = (
                    collider.bpy_object.children[0].name if collider.bpy_object else ""
                )
                new_item = items.add()
                new_item.item_type[3] = True
                new_item.name = f"{k} {child_object_name}"
                new_item.bone_name = k
                new_item.collider_name = child_object_name
                new_item.collider_object = collider.bpy_object
                new_item.collider_type = "CAPSULE_END"
                new_item.parent_count = parent_count + 2
                new_item.item_index = n

    return len(list(items))


def remove_vrm1_collider_by_selected_object(source_object: Object) -> str:
    """
    VRM1 Collidersの内､引数'collider_name'と同一のオブジェクトが登録されたコライダを消去する｡

    Parameters
    ----------
    source_object : Object
        削除対象となるオブジェクト名｡

    Returns
    -------
    str
        削除対象のコライダーに登録されていたuuidの値｡
    """

    colliders = get_vrm_extension_property("COLLIDER")

    # 'source_object'がコライダーの'bpy_object'あるいは'bpy_object'の子オブジェクトである｡
    if collider := [
        i
        for i in colliders
        if i.bpy_object == source_object
        or (i.bpy_object.children and i.bpy_object.children[0] == source_object)
    ]:
        target_collider = collider[0]
        target_uuid = target_collider.uuid

        # 'source_object'とそれに対応したコライダーを削除する｡
        remove_vrm1_collider_group_collider_when_removed_collider(target_uuid)
        colliders.remove(list(colliders).index(target_collider))

        # 'source_object'を削除する｡子が存在すればそれを先に削除する｡
        if source_object.children:
            [
                bpy.data.objects.remove(obj, do_unlink=True)
                for obj in source_object.children
            ]

        bpy.data.objects.remove(source_object, do_unlink=True)


def generate_head_collider_position(head: Vector) -> Matrix:
    """
    コライダーをボーンのヘッドに設置するためのマトリックスを返す｡

    Parameters
    ----------
    head : Vector
        親ボーンのヘッド

    Returns
    -------
    Matrix
        親ボーンのヘッドを基に生成されたマトリックス｡

    """
    return Matrix.Translation(head)


def generate_tail_collider_position(bone: PoseBone, tail: Vector) -> Matrix:
    """
    コライダーをボーンのテールの位置に設置するためのマトリックスを返す｡

    Parameters
    ----------
    bone : EditBone | PoseBone
        ヘッドコライダーの親ボーン｡

    tail : Vector
        親ボーンのテール｡

    Returns
    -------
    Matrix
        親ボーンのテールを基に生成されたマトリックス｡

    """
    armature_object = get_target_armature()
    return (
        armature_object.matrix_world.inverted()
        @ bone.matrix.inverted()
        @ Matrix.Translation(tail)
    )


# -----------------------------------------------------


"""---------------------------------------------------------
    Collider Group
---------------------------------------------------------"""


def is_existing_collider_group() -> bool:
    """
    Target Armature内にコライダーグループが存在しているかどうかをチェックする｡

    Returns
    -------
    bool
        コライダーグループが1つ以上存在する場合はTrue｡そうでなければFalse｡

    """
    if get_vrm_extension_property("COLLIDER_GROUP"):
        return True

    else:
        return False


def get_active_list_item_in_collider_group() -> (
    VRMHELPER_WM_vrm1_collider_group_list_items | None
):
    """
    UIリストのアクティブインデックスに対応したコライダーグループを取得する｡

    Returns
    -------
    PropertyGroup | None
        取得されたコライダーグループ｡取得できなければNone｡

    """
    if collider_group_list := get_ui_vrm1_collider_group_prop():
        return collider_group_list[get_vrm1_active_index_prop("COLLIDER_GROUP")]
    else:
        return None


def get_source_vrm1_collider_groups() -> (
    Optional[Generator[tuple[ReferenceVrm1ColliderGroupPropertyGroup, Any], None, None]]
):
    """
    Target ArmatureのVRM Extension内のVRM1コライダーグループと登録されたコライダーの情報を格納した辞書を返す｡

    Returns
    -------
    Optional[Generator[tuple[ReferenceVrm1ColliderGroupPropertyGroup, Any]]]
        VRM Extensionに登録されたコライダーグループと､
        グループに登録されたコライダーを格納したタプルを出力するジェネレーター

    """
    # VRM Extensionの'colliders'を取得する
    collider_groups = get_vrm_extension_property("COLLIDER_GROUP")

    return ((group, group.colliders) for group in collider_groups)


def get_operator_target_collider_group() -> list[str]:
    """
    コライダーグループを登録するオペレーターのターゲットとなるコライダーグループの名前を格納したリストを返す｡

    Returns
    -------
    list[str]
        ターゲットコライダーグループの名前を格納したリスト｡

    """
    collider_group_collection = get_ui_vrm1_operator_collider_group_prop()
    target_name_list = [i.name for i in collider_group_collection if i.is_target]
    return target_name_list


def add_items2collider_group_ui_list() -> int:
    """
    VRM1のSpring Bone_Collider Groupの確認/設定を行なうUI Listの描画候補アイテムをコレクションプロパティに追加する｡
    UI Listのrows入力用にアイテム数を返す｡

    Returns
    -------
    int
        リストに表示するアイテム数｡

    """
    # wm_prop = get_addon_prop_group("WM")
    # items = wm_prop.collider_group_list_items4custom_filter
    items = get_ui_vrm1_collider_group_prop()

    # コレクションプロパティの初期化処理｡
    items.clear()

    # コレクションプロパティにCollider Groupsの各情報を追加する｡
    for m, collider_group in enumerate(get_source_vrm1_collider_groups()):
        group, colliders = collider_group

        # セパレーター用ラベルをコレクションプロパティに追加する｡
        if m != 0:
            label = items.add()
            label.item_type[0] = True

        # コライダーグループをコレクションプロパティに追加する｡
        new_item = items.add()
        new_item.item_type[1] = True
        new_item.name = group.vrm_name
        new_item.item_name = group.vrm_name
        new_item.item_indexes[0] = m
        # コライダーグループ毎に登録されているコライダーをコレクションプロパティに追加する｡
        for n, collider in enumerate(colliders):
            new_item = items.add()
            new_item.item_type[2] = True
            new_item.name = collider.collider_name
            new_item.item_name = collider.collider_name
            new_item.item_indexes[0] = m
            new_item.item_indexes[1] = n

    return len(list(items))


def remove_vrm1_collider_group_collider_when_removed_collider(collider_uuid: str):
    """
    VRM1のコライダーが削除される時にそれを参照しているコライダーグループの値を更新する｡

    Parameters
    ----------
    collider_uuid : str
        削除されるコライダーのuuid

    """
    collider_groups = get_vrm_extension_property("COLLIDER_GROUP")
    for collider_group in collider_groups:
        for collider in (colliders := collider_group.colliders):
            if collider.collider_uuid == collider_uuid:
                colliders.remove(list(colliders).index(collider))

    cleanup_empty_collider_group()


def cleanup_empty_collider_group():
    """
    VRM1のコライダーグループのうち､コライダーが登録されていないものを削除する｡
    """
    collider_groups = get_vrm_extension_property("COLLIDER_GROUP")
    candidate_remove_target_group_uuid = []
    for collider_group in collider_groups:
        if not collider_group.colliders:
            logger.debug(f"Colliders is empty : {collider_group.name}")
            remove_vrm1_spring_collider_group_when_removed_collider_group(
                collider_group.name
            )
            candidate_remove_target_group_uuid.append(collider_group.uuid)

    if candidate_remove_target_group_uuid:
        # for uuid in candidate_remove_target_group_uuid:
        if remove_target_group := [
            i for i in collider_groups if i.uuid in candidate_remove_target_group_uuid
        ]:
            collider_groups.remove(list(collider_groups).index(remove_target_group[0]))


"""---------------------------------------------------------
    Spring
---------------------------------------------------------"""


def get_active_list_item_in_spring() -> Optional[VRMHELPER_WM_vrm1_spring_list_items]:
    """
    SpringのUI List内でアクティブになっているアイテムを取得して返す｡

    Returns
    -------
    Optional[VRMHELPER_WM_vrm1_spring_list_items]
        SpringのUi List内のアクティブアイテム

    """

    if spring_group_list := get_ui_vrm1_spring_prop():
        return spring_group_list[get_vrm1_active_index_prop("SPRING")]
    else:
        return None


def get_source_vrm1_springs() -> (
    Generator[tuple[ReferenceVrm1SpringPropertyGroup, Any, Any], None, None]
):
    """
    Target ArmatureのVRM Extension内のVRM1スプリングの全スプリングから
    'spring', 'joints', 'collider_groups'を格納したタプルのジェネレーターを作成する｡

    Returns
    -------
    Generator[tuple[ReferenceVrm1SpringPropertyGroup, Any, Any]]
        全スプリングが持つ'spring', 'joints', 'collider_groups'の属性を格納したタプルのジェネレーター｡
    """
    # VRM Extensionの'colliders'を取得する
    springs = get_vrm_extension_property("SPRING")

    return ((spring, spring.joints, spring.collider_groups) for spring in springs)


def add_items2spring_ui_list() -> int:
    """
    VRM1のSpringの確認/設定を行なうUI Listの描画候補アイテムをコレクションプロパティに追加する｡
    UI Listのrows入力用にアイテム数を返す｡

    Returns
    -------
    int
        リストに表示するアイテム数｡

    """
    # wm_prop = get_addon_prop_group("WM")
    # items = wm_prop.spring_list_items4custom_filter
    items = get_ui_vrm1_spring_prop()

    # コレクションプロパティの初期化処理｡
    items.clear()

    # コレクションプロパティにSpringの各情報を追加する｡
    for m, springs in enumerate(get_source_vrm1_springs()):
        spring, joints, collider_groups = springs
        if m != 0:
            # セパレーター用ラベルをコレクションプロパティに追加する｡
            label = items.add()
            label.item_type[0] = True
            label.name = ""

        # -----------------------------------------------------
        # Springをコレクションプロパティに追加する｡
        new_item = items.add()
        new_item.item_type[1] = True
        new_item.item_indexes[0] = m
        new_item.name = spring.vrm_name
        new_item.item_name = spring.vrm_name

        # -----------------------------------------------------
        # Joint用ラベルをコレクションプロパティに追加する｡
        label = items.add()
        label.item_type[0] = True
        label.item_indexes[0] = m
        label.name = "Joint"

        # Jointをコレクションプロパティに追加する｡
        for n, joint in enumerate(joints):
            new_item = items.add()
            new_item.item_type[2] = True
            new_item.item_indexes[0] = m
            new_item.item_indexes[1] = n
            new_item.name = spring.vrm_name
            new_item.item_name = joint.node.bone_name

        # -----------------------------------------------------
        # Collider Group用ラベルをコレクションプロパティに追加する｡
        label = items.add()
        label.item_type[0] = True
        label.item_indexes[0] = m
        label.name = "Collider Group"

        # Collider Groupをコレクションプロパティに追加する｡
        for n, group in enumerate(collider_groups):
            new_item = items.add()
            new_item.item_type[3] = True
            new_item.item_indexes[0] = m
            new_item.item_indexes[2] = n
            new_item.name = spring.vrm_name
            new_item.item_name = group.name

    return len(list(items))


def remove_vrm1_spring_collider_group_when_removed_collider_group(
    collider_group_name: str,
):
    """
    VRM1のコライダーグループが削除され時に､それを参照しているスプリングのコライダーグループの値を更新する｡

    Parameters
    ----------
    collider_group_name : str
        削除されるコライダーグループの名前｡

    """

    logger.debug(collider_group_name)
    springs = get_vrm_extension_property("SPRING")
    for spring in springs:
        for n, group in enumerate(groups := spring.collider_groups):
            if group.collider_group_name == collider_group_name:
                groups.remove(n)


# ----------------------------------------------------------
#    For Operator
# ----------------------------------------------------------


def add_list_item2bone_group_list4operator():
    """
    オペレーターの処理対象ボーングループを定義するためのコレクションプロパティにアイテムを登録する｡
    """

    addon_pref = get_addon_preferences()
    filtering_word = addon_pref.bone_group_filter_name

    bone_group_collection = get_ui_vrm1_operator_bone_group_prop()
    bone_group_collection.clear()
    for n, group in enumerate(get_target_armature().pose.bone_groups):
        new_item = bone_group_collection.add()
        new_item.name = group.name
        new_item.group_index = n
        # Bone Groupの名前に'filter_word'が含まれる場合は初期値をTrueにする｡
        if filtering_word in group.name:
            new_item.is_target = True


def add_list_item2collider_group_list4operator():
    """
    オペレーターの処理対象コライダーグループを定義するためのコレクションプロパティにアイテムを登録する｡
    """

    collider_group_collection = get_ui_vrm1_operator_collider_group_prop()
    collider_group_collection.clear()
    for group in get_vrm_extension_property("COLLIDER_GROUP"):
        new_item = collider_group_collection.add()
        new_item.name = group.name
        new_item.vrm_name = group.vrm_name
        new_item.is_target = True


def add_list_item2joint_list4operator():
    """
    オペレーターの処理対象ジョインツを定義するためのコレクションプロパティにアイテムを登録する｡
    """

    spring_collection = get_ui_vrm1_operator_spring_prop()
    spring_collection.clear()
    for n, spring in enumerate(get_vrm_extension_property("SPRING")):
        new_item = spring_collection.add()
        new_item.name = spring.vrm_name
        new_item.is_target = True
        new_item.spring_index = n
