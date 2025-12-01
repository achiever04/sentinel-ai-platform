#!/bin/bash

echo "========================================="
echo "🎥 Camera Permission Fix Script"
echo "========================================="

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "❌ This script is for Linux only"
    exit 1
fi

# List available cameras
echo ""
echo "📹 Checking available video devices..."
if ls /dev/video* 1> /dev/null 2>&1; then
    ls -l /dev/video*
else
    echo "❌ No video devices found!"
    echo "   Is your webcam connected?"
    exit 1
fi

# Add user to video group
echo ""
echo "👤 Adding user '$USER' to 'video' group..."
sudo usermod -a -G video $USER

# Set permissions on all video devices
echo ""
echo "🔓 Setting permissions on video devices..."
for device in /dev/video*; do
    if [ -e "$device" ]; then
        sudo chmod 666 "$device"
        echo "   ✅ $device permissions set"
    fi
done

# Test camera access
echo ""
echo "🧪 Testing camera access..."
python3 << 'EOF'
import cv2
import sys

print("\nTesting cameras...")
found_working = False

for i in range(5):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret and frame is not None:
            print(f"✅ Camera {i} is WORKING (Resolution: {frame.shape[1]}x{frame.shape[0]})")
            found_working = True
        else:
            print(f"⚠️  Camera {i} opens but can't read frames")
        cap.release()

if not found_working:
    print("\n❌ No working cameras found!")
    print("   Possible issues:")
    print("   - Camera is being used by another app (Zoom, Chrome, etc)")
    print("   - Driver issues")
    print("   - USB connection problem")
    sys.exit(1)
else:
    print("\n✅ At least one camera is working!")
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "✅ Camera setup complete!"
    echo "========================================="
    echo ""
    echo "⚠️  IMPORTANT NEXT STEPS:"
    echo "1. LOGOUT and LOGIN again (for group changes)"
    echo "2. Close all apps using the camera (Chrome, Zoom, etc)"
    echo "3. Run: python3 update_cameras.py"
    echo "4. Then restart the backend"
    echo ""
else
    echo ""
    echo "❌ Camera test failed. Please check the issues above."
    echo ""
fi