import Foundation
import simd

class FaceDataSmoother {
    private var smoothedBlendShapes: [Float] = Array(repeating: 0, count: 52)
    private var smoothedHeadRotation: SIMD4<Float> = SIMD4(0, 0, 0, 1)
    private var smoothedLeftEye: SIMD3<Float> = .zero
    private var smoothedRightEye: SIMD3<Float> = .zero
    private var initialized = false

    var blendShapeAlpha: Float = 0.7
    var headRotationAlpha: Float = 0.5
    var eyeAlpha: Float = 0.6

    func smooth(
        blendShapes: [Float],
        headRotation: SIMD4<Float>,
        leftEye: SIMD3<Float>,
        rightEye: SIMD3<Float>
    ) -> (blendShapes: [Float], headRotation: SIMD4<Float>, leftEye: SIMD3<Float>, rightEye: SIMD3<Float>) {
        guard initialized else {
            smoothedBlendShapes = blendShapes
            smoothedHeadRotation = headRotation
            smoothedLeftEye = leftEye
            smoothedRightEye = rightEye
            initialized = true
            return (blendShapes, headRotation, leftEye, rightEye)
        }

        for i in 0..<min(blendShapes.count, 52) {
            smoothedBlendShapes[i] = blendShapeAlpha * blendShapes[i] + (1 - blendShapeAlpha) * smoothedBlendShapes[i]
        }

        smoothedHeadRotation = slerp(smoothedHeadRotation, headRotation, t: headRotationAlpha)
        smoothedLeftEye = mix(smoothedLeftEye, leftEye, t: eyeAlpha)
        smoothedRightEye = mix(smoothedRightEye, rightEye, t: eyeAlpha)

        return (smoothedBlendShapes, smoothedHeadRotation, smoothedLeftEye, smoothedRightEye)
    }

    func reset() {
        initialized = false
        smoothedBlendShapes = Array(repeating: 0, count: 52)
        smoothedHeadRotation = SIMD4(0, 0, 0, 1)
    }

    private func slerp(_ q1: SIMD4<Float>, _ q2: SIMD4<Float>, t: Float) -> SIMD4<Float> {
        var dot = simd_dot(q1, q2)
        var target = q2
        if dot < 0 {
            target = -target
            dot = -dot
        }
        if dot > 0.9995 {
            return simd_normalize(q1 + t * (target - q1))
        }
        let theta = acos(min(dot, 1.0))
        let sinTheta = sin(theta)
        let w1 = sin((1 - t) * theta) / sinTheta
        let w2 = sin(t * theta) / sinTheta
        return w1 * q1 + w2 * target
    }

    private func mix(_ a: SIMD3<Float>, _ b: SIMD3<Float>, t: Float) -> SIMD3<Float> {
        return a + t * (b - a)
    }
}
