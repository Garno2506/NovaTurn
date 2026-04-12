NovaTurn — Premium Media Player for Windows
NovaTurn is a modern, cinematic media player for Windows, built with Python, PyQt5, and VLC.
It delivers a fast, polished, and visually rich experience with a custom UI, dynamic animations, a touch‑friendly on‑screen keyboard, and a fully self‑contained installer that runs on any clean Windows machine.

NovaTurn is engineered with a stable build pipeline, PyInstaller‑safe asset loading, and a frozen folder structure to guarantee reliability across development, EXE builds, and installer deployments.

✨ Features
Cinematic UI built with PyQt5

VLC‑powered audio & video playback

Custom On‑Screen Keyboard (OSK) for touch devices

Media Library with metadata extraction (Mutagen)

Plugin‑ready architecture

Password‑protected sections

PyInstaller‑safe asset loader

Fully self‑contained Windows installer (no Python or VLC required)

Stable folder structure designed for reproducible builds

📁 Project Structure
Code
NovaTurn/
│
├── Run.py
├── NovaTurn.spec
├── NovaTurnInstaller.iss
│
├── app/
│   ├── main.py
│   ├── ui/
│   ├── banners/
│   ├── assets/
│   │   └── branding/
│   ├── vlc/
│   └── db/
│
├── dist/
├── build/
└── Output/
Rules
All runtime assets live inside app/

All build artifacts (dist/, build/, Output/) live outside app/

Folder names and locations are frozen — do not change them

🔧 Universal Asset Loader
NovaTurn uses a PyInstaller‑safe loader that works in:

Dev mode

EXE mode

Installer mode

Clean machines

python
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), relative_path)
Example usage:

python
resource_path("banners/NovaTurn_OSK.png")
resource_path("assets/branding/novaturn.ico")
resource_path("vlc")
🎬 VLC Integration
NovaTurn bundles a full VLC runtime inside:

Code
app/vlc/
The VLC bootstrap:

Sets PYTHON_VLC_LIB_PATH

Sets VLC_PLUGIN_PATH

Ensures DLLs load correctly

Works in dev mode and EXE mode

This section is protected — do not modify it.

🛠 Build Pipeline
1. Clean (optional but recommended)
Delete:

Code
build/
dist/
2. Build the EXE
From the project root:

powershell
& "C:\Program Files\Python314\python.exe" -m PyInstaller app\NovaTurn.spec
Output:

Code
dist/NovaTurn/
3. Build the Installer
Open Inno Setup and compile:

Code
NovaTurnInstaller.iss
Output:

Code
Output/NovaTurnSetup.exe
This installer is fully self‑contained and works on clean Windows machines.

🧪 Testing Workflow
Dev mode
powershell
python Run.py
EXE mode
powershell
dist/NovaTurn/NovaTurn.exe
Installer mode
powershell
Output/NovaTurnSetup.exe
Clean machine
A Windows machine with:

no Python

no VLC

no dev tools

This confirms the build is fully self‑contained.

🤝 Contributor Guidelines
Anyone contributing to NovaTurn must follow these rules:

Do not move or rename folders

Do not modify the VLC bootstrap

Do not bypass resource_path()

Do not modify the .spec file

Do not modify installer paths

Do not introduce absolute paths

Do not add assets outside app/

Breaking these rules risks:

EXE build failures

Installer failures

Clean‑machine incompatibility

🚀 Release Workflow
Update version in .iss

Clean build

Build EXE

Build installer

Test on clean machine

Archive installer

Tag release in GitHub

📄 License
(NovaTurn Proprietary License Agreement
Copyright © 2026 Michael Garnett. All rights reserved.
This software, including all source code, compiled binaries, assets, images, icons, UI layouts, documentation, and asso
ciated files (collectively, the “Software”), is the exclusive property of Michael Garnett.
By installing, copying, accessing, or using the Software, you agree to the terms of this License Agreement.
1. Grant of License
You are granted a non-exclusive, non-transferable, revocable license to install and use the Software for personal use
only.
No other rights are granted.
2. Restrictions
You may NOT, under any circumstances:
Copy, distribute, or publish the Software
Modify, decompile, disassemble, or reverse-engineer the Software
Create derivative works based on the Software
Sell, rent, lease, sublicense, or otherwise commercialize the Software
Remove or alter any copyright notices, branding, or proprietary markings
Redistribute the installer, executable, or any bundled files
Use any part of the Software’s code, UI, assets, or design in another project
Any violation of these restrictions terminates your license immediately.
3. Ownership
The Software is licensed, not sold.
All rights, title, and interest in the Software remain the exclusive property of Michael Garnett, including but not limited to:
Source code
Compiled binaries
UI/UX design
Branding and artwork
Media assets
Build scripts
Installer scripts
Documentation
Database structures
Custom modules and integrations
4. No Warranty
The Software is provided “as is”, without warranty of any kind, express or implied.
You assume all risks associated with using the Software.
5. Limitation of Liability
In no event shall the author be liable for:
Damages
Data loss
Loss of profits
System failures
Or any other consequences arising from the use or inability to use the Software
6. Termination
This license terminates automatically if:
You violate any terms of this agreement
You attempt to reverse-engineer or modify the Software
You redistribute any part of the Software
Upon termination, you must immediately delete all copies of the Software.
7. Updates
The author may provide updates, patches, or new versions at their discretion. This license applies to all updates unless
explicitly stated otherwise.
8. Governing Law
This agreement is governed by the laws of the United Kingdom.
9. Contact
For licensing inquiries, permissions, or commercial use requests, contact the author directly)

🙏 Credits
NovaTurn is built with:

Python

PyQt5

VLC

Mutagen

Inno Setup

PyInstaller

…and a lot of craftsmanship, iteration, and attention to detail.
