Multi-Application SSO Simulation (TLS/SSL)

📌 Description

This project is a simulation of a Single Sign-On (SSO) system designed to centralize authentication across multiple client applications. Developed as part of an academic project for an NGO, it relies on a client-server architecture using Secure Sockets (TLS/SSL) to guarantee the confidentiality and integrity of all data exchanges.

 Security Features
End-to-End Encryption: Implementation of the TLS protocol to secure all Socket communications.
Robust Hashing: Secure password storage using the Bcrypt algorithm with salting.
Unique Identifiers: Use of UUIDv4 for session management and token generation.
Attack Mitigation: Built-in defense mechanisms against SQL injection and malformed JSON payloads.
captcha verification

 Installation
1. Prerequisites
Python 3.10+
OpenSSL 

2. Setup
git clone https://github.com/cyberr-genius/secure_login.git
cd secure_login
3. Certificate Generation
Bash
mkdir certs
cd certs
openssl req -x509 -newkey rsa:4096 -keyout server.key -out server.crt -days 365 -nodes

4. create database
createdb -U postgres mydatabase
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    login VARCHAR(50) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    failed_attempts INTEGER DEFAULT 0,
    lock_until TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

 Usage
Launch the Main Application :
python3 main.py

Launch the Admin Interface:
python3 admin.py

 Authors
SOULAMA Hanna
SANA Ibrahim
