import PySimpleGUI as sg
import os
import shutil
import random
import string
from pathlib import Path

from password_manager.vault import init_vault, load_vault, save_vault
from password_manager.utils import generate_password

VAULT_PATH = Path.home() / ".vault.dat"

def vault_exists():
    return VAULT_PATH.exists()

def generate_captcha(length=12):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def relock_ui(window):
    exists = vault_exists()
    window["Init Vault"].update(visible=not exists)
    window["Unlock"].update(visible=exists)
    window["Delete Vault"].update(visible=exists)
    window["-STATUS-"].update("🔒 Vault is locked. Please unlock to continue.", text_color="red")

def main():
    sg.theme("LightBlue2")

    exists = vault_exists()

    layout_locked = [
        [sg.Text("Master Password"), sg.Input(key="-MPW-", password_char="*")],
        [sg.Button("Init Vault", visible=not exists),
         sg.Button("Unlock", visible=exists),
         sg.Button("Delete Vault", visible=exists)],
        [sg.HorizontalSeparator()],
        [sg.Text("🔒 Vault is locked. Please unlock to continue.", key="-STATUS-", text_color="red")]
    ]

    layout_unlocked = [
        [sg.Button("Logout", button_color="red")],
        [sg.TabGroup([[

            sg.Tab("Add", [
                [sg.Text("Service"), sg.Input(key="-SRV_ADD-")],
                [sg.Text("Username"), sg.Input(key="-USR_ADD-")],
                [sg.Text("Password"), sg.Input(key="-PWD_ADD-")],
                [sg.Checkbox("Generate", key="-GEN-", enable_events=True)],
                [sg.Slider(range=(8, 32), default_value=16, orientation="h", key="-LEN-")],
                [sg.Button("Save Entry")]
            ]),

            sg.Tab("Get", [
                [sg.Text("Search"), sg.Input(key="-GET_SEARCH-", enable_events=True)],
                [sg.Listbox(values=[], size=(40, 6), key="-GET_LIST-", enable_events=True)],
                [sg.Multiline(key="-OUT_GET-", size=(40, 5), disabled=True)]
            ]),

            sg.Tab("List", [
                [sg.Listbox(values=[], size=(40, 12), key="-LIST-", enable_events=False)]
            ])

        ]], key="-TABGROUP-", expand_x=True, expand_y=True)]
    ]

    window = sg.Window("Password Manager", layout_locked, finalize=True)

    vault = {}
    mpw = None
    is_unlocked = False

    while True:
        event, vals = window.read()
        if event in (sg.WIN_CLOSED, None):
            break

        if event == "Init Vault":
            try:
                init_vault(vals["-MPW-"], VAULT_PATH)
                sg.popup("Vault created successfully.")
                relock_ui(window)
            except Exception as e:
                sg.popup_error(str(e))

        if event == "Unlock":
            try:
                mpw = vals["-MPW-"]
                vault = load_vault(mpw, VAULT_PATH)
                is_unlocked = True
                window.extend_layout(window, layout_unlocked)
                window["-STATUS-"].update("🔓 Vault unlocked!", text_color="green")
                window["-LIST-"].update(values=list(vault.keys()))
                window["-GET_LIST-"].update(values=list(vault.keys()))
            except Exception as e:
                sg.popup_error(str(e))
                vault = {}
                mpw = None
                is_unlocked = False
                window["-STATUS-"].update("❌ Unlock failed. Try again.", text_color="red")

        if event == "Logout":
            sg.popup("Vault locked.")
            window.close()
            return main()

        if event == "Delete Vault":
            if not vault_exists():
                sg.popup("No vault file found.")
                continue
            captcha = generate_captcha()
            confirm_layout = [
                [sg.Text("Type the following to confirm deletion:")],
                [sg.Text(f"{captcha}", font=("Courier", 12, "bold"), text_color="red")],
                [sg.Input(key="-CONFIRM-")],
                [sg.Button("Delete"), sg.Button("Cancel")]
            ]
            confirm_win = sg.Window("Confirm Deletion", confirm_layout)
            event2, vals2 = confirm_win.read()
            confirm_win.close()

            if event2 == "Delete" and vals2["-CONFIRM-"] == captcha:
                try:
                    backup_path = VAULT_PATH.with_suffix(".bak")
                    shutil.copy(VAULT_PATH, backup_path)
                    os.remove(VAULT_PATH)
                    sg.popup(f"Vault deleted and backed up to {backup_path}. Restarting.")
                    window.close()
                    return main()
                except Exception as e:
                    sg.popup_error(f"Error deleting vault: {e}")
            elif event2 != "Cancel":
                sg.popup_error("CAPTCHA mismatch. Vault not deleted.")

        if event == "-GEN-":
            window["-PWD_ADD-"].update(disabled=vals["-GEN-"])

        if event == "Save Entry":
            if not is_unlocked:
                sg.popup_error("Vault not unlocked yet.")
                continue
            svc = vals["-SRV_ADD-"].strip()
            usr = vals["-USR_ADD-"].strip()
            pwd = vals["-PWD_ADD-"]
            if vals["-GEN-"]:
                pwd = generate_password(int(vals["-LEN-"]))
                window["-PWD_ADD-"].update(pwd)
            if not svc or not usr or not pwd:
                sg.popup_error("Service, Username, and Password are required.")
                continue
            vault[svc] = {"username": usr, "password": pwd}
            save_vault(mpw, vault, VAULT_PATH)
            sg.popup(f"Saved '{svc}' successfully.")
            window["-LIST-"].update(values=list(vault.keys()))
            window["-GET_LIST-"].update(values=list(vault.keys()))

        if event == "-GET_SEARCH-" and is_unlocked:
            query = vals["-GET_SEARCH-"].strip().lower()
            filtered = [svc for svc in vault.keys() if query in svc.lower()] if query else list(vault.keys())
            window["-GET_LIST-"].update(values=filtered)

        if event == "-GET_LIST-" and is_unlocked:
            selected = vals["-GET_LIST-"]
            if selected:
                svc = selected[0]
                entry = vault.get(svc)
                if entry:
                    msg = f"Service: {svc}\nUsername: {entry['username']}\nPassword: {entry['password']}"
                    window["-OUT_GET-"].update(msg)

    window.close()

if __name__ == "__main__":
    main()
