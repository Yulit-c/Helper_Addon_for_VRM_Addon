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
    Optional,
    Iterator,
    TypedDict,
    Any,
)
import bpy
from mathutils import Vector, Matrix

from .addon_classes import (
    VRMHelper_Addon_Collection_Dict,
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

    # logger.debug(splitted_attrs)
    for n, attr in enumerate(splitted_attrs):
        if not object:
            return

        if not n == len(splitted_attrs) - 1:
            object = getattr(object, attr, None)

        else:
            logger.debug(f"Set Attribute\n{object}\n{splitted_attrs[-1]}\n{value}")
            setattr(object, attr, value)


def get_properties_to_dict(source: object, property_names: Iterator[str]) -> dict[str, Any]:
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


def get_active_bone() -> Optional[bpy.types.Bone]:
    """
    Edit/Pose Modeでアクティブになっているボーンを取得する｡

    Parameters
    ----------

    Returns
    -------
    bpy.types.Bone
        取得されたボーン

    """

    active_object = bpy.context.active_object
    if active_object.type != "ARMATURE":
        return

    match bpy.context.mode:
        case "EDIT_ARMATURE":
            active_bone = bpy.context.active_bone

        case "POSE":
            active_bone = bpy.context.active_pose_bone

        case _:
            return

    obtained_bone = active_object.data.bones.get(active_bone.name)
    return obtained_bone


def get_selected_bone() -> Optional[list[bpy.types.Bone]]:
    """
    Edit/Pose Modeで選択されたボーンの名前と一致するボーンをアクティブオブジェクトデータのbonesから取得する｡

    Returns
    -------
    Optional[list[bpy.types.Bone]]
        のbonesから取得した､選択中ボーンのリスト

    """

    context = bpy.context
    active_object = context.active_object
    if active_object.type != "ARMATURE":
        return

    bones = []
    bone_names = []

    match context.mode:
        case "EDIT_ARMATURE":
            bone_names = [i.name for i in context.selected_bones]

        case "POSE":
            bone_names = [i.name for i in context.selected_pose_bones]

    if bone_names:
        bones = [i for i in active_object.data.bones if i.name in bone_names]

    return bones


def get_selected_bone_names() -> Optional[list[str]]:
    """
    Edit/Pose Modeで選択されたボーンの名前と一致するボーンをアクティブオブジェクトデータのbonesから取得する｡

    Returns
    -------
    Optional[list[bpy.types.Bone]]
        のbonesから取得した､選択中ボーンのリスト

    """

    context = bpy.context
    active_object = context.active_object
    if active_object.type != "ARMATURE":
        return

    match context.mode:
        case "EDIT_ARMATURE":
            bone_names = [i.name for i in context.selected_bones]

        case "POSE":
            bone_names = [i.name for i in context.selected_pose_bones]

    return bone_names


def get_pose_bone_by_name(source: bpy.types.Object, bone_name: str) -> Optional[bpy.types.PoseBone]:
    """
    "source"のArmatureオブジェクト内のPose Boneを名前によって取得する｡

    Parameters
    ----------
    source : bpy.types.Object
        処理対象のArmatureオブジェクト

    bone_name : str
        取得したいボーンのなめ

    Returns
    -------
    bpy.types.PoseBone
        取得されたPose Bone

    """
    if source.type != "ARMATURE":
        return

    obtained_pose_bone = source.pose.bones[bone_name]
    return obtained_pose_bone


def get_branch_root_bone(source_bone: bpy.types.Bone) -> Optional[bpy.types.Bone]:
    """
    source_boneの親ボーンを再帰的に走査して枝ボーンの根元となるボーンを取得する｡
    source_boneが枝ボーンの一部でない場合はNoneを返す｡

    Parameters
    ----------
    source_bone : bpy.types.Bone
        処理対象となるボーン｡

    Returns
    -------
    Optional[bpy.types.Bone]
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
    source_bone: bpy.types.Bone,
    result: list[bpy.types.Bone],
) -> list[bpy.types.Bone]:
    """
    'source_bone'が属する枝に含まれるボーンのリストを返す｡

    Parameters
    ----------
    source_bone : bpy.types.Bone
        処理対象となるボーン｡

    result : list[bpy.types.Bone]
        返り値として渡されるリスト｡再帰処理で値が更新される｡

    Returns
    -------
    list[bpy.types.Bone]
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
            get_child_bones_in_branch(source_bone, result)

    return result


def get_bones_for_each_branch_from_source_bones(
    target_armature: bpy.types.Object, source_bones: Iterator[bpy.types.Bone]
) -> list[list[bpy.types.Bone]]:
    """
    'source_bones'で受け取ったボーンが属する枝の全ボーンを枝毎にグルーピングして取得する｡

    Parameters
    ----------
    target_armature : bpy.types.Object
        ボーンを取得基となるArmature Object

    source_bones : Iterator[bpy.types.Bone]
        処理対象となるボーンを格納したイテレーター

    Returns
    -------
    list[list[bpy.types.Bone]]
        取得されたボーンを枝毎に格納したリスト全てを格納したリスト｡

    """

    # 処理対象となるボーンを､枝毎にグルーピングされた状態で取得する｡
    branch_root_bones = list({y for x in source_bones if (y := get_branch_root_bone(x))})
    sort_order = [i.name for i in target_armature.data.bones if i in branch_root_bones]
    branch_root_bones.sort(key=lambda x: sort_order.index(x.name))

    # [logger.debug(i.name) for i in branch_root_bones]
    retrieved_bones = [get_child_bones_in_branch(i, []) for i in branch_root_bones]

    return retrieved_bones


def generate_head_collider_position(head: Vector) -> Matrix:
    """
    ボーンのヘッドの位置のマトリックスを返す｡

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


def generate_tail_collider_position(
    armature_object: bpy.types.Object, pose_bone: bpy.types.PoseBone, tail: Vector
) -> Matrix:
    """
    ボーンのテールの位置のマトリックスを返す｡

    Parameters
    ----------
    armature_object: bpy.types.Object
        処理対象のボーンが属しているArmatureオブジェクト

    pose_bone : EditBone | PoseBone
        ヘッドコライダーの親ボーン｡

    tail : Vector
        親ボーンのテール｡

    Returns
    -------
    Matrix
        親ボーンのテールを基に生成されたマトリックス｡

    """
    return armature_object.matrix_world.inverted() @ pose_bone.matrix.inverted() @ Matrix.Translation(tail)


"""---------------------------------------------------------
    Collection
---------------------------------------------------------"""


def link_object2collection(target_object: bpy.types.Object, dest_collection: bpy.types.Collection):
    """
    'Target_object'のオブジェクトを'dest_collection'のコレクションにリンクさせる｡

    Parameters
    ----------
    target_object : bpy.types.Object
        対象となるオブジェクト｡

    dest_collection : bpy.types.Collection
        リンクさせるコレクション｡

    """
    if target_object in list(dest_collection.objects):
        logger.debug(f"This object is allready linked : {target_object}")
        return

    dest_collection.objects.link(target_object)


def unlink_collection_from_all(target_collection: bpy.types.Collection):
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


def unlink_object_from_all_collections(target_object: bpy.types.Object):
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
    dest_collection_name: Optional[str] = None,
) -> Optional[bpy.types.Collection]:
    """
    "dest_collection_name"で指定したコレクションにリンクする｡

    Parameters
    ----------
    target_collection_name : str
        作成/取得するコレクションの名前

    dest_collection_name : Optional[str],  --optional
        target collectionをリンクさせるコレクションの名前｡
        by default : None

    Returns
    -------
    Optional[bpy.types.Collection]
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
    vrm0_collider = get_addon_collection_name("VRM0_COLLIDER")
    vrm0_blend_shape_morph = get_addon_collection_name("VRM0_BLENDSHAPE_MORPH")
    vrm0_blend_shape_material = get_addon_collection_name("VRM0_BLENDSHAPE_MATERIAL")
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

    vrm0_collider_collection = create_or_get_collection_and_link_to_dest(
        vrm0_collider, vrm0_root_collection.name
    )

    vrm0_blend_shape_morph_collection = create_or_get_collection_and_link_to_dest(
        vrm0_blend_shape_morph, vrm0_root_collection.name
    )

    vrm0_blend_shape_material_collection = create_or_get_collection_and_link_to_dest(
        vrm0_blend_shape_material, vrm0_root_collection.name
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
        "VRM0_COLLIDER": vrm0_collider_collection,
        "VRM0_BLEND_SHAPE_MORPH": vrm0_blend_shape_morph_collection,
        "VRM0_BLEND_SHAPE_MATERIAL": vrm0_blend_shape_material_collection,
        "VRM1_Root": vrm1_root_collection,
        "VRM1_COLLIDER": vrm1_collider_collection,
        "VRM1_EXPRESSION_MORPH": vrm1_expression_morph_collection,
        "VRM1_EXPRESSION_MATERIAL": vrm1_expression_material_collection,
    }

    return vrm_helper_collection_dict


"""---------------------------------------------------------
    Material
---------------------------------------------------------"""


def get_all_materials_from_source_collection_objects(
    source_collection: bpy.types.Collection,
) -> set[bpy.types.Material]:
    """
    'source collection'で指定したコレクションにリンクされた全オブジェクトのマテリアルを集合として取得する｡

    Parameters
    ----------
    source_collection : bpy.types.Collection
        処理対象のコレクション｡

    Returns
    -------
    set[bpy.types.Material]
        取得されたマテリアルを格納した集合｡

    """
    all_materials = {slot.material for obj in source_collection.all_objects for slot in obj.material_slots}

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


def filtering_mesh_type(source_object: bpy.types.Object) -> bool:
    """
    引数で受け取ったオブジェクトのタイプがMeshか否かを判定する｡

    Parameters
    ----------
    source_object : bpy.types.Object
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


def get_parent_count(
    source: bpy.types.Object | bpy.types.Bone, parent_count: int
) -> tuple[Optional[bpy.types.Object | bpy.types.Bone], int]:
    """
    'source'で受け取ったオブジェクトかボーンの親の数を再帰的にカウントしてその総数を返す｡

    Parameters
    ----------
    source : bpy.types.Object | bpy.types.Bone
        処理の対象となるオブジェクトまたはボーン

    parent_count : int
        現在までにカウントされた親要素の数

    Returns
    -------
    tuple[Optional[bpy.types.Object|bpy.types.Bone], int]
        次の処理対象となるオブジェクトまたはボーンと現在までにカウントされた親要素の数を格納したタプル

    """
    if not source.parent:
        return None, parent_count

    source = source.parent
    parent_count += 1

    return get_parent_count(source, parent_count)


def filtering_empty_from_selected_objects() -> Optional[list[bpy.types.Object]]:
    """
    選択オブジェクトに含まれるEmptyオブジェクトを抽出する｡

    Returns
    -------
    Optional[list[bpy.types.Object]]
        選択オブジェクト中に含まれるEmptyオブジェクトのリスト｡一つもない場合はNoneが返る｡
    """

    empty_object_list = [i for i in bpy.context.selected_objects if i.type == "EMPTY"]
    if not empty_object_list:
        return None

    return empty_object_list


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


def reset_shape_keys_value(target_mesh: bpy.types.Mesh):
    """
    'target_mesh'に存在するすべてのシェイプキーの値を0にセットする.add()

    Parameters
    ----------
    target_mesh : bpy.types.Mesh
        処理対象のMesh

    """
    if sks := target_mesh.shape_keys:
        key_blocks = sks.key_blocks
        for key in key_blocks:
            key.value = 0.0
