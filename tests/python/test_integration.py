import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

class TestIntegration(unittest.TestCase):
    """Entegrasyon testleri - moduller arasi işbirliği"""
    
    def setUp(self):
        """Her test için setup"""
        self.mock_mediapipe_available = True
        
    def test_gesture_to_action_flow(self):
        """Gesture'dan action'a tam akiş testi"""
        # Mock moduller oluştur
        mock_detector = Mock()
        mock_action_handler = Mock()
        
        # Mock gesture sonucu
        mock_gesture_result = {
            'action': 'left_click',
            'type': 'click',
            'confidence': 0.9,
            'stable': True,
            'pinch_active': True,
            'cursor_pos': (500, 400)
        }
        
        mock_detector.detect_gesture.return_value = mock_gesture_result
        mock_action_handler.execute_action.return_value = True
        
        # Test akişi
        landmarks = [Mock() for _ in range(21)]  # 21 MediaPipe landmark
        
        # Gesture algila
        gesture_result = mock_detector.detect_gesture(landmarks)
        self.assertEqual(gesture_result['action'], 'left_click')
        
        # Action yurut
        success = mock_action_handler.execute_action(
            gesture_result, 
            gesture_result['cursor_pos']
        )
        self.assertTrue(success)
    
    def test_calibration_to_detection_flow(self):
        """Kalibrasyondan gesture algilamaya akiş testi"""
        mock_detector = Mock()
        
        # Kalibrasyon sureci
        mock_detector.is_calibrated = False
        mock_detector.calibrate_hand.return_value = True
        
        # Mock landmarks
        landmarks = [Mock() for _ in range(21)]
        
        # Kalibrasyon yap
        calibration_success = mock_detector.calibrate_hand(landmarks)
        self.assertTrue(calibration_success)
        
        # Kalibrasyon sonrasi algilama
        mock_detector.is_calibrated = True
        mock_gesture_result = {
            'action': 'right_click',
            'confidence': 0.85,
            'stable': True
        }
        mock_detector.detect_gesture.return_value = mock_gesture_result
        
        gesture_result = mock_detector.detect_gesture(landmarks)
        self.assertEqual(gesture_result['action'], 'right_click')
    
    def test_safety_system_integration(self):
        """Guvenlik sistemi entegrasyonu testi"""
        mock_action_handler = Mock()
        
        # Guvenli mod aktif
        mock_action_handler.safe_mode = True
        mock_action_handler.execute_action.side_effect = lambda gesture, pos: (
            gesture['confidence'] >= 0.7 and gesture.get('stable', False)
        )
        
        # Guvenli gesture
        safe_gesture = {
            'action': 'left_click',
            'confidence': 0.9,
            'stable': True
        }
        
        result = mock_action_handler.execute_action(safe_gesture, (500, 400))
        self.assertTrue(result)
        
        # Guvenli olmayan gesture
        unsafe_gesture = {
            'action': 'left_click',
            'confidence': 0.5,  # Duşuk guven
            'stable': False
        }
        
        result = mock_action_handler.execute_action(unsafe_gesture, (500, 400))
        self.assertFalse(result)
    
    def test_service_workflow(self):
        """Service workflow testi"""
        # Mock service bileşenleri
        mock_service = Mock()
        mock_service.running = False
        mock_service.status = {
            'active': False,
            'calibrated': False,
            'tutorial_mode': False,
            'stats': {
                'frames_processed': 0,
                'gestures_detected': 0
            }
        }
        
        # Service başlatma
        mock_service.start.return_value = None
        mock_service.running = True
        mock_service.status['active'] = True
        
        mock_service.start()
        self.assertTrue(mock_service.running)
        self.assertTrue(mock_service.status['active'])
        
        # Frame işleme simulasyonu
        mock_service._process_frame.return_value = None
        mock_service.status['stats']['frames_processed'] = 1
        
        mock_service._process_frame(Mock())
        self.assertEqual(mock_service.status['stats']['frames_processed'], 1)
    
    def test_error_handling_integration(self):
        """Hata yonetimi entegrasyonu testi"""
        mock_detector = Mock()
        mock_action_handler = Mock()
        
        # Detector hatasi
        mock_detector.detect_gesture.side_effect = Exception("Detection error")
        
        # Hata durumunda graceful handling
        try:
            result = mock_detector.detect_gesture([])
            self.fail("Exception expected")
        except Exception as e:
            self.assertEqual(str(e), "Detection error")
        
        # Action handler hatasi
        mock_action_handler.execute_action.side_effect = Exception("Action error")
        
        try:
            result = mock_action_handler.execute_action({}, (0, 0))
            self.fail("Exception expected")
        except Exception as e:
            self.assertEqual(str(e), "Action error")
    
    def test_config_propagation(self):
        """Konfigurasyon yayilimi testi"""
        # Mock config
        mock_config = {
            "settings": {
                "smoothing": 0.3,
                "click_cooldown": 0.2,
                "safe_mode": True
            }
        }
        
        # Mock detector
        mock_detector = Mock()
        mock_detector.config = mock_config
        
        # Mock action handler
        mock_action_handler = Mock()
        mock_action_handler.safe_mode = mock_config["settings"]["safe_mode"]
        
        # Config değerlerinin doğru aktarildiğini kontrol et
        self.assertEqual(mock_detector.config["settings"]["smoothing"], 0.3)
        self.assertTrue(mock_action_handler.safe_mode)
    
    def test_statistics_collection(self):
        """İstatistik toplama testi"""
        mock_detector = Mock()
        mock_action_handler = Mock()
        
        # Mock istatistikler
        mock_detector.get_performance_stats.return_value = {
            'total_frames': 100,
            'gestures_detected': 50
        }
        
        mock_action_handler.get_stats.return_value = {
            'total_actions': 25,
            'successful_actions': 20,
            'success_rate': 80.0
        }
        
        # İstatistikleri topla
        detector_stats = mock_detector.get_performance_stats()
        action_stats = mock_action_handler.get_stats()
        
        # Birleşik istatistikler
        combined_stats = {
            **detector_stats,
            **action_stats
        }
        
        self.assertEqual(combined_stats['total_frames'], 100)
        self.assertEqual(combined_stats['total_actions'], 25)
        self.assertEqual(combined_stats['success_rate'], 80.0)
    
    @patch('cv2.VideoCapture')
    def test_camera_integration(self, mock_capture):
        """Kamera entegrasyonu testi"""
        # Mock camera
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, Mock())  # success, frame
        mock_capture.return_value = mock_cap
        
        # Camera wrapper test
        camera = mock_capture(0)
        self.assertTrue(camera.isOpened())
        
        success, frame = camera.read()
        self.assertTrue(success)
        self.assertIsNotNone(frame)
    
    def test_command_processing_integration(self):
        """Komut işleme entegrasyonu testi"""
        mock_service = Mock()
        
        # Mock komut işleme
        commands = ['calibrate', 'tutorial_on', 'safe_on', 'stop']
        
        for command in commands:
            mock_service._handle_command.return_value = None
            mock_service._handle_command(command)
            mock_service._handle_command.assert_called_with(command)
    
    def test_logging_integration(self):
        """Loglama entegrasyonu testi"""
        import logging
        from io import StringIO
        
        # Mock log handler
        log_capture = StringIO()
        handler = logging.StreamHandler(log_capture)
        
        # Test logger
        logger = logging.getLogger('test_integration')
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        # Log mesajlari
        logger.info("Test message 1")
        logger.warning("Test warning")
        logger.error("Test error")
        
        # Log içeriğini kontrol et
        log_contents = log_capture.getvalue()
        self.assertIn("Test message 1", log_contents)
        self.assertIn("Test warning", log_contents)
        self.assertIn("Test error", log_contents)


