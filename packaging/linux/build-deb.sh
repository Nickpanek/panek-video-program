#!/bin/bash
# Build script for creating DEB package
set -e

VERSION=${1:-2.0.0}
PACKAGE_NAME="panek-video-program_${VERSION}_all"
BUILD_DIR="deb-build/${PACKAGE_NAME}"

echo "Building Panek Video Program DEB package v${VERSION}..."

# Clean previous build
rm -rf deb-build
rm -f *.deb

# Create package directory structure
mkdir -p "${BUILD_DIR}/DEBIAN"
mkdir -p "${BUILD_DIR}/usr/bin"
mkdir -p "${BUILD_DIR}/usr/share/applications"
mkdir -p "${BUILD_DIR}/usr/share/icons/hicolor/256x256/apps"
mkdir -p "${BUILD_DIR}/usr/share/doc/panek-video-program"

# Copy application files
cp panek_video_program.py "${BUILD_DIR}/usr/bin/panek-video-program"
chmod +x "${BUILD_DIR}/usr/bin/panek-video-program"

# Copy desktop file and icon
cp packaging/linux/panek-video.desktop "${BUILD_DIR}/usr/share/applications/"
cp packaging/linux/icon.png "${BUILD_DIR}/usr/share/icons/hicolor/256x256/apps/panek-video.png"

# Copy documentation
cp README.md "${BUILD_DIR}/usr/share/doc/panek-video-program/"
cp MANUAL.md "${BUILD_DIR}/usr/share/doc/panek-video-program/"
cp LICENSE.txt "${BUILD_DIR}/usr/share/doc/panek-video-program/"
cp CHANGELOG.md "${BUILD_DIR}/usr/share/doc/panek-video-program/"

# Copy and update DEBIAN control files
cp packaging/linux/deb/DEBIAN/control "${BUILD_DIR}/DEBIAN/"
cp packaging/linux/deb/DEBIAN/postinst "${BUILD_DIR}/DEBIAN/"
cp packaging/linux/deb/DEBIAN/prerm "${BUILD_DIR}/DEBIAN/"

# Replace version placeholder
sed -i "s/VERSION_PLACEHOLDER/${VERSION}/g" "${BUILD_DIR}/DEBIAN/control"

# Set permissions
chmod 755 "${BUILD_DIR}/DEBIAN/postinst"
chmod 755 "${BUILD_DIR}/DEBIAN/prerm"
chmod 644 "${BUILD_DIR}/DEBIAN/control"

# Build the package
dpkg-deb --build --root-owner-group "${BUILD_DIR}"

# Move to root directory
mv "deb-build/${PACKAGE_NAME}.deb" "./"

echo "DEB package created: ${PACKAGE_NAME}.deb"
