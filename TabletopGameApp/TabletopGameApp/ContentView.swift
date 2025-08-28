//
//  ContentView.swift
//  TabletopGameApp
//
//  Created by Brian Murdoch on 27/08/2025.
//

import SwiftUI

enum AppRoute: Hashable {
    case dashboard
    case gameSelection
    case chat(game: Game)
}

@MainActor
class NavigationManager: ObservableObject {
    @Published var path = NavigationPath()
    
    func navigateToGameSelection() {
        path.append(AppRoute.gameSelection)
    }
    
    func navigateToChat(game: Game) {
        path.append(AppRoute.chat(game: game))
    }
    
    func navigateToDashboard() {
        path = NavigationPath() // Reset to root (dashboard)
    }
    
    func goBack() {
        if !path.isEmpty {
            path.removeLast()
        }
    }
}

struct ContentView: View {
    @StateObject private var authManager = AuthenticationManager()
    @StateObject private var navigationManager = NavigationManager()
    
    var body: some View {
        Group {
            if authManager.isAuthenticated {
                NavigationStack(path: $navigationManager.path) {
                    DashboardView()
                        .navigationDestination(for: AppRoute.self) { route in
                            switch route {
                            case .dashboard:
                                DashboardView()
                            case .gameSelection:
                                GameSelectionView()
                            case .chat(let game):
                                ChatView(game: game)
                            }
                        }
                }
                .environmentObject(authManager)
                .environmentObject(navigationManager)
                .onAppear {
                    print("📱 Dashboard view appeared - user authenticated!")
                }
            } else {
                LoginView()
                    .environmentObject(authManager)
                    .onAppear {
                        print("🔐 Login view appeared - user not authenticated")
                    }
            }
        }
        .preferredColorScheme(.dark)
        .animation(.easeInOut, value: authManager.isAuthenticated)
        .onChange(of: authManager.isAuthenticated) {
            print("🔄 Authentication state changed to: \(authManager.isAuthenticated)")
            // Reset navigation when authentication changes
            navigationManager.navigateToDashboard()
        }
    }
}

#Preview {
    ContentView()
}
