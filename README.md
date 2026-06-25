ROS 2 AI-Powered Smart Security Camera

An intelligent, edge-computing security appliance built on top of **ROS 2**. This system transforms a standard network camera stream into an asynchronous computer vision pipeline that tracks human presence, saves short video clips locally, and dispatches encrypted instant email alerts over secure SMTP.


**Key Features**

**Two-Stage Multi-Filtering Pipeline:** Uses lightweight pixel-differencing motion detection to wake up the system, drastically minimizing continuous CPU idle overhead.

**YOLOv8 Object Detection Tracking:** Integrates a state-of-the-art neural network engine optimized to run inference.

**Asynchronous Multi-Threading Framework:** Offloads network blockages and slow SMTP transmissions to a secondary worker thread, ensuring the primary camera streaming worker maintains a rock-solid **30 FPS frame rate**

**Edge Clip Compilation:** Compresses verified physical threat captures into local `.mp4` video segments to maximize disk space efficiency.

**System Dependencies**

Ensure the following prerequisites are met on your Ubuntu environment:

**ROS 2** (Humble Hawksbill or newer)
**Python 3.10+**
**OpenCV** (`opencv-python`)
**Ultralytics** (`ultralytics` for YOLOv8)


**How to Run the Project**

**1. Setup the Camera Source**
Ensure your mobile phone is broadcasting an MJPEG network stream via the DroidCam application on your local Wi-Fi subnet. Update the stream target URL in `human_tracker.py`:```python

self.stream_url = "http://<YOUR_DROIDCAM_IP>:4747/video"
