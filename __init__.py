bl_info = {
    "name": "Helper Addon for VRM Addon",
    "author": "Yu-Lit",
    "version": (0, 1, 3),
    "blender": (3, 3, 0),
    "location": "Property Panel, Press N in the 3DView",
    "description": "Addon for VRM Setup",
    "warning": "",
    "support": "COMMUNITY",
    "doc_url": "",
    "tracker_url": "",
    "category": "Import-Export",
}


if "bpy" in locals():
    import importlib

    reloadable_modules = [
        "preferences",
        "preparation_logger",
        "debug",
        "preferences",
        "property_groups",
        "operators",
        "vrm1_operators",
        "ui",
        "vrm1_ui",
    ]

    for module in reloadable_modules:
        if module in locals():
            importlib.reload(locals()[module])

else:
    from .Logging import preparation_logger
    from . import preferences
    from . import property_groups
    from . import operators
    from .Vrm1 import vrm1_operators
    from . import ui
    from .Vrm1 import vrm1_ui


import bpy
from bpy.types import (
    WindowManager,
    Scene,
)
from bpy.props import (
    PointerProperty,
)

from .debug import (
    launch_debug_server,
)


"""---------------------------------------------------------
------------------------------------------------------------
    Logger
------------------------------------------------------------
---------------------------------------------------------"""
from .Logging.preparation_logger import preparating_logger

logger = preparating_logger(__name__)


"""---------------------------------------------------------
------------------------------------------------------------
    REGISTER/UNREGISTER
------------------------------------------------------------
---------------------------------------------------------"""
CLASSES = (
    *preferences.CLASSES,
    *property_groups.CLASSES,
    *operators.CLASSES,
    *vrm1_operators.CLASSES,
    *vrm1_ui.CLASSES,
    *ui.CLASSES,
)


def register():
    for cls in CLASSES:
        try:
            bpy.utils.register_class(cls)
        except:
            logger.debug(f"{cls.__name__} : already registred")

    ## Property Group の登録
    WindowManager.vrm_helper = PointerProperty(
        type=property_groups.VRMHELPER_WM_root_property_group
    )
    Scene.vrm_helper = PointerProperty(
        type=property_groups.VRMHELPER_SCENE_root_property_group
    )

    # デバッグ用
    # launch_debug_server()


def unregister():
    del WindowManager.vrm_helper
    del Scene.vrm_helper

    for cls in CLASSES:
        if hasattr(bpy.types, cls.__name__):
            bpy.utils.unregister_class(cls)
            logger.debug(f"{cls.__name__} unregistred")
