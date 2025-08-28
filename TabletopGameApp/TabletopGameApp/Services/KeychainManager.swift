//
//  KeychainManager.swift
//  TabletopGameApp
//
//  Created by Claude on 27/08/2025.
//

import Foundation
import Security

class KeychainManager {
    static let shared = KeychainManager()
    private let tokenAccount = "tabletop_auth_token"
    
    private init() {}
    
    enum KeychainError: Error {
        case noToken
        case unhandledError(status: OSStatus)
        case unexpectedTokenData
        case encodingError
    }
    
    func storeToken(_ token: String) throws {
        guard let data = token.data(using: .utf8) else {
            throw KeychainError.encodingError
        }
        
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: tokenAccount,
            kSecValueData as String: data,
            kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly
        ]
        
        // Delete existing item if it exists
        SecItemDelete(query as CFDictionary)
        
        let status = SecItemAdd(query as CFDictionary, nil)
        guard status == errSecSuccess else {
            throw KeychainError.unhandledError(status: status)
        }
    }
    
    func retrieveToken() throws -> String {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: tokenAccount,
            kSecReturnData as String: kCFBooleanTrue!,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]
        
        var item: CFTypeRef?
        let status = SecItemCopyMatching(query as CFDictionary, &item)
        
        guard status != errSecItemNotFound else {
            throw KeychainError.noToken
        }
        
        guard status == errSecSuccess else {
            throw KeychainError.unhandledError(status: status)
        }
        
        guard let tokenData = item as? Data,
              let token = String(data: tokenData, encoding: .utf8) else {
            throw KeychainError.unexpectedTokenData
        }
        
        return token
    }
    
    func deleteToken() {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: tokenAccount
        ]
        
        SecItemDelete(query as CFDictionary)
    }
    
    func hasToken() -> Bool {
        do {
            _ = try retrieveToken()
            return true
        } catch {
            return false
        }
    }
}