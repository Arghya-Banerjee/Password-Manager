import PySimpleGUI as sg

from password_manager.vault import init_vault, load_vault, save_vault
from password_manager.utils import generate_password

def main():
    sg.theme("LightBlue2")

    # Initial layout: only unlock area
    layout_locked = [
        [sg.Text("Master Password"), sg.Input(key="-MPW-", password_char="*")],
        [sg.Button("Init Vault"), sg.Button("Unlock")],
        [sg.HorizontalSeparator()],
        [sg.Text("🔒 Vault is locked. Please unlock to continue.", key="-STATUS-", text_color="red")]
    ]

    # Layout shown after unlocking
    layout_unlocked = [
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

        # Init vault
        if event == "Init Vault":
            try:
                init_vault(vals["-MPW-"])
                sg.popup("Vault created successfully.")
            except Exception as e:
                sg.popup_error(str(e))

        # Unlock vault
        if event == "Unlock":
            try:
                mpw = vals["-MPW-"]
                vault = load_vault(mpw)
                is_unlocked = True
                window["-STATUS-"].update("🔓 Vault unlocked!", text_color="green")

                # Extend layout with main tabs
                window.extend_layout(window, layout_unlocked)
                # Populate full list in "List" tab
                window["-LIST-"].update(values=list(vault.keys()))
                # Also preload into Get tab search list
                window["-GET_LIST-"].update(values=list(vault.keys()))

            except Exception as e:
                sg.popup_error(str(e))
                vault = {}
                mpw = None
                is_unlocked = False
                window["-STATUS-"].update("❌ Unlock failed. Try again.", text_color="red")

        # Password generator toggle
        if event == "-GEN-":
            window["-PWD_ADD-"].update(disabled=vals["-GEN-"])

        # Save Entry
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
            save_vault(mpw, vault)
            sg.popup(f"Saved '{svc}' successfully.")

            # Refresh both lists
            window["-LIST-"].update(values=list(vault.keys()))
            window["-GET_LIST-"].update(values=list(vault.keys()))

        # Live search in Get tab
        if event == "-GET_SEARCH-" and is_unlocked:
            query = vals["-GET_SEARCH-"].strip().lower()
            if query == "":
                filtered = list(vault.keys())
            else:
                filtered = [svc for svc in vault.keys() if query in svc.lower()]
            window["-GET_LIST-"].update(values=filtered)

        # Double-click to retrieve credentials in Get tab
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
