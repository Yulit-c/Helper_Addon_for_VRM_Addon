if "bpy" in locals():
    import importlib

    reloadable_modules = [
        "Logging.preparation_logger",
        "preferences",
    ]

    for module in reloadable_modules:
        if module in locals():
            importlib.reload(locals()[module])
            print(f"reloaded {module}")

else:
    from .Logging import preparation_logger
    from . import preferences


from pprint import pprint
from typing import (
    Any,
    Iterator,
    TypedDict,
)
import bpy
from bpy.types import (
    Object,
    Armature,
    Bone,
    Material,
    Collection,
    UILayout,
)


from .preferences import (
    get_addon_preferences,
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
    Class
------------------------------------------------------------
---------------------------------------------------------"""


# ----------------------------------------------------------
#    UI List
# ----------------------------------------------------------
class VRMHelper_Addon_Collection_Dict(TypedDict):
    ROOT: Collection
    VRM0_Root: Collection
    VRM1_Root: Collection
    VRM1_Collider: Collection
    VRM1_EXPRESSION_MORPH: Collection
    VRM1_EXPRESSION_MATERIAL: Collection


class VRMHELPER_UL_base:
    """
    UI List用基底クラス
    """

    def add_blank_labels(self, layout: UILayout, count: int, factor: float = 2.0):
        iteration_count = 0
        while iteration_count != count:
            layout.separator(factor=factor)
            iteration_count += 1


"""---------------------------------------------------------
------------------------------------------------------------
    Function
------------------------------------------------------------
---------------------------------------------------------"""

"""---------------------------------------------------------
    Attribute
---------------------------------------------------------"""


def get_attr_from_strings(object: object, attrs: str) -> Any:
    if not (splitted_attrs := attrs.split(".")):
        return

    for attr in splitted_attrs:
        if not object:
            break

        object = getattr(object, attr, None)

    return object


def set_attr_from_strings(object: object, attrs: str, value: Any):
    """
    属性を"."区切りを含む文字列で受け取り､引数"object"に引数"value"をセットする｡

    Parameters
    ----------
    object : object
        処理対象のオブジェクト

    attrs : str
        値をセットしたい属性名｡"."で区切られている場合は末尾の部分の属性に値をセットする｡

    value : Any
        セットされる値｡

    """

    if not (splitted_attrs := attrs.split(".")):
        return

    logger.debug(splitted_attrs)
    for n, attr in enumerate(splitted_attrs):
        if not object:
            return

        if not n == len(splitted_attrs) - 1:
            object = getattr(object, attr, None)

        else:
            logger.debug(f"Set Attribute\n{object}\n{splitted_attrs[-1]}\n{value}")
            setattr(object, attr, value)


def get_properties_to_dict(
    source: object, property_names: Iterator[str]
) -> dict[str, Any]:
    """
    'property_names'で指定した属性を'source'から取得し､それらの値を辞書に格納して帰す｡

    Parameters
    ----------
    source : PropertyGroup
        属性を取得したいプロパティグループ｡

    property_names : tuple
        取得したい属性名を格納したタプル｡

    Returns
    -------
    dict[str, Any]
        取得された値を属性名をキーとして格納した辞書｡

    """

    result = {}
    for name in property_names:
        if value := getattr(source, name):
            result[name] = value

    return result


def set_properties_to_from_dict(target: object, source_dict: dict[str, Any]):
    """
    'target'のオブジェクトが持つ属性の内'source_dict'のキーで指定した属性に対して､キーに対応した値をセットする｡

    Parameters
    ----------
    target : Operator
        処理対象となるオブジェクト｡

    source_dict : dict[str, float, int, bool, Vector]
        属性名と値のペアを格納した辞書｡

    """
    for k, v in source_dict.items():
        setattr(target, k, v)


"""---------------------------------------------------------
    Bone
---------------------------------------------------------"""


def get_selected_bone(target_armature: Armature) -> list[Bone] | None:
    """
    Edit/Pose Modeで選択されたボーンの名前と一致するボーンをtarget_armatureのbonesから取得する｡

    Parameters
    ----------
    target_armature : Armature
        対象のArmatureデータ

    Returns
    -------
    list[Bone]|None
        target_armatureのbonesから取得した､選択中ボーンのリスト

    """

    context = bpy.context
    bones = None
    bone_names = (
        [i.name for i in context.selected_bones]
        if context.selected_bones
        else [i.name for i in context.selected_pose_bones]
    )
    if bone_names:
        bones = [i for i in target_armature.bones if i.name in bone_names]

    return bones


def get_branch_root_bone(source_bone: Bone) -> Bone | None:
    """
    source_boneの親ボーンを再帰的に走査して枝ボーンの根元となるボーンを取得する｡
    source_boneが枝ボーンの一部出ない場合はNoneを返す｡

    Parameters
    ----------
    source_bone : Bone
        処理対象となるボーン｡

    parent_bone : Bone
        処理対象ボーンの親ボーン｡

    Returns
    -------
    Bone | None
        取得された枝ボーンの根元となるボーン｡取得できなかった場合はNone｡

    """
    if source_bone.parent:
        # source_boneに親ボーンが存在しておりconnectがOFFである｡
        if not source_bone.use_connect:
            # 自身の子ボーンにconnectがOFFになっているものが含まれる｡
            if len(source_bone.children) > 1:
                for child in source_bone.children:
                    if not child.use_connect:
                        return source_bone

            return source_bone

        source_bone = source_bone.parent
        return get_branch_root_bone(source_bone)

    return None


def get_child_bones_in_branch(
    source_bone: Bone,
    result: list[Bone],
) -> list[Bone] | None:
    """
    'source_bone'が属する枝に含まれるボーンのリストを返す｡

    Parameters
    ----------
    source_bone : Bone
        処理対象となるボーン｡

    result : list[Bone]
        返り値として渡されるリスト｡再帰処理で値が更新される｡

    Returns
    -------
    list[Bone] | None
        'source_bone'が属する枝に含まれるボーンを格納したリスト｡

    """

    result.append(source_bone)
    if source_bone.children:
        # source_boneに子ボーンが存在しており､その中にconnectがONであるものが含まれている｡
        child_bones = []
        for child in source_bone.children:
            if not child.use_connect:
                continue
            else:
                child_bones.append(child)

        if child_bones:
            source_bone = child_bones[0]
            get_child_bones_in_branch(source_bone, result=result)

    return result


def get_bones_for_each_branch_from_source_bones(
    target_armature: Object, source_bones: Iterator[Bone]
) -> list[list[Bone]]:
    """
    'source_bones'で受け取ったボーンが属する枝の全ボーンを枝毎にグルーピングして取得する｡

    Parameters
    ----------
    target_armature : Object
        ボーンを取得基となるArmature Object

    source_bones : Iterator[Bone]
        処理対象となるボーンを格納したイテレーター

    Returns
    -------
    list[list[Bone]]
        取得されたボーンを枝毎に格納したリスト全てを格納したリスト｡

    """

    # 処理対象となるボーンを､枝毎にグルーピングされた状態で取得する｡
    branch_root_bones = list(
        {y for x in source_bones if (y := get_branch_root_bone(x))}
    )
    sort_order = [i.name for i in target_armature.data.bones if i in branch_root_bones]
    branch_root_bones.sort(key=lambda x: sort_order.index(x.name))

    # [logger.debug(i.name) for i in branch_root_bones]
    retrieved_bones = [get_child_bones_in_branch(i, []) for i in branch_root_bones]

    return retrieved_bones


"""---------------------------------------------------------
    Collection
---------------------------------------------------------"""


def link_object2collection(target_object: Object, dest_collection: Collection):
    """
    'Target_object'のオブジェクトを'dest_collection'のコレクションにリンクさせる｡

    Parameters
    ----------
    target_object : Object
        対象となるオブジェクト｡

    dest_collection : Collection
        リンクさせるコレクション｡

    """
    if target_object in list(dest_collection.objects):
        logger.debug(f"This object is allready linked : {target_object}")
        return

    dest_collection.objects.link(target_object)


def unlink_collection_from_all(target_collection: Collection):
    """
    'target_collection'に設定されている全てのコレクションリンクを解除する｡

    Parameters
    ----------
    target_collection : Collection
        処理対象のコレクション

    """
    # 全てのコレクションからリンクを解除する｡
    for c in bpy.data.collections:
        if target_collection in list(c.children):
            c.children.unlink(target_collection)

    # 全てのシーンコレクションからリンクを解除する｡
    for s in bpy.data.scenes:
        if target_collection in list(s.collection.children):
            s.collection.children.unlink(target_collection)


def unlink_object_from_all_collections(target_object: Object):
    # 全てのコレクションからリンクを解除する｡
    for c in bpy.data.collections:
        if target_object in list(c.objects):
            c.objects.unlink(target_object)

    # 全てのシーンコレクションからリンクを解除する｡
    for s in bpy.data.scenes:
        if target_object in list(s.collection.objects):
            s.collection.objects.unlink(target_object)


def create_or_get_collection_and_link_to_dest(
    target_collection_name: str,
    dest_collection_name: str | None = None,
) -> Collection | None:
    """
    "target_collection_name"で指定したコレクションを作成/取得し､
    "dest_collection_name"で指定したコレクションにリンクする｡

    Parameters
    ----------
    target_collection_name : str
        作成/取得するコレクションの名前

    dest_collection_name : str | None,  --optional
        target collectionをリンクさせるコレクションの名前,
        by default : None

    Returns
    -------
    Collection|None
        作成/取得したコレクション｡

    """
    context = bpy.context
    # Target Collectionの作成あるいは取得する｡
    if not (target_collection := bpy.data.collections.get(target_collection_name)):
        logger.debug(f"Created a New Collection : {target_collection_name}")
        target_collection = bpy.data.collections.new(target_collection_name)

    # 'dest_collection_name'を指定しない場合はSceneのルートコレクションにリンクする｡
    if not dest_collection_name:
        if not target_collection in list(context.scene.collection.children):
            context.scene.collection.children.link(target_collection)
        return target_collection

    # Dest Collectionの作成あるいは取得する｡
    if not (dest_collection := bpy.data.collections.get(dest_collection_name)):
        return target_collection

    if not target_collection in list(dest_collection.children):
        # Target CollectionをDest Collectionにリンクさせる前に他のリンクをすべて解除する｡
        unlink_collection_from_all(target_collection)

        dest_collection.children.link(target_collection)

    return target_collection


def setting_vrm_helper_collection() -> VRMHelper_Addon_Collection_Dict:
    """
    このアドオンが定義する構造のコレクションツリーを作成する｡作成されたコレクションを格納した辞書を返す｡

    Parameters
    ----------

    Returns
    -------
    VRMHelper_Addon_Collection_Dict
        作成したコレクションを格納した辞書

    """

    root = get_addon_collection_name("ROOT")
    vrm0_root = get_addon_collection_name("VRM0_ROOT")
    vrm1_root = get_addon_collection_name("VRM1_ROOT")
    vrm1_collider = get_addon_collection_name("VRM1_COLLIDER")
    vrm1_expression_morph = get_addon_collection_name("VRM1_EXPRESSION_MORPH")
    vrm1_expression_material = get_addon_collection_name("VRM1_EXPRESSION_MATERIAL")

    vrm_helper_collection_dict = {}

    # ----------------------------------------------------------
    #    VRM Helperのルートコレクションをセットアップする｡
    # ----------------------------------------------------------
    addon_root_collection = create_or_get_collection_and_link_to_dest(
        root,
    )
    vrm_helper_collection_dict["ROOT"] = addon_root_collection

    # ----------------------------------------------------------
    #    VRM0用コレクションのセットアップする｡
    # ----------------------------------------------------------
    vrm0_root_collection = create_or_get_collection_and_link_to_dest(
        vrm0_root,
        addon_root_collection.name,
    )

    # ----------------------------------------------------------
    #    VRM1用コレクションのセットアップする｡
    # ----------------------------------------------------------
    vrm1_root_collection = create_or_get_collection_and_link_to_dest(
        vrm1_root,
        addon_root_collection.name,
    )

    vrm1_collider_collection = create_or_get_collection_and_link_to_dest(
        vrm1_collider,
        vrm1_root_collection.name,
    )

    vrm1_expression_morph_collection = create_or_get_collection_and_link_to_dest(
        vrm1_expression_morph,
        vrm1_root_collection.name,
    )

    vrm1_expression_material_collection = create_or_get_collection_and_link_to_dest(
        vrm1_expression_material,
        vrm1_root_collection.name,
    )

    vrm_helper_collection_dict: VRMHelper_Addon_Collection_Dict = {
        "ROOT": addon_root_collection,
        "VRM0_Root": vrm0_root_collection,
        "VRM1_Root": vrm1_root_collection,
        "VRM1_Collider": vrm1_collider_collection,
        "VRM1_EXPRESSION_MORPH": vrm1_expression_morph_collection,
        "VRM1_EXPRESSION_MATERIAL": vrm1_expression_material_collection,
    }

    return vrm_helper_collection_dict


"""---------------------------------------------------------
    Material
---------------------------------------------------------"""


def get_all_materials_from_source_collection_objects(
    source_collection: Collection,
) -> set[Material]:
    """
    'source collection'で指定したコレクションにリンクされた全オブジェクトのマテリアルを集合として取得する｡

    Parameters
    ----------
    source_collection : Collection
        処理対象のコレクション｡

    Returns
    -------
    set[Material]
        取得されたマテリアルを格納した集合｡

    """
    all_materials = {
        slot.material
        for obj in source_collection.all_objects
        for slot in obj.material_slots
    }

    return all_materials


def get_all_materials(scene, context) -> list[tuple[str]]:
    """
    Enum PropertyのUpdateコールバック関数用として､Blendファイル内の全マテリアルを取得して
    プロパティのItemとして渡す｡


    Returns
    -------
    list[tuple[str]]
        Blendファイル内の全マテリアルの名前をEnum PropertyのItemが要求する型に整形したタプルのリスト｡

    """
    try:
        result = []
        for mat in bpy.data.materials:
            id_name = mat.name
            name = mat.name
            description = ""
            item = (id_name, name, description)
            result.append(item)

        return result
    except:
        return [("", "", "")]


"""---------------------------------------------------------
    Misc
---------------------------------------------------------"""


def filtering_mesh_type(source_object: Object) -> bool:
    """
    引数で受け取ったオブジェクトのタイプがMeshか否かを判定する｡

    Parameters
    ----------
    source_object : Object
        対象となるオブジェクト｡

    Returns
    -------
    bool
        source_objectのタイプがMeshであればTrue､それ以外であればFalseが返る｡

    """
    if source_object.type == "MESH":
        return True
    else:
        return False


def get_parent_count(source, parent_count) -> int:
    """
    'source'で受け取ったオブジェクトかボーンの親の数を再帰的にカウントしてその総数を返す｡

    Parameters
    ----------
    source : Object | Bone
        対象となるオブジェクトあるいはボーン

    Returns
    -------
    int
        'source'の親の数を再帰的にカウントした総数｡

    """
    if not source.parent:
        return None, parent_count

    source = source.parent
    parent_count += 1

    return get_parent_count(source, parent_count)


def is_including_empty_in_selected_object() -> bool:
    """
    選択オブジェクトにEmptyが含まれているか否かを判定する｡

    Returns
    -------
    bool
        選択オブジェクト中にEmptyが存在していればTrueが､それ以外はFalseが返る｡
    """

    if not [i for i in bpy.context.selected_objects if i.type == "EMPTY"]:
        return False

    return True


def define_ui_list_rows(item_count: int, max_length: int = 10) -> int:
    """
    引数'item_count'に応じてUI Listの表示する最小幅を返す｡

    Parameters
    ----------
    item_count : int
        リストに表示するアイテムの総数｡

    max_length : int,  --optional
        この数値を超えたアイテム数を持つリストの場合はこちらの値を返す｡,
        by default : 10

    Returns
    -------
    int
        UI Listに表示するアイテム数の最小幅｡

    """
    return max(min(item_count, max_length), 5)
