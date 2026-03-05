# Secure Blockchain Voting System

A **privacy-preserving blockchain-based e-voting system** built using Python and Flask.
The system combines **cryptographic techniques and blockchain principles** to ensure vote confidentiality, integrity, and transparency.

---

## Overview

This project simulates a secure digital voting environment where:

* Only **authenticated voters** can participate.
* Votes are **encrypted** before storage.
* A **blockchain ledger** guarantees tamper-resistant vote records.
* **Blind signatures** protect voter identity.
* **Mixnet shuffling** anonymizes ballots before counting.

The goal is to demonstrate how cryptographic protocols can enhance election security.

---

## Features

* Secure voter authentication
* Pre-authorized voter list
* Double-vote prevention
* Blind signature protocol
* Encrypted ballot storage
* Mixnet-based vote anonymization
* Blockchain vote ledger
* Election result visualization
* Blockchain integrity verification
* Admin dashboard

---

## System Architecture

User → Authentication → Vote Encryption → Mixnet → Blockchain Storage → Result Calculation

Main components:

* **Flask Web Server**
* **SQLite Database**
* **Blockchain Ledger**
* **Cryptographic Modules**
* **Visualization for Results**

---

## Technologies Used

* Python
* Flask
* SQLite
* Cryptography
* Matplotlib
* HTML / CSS / JavaScript
* Bootstrap

---

## Project Structure


secure-blockchain-voting-system
│
├── blockchain/        # Blockchain implementation
├── crypto/            # Encryption and blind signatures
├── database/          # Database operations
├── mixnet/            # Vote anonymization
├── templates/         # HTML pages
├── static/            # CSS, JS, charts
├── app.py             # Main application
├── config.py          # Configuration
├── requirements.txt   # Dependencies


---

## How to Run the Project

### 1. Clone the Repository


git clone https://github.com/navyaSree0528/secure-blockchain-voting-system.git
cd secure-blockchain-voting-system


---

### 2. Create Virtual Environment

Windows:


python -m venv venv
venv\Scripts\activate


Mac/Linux:


python3 -m venv venv
source venv/bin/activate


---

### 3. Install Dependencies


pip install -r requirements.txt


---

### 4. Run the Application


python app.py


---

### 5. Open in Browser


http://127.0.0.1:5000


---

## Demo Voter Credentials

| Voter ID | Password |
| -------- | -------- |
| VOTER001 | 1234     |
| VOTER002 | 1234     |
| VOTER003 | 1234     |
| VOTER004 | 1234     |
| VOTER005 | 1234     |
| VOTER006 | 1234     |
| VOTER007 | 1234     |
| VOTER008 | 1234     |
| VOTER009 | 1234     |
| VOTER010 | 1234     |
| VOTER011 | 1234     |
| VOTER012 | 1234     |
| VOTER013 | 1234     |
| VOTER014 | 1234     |
| VOTER015 | 1234     |

Admin login:


Admin ID: admin
Password: admin123


---

## Security Mechanisms

The system integrates multiple security layers:

* **Authentication** → verifies eligible voters
* **Blind Signatures** → protects voter identity
* **Encryption** → secures ballots
* **Mixnet Shuffling** → removes vote-voter link
* **Blockchain Ledger** → ensures immutability
* **Integrity Verification** → detects tampering

---

## Educational Purpose

This project is a **prototype implementation** designed for educational and research purposes to demonstrate how blockchain and cryptography can enhance voting security.

---



