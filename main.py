import os
import json
import base64
import getpass
import secrets
import string
import PySimpleGUI as sg
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet

# Vault settings
VAULT_FILE = os.path.expanduser("~/.vault.dat")
KDF_ITERATIONS = 390000

# Key derivation
def derive_key(password: bytes, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=32,
        salt=salt, iterations=KDF_ITERATIONS,
        backend=default_backend())
    return base64.urlsafe_b64encode(kdf.derive(password))

# Vault operations
def init_vault():
    if os.path.exists(VAULT_FILE):
        return "Vault already exists."  
    # Prompt via GUI
    pwd = sg.popup_get_text("Create master password:", password_char="*")
    if not pwd: return "Initialization cancelled."
    pwd2 = sg.popup_get_text("Confirm master password:", password_char="*")
    if pwd != pwd2:
        return "Passwords do not match."
    salt = os.urandom(16)
    key = derive_key(pwd.encode(), salt)
    f = Fernet(key)
    empty = json.dumps({}).encode()
    token = f.encrypt(empty)
    blob = {'salt': base64.b64encode(salt).decode(), 'data': base64.b64encode(token).decode()}
    with open(VAULT_FILE, 'w') as fd: json.dump(blob, fd)
    return "Vault initialized successfully."

# Load vault and return (vault_dict, key, salt)
def load_vault():
    if not os.path.exists(VAULT_FILE): raise FileNotFoundError("Vault not found.")
    pwd = sg.popup_get_text("Master password:", password_char="*")
    with open(VAULT_FILE, 'r') as fd: blob = json.load(fd)
    salt = base64.b64decode(blob['salt'])
    key = derive_key(pwd.encode(), salt)
    f = Fernet(key)
    data = base64.b64decode(blob['data'])
    vault = json.loads(f.decrypt(data).decode())
    return vault, key, salt

# Save vault back to file
def save_vault(vault, key, salt):
    f = Fernet(key)
    token = f.encrypt(json.dumps(vault).encode())
    blob = {'salt': base64.b64encode(salt).decode(), 'data': base64.b64encode(token).decode()}
    with open(VAULT_FILE, 'w') as fd: json.dump(blob, fd)

# GUI Layout
globals()['sg.theme']('LightGrey1')
tab1 = [[sg.Button('Initialize Vault', key='-INIT-')]]
tab2 = [
    [sg.Text('Service'), sg.Input(key='-ADD-SERVICE-')],
    [sg.Text('Username'), sg.Input(key='-ADD-USER-')],
    [sg.Text('Password'), sg.Input(key='-ADD-PASS-', password_char='*')],
    [sg.Checkbox('Generate random', key='-ADD-GEN-'), sg.Text('Length'), sg.Spin([i for i in range(8,33)], initial_value=16, key='-ADD-LEN-')],
    [sg.Checkbox('Override existing', key='-ADD-OVR-')],
    [sg.Button('Add Entry', key='-ADD-OK-')],
    [sg.Text('', size=(40,2), key='-ADD-OUT-')]
]
tab3 = [
    [sg.Text('Service'), sg.Input(key='-GET-SERVICE-')],
    [sg.Button('Get Entry', key='-GET-OK-')],
    [sg.Multiline('', size=(40,5), key='-GET-OUT-')]
]
tab4 = [
    [sg.Button('List Services', key='-LIST-OK-')],
    [sg.Listbox(values=[], size=(40,10), key='-LIST-OUT-')]
]
layout = [[sg.TabGroup([[sg.Tab('Init', tab1), sg.Tab('Add', tab2), sg.Tab('Get', tab3), sg.Tab('List', tab4)]])]]
window = sg.Window('Password Manager', layout)

# Event loop
while True:
    event, vals = window.read()
    if event in (sg.WIN_CLOSED, 'Exit'): break
    try:
        if event == '-INIT-':
            msg = init_vault()
            sg.popup(msg)

        elif event == '-ADD-OK-':
            vault, key, salt = load_vault()
            svc = vals['-ADD-SERVICE-'].strip()
            if not svc:
                window['-ADD-OUT-'].update('Service required.')
                continue
            if svc in vault and not vals['-ADD-OVR-']:
                window['-ADD-OUT-'].update('Use override to overwrite existing.')
                continue
            if vals['-ADD-GEN-']:
                alphabet = string.ascii_letters + string.digits + string.punctuation
                pw = ''.join(secrets.choice(alphabet) for _ in range(int(vals['-ADD-LEN-'])))
            else:
                pw = vals['-ADD-PASS-']
            usr = vals['-ADD-USER-'] or ''
            vault[svc] = {'username': usr, 'password': pw}
            save_vault(vault, key, salt)
            window['-ADD-OUT-'].update(f"Saved entry for {svc}.")

        elif event == '-GET-OK-':
            vault, _, _ = load_vault()
            svc = vals['-GET-SERVICE-'].strip()
            entry = vault.get(svc)
            if entry:
                out = f"Service: {svc}\nUsername: {entry['username']}\nPassword: {entry['password']}"
            else:
                out = 'No entry found.'
            window['-GET-OUT-'].update(out)

        elif event == '-LIST-OK-':
            vault, _, _ = load_vault()
            window['-LIST-OUT-'].update(list(vault.keys()))

    except FileNotFoundError:
        sg.popup_error('Vault not initialized. Please initialize first.')
    except Exception as e:
        sg.popup_error('Error:', str(e))

window.close()
