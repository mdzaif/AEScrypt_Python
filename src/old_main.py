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

from pyAesCrypt import encryptStream, decryptStream
import argparse
import sys
from os import stat, remove, path
import getpass
from pathlib import Path


# Set up argument parser
parser = argparse.ArgumentParser()
parser.add_argument('-m','--option', type=str, help="encryption: e or decryption: d")
parser.add_argument('-f', '--filename', type=str, help=".aes for decryption and others for encryption do not use folder make folder as copressed file")
parser.add_argument('-p', '--password', type=str, help ="try to give strong password, use a text file with fully qualified path for security")
parser.add_argument('-o', '--output', type=str, help ="specify fully qualified output path and use double qoute for better input", default="./")
args = parser.parse_args()

def encryption(file, bufferSize, password):
    # encrypt
    try:
        com_password = getpass.getpass("Confirm the password: ")
        if password == com_password:
            file1 = Path(file).name
            file1 = output+file1
            file1 = f"{file1}.aes"
            with open(file, "rb") as fIn:
                with open(file1, "wb") as fOut:
                    encryptStream(fIn, fOut, password, bufferSize)
            print(f"Encryption complete! file saved at: {file1}")
        else:
            print("Encryption failed! Password not matched! Try again")
    except FileNotFoundError:
        print("File not found!")
    except PermissionError:
        print("It is maybe a directory! permission error!")

def decryption(file, bufferSize, password):
    #decrypt
    with open(file, "rb") as fIn:
        try:
            file1 = Path(file).name
            file1 = Path(file).stem
            file1 = output+file1
            with open(file1, "wb") as fOut:
                # decrypt file stream
                decryptStream(fIn, fOut, password, bufferSize)
            print(f"Decryption complete! file saved at: {file1}")
        except ValueError:
            # remove output file on error
            remove(file1)
            print("Decryption failed!")
        except FileNotFoundError:
            print("File not found!")


if __name__ == "__main__":

    bufferSize = 64 * 1024

    if not args.option or not args.filename or not args.password:
        parser.print_help()
        sys.exit(1)
    else:
        option = args.option.strip()
        filename = args.filename.strip()
        password = args.password
        output = args.output

        if path.isfile(password):
            password = open(password, "r")
            password = password.readline()
        if option == "d":
            if filename.endswith(".aes"):
                decryption(filename, bufferSize, password)
            else:
                print("Decryption Failed! error: It is not .aes file!")
        elif option == "e":
            encryption(filename, bufferSize, password)
        else:
            print("Wrong Input!")