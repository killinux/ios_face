import json
import os
import math
from .arkit_constants import ARKIT_INDEX


class MappingEngine:
    def __init__(self):
        self.mappings = []
        self.load_default_mapping()

    def load_default_mapping(self):
        mapping_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "mapping", "default_mmd_mapping.json"
        )
        if os.path.exists(mapping_path):
            with open(mapping_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.mappings = data.get("mappings", [])
                self.head_bone_config = data.get("head_bone", {})
                self.eye_bone_config = data.get("eye_bones", {})

    def load_mapping_file(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.mappings = data.get("mappings", [])
            self.head_bone_config = data.get("head_bone", {})
            self.eye_bone_config = data.get("eye_bones", {})

    def compute(self, blendshapes: list) -> dict:
        result = {}
        for mapping in self.mappings:
            target = mapping["target_morph"]
            value = self._compute_single(mapping, blendshapes, result)
            result[target] = max(0.0, min(1.0, value))
        return result

    def _compute_single(self, mapping: dict, blendshapes: list, computed: dict) -> float:
        mapping_type = mapping.get("type", "direct")
        sources = mapping.get("sources", [])
        threshold = mapping.get("threshold", 0.0)

        if mapping_type == "direct":
            value = self._get_source_value(sources[0], blendshapes) if sources else 0.0

        elif mapping_type == "weighted_sum":
            value = sum(self._get_source_value(s, blendshapes) for s in sources)
            subtract = mapping.get("subtract", [])
            value -= sum(self._get_source_value(s, blendshapes) for s in subtract)

        elif mapping_type == "combined_max":
            value = max((self._get_source_value(s, blendshapes) for s in sources), default=0.0)

        elif mapping_type == "combined_avg":
            values = [self._get_source_value(s, blendshapes) for s in sources]
            value = sum(values) / len(values) if values else 0.0

        else:
            value = 0.0

        value = self._apply_curve(value, mapping.get("curve", "linear"))

        if value < threshold:
            value = 0.0

        suppress = mapping.get("suppress_when")
        if suppress and suppress["morph"] in computed:
            if computed[suppress["morph"]] > suppress.get("above", 0.7):
                value = 0.0

        return value

    def _get_source_value(self, source: dict, blendshapes: list) -> float:
        arkit_name = source.get("arkit", "")
        weight = source.get("weight", 1.0)
        idx = ARKIT_INDEX.get(arkit_name, -1)
        if idx < 0 or idx >= len(blendshapes):
            return 0.0
        return blendshapes[idx] * weight

    def _apply_curve(self, value: float, curve: str) -> float:
        if curve == "linear":
            return value
        elif curve == "ease_in":
            return value * value
        elif curve == "ease_out":
            return 1.0 - (1.0 - value) ** 2
        elif curve.startswith("power_"):
            try:
                power = float(curve.split("_")[1])
                return math.pow(max(0.0, value), power)
            except (IndexError, ValueError):
                return value
        elif curve == "sigmoid":
            if value <= 0:
                return 0.0
            if value >= 1:
                return 1.0
            x = (value - 0.5) * 10
            return 1.0 / (1.0 + math.exp(-x))
        return value

    def convert_head_rotation(self, quaternion: tuple) -> tuple:
        x, y, z, w = quaternion
        scale = self.head_bone_config.get("rotation_scale", 0.8)
        # ARKit right-handed to MMD left-handed: negate x and z
        return (-x * scale, y * scale, -z * scale, w)

    def convert_eye_direction(self, direction: tuple, eye: str = "left") -> tuple:
        x, y, z = direction
        config = self.eye_bone_config.get(eye, {})
        h_limit = math.radians(config.get("h_limit", 30))
        v_limit = math.radians(config.get("v_limit", 20))

        yaw = math.atan2(-x, -z)
        pitch = math.asin(max(-1.0, min(1.0, y)))

        yaw = max(-h_limit, min(h_limit, yaw))
        pitch = max(-v_limit, min(v_limit, pitch))

        return (pitch, yaw)
