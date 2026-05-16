import Foundation
import Combine

class AppState: ObservableObject {
    @Published var isTracking = false
    @Published var isSending = false
    @Published var targetIP: String = "192.168.1.255"
    @Published var targetPort: UInt16 = 49983
    @Published var smoothingAlpha: Float = 0.7
    @Published var currentFPS: Int = 0
    @Published var packetsSent: UInt64 = 0
    @Published var trackingQuality: String = "None"

    @Published var blendShapeValues: [Float] = Array(repeating: 0, count: 52)
    @Published var headRotation: SIMD4<Float> = .zero
    @Published var leftEyeDirection: SIMD3<Float> = .zero
    @Published var rightEyeDirection: SIMD3<Float> = .zero
}
