import bpy
import time
import math
from mathutils import Quaternion
from ..core.udp_receiver import UDPReceiver
from ..core.mapping_engine import MappingEngine

_receiver: UDPReceiver | None = None
_mapping_engine: MappingEngine | None = None


class FACECAP_OT_start_receiver(bpy.types.Operator):
    bl_idname = "facecap.start_receiver"
    bl_label = "Start Receiving"
    bl_description = "Start receiving face capture data over UDP"

    _timer = None
    _last_frame_time = 0
    _frame_count = 0
    _prev_morph_values = {}
    _prev_head_quat = Quaternion((1, 0, 0, 0))

    @classmethod
    def poll(cls, context):
        return not context.scene.facecap.is_receiving

    def execute(self, context):
        global _receiver, _mapping_engine

        props = context.scene.facecap

        _receiver = UDPReceiver(port=props.port)
        _receiver.start()

        _mapping_engine = MappingEngine()

        self._timer = context.window_manager.event_timer_add(1.0 / 60.0, window=context.window)
        context.window_manager.modal_handler_add(self)

        props.is_receiving = True
        self._last_frame_time = time.time()
        self._frame_count = 0
        self._prev_morph_values = {}

        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        global _receiver

        if event.type == 'TIMER':
            self._process_frame(context)

        if not context.scene.facecap.is_receiving:
            self._cleanup(context)
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def _process_frame(self, context):
        global _receiver, _mapping_engine

        if not _receiver:
            return

        face_data = _receiver.get_latest()
        if face_data is None or not face_data.is_tracking:
            return

        props = context.scene.facecap

        # Update stats
        self._frame_count += 1
        now = time.time()
        if now - self._last_frame_time >= 1.0:
            props.fps = self._frame_count
            props.packets_received = _receiver.packets_received
            props.packets_dropped = _receiver.packets_dropped
            self._frame_count = 0
            self._last_frame_time = now

        # Compute morph values from mapping engine
        morph_values = _mapping_engine.compute(face_data.blendshapes)

        # Apply smoothing
        smooth_factor = props.smoothing
        for morph_name, value in morph_values.items():
            if morph_name in self._prev_morph_values:
                value = value * (1 - smooth_factor) + self._prev_morph_values[morph_name] * smooth_factor
            self._prev_morph_values[morph_name] = value
            morph_values[morph_name] = value

        # Apply to shape keys
        self._apply_shape_keys(context, morph_values)

        # Apply head rotation
        if props.head_rotation_enabled:
            self._apply_head_rotation(context, face_data.head_quaternion)

        # Apply eye tracking
        if props.eye_tracking_enabled:
            self._apply_eye_rotation(context, face_data.left_eye_direction, face_data.right_eye_direction)

        # Force viewport update
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

    def _apply_shape_keys(self, context, morph_values: dict):
        props = context.scene.facecap
        mesh_obj = bpy.data.objects.get(props.target_mesh)
        if not mesh_obj or not mesh_obj.data.shape_keys:
            return

        key_blocks = mesh_obj.data.shape_keys.key_blocks
        for morph_name, value in morph_values.items():
            if morph_name in key_blocks:
                key_blocks[morph_name].value = value

    def _apply_head_rotation(self, context, quaternion: tuple):
        global _mapping_engine
        props = context.scene.facecap
        armature = bpy.data.objects.get(props.target_armature)
        if not armature or armature.type != 'ARMATURE':
            return

        converted = _mapping_engine.convert_head_rotation(quaternion)
        target_quat = Quaternion((converted[3], converted[0], converted[1], converted[2]))

        head_config = _mapping_engine.head_bone_config
        bone_name = head_config.get("target", "頭")
        fallbacks = head_config.get("fallback_targets", [])

        bone = armature.pose.bones.get(bone_name)
        if not bone:
            for fallback in fallbacks:
                bone = armature.pose.bones.get(fallback)
                if bone:
                    break

        if bone:
            smooth = context.scene.facecap.smoothing
            self._prev_head_quat = self._prev_head_quat.slerp(target_quat, 1.0 - smooth)
            bone.rotation_quaternion = self._prev_head_quat

    def _apply_eye_rotation(self, context, left_eye_dir: tuple, right_eye_dir: tuple):
        global _mapping_engine
        props = context.scene.facecap
        armature = bpy.data.objects.get(props.target_armature)
        if not armature or armature.type != 'ARMATURE':
            return

        eye_config = _mapping_engine.eye_bone_config

        for eye_side, direction in [("left", left_eye_dir), ("right", right_eye_dir)]:
            config = eye_config.get(eye_side, {})
            bone_name = config.get("target", "左目" if eye_side == "left" else "右目")
            fallbacks = config.get("fallback_targets", [])

            bone = armature.pose.bones.get(bone_name)
            if not bone:
                for fallback in fallbacks:
                    bone = armature.pose.bones.get(fallback)
                    if bone:
                        break

            if bone:
                pitch, yaw = _mapping_engine.convert_eye_direction(direction, eye_side)
                eye_quat = Quaternion((1, 0, 0, 0))
                eye_quat @= Quaternion((0, 1, 0), yaw)
                eye_quat @= Quaternion((1, 0, 0), pitch)
                bone.rotation_quaternion = eye_quat

    def _cleanup(self, context):
        global _receiver
        if self._timer:
            context.window_manager.event_timer_remove(self._timer)
            self._timer = None
        if _receiver:
            _receiver.stop()
            _receiver = None


class FACECAP_OT_stop_receiver(bpy.types.Operator):
    bl_idname = "facecap.stop_receiver"
    bl_label = "Stop Receiving"
    bl_description = "Stop receiving face capture data"

    @classmethod
    def poll(cls, context):
        return context.scene.facecap.is_receiving

    def execute(self, context):
        context.scene.facecap.is_receiving = False
        return {'FINISHED'}
