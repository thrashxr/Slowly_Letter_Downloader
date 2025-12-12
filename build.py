import PyInstaller.__main__
import os
import shutil

def build():
    print("Building Slowly Letter Downloader...")
    
    # Define the arguments for PyInstaller
    args = [
        'main.py',                       # Entry point
        '--name=SlowlyLetterDownloader', # Name of the executable
        '--windowed',                    # No console window (GUI mode)
        '--onefile',                     # Single executable file
        '--paths=src',                   # Add src to path
        '--clean',                       # Clean cache
        '--collect-all=customtkinter',   # Collect customtkinter assets
        '--collect-all=playwright',      # Collect playwright drivers
    ]
    
    # Run PyInstaller
    PyInstaller.__main__.run(args)
    
    print("\nBuild complete! Check the 'dist' folder for your executable.")

if __name__ == '__main__':
    build()
