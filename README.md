**ROS 2 AI-Powered Smart Security Camera**

An intelligent, edge-computing security appliance built on ROS 2 Humble. It transforms a standard network camera stream into an asynchronous computer vision pipeline that tracks human presence, saves local video clips, and dispatches instant email alerts over secure SMTP.


**The Problem**

Continuous video surveillance on edge hardware faces three major bottlenecks:
1. **High CPU Waste:** Running heavy deep-learning object detection (like YOLO) on an empty room drains system resources.
2. **Network Bottlenecks:** Blocking the camera stream to process slow cloud tasks (like sending emails) drops critical frames.
3. **Storage Depletion:** 24/7 raw video logs quickly fill up local disk space.


**The Solution**

An edge-centric architecture that reduces idle CPU usage by ~70%. It uses a lightweight pixel-differencing motion detector as a gatekeeper to wake up the YOLOv8 layer only when movement is found, and utilizes background worker threads to keep the camera feed running smoothly at 30 FPS.


**Key Technical Features**

- **Two-Stage Vision Pipeline:** OpenCV motion detection acts as a low-overhead trigger for the heavier YOLOv8 human detection model.
- **Edge Inference Tracking:** Optimized YOLOv8 Nano model downscaled to $320 \times 320$ pixels for high-speed tracking inside an ARM64 Virtual Machine without a dedicated GPU.
- **Asynchronous Threading:** Python threading and queue modules decouple the live camera stream from slow cloud SMTP mail handshakes, preventing frame drops.
- **Local Clip Compilation:** Saves space by compressing verified threat events into 3-second `.mp4` clips using OpenCV's VideoWriter.


**Installation & Setup**

Ensure the following prerequisites are met on your Ubuntu environment:
- ROS 2 (Humble Hawksbill or newer)
- Python 3.10+
- OpenCV (`opencv-python`)
- Ultralytics (`ultralytics` for YOLOv8)

**Setup the Camera Source**
Ensure your mobile phone is broadcasting an MJPEG network stream via the DroidCam application on your local Wi-Fi subnet. Update the stream target URL in `human_tracker.py`:```python
self.stream_url = "http://YOUR_DROIDCAM_IP:4747/video"
