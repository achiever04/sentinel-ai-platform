"""
Camera & WebSocket Diagnostic Tool
Run this to test camera capture and frame processing
"""

import cv2
import numpy as np
import json
from backend.processors.video_ingestor import VideoIngestor
from backend.processors.frame_processor import FrameProcessor

print("=" * 60)
print("CAMERA & FRAME PROCESSING DIAGNOSTIC TEST")
print("=" * 60)

# Test 1: Video Capture
print("\n[TEST 1] Testing Camera Capture...")
ingestor = VideoIngestor("0", "webcam")
if ingestor.start():
    print("✅ Camera opened successfully")
    
    success, frame = ingestor.read_frame()
    if success and frame is not None:
        print(f"✅ Frame captured: shape={frame.shape}, dtype={frame.dtype}")
    else:
        print("❌ Failed to read frame")
    
    ingestor.stop()
else:
    print("❌ Failed to open camera")

# Test 2: Synthetic Frame
print("\n[TEST 2] Testing Synthetic Frame Generation...")
synth_ingestor = VideoIngestor("synthetic", "synthetic")
synth_ingestor.start()
success, frame = synth_ingestor.read_frame()
if success:
    print(f"✅ Synthetic frame generated: shape={frame.shape}")
else:
    print("❌ Failed to generate synthetic frame")
synth_ingestor.stop()

# Test 3: Frame Processing
print("\n[TEST 3] Testing Frame Processor...")
processor = FrameProcessor()
test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

try:
    results = processor.process_frame(test_frame, camera_id=1, frame_count=0)
    print(f"✅ Frame processed successfully")
    print(f"   Detections: {results.get('detections', [])}")
    
    # Check for NumPy types
    print("\n[TEST 4] Checking for NumPy Types...")
    def check_numpy_types(obj, path=""):
        issues = []
        if isinstance(obj, dict):
            for key, value in obj.items():
                issues.extend(check_numpy_types(value, f"{path}.{key}"))
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                issues.extend(check_numpy_types(item, f"{path}[{i}]"))
        elif isinstance(obj, (np.bool_, np.integer, np.floating, np.ndarray)):
            issues.append(f"{path}: {type(obj).__name__}")
        return issues
    
    numpy_issues = check_numpy_types(results, "results")
    if numpy_issues:
        print("❌ Found NumPy types that will cause JSON errors:")
        for issue in numpy_issues[:10]:  # Show first 10
            print(f"   - {issue}")
    else:
        print("✅ No NumPy types found - JSON serialization should work")
        
except Exception as e:
    print(f"❌ Frame processing failed: {e}")
    import traceback
    traceback.print_exc()

# Test 5: JSON Serialization
print("\n[TEST 5] Testing JSON Serialization...")
test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
results = processor.process_frame(test_frame, camera_id=1, frame_count=0)
detections = results.get('detections', [])

try:
    # Try without conversion
    json_str = json.dumps({
        'test': 'data',
        'detections': detections[:5]
    })
    print("✅ JSON serialization works WITHOUT conversion")
except TypeError as e:
    print(f"❌ JSON serialization FAILS without conversion: {e}")
    
    # Try with conversion
    from backend.api.stream import convert_numpy_types
    safe_detections = convert_numpy_types(detections[:5])
    try:
        json_str = json.dumps({
            'test': 'data',
            'detections': safe_detections
        })
        print("✅ JSON serialization works WITH conversion")
    except Exception as e2:
        print(f"❌ JSON serialization STILL fails: {e2}")

# Test 6: JPEG Encoding
print("\n[TEST 6] Testing JPEG Encoding...")
test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
ret, buffer = cv2.imencode('.jpg', test_frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
if ret:
    print(f"✅ JPEG encoding works: buffer size={len(buffer)} bytes")
    import base64
    b64 = base64.b64encode(buffer).decode('utf-8')
    print(f"✅ Base64 encoding works: length={len(b64)}")
else:
    print("❌ JPEG encoding failed")

print("\n" + "=" * 60)
print("DIAGNOSTIC TEST COMPLETE")
print("=" * 60)
