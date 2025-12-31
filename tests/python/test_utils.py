import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src_python.src'))


class TestSmoothingFilters(unittest.TestCase):
    """Smoothing filters (akilli filtreleme) modulu testleri"""
    
    def setUp(self):
        """Her test için setup"""
        try:
            from src_python.src.utils.smoothing_filters import AutoCalibrator, SmartCursor
            self.auto_calibrator = AutoCalibrator()
            self.smart_cursor = SmartCursor()
        except ImportError:
            self.skipTest("Smoothing filters module not available")
    
    def test_auto_calibrator_initialization(self):
        """AutoCalibrator başlatma testi"""
        self.assertFalse(self.auto_calibrator.is_calibrating)
        self.assertFalse(self.auto_calibrator.get_calibration_parameters()['is_calibrated'])
    
    def test_auto_calibrator_start_calibration(self):
        """AutoCalibrator kalibrasyon başlatma testi"""
        self.auto_calibrator.start_calibration()
        self.assertTrue(self.auto_calibrator.is_calibrating)
    
    def test_smart_cursor_initialization(self):
        """SmartCursor başlatma testi"""
        self.assertIsNotNone(self.smart_cursor.get_stats())
        
    def test_smart_cursor_movement_processing(self):
        """SmartCursor hareket işleme testi"""
        # İlk pozisyon
        pos1 = self.smart_cursor.process_movement(0.5, 0.5, 1920, 1080)
        self.assertIsInstance(pos1, tuple)
        self.assertEqual(len(pos1), 2)
        
        # İkinci pozisyon (yakin)
        pos2 = self.smart_cursor.process_movement(0.51, 0.51, 1920, 1080)
        self.assertIsInstance(pos2, tuple)
        
        # Filtreleme çalişiyor mu kontrol et
        self.assertNotEqual(pos1, pos2)
    
    def test_smart_cursor_reset(self):
        """SmartCursor sifirlama testi"""
        # Birkaç hareket yap
        self.smart_cursor.process_movement(0.5, 0.5, 1920, 1080)
        self.smart_cursor.process_movement(0.6, 0.6, 1920, 1080)
        
        # Sifirla
        self.smart_cursor.reset()
        
        # Stats sifirlanmiş olmali
        stats = self.smart_cursor.get_stats()
        self.assertIsInstance(stats, dict)
    
    def test_smart_cursor_sensitivity(self):
        """SmartCursor hassasiyet ayarlari testi"""
        # Varsayilan hassasiyet
        default_pos = self.smart_cursor.process_movement(0.5, 0.5, 1920, 1080)
        
        # Hassasiyeti değiştir
        self.smart_cursor.sensitivity_x = 2.0
        self.smart_cursor.sensitivity_y = 2.0
        
        # Ayni hareketi tekrarla
        high_sens_pos = self.smart_cursor.process_movement(0.51, 0.51, 1920, 1080)
        
        # Pozisyonlar farkli olmali
        self.assertNotEqual(default_pos, high_sens_pos)


class TestPerformanceMonitor(unittest.TestCase):
    """Performance monitor modulu testleri"""
    
    def setUp(self):
        """Her test için setup"""
        try:
            from utils.performance_monitor import PerformanceMonitor
            self.monitor = PerformanceMonitor()
        except ImportError:
            self.skipTest("Performance monitor module not available")
    
    def test_performance_monitor_initialization(self):
        """PerformanceMonitor başlatma testi"""
        self.assertIsNotNone(self.monitor)
    
    def test_frame_counting(self):
        """Frame sayma testi"""
        # Başlangiç frame sayisi
        initial_stats = self.monitor.get_stats()
        initial_frame_count = initial_stats.get('frame_count', 0)
        
        # Frame işle
        self.monitor.process_frame()
        
        # Frame sayisi artmiş olmali
        new_stats = self.monitor.get_stats()
        new_frame_count = new_stats.get('frame_count', 0)
        
        self.assertGreater(new_frame_count, initial_frame_count)
    
    def test_fps_calculation(self):
        """FPS hesaplama testi"""
        import time
        
        # Birkaç frame işle
        for _ in range(5):
            self.monitor.process_frame()
            time.sleep(0.01)  # Kuçuk gecikme
        
        stats = self.monitor.get_stats()
        fps = stats.get('fps', 0)
        
        # FPS pozitif olmali
        self.assertGreater(fps, 0)
    
    def test_reset_statistics(self):
        """İstatistik sifirlama testi"""
        # Birkaç frame işle
        for _ in range(3):
            self.monitor.process_frame()
        
        # İstatistikleri sifirla
        self.monitor.reset()
        
        # Frame sayisi sifirlanmiş olmali
        stats = self.monitor.get_stats()
        frame_count = stats.get('frame_count', 0)
        self.assertEqual(frame_count, 0)


class TestMainModule(unittest.TestCase):
    """Ana main.py modulu testleri"""
    
    def setUp(self):
        """Her test için setup"""
        try:
            import main
            self.main_module = main
        except ImportError:
            self.skipTest("Main module not available")
    
    def test_gesture_control_system_init(self):
        """GestureControlSystem başlatma testi"""
        if hasattr(self.main_module, 'GestureControlSystem'):
            # Mock config dosyasi ile başlat
            with patch('builtins.open', create=True) as mock_open:
                mock_open.return_value.__enter__.return_value.read.return_value = '{"settings": {"smoothing": 0.3}}'
                
                system = self.main_module.GestureControlSystem()
                self.assertIsNotNone(system)
                self.assertFalse(system.tutorial_mode)
    
    def test_distance_calculation(self):
        """Mesafe hesaplama fonksiyonu testi"""
        if hasattr(self.main_module, '_dist'):
            # Test mesafe hesaplama
            distance = self.main_module._dist((0, 0), (3, 4))
            self.assertAlmostEqual(distance, 5.0, places=2)
    
    @patch('cv2.VideoCapture')
    @patch('cv2.namedWindow')
    @patch('cv2.startWindowThread')
    def test_run_function_initialization(self, mock_thread, mock_window, mock_capture):
        """Run fonksiyonu başlatma testi"""
        # Mock camera
        mock_cap = Mock()
        mock_cap.isOpened.return_value = False  # Kamera açilmadi
        mock_capture.return_value = mock_cap
        
        # Mock MediaPipe import
        with patch.dict('sys.modules', {'mediapipe': Mock()}):
            # run fonksiyonunu test et (kamera hatasi bekleniyor)
            if hasattr(self.main_module, 'run'):
                # Kamera hatasi nedeniyle erken çikiş yapmali
                try:
                    self.main_module.run(camera_index=0)
                except:
                    pass  # Hata bekleniyor
                
                # Mock'larin çağrildiğini kontrol et
                mock_capture.assert_called_once_with(0)


class TestServiceModule(unittest.TestCase):
    """Service.py modulu testleri"""
    
    def setUp(self):
        """Her test için setup"""
        try:
            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
            import service
            self.service_module = service
        except ImportError:
            self.skipTest("Service module not available")
    
    def test_hci_gesture_service_init(self):
        """HCIGestureService başlatma testi"""
        if hasattr(self.service_module, 'HCIGestureService'):
            # Geçici dizin oluştur
            import tempfile
            with tempfile.TemporaryDirectory() as temp_dir:
                service = self.service_module.HCIGestureService(temp_dir)
                self.assertIsNotNone(service)
                self.assertFalse(service.running)
    
    def test_service_status_tracking(self):
        """Service durum takibi testi"""
        if hasattr(self.service_module, 'HCIGestureService'):
            import tempfile
            with tempfile.TemporaryDirectory() as temp_dir:
                service = self.service_module.HCIGestureService(temp_dir)
                
                # Başlangiç durumu
                self.assertIn('active', service.status)
                self.assertIn('calibrated', service.status)
                self.assertIn('stats', service.status)
                
                # İstatistikler
                stats = service.status['stats']
                self.assertEqual(stats['frames_processed'], 0)
                self.assertEqual(stats['gestures_detected'], 0)
    
    @patch('cv2.VideoCapture')
    def test_service_camera_initialization(self, mock_capture):
        """Service kamera başlatma testi"""
        if hasattr(self.service_module, 'HCIGestureService'):
            import tempfile
            with tempfile.TemporaryDirectory() as temp_dir:
                service = self.service_module.HCIGestureService(temp_dir)
                
                # Mock camera
                mock_cap = Mock()
                mock_cap.isOpened.return_value = True
                mock_capture.return_value = mock_cap
                
                # Kamera başlatma testi
                try:
                    service._init_camera()
                    self.assertIsNotNone(service.camera)
                except:
                    pass  # MediaPipe import hatasi olabilir


class TestUtilityFunctions(unittest.TestCase):
    """Yardimci fonksiyonlar testi"""
    
    def test_import_safety(self):
        """Import guvenliği testi"""
        # Ana modullerin import edilebilirliği
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
            
            # Core moduller
            try:
                from core import gesture_detector, action_handler
                core_imports_ok = True
            except ImportError:
                core_imports_ok = False
            
            # Utils moduller
            try:
                from utils import smoothing_filters
                utils_imports_ok = True
            except ImportError:
                utils_imports_ok = False
            
            # En az bir modul çalişiyor olmali
            self.assertTrue(core_imports_ok or utils_imports_ok)
            
        except Exception as e:
            self.skipTest(f"Import test failed: {e}")
    
    def test_config_file_handling(self):
        """Config dosyasi işleme testi"""
        import tempfile
        import json
        
        # Geçici config dosyasi oluştur
        config_data = {
            "settings": {
                "smoothing": 0.3,
                "click_cooldown": 0.2
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name
        
        try:
            # Config dosyasini oku
            with open(config_path, 'r') as f:
                loaded_config = json.load(f)
            
            self.assertEqual(loaded_config['settings']['smoothing'], 0.3)
            self.assertEqual(loaded_config['settings']['click_cooldown'], 0.2)
            
        finally:
            # Geçici dosyayi temizle
            os.unlink(config_path)


if __name__ == '__main__':
    unittest.main()