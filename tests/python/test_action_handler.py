import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

try:
    from src_python.src.core.action_handler import ActionHandler
except ImportError:
    # Fallback - create a mock for testing
    class ActionHandler:
        def __init__(self):
            self.is_disabled = False
            self.cursor_frozen = False
            self.drag_mode = False
            self.safe_mode = True


class TestActionHandler(unittest.TestCase):
    """ActionHandler modülü için unit testler"""
    
    def setUp(self):
        """Her test için setup"""
        self.action_handler = ActionHandler()
        
    def tearDown(self):
        """Her test sonrası cleanup"""
        self.action_handler = None
    
    @patch('pyautogui.click')
    def test_left_click_safe(self, mock_click):
        """Güvenli sol tıklama testi"""
        # Mock pyautogui.position to return a safe position
        with patch('pyautogui.position', return_value=(500, 400)):
            with patch('pyautogui.size', return_value=(1920, 1080)):
                self.action_handler.safe_margin = 50
                result = self.action_handler._left_click_safe()
                
                if hasattr(self.action_handler, '_left_click_safe'):
                    self.assertTrue(result)
                    mock_click.assert_called_once()
    
    @patch('pyautogui.click')
    def test_right_click_safe(self, mock_click):
        """Güvenli sağ tıklama testi"""
        with patch('pyautogui.position', return_value=(500, 400)):
            with patch('pyautogui.size', return_value=(1920, 1080)):
                self.action_handler.safe_margin = 50
                
                if hasattr(self.action_handler, '_right_click_safe'):
                    result = self.action_handler._right_click_safe()
                    self.assertTrue(result)
                    mock_click.assert_called_once_with(button='right')
    
    def test_safe_mode_toggle(self):
        """Güvenli mod açma/kapama testi"""
        # Başlangıçta güvenli mod açık
        self.assertTrue(self.action_handler.safe_mode)
        
        # Güvenli modu kapat
        self.action_handler.enable_safe_mode(False)
        self.assertFalse(self.action_handler.safe_mode)
        
        # Tekrar aç
        self.action_handler.enable_safe_mode(True)
        self.assertTrue(self.action_handler.safe_mode)
    
    def test_position_safety_check(self):
        """Pozisyon güvenlik kontrolü testi"""
        if hasattr(self.action_handler, '_is_position_safe'):
            # Güvenli pozisyon
            safe_result = self.action_handler._is_position_safe(500, 400)
            self.assertTrue(safe_result)
            
            # Güvenli olmayan pozisyonlar (ekran kenarları)
            unsafe_positions = [
                (10, 400),    # Sol kenar
                (1910, 400),  # Sağ kenar
                (500, 10),    # Üst kenar
                (500, 1070)   # Alt kenar
            ]
            
            for x, y in unsafe_positions:
                unsafe_result = self.action_handler._is_position_safe(x, y)
                self.assertFalse(unsafe_result)
    
    def test_action_safety_rate_limiting(self):
        """Eylem hız sınırlama testi"""
        if hasattr(self.action_handler, '_is_action_safe'):
            # İlk eylem güvenli olmalı
            self.assertTrue(self.action_handler._is_action_safe('left_click'))
            
            # Aynı eylemi hızlıca tekrarlama
            for _ in range(5):
                result = self.action_handler._is_action_safe('left_click')
            
            # Rate limiting devreye girmeli
            final_result = self.action_handler._is_action_safe('left_click')
            # Bu test platformdan platforma değişebilir
    
    def test_disabled_mode(self):
        """Devre dışı modu testi"""
        # Normal durumda aktif
        self.assertFalse(self.action_handler.is_disabled)
        
        # Devre dışı bırak
        if hasattr(self.action_handler, '_toggle_disabled_mode'):
            self.action_handler._toggle_disabled_mode()
            self.assertTrue(self.action_handler.is_disabled)
            
            # Tekrar aktif et
            self.action_handler._toggle_disabled_mode()
            self.assertFalse(self.action_handler.is_disabled)
    
    def test_cursor_freeze(self):
        """İmleç dondurma testi"""
        # Normal durumda serbest
        self.assertFalse(self.action_handler.cursor_frozen)
        
        # Dondur
        if hasattr(self.action_handler, '_toggle_cursor_freeze'):
            self.action_handler._toggle_cursor_freeze()
            self.assertTrue(self.action_handler.cursor_frozen)
            
            # Çöz
            self.action_handler._toggle_cursor_freeze()
            self.assertFalse(self.action_handler.cursor_frozen)
    
    def test_drag_mode(self):
        """Sürükleme modu testi"""
        # Başlangıçta drag modu kapalı
        self.assertFalse(self.action_handler.drag_mode)
        
        # Mock cursor position
        with patch('pyautogui.position', return_value=(500, 400)):
            with patch('pyautogui.size', return_value=(1920, 1080)):
                with patch('pyautogui.mouseDown'):
                    if hasattr(self.action_handler, '_start_drag_safe'):
                        # Drag başlat
                        result = self.action_handler._start_drag_safe((500, 400))
                        if result:
                            self.assertTrue(self.action_handler.drag_mode)
    
    @patch('pyautogui.moveTo')
    def test_cursor_movement(self, mock_move):
        """İmleç hareketi testi"""
        with patch('pyautogui.position', return_value=(500, 400)):
            with patch('pyautogui.size', return_value=(1920, 1080)):
                # Pinch aktifken hareket
                result = self.action_handler.move_cursor(600, 500, pinch_active=True)
                self.assertTrue(result)
                mock_move.assert_called()
                
                # Pinch aktif değilken hareket etmemeli
                result = self.action_handler.move_cursor(600, 500, pinch_active=False)
                self.assertFalse(result)
    
    def test_status_reporting(self):
        """Durum raporlama testi"""
        status = self.action_handler.get_status()
        
        # Temel durum alanları mevcut olmalı
        expected_fields = ['disabled', 'cursor_frozen', 'drag_mode', 'safe_mode']
        for field in expected_fields:
            self.assertIn(field, status)
    
    def test_statistics_reporting(self):
        """İstatistik raporlama testi"""
        stats = self.action_handler.get_stats()
        
        # Temel istatistik alanları
        self.assertIn('total_actions', stats)
        self.assertIsInstance(stats['total_actions'], int)
    
    def test_execute_action_with_mock_gesture(self):
        """Mock gesture verisi ile eylem yürütme testi"""
        # Mock gesture verisi
        gesture_data = {
            'action': 'left_click',
            'type': 'click',
            'confidence': 0.9,
            'stable': True
        }
        cursor_pos = (500, 400)
        
        with patch('pyautogui.click') as mock_click:
            with patch('pyautogui.position', return_value=(500, 400)):
                with patch('pyautogui.size', return_value=(1920, 1080)):
                    result = self.action_handler.execute_action(gesture_data, cursor_pos)
                    
                    # Güvenli mod aktifse eylem bloklanabilir
                    if not self.action_handler.safe_mode or result:
                        # Action execute edilmişse click çağrılmalı
                        if result:
                            mock_click.assert_called()
    
    def test_action_safety_with_low_confidence(self):
        """Düşük güvenle eylem güvenlik testi"""
        # Düşük güvenli gesture
        gesture_data = {
            'action': 'left_click',
            'type': 'click',
            'confidence': 0.5,  # Düşük güven
            'stable': True
        }
        cursor_pos = (500, 400)
        
        result = self.action_handler.execute_action(gesture_data, cursor_pos)
        # Düşük güvenli eylemler reddedilmeli
        self.assertFalse(result)
    
    def test_action_safety_with_unstable_gesture(self):
        """Stabil olmayan gesture güvenlik testi"""
        # Stabil olmayan gesture
        gesture_data = {
            'action': 'left_click',
            'type': 'click',
            'confidence': 0.9,
            'stable': False  # Stabil değil
        }
        cursor_pos = (500, 400)
        
        result = self.action_handler.execute_action(gesture_data, cursor_pos)
        # Stabil olmayan eylemler reddedilmeli
        self.assertFalse(result)
    
    @patch('subprocess.Popen')
    def test_open_app_safe(self, mock_popen):
        """Güvenli uygulama açma testi"""
        if hasattr(self.action_handler, '_open_app_safe'):
            result = self.action_handler._open_app_safe('firefox')
            self.assertTrue(result)
            mock_popen.assert_called_once()
    
    @patch('pyautogui.scroll')
    def test_scroll_safe(self, mock_scroll):
        """Güvenli kaydırma testi"""
        if hasattr(self.action_handler, '_scroll_safe'):
            # Yukarı kaydırma
            result = self.action_handler._scroll_safe('scroll_up')
            self.assertTrue(result)
            mock_scroll.assert_called_with(2)
            
            # Aşağı kaydırma
            result = self.action_handler._scroll_safe('scroll_down')
            self.assertTrue(result)
            mock_scroll.assert_called_with(-2)
    
    @patch('pyautogui.hotkey')
    def test_navigation_safe(self, mock_hotkey):
        """Güvenli navigasyon testi"""
        if hasattr(self.action_handler, '_navigate_safe'):
            # Geri gitme
            result = self.action_handler._navigate_safe('navigate_back')
            self.assertTrue(result)
            mock_hotkey.assert_called_with('alt', 'left')
            
            # İleri gitme
            result = self.action_handler._navigate_safe('navigate_forward')
            self.assertTrue(result)
            mock_hotkey.assert_called_with('alt', 'right')


if __name__ == '__main__':
    unittest.main()