import Foundation
import Network

class UDPBroadcaster {
    private var connection: NWConnection?
    private let queue = DispatchQueue(label: "com.facecapture.udp", qos: .userInteractive)
    private(set) var isSending = false

    func start(host: String, port: UInt16) {
        let endpoint = NWEndpoint.hostPort(
            host: NWEndpoint.Host(host),
            port: NWEndpoint.Port(rawValue: port)!
        )

        let params = NWParameters.udp
        params.allowLocalEndpointReuse = true
        if host.hasSuffix(".255") {
            params.allowLocalEndpointReuse = true
            params.requiredInterfaceType = .wifi
        }

        connection = NWConnection(to: endpoint, using: params)
        connection?.stateUpdateHandler = { [weak self] state in
            switch state {
            case .ready:
                self?.isSending = true
            case .failed, .cancelled:
                self?.isSending = false
            default:
                break
            }
        }
        connection?.start(queue: queue)
    }

    func send(data: Data) {
        guard isSending else { return }
        connection?.send(content: data, completion: .contentProcessed { _ in })
    }

    func stop() {
        connection?.cancel()
        connection = nil
        isSending = false
    }
}
