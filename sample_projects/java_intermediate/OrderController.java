package com.university.review.controller;

import java.io.IOException;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

/**
 * Intermediate Java Project: Order Controller.
 * 
 * Demonstrates:
 * 1. SQL Injection via Statement concatenation
 * 2. Reflected Cross-Site Scripting (XSS)
 * 3. Hardcoded database credentials
 * 4. Empty catch block
 * 5. Stack trace leakage (e.printStackTrace())
 */
public class OrderController {

    // VULNERABILITY: Hardcoded Database Password
    private static final String DB_PASSWORD = "SuperSecretPassword123!";
    private static final String DB_USER = "admin";

    public void processOrder(HttpServletRequest request, HttpServletResponse response) throws IOException {
        String orderId = request.getParameter("orderId");
        String customerId = request.getParameter("customerId");

        try {
            Connection conn = DriverManager.getConnection("jdbc:mysql://localhost:3306/shop", DB_USER, DB_PASSWORD);
            Statement stmt = conn.createStatement();

            // VULNERABILITY: SQL Injection via direct string concatenation
            String sql = "SELECT * FROM orders WHERE order_id = '" + orderId + "' AND customer_id = '" + customerId + "'";
            ResultSet rs = stmt.executeQuery(sql);

            if (rs.next()) {
                // VULNERABILITY: Reflected XSS via unescaped output rendering
                response.getWriter().write("<h3>Order Confirmed: " + orderId + "</h3>");
            }
            conn.close();
        } catch (Exception e) {
            // QUALITY SMELL: Swallowing exception with empty catch or printStackTrace
            e.printStackTrace(); // Security Misconfiguration: Stack trace exposure
        }
    }

    public void generateOrderSummary(String[] items) {
        String summary = "";
        // QUALITY SMELL: Inefficient string concatenation in loop
        for (int i = 0; i < items.length; i++) {
            summary = summary + items[i] + ", ";
        }
        System.out.println("Summary: " + summary);
    }
}
