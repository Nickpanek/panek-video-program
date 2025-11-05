   # Changelog

   All notable changes to Panek Video Program.

   ## [3.0.0] - 2025-11-05

   ### 🎉 Enhanced Edition - Major Feature Expansion

   #### Added
   - ✨ **Text Overlays**: Add custom text to videos with full styling control
     - Position options: Top, Center, Bottom
     - Font size: 12-200pt adjustable
     - Color picker for any text color
     - Automatic text escaping for FFmpeg compatibility
   - 🎬 **Video File Input**: Support for video files as input (not just images)
     - Formats: MP4, MOV, AVI, MKV, WEBM, FLV, WMV, M4V, MPG, MPEG
     - Intelligent processing: videos use standard encoding, images use stillimage tune
     - Automatic media type detection
   - 🌅 **Fade Transitions**: Professional fade in/out effects
     - Independent video and audio fading
     - Range: 0-10 seconds in 0.5 second increments
     - Synchronized video and audio transitions

   #### Changed
   - Renamed "Image File" to "Media File" throughout UI
   - Enhanced FFmpeg command builder with filter chain support
   - Increased minimum window size to 700x900 for new features
   - Updated window title to "Enhanced Edition v3.0"

   #### Technical
   - New video filter chain: scale, pad, fade, drawtext
   - New audio filter chain: afade
   - Added `is_video_file()` utility function
   - Enhanced `_build_ffmpeg_cmd()` with 6 new parameters
   - New UI components: QGroupBox, QComboBox, QSpinBox, QDoubleSpinBox, QColorDialog
   - Text color preview widget with live updates
   - All new controls integrated with enable/disable during render

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
