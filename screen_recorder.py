import cv2
import numpy as np
import win32gui
import win32ui
import win32con
import win32api
import time
import os
from datetime import datetime
import sys

def get_actual_screen_size():
    width = win32api.GetSystemMetrics(0)
    height = win32api.GetSystemMetrics(1)
    return width, height

def screen_capture(output_folder, timestamp):

    screen_width, screen_height = get_actual_screen_size()
    print(f"Detected Screen resolution: {screen_width}x{screen_height}")

    fps = 10.0
    segment_duration = 20 * 60  # 20 minutes in seconds

    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.join(output_folder, f"screen_record_{timestamp}.avi")
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_file, fourcc, fps, (screen_width, screen_height))

    hdesktop = win32gui.GetDesktopWindow()
    desktop_dc = win32gui.GetWindowDC(hdesktop)
    dc_obj = win32ui.CreateDCFromHandle(desktop_dc)
    cdc = dc_obj.CreateCompatibleDC()
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(dc_obj, screen_width, screen_height)
    cdc.SelectObject(bmp)

    total_frames = int(fps * segment_duration)
    frame_count = 0

    print(f"Recording started: {output_file}")

    while frame_count < total_frames:
        loop_start = time.time()

        cdc.BitBlt((0, 0), (screen_width, screen_height), dc_obj, (0, 0), win32con.SRCCOPY)
        bmp_str = bmp.GetBitmapBits(True)
        img = np.frombuffer(bmp_str, dtype='uint8')
        # Ensure the shape matches the bitmap size (height, width, 4)
        try:
            img = img.reshape((screen_height, screen_width, 4))
        except Exception as e:
            print(f"Error reshaping image: {e}, buffer size: {img.size}, expected: {screen_height*screen_width*4}")
            continue

        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        out.write(img)
        frame_count += 1

        elapsed = time.time() - loop_start
        delay = max(0, (1 / fps) - elapsed)
        time.sleep(delay)

    out.release()
    win32gui.DeleteObject(bmp.GetHandle())
    cdc.DeleteDC()
    dc_obj.DeleteDC()
    win32gui.ReleaseDC(hdesktop, desktop_dc)

    print(f"Saved recording: {output_file}")

if __name__ == "__main__":
    try:
        if len(sys.argv) > 2:
            output_folder = sys.argv[1]
            timestamp = sys.argv[2]
            screen_capture(output_folder, timestamp)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screen_capture("screen_recordings", timestamp)
    except KeyboardInterrupt:
        print("Screen recording stopped by user")