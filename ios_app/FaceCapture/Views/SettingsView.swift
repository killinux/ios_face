import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var appState: AppState
    @Environment(\.dismiss) var dismiss

    var body: some View {
        NavigationView {
            Form {
                Section("Network") {
                    HStack {
                        Text("Target IP")
                        Spacer()
                        TextField("192.168.1.255", text: $appState.targetIP)
                            .multilineTextAlignment(.trailing)
                            .keyboardType(.decimalPad)
                    }
                    HStack {
                        Text("Port")
                        Spacer()
                        TextField("49983", value: $appState.targetPort, format: .number)
                            .multilineTextAlignment(.trailing)
                            .keyboardType(.numberPad)
                    }
                }

                Section("Smoothing") {
                    VStack(alignment: .leading) {
                        Text("Alpha: \(appState.smoothingAlpha, specifier: "%.2f")")
                        Slider(value: $appState.smoothingAlpha, in: 0.1...1.0, step: 0.05)
                    }
                    Text("Lower = smoother but more latency. Higher = more responsive but jittery.")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                Section("Status") {
                    LabeledContent("Packets Sent", value: "\(appState.packetsSent)")
                    LabeledContent("FPS", value: "\(appState.currentFPS)")
                    LabeledContent("Tracking", value: appState.isTracking ? "Active" : "Inactive")
                }

                Section("Info") {
                    Text("This app captures facial expressions via ARKit and streams 52 blendshape coefficients + head rotation + eye gaze data over UDP to a Blender addon.")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            .navigationTitle("Settings")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Done") { dismiss() }
                }
            }
        }
    }
}
