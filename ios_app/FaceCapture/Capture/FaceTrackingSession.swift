import ARKit
import Combine

class FaceTrackingSession: NSObject, ObservableObject {
    private var session: ARSession?
    private let broadcaster = UDPBroadcaster()
    private let smoother = FaceDataSmoother()
    private var sequenceNumber: UInt32 = 0
    private var sessionStartTime: TimeInterval = 0
    private var frameCount: Int = 0
    private var lastFPSUpdate: TimeInterval = 0

    weak var appState: AppState?

    static let blendShapeOrder: [ARFaceAnchor.BlendShapeLocation] = [
        .browDownLeft, .browDownRight, .browInnerUp, .browOuterUpLeft, .browOuterUpRight,
        .cheekPuff, .cheekSquintLeft, .cheekSquintRight,
        .eyeBlinkLeft, .eyeBlinkRight, .eyeLookDownLeft, .eyeLookDownRight,
        .eyeLookInLeft, .eyeLookInRight, .eyeLookOutLeft, .eyeLookOutRight,
        .eyeLookUpLeft, .eyeLookUpRight, .eyeSquintLeft, .eyeSquintRight,
        .eyeWideLeft, .eyeWideRight,
        .jawForward, .jawLeft, .jawOpen, .jawRight,
        .mouthClose, .mouthDimpleLeft, .mouthDimpleRight, .mouthFrownLeft, .mouthFrownRight,
        .mouthFunnel, .mouthLeft, .mouthLowerDownLeft, .mouthLowerDownRight,
        .mouthPressLeft, .mouthPressRight, .mouthPucker, .mouthRight,
        .mouthRollLower, .mouthRollUpper, .mouthShrugLower, .mouthShrugUpper,
        .mouthSmileLeft, .mouthSmileRight, .mouthStretchLeft, .mouthStretchRight,
        .mouthUpperUpLeft, .mouthUpperUpRight,
        .noseSneerLeft, .noseSneerRight,
        .tongueOut
    ]

    static var isSupported: Bool {
        ARFaceTrackingConfiguration.isSupported
    }

    func start() {
        guard Self.isSupported else { return }

        let configuration = ARFaceTrackingConfiguration()
        configuration.isWorldTrackingEnabled = false
        configuration.maximumNumberOfTrackedFaces = 1

        session = ARSession()
        session?.delegate = self
        session?.run(configuration, options: [.resetTracking, .removeExistingAnchors])
        sessionStartTime = CACurrentMediaTime()

        appState?.isTracking = true
    }

    func stop() {
        session?.pause()
        session = nil
        appState?.isTracking = false
    }

    func startSending(host: String, port: UInt16) {
        broadcaster.start(host: host, port: port)
        appState?.isSending = true
    }

    func stopSending() {
        broadcaster.stop()
        appState?.isSending = false
    }

    func setSmoothingAlpha(_ alpha: Float) {
        smoother.blendShapeAlpha = alpha
    }
}

extension FaceTrackingSession: ARSessionDelegate {
    func session(_ session: ARSession, didUpdate anchors: [ARAnchor]) {
        guard let faceAnchor = anchors.compactMap({ $0 as? ARFaceAnchor }).first else { return }

        let blendShapes = Self.blendShapeOrder.map { location -> Float in
            (faceAnchor.blendShapeCoefficients[location] as? Float) ?? 0.0
        }

        let transform = faceAnchor.transform
        let quaternion = simd_quaternion(transform)
        let headQuat = SIMD4<Float>(quaternion.imag.x, quaternion.imag.y, quaternion.imag.z, quaternion.real)

        let leftEyeTransform = faceAnchor.leftEyeTransform
        let rightEyeTransform = faceAnchor.rightEyeTransform
        let leftEyeDir = SIMD3<Float>(leftEyeTransform.columns.2.x, leftEyeTransform.columns.2.y, leftEyeTransform.columns.2.z)
        let rightEyeDir = SIMD3<Float>(rightEyeTransform.columns.2.x, rightEyeTransform.columns.2.y, rightEyeTransform.columns.2.z)

        let smoothed = smoother.smooth(
            blendShapes: blendShapes,
            headRotation: headQuat,
            leftEye: leftEyeDir,
            rightEye: rightEyeDir
        )

        let flags: UInt32 = faceAnchor.isTracked ? 1 : 0
        let timestamp = Float32(CACurrentMediaTime() - sessionStartTime)

        let packet = FaceCapturePacket(
            sequenceNumber: sequenceNumber,
            timestamp: timestamp,
            flags: flags,
            blendShapes: smoothed.blendShapes,
            headQuaternion: smoothed.headRotation,
            leftEyeDirection: smoothed.leftEye,
            rightEyeDirection: smoothed.rightEye
        )

        broadcaster.send(data: packet.encode())
        sequenceNumber += 1

        updateFPS()
        updateAppState(blendShapes: smoothed.blendShapes, headRotation: smoothed.headRotation,
                      leftEye: smoothed.leftEye, rightEye: smoothed.rightEye)
    }

    private func updateFPS() {
        frameCount += 1
        let now = CACurrentMediaTime()
        if now - lastFPSUpdate >= 1.0 {
            DispatchQueue.main.async { [weak self] in
                self?.appState?.currentFPS = self?.frameCount ?? 0
                self?.appState?.packetsSent = UInt64(self?.sequenceNumber ?? 0)
            }
            frameCount = 0
            lastFPSUpdate = now
        }
    }

    private func updateAppState(blendShapes: [Float], headRotation: SIMD4<Float>,
                                leftEye: SIMD3<Float>, rightEye: SIMD3<Float>) {
        DispatchQueue.main.async { [weak self] in
            self?.appState?.blendShapeValues = blendShapes
            self?.appState?.headRotation = headRotation
            self?.appState?.leftEyeDirection = leftEye
            self?.appState?.rightEyeDirection = rightEye
        }
    }
}
