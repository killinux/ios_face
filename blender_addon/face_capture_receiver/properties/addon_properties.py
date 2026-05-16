import bpy
from bpy.props import IntProperty, BoolProperty, FloatProperty, StringProperty, EnumProperty


class FaceCapProperties(bpy.types.PropertyGroup):
    port: IntProperty(
        name="UDP Port",
        default=49983,
        min=1024,
        max=65535,
        description="UDP port to listen on"
    )

    is_receiving: BoolProperty(
        name="Receiving",
        default=False,
    )

    target_mesh: StringProperty(
        name="Target Mesh",
        description="Name of the mesh object with shape keys to drive"
    )

    target_armature: StringProperty(
        name="Target Armature",
        description="Name of the armature for head/eye bone rotation"
    )

    smoothing: FloatProperty(
        name="Smoothing",
        default=0.3,
        min=0.0,
        max=0.95,
        description="Additional Blender-side smoothing (0 = none, higher = smoother)"
    )

    head_rotation_enabled: BoolProperty(
        name="Head Rotation",
        default=True,
        description="Drive head bone rotation from face tracking data"
    )

    eye_tracking_enabled: BoolProperty(
        name="Eye Tracking",
        default=True,
        description="Drive eye bone rotation from gaze direction"
    )

    mapping_preset: EnumProperty(
        name="Mapping Preset",
        items=[
            ('DEFAULT', "Standard MMD", "Default mapping for standard MMD models"),
            ('TDA', "TDA Style", "Mapping optimized for TDA-style models"),
            ('CUSTOM', "Custom", "Custom user-defined mapping"),
        ],
        default='DEFAULT',
        description="Morph mapping preset to use"
    )

    show_debug: BoolProperty(
        name="Show Debug",
        default=False,
        description="Show real-time blendshape values"
    )

    fps: IntProperty(name="FPS", default=0)
    packets_received: IntProperty(name="Packets", default=0)
    packets_dropped: IntProperty(name="Dropped", default=0)
