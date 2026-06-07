from cryptography.fernet import Fernet

def encrypt_file(file_path: str, key: bytes) -> str:
    """Encrypts a file and overwrites it with the secure version."""
    f = Fernet(key)
    
    # Read the original raw file data
    with open(file_path, "rb") as file:
        file_data = file.read()
        
    # Encrypt the data
    encrypted_data = f.encrypt(file_data)
    
    # Overwrite the original file with encrypted data
    with open(file_path, "wb") as file:
        file.write(encrypted_data)
        
    return f"File encrypted successfully: {file_path}"


def decrypt_file(file_path: str, key: bytes) -> str:
    """Decrypts an encrypted file and overwrites it with the original version."""
    f = Fernet(key)
    
    # Read the encrypted file data
    with open(file_path, "rb") as file:
        encrypted_data = file.read()
        
    # Decrypt the data
    decrypted_data = f.decrypt(encrypted_data)
    
    # Overwrite the file with the decrypted data
    with open(file_path, "wb") as file:
        file.write(decrypted_data)
        
    return f"File decrypted successfully: {file_path}"