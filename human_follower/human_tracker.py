#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import cv2
import os
import smtplib
import threading  # <--- Optimization 1: Imported for background threads
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from ultralytics import YOLO

class SmartSecurityNode(Node):
    def __init__(self):
        super().__init__('smart_security_node')
        
        # 1. Create directory to store security clips
        self.save_dir = os.path.expanduser('~/Desktop/security_clips')
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
            
        # 2. Network & Stream Configuration (Your DroidCam IP)
        self.stream_url = "http://172.A.B.C:YYYY/video"
        
        # 3. EMAIL CREDENTIAL CONFIGURATION
        self.SENDER_EMAIL = "your_email@gmail.com"
        self.SENDER_PASSWORD = "your_16_character_app_password"" 
        self.RECEIVER_EMAIL = "receiver_email@gmail.com"
        
        # 4. Initialize AI Model (YOLOv8 Nano)
        self.get_logger().info("Loading YOLO AI Model into memory...")
        self.model = YOLO('yolov8n.pt') 
        
        # 5. Video Capture & Motion Tracking Variables
        self.cap = cv2.VideoCapture(self.stream_url)
        self.prev_frame = None
        
        # Video recording variables
        self.is_recording = False
        self.video_writer = None
        self.frames_to_record = 90  # 3 seconds at 30 FPS
        self.recorded_frames_count = 0
        self.current_clip_path = ""
        
        # Cooldown timer to prevent flooding your inbox
        self.last_alert_time = 0
        self.alert_cooldown = 15.0  
        
        # Main processing loop (30 FPS)
        self.timer = self.create_timer(1.0 / 30.0, self.timer_callback)
        self.get_logger().info("Optimized Multi-Threaded AI Security System Ready!")

    def timer_callback(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        # If system is actively recording a confirmed human, save the frame immediately
        if self.is_recording:
            self.video_writer.write(frame)
            self.recorded_frames_count += 1
            
            # Draw visual recording indicator overlay
            cv2.circle(frame, (30, 30), 10, (0, 0, 255), -1)
            cv2.putText(frame, "REC", (50, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            if self.recorded_frames_count >= self.frames_to_record:
                self.stop_recording_and_send()
                
            cv2.imshow("AI Motion Security Monitor", frame)
            cv2.waitKey(1)
            return

        # --- STANDARD MOTION DETECTION PROCESSING ---
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if self.prev_frame is None:
            self.prev_frame = gray
            return

        frame_delta = cv2.absdiff(self.prev_frame, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        motion_detected = any(cv2.contourArea(c) > 1200 for c in contours)
        self.prev_frame = gray

        # If motion is detected, use AI to verify if it is a Human
        if motion_detected:
            current_time = self.get_clock().now().nanoseconds / 1e9
            if (current_time - self.last_alert_time) > self.alert_cooldown:
                
                # -------------------------------------------------------------
                # OPTIMIZATION 2: AI Frame Downscaling
                # Resize the image matrix down to 320x320 before giving it to YOLO.
                # This drops CPU cycles inside your VM exponentially!
                # -------------------------------------------------------------
                small_frame = cv2.resize(frame, (320, 320))
                results = self.model(small_frame, verbose=False)[0]
                
                human_found = False
                for box in results.boxes:
                    class_id = int(box.cls[0])
                    label = self.model.names[class_id]
                    
                    if label == 'person':
                        human_found = True
                        break
                
                if human_found:
                    self.get_logger().info("🚨 AI VERIFIED: Human detected! Starting 3-second recording...")
                    self.last_alert_time = current_time
                    self.start_recording(frame)

        cv2.imshow("AI Motion Security Monitor", frame)
        cv2.waitKey(1)

    def start_recording(self, initial_frame):
        self.is_recording = True
        self.recorded_frames_count = 0
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_clip_path = os.path.join(self.save_dir, f"security_{timestamp}.mp4")
        
        h, w, _ = initial_frame.shape
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.video_writer = cv2.VideoWriter(self.current_clip_path, fourcc, 30.0, (w, h))
        self.video_writer.write(initial_frame)

    def stop_recording_and_send(self):
        self.is_recording = False
        self.video_writer.release()
        self.get_logger().info("Video file compiled locally. Spawning network thread...")
        
        # -------------------------------------------------------------
        # OPTIMIZATION 1: Background Multi-Threading Execution
        # We wrap the slow email upload function inside a background worker thread. 
        # This keeps the main camera loop running smoothly at 30 FPS!
        # -------------------------------------------------------------
        email_thread = threading.Thread(
            target=self.send_email_alert, 
            args=(self.current_clip_path,)
        )
        email_thread.daemon = True  # Allows thread to close automatically if node exits
        email_thread.start()

    def send_email_alert(self, video_file_path):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.SENDER_EMAIL
            msg['To'] = self.RECEIVER_EMAIL
            msg['Subject'] = "⚠️ SECURITY ALERT: Intruder Detected by ROS 2 AI Node"
            
            body = f"Alert triggered on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. A 3-second video clip is attached."
            msg.attach(MIMEText(body, 'plain'))
            
            with open(video_file_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(video_file_path)}")
                msg.attach(part)
                
            # Connect to Google Mail Server over safe TLS channel
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.SENDER_EMAIL, self.SENDER_PASSWORD)
            server.sendmail(self.SENDER_EMAIL, self.RECEIVER_EMAIL, msg.as_string())
            server.quit()
            
            self.get_logger().info("📬 Background Thread: Email dispatch completely successful!")
        except Exception as e:
            self.get_logger().error(f"Background Thread Error: Failed to transmit email: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = SmartSecurityNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node.video_writer:
            node.video_writer.release()
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
