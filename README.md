# Panek Video Program

A simple desktop tool that takes **one image** + **one audio file** and renders a clean **1920×1080 MP4** with AAC audio. Designed for artists, musicians, designers, and anyone making YouTube, TikTok, Loom, Shorts, Reels, or visual loop content. 
## 🚀 Upcoming v2.0: The PySide6 Modernization Refactor

We are excited to announce an upcoming, major rewrite of the Panek Video Program. This update is currently in testing and will completely modernize the codebase, improve the user experience, and establish a professional architecture that is more stable, maintainable, and responsive.

### Summary of Changes

The application has been rebuilt from the ground up, moving from a single-file `PyQt5` script to a modern, decoupled `PySide6` application. This addresses several long-standing bugs, simplifies the code, and adds critical new features.

### Key Architectural & Feature Changes

* **Framework Migration: `PyQt5` to `PySide6`**
    The entire application has been ported from `PyQt5` to `PySide6`. This moves the project to a more modern toolkit with a more flexible (LGPL) license, ensuring future compatibility and easier distribution.

* **New Architecture: Decoupled UI and Backend**
    * **Before:** The original script was a single monolithic class (`MainUI`) that handled both the UI layout and the `QProcess` execution.
    * **After:** The new architecture (based on the "Modern Python Application" guide) separates concerns. The `MainWindow` class now *only* handles UI events. A new `FFmpegRunner` class now lives in the "core" and manages all `QProcess` logic, emitting signals for logs, progress, and completion. This makes the application far more stable and prevents the UI from freezing.

* **New UI: Professional Dark Theme & Minimalist Layout**
    * **Before:** The UI used custom-coded stylesheets (e.g., the gray/green render button, colored labels) that were difficult to maintain.
    * **After:** All custom stylesheets have been removed. The app now uses the `pyqtdarktheme` library to apply a consistent, professional, and fully-featured dark theme with a single line of code. The layout has also been simplified from manual `QHBoxLayout`s to a clean `QFormLayout`.

* **New Feature: File Overwrite Confirmation**
    * **Before:** The app used an `ffmpeg -y` flag, which would *silently overwrite* any existing video with the same name.
    * **After:** The app now checks if the output file exists *before* rendering. If it does, a native confirmation dialog asks the user if they wish to proceed, preventing accidental data loss.

* **New Feature: Pre-flight File Validation**
    * **Before:** A render could be started, only to fail 30 seconds later because an input file was moved or deleted.
    * **After:** The app now performs validation *before* starting `ffmpeg`. It checks that the selected image file, audio file, and output directory all exist, showing a clear warning if anything is missing.

* **Code Simplification: Removed Dialog Cascade**
    * **Before:** The original script included ~100 lines of complex "cascade" logic (`kde_getopenfilename`, `zenity_getopenfilename`, `osascript_choose_file`) to manually detect the user's OS and show the "correct" native file dialog.
    * **After:** This entire system has been removed. The new script uses `QFileDialog` directly, which `PySide6` automatically and correctly maps to the native system dialog on Windows, macOS, KDE, and GNOME.

* **Bug Fix: Correct Progress Bar Parsing**
    * **Before:** The original script had a bug where it used `ffmpeg -nostats`, which *disables* the progress information it was trying to read.
    * **After:** The bug is fixed. The `ffmpeg` command now correctly pipes progress to `stdout` (which the `FFmpegRunner` reads for the progress bar) and logs to `stderr` (which is shown in the log window). This results in a reliable and responsive progress bar.

### New Dependencies (for v2.0)

To run this new version, the dependencies will change.

**Old Dependencies:**
* `python3-pyqt5`

**New Dependencies:**
* `PySide6`
* `pyqtdarktheme`

They can be installed via pip:
```bash
pip install PySide6
pip install pyqtdarktheme



### 📖 Documentation & Support
- **[User Manual](MANUAL.md)** - Complete guide with installation, usage, and troubleshooting
- **[🤖 AI Help Desk](https://chatgpt.com/g/g-68ff031d991081919e3da5b0b7ea683f-panek-video-program-help-desk)** - Get instant help with installation and debugging across all platforms

### Features
- Supports **JPG, PNG, WEBP** images
- Supports **MP3 and WAV** audio
- Output: **H.264 MP4**, yuv420p, CRF 20, faststart enabled
- Native system file dialogs:
  - KDE → `kdialog`
  - GNOME/XFCE → `zenity`
  - macOS → `osascript` (if developed)
  - fallback → Qt dialog
- Render button only enables when both files are selected
- Output filename auto-generates if no title is given

### Requirements
- **ffmpeg** and **ffprobe** must be installed

**Need help installing FFmpeg?** → [AI Help Desk](https://chatgpt.com/g/g-68ff031d991081919e3da5b0b7ea683f-panek-video-program-help-desk)

### Install (Linux)
Download the `.AppImage` or `.deb` from Releases:

➡️ https://github.com/Nickpanek/panek-video-program/releases/latest

**Installation issues?** → [AI Help Desk](https://chatgpt.com/g/g-68ff031d991081919e3da5b0b7ea683f-panek-video-program-help-desk) for step-by-step guidance

### Run (Source)
```bash
python3 panek_video_program.py
```

### Support
- 🤖 [AI Help Desk](https://chatgpt.com/g/g-68ff031d991081919e3da5b0b7ea683f-panek-video-program-help-desk) - Trained on installation & debugging
- 📖 [User Manual](MANUAL.md) - Comprehensive documentation
- 🐛 [GitHub Issues](https://github.com/Nickpanek/panek-video-program/issues) - Bug reports & feature requests
- ☕ [Buy Me a Coffee](https://buymeacoffee.com/prompternick) - Support development
- 🔬 [PatternRipple Lab](https://www.patternripple.com/lab) - More tools
