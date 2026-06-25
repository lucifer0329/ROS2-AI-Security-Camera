**ROS 2 AI-Powered Smart Security Camera**

An intelligent, edge-computing security appliance built on top of **ROS 2 (Humble/Iron)**. This system transforms a standard network camera stream into an asynchronous computer vision pipeline that tracks human presence, saves short video clips locally, and dispatches encrypted instant email alerts over secure SMTP.


**The Problem Statement**

Traditional continuous video surveillance systems suffer from three distinct engineering inefficiencies when deployed on edge compute hardware (such as localized smart home hubs or restricted virtual machines):
1. **High CPU Idle Waste:** Running continuous deep-learning object detection (like YOLO) across every frame of an empty room creates immense thermal and CPU overhead.
2. **Network/I-O Bottlenecks:** Blocking primary camera frame acquisition loops to handle slow cloud network tasks (like assembling and transmitting emails via SMTP) results in severe frame drops and laggy video playback.
3. **Storage Depletion:** Saving raw, continuous 24/7 video logs quickly consumes local disk partitions, rendering the security node unstable over time.

**The Solution**
This project introduces an edge-centric architecture that decouples video streaming from cloud alerts using multi-threaded worker queues, uses a low-overhead frame differencing mechanism to trigger the heavier deep learning vision layer only when physical motion is present, and optimizes data retention via targeted, compressed event clips.


**Key Features**

**Two-Stage Multi-Filtering Pipeline:** Employs a lightweight pixel-differencing motion detection thresholding algorithm to act as a system gatekeeper. The computationally expensive deep-learning engine is kept asleep until structural movement is verified, cutting idle CPU load down dramatically.

**YOLOv8 Object Detection Tracking:** Integrates a state-of-the-art neural network engine optimized to run inference at a downscaled resolution of $320 \times 320$ pixels inside an ARM64 Virtual Machine environment to achieve rapid classification latency without relying on a dedicated GPU.

**Asynchronous Multi-Threading Framework:** Implements a Python concurrency model that offloads network delays and slow SMTP mail server handshakes onto an independent background worker thread. This keeps the primary camera streaming loop unblocked, preserving a rock-solid **30 FPS capture rate**.

**Edge Clip Compilation:** Compresses verified physical threat captures into localized `.mp4` video segments using OpenCV's `VideoWriter` interface, applying optimized frame limits to maximize long-term storage partition efficiency.
