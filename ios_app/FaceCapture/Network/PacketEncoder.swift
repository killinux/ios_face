import Foundation

struct FaceCapturePacket {
    static let magic: [UInt8] = [0xFA, 0xCE]
    static let version: UInt8 = 1
    static let packetSize = 264

    var sequenceNumber: UInt32
    var timestamp: Float32
    var flags: UInt32
    var blendShapes: [Float32]  // 52 values
    var headQuaternion: SIMD4<Float32>  // x, y, z, w
    var leftEyeDirection: SIMD3<Float32>
    var rightEyeDirection: SIMD3<Float32>

    func encode() -> Data {
        var data = Data(capacity: Self.packetSize)

        data.append(contentsOf: Self.magic)
        data.append(Self.version)
        data.append(0) // type: face data

        withUnsafeBytes(of: sequenceNumber.littleEndian) { data.append(contentsOf: $0) }
        withUnsafeBytes(of: timestamp.bitPattern.littleEndian) { data.append(contentsOf: $0) }
        withUnsafeBytes(of: flags.littleEndian) { data.append(contentsOf: $0) }

        for value in blendShapes {
            withUnsafeBytes(of: value.bitPattern.littleEndian) { data.append(contentsOf: $0) }
        }

        withUnsafeBytes(of: headQuaternion.x.bitPattern.littleEndian) { data.append(contentsOf: $0) }
        withUnsafeBytes(of: headQuaternion.y.bitPattern.littleEndian) { data.append(contentsOf: $0) }
        withUnsafeBytes(of: headQuaternion.z.bitPattern.littleEndian) { data.append(contentsOf: $0) }
        withUnsafeBytes(of: headQuaternion.w.bitPattern.littleEndian) { data.append(contentsOf: $0) }

        withUnsafeBytes(of: leftEyeDirection.x.bitPattern.littleEndian) { data.append(contentsOf: $0) }
        withUnsafeBytes(of: leftEyeDirection.y.bitPattern.littleEndian) { data.append(contentsOf: $0) }
        withUnsafeBytes(of: leftEyeDirection.z.bitPattern.littleEndian) { data.append(contentsOf: $0) }

        withUnsafeBytes(of: rightEyeDirection.x.bitPattern.littleEndian) { data.append(contentsOf: $0) }
        withUnsafeBytes(of: rightEyeDirection.y.bitPattern.littleEndian) { data.append(contentsOf: $0) }
        withUnsafeBytes(of: rightEyeDirection.z.bitPattern.littleEndian) { data.append(contentsOf: $0) }

        return data
    }
}
