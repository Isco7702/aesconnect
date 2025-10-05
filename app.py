from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import secrets
import os

app = Flask(__name__)
CORS(app)

def generate_key_from_password(password: str, salt: bytes) -> bytes:
    """Generate a 256-bit key from password using PBKDF2"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())

def encrypt_text(plaintext: str, password: str) -> dict:
    """Encrypt text using AES-256-CBC"""
    try:
        # Generate random salt and IV
        salt = secrets.token_bytes(16)
        iv = secrets.token_bytes(16)
        
        # Generate key from password
        key = generate_key_from_password(password, salt)
        
        # Pad the plaintext
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext.encode()) + padder.finalize()
        
        # Encrypt
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        # Combine salt + iv + ciphertext and encode in base64
        encrypted_data = salt + iv + ciphertext
        encoded_data = base64.b64encode(encrypted_data).decode()
        
        return {
            'success': True,
            'encrypted_data': encoded_data,
            'message': 'Text encrypted successfully'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def decrypt_text(encrypted_data: str, password: str) -> dict:
    """Decrypt text using AES-256-CBC"""
    try:
        # Decode base64 data
        data = base64.b64decode(encrypted_data.encode())
        
        # Extract salt, iv, and ciphertext
        salt = data[:16]
        iv = data[16:32]
        ciphertext = data[32:]
        
        # Generate key from password
        key = generate_key_from_password(password, salt)
        
        # Decrypt
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Remove padding
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
        
        return {
            'success': True,
            'decrypted_text': plaintext.decode(),
            'message': 'Text decrypted successfully'
        }
    except Exception as e:
        return {
            'success': False,
            'error': 'Invalid encrypted data or wrong password'
        }

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/encrypt', methods=['POST'])
def encrypt_endpoint():
    """Encrypt text endpoint"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        password = data.get('password', '')
        
        if not text or not password:
            return jsonify({
                'success': False,
                'error': 'Text and password are required'
            }), 400
        
        result = encrypt_text(text, password)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/decrypt', methods=['POST'])
def decrypt_endpoint():
    """Decrypt text endpoint"""
    try:
        data = request.get_json()
        encrypted_data = data.get('encrypted_data', '')
        password = data.get('password', '')
        
        if not encrypted_data or not password:
            return jsonify({
                'success': False,
                'error': 'Encrypted data and password are required'
            }), 400
        
        result = decrypt_text(encrypted_data, password)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'AES Connect API'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)