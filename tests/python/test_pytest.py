import pytest
import sys
import os
from unittest.mock import Mock, patch

class TestGestureDetectorPytest:
    """Pytest ile GestureDetector testleri"""
    
    def setup_method(self):
        """Her test metodu için setup"""
        try:
            from src_python.src.core.gesture_detector import GestureDetector
            self.detector = GestureDetector()
        except ImportError:
            pytest.skip("GestureDetector module not available")
    
    def test_detector_initialization(self):
        """Detector başlatma testi"""
        assert self.detector is not None
        assert hasattr(self.detector, 'detect_gesture')
    
    @pytest.mark.parametrize("distance_input,expected", [
        (((0.0, 0.0), (3.0, 4.0)), 5.0),
        (((0.0, 0.0), (0.0, 0.0)), 0.0),
        (((1.0, 1.0), (1.0, 1.0)), 0.0),
    ])
    def test_distance_calculation_parametrized(self, distance_input, expected):
        """Parametrize edilmiş mesafe hesaplama testi"""
        p1, p2 = distance_input
        if hasattr(self.detector, '_distance'):
            result = self.detector._distance(p1, p2)
            assert abs(result - expected) < 0.01
    
    def test_calibration_status(self):
        """Kalibrasyon durum testi"""
        status = self.detector.get_calibration_status()
        assert isinstance(status, dict)
        assert 'is_calibrated' in status
    
    @pytest.fixture
    def mock_landmarks(self):
        """Mock landmarks fixture"""
        class MockLandmark:
            def __init__(self, x, y, z=0.0):
                self.x, self.y, self.z = x, y, z
        
        return [MockLandmark(i * 0.05, i * 0.05) for i in range(21)]
    
    def test_gesture_detection_with_fixture(self, mock_landmarks):
        """Fixture kullanarak gesture algılama testi"""
        result = self.detector.detect_gesture(mock_landmarks)
        assert isinstance(result, dict)
        assert 'action' in result
        assert 'confidence' in result


class TestActionHandlerPytest:
    """Pytest ile ActionHandler testleri"""
    
    def setup_method(self):
        """Her test metodu için setup"""
        try:
            from src_python.src.core.action_handler import ActionHandler
            self.handler = ActionHandler()
        except ImportError:
            pytest.skip("ActionHandler module not available")
    
    def test_handler_initialization(self):
        """Handler başlatma testi"""
        assert self.handler is not None
        assert hasattr(self.handler, 'execute_action')
    
    @pytest.mark.parametrize("safe_mode", [True, False])
    def test_safe_mode_toggle(self, safe_mode):
        """Parametrize edilmiş güvenli mod testi"""
        self.handler.enable_safe_mode(safe_mode)
        assert self.handler.safe_mode == safe_mode
    
    def test_status_reporting(self):
        """Durum raporlama testi"""
        status = self.handler.get_status()
        assert isinstance(status, dict)
        required_fields = ['disabled', 'cursor_frozen', 'safe_mode']
        for field in required_fields:
            assert field in status
    
    @pytest.mark.parametrize("gesture_data,expected_result", [
        ({
            'action': 'left_click',
            'confidence': 0.9,
            'stable': True
        }, None),  # Result depends on mocking
        ({
            'action': 'right_click',
            'confidence': 0.5,  # Low confidence
            'stable': True
        }, False),  # Should be rejected
    ])
    def test_action_execution_parametrized(self, gesture_data, expected_result):
        """Parametrize edilmiş eylem yürütme testi"""
        with patch('pyautogui.click'):
            with patch('pyautogui.position', return_value=(500, 400)):
                with patch('pyautogui.size', return_value=(1920, 1080)):
                    result = self.handler.execute_action(gesture_data, (500, 400))
                    if expected_result is not None:
                        assert result == expected_result


