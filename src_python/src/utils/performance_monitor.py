"""
HCI Gesture Service Module

This module provides the HCIGestureService class that wraps the gesture control system
for integration with GNOME Shell extension and other services.
"""

import os
import sys
import time
import cv2
import threading
import json
from pathlib import Path
from typing import Dict, Any, Optional, Callable

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from src.main import GestureControlSystem
    from src.core.gesture_detector import GestureDetector
    from src.core.action_handler import ActionHandler
except ImportError as e:
    print(f"Warning: Could not import core modules: {e}")
    GestureControlSystem = None
    GestureDetector = None
    ActionHandler = None


class PerformanceMonitor:
    """
    Performance monitoring for gesture detection system
    """
    
    def __init__(self):
        self.frame_count = 0
        self.start_time = time.time()
        self.processing_times = []
        self.fps = 0.0
    
    def process_frame(self):
        """Process a frame for performance tracking"""
        self.frame_count += 1
        current_time = time.time()
        
        # Calculate FPS
        elapsed = current_time - self.start_time
        if elapsed > 0:
            self.fps = self.frame_count / elapsed
    
    def get_stats(self):
        """Get performance statistics"""
        return {
            'frame_count': self.frame_count,
            'fps': self.fps,
            'avg_processing_time': sum(self.processing_times) / len(self.processing_times) if self.processing_times else 0.0
        }
    
    def reset(self):
        """Reset performance statistics"""
        self.frame_count = 0
        self.start_time = time.time()
        self.processing_times = []
        self.fps = 0.0


