# KebiShifrator

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org)
[![PyQt6 6.6.0](https://img.shields.io/badge/PyQt6-6.6.0-green)](https://www.riverbankcomputing.com/software/pyqt/)
[![cryptography 41.0.0](https://img.shields.io/badge/cryptography-41.0.0-orange)](https://cryptography.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](https://opensource.org/licenses/MIT)

A professional desktop application for secure file encryption and decryption using hybrid cryptography (RSA + AES). Built with Python and PyQt6.

## Features

### Security Features
- **Hybrid Encryption**: RSA-4096 + AES-256-GCM
- **Secure Key Management**: Password-protected private keys
- **Authenticated Encryption**: GCM mode for data integrity
- **Key Derivation**: PBKDF2 with 480,000 iterations

### User Interface
- **Modern Themes**: Professional appearance. Light and Dark theme support
- **Multi-language**: English and Russian interface
- **Tab-based Layout**: Intuitive organization
- **Progress Tracking**: Real-time progress bars
- **Operation History**: Complete activity log

## Quick Start

### Installation

```bash
# Install dependencies
pip install PyQt6 cryptography qdarkstyle
```

### Usage

```bash
# Run the application
python kebishifrator.py
```

## How to Use

### 1. Key Generation
- Navigate to "Key Management" tab
- Enter key pair name
- Set a strong password
- Select key directory
- Click "Generate Key Pair"

### 2. File Encryption
- Go to "Encryption" tab
- Select file to encrypt
- Choose public key from dropdown
- Set output file path
- Click "Encrypt"

### 3. File Decryption
- Go to "Decryption" tab
- Select encrypted file
- Choose private key from dropdown
- Enter password
- Set output file path
- Click "Decrypt"

## Technical Details

### Cryptography
- **Asymmetric Encryption**: RSA-4096 with OAEP padding
- **Symmetric Encryption**: AES-256-GCM
- **Key Derivation**: PBKDF2-HMAC-SHA256
- **Random Generation**: Secure random bytes

### File Format
```
[16 bytes - IV]
[16 bytes - GCM tag]
[4 bytes - encrypted key length]
[N bytes - encrypted session key]
[remaining - encrypted data]
```

### Key Storage
- **Public Keys**: Standard PEM format
- **Private Keys**: Encrypted with AES-GCM

## Project Structure

```
kebishifrator/
├── kebishifrator.py          # Main application
├── requirements.txt          # Dependencies
├── README.md                 # Documentation
├── icon.ico                  # Application icon
├── KebiShifrator.exe         # Application .exe file
├── license.txt               # License file
└── .gitignore                # Git ignore rules
```

## Security Notice

This software is developed for educational and personal use. While it implements industry-standard cryptographic algorithms, it has not undergone professional security audit. For mission-critical data protection, always use professionally audited and supported encryption solutions.

## Development

### Requirements
- Python 3.8 or higher
- PyQt6 6.6.0
- cryptography 41.0.0
- qdarkstyle 3.1.0

### Building from Source
```bash
git clone https://github.com/yourusername/kebishifrator.git
cd kebishifrator
pip install -r requirements.txt
python kebishifrator.py
```

## Troubleshooting

### Common Issues

**Empty dropdown lists**
- Ensure key directory is selected
- Generate keys first
- Use "Browse" to reselect key directory

**Encryption/Decryption errors**
- Verify file permissions
- Check if keys are valid
- Ensure correct password for private key

**Application not starting**
- Verify Python version (3.8+ required)
- Check all dependencies are installed
- Run from terminal to see error messages

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the code comments
3. Ensure all dependencies are properly installed