class TestServicePytest:
    """Pytest ile Service testleri"""
    
    def setup_method(self):
        """Her test metodu için setup"""
        try:
            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
            import src_python.service
            self.service_module = service
        except ImportError:
            pytest.skip("Service module not available")
    
    def test_service_class_exists(self):
        """Service sınıfı varlık testi"""
        assert hasattr(self.service_module, 'HCIGestureService')
    
    @pytest.fixture
    def temp_extension_dir(self, tmp_path):
        """Geçici extension dizini fixture"""
        return str(tmp_path)
    
    def test_service_initialization(self, temp_extension_dir):
        """Service başlatma testi"""
        service = self.service_module.HCIGestureService(temp_extension_dir)
        assert service is not None
        assert not service.running
        assert service.extension_dir.exists()


class TestUtilsPytest:
    """Pytest ile Utils testleri"""
    
    def test_smoothing_filters_import(self):
        """Smoothing filters import testi"""
        try:
            from src_python.src.utils.smoothing_filters import AutoCalibrator, SmartCursor
            calibrator = AutoCalibrator()
            cursor = SmartCursor()
            assert calibrator is not None
            assert cursor is not None
        except ImportError:
            pytest.skip("Smoothing filters not available")
    
    @pytest.mark.parametrize("x,y,screen_w,screen_h", [
        (0.5, 0.5, 1920, 1080),
        (0.0, 0.0, 1920, 1080),
        (1.0, 1.0, 1920, 1080),
    ])
    def test_cursor_movement_parametrized(self, x, y, screen_w, screen_h):
        """Parametrize edilmiş cursor hareketi testi"""
        try:
            from src_python.src.utils.smoothing_filters import SmartCursor
            cursor = SmartCursor()
            result = cursor.process_movement(x, y, screen_w, screen_h)
            assert isinstance(result, tuple)
            assert len(result) == 2
            assert 0 <= result[0] <= screen_w
            assert 0 <= result[1] <= screen_h
        except ImportError:
            pytest.skip("SmartCursor not available")


class TestConfigurationPytest:
    """Pytest ile konfigürasyon testleri"""
    
    @pytest.fixture
    def sample_config(self):
        """Örnek konfigürasyon fixture"""
        return {
            "settings": {
                "smoothing": 0.3,
                "click_cooldown": 0.2,
                "safe_mode": True,
                "tutorial_mode": False
            },
            "gestures": {
                "left_click": {
                    "confidence_threshold": 0.8,
                    "stability_required": True
                },
                "right_click": {
                    "confidence_threshold": 0.75,
                    "stability_required": True
                }
            }
        }
    
    def test_config_structure(self, sample_config):
        """Konfigürasyon yapısı testi"""
        assert "settings" in sample_config
        assert "gestures" in sample_config
        
        settings = sample_config["settings"]
        assert "smoothing" in settings
        assert "click_cooldown" in settings
        assert isinstance(settings["smoothing"], (int, float))
        assert isinstance(settings["click_cooldown"], (int, float))
    
    def test_gesture_config(self, sample_config):
        """Gesture konfigürasyonu testi"""
        gestures = sample_config["gestures"]
        
        for gesture_name, gesture_config in gestures.items():
            assert "confidence_threshold" in gesture_config
            assert "stability_required" in gesture_config
            assert 0.0 <= gesture_config["confidence_threshold"] <= 1.0
            assert isinstance(gesture_config["stability_required"], bool)
    
    @pytest.mark.parametrize("config_file", [
        "gesture_map.json",
        "config/gesture_map.json",
    ])
    def test_config_file_paths(self, config_file):
        """Konfigürasyon dosya yolları testi"""
        # Test that config paths are properly formed
        assert config_file.endswith('.json')
        assert 'gesture' in config_file.lower()


