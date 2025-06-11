from modules import functions

PASSWORD = ""
CONFIRM_PASSWORD = ""
if __name__ == "__main__":

    functions.main(PASSWORD, CONFIRM_PASSWORD)

#pyinstaller --onefile --hidden-import=psutil --hidden-import=Crypto.Cipher._raw_aes --hidden-import=Crypto.Cipher.AES --name "aes-tool" main.py
