   # Changelog
   
   All notable changes to Panek Video Program.
   
   ## [2.0.0] - 2025-10-28
   
   ### 🎉 Complete Modernization Rewrite
   
   #### Changed
   - **Framework Migration**: PyQt5 → PySide6 for better licensing and modern Qt6 support
   - **Architecture**: Complete separation of UI and backend using signal/slot pattern
   - **UI Theme**: Professional dark theme via qdarktheme library
   - **Progress Bar**: Fixed progress tracking (removed `-nostats` bug)
   - **File Dialogs**: Native QFileDialog instead of OS-specific cascade
   
   #### Added
   - ✅ **Overwrite Protection**: Confirmation dialog before overwriting existing files
   - ✅ **Pre-flight Validation**: Checks all inputs exist before starting render
   - ✅ **Auto-close Timer**: 30-second countdown on completion dialog
   - ✅ **Windows Console Suppression**: Cleaner experience on Windows
   - ✅ **Improved Error Handling**: Clear error messages for missing files
   
   #### Removed
   - ❌ Custom CSS stylesheets (replaced with qdarktheme)
   - ❌ OS-specific dialog detection (kdialog/zenity/osascript)
   - ❌ Manual style management code
   
   #### Technical
   - New `FFmpegRunner` class handles all QProcess operations
   - Proper signal/slot communication between UI and backend
   - Clean separation of concerns
   
   ## [1.0.1] - 2025-10-27
   
   ### Fixed
   - Initial stable release with PyQt5
   - Basic functionality established
   
   ## [1.0.0] - 2025-10-26
   
   ### Added
   - Initial release
   - PyQt5-based UI
   - FFmpeg integration
   - Support for JPG, PNG, WEBP images
   - Support for MP3, WAV audio