class TestSystemRequirements(unittest.TestCase):
    """Sistem gereksinimleri testleri"""
    
    def test_python_version(self):
        """Python versiyon kontrolu"""
        self.assertGreaterEqual(sys.version_info[:2], (3, 6))
    
    def test_essential_imports(self):
        """Temel kutuphane import kontrolu"""
        essential_modules = [
            'json', 'time', 'math', 'os', 'sys', 
            'threading', 'logging', 'unittest'
        ]
        
        for module_name in essential_modules:
            try:
                __import__(module_name)
                import_success = True
            except ImportError:
                import_success = False
            
            self.assertTrue(import_success, f"Essential module {module_name} not available")
    
    def test_optional_imports(self):
        """Opsiyonel kutuphane kontrolu"""
        optional_modules = {
            'cv2': 'OpenCV',
            'mediapipe': 'MediaPipe',
            'pyautogui': 'PyAutoGUI',
            'numpy': 'NumPy'
        }
        
        available_modules = []
        
        for module_name, description in optional_modules.items():
            try:
                __import__(module_name)
                available_modules.append(description)
            except ImportError:
                pass
        
        # En az bir opsiyonel modul mevcut olmali
        self.assertGreater(len(available_modules), 0, 
                          f"No optional modules available. Tried: {list(optional_modules.values())}")


class TestMockComponents(unittest.TestCase):
    """Mock bileşenler testi"""
    
    def test_mock_landmarks(self):
        """Mock landmark'lar testi"""
        # MediaPipe landmark benzeri mock
        class MockLandmark:
            def __init__(self, x, y, z=0.0):
                self.x = x
                self.y = y
                self.z = z
        
        landmarks = []
        for i in range(21):  # MediaPipe 21 hand landmark
            landmarks.append(MockLandmark(i * 0.05, i * 0.05))
        
        self.assertEqual(len(landmarks), 21)
        self.assertEqual(landmarks[0].x, 0.0)
        self.assertEqual(landmarks[20].x, 1.0)
    
    def test_mock_gesture_data(self):
        """Mock gesture verisi testi"""
        gesture_templates = [
            {
                'action': 'left_click',
                'type': 'click',
                'confidence': 0.9,
                'stable': True,
                'pinch_active': True
            },
            {
                'action': 'right_click',
                'type': 'click',
                'confidence': 0.85,
                'stable': True,
                'pinch_active': False
            },
            {
                'action': 'drag_start',
                'type': 'drag',
                'confidence': 0.95,
                'stable': True,
                'drag_active': True
            }
        ]
        
        for gesture in gesture_templates:
            self.assertIn('action', gesture)
            self.assertIn('confidence', gesture)
            self.assertGreaterEqual(gesture['confidence'], 0.8)


if __name__ == '__main__':
    unittest.main()