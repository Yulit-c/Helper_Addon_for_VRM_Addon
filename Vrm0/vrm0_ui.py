if "bpy" in locals():
    import importlib

    reloadable_modules = [
        "preparation_logger",
        "property_groups",
        "utils_common",
        "operators",
        "vrm0_operators",
    ]

    for module in reloadable_modules:
        if module in locals():
            importlib.reload(locals()[module])

else:
    from ..Logging import preparation_logger
    from .. import property_groups
    from .. import utils_common
    from .. import operators
    from . import vrm0_operators


import bpy


from ..addon_classes import (
    ReferenceVrm1ExpressionPropertyGroup,
    # ----------------------------------------------------------
    VRMHELPER_UL_base,
)

from ..addon_constants import (
    PRESET_EXPRESSION_NAME_DICT,
    EXPRESSION_ICON_DICT,
    EXPRESSION_OPTION_ICON,
    MOVE_UP_CUSTOM_EXPRESSION_OPS_NAME,
    MOVE_DOWN_CUSTOM_EXPRESSION_OPS_NAME,
    JOINT_PROP_NAMES,
)

from ..property_groups import (
    get_target_armature,
    get_target_armature_data,
    get_vrm0_scene_root_prop,
)

from ..utils_common import (
    get_properties_to_dict,
    define_ui_list_rows,
    set_properties_to_from_dict,
)

from ..utils_vrm_base import (
    get_vrm_extension_root_property,
    get_vrm_extension_property,
    get_vrm1_extension_property_expression,
    is_existing_target_armature,
    check_addon_mode,
)


from ..operators import (
    VRMHELPER_OT_reset_shape_keys_on_selected_objects,
)

"""
from .vrm0_operators import (
    # ----------------------------------------------------------
    #    First Person
    # ----------------------------------------------------------
)
"""

"""---------------------------------------------------------
------------------------------------------------------------
    Logger
------------------------------------------------------------
---------------------------------------------------------"""
from ..Logging.preparation_logger import preparating_logger

logger = preparating_logger(__name__)
#######################################################


"""---------------------------------------------------------
    First Person
---------------------------------------------------------"""

"""---------------------------------------------------------
------------------------------------------------------------
    Resiter Target
------------------------------------------------------------
---------------------------------------------------------"""
CLASSES = (
    # ----------------------------------------------------------
    #    UI List
    # ----------------------------------------------------------
)
