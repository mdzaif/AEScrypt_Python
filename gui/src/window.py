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

from functions import *
from threading import Thread


class EnterButton(ttk.Button):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        # Bind Enter key to invoke the button's command
        self.bind('<Return>', lambda event: self.invoke())



def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # This exists in PyInstaller bundles
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

icon_path = resource_path("assets/aes_tool_icon.ico")

def close_window(window):
    window.destroy()

def submit(window, file_to_open, password):
    close_window(window)  # Close the password entry window
    show_log_window(file_to_open, password)  # Open log window

def toggle_passwords(window):
    if window == "root1":
        if password_entry.cget('show') == '':
            password_entry.config(show='*')
            toggle_btn.config(text='Show')
        else:
            password_entry.config(show='')
            toggle_btn.config(text='Hide')
    else:
        if password_entry.cget('show') == '':
            password_entry.config(show='*')
            confirm_entry.config(show='*')
            toggle_btn.config(text='Show')
        else:
            password_entry.config(show='')
            confirm_entry.config(show='')
            toggle_btn.config(text='Hide')

def check_password_match(*args):
    pwd = password_entry.get()
    confirm = confirm_entry.get()
    if pwd == "" and confirm == "":
        submit_btn.config(state="disabled")  # Disable button
    elif pwd == confirm:
        submit_btn.config(state="normal", command=lambda: submit(root, file_to_open, password_entry.get()))# Enable button
    else:
        submit_btn.config(state="disabled")  # Disable button



def show_log_window(file_to_open, password):
    class TextRedirector:
        def __init__(self, text_widget):
            self.text_widget = text_widget

        def write(self, message):
            self.text_widget.configure(state='normal')  # Allow writing
            self.text_widget.insert(tk.END, message)
            self.text_widget.see(tk.END)
            self.text_widget.configure(state='disabled')  # Disable editing

        def flush(self):
            pass

    log_window = tk.Tk()
    apply_system_theme()
    # Set a fixed window size
    window_width = 600
    window_height = 350
    log_window.geometry(f"{window_width}x{window_height}")
    log_window.title("Logs")
        # Calculate position to center the window
    screen_width = log_window.winfo_screenwidth()
    screen_height = log_window.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    # Apply the calculated position
    log_window.geometry(f"+{x}+{y}")
    log_window.iconbitmap(icon_path)
    log_window.resizable(False, False)

    log_display = tk.Text(log_window, height=15, width=80, wrap="word")
    log_display.pack(padx=10, pady=10)

    # Redirect print output
    sys.stdout = TextRedirector(log_display)

    if not file_to_open.endswith('.aes'):
        # Encrypt and print logs
        encrypt = Thread(target=encrypt_file, args=(file_to_open, password))
        encrypt.start()
    else:
        # Decrypt and print logs
        decrypt = Thread(target=decrypt_file, args=(file_to_open, password))
        decrypt.start()
    # Disable editing (user can't type in the Text box)
    log_display.configure(state='disabled')

    #log_display.bind("<Tab>", focus_next)

    ok_btn = EnterButton(log_window, text="OK", command=lambda: close_window(log_window))
    ok_btn.pack(padx=10, pady=10)

    log_window.mainloop()

def encrypt_window(file):
    global password_entry, confirm_entry, toggle_btn, file_to_open, submit_btn, root
    file_to_open = file
    root = tk.Tk()
    apply_system_theme()
    # Set a fixed window size
    window_width = 500
    window_height = 150
    root.geometry(f"{window_width}x{window_height}")
    root.iconbitmap(icon_path)
    root.resizable(False, False)
    root.title("Encrypt File")
    # Calculate position to center the window
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    # Apply the calculated position
    root.geometry(f"+{x}+{y}")

    ttk.Label(root, text="Password:").grid(row=0, column=0, padx=10, pady=5, sticky="nesw")
    password_entry = ttk.Entry(root, show="*", width=30)
    password_entry.grid(row=0, column=1, padx=10, pady=5)

    ttk.Label(root, text="Confirm Password:").grid(row=1, column=0, padx=10, pady=5, sticky="nesw")
    confirm_entry = ttk.Entry(root, show="*", width=30)
    confirm_entry.grid(row=1, column=1, padx=10, pady=5)

    toggle_btn = EnterButton(root, text="Show", command=lambda: toggle_passwords("root"))
    toggle_btn.grid(row=0, column=2, padx=10, pady=5)

    confirm_entry.bind("<KeyRelease>", check_password_match)
    password_entry.bind("<KeyRelease>", check_password_match)

    submit_btn = EnterButton(root, text="Encrypt", state="disabled")
    submit_btn.grid(row=3, column=1, pady=10)

    cancel_btn = EnterButton(root, text="Cancel", state="normal", command=lambda: close_window(root))
    cancel_btn.grid(row=1, column=2, pady=10)
    
    root.mainloop()

def decrypt_window(file_to_open):
    global password_entry, toggle_btn, s_btn, root1
    root1 = tk.Tk()
    apply_system_theme()
    # Set a fixed window size
    window_width = 400
    window_height = 150
    root1.geometry(f"{window_width}x{window_height}")
    #root1.geometry("400x150")
    root1.iconbitmap(icon_path)
    root1.resizable(False, False)
    root1.title("Decrypt File")
    # Calculate position to center the window
    screen_width = root1.winfo_screenwidth()
    screen_height = root1.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    # Apply the calculated position
    root1.geometry(f"+{x}+{y}")

    ttk.Label(root1, text="Password:").grid(row=0, column=0, padx=10, pady=5, sticky="nesw")
    password_entry = ttk.Entry(root1, show="*", width=30)
    password_entry.grid(row=0, column=1, padx=10, pady=5)

    toggle_btn = EnterButton(root1, text="Show", command=lambda: toggle_passwords("root1"))
    toggle_btn.grid(row=0, column=2, padx=10, pady=5)

    s_btn = EnterButton(root1, text="Decrypt", state="normal", command=lambda: submit(root1, file_to_open, password_entry.get()))
    s_btn.grid(row=1, column=1, pady=10, sticky='w')

    cancel_btn = EnterButton(root1, text="Cancel", state="normal", command=lambda: close_window(root1))
    cancel_btn.grid(row=1, column=1, pady=10, sticky='e')

    root1.mainloop()