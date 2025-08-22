import cv2
import numpy as np
import threading
import time
from typing import Optional, Callable, Generator
import yaml

class WebcamProcessor:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.camera_index = cfg.get("camera_index", 0)
        self.resolution = cfg.get("resolution", (640, 480))
        self.fps = cfg.get("fps", 30)
        self.is_running = False
        self.cap = None
        self.current_frame = None
        self.frame_lock = threading.Lock()
        
        # Initialize camera
        self._init_camera()
    
    def _init_camera(self):
        """Initialize the webcam capture"""
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            
            if not self.cap.isOpened():
                raise Exception(f"Could not open camera at index {self.camera_index}")
                
            print(f"Webcam initialized: {self.resolution[0]}x{self.resolution[1]} @ {self.fps}fps")
            
        except Exception as e:
            print(f"Failed to initialize webcam: {e}")
            self.cap = None
    
    def start_stream(self):
        """Start the webcam stream in a separate thread"""
        if not self.cap or self.is_running:
            return
            
        self.is_running = True
        self.stream_thread = threading.Thread(target=self._stream_loop, daemon=True)
        self.stream_thread.start()
    
    def stop_stream(self):
        """Stop the webcam stream"""
        self.is_running = False
        if self.stream_thread:
            self.stream_thread.join(timeout=1.0)
    
    def _stream_loop(self):
        """Main streaming loop"""
        while self.is_running and self.cap:
            ret, frame = self.cap.read()
            if ret:
                with self.frame_lock:
                    self.current_frame = frame.copy()
            else:
                print("Failed to read frame from webcam")
                break
            time.sleep(1.0 / self.fps)
    
    def get_current_frame(self) -> Optional[np.ndarray]:
        """Get the most recent frame"""
        with self.frame_lock:
            return self.current_frame.copy() if self.current_frame is not None else None
    
    def capture_photo(self) -> Optional[np.ndarray]:
        """Capture a single photo"""
        if not self.cap:
            return None
            
        ret, frame = self.cap.read()
        if ret:
            return frame
        return None
    
    def detect_faces(self, frame: np.ndarray) -> list:
        """Detect faces in the frame using OpenCV"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        return faces
    
    def detect_objects(self, frame: np.ndarray) -> list:
        """Basic object detection using color and contour analysis"""
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Example: detect red objects
        lower_red = np.array([0, 50, 50])
        upper_red = np.array([10, 255, 255])
        mask = cv2.inRange(hsv, lower_red, upper_red)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        objects = []
        for contour in contours:
            if cv2.contourArea(contour) > 500:  # Filter small objects
                x, y, w, h = cv2.boundingRect(contour)
                objects.append({
                    'type': 'red_object',
                    'bbox': (x, y, w, h),
                    'center': (x + w//2, y + h//2)
                })
        
        return objects
    
    def analyze_scene(self, frame: np.ndarray) -> dict:
        """Analyze the scene and return structured information"""
        analysis = {
            'faces_detected': 0,
            'objects_detected': [],
            'brightness': 0,
            'dominant_colors': [],
            'motion_detected': False
        }
        
        # Face detection
        faces = self.detect_faces(frame)
        analysis['faces_detected'] = len(faces)
        
        # Object detection
        objects = self.detect_objects(frame)
        analysis['objects_detected'] = objects
        
        # Brightness analysis
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        analysis['brightness'] = np.mean(gray)
        
        # Dominant colors (simplified)
        pixels = frame.reshape(-1, 3)
        from sklearn.cluster import KMeans
        try:
            kmeans = KMeans(n_clusters=3, random_state=42)
            kmeans.fit(pixels)
            colors = kmeans.cluster_centers_.astype(int)
            analysis['dominant_colors'] = colors.tolist()
        except:
            pass
        
        return analysis
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.stop_stream()
        if self.cap:
            self.cap.release()

class WebcamInput:
    """High-level webcam interface for Jarvis"""
    
    def __init__(self, cfg: dict):
        self.processor = WebcamProcessor(cfg)
        self.is_active = False
    
    def start(self):
        """Start webcam processing"""
        self.processor.start_stream()
        self.is_active = True
        print("Webcam input started")
    
    def stop(self):
        """Stop webcam processing"""
        self.processor.stop_stream()
        self.is_active = False
        print("Webcam input stopped")
    
    def get_scene_description(self) -> str:
        """Get a natural language description of the current scene"""
        frame = self.processor.get_current_frame()
        if frame is None:
            return "No webcam feed available"
        
        analysis = self.processor.analyze_scene(frame)
        
        description = f"Webcam scene: "
        
        if analysis['faces_detected'] > 0:
            description += f"{analysis['faces_detected']} face(s) detected. "
        
        if analysis['objects_detected']:
            description += f"{len(analysis['objects_detected'])} colored objects visible. "
        
        brightness = analysis['brightness']
        if brightness < 50:
            description += "Scene is dark. "
        elif brightness > 200:
            description += "Scene is bright. "
        else:
            description += "Scene has normal lighting. "
        
        return description
    
    def capture_and_analyze(self) -> dict:
        """Capture a frame and return detailed analysis"""
        frame = self.processor.capture_photo()
        if frame is None:
            return {"error": "Failed to capture frame"}
        
        analysis = self.processor.analyze_scene(frame)
        analysis['timestamp'] = time.time()
        analysis['frame_shape'] = frame.shape
        
        return analysis
