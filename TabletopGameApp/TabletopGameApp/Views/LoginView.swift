//
//  LoginView.swift
//  TabletopGameApp
//
//  Created by Claude on 27/08/2025.
//

import SwiftUI

struct LoginView: View {
    @State private var username = ""
    @State private var password = ""
    @State private var showPassword = false
    @EnvironmentObject private var authManager: AuthenticationManager
    
    var body: some View {
        GeometryReader { geometry in
            ZStack {
                // Background Gradient
                LinearGradient(
                    colors: [Color.gamingBackground, Color.gamingPrimary],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
                .ignoresSafeArea()
                
                VStack(spacing: 32) {
                    // Logo and Title
                    VStack(spacing: 16) {
                        Image(systemName: "gamecontroller.fill")
                            .font(.system(size: 64))
                            .foregroundColor(.gamingAccent)
                        
                        Text("TabletopPro")
                            .font(.system(size: 32, weight: .bold, design: .rounded))
                            .foregroundColor(.gamingText)
                    }
                    .padding(.top, 40)
                    
                    // Login Form
                    VStack(spacing: 20) {
                        // Username Field
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Username")
                                .font(.system(size: 14, weight: .medium))
                                .foregroundColor(.gamingSecondary)
                            
                            TextField("Enter your username", text: $username)
                                .textFieldStyle(GamingTextFieldStyle())
                                .keyboardType(.emailAddress)
                                .autocapitalization(.none)
                                .autocorrectionDisabled()
                        }
                        
                        // Password Field
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Password")
                                .font(.system(size: 14, weight: .medium))
                                .foregroundColor(.gamingSecondary)
                            
                            HStack {
                                Group {
                                    if showPassword {
                                        TextField("Enter your password", text: $password)
                                    } else {
                                        SecureField("Enter your password", text: $password)
                                    }
                                }
                                .textFieldStyle(GamingTextFieldStyle())
                                
                                Button(action: { showPassword.toggle() }) {
                                    Image(systemName: showPassword ? "eye.slash" : "eye")
                                        .foregroundColor(.gamingSecondary)
                                }
                                .padding(.trailing, 12)
                            }
                        }
                        
                        // Login Button
                        Button(action: performLogin) {
                            HStack {
                                if authManager.isLoading {
                                    ProgressView()
                                        .progressViewStyle(CircularProgressViewStyle(tint: .white))
                                        .scaleEffect(0.8)
                                }
                                
                                Text(authManager.isLoading ? "Signing In..." : "Sign In")
                                    .font(.system(size: 16, weight: .semibold))
                                    .foregroundColor(.white)
                            }
                            .frame(maxWidth: .infinity)
                            .frame(height: 48)
                            .background(
                                RoundedRectangle(cornerRadius: 8)
                                    .fill(isFormValid ? Color.gamingAccent : Color.gamingSecondary)
                            )
                        }
                        .disabled(!isFormValid || authManager.isLoading)
                        
                        // Error Message
                        if let errorMessage = authManager.errorMessage {
                            Text(errorMessage)
                                .font(.system(size: 14))
                                .foregroundColor(.red)
                                .multilineTextAlignment(.center)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                    }
                    .padding(.horizontal, 24)
                    
                    Spacer()
                    
                    // Helper Text
                    VStack(spacing: 8) {
                        Text("Demo Credentials:")
                            .font(.system(size: 12, weight: .medium))
                            .foregroundColor(.gamingSecondary)
                        
                        Text("Username: admin • Password: secret")
                            .font(.system(size: 12))
                            .foregroundColor(.gamingSecondary.opacity(0.8))
                    }
                    .padding(.bottom, 20)
                }
            }
        }
        .preferredColorScheme(.dark)
        .onSubmit {
            if isFormValid {
                performLogin()
            }
        }
        .onChange(of: authManager.errorMessage) { _ in
            // Clear error after 5 seconds
            if authManager.errorMessage != nil {
                DispatchQueue.main.asyncAfter(deadline: .now() + 5) {
                    authManager.clearError()
                }
            }
        }
    }
    
    private var isFormValid: Bool {
        !username.isEmpty && !password.isEmpty
    }
    
    private func performLogin() {
        Task {
            do {
                try await authManager.login(username: username, password: password)
            } catch {
                // Error is handled by the AuthenticationManager
                print("Login error: \(error)")
            }
        }
    }
}

// MARK: - Gaming Text Field Style

struct GamingTextFieldStyle: TextFieldStyle {
    func _body(configuration: TextField<Self._Label>) -> some View {
        configuration
            .padding(.horizontal, 16)
            .padding(.vertical, 12)
            .background(
                RoundedRectangle(cornerRadius: 8)
                    .fill(Color.gamingPrimary)
                    .overlay(
                        RoundedRectangle(cornerRadius: 8)
                            .stroke(Color.gamingSecondary.opacity(0.3), lineWidth: 1)
                    )
            )
            .foregroundColor(.gamingText)
            .font(.system(size: 16))
    }
}

// MARK: - Gaming Colors

extension Color {
    static let gamingBackground = Color(red: 0.05, green: 0.07, blue: 0.09)  // #0D1117
    static let gamingPrimary = Color(red: 0.13, green: 0.15, blue: 0.18)     // #21262D
    static let gamingAccent = Color(red: 0.35, green: 0.65, blue: 1.0)       // #58A6FF
    static let gamingText = Color(red: 0.94, green: 0.96, blue: 0.99)        // #F0F6FC
    static let gamingSecondary = Color(red: 0.55, green: 0.58, blue: 0.62)   // #8B949E
    static let gamingSuccess = Color(red: 0.25, green: 0.69, blue: 0.31)     // #40B14D
    static let gamingWarning = Color(red: 1.0, green: 0.65, blue: 0.0)       // #FF8C00
    static let gamingError = Color(red: 0.96, green: 0.26, blue: 0.21)       // #F54133
}

#Preview {
    LoginView()
        .environmentObject(AuthenticationManager())
}