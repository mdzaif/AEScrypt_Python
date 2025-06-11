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

from modules.gui import sys, os
from modules.window import encrypt_window, decrypt_window, filedialog, Tk


def select_file():
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    root.destroy()
    return file_path

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_to_open = sys.argv[1]
    else:
        file_to_open = select_file()

    if file_to_open and os.path.isfile(file_to_open):
        if not file_to_open.endswith('.aes'):
            encrypt_window(file_to_open)
        else:
            decrypt_window(file_to_open)

#pyinstaller --onefile --windowed --add-data "assets/aes_tool_icon.ico;assets" --icon=assets/aes_tool_icon.ico --hidden-import=psutil --hidden-import=Crypto.Cipher._raw_aes --hidden-import=Crypto.Cipher.AES --name "aes-gui" main.py

