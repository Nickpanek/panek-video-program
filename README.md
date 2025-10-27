# Panek Video Program

A simple desktop tool that takes **one image** + **one audio file** and renders a clean **1920×1080 MP4** with AAC audio. Designed for artists, musicians, designers, and anyone making YouTube, TikTok, Loom, Shorts, Reels, or visual loop content.

### Features
- Supports **JPG, PNG, WEBP** images
- Supports **MP3 and WAV** audio
- Output: **H.264 MP4**, yuv420p, CRF 20, faststart enabled
- Native system file dialogs:
  - KDE → `kdialog`
  - GNOME/XFCE → `zenity`
  - macOS → `osascript`
  - fallback → Qt dialog
- Render button only enables when both files are selected
- Output filename auto-generates if no title is given

### Requirements
- **ffmpeg** and **ffprobe** must be installed

### Install (Linux)
Download the `.AppImage` or `.deb` from Releases:

➡ https://github.com/Nickpanek/panek-video-program/releases/latest

### Run (Source)
```bash
python3 panek_video_program.py