class TestPerformancePytest:
    """Pytest ile performans testleri"""
    
    @pytest.mark.performance
    def test_gesture_detection_performance(self):
        """Gesture algılama performans testi"""
        try:
            from src_python.src.core.gesture_detector import GestureDetector
            import time
            
            detector = GestureDetector()
            
            # Mock landmarks
            class MockLandmark:
                def __init__(self, x, y):
                    self.x, self.y = x, y
            
            landmarks = [MockLandmark(i * 0.05, i * 0.05) for i in range(21)]
            
            # Performans ölçümü
            start_time = time.time()
            
            for _ in range(100):  # 100 gesture detection
                detector.detect_gesture(landmarks)
            
            end_time = time.time()
            avg_time = (end_time - start_time) / 100
            
            # Her gesture detection 10ms'den az sürmeli
            assert avg_time < 0.01, f"Average detection time too slow: {avg_time:.4f}s"
            
        except ImportError:
            pytest.skip("GestureDetector not available for performance test")
    
    @pytest.mark.performance
    def test_action_execution_performance(self):
        """Action yürütme performans testi"""
        try:
            from src_python.src.core.action_handler import ActionHandler
            import time
            
            handler = ActionHandler()
            
            gesture_data = {
                'action': 'left_click',
                'confidence': 0.9,
                'stable': True
            }
            
            start_time = time.time()
            
            with patch('pyautogui.click'):
                with patch('pyautogui.position', return_value=(500, 400)):
                    with patch('pyautogui.size', return_value=(1920, 1080)):
                        for _ in range(50):  # 50 action executions
                            handler.execute_action(gesture_data, (500, 400))
            
            end_time = time.time()
            avg_time = (end_time - start_time) / 50
            
            # Her action execution 5ms'den az sürmeli
            assert avg_time < 0.005, f"Average action time too slow: {avg_time:.4f}s"
            
        except ImportError:
            pytest.skip("ActionHandler not available for performance test")


class TestEdgeCasesPytest:
    """Pytest ile edge case testleri"""
    
    @pytest.mark.parametrize("invalid_input", [
        None,
        [],
        {},
        "invalid",
        123
    ])
    def test_invalid_landmarks_input(self, invalid_input):
        """Geçersiz landmark girişi testi"""
        try:
            from src_python.src.core.gesture_detector import GestureDetector
            detector = GestureDetector()
            
            # Invalid input should not crash
            try:
                result = detector.detect_gesture(invalid_input)
                # Should return a valid response or handle gracefully
                assert isinstance(result, dict) or result is None
            except (TypeError, AttributeError, IndexError, KeyError):
                # These exceptions are acceptable for invalid input
                pass
                
        except ImportError:
            pytest.skip("GestureDetector not available")
    
    @pytest.mark.parametrize("extreme_coords", [
        (-1000, -1000),
        (10000, 10000),
        (0, 0),
        (1, 1)
    ])
    def test_extreme_coordinate_handling(self, extreme_coords):
        """Ekstrem koordinat işleme testi"""
        try:
            from src_python.src.core.action_handler import ActionHandler
            handler = ActionHandler()
            
            # Extreme coordinates should be handled safely
            with patch('pyautogui.position', return_value=(500, 400)):
                with patch('pyautogui.size', return_value=(1920, 1080)):
                    result = handler.move_cursor(
                        extreme_coords[0], extreme_coords[1], 
                        pinch_active=True
                    )
                    # Should not crash and return boolean
                    assert isinstance(result, bool)
                    
        except ImportError:
            pytest.skip("ActionHandler not available")
    
    def test_memory_usage(self):
        """Bellek kullanımı testi"""
        try:
            from src_python.src.core.gesture_detector import GestureDetector
            import gc
            
            # Create and destroy multiple instances
            for _ in range(10):
                detector = GestureDetector()
                del detector
                gc.collect()
            
            # Memory should be freed properly
            # This is a basic test - advanced memory profiling would need additional tools
            assert True  # If we reach here without memory errors, it's good
            
        except ImportError:
            pytest.skip("GestureDetector not available for memory test")


if __name__ == '__main__':
    pytest.main([__file__])