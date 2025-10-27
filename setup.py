from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["requests", "bs4", "pyqt6"],
    "include_files": ["Jaro-Regular.ttf"],
}

setup(
    name="DFLIX-Test",
    version="0.1.1",
    description="DFLIX-Test v0.1.1",
    options={"build_exe": build_exe_options},
    executables=[Executable("app.py", base=None)],
)
