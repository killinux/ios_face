import bpy
from ..core.udp_receiver import UDPReceiver
from .receiver_operator import _receiver


class FACECAP_OT_calibrate_neutral(bpy.types.Operator):
    bl_idname = "facecap.calibrate_neutral"
    bl_label = "Calibrate Neutral"
    bl_description = "Capture current face pose as neutral baseline (resets all morphs to zero at this pose)"

    @classmethod
    def poll(cls, context):
        return context.scene.facecap.is_receiving and _receiver is not None

    def execute(self, context):
        if _receiver is None:
            self.report({'WARNING'}, "Receiver not active")
            return {'CANCELLED'}

        face_data = _receiver.get_latest()
        if face_data is None:
            self.report({'WARNING'}, "No face data available")
            return {'CANCELLED'}

        # Store current values as neutral offset
        # This will be subtracted from future readings
        context.scene.facecap["neutral_offset"] = list(face_data.blendshapes)
        self.report({'INFO'}, "Neutral pose calibrated")
        return {'FINISHED'}
