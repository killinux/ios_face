import SwiftUI
import ARKit

struct CaptureView: View {
    @EnvironmentObject var appState: AppState
    @StateObject private var trackingSession = FaceTrackingSession()
    @State private var showSettings = false

    var body: some View {
        ZStack {
            Color.black.ignoresSafeArea()

            VStack(spacing: 16) {
                headerView
                blendShapePreview
                Spacer()
                controlButtons
            }
            .padding()
        }
        .sheet(isPresented: $showSettings) {
            SettingsView()
        }
        .onAppear {
            trackingSession.appState = appState
        }
    }

    private var headerView: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text("Face Capture")
                    .font(.title2.bold())
                    .foregroundColor(.white)
                HStack(spacing: 12) {
                    StatusDot(active: appState.isTracking, label: "Tracking")
                    StatusDot(active: appState.isSending, label: "Sending")
                    Text("\(appState.currentFPS) fps")
                        .font(.caption)
                        .foregroundColor(.gray)
                }
            }
            Spacer()
            Button(action: { showSettings = true }) {
                Image(systemName: "gear")
                    .font(.title3)
                    .foregroundColor(.white)
            }
        }
    }

    private var blendShapePreview: some View {
        VStack(alignment: .leading, spacing: 2) {
            Text("Blendshapes")
                .font(.caption)
                .foregroundColor(.gray)

            LazyVGrid(columns: Array(repeating: GridItem(.flexible(), spacing: 2), count: 13), spacing: 2) {
                ForEach(0..<52, id: \.self) { i in
                    Rectangle()
                        .fill(barColor(for: appState.blendShapeValues[safe: i] ?? 0))
                        .frame(height: CGFloat(max(2, (appState.blendShapeValues[safe: i] ?? 0) * 40)))
                }
            }
            .frame(height: 44)
        }
        .padding(8)
        .background(Color.white.opacity(0.05))
        .cornerRadius(8)
    }

    private var controlButtons: some View {
        HStack(spacing: 20) {
            Button(action: toggleTracking) {
                Label(
                    appState.isTracking ? "Stop" : "Start",
                    systemImage: appState.isTracking ? "stop.fill" : "play.fill"
                )
                .font(.headline)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 14)
                .background(appState.isTracking ? Color.red : Color.green)
                .foregroundColor(.white)
                .cornerRadius(12)
            }

            Button(action: toggleSending) {
                Label(
                    appState.isSending ? "Disconnect" : "Connect",
                    systemImage: appState.isSending ? "wifi.slash" : "wifi"
                )
                .font(.headline)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 14)
                .background(appState.isSending ? Color.orange : Color.blue)
                .foregroundColor(.white)
                .cornerRadius(12)
            }
            .disabled(!appState.isTracking)
        }
    }

    private func toggleTracking() {
        if appState.isTracking {
            trackingSession.stopSending()
            trackingSession.stop()
        } else {
            trackingSession.start()
        }
    }

    private func toggleSending() {
        if appState.isSending {
            trackingSession.stopSending()
        } else {
            trackingSession.startSending(host: appState.targetIP, port: appState.targetPort)
        }
    }

    private func barColor(for value: Float) -> Color {
        if value < 0.3 { return .green.opacity(Double(value) + 0.3) }
        if value < 0.7 { return .yellow.opacity(Double(value) + 0.3) }
        return .red.opacity(Double(value) + 0.2)
    }
}

struct StatusDot: View {
    let active: Bool
    let label: String

    var body: some View {
        HStack(spacing: 4) {
            Circle()
                .fill(active ? Color.green : Color.red)
                .frame(width: 8, height: 8)
            Text(label)
                .font(.caption)
                .foregroundColor(.gray)
        }
    }
}

extension Array {
    subscript(safe index: Int) -> Element? {
        indices.contains(index) ? self[index] : nil
    }
}
