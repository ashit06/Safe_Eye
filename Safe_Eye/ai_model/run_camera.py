from camera_detection import camera_service

if __name__ == "__main__":
    print("🔁 Starting detection manually from run_camera.py")
    camera_service.start_camera_detection(camera_source="test1.png", detection_interval=1.0)
