# 🔐 Password Manager – Secure, Simple, Offline

A beautiful, **offline-first**, and **zero-knowledge** password manager built with Python and PySimpleGUI.  
No internet, no database, no tracking — just **strong encryption**, clean UI, and peace of mind.

---

## ✨ Features

- ✅ Master-password-based vault encryption (AES + PBKDF2)
- 🧠 Smart UI: shows only relevant actions (Init/Unlock/Delete Vault)
- 🔍 Search & retrieve passwords instantly
- 🧾 Copy-safe view, no accidental exposure
- 🔐 Data stored **locally only** in encrypted format
- 🛑 CAPTCHA-based vault deletion confirmation
- 📦 Packable as a single `.exe` for Windows use


---

## 🚀 Quick Start

### 🔧 Requirements
- Python 3.11+
- Windows/Linux/macOS
- No database or internet needed

### 📦 Install dependencies

```bash
git clone https://github.com/yourusername/password-manager.git
cd password-manager
python -m venv .venv
.venv\Scripts\activate  # or source .venv/bin/activate
pip install -r requirements.txt
```

---

## 💻 Running the App

### ▶️ GUI Mode

```bash
python -m password_manager.gui
```

### 🖥 CLI Mode

```bash
python -m password_manager.cli init
python -m password_manager.cli add example.com -u alice --generate
python -m password_manager.cli get example.com
python -m password_manager.cli list
```

> 📁 Your vault is securely stored in your home directory as `.vault.dat`

---

## 🔒 Security Design

| Layer         | Implementation                          |
|---------------|------------------------------------------|
| Encryption    | AES via `Fernet` (symmetric cipher)      |
| Key Derivation| PBKDF2HMAC with 390k iterations + salt   |
| Vault File    | Encrypted JSON blob, base64-encoded      |
| Storage       | Local only (`~/.vault.dat`)              |
| Recovery      | Zero-knowledge: no password = no recovery|

---

## 📁 Folder Structure

```
password-manager/
├── .venv/                  ← Local virtual env (gitignored)
├── src/
│   └── password_manager/
│       ├── gui.py          ← Main GUI script
│       ├── cli.py          ← CLI interface
│       ├── crypto.py       ← KDF + encryption logic
│       ├── vault.py        ← Load/save vault securely
│       └── utils.py        ← Shared helpers (e.g., password gen)
├── tests/                  ← Pytest-based tests
├── requirements.txt        ← Dependencies
├── .gitignore
└── README.md               ← This file
```

---

## 📦 Building a Windows `.exe`

```bash
pip install pyinstaller
pyinstaller --onefile --windowed src/password_manager/gui.py --name password-manager
```

> Output will be in the `dist/` folder:  
> `dist/password-manager.exe`

---

## 🧑‍💻 Author

**Arghya Banerjee**  
📧 [arghya.banerjee.dev@gmail.com](mailto:arghya.banerjee.dev@gmail.com)  
🌐 [LinkedIn](https://linkedin.com/in/arghya-banerjee-32a018229) | [GitHub](https://github.com/Arghya-Banerjee)

---

## ⚖️ License

This project is licensed under the MIT License.

---

## 🤝 Contributions

If you'd like to suggest a feature or report a bug, feel free to open an issue or PR!
