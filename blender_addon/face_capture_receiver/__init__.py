bl_info = {
    "name": "Face Capture Receiver",
    "author": "ios_face project",
    "version": (1, 0, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > FaceCap",
    "description": "Receive ARKit face tracking data over UDP and drive MMD model morphs in real-time",
    "category": "Animation",
}

import bpy
from . import properties
from .operators import receiver_operator, calibration_operator
from .panels import main_panel

classes = [
    properties.addon_properties.FaceCapProperties,
    receiver_operator.FACECAP_OT_start_receiver,
    receiver_operator.FACECAP_OT_stop_receiver,
    calibration_operator.FACECAP_OT_calibrate_neutral,
    main_panel.FACECAP_PT_main_panel,
    main_panel.FACECAP_PT_mapping_panel,
    main_panel.FACECAP_PT_debug_panel,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.facecap = bpy.props.PointerProperty(type=properties.addon_properties.FaceCapProperties)


def unregister():
    del bpy.types.Scene.facecap
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
