import bpy


class FACECAP_PT_main_panel(bpy.types.Panel):
    bl_label = "Face Capture"
    bl_idname = "FACECAP_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "FaceCap"

    def draw(self, context):
        layout = self.layout
        props = context.scene.facecap

        # Connection
        box = layout.box()
        box.label(text="Connection", icon='PLUGIN')
        row = box.row()
        row.prop(props, "port")

        if props.is_receiving:
            box.operator("facecap.stop_receiver", text="Stop", icon='PAUSE')
            row = box.row()
            row.label(text=f"FPS: {props.fps}")
            row.label(text=f"Recv: {props.packets_received}")
            row.label(text=f"Drop: {props.packets_dropped}")
        else:
            box.operator("facecap.start_receiver", text="Start", icon='PLAY')

        layout.separator()

        # Target
        box = layout.box()
        box.label(text="Target", icon='MESH_DATA')
        box.prop_search(props, "target_mesh", bpy.data, "objects", text="Mesh")
        box.prop_search(props, "target_armature", bpy.data, "objects", text="Armature")

        layout.separator()

        # Settings
        box = layout.box()
        box.label(text="Settings", icon='PREFERENCES')
        box.prop(props, "smoothing", slider=True)
        box.prop(props, "head_rotation_enabled")
        box.prop(props, "eye_tracking_enabled")
        box.prop(props, "mapping_preset")

        layout.separator()

        # Calibration
        box = layout.box()
        box.label(text="Calibration", icon='ORIENTATION_NORMAL')
        box.operator("facecap.calibrate_neutral", text="Set Neutral Pose", icon='SNAP_FACE')


class FACECAP_PT_mapping_panel(bpy.types.Panel):
    bl_label = "Morph Mapping"
    bl_idname = "FACECAP_PT_mapping_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "FaceCap"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        props = context.scene.facecap

        mesh_obj = bpy.data.objects.get(props.target_mesh)
        if not mesh_obj or not mesh_obj.data.shape_keys:
            layout.label(text="Select a mesh with shape keys", icon='INFO')
            return

        key_blocks = mesh_obj.data.shape_keys.key_blocks
        layout.label(text=f"Shape Keys: {len(key_blocks) - 1}", icon='SHAPEKEY_DATA')

        col = layout.column(align=True)
        for kb in key_blocks[1:]:  # Skip Basis
            row = col.row(align=True)
            row.label(text=kb.name)
            bar_text = f"{kb.value:.2f}"
            row.label(text=bar_text)


class FACECAP_PT_debug_panel(bpy.types.Panel):
    bl_label = "Debug"
    bl_idname = "FACECAP_PT_debug_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "FaceCap"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        props = context.scene.facecap

        layout.prop(props, "show_debug")

        if not props.show_debug:
            return

        from ..core.arkit_constants import ARKIT_BLENDSHAPE_NAMES
        from ..operators.receiver_operator import _receiver

        if _receiver is None:
            layout.label(text="Receiver not active", icon='ERROR')
            return

        face_data = _receiver.get_latest()
        if face_data is None:
            layout.label(text="No data", icon='ERROR')
            return

        col = layout.column(align=True)
        for i, name in enumerate(ARKIT_BLENDSHAPE_NAMES):
            value = face_data.blendshapes[i] if i < len(face_data.blendshapes) else 0
            row = col.row(align=True)
            row.label(text=f"{name[:16]}")
            row.progress(factor=value, type='BAR', text=f"{value:.2f}")
