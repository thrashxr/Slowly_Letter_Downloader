# Slowly Letter Downloader

**A cross-platform tool to back up your Slowly letters safely, locally, and in an organized format.**
This tool automates downloading your letters from the official Slowly web app and saves them as clean PDF files grouped by pen pal.

Slowly does not currently offer any built-in export or backup feature. Many users have years of conversations and personal memories stored inside the app — this project aims to give you control over your own data while keeping everything on your device.

---

## ✨ Features

* **Cross-platform:** macOS, Windows, and Linux supported
* **Modern browser automation:** powered by Playwright
* **Persistent login sessions:** no need to sign in every time
* **Simple and clean graphical interface**
* **Organized exports:** letters sorted into per-pen-pal folders
* **Duplicate detection:** existing files are skipped automatically
* **Local-only processing:** all data stays on your computer

---

## 📦 Requirements

* Python **3.8+**
* Google Chrome browser installed

---

## 🔧 Installation

Clone or download the repository:

```bash
git clone https://github.com/yourname/Slowly_Letter_Downloader
cd Slowly_Letter_Downloader
```

Install required Python packages:

```bash
pip install -r requirements.txt
```

Install the browser engine for Playwright:

```bash
playwright install chromium
```

> Playwright automatically downloads its own Chromium build — no manual driver installation needed.

---

## 🚀 Usage

Start the application:

```bash
python main.py
```

### Workflow

1. Click **Login**
   A browser window will open.

2. Sign in to your Slowly account inside that browser.

3. After login completes, return to the app and click **Scan Friends**
   Your pen pals will be listed.

4. Select the pen pals whose letters you want to export.

5. Click **Download Selected**
   Letters will be downloaded and saved as PDF files.

All exported letters will appear inside a folder named **Slowly Letters** on your Desktop, organized by pen pal.

---

## 📁 Project Structure

```
src/sld/
│
├── core/        # Browser automation, scraping logic, PDF generation
├── gui/         # Graphical user interface components
└── config.py    # Paths, session storage, configuration management
```

The project intentionally separates core logic and UI, making it easier to maintain, test, and extend.

---

## 🔒 Privacy & Safety Notes

* This tool only accesses **your own Slowly account**.
* No data is uploaded, shared, or sent to any server — everything stays on your machine.
* The project does **not** attempt to interact with other users’ data or bypass any security restrictions.
* It is intended **solely for personal backups** of your own letters.

Slowly Communications Ltd. does not provide a data export option, despite many users relying on the app for long-term correspondence. This tool exists to give individuals control over their personal archives.

---

## ⚠️ Terms of Service Notice (Read Before Use)

Automated tools can fall under “scraping” depending on Slowly's Terms of Service wording.
Use this tool responsibly and only on your own account. The author assumes no liability for any misuse or account issues.

---

## 🤝 Contributing

Contributions, bug reports, and feature suggestions are welcome!

If you’d like to help:

1. Fork the project
2. Create a feature branch
3. Submit a pull request

Please keep core logic and UI separate when adding new features.

---

## ❤️ Acknowledgements

Thanks to the Slowly community for the encouragement, the testing feedback, and the motivation to keep improving the tool. Many users have years of memories stored inside Slowly — preserving them matters.
