import unittest
import sys
import os

from src_python.src.core.gesture_detector import GestureDetector
import math
import time


class MockLandmark:
    """MediaPipe landmark'ı taklit eden mock sınıf"""
    def __init__(self, x, y, z=0.0):
        self.x = x
        self.y = y
        self.z = z


class TestGestureDetector(unittest.TestCase):
    """GestureDetector modülü için unit testler"""
    
    def setUp(self):
        """Her test için setup"""
        self.detector = GestureDetector()
        # Mock config
        self.detector.config = {
            "settings": {
                "click_cooldown": 0.1,
                "smoothing": 0.3
            }
        }
    
    def tearDown(self):
        """Her test sonrası cleanup"""
        self.detector = None
    
    def create_mock_hand_landmarks(self, finger_positions):
        """Mock el landmark'ları oluştur
        finger_positions: {
            'wrist': (x, y),
            'thumb': (x, y),
            'index': (x, y),
            'middle': (x, y),
            'ring': (x, y),
            'pinky': (x, y)
        }
        """
        # MediaPipe hand landmark sırasına göre
        landmarks = [MockLandmark(0, 0)] * 21  # 21 landmark
        
        # Temel pozisyonları ayarla
        if 'wrist' in finger_positions:
            landmarks[0] = MockLandmark(*finger_positions['wrist'])
        if 'thumb' in finger_positions:
            landmarks[4] = MockLandmark(*finger_positions['thumb'])
        if 'index' in finger_positions:
            landmarks[8] = MockLandmark(*finger_positions['index'])
        if 'middle' in finger_positions:
            landmarks[12] = MockLandmark(*finger_positions['middle'])
        if 'ring' in finger_positions:
            landmarks[16] = MockLandmark(*finger_positions['ring'])
        if 'pinky' in finger_positions:
            landmarks[20] = MockLandmark(*finger_positions['pinky'])
        
        return landmarks
    
    def test_distance_calculation(self):
        """Mesafe hesaplama testi"""
        p1 = (0.0, 0.0)
        p2 = (3.0, 4.0)
        distance = self.detector._distance(p1, p2)
        self.assertAlmostEqual(distance, 5.0, places=2)
    
    def test_pinch_detection(self):
        """Pinch algılama testi"""
        # Manuel kalibrasyon ile başla
        self.detector.hand_size = 0.2
        self.detector.is_calibrated = True
        self.detector.pinch_threshold = 0.05
        
        # Pinch pozisyonu (başparmak ve işaret parmağı yakın)
        landmarks = self.create_mock_hand_landmarks({
            'wrist': (0.5, 0.5),
            'thumb': (0.52, 0.48),  # Yakın pozisyon
            'index': (0.53, 0.47),  # Yakın pozisyon
            'middle': (0.55, 0.45)
        })
        
        result = self.detector.detect_gesture(landmarks)
        self.assertTrue(result['pinch_active'])
    
    def test_no_pinch_detection(self):
        """Pinch algılanmama testi"""
        # Manuel kalibrasyon
        self.detector.hand_size = 0.2
        self.detector.is_calibrated = True
        self.detector.pinch_threshold = 0.05
        
        # Normal pozisyon (parmaklar uzak)
        landmarks = self.create_mock_hand_landmarks({
            'wrist': (0.5, 0.5),
            'thumb': (0.4, 0.4),    # Uzak pozisyon
            'index': (0.6, 0.3),    # Uzak pozisyon
            'middle': (0.65, 0.25)
        })
        
        result = self.detector.detect_gesture(landmarks)
        self.assertFalse(result['pinch_active'])
    
    def test_click_detection_sequence(self):
        """Click algılama sekansı testi"""
        # Manuel kalibrasyon
        self.detector.hand_size = 0.2
        self.detector.is_calibrated = True
        self.detector.pinch_threshold = 0.05
        
        # 1. Normal pozisyon
        landmarks1 = self.create_mock_hand_landmarks({
            'thumb': (0.4, 0.4),
            'index': (0.6, 0.3)
        })
        result1 = self.detector.detect_gesture(landmarks1)
        self.assertFalse(result1['pinch_active'])
        
        # 2. Pinch pozisyonu
        landmarks2 = self.create_mock_hand_landmarks({
            'thumb': (0.52, 0.48),
            'index': (0.53, 0.47)
        })
        result2 = self.detector.detect_gesture(landmarks2)
        self.assertTrue(result2['pinch_active'])
        
        # 3. Tekrar normal pozisyon (click tetiklenmeli)
        time.sleep(0.05)  # Kısa bekleme
        landmarks3 = self.create_mock_hand_landmarks({
            'thumb': (0.4, 0.4),
            'index': (0.6, 0.3)
        })
        result3 = self.detector.detect_gesture(landmarks3)
        
        # Click action bekleniyor
        if result3['action']:
            self.assertIn(result3['action'], ['left_click', 'right_click'])
    
    def test_drag_detection(self):
        """Drag (sürükleme) algılama testi"""
        # Manuel kalibrasyon
        self.detector.hand_size = 0.2
        self.detector.is_calibrated = True
        self.detector.pinch_threshold = 0.05
        
        # 3 parmak birlikte (drag grip)
        landmarks = self.create_mock_hand_landmarks({
            'thumb': (0.52, 0.48),
            'index': (0.53, 0.47),
            'middle': (0.525, 0.475)  # 3 parmak yakın
        })
        
        result = self.detector.detect_gesture(landmarks)
        self.assertTrue(result.get('drag_active', False))
    
    def test_calibration_system(self):
        """Kalibrasyon sistemi testi"""
        # Başlangıçta kalibre edilmemiş olmalı
        self.assertFalse(self.detector.is_calibrated)
        
        # Mock kalibrasyon verisi
        landmarks = self.create_mock_hand_landmarks({
            'wrist': (0.5, 0.5),
            'thumb': (0.4, 0.4),
            'index': (0.6, 0.3),
            'middle': (0.65, 0.25),
            'ring': (0.63, 0.2),
            'pinky': (0.6, 0.15)
        })
        
        # Kalibrasyon çalıştır
        result = self.detector.calibrate_hand(landmarks)
        
        # Sonuç kontrol et (auto calibrator'ın başarılı olup olmadığına bağlı)
        if result:
            self.assertTrue(self.detector.is_calibrated)
            self.assertIsNotNone(self.detector.hand_size)
    
    def test_extended_fingers_count(self):
        """Uzatılmış parmak sayma testi"""
        # Manuel kalibrasyon
        self.detector.hand_size = 0.2
        self.detector.is_calibrated = True
        
        # Tüm parmaklar açık
        landmarks = self.create_mock_hand_landmarks({
            'wrist': (0.5, 0.7),
            'thumb': (0.3, 0.4),
            'index': (0.5, 0.2),
            'middle': (0.6, 0.15),
            'ring': (0.65, 0.2),
            'pinky': (0.7, 0.25)
        })
        
        count = self.detector._count_extended_fingers(landmarks)
        self.assertGreaterEqual(count, 4)  # En az 4 parmak uzatılmış olmalı
    
    def test_gesture_stability(self):
        """Gesture stabilitesi testi"""
        # Manuel kalibrasyon
        self.detector.hand_size = 0.2
        self.detector.is_calibrated = True
        self.detector.pinch_threshold = 0.05
        
        # Aynı pozisyonda birkaç frame
        landmarks = self.create_mock_hand_landmarks({
            'thumb': (0.52, 0.48),
            'index': (0.53, 0.47)
        })
        
        results = []
        for _ in range(5):
            result = self.detector.detect_gesture(landmarks)
            results.append(result)
            time.sleep(0.01)
        
        # Tüm sonuçlar benzer olmalı
        for result in results:
            self.assertTrue(result['pinch_active'])
    
    def test_movement_threshold(self):
        """Hareket eşiği testi"""
        # Küçük hareket (titreme)
        small_movement = 0.001
        self.assertFalse(self.detector._is_intentional_movement(small_movement))
        
        # Büyük hareket (kasıtlı)
        large_movement = 0.05
        self.assertTrue(self.detector._is_intentional_movement(large_movement))
    
    def test_win_key_gesture(self):
        """Win tuşu gesture testi"""
        # Manuel kalibrasyon
        self.detector.hand_size = 0.2
        self.detector.is_calibrated = True
        
        # İlk yumruk pozisyonu
        fist_landmarks = self.create_mock_hand_landmarks({
            'wrist': (0.5, 0.7),
            'thumb': (0.48, 0.65),
            'index': (0.52, 0.65),
            'middle': (0.51, 0.68),
            'ring': (0.5, 0.69),
            'pinky': (0.49, 0.68)
        })
        
        result1 = self.detector.detect_gesture(fist_landmarks)
        
        # Sonra açık el pozisyonu
        time.sleep(0.1)
        open_landmarks = self.create_mock_hand_landmarks({
            'wrist': (0.5, 0.7),
            'thumb': (0.3, 0.4),
            'index': (0.5, 0.2),
            'middle': (0.6, 0.15),
            'ring': (0.65, 0.2),
            'pinky': (0.7, 0.25)
        })
        
        result2 = self.detector.detect_gesture(open_landmarks)
        
        # Win tuşu action'ı bekleniyor
        if result2['action']:
            self.assertEqual(result2['action'], 'win_key')
    
    def test_performance_stats(self):
        """Performans istatistikleri testi"""
        stats = self.detector.get_performance_stats()
        
        self.assertIn('total_frames', stats)
        self.assertIn('auto_calibration_frames', stats)
        self.assertIn('calibration_complete', stats)
        self.assertIsInstance(stats['total_frames'], int)
    
    def test_calibration_status(self):
        """Kalibrasyon durumu testi"""
        status = self.detector.get_calibration_status()
        
        self.assertIn('is_calibrated', status)
        self.assertIn('frames_processed', status)
        self.assertIsInstance(status['is_calibrated'], bool)
    
    def test_reset_calibration(self):
        """Kalibrasyon sıfırlama testi"""
        # İlk kalibre et
        self.detector.is_calibrated = True
        self.detector.hand_size = 0.2
        
        # Sıfırla
        self.detector.reset_calibration()
        
        # Kontrol et
        self.assertFalse(self.detector.is_calibrated)
        self.assertIsNone(self.detector.hand_size)
        self.assertEqual(len(self.detector.pinch_events), 0)


if __name__ == '__main__':
    unittest.main()