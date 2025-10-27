# Panek Video Program

A simple desktop tool that takes **one image** + **one audio file** and renders a clean **1920×1080 MP4** with AAC audio. Designed for artists, musicians, designers, and anyone making YouTube, TikTok, Loom, Shorts, Reels, or visual loop content.

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
  - macOS → `osascript`
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
