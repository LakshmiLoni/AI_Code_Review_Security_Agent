package com.university.review.service;

import java.security.MessageDigest;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

/**
 * Intermediate Java Project: Secure Authentication Service.
 * Demonstrates parameterized queries, constant-time verification, and structured exception handling.
 */
public class SecureAuthService {

    private final Connection connection;

    public SecureAuthService(Connection connection) {
        this.connection = connection;
    }

    public boolean authenticateUser(String username, String passwordHash) throws SQLException {
        if (username == null || username.trim().isEmpty()) {
            throw new IllegalArgumentException("Username must not be empty.");
        }

        // SECURE: Parameterized SQL Query with PreparedStatement
        String sql = "SELECT password_hash FROM accounts WHERE username = ? AND is_active = 1";
        try (PreparedStatement pstmt = connection.prepareStatement(sql)) {
            pstmt.setString(1, username);
            try (ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) {
                    String storedHash = rs.getString("password_hash");
                    // SECURE: Constant-time byte comparison prevents timing attacks
                    return MessageDigest.isEqual(storedHash.getBytes(), passwordHash.getBytes());
                }
            }
        }
        return false;
    }
}
