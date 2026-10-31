
name: Build MovieFolderCovers EXE

on:
  workflow_dispatch:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: windows-latest

    steps:
      - name: Get source
        uses: actions/checkout@v4

      - name: Install Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install libraries
        run: |
          python -m pip install --upgrade pip
          pip install Pillow pywin32 pyinstaller

      - name: Build EXE
        run: |
          pyinstaller --noconfirm --clean --onefile --windowed --name MovieFolderCovers --collect-all win32com --hidden-import=pythoncom --hidden-import=pywintypes movie_folder_covers.py

      - name: Upload EXE
        uses: actions/upload-artifact@v4
        with:
          name: MovieFolderCovers-Windows-64bit
          path: dist/MovieFolderCovers.exe
