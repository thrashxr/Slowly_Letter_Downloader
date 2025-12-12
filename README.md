# Slowly Letter Downloader

A cross-platform tool to backup and download letters from the Slowly web application. This tool automates the process of saving your letters as PDF files, organizing them by pen pal.

## Features

-  Cross-platform support for macOS, Windows, and Linux
-  Modern browser automation using Playwright
-  Persistent login sessions to avoid repeated sign-ins
-  Clean and simple graphical user interface
-  Automatically organizes downloads by pen pal name
-  Detects existing files to avoid duplicates

## Requirements

-  Python 3.8 or higher
-  Google Chrome browser

## Installation

1. Clone or download the repository
2. Install the required Python packages

   pip install -r requirements.txt

3. Install the browser binaries for Playwright

   playwright install chromium

## Usage

Run the main script to start the application:

python main.py

1. Click Login to open the browser.
2. Sign in to your Slowly account in the opened window.
3. Once logged in, click Scan Friends to load your pen pal list.
4. Select the pen pals whose letters you want to download.
5. Click Download Selected to start the process.

Letters are saved to the Slowly Letters folder on your Desktop.

## Project Structure

-  src/sld/core: Core logic for browser automation and downloading
-  src/sld/gui: User interface components
-  src/sld/config.py: Configuration and path management

## Disclaimer

This tool is not affiliated with or endorsed by Slowly Communications Ltd. It is intended for personal backup purposes only.
