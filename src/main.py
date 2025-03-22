import argparse
import sys
import getpass
import os
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
import psutil
import time


# Constants
SALT_SIZE = 16
KEY_SIZE = 32
NONCE_SIZE = 12
TAG_SIZE = 16
ITERATIONS = 100_000

def get_dynamic_buffer_size(file_path):
    """Determine the buffer size based on file size dynamically."""
    try:
        file_size = os.path.getsize(file_path)
    except FileNotFoundError:
        print("Error: File not found!")
        sys.exit(1)
    total_ram = psutil.virtual_memory().total
    print(f"File path: {file_path}\nFile size: {file_size} bytes\nTotal system ram: {total_ram} bytes")
    if total_ram <= 4 * 1024 * 1024 * 1024:  # 4 GB RAM
        return 128 * 1024  # 128 KB
    elif total_ram <= 8 * 1024 * 1024 * 1024:  # 8 GB RAM
        return 256 * 1024  # 256 KB
    else:
        if file_size < 500 * 1024 * 1024:  # < 500 MB
            return 64 * 1024   # 64 KB
        elif file_size < 2 * 1024 * 1024 * 1024:  # < 2 GB
            return 256 * 1024  # 256 KB
        elif file_size < 10 * 1024 * 1024 * 1024:  # < 10 GB
            return 1 * 1024 * 1024  # 1 MB
        else:  # 10+ GB
            return 4 * 1024 * 1024  # 4 MB

def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a 256-bit key from the password using PBKDF2."""
    return PBKDF2(password, salt, dkLen=KEY_SIZE, count=ITERATIONS)

def encrypt_file(file_path, buffersize, password, output_dir):
    """Encrypt a file using AES-GCM (Authenticated Encryption)."""
    start = time.perf_counter() # starting time counter
    try:
        salt = get_random_bytes(SALT_SIZE)
        key = derive_key(password, salt)
        nonce = get_random_bytes(NONCE_SIZE)
        
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        encrypted_file = os.path.join(output_dir, Path(file_path).name + ".aes")

        with open(file_path, "rb") as f_in, open(encrypted_file, "wb") as f_out:
            f_out.write(salt + nonce)  # Store salt + nonce for decryption
            while chunk := f_in.read(buffersize):
                f_out.write(cipher.encrypt(chunk))
            tag = cipher.digest()
            f_out.write(tag)  # Store tag at the end
        ending = time.perf_counter() # end time counter
        print(f"Encryption successful! File saved at: {encrypted_file}")
        print(f"Total encryption time: {ending-start:.6f} seconds")

    except FileNotFoundError:
        print("Error: File not found.")
    except Exception as e:
        print(f"Encryption failed: {e}")

def decrypt_file(file_path, password, output_dir):
    """Decrypt a file using AES-GCM (Authenticated Decryption)."""
    start = time.perf_counter() # starting time counter
    try:
        with open(file_path, "rb") as f_in:
            salt = f_in.read(SALT_SIZE)
            nonce = f_in.read(NONCE_SIZE)
            key = derive_key(password, salt)

            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)

            decrypted_file = os.path.join(output_dir, Path(file_path).stem)

            with open(decrypted_file, "wb") as f_out:
                ciphertext = f_in.read()
                tag = ciphertext[-TAG_SIZE:]  # Extract authentication tag
                ciphertext = ciphertext[:-TAG_SIZE]  # Remove tag from ciphertext
                f_out.write(cipher.decrypt_and_verify(ciphertext, tag))
                
            ending = time.perf_counter() # end time counter
            print(f"Decryption successful! File saved at: {decrypted_file}")
            print(f"Total encryption time: {ending-start:.6f} seconds")

    except ValueError:
        print("Error: Decryption failed! Incorrect password or corrupted file.")
    except FileNotFoundError:
        print("Error: File not found.")
    except Exception as e:
        print(f"Decryption failed: {e}")

def main():
    #arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mode', type=str, choices=['e', 'd'], help="Mode: 'e' for encryption, 'd' for decryption")
    parser.add_argument('-f', '--file', type=str, help="File to encrypt/decrypt")
    parser.add_argument('-p', '--password', type=str, help="Password (or provide a file path containing the password)")
    parser.add_argument('-o', '--output', type=str, default="./", help="Output directory")
    args = parser.parse_args()

    if not args.mode or not args.file:
        parser.print_help()
        sys.exit(2)
    # Resolve password
    if args.password and os.path.isfile(args.password):
        with open(args.password, "r") as f:
            password = f.readline().strip()
        confirm_password = password

    elif args.password:
        confirm_password = getpass.getpass("Confirm password: ")

    else:
        if args.mode == 'e':
            password = getpass.getpass("Enter the password: ")
            confirm_password = getpass.getpass("Confirm password: ")
        else:
            password = getpass.getpass("Enter the password: ")
            confirm_password = password
        
    if password != confirm_password:
        print("Error: Password do not match.")
        sys.exit(3)
    else:
        print("Password matched!")

    # Ensure output directory exists
    os.makedirs(args.output, exist_ok=True)

    if args.mode == "e":
        buffersize= get_dynamic_buffer_size(args.file)
        print(f"Buffer size: {buffersize}")
        encrypt_file(args.file, buffersize, password, args.output)
    elif args.mode == "d":
        file_size = os.path.getsize(args.file)
        total_ram = psutil.virtual_memory().total
        print(f"File path: {args.file}\nFile size: {file_size} bytes\nTotal system ram: {total_ram} bytes")
        if not args.file.endswith(".aes"):
            print("Error: Decryption requires a '.aes' file.")
            sys.exit(3)
        decrypt_file(args.file, password, args.output)

    # Wipe password from memory
    del password
    del confirm_password

if __name__ == "__main__":
    main()