class HCIGestureService:
    """
    HCI Gesture Service for GNOME Shell integration

    This service manages the gesture control system, camera input,
    and provides status information for the extension.
    """

    def __init__(self, extension_dir: str):
        """
        Initialize the HCI Gesture Service

        Args:
            extension_dir: Path to the GNOME Shell extension directory
        """
        self.extension_dir = Path(extension_dir)
        self.running = False
        self.camera = None
        self.gesture_system = None
        self.performance_monitor = None

        # Status tracking
        self.status = {
            'active': False,
            'calibrated': False,
            'stats': {
                'frames_processed': 0,
                'gestures_detected': 0,
                'actions_executed': 0,
                'errors': 0
            },
            'performance': {
                'fps': 0.0,
                'avg_processing_time': 0.0
            }
        }

        # Threading
        self.processing_thread = None
        self.stop_event = threading.Event()

        # Callbacks
        self.on_status_change: Optional[Callable] = None
        self.on_gesture_detected: Optional[Callable] = None

        # Initialize components
        self._init_components()

    def _init_components(self):
        """Initialize service components"""
        try:
            # Create gesture control system
            config_path = self.extension_dir / "config" / "gesture_map.json"
            self.gesture_system = GestureControlSystem(str(config_path))

            # Create performance monitor if available
            if PerformanceMonitor:
                self.performance_monitor = PerformanceMonitor()
            else:
                print("Performance monitor not available")

            print("✅ Service components initialized")

        except Exception as e:
            print(f"❌ Failed to initialize service components: {e}")
            self.status['stats']['errors'] += 1

    def _init_camera(self):
        """Initialize camera"""
        try:
            camera_index = getattr(self.gesture_system, 'camera_index', 0) if self.gesture_system else 0
            self.camera = cv2.VideoCapture(camera_index)

            if not self.camera.isOpened():
                raise RuntimeError(f"Could not open camera {camera_index}")

            print(f"✅ Camera initialized (index: {camera_index})")

        except Exception as e:
            print(f"❌ Failed to initialize camera: {e}")
            self.status['stats']['errors'] += 1
            raise

    def start(self) -> bool:
        """
        Start the gesture service

        Returns:
            bool: True if started successfully
        """
        if self.running:
            return True

        try:
            # Initialize camera if not already done
            if self.camera is None:
                self._init_camera()

            # Start processing thread
            self.stop_event.clear()
            self.processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
            self.processing_thread.start()

            self.running = True
            self.status['active'] = True

            print("✅ HCI Gesture Service started")
            return True

        except Exception as e:
            print(f"❌ Failed to start service: {e}")
            self.status['stats']['errors'] += 1
            return False

    def stop(self):
        """Stop the gesture service"""
        if not self.running:
            return

        self.stop_event.set()
        self.running = False
        self.status['active'] = False

        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=2.0)

        if self.camera:
            self.camera.release()
            self.camera = None

        print("🛑 HCI Gesture Service stopped")

    def _processing_loop(self):
        """Main processing loop"""
        import mediapipe as mp

        mp_hands = mp.solutions.hands
        mp_drawing = mp.solutions.drawing_utils

        confidence_level = getattr(self.gesture_system, 'confidence_minimum', 0.7) if self.gesture_system else 0.7

        with mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=confidence_level,
            min_tracking_confidence=confidence_level
        ) as hands:

            frame_count = 0
            start_time = time.time()

            while not self.stop_event.is_set() and self.camera and self.camera.isOpened():
                try:
                    ok, frame = self.camera.read()
                    if not ok:
                        break

                    frame_count += 1
                    self.status['stats']['frames_processed'] = frame_count

                    # Flip frame
                    frame = cv2.flip(frame, 1)
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    # Process with MediaPipe
                    results = hands.process(rgb)

                    if results.multi_hand_landmarks:
                        for landmarks in results.multi_hand_landmarks:
                            # Process frame with gesture system
                            if self.gesture_system:
                                gesture_info = self.gesture_system.process_frame(frame, landmarks)

                                # Update status
                                if gesture_info.get('action'):
                                    self.status['stats']['gestures_detected'] += 1

                                # Update calibration status
                                if hasattr(self.gesture_system, 'detector'):
                                    cal_status = self.gesture_system.detector.get_calibration_status()
                                    self.status['calibrated'] = cal_status.get('is_calibrated', False)

                                # Call gesture callback
                                if self.on_gesture_detected and gesture_info.get('action'):
                                    self.on_gesture_detected(gesture_info)

                    # Update performance stats
                    if frame_count % 30 == 0:  # Every 30 frames
                        elapsed = time.time() - start_time
                        self.status['performance']['fps'] = frame_count / elapsed

                        if self.performance_monitor:
                            perf_stats = self.performance_monitor.get_stats()
                            self.status['performance']['avg_processing_time'] = perf_stats.get('avg_processing_time', 0.0)

                    # Call status change callback
                    if self.on_status_change:
                        self.on_status_change(self.status)

                except Exception as e:
                    print(f"Error in processing loop: {e}")
                    self.status['stats']['errors'] += 1
                    time.sleep(0.1)  # Brief pause on error

    def get_status(self) -> Dict[str, Any]:
        """
        Get current service status

        Returns:
            Dict containing status information
        """
        # Update additional stats from gesture system
        if self.gesture_system:
            session_stats = self.gesture_system.get_session_stats()
            self.status['stats'].update({
                'frames_processed': session_stats.get('frames_processed', 0),
                'gestures_detected': session_stats.get('gestures_detected', 0),
                'actions_executed': session_stats.get('successful_actions', 0)
            })

        return self.status.copy()

    def set_setting(self, key: str, value: Any):
        """
        Set a service setting

        Args:
            key: Setting key
            value: Setting value
        """
        if self.gesture_system and hasattr(self.gesture_system, 'settings'):
            self.gesture_system.settings[key] = value

            # Apply specific settings
            if key == 'safe_mode' and hasattr(self.gesture_system, 'action_handler'):
                self.gesture_system.action_handler.enable_safe_mode(value)
            elif key == 'tutorial_mode':
                self.gesture_system.tutorial_mode = value

    def get_setting(self, key: str) -> Any:
        """
        Get a service setting

        Args:
            key: Setting key

        Returns:
            Setting value
        """
        if self.gesture_system and hasattr(self.gesture_system, 'settings'):
            return self.gesture_system.settings.get(key)
        return None

    def calibrate(self):
        """Trigger hand calibration"""
        if self.gesture_system:
            self.gesture_system.start_calibration()

    def reset_calibration(self):
        """Reset calibration"""
        if self.gesture_system and hasattr(self.gesture_system, 'detector'):
            self.gesture_system.detector.reset_calibration()
            self.status['calibrated'] = False

    def __del__(self):
        """Cleanup on destruction"""
        self.stop()
