# Panek Video Program - User Manual

**A Simple Tool for Creating Video Content**

Welcome! This manual will help you create professional 1920×1080 MP4 videos from a single image and audio file. Perfect for YouTube uploads, social media content, music releases, podcasts, and visual presentations.

**🤖 Need Help?** Our [AI Help Desk](https://chatgpt.com/g/g-68ff031d991081919e3da5b0b7ea683f-panek-video-program-help-desk) is trained on installation and troubleshooting across all platforms. Get instant answers 24/7!

---

## What Does It Do?

Panek Video Program takes:
- **One image** (your album cover, logo, artwork, photo, etc.)
- **One audio file** (your song, podcast, narration, etc.)

And creates:
- **A high-quality 16:9 MP4 video** ready to upload anywhere

The video automatically scales your image to fit 1920×1080, adds black bars if needed, and syncs the audio perfectly. No video editing experience required!

---

## System Requirements

### All Systems
- **FFmpeg** must be installed (see installation section below)
- At least 500 MB of free disk space
- Basic file management skills (finding files, choosing folders)

### Linux
- Any modern Linux distribution (Ubuntu, Fedora, Mint, Pop!_OS, etc.)
- Works with KDE, GNOME, XFCE, and most desktop environments

### macOS
- macOS 10.13 or newer recommended

---

## Installation

**Need installation help?** Our [AI Help Desk](https://chatgpt.com/g/g-68ff031d991081919e3da5b0b7ea683f-panek-video-program-help-desk) can walk you through the process step-by-step for your specific operating system.

### Linux Users (Recommended)

You have two options:

#### Option 1: AppImage (Works Everywhere)
1. Go to [https://github.com/Nickpanek/panek-video-program/releases/latest](https://github.com/Nickpanek/panek-video-program/releases/latest)
2. Download `PanekVideoProgram-x86_64.AppImage`
3. Open your file manager and navigate to your Downloads folder
4. Right-click the AppImage file → Properties → Permissions
5. Check "Allow executing file as program" or "Make executable"
6. Double-click to run!

**Note:** You may need to install `libfuse2` first:
```bash
sudo apt install libfuse2
```

#### Option 2: DEB Package (Ubuntu/Debian/Mint)
1. Go to [https://github.com/Nickpanek/panek-video-program/releases/latest](https://github.com/Nickpanek/panek-video-program/releases/latest)
2. Download the `.deb` file
3. Double-click the file to install via Software Center, or run:
```bash
sudo dpkg -i panek-video-program*.deb
```
4. Launch from your applications menu

### macOS Users

Currently requires running from source (see Advanced section).

### Installing FFmpeg (Required!)

The program needs FFmpeg to create videos.

**Ubuntu/Debian/Mint:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Fedora:**
```bash
sudo dnf install ffmpeg
```

**macOS (using Homebrew):**
```bash
brew install ffmpeg
```

To verify FFmpeg is installed, open Terminal and type:
```bash
ffmpeg -version
```

If you see version information, you're good to go!

---

## Using the Program

### Step-by-Step Guide

1. **Launch the program**
   - Double-click the AppImage, or
   - Find "Panek Video Program" in your applications menu

2. **Choose your output folder** (optional)
   - Click "Choose Output Folder" to select where your video will be saved
   - By default, it saves to the folder where you launched the program

3. **Set a title** (optional)
   - Type a name for your video in the title field
   - If you leave it blank, the program will auto-generate a name with the date and time
   - Example: `my-awesome-song` becomes `my-awesome-song.mp4`

4. **Choose your image**
   - Click "Choose Image"
   - Select your JPG, PNG, or WEBP file
   - **Tip:** 16:9 images (1920×1080, 1280×720, etc.) work best and won't have black bars

5. **Choose your audio**
   - Click "Choose Audio"
   - Select your MP3 or WAV file
   - The video length will match your audio length exactly

6. **Click "Render Video"**
   - The button turns green when you're ready
   - You'll see a progress bar as the video is created
   - This can take a few seconds to several minutes depending on audio length

**New in v2.0:** If a file with the same name already exists, the program will ask if you want to overwrite it. Choose "Yes" to replace it or "No" to cancel and choose a different name.

7. **Done!**
   - A popup will show you where your video was saved
   - You can render another video or close the program

---

## Tips for Best Results

### Image Tips
- **Use 16:9 aspect ratio** images when possible (1920×1080 is perfect)
- Square images will get black bars on the sides
- Vertical images will get black bars on the top and bottom
- High resolution images work great – the program will scale them properly
- Supported formats: JPG, JPEG, PNG, WEBP

### Audio Tips
- Both MP3 and WAV files work perfectly
- The final video will be exactly as long as your audio
- Audio is converted to AAC format at 192kbps for compatibility
- Any sample rate or bitrate will work

### File Naming
- Avoid special characters in your title (like `/ \ : * ? " < > |`)
- The program will automatically clean up problematic characters
- Spaces are fine and will be preserved

---

## Troubleshooting

**💡 Quick Help:** Can't find your answer below? Try our [AI Help Desk](https://chatgpt.com/g/g-68ff031d991081919e3da5b0b7ea683f-panek-video-program-help-desk) for instant, personalized troubleshooting based on your specific system and issue.

---

### "ffmpeg not found" Error
**Problem:** The program can't find FFmpeg on your system.

**Solution:**
1. Install FFmpeg using the instructions in the Installation section
2. Restart the program after installing FFmpeg

### Video Won't Play on Some Devices
**Problem:** Video plays on computer but not on phone or TV.

**Solution:** This shouldn't happen with Panek Video Program – it creates highly compatible MP4 files. If you encounter this, please report it as a bug.

### Render Button Stays Gray
**Problem:** Can't click the Render button.

**Solution:**
- Make sure you've selected both an image AND an audio file
- Both labels should show file paths, not "not selected"
- The button will turn green when both files are chosen

### Program Crashes or Freezes
**Problem:** Program stops responding during render.

**Solution:**
1. Check if FFmpeg is still running (look in System Monitor/Activity Monitor)
2. Very long audio files (hours) may take significant time
3. Try with a shorter audio clip first to test
4. Check the log window at the bottom for error messages

### AppImage Won't Launch (Linux)
**Problem:** Double-clicking does nothing.

**Solution:**
1. Make sure the file is executable (right-click → Properties → Permissions)
2. Install `libfuse2`: `sudo apt install libfuse2`
3. Try running from terminal to see error messages:
   ```bash
   ./PanekVideoProgram-x86_64.AppImage
   ```

**Still stuck?** Paste your error message into the [AI Help Desk](https://chatgpt.com/g/g-68ff031d991081919e3da5b0b7ea683f-panek-video-program-help-desk) for system-specific guidance.

### File Dialog Doesn't Open
**Problem:** Nothing happens when clicking file selection buttons.

**Solution:** The program tries multiple dialog systems. If one fails, you can:
1. Update your system
2. Install dialog tools: `sudo apt install kdialog zenity`
3. Check the log window for specific errors

**Need more help?** The [AI Help Desk](https://chatgpt.com/g/g-68ff031d991081919e3da5b0b7ea683f-panek-video-program-help-desk) can diagnose dialog issues for your specific desktop environment.

---

## Technical Details

For users who want to know more:

**Video Specifications:**
- Resolution: 1920×1080 (Full HD)
- Format: MP4 (H.264 video, AAC audio)
- Frame rate: 30 fps
- Video quality: CRF 20 (high quality)
- Color space: BT.709 (standard HD)
- Pixel format: yuv420p (universal compatibility)

**Audio Specifications:**
- Codec: AAC
- Bitrate: 192 kbps
- Automatically matched to video length

**Processing:**
- Images are scaled to fit 1920×1080 preserving aspect ratio
- Black padding is added as needed to reach 16:9
- Fast start enabled for web streaming
- Optimized for YouTube, Vimeo, and social media

---

## Use Cases

Here are some ways people use Panek Video Program:

**Musicians & Artists:**
- Upload songs to YouTube with album artwork
- Create visual versions of audio-only releases
- Make simple music videos for streaming platforms

**Podcasters:**
- Convert podcast episodes to video for YouTube
- Add branding images to audio content
- Reach video platform audiences

**Content Creators:**
- Create simple visualizations for audio content
- Make countdown videos with static images
- Produce meditation/ambient content

**Educators:**
- Turn audio lessons into video format
- Add branding to educational audio
- Create accessible content for video platforms

**Business:**
- Audio presentations with logo/branding
- Product announcement videos
- Simple video ads from audio scripts

---

## Frequently Asked Questions

**Q: Where can I get help if I'm stuck?**
A: Try our [AI Help Desk](https://chatgpt.com/g/g-68ff031d991081919e3da5b0b7ea683f-panek-video-program-help-desk) first! It's trained on installation and debugging across all platforms and can provide instant, personalized help. You can also check GitHub Issues or the troubleshooting section in this manual.

**Q: Can I use this commercially?**
A: Yes! You own all the videos you create. Use them however you like commercially.

**Q: Can I redistribute or sell the program itself?**
A: No, the software cannot be redistributed or resold. See LICENSE.txt for details.

**Q: Does it work on Windows?**
A: Currently optimized for Linux and macOS. Windows support may come in the future.

**Q: Can I use video files instead of images?**
A: Not currently. The program is designed for static images only.

**Q: What if my image isn't 16:9?**
A: No problem! The program automatically adds black bars to make it fit perfectly.

**Q: Can I add text or effects?**
A: Not in this version. Panek Video Program keeps things simple – one image, one audio file.

**Q: How long does rendering take?**
A: Usually 10-30 seconds for a 3-4 minute song, depending on your computer speed.

**Q: Is there a file size limit?**
A: No strict limit, but very large files (multi-GB images or very long audio) may take longer to process.

**Q: Where can I report bugs or request features?**
A: Visit the GitHub repository: [https://github.com/Nickpanek/panek-video-program](https://github.com/Nickpanek/panek-video-program)

---

## Running from Source (Advanced)

If you want to run the program from Python source code:

```bash
# Install dependencies
   sudo apt install ffmpeg
   pip install PySide6 qdarktheme
   
   # Clone the repository
   git clone https://github.com/Nickpanek/panek-video-program.git
   cd panek-video-program
   
   # Run the program
   python3 panek_video_program.py
```

**Encountering errors?** The [AI Help Desk](https://chatgpt.com/g/g-68ff031d991081919e3da5b0b7ea683f-panek-video-program-help-desk) can help debug Python dependencies and environment issues specific to your system.

---

## Support & Contact

**Having issues?** Check the troubleshooting section above first.

**Need help?**
- **🤖 AI Help Desk:** [Panek Video Program Help Desk](https://chatgpt.com/g/g-68ff031d991081919e3da5b0b7ea683f-panek-video-program-help-desk) - Custom GPT trained on installation and debugging across all platforms
- **GitHub Issues:** [Report bugs or request features](https://github.com/Nickpanek/panek-video-program/issues)
- **Website:** [https://www.patternripple.com/panekvideo/](https://www.patternripple.com/panekvideo/)

**Want to support development?**
- [Buy Me a Coffee](https://buymeacoffee.com/prompternick)
- Visit [PatternRipple Lab](https://www.patternripple.com/lab) for more tools

---

## Quick Reference Card

**Supported Image Formats:** JPG, PNG, WEBP  
**Supported Audio Formats:** MP3, WAV  
**Output Format:** MP4 (1920×1080, H.264, AAC)  
**Required Software:** FFmpeg  
**🤖 Get Help:** [AI Help Desk](https://chatgpt.com/g/g-68ff031d991081919e3da5b0b7ea683f-panek-video-program-help-desk)

**Basic Workflow:**
1. Choose output folder (optional)
2. Enter title (optional)
3. Choose image
4. Choose audio
5. Click Render
6. Wait for completion
7. Find your video in the output folder

---

## License & Credits

**Panek Video Program**  
Copyright © 2025 PatternRipple Labs / Nick Panek  
All Rights Reserved.

You may use the software and create content with it (including commercial content), but you may not redistribute, modify, or resell the software itself.

For licensing inquiries: nick@patternripple.com

---

**Version:** 1.0  
**Last Updated:** October 2025  
**Manual Revision:** 1.0

---

*Thank you for using Panek Video Program! We hope it helps you create amazing content.*
