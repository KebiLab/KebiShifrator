import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget,
                             QWidget, QVBoxLayout, QLabel, QStatusBar,
                             QFileDialog, QLineEdit, QPushButton, QTextEdit,
                             QGridLayout, QHeaderView, QTableWidget, QTableWidgetItem,
                             QComboBox, QProgressBar)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
import ctypes
import qdarkstyle
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.exceptions import InvalidTag
import secrets
import base64
import hashlib
import logging


def set_window_app_id():
    try:
        myappid = 'kebilab.kebishifrator.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception as e:
        print(f"AppUserModelID setting failed: {e}")

def get_icon_path():
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(base_path, 'icon.ico')    
    if not os.path.exists(icon_path):
        print(f"Icon not found at: {icon_path}")
        return None
    
    return icon_path


class KebiShifrator(QMainWindow):
    def __init__(self):
        super().__init__()

        icon_path = get_icon_path()
        if icon_path:
            self.setWindowIcon(QIcon(icon_path))
            print(f"Window icon set from: {icon_path}")
        else:
            print("Warning: Icon not found, using default")
        
        self.setWindowTitle("KebiShifrator - Made by KebiLab")
        self.setGeometry(100, 100, 800, 600)

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.key_management_tab = QWidget()
        self.encryption_tab = QWidget()
        self.decryption_tab = QWidget()
        self.history_tab = QWidget()

        self.tab_widget.addTab(self.key_management_tab, "Key Management")
        self.tab_widget.addTab(self.encryption_tab, "Encryption")
        self.tab_widget.addTab(self.decryption_tab, "Decryption")
        self.tab_widget.addTab(self.history_tab, "History")

        # Configure logging
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')

        self.setup_ui()

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # Add progress bar to status bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)




    def setup_ui(self):
        self.setup_key_management_tab()
        self.setup_encryption_tab()
        self.setup_decryption_tab()
        self.setup_history_tab()

    def setup_key_management_tab(self):
        layout = QGridLayout()

        # Key Pair Name
        layout.addWidget(QLabel("Key Pair Name:"), 0, 0)
        self.key_name_input = QLineEdit()
        layout.addWidget(self.key_name_input, 0, 1)

        # Password
        layout.addWidget(QLabel("Password:"), 1, 0)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input, 1, 1)

        # Confirm Password
        layout.addWidget(QLabel("Confirm Password:"), 2, 0)
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.confirm_password_input, 2, 1)

        # Key Directory
        layout.addWidget(QLabel("Key Directory:"), 3, 0)
        self.key_directory_input = QLineEdit()
        layout.addWidget(self.key_directory_input, 3, 1)
        self.key_directory_button = QPushButton("Browse")
        self.key_directory_button.clicked.connect(self.select_key_directory)
        layout.addWidget(self.key_directory_button, 3, 2)

        # Generate Key Button
        self.generate_key_button = QPushButton("Generate Key Pair")
        self.generate_key_button.clicked.connect(self.generate_key_pair)
        layout.addWidget(self.generate_key_button, 4, 0, 1, 3)

        self.key_management_tab.setLayout(layout)

    def setup_encryption_tab(self):
        layout = QGridLayout()

        # Select File
        layout.addWidget(QLabel("Select File:"), 0, 0)
        self.encryption_file_input = QLineEdit()
        layout.addWidget(self.encryption_file_input, 0, 1)
        self.encryption_file_button = QPushButton("Browse")
        self.encryption_file_button.clicked.connect(self.select_encryption_file)
        layout.addWidget(self.encryption_file_button, 0, 2)

        # File Information
        self.encryption_file_info = QLabel("No file selected")
        layout.addWidget(self.encryption_file_info, 1, 0, 1, 3)

        # Select Public Key
        layout.addWidget(QLabel("Select Public Key:"), 2, 0)
        self.encryption_key_combo = QComboBox()
        layout.addWidget(self.encryption_key_combo, 2, 1, 1, 2)



        # Output File Path
        layout.addWidget(QLabel("Output File Path:"), 3, 0)
        self.encryption_output_path_input = QLineEdit()
        layout.addWidget(self.encryption_output_path_input, 3, 1)
        self.encryption_output_path_button = QPushButton("Browse")
        self.encryption_output_path_button.clicked.connect(self.select_encryption_output_path)
        layout.addWidget(self.encryption_output_path_button, 3, 2)

        # Encrypt Button
        self.encrypt_button = QPushButton("Encrypt")
        self.encrypt_button.clicked.connect(self.encrypt_file)
        layout.addWidget(self.encrypt_button, 4, 0, 1, 3)

        self.encryption_tab.setLayout(layout)

    def select_encryption_file(self):
        file_path = QFileDialog.getOpenFileName(self, "Select File to Encrypt")[0]
        self.encryption_file_input.setText(file_path)
        if file_path:
            file_size = os.path.getsize(file_path)
            self.encryption_file_info.setText(f"File: {os.path.basename(file_path)}, Size: {file_size} bytes")
        else:
            self.encryption_file_info.setText("No file selected")

    def select_encryption_output_path(self):
        file_path = QFileDialog.getSaveFileName(self, "Select Output File Path")[0]
        self.encryption_output_path_input.setText(file_path)

    def encrypt_file(self):
        file_path = self.encryption_file_input.text()
        output_path = self.encryption_output_path_input.text()

        if not file_path:
            self.status_bar.showMessage("Please select a file to encrypt.")
            return

        if not output_path:
            self.status_bar.showMessage("Please select an output file path.")
            return

        if self.encryption_key_combo.currentIndex() < 0:
            self.status_bar.showMessage("Please select a public key.")
            return

        # TODO: Implement encryption logic here
        logging.info(f"Encrypting file: {file_path} to {output_path}")
        self.status_bar.showMessage(f"Encrypting file: {file_path}")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        try:
            # Generate a random session key
            session_key = secrets.token_bytes(32)  # 256 bits

            # Read the file data
            with open(file_path, "rb") as f:
                file_data = f.read()

            # Encrypt the file data with AES-256-GCM
            iv = secrets.token_bytes(16)
            cipher = Cipher(algorithms.AES(session_key), modes.GCM(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            encrypted_data = encryptor.update(file_data) + encryptor.finalize()
            tag = encryptor.tag

            # Load the public key
            try:
                key_name = self.encryption_key_combo.currentText()
                key_directory = self.key_directory_input.text()
                key_path = os.path.join(key_directory, key_name)
                with open(key_path, "rb") as key_file:
                    public_key = serialization.load_pem_public_key(
                        key_file.read(),
                        backend=default_backend()
                    )
                # Encrypt the session key with the public key
                encrypted_session_key = public_key.encrypt(
                    session_key,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
            except Exception as e:
                logging.error(f"Error loading public key or encrypting session key: {e}")
                self.status_bar.showMessage(f"Error loading public key or encrypting session key: {e}")
                return

            # Write the encrypted data to the output file
            with open(output_path, "wb") as f:
                f.write(iv)
                f.write(tag)
                # Store the length of the encrypted session key
                session_key_length = len(encrypted_session_key)
                f.write(session_key_length.to_bytes(4, byteorder='big'))
                f.write(encrypted_session_key)
                f.write(encrypted_data)

            logging.info(f"File encrypted successfully: {file_path} to {output_path}")
            self.status_bar.showMessage(f"File encrypted successfully: {file_path}")
            self.progress_bar.setValue(100)
            self.progress_bar.setVisible(False)
            self.add_history_entry("Encryption", os.path.basename(file_path), "Success")

        except Exception as e:
            logging.error(f"Error encrypting file: {e}")
            self.status_bar.showMessage(f"Error encrypting file: {e}")
            self.progress_bar.setVisible(False)
            self.add_history_entry("Encryption", os.path.basename(file_path), "Failed")

    def setup_decryption_tab(self):
        layout = QGridLayout()

        # Select Encrypted File
        layout.addWidget(QLabel("Select Encrypted File:"), 0, 0)
        self.decryption_file_input = QLineEdit()
        layout.addWidget(self.decryption_file_input, 0, 1)
        self.decryption_file_button = QPushButton("Browse")
        self.decryption_file_button.clicked.connect(self.select_decryption_file)
        layout.addWidget(self.decryption_file_button, 0, 2)

        # Select Private Key
        layout.addWidget(QLabel("Select Private Key:"), 1, 0)
        self.decryption_key_combo = QComboBox()
        layout.addWidget(self.decryption_key_combo, 1, 1, 1, 2)



        # Password
        layout.addWidget(QLabel("Password:"), 2, 0)
        self.decryption_password_input = QLineEdit()
        self.decryption_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.decryption_password_input, 2, 1, 1, 2)

        # Output File Path
        layout.addWidget(QLabel("Output File Path:"), 3, 0)
        self.decryption_output_path_input = QLineEdit()
        layout.addWidget(self.decryption_output_path_input, 3, 1)
        self.decryption_output_path_button = QPushButton("Browse")
        self.decryption_output_path_button.clicked.connect(self.select_decryption_output_path)
        layout.addWidget(self.decryption_output_path_button, 3, 2)

        # Decrypt Button
        self.decrypt_button = QPushButton("Decrypt")
        self.decrypt_button.clicked.connect(self.decrypt_file)
        layout.addWidget(self.decrypt_button, 4, 0, 1, 3)

        self.decryption_tab.setLayout(layout)

    def select_decryption_file(self):
        file_path = QFileDialog.getOpenFileName(self, "Select File to Decrypt")[0]
        self.decryption_file_input.setText(file_path)

    def select_decryption_key(self):
        # This function is no longer needed because we're using a QTableWidget for key selection
        pass

    def select_decryption_output_path(self):
        file_path = QFileDialog.getSaveFileName(self, "Select Output File Path")[0]
        self.decryption_output_path_input.setText(file_path)

    def decrypt_file(self):
        file_path = self.decryption_file_input.text()
        key_name = self.decryption_key_combo.currentText()
        key_directory = self.key_directory_input.text()
        key_path = os.path.join(key_directory, key_name)
        password = self.decryption_password_input.text()
        output_path = self.decryption_output_path_input.text()

        password_encoded = password.encode('utf-8')

        if not file_path:
            self.status_bar.showMessage("Please select a file to decrypt.")
            return

        if not key_path or self.decryption_key_combo.currentIndex() < 0:
            self.status_bar.showMessage("Please select a private key.")
            return

        if not password:
            self.status_bar.showMessage("Please enter the password.")
            return

        if not output_path:
            self.status_bar.showMessage("Please select an output file path.")
            return

        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            # Read the IV, tag, salt, and encrypted private key from the private key file
            with open(key_path, "r") as f:
                iv_b64 = f.readline().strip()
                tag_b64 = f.readline().strip()
                salt_b64 = f.readline().strip()
                encrypted_private_key_b64 = f.readline().strip()

            # Decode the IV, tag, salt, and encrypted private key from base64
            iv = base64.b64decode(iv_b64)
            tag = base64.b64decode(tag_b64)
            salt = base64.b64decode(salt_b64)
            encrypted_private_key = base64.b64decode(encrypted_private_key_b64)

            # Derive the key from the password
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=480000,
                backend=default_backend()
            )
            key = kdf.derive(password_encoded)

            # Create a cipher object with GCM mode
            cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
            decryptor = cipher.decryptor()

            # Decrypt the private key
            private_pem = decryptor.update(encrypted_private_key) + decryptor.finalize()

            # Load the private key
            private_key = serialization.load_pem_private_key(
                private_pem,
                password=None,
                backend=default_backend()
            )

            # Read the encrypted data from the input file
            with open(file_path, "rb") as f:
                iv = f.read(16)
                tag = f.read(16)
                # Read the length of the encrypted session key
                session_key_length_bytes = f.read(4)
                session_key_length = int.from_bytes(session_key_length_bytes, byteorder='big')
                encrypted_session_key = f.read(session_key_length)
                encrypted_data = f.read()

            # Decrypt the session key with the private key
            session_key = private_key.decrypt(
                encrypted_session_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            # Decrypt the file data with AES-256-GCM
            cipher = Cipher(algorithms.AES(session_key), modes.GCM(iv, tag), backend=default_backend())
            decryptor = cipher.decryptor()
            decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

            # Write the decrypted data to the output file
            with open(output_path, "wb") as f:
                f.write(decrypted_data)

            logging.info(f"File decrypted successfully: {file_path} to {output_path}")
            self.status_bar.showMessage(f"File decrypted successfully: {file_path}")
            self.progress_bar.setValue(100)
            self.progress_bar.setVisible(False)
            self.add_history_entry("Decryption", os.path.basename(file_path), "Success")

        except Exception as e:
            logging.error(f"Error decrypting file: {e}")
            self.status_bar.showMessage(f"Error decrypting file: {e}")
            self.progress_bar.setVisible(False)
            self.add_history_entry("Decryption", os.path.basename(file_path), "Failed")



    def setup_history_tab(self):
        layout = QVBoxLayout()

        # History Table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["Date", "Operation", "File", "Status"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.history_table)

        # TODO: Add filtering and sorting options

        self.history_tab.setLayout(layout)


    def select_key_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Key Directory")
        self.key_directory_input.setText(directory)
        self.load_keys()
    def load_keys(self):
        key_directory = self.key_directory_input.text()
        if not key_directory:
            return

        keys = KebiShifrator.load_keys_from_directory(key_directory)

        public_keys = [key for key in keys if os.path.exists(os.path.join(key_directory, key + "_public.pem"))]
        private_keys = [key for key in keys if os.path.exists(os.path.join(key_directory, key + "_private.pem"))]

        self.update_key_combos(public_keys, private_keys)

    def update_key_combos(self, public_keys, private_keys):
        # Update encryption key combo
        self.encryption_key_combo.clear()
        for key in public_keys:
            self.encryption_key_combo.addItem(key + "_public.pem")

        # Update decryption key combo
        self.decryption_key_combo.clear()
        for key in private_keys:
            self.decryption_key_combo.addItem(key + "_private.pem")

        self.status_bar.showMessage(f"Loaded {len(public_keys)} public keys and {len(private_keys)} private keys.")

    def add_history_entry(self, operation, file_name, status):
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row_count = self.history_table.rowCount()
        self.history_table.insertRow(row_count)
        self.history_table.setItem(row_count, 0, QTableWidgetItem(current_time))
        self.history_table.setItem(row_count, 1, QTableWidgetItem(operation))
        self.history_table.setItem(row_count, 2, QTableWidgetItem(file_name))
        self.history_table.setItem(row_count, 3, QTableWidgetItem(status))

    @staticmethod
    def load_keys_from_directory(directory):
        keys = []
        try:
            for filename in os.listdir(directory):
                if filename.endswith("_public.pem"):
                    keys.append(filename[:-11])  # Remove "_public.pem"
                elif filename.endswith("_private.pem"):
                    keys.append(filename[:-12])  # Remove "_private.pem"
        except FileNotFoundError:
            logging.error(f"Key directory not found: {directory}")
            return []
        return keys

    def generate_key_pair(self):
        key_name = self.key_name_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        key_directory = self.key_directory_input.text()

        if not key_name:
            self.status_bar.showMessage("Please enter a key pair name.")
            return

        if not password:
            self.status_bar.showMessage("Please enter a password.")
            return

        if password != confirm_password:
            self.status_bar.showMessage("Passwords do not match.")
            return

        if not key_directory:
            self.status_bar.showMessage("Please select a key directory.")
            return

        # TODO: Implement key generation logic here
        logging.info(f"Generating key pair: {key_name}")
        self.status_bar.showMessage(f"Generating key pair: {key_name}")

        try:
            # Generate RSA key pair
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=4096,
                backend=default_backend()
            )
            public_key = private_key.public_key()

            # Encrypt private key with password
            password_encoded = password.encode('utf-8')
            salt = secrets.token_bytes(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=480000,
                backend=default_backend()
            )
            key = kdf.derive(password_encoded)
            key_b64 = base64.b64encode(key).decode('utf-8')

            # Serialize keys
            # Generate a random IV
            iv = secrets.token_bytes(16)

            # Create an AES cipher object with GCM mode
            cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
            encryptor = cipher.encryptor()

            # Encrypt the private key
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            encrypted_private_key = encryptor.update(private_pem) + encryptor.finalize()
            tag = encryptor.tag  # Save the tag for verification!

            # Encode the IV, tag, salt, and encrypted private key to base64
            iv_b64 = base64.b64encode(iv).decode('utf-8')
            tag_b64 = base64.b64encode(tag).decode('utf-8')
            salt_b64 = base64.b64encode(salt).decode('utf-8')
            encrypted_private_key_b64 = base64.b64encode(encrypted_private_key).decode('utf-8')

            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode('utf-8')

            # Save keys to files
            private_key_path = os.path.join(key_directory, f"{key_name}_private.pem")
            public_key_path = os.path.join(key_directory, f"{key_name}_public.pem")

            with open(private_key_path, "w") as f:
                f.write(iv_b64 + "\n")
                f.write(tag_b64 + "\n")
                f.write(salt_b64 + "\n")
                f.write(encrypted_private_key_b64)
            with open(public_key_path, "w") as f:
                f.write(public_pem)
            
            self.load_keys()
            # Log success
            logging.info(f"Key pair generated successfully: {key_name}")
            self.status_bar.showMessage(f"Key pair generated successfully: {key_name}")

        except Exception as e:
            logging.error(f"Error generating key pair: {e}")
            self.status_bar.showMessage(f"Error generating key pair: {e}")

if __name__ == '__main__':
    set_window_app_id()
    app = QApplication(sys.argv)
    icon_path = get_icon_path()
    if icon_path and os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
        print(f"Application icon set from: {icon_path}")
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt6())
    mainWin = KebiShifrator()
    mainWin.show()
    sys.exit(app.exec())