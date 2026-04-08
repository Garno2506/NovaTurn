Contributing to NovaTurn
Thank you for your interest in contributing to NovaTurn, a premium media player built with Python, PyQt5, and VLC.
This project has a frozen architecture and a strict build pipeline, so please read this guide carefully before making
changes.
NovaTurn’s stability depends on maintaining:
a fixed folder structure
a fixed asset-loading system
a fixed VLC bootstrap
a fixed PyInstaller spec
a fixed installer script
Following these rules ensures that NovaTurn continues to build and run correctly in:
development mode
PyInstaller EXE mode
installer mode
clean Windows machines
1. Code of Conduct
Be respectful, constructive, and collaborative. NovaTurn is a craftsmanship-driven project — clarity and maintainability
matter.
2. Project Structure (Frozen)
The folder structure must remain exactly as follows:
Code
MicksMediaPlayer/
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
Do not:
Move or rename folders
Add new top-level folders
Place runtime assets outside app/
Do:
Keep all runtime assets inside app/
Keep all build artifacts outside app/
    3. Asset Loading Rules
All assets must be loaded using the universal loader:
python
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), relat
ive_path)
Do not:
Use absolute paths
Use os.getcwd()
Use __file__ directly for assets
Hard-code Windows paths
Do:
Use relative paths like:
python
resource_path("banners/NovaTurn_OSK.png")
resource_path("assets/branding/novaturn.ico")
resource_path("vlc")
  4. VLC Bootstrap (Protected)
The VLC bootstrap in main.py is frozen.
Do not:
Modify the VLC environment variables
Change the VLC folder location
Rename or restructure app/vlc/
Remove or alter DLL loading logic
Do:
Keep VLC exactly where it is
Add new VLC plugins only if required
5. Build Pipeline (Frozen)
All contributors must follow the official build process.
Step A — Clean (optional)
Delete:
build/
dist/
Step B — Build EXE
Code
& "C:\Program Files\Python314\python.exe" -m PyInstaller app\NovaTurn.spec
Step C — Build Installer
Open Inno Setup and compile:
Code
NovaTurnInstaller.iss
Do not:
Modify the .spec file
Modify the .iss installer paths
Add new PyInstaller hooks unless approved
6. Testing Requirements
Before submitting changes, test NovaTurn in:
Dev mode
Code
python Run.py
EXE mode
Code
dist/NovaTurn/NovaTurn.exe
Installer mode
Code
Output/NovaTurnSetup.exe
Clean machine
A Windows machine with:
no Python
no VLC
no dev tools
This ensures the build is fully self-contained.
7. Code Style
Use clear, descriptive variable names
Keep functions small and modular
Avoid unnecessary complexity
Comment only where logic is non-obvious
Follow PEP8 where practical
8. Protected Files
The following files must not be modified without explicit approval:
NovaTurn.spec
NovaTurnInstaller.iss
app/vlc/
VLC bootstrap in main.py
resource_path() implementation
Folder structure
These are foundational to NovaTurn’s stability.
9. Submitting Changes
1st
2ndFork the repository
3rd
4thCreate a feature branch
5th
6thMake your changes
7th
8thTest in all environments
9th
10thSubmit a pull request with:
a clear description
screenshots if UI changes
explanation of why the change is needed
10. Thank You
Your contributions help NovaTurn grow into a polished, professional media experience. Thank you for respecting the
architecture and helping keep the project stable and beautiful.
