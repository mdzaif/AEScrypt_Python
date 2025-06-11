# aes-tool - A simple encryption tool
# Copyright (C) 2025 Md. Zaif Imam Mahi
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import sys
import os
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
import psutil
import time
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedStyle
import darkdetect 
from threading import Thread
import platform
#Constant
SALT_SIZE = 16
KEY_SIZE = 32
NONCE_SIZE = 12
TAG_SIZE = 16
ITERATIONS = 100_000





def system_plat():
    
    return platform.system()

def apply_system_theme(window):

    system = system_plat()
    style = ttk.Style()
    
    # Detect system theme
    theme = darkdetect.theme().lower()  # Returns 'dark' or 'light'
    window.tk.call('source', r'E:\\github\\AEScrypt_Python\\Forest-ttk-theme\\forest-dark.tcl')
    # Apply the theme
    ttk.Style().theme_use('forest-dark')
    # if system == "Windows":
    #     try:
    #         style.theme_use('forest-dark')
    #     except:
    #         style.theme_use('winnative')
    # elif system == "Darwin":  # macOS
    #     try:
    #         style.theme_use('aqua')
    #     except:
    #         style.theme_use('clam')
    # else:  # Linux and others
    #     style.theme_use('clam')
    #     window.config(bg="white")
    #     window.option_add("*background", "white")
    #     window.option_add("*foreground", "black")

def get_dynamic_buffer_size(file_path):
    """Determine the buffer size based on file size dynamically."""
    file_size = os.path.getsize(file_path)
    total_ram = psutil.virtual_memory().total
    print(f"File path: {file_path}\nFile size: {file_size} bytes\nTotal system ram: {total_ram} bytes\nLarge files take time. Please wait...")
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

def encrypt_file(file_path, password):
    """Get the buffersize"""
    buffersize= get_dynamic_buffer_size(file_path)

    """Encrypt a file using AES-GCM (Authenticated Encryption)."""
    start = time.perf_counter() # starting time counter
    try:
        salt = get_random_bytes(SALT_SIZE)
        key = derive_key(password, salt)
        nonce = get_random_bytes(NONCE_SIZE)
        
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        encrypted_file = file_path + ".aes"
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

def decrypt_file(file_path, password):
    #global password_entry, toggle_btn, confirm_entry, submit_btn, root
    file_size = os.path.getsize(file_path)
    total_ram = psutil.virtual_memory().total
    print(f"File path: {file_path}\nFile size: {file_size} bytes\nTotal system ram: {total_ram} bytes\nLarge files take time. Please wait...")
    """Decrypt a file using AES-GCM (Authenticated Decryption)."""
    start = time.perf_counter() # starting time counter
    try:
        with open(file_path, "rb") as f_in:
            salt = f_in.read(SALT_SIZE)
            nonce = f_in.read(NONCE_SIZE)
            key = derive_key(password, salt)

            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)

            decrypted_file = file_path.removesuffix('.aes')

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
        os.remove(file_path.removesuffix('.aes'))
    except FileNotFoundError:
        print("Error: File not found.")
    except Exception as e:
        print(f"Decryption failed: {e}")

