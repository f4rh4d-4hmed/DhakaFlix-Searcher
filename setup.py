from cx_Freeze import setup, Executable
import sys
import os
import PyQt6

base = "gui" if sys.platform == "win32" else None

qt_plugins_dir = os.path.join(os.path.dirname(PyQt6.__file__), "Qt6", "plugins")

build_exe_options = {
    "packages": ["requests", "bs4", "PyQt6"],
    "include_files": [
        "Jaro-Regular.ttf",
        (qt_plugins_dir, "plugins"),
    ],
    "excludes": ["tkinter"],
}

setup(
    name="DFLIX-Test",
    version="0.1.2",
    description="DFLIX-Test v0.1.2",
    options={"build_exe": build_exe_options},
    executables=[Executable("app.py", base=base)],
)
