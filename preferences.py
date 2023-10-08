if "bpy" in locals():
    import importlib

    reloadable_modules = [
        "preparation_logger",
    ]

    for module in reloadable_modules:
        if module in locals():
            importlib.reload(locals()[module])

else:
    from .Logging import preparation_logger

from pathlib import (
    Path,
)
from typing import (
    Literal,
)

import bpy

from bpy.types import (
    AddonPreferences,
)
from bpy.utils import resource_path

from bpy.props import (
    StringProperty,
    BoolProperty,
    FloatVectorProperty,
    FloatProperty,
    EnumProperty,
    IntProperty,
    FloatVectorProperty,
    BoolVectorProperty,
    PointerProperty,
    CollectionProperty,
)

"""---------------------------------------------------------
    Constant
---------------------------------------------------------"""
USER = Path(resource_path("USER"))
ADDON_NAME = "VRM_Helper"

"""----------------------------------------------------
    Logger
-----------------------------------------------------"""
from .Logging.preparation_logger import preparating_logger

logger = preparating_logger(__name__)
#######################################################


"""----------------------------------------------------
#    Addon Preference
-----------------------------------------------------"""


class VRMHELPER_PREF_addon_preferences(AddonPreferences):
    bl_idname = __package__

    # ----------------------------------------------------------
    #    Property Group
    # ----------------------------------------------------------
    addon_collection_dict: dict[str, str] = {
        "ROOT": "VRMHelper_Collection",
        "VRM0_ROOT": "VRMHelper_VRM0",
        "VRM0_BLENDSHAPE_MORPH": "VRMHelper_VRM0_Collider",
        "VRM0_BLENDSHAPE_MATERIAL": "VRMHelper_VRM0_BlendShape_Morph",
        "VRM0_COLLIDER": "VRMHelper_VRM0_BlendShape_Material",
        "VRM1_ROOT": "VRMHelper_VRM1",
        "VRM1_COLLIDER": "VRMHelper_VRM1_Collider",
        "VRM1_EXPRESSION_MORPH": "VRMHelper_VRM1_Expression_Morph",
        "VRM1_EXPRESSION_MATERIAL": "VRMHelper_VRM1_Expression_Material",
    }

    bone_group_filter_name: StringProperty(
        name="Bone Group Filter Name",
        description="Name that the operator creating the joints will recognize as the target bone group",
        default="spring_",
    )

    # ----------------------------------------------------------
    #    UI描画
    # ----------------------------------------------------------
    def draw(self, context):
        layout = self.layout
        for k, v in self.addon_collection_dict.items():
            row = layout.row(align=True)
            row.label(text=k)
            row.label(text=v)

        layout.separator()
        layout.prop(self, "bone_group_filter_name")


"""----------------------------------------------------
#    Function
-----------------------------------------------------"""


def get_addon_preferences() -> VRMHELPER_PREF_addon_preferences:
    """
    アドオンが定義したプリファレンスの変数を取得して使用できるようにする｡
    自身のパッケージ名からプリファレンスを取得する｡


    Returns
    -------
    VRMHELPER_PREF_addon_preferences
        取得したプリファレンスのインスタンス
    """

    return bpy.context.preferences.addons[__package__].preferences


def get_addon_collection_name(
    target_name: Literal[
        "ROOT",
        "VRM0_ROOT",
        "VRM0_BLENDSHAPE_MORPH",
        "VRM0_BLENDSHAPE_MATERIAL",
        "VRM0_COLLIDER",
        "VRM1_ROOT",
        "VRM1_EXPRESSION_MORPH",
        "VRM1_EXPRESSION_MATERIAL",
        "VRM1_COLLIDER",
    ],
) -> str:
    """
    アドオンのプリファレンス内の､アドオンが定義するコレクション名の辞書から
    'target_name'に対応する値を取得する｡

    Parameters
    ----------
    target_name: Literal[
        "ROOT",
        "VRM0_ROOT",
        "VRM0_BLENDSHAPE_MORPH",
        "VRM0_BLENDSHAPE_MATERIAL",
        "VRM0_COLLIDER",
        "VRM1_ROOT",
        "VRM1_EXPRESSION_MORPH"
        "VRM1_EXPRESSION_MATERIAL",
        "VRM1_COLLIDER",
    ]
        取得するコレクション名に対応するキー

    Returns
    -------
    str
        取得したコレクション名の文字列｡

    """

    addon_collection_dict = get_addon_preferences().addon_collection_dict
    return addon_collection_dict[target_name]


"""---------------------------------------------------------
------------------------------------------------------------
    Register Target
------------------------------------------------------------
---------------------------------------------------------"""

CLASSES = (VRMHELPER_PREF_addon_preferences,)
