import SwiftUI

@main
struct FaceCaptureApp: App {
    @StateObject private var appState = AppState()

    var body: some Scene {
        WindowGroup {
            CaptureView()
                .environmentObject(appState)
        }
    }
}
