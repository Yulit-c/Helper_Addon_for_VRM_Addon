if "bpy" in locals():
    import importlib

    reloadable_modules = [
        "preparation_logger",
        "property_groups",
        "utils_common",
        "utils_vrm_base",
    ]

    for module in reloadable_modules:
        if module in locals():
            importlib.reload(locals()[module])

else:
    from ..Logging import preparation_logger
    from .. import property_groups
    from .. import utils_common
    from .. import utils_vrm_base

from pprint import pprint

import re
from sys import float_info
from typing import (
    Literal,
)
import bpy
from bpy.types import (
    Object,
    PoseBone,
    Constraint,
    CopyRotationConstraint,
    DampedTrackConstraint,
    UILayout,
)

from ..property_groups import (
    VRMHELPER_WM_vrm1_constraint_list_items,
    get_addon_prop_group,
    get_vrm1_active_index_prop,
    get_wm_vrm1_constraint_prop,
    get_target_armature,
    get_ui_list_prop4custom_filter,
)

from ..utils_vrm_base import (
    VrmRollConstraint,
    VrmAimConstraint,
    VrmRotationConstraint,
    CandidateConstraitProperties,
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


# ----------------------------------------------------------
#    For UI List
# ----------------------------------------------------------
def evaluate_aim_constraint_target(
    source_constraint: Constraint,
    target_armature: Object,
) -> bool:
    """
    'source_constraint'のtarget,subtargetのパラメーターが適切に設定されているか否かを評価する｡
    正しく設定されていればTrue,誤りがあればFalseを返す｡

    Parameters
    ----------
    source_constraint : Constraint
        処理対象となるコンストレイント


    Returns
    -------
    bool
        評価の結果｡設定が正しければTrue｡不適切な設定がされていればFalse｡

    """

    match source_constraint.target.type:
        case "Armature":
            # result = (
            #     source_constraint.target == target_armature
            #     and source_constraint.subtarget in target_armature.data.bones
            #     and abs(source_constraint.head_tail) < float_info.epsilon
            # )
            result = abs(source_constraint.head_tail) < float_info.epsilon

        case _:
            result = True

    return result


def determine_constraint_type(
    source_constraint: Constraint,
    target_armature: Object,
) -> VrmRollConstraint | VrmAimConstraint | VrmRotationConstraint | None:
    """
    'source_constraint'がVRMが定義するコンストレイントの内､どれに該当するかを判定する｡
    パラメーター設定に応じて'Roll', 'Aim', 'Rotation'､あるいはNoneとと判定される｡

    Parameters
    ----------
    source_constraint : Constraint
        処理対象のコンストレイント

    target_armature : Object
        アドオンが参照しているArmatureオブジェクト

    Returns
    -------
    VrmRollConstraint | VrmAimConstraint | VrmRotationConstraint | None
        判定の結果｡いずれにも該当しない場合はNone｡

    """

    is_roll_or_rotation = False

    # Rool Constraint
    is_roll_or_rotation = (
        isinstance(source_constraint, CopyRotationConstraint)
        # and source_constraint.is_valid
        and not source_constraint.mute
        and source_constraint.target
        and source_constraint.target in list(bpy.data.objects)
        and not source_constraint.invert_x
        and not source_constraint.invert_y
        and not source_constraint.invert_z
        and source_constraint.mix_mode == "ADD"
        and source_constraint.owner_space == "LOCAL"
        and source_constraint.target_space == "LOCAL"
    )

    if is_roll_or_rotation:
        if (
            int(source_constraint.use_x)
            + int(source_constraint.use_y)
            + int(source_constraint.use_z)
        ) == 1:
            return VrmRollConstraint()

    # Aim Constraint
    if isinstance(
        source_constraint, DampedTrackConstraint
    ) and evaluate_aim_constraint_target(source_constraint, target_armature):
        return VrmAimConstraint()

    # Rotation Constraint
    if is_roll_or_rotation:
        if (
            source_constraint.use_x
            and source_constraint.use_y
            and source_constraint.use_z
        ):
            return VrmRotationConstraint()


def get_object_has_constraint(
    source_type: Literal["OBJECT", "BONE"],
    source_armature: Object,
) -> dict[str : Object | PoseBone]:
    """
    'source_type'に応じてオブジェクトまたはポーズボーンからコンストレイントを持ったものを抽出し､
    データ名をキーとする辞書として返す｡'source_type'が'Object'の場合はキーでソートする｡

    Returns
    -------
    _type_
        カレントシーン/'source_armatrue'おポーズボーンからコンストレイントを持ったデータを値､
        データ名をキーとして格納した辞書｡

    """

    if source_type == "OBJECT":
        source = bpy.data.objects
        candidate_objects_dict = {i.name: i for i in source if i.constraints}
        result = sorted(candidate_objects_dict.items())

    else:
        source = source_armature.pose.bones
        candidate_objects_dict = {i.name: i for i in source if i.constraints}
        result = list(candidate_objects_dict.items())

    return result


def get_candidate_constraints_for_draw_ui(
    source_type: Literal["OBJECT", "BONE"],
) -> list[CandidateConstraitProperties]:
    """
    Target ArmatureのVRM Extension内のVRM1のコンストレイントの情報を格納した辞書を返す｡

    Parameters
    ----------
    source_type :
        アイテムを登録するコレクションがObject ConstraintのものかBone Constraintのものかを選択する｡

    Returns
    -------
    CandidateConstraints
        UI Listに表示する候補となるコンストレイントを格納した辞書｡

    """

    target_armature = get_target_armature()
    # 描画モードに応じてオブジェクトかポーズボーンを取得し､コンストレイントを持ったものを抽出する｡
    sorted_dict = get_object_has_constraint(source_type, target_armature)
    element_has_constraint_list = [obj_or_bone for name, obj_or_bone in sorted_dict]

    roll_constraint_list = []
    aim_constraint_list = []
    rotation_constraint_list = []

    # 対象データが持っているコンストレイントのプロパティに応じてVRM定義のコンストレイントと判定する｡
    for element in element_has_constraint_list:
        for n, constraint in enumerate(element.constraints):
            constraint_type = determine_constraint_type(constraint, target_armature)
            match constraint_type:
                case VrmRollConstraint():
                    temp_tuple: CandidateConstraitProperties = (
                        VrmRollConstraint(),
                        element,
                        n,
                        False,
                        constraint,
                    )
                    roll_constraint_list.append(temp_tuple)

                case VrmAimConstraint():
                    temp_tuple: CandidateConstraitProperties = (
                        VrmAimConstraint(),
                        element,
                        n,
                        False,
                        constraint,
                    )
                    aim_constraint_list.append(temp_tuple)

                case VrmRotationConstraint():
                    temp_tuple: CandidateConstraitProperties = (
                        VrmRotationConstraint(),
                        element,
                        n,
                        False,
                        constraint,
                    )
                    rotation_constraint_list.append(temp_tuple)

    candidate_constraints = (
        roll_constraint_list + aim_constraint_list + rotation_constraint_list
    )

    return candidate_constraints


def exclude_circular_dependency_constraints(
    candidate_constraints_list: list[CandidateConstraitProperties],
) -> list[CandidateConstraitProperties]:
    excluded_constraint_list: list[Constraint] = []
    source_constraint_list = [
        constraint for _, _, _, _, constraint in candidate_constraints_list
    ]

    for search_constraint in source_constraint_list:
        # TODO : Aim Constraint's circular dependency detectio
        if isinstance(search_constraint, DampedTrackConstraint):
            continue

        current_constraints = [
            (
                search_constraint,
                (
                    search_constraint.use_x,
                    search_constraint.use_y,
                    search_constraint.use_z,
                ),
            )
        ]

        iterated_constraints = set()
        while current_constraints:
            current_constraint, current_axis = current_constraints.pop()

            if current_constraint in iterated_constraints:
                break
            iterated_constraints.add(current_constraint)

            found = False

            match current_constraint.target.type:
                case "ARMATURE" if current_constraint.subtarget:
                    bone = current_constraint.target.pose.bones[
                        current_constraint.subtarget
                    ]
                    target_constraints = bone.constraints

                case _:
                    target_constraints = current_constraint.target.constraints

            for target_constraint in target_constraints:
                if target_constraint not in source_constraint_list:
                    continue

                next_target_axis = (
                    current_axis[0] and target_constraint.use_x,
                    current_axis[1] and target_constraint.use_y,
                    current_axis[2] and target_constraint.use_z,
                )
                if next_target_axis == (False, False, False):
                    continue

                if target_constraint != search_constraint:
                    current_constraints.append((target_constraint, next_target_axis))
                    continue

                excluded_constraint_list.append(search_constraint)

                found = True
                break

            if found:
                break

    detected_circular_dependency_constraints: list[CandidateConstraitProperties] = [
        (constraint_type, element, index, True, constraint)
        if constraint in excluded_constraint_list
        else (constraint_type, element, index, False, constraint)
        for (
            constraint_type,
            element,
            index,
            _is_circular_dependency,
            constraint,
        ) in candidate_constraints_list
    ]

    return detected_circular_dependency_constraints


def add_items2constraint_ui_list(constraint_type: Literal["OBJECT", "BONE"]) -> int:
    """
    現在の描画タイプに応じて､Constraintの確認/設定を行なうUI Listの描画候補アイテムをコレクションプロパティに追加する｡
    UI Listのrows入力用にアイテム数を返す｡

    Returns
    -------
    int
        リストに表示するアイテム数｡

    """

    items = get_ui_list_prop4custom_filter("CONSTRAINT")

    # Current Sceneに存在するオブジェクトから対象オブジェクトを取得する｡
    candidate_constraints_list = get_candidate_constraints_for_draw_ui(constraint_type)
    # logger.debug(len(candidate_constraints_list))

    candidate_constraints_list = exclude_circular_dependency_constraints(
        candidate_constraints_list
    )
    # pprint(candidate_constraints_list)

    # コレクションプロパティの初期化処理｡
    items.clear()
    row_length = 0
    current_constraint_type = None
    type_index = None

    for (
        vrm_constraint_type,
        element,
        index,
        is_circular_dependency,
        constraint,
    ) in candidate_constraints_list:
        # 現在処理中のコンストレイントタイプが変化したらラベルを追加する｡
        if current_constraint_type != type(vrm_constraint_type):
            current_constraint_type = type(vrm_constraint_type)
            match vrm_constraint_type:
                case VrmRollConstraint():
                    type_index = 0
                case VrmAimConstraint():
                    type_index = 1
                case VrmRotationConstraint():
                    type_index = 2

            if not row_length == 0:
                row_blank = items.add()
                row_blank.name = "Blank"
                row_blank.is_blank = True

            row_length += 1
            new_label = items.add()
            new_label.is_label = True
            new_label.constraint_type = type_index

        # UI Listのアイテムにコンストレイントを追加する｡
        new_item = items.add()
        new_item.name = element.name
        new_item.constraint_name = constraint.name
        new_item.is_object_constraint = constraint_type == "OBJECT"
        new_item.constraint_type = type_index
        new_item.constraint_index = index
        new_item.is_circular_dependency = is_circular_dependency
        # new_item.is_circular_dependency = True

    ############################################################
    length = len(candidate_constraints_list) + row_length
    return length


"""---------------------------------------------------------
    Draw UI Panel
---------------------------------------------------------"""


def get_current_constraint_axis(source_constraint: Constraint) -> str:
    """
    'source_constraint'で受け取ったRoll ConstraintのAxisの値を取得する｡

    Parameters
    ----------
    source_constraint : Constraint
        処理対象のコンストレイント

    Returns
    -------
    str
        選択されている軸を表す文字列｡

    """

    constraint_axis = (
        source_constraint.use_x,
        source_constraint.use_y,
        source_constraint.use_z,
    )

    match constraint_axis:
        case (1, 0, 0):
            current_axis = "X"

        case (0, 1, 0):
            current_axis = "Y"

        case (0, 0, 1):
            current_axis = "Z"

        case _:
            current_axis = "X"

    return current_axis


def draw_name(layout: UILayout, source_constraint: Constraint):
    """
    コンストレイントのパラメーターの内､名前を描画する

    Parameters
    ----------
    layout : UILayout
        描画対象のUILayout

    source_constraint : Constraint
        名前を描画されるコンストレイント

    """

    col = layout.column()
    col.prop(source_constraint, "name", text="Constraint Name")


def draw_target(
    layout: UILayout, source_constraint: Constraint, target_is_object: bool = False
):
    """
    コンストレイントのパラメーターの内､ターゲットに関わる部分を描画する

    Parameters
    ----------
    layout : UILayout
        描画対象のUILayout

    source_constraint : Constraint
        パラメーターを描画されるコンストレイント

    target_is_object : bool,  --optional
        処理対象のコンストレイントがオブジェクトコンストレイントである場合はTrueを選ぶ｡,
        by default : False

    """

    col = layout.column()

    if target_is_object:
        col.prop(source_constraint, "target")

    match source_constraint.target.type:
        case "ARMATURE":
            col.prop_search(
                source_constraint,
                "subtarget",
                source_constraint.target.data,
                "bones",
                text="Target Bone",
            )

            if source_constraint.subtarget and hasattr(source_constraint, "head_tail"):
                row = col.row(align=True)
                row.use_property_decorate = False
                sub = row.row(align=True)
                sub.prop(source_constraint, "head_tail")

                sub.prop(
                    source_constraint, "use_bbone_shape", text="", icon="IPO_BEZIER"
                )
                row.prop_decorator(source_constraint, "head_tail")

        case _:
            col.prop_search(
                source_constraint,
                "target",
                bpy.data,
                "objects",
                text="Target Object",
            )


def draw_influence(
    layout: UILayout,
    source_constraint: Constraint,
):
    """
    コンストレイントのパラメーターの内､影響度に関わる部分を描画する｡

    Parameters
    ----------
    layout : UILayout
        描画対象のUILayout

    source_constraint : Constraint
        パラメーターを描画されるコンストレイント

    """

    layout.separator()
    row = layout.row(align=True)
    row.prop(source_constraint, "influence")
    row.operator("constraint.disable_keep_transform", text="", icon="CANCEL")


def draw_roll_constraint(
    layout: UILayout,
    source_constraint: CopyRotationConstraint,
):
    """
    UI上にRoll Constraintのパラメーターを描画する

    Parameters
    ----------
    layout : UILayout
        描画対象のUILayout

    source_constraint : Constraint
        パラメーターを描画されるコンストレイント

    """

    current_axis = get_current_constraint_axis(source_constraint)
    wm_constraint_prop = get_wm_vrm1_constraint_prop()
    wm_constraint_prop.is_locked_update = True
    wm_constraint_prop.axis = current_axis
    wm_constraint_prop.is_locked_update = False

    layout.use_property_split = True
    layout.use_property_decorate = True

    draw_name(
        layout,
        source_constraint,
    )

    draw_target(
        layout,
        source_constraint,
    )

    row = layout.row(align=True)
    row.alignment = "LEFT"
    row.label(text="Axis")
    row.prop(wm_constraint_prop, "axis", text=" ", expand=True)

    draw_influence(
        layout,
        source_constraint,
    )


def draw_aim_constraint(
    layout: UILayout,
    source_constraint: CopyRotationConstraint,
):
    """
    UI上にAim Constraintのパラメーターを描画する

    Parameters
    ----------
    layout : UILayout
        描画対象のUILayout

    source_constraint : Constraint
        パラメーターを描画されるコンストレイント

    """

    layout.use_property_split = True
    layout.use_property_decorate = True

    draw_name(
        layout,
        source_constraint,
    )

    draw_target(
        layout,
        source_constraint,
    )

    row = layout.row()
    row.prop(source_constraint, "track_axis", expand=True)

    draw_influence(
        layout,
        source_constraint,
    )


def draw_rotation_constraint(
    layout: UILayout,
    source_constraint: DampedTrackConstraint,
):
    """
    UI上にRotation Constraintのパラメーターを描画する

    Parameters
    ----------
    layout : UILayout
        描画対象のUILayout

    source_constraint : Constraint
        パラメーターを描画されるコンストレイント

    """
    layout.use_property_split = True
    layout.use_property_decorate = True

    draw_name(
        layout,
        source_constraint,
    )

    draw_target(
        layout,
        source_constraint,
    )

    draw_influence(
        layout,
        source_constraint,
    )


# ----------------------------------------------------------
#    For Operator
# ----------------------------------------------------------
def detect_constraint_or_label() -> VRMHELPER_WM_vrm1_constraint_list_items:
    if not (constraint_ui_list := get_ui_list_prop4custom_filter("CONSTRAINT")):
        return

    active_index = get_vrm1_active_index_prop("CONSTRAINT")
    active_item: VRMHELPER_WM_vrm1_constraint_list_items = constraint_ui_list[
        active_index
    ]

    if active_item.is_blank or active_item.is_label:
        return

    return active_item


def detect_constrainted_and_target_element() -> (
    tuple[Object | PoseBone, Object | PoseBone] | tuple[None, None]
):
    """
    現在のオブジェクト/ポーズボーンの選択状況からコンストレイント作成が可能な状態であるかどうかを
    判定し､可能な状態であれば'コンストレイントが作成されるオブジェクト'と'コンストレイントのターゲット'をタプルで返す｡

    Returns
    -------
    tuple[Object | PoseBone, Object | PoseBone] | tuple(None,None)
        コンストレイントが作成されるオブジェクトとコンストレイントターゲットのペアを格納したタプル｡
        コンストレイントを作成できない状態である場合はNoneのペアを格納したタプルを返す｡

    """

    context = bpy.context
    no_target = (None, None)
    match context.mode:
        # Object Modeの場合
        case "OBJECT":
            source_elements = context.selected_objects  # 'Object & Object'
            # アクティブオブジェクトが選択オブジェクトに含まれているかつ選択オブジェクト数が2個である｡
            if not (
                (active_element := context.active_object) in source_elements
                and len(context.selected_objects) == 2
            ):
                return no_target

        # Pose Modeの場合
        case "POSE":
            source_elements = context.selected_pose_bones
            # アクティブボーンが存在する｡
            if not (active_element := context.active_pose_bone):
                return no_target

            # ポーズボーンが2つ選択されている状態を優先する｡
            match len(context.selected_pose_bones):
                case 2:
                    source_elements = context.selected_pose_bones  # Bone & Bone'

                # 選択ポーズボーン数が2以外の場合はアクティブボーンと他オブジェクトとのコンビネーションとなる｡
                case _:
                    # 選択オブジェクト数が2である｡
                    if not len(context.selected_objects) == 2:
                        return no_target

                    excluded_armature_list = [
                        obj
                        for obj in context.selected_objects
                        if obj.type != "ARMATURE"
                    ]
                    target_object = excluded_armature_list[0]
                    source_elements = [active_element, target_object]  # 'Bone & Object'

    constrainted_element = source_elements.pop(source_elements.index(active_element))
    target_element = source_elements[0]

    return constrainted_element, target_element


def set_roll_and_rotation_common_paramette(source_constraint: CopyRotationConstraint):
    source_constraint.mix_mode = "ADD"
    source_constraint.owner_space = "LOCAL"
    source_constraint.target_space = "LOCAL"


def set_vrm_constraint_parametters(
    source_constraint: CopyRotationConstraint | DampedTrackConstraint,
    constraint_type: Literal["ROLL", "AIM", "ROTATION"],
):
    match constraint_type:
        case "ROLL":
            logger.debug("Created VRM Constraint : Roll Constraint")
            set_roll_and_rotation_common_paramette(source_constraint)
            source_constraint.use_y = False
            source_constraint.use_z = False

        case "AIM":
            logger.debug("Created VRM Constraint : Aim Constraint")

        case "ROTATION":
            logger.debug("Created VRM Constraint : Rotation Constraint")
            set_roll_and_rotation_common_paramette(source_constraint)
