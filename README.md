# Secure Blockchain-Based Voting System

A secure and privacy-preserving electronic voting system built using Flask, encryption, and blockchain concepts. The system ensures that only verified voters can register, votes remain confidential, and all records are tamper-resistant.

---

## Overview

This project implements a voting platform with strong security mechanisms:

* Voter registration is protected using OTP verification
* Passwords are securely stored using hashing
* Votes are encrypted before storage
* A blockchain structure ensures data integrity
* Mixnet is used to anonymize votes before counting

---

## Features

### Voter Registration

* Only eligible voters can register
* OTP verification using registered phone numbers
* Prevents unauthorized account creation
* Passwords stored using bcrypt hashing

### Authentication

* Login using Voter ID and password
* Session-based access control

### Voting System

* Each voter can vote only once
* Votes are encrypted using Fernet encryption
* Ensures vote confidentiality and integrity

### Blockchain Storage

* Votes are stored as blocks in a blockchain
* Each block contains:

  * Encrypted vote
  * Hash of previous block
* Ensures immutability and tamper detection

### Mixnet Anonymization

* Votes are shuffled before counting
* Prevents linking voters to their votes

### Admin Panel

* Open and close elections
* View total votes and registered voters
* View election results with charts
* Verify blockchain integrity
* Export blockchain data

### Vote Verification

* Each vote generates a unique hash
* Users can verify that their vote exists in the system

---

## System Flow

```id="flow001"
Registration
   ↓
OTP Verification
   ↓
Password Creation
   ↓
Login
   ↓
Vote Encryption
   ↓
Blockchain Storage
   ↓
Mixnet Shuffling
   ↓
Result Decryption (Admin)
```

---

## Technology Stack

* Backend: Python, Flask
* Database: SQLite
* Encryption: Fernet (cryptography library)
* Password Hashing: bcrypt
* Blockchain: Custom implementation in Python
* Frontend: HTML, Bootstrap
* Visualization: Matplotlib

---

## Project Structure

```id="struct001"
secure_voting_system/
│
├── app.py
├── requirements.txt
├── README.md
│
├── database/
│   └── db.py
│
├── blockchain/
│   ├── block.py
│   └── blockchain.py
│
├── crypto/
│   ├── encryption.py
│   └── blind_signature.py
│
├── mixnet/
│   └── mixnet.py
│
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── verify_otp.html
│   ├── set_password.html
│   ├── dashboard.html
│   ├── vote.html
│   ├── vote_success.html
│   ├── verify_vote.html
│   ├── verify_result.html
│   ├── blockchain_view.html
│   ├── chain_status.html
│   ├── admin_login.html
│   ├── admin_dashboard.html
│   └── admin_results.html
│
├── static/
│   └── charts/
│
├── logs/
└── voters.db
```

---

## Installation and Setup

### 1. Clone the repository

```id="setup001"
git clone https://github.com/YOUR_USERNAME/secure-blockchain-voting-system.git
cd secure-blockchain-voting-system
```

### 2. Create a virtual environment

```id="setup002"
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```id="setup003"
pip install -r requirements.txt
```

If requirements.txt is not available:

```id="setup004"
pip install flask bcrypt cryptography matplotlib
```

### 4. Run the application

```id="setup005"
python app.py
```

Open the application in your browser:

```id="setup006"
http://127.0.0.1:5000/
```

---

## Security Features

* OTP-based verification during registration
* Password hashing using bcrypt
* Encrypted votes using Fernet
* Blockchain structure to prevent tampering
* Mixnet anonymization for voter privacy
* One-vote-per-user enforcement

---

## Limitations

* OTP is displayed in the terminal (no SMS integration)
* SQLite is not suitable for large-scale deployment
* Blockchain implementation is simplified for educational purposes

---

## Future Enhancements

* Integration with SMS APIs (Fast2SMS or Twilio)
* CAPTCHA to prevent OTP abuse
* Cloud deployment
* Real-time analytics dashboard
* Improved user interface for production use

---

