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

struct ContentView: View {
    @StateObject private var authManager = AuthenticationManager()
    @State private var navigationPath = NavigationPath()
    
    var body: some View {
        Group {
            if authManager.isAuthenticated {
                DashboardView()
                    .environmentObject(authManager)
            } else {
                LoginView()
                    .environmentObject(authManager)
            }
        }
        .preferredColorScheme(.dark)
        .animation(.easeInOut, value: authManager.isAuthenticated)
    }
}

#Preview {
    ContentView()
}
