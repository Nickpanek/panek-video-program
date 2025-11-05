#!/bin/bash
# Build script for creating AppImage
set -e

VERSION=${1:-2.0.0}
APPDIR="AppDir"

echo "Building Panek Video Program AppImage v${VERSION}..."

# Clean previous build
rm -rf "${APPDIR}"
rm -f *.AppImage

# Create AppDir structure
mkdir -p "${APPDIR}/usr/bin"
mkdir -p "${APPDIR}/usr/share/applications"
mkdir -p "${APPDIR}/usr/share/icons/hicolor/256x256/apps"
mkdir -p "${APPDIR}/usr/lib/python3/dist-packages"

# Copy application files
cp panek_video_program.py "${APPDIR}/usr/bin/panek-video-program"
chmod +x "${APPDIR}/usr/bin/panek-video-program"

# Copy desktop file and icon
cp packaging/linux/appdir/panek-video.desktop "${APPDIR}/"
cp packaging/linux/appdir/panek-video.desktop "${APPDIR}/usr/share/applications/"
cp packaging/linux/icon.png "${APPDIR}/panek-video.png"
cp packaging/linux/icon.png "${APPDIR}/usr/share/icons/hicolor/256x256/apps/panek-video.png"

# Copy AppRun
cp packaging/linux/appdir/AppRun "${APPDIR}/"
chmod +x "${APPDIR}/AppRun"

# Install Python dependencies into AppDir
pip install --target="${APPDIR}/usr/lib/python3/dist-packages" PySide6 pyqtdarktheme

# Download appimagetool if not present
if [ ! -f appimagetool-x86_64.AppImage ]; then
    echo "Downloading appimagetool..."
    wget -q https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x appimagetool-x86_64.AppImage
fi

# Build AppImage
ARCH=x86_64 ./appimagetool-x86_64.AppImage "${APPDIR}" "PanekVideoProgram-${VERSION}-x86_64.AppImage"

echo "AppImage created: PanekVideoProgram-${VERSION}-x86_64.AppImage"
