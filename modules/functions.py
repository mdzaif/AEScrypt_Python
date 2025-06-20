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
from rich.progress import Progress


# Constants
VERSION = "1.2.1"
SALT_SIZE = 16
KEY_SIZE = 32
NONCE_SIZE = 12
TAG_SIZE = 16
ITERATIONS = 100_000


def output_dir(out_dir):
    # Ensure output directory exists
    os.makedirs(out_dir, exist_ok=True)

def get_dynamic_buffer_size(file_path):
    """Determine the buffer size based on file size dynamically."""
    file_size = os.path.getsize(file_path)
    total_ram = psutil.virtual_memory().total
    print(f"File path: {file_path}\nFile size: {file_size} bytes\nTotal system ram: {total_ram} bytes")
    cal = 1024 * 1024 * 1024
    if total_ram <= 2 * cal: # 2 GB RAM
        return 64 * 1024
    if total_ram <= 4 * cal:  # 4 GB RAM
        return 128 * 1024  # 128 KB
    elif total_ram <= 8 * cal:  # 8 GB RAM
        return 256 * 1024  # 256 KB
    else:
        cal1 = 1024 * 1024
        if file_size < 500 * cal1:  # < 500 MB
            return 64 * 1024   # 64 KB
        elif file_size < 2 * cal:  # < 2 GB
            return 256 * 1024  # 256 KB
        elif file_size < 10 * cal:  # < 10 GB
            return 1 * cal1  # 1 MB
        else:  # 10+ GB
            return 4 * cal1  # 4 MB

def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a 256-bit key from the password using PBKDF2."""
    return PBKDF2(password, salt, dkLen=KEY_SIZE, count=ITERATIONS)

def encrypt_file(file_path, password, output_dir):

    """Encrypt a file using AES-GCM (Authenticated Encryption)."""
    start = time.perf_counter() # starting time counter
    buffersize= get_dynamic_buffer_size(file_path)
    print(f"Buffer size: {buffersize}")
    try:
        with Progress() as progress:
            encrypt_task = progress.add_task('[cyan]Encrypt file...')
            salt = get_random_bytes(SALT_SIZE)
            key = derive_key(password, salt)
            nonce = get_random_bytes(NONCE_SIZE)
            
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)

            if output_dir:
                encrypted_file = os.path.join(output_dir, Path(file_path).name + ".aes")
            else:
                encrypted_file = file_path + ".aes"
    
            with open(file_path, "rb") as f_in, open(encrypted_file, "wb") as f_out:
                f_out.write(salt + nonce)  # Store salt + nonce for decryption
                while chunk := f_in.read(buffersize):
                    f_out.write(cipher.encrypt(chunk))
                tag = cipher.digest()
                f_out.write(tag)  # Store tag at the end
                while not progress.finished:
                        progress.update(encrypt_task, advance=1)
                        time.sleep(0.005)
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
        with Progress() as progress:
            decrypt_task = progress.add_task('[cyan]Decrypt file...')
            with open(file_path, "rb") as f_in:
                salt = f_in.read(SALT_SIZE)
                nonce = f_in.read(NONCE_SIZE)
                key = derive_key(password, salt)

                cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)

                if output_dir:
                    decrypted_file = os.path.join(output_dir, Path(file_path).stem)
                else:
                    decrypted_file = file_path.removesuffix('.aes')

                with open(decrypted_file, "wb") as f_out:
                    ciphertext = f_in.read()
                    tag = ciphertext[-TAG_SIZE:]  # Extract authentication tag
                    ciphertext = ciphertext[:-TAG_SIZE]  # Remove tag from ciphertext
                    f_out.write(cipher.decrypt_and_verify(ciphertext, tag))
                    while not progress.finished:
                        progress.update(decrypt_task, advance=1)
                        time.sleep(0.05)
                ending = time.perf_counter() # end time counter

        print(f"Decryption successful! File saved at: {decrypted_file}")
        print(f"Total encryption time: {ending-start:.6f} seconds")

    except ValueError:
        print("Error: Decryption failed! Incorrect password or corrupted file.")
        os.remove(file_path.removesuffix('.aes'))
    except FileNotFoundError:
        print("Error: File not found.")
    except Exception as e:
        print(f"Decryption failed: {e}")
    del password

def main(PASSWORD, CONFIRM_PASSWORD):

    #arguments
    parser = argparse.ArgumentParser(description="AES Encryption Tool; GNU GENERAL PUBLIC LICENSE version 3")
    parser.add_argument('-v', '--version', action='version', version=f"AES Tool {VERSION}")
    #parser.add_argument('-m', '--mode', type=str, choices=['e', 'd'], help="Mode: 'e' for encryption, 'd' for decryption")
    parser.add_argument('-f', '--file', type=str, help="File to encrypt/decrypt")
    parser.add_argument('-p', '--password', type=str, help="Password (or provide a file path containing the password)")
    parser.add_argument('-o', '--output', type=str, help="Output directory")
    args = parser.parse_args()


    # Resolve files
    if args.file:
        file = args.file
        if os.path.isfile(file):
            if not file.endswith('.aes'):
                if args.password and os.path.isfile(args.password):
                    with open(args.password, "r") as f:
                        PASSWORD = f.readline().strip()
                    CONFIRM_PASSWORD = PASSWORD
                
                elif args.password and not file.endswith('.aes'):
                    PASSWORD = args.password
                    CONFIRM_PASSWORD = getpass.getpass("Confirm password: ")

                else:
                    PASSWORD = getpass.getpass("Enter the password: ")
                    CONFIRM_PASSWORD = getpass.getpass("Confirm password: ")
                    if PASSWORD != CONFIRM_PASSWORD:
                        print("Error: password not matched!")
                        del PASSWORD
                        del CONFIRM_PASSWORD
                        sys.exit(1)
                    else:
                        print("Success: password matched!")
                if args.output:
                    output_dir(args.output)
                
                encrypt_file(file, PASSWORD, args.output)
                del PASSWORD
                del CONFIRM_PASSWORD
            else:
                if args.password and os.path.isfile(args.password):
                    with open(args.password, "r") as f:
                        PASSWORD = f.readline().strip()
                elif args.password:
                    PASSWORD = args.password
                    print(PASSWORD)
                    
                else:
                    PASSWORD = getpass.getpass("Enter the password: ")
                
                file_size = os.path.getsize(file)
                total_ram = psutil.virtual_memory().total
                print(f"File path: {file}\nFile size: {file_size} bytes\nTotal system ram: {total_ram} bytes\nLrage file may take time")
                decrypt_file(file, PASSWORD, args.output)
                del PASSWORD
        else:
            print("Faild: file not found!")
            sys.exit(2)
    else:
        parser.print_help()
        sys.exit(3)