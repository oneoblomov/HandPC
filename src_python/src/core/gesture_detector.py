import math
import time
from typing import Dict, Tuple, Any
import json

# Import sorununu çözmek için absolute import kullan
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from utils.smoothing_filters import AutoCalibrator, SmartCursor
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
    from smoothing_filters import AutoCalibrator, SmartCursor


class GestureDetector:
    """ULTRA OPTİMİZE GESTİCR DETECTOR - Akıllı filtreleme ve otomatik kalibrasyon"""

    def __init__(self, config_path: str = "config/gesture_map.json"):
        self.config = self._load_config(config_path)

        # Yeni akıllı sistemler
        self.auto_calibrator = AutoCalibrator()
        self.smart_cursor = SmartCursor()

        # Legacy compatibility
        self.hand_size = None
        self.is_calibrated = False

        # Dinamik eşikler (otomatik ayarlanacak)
        self.pinch_threshold = 0.05
        self.movement_threshold = 0.02

        # State tracking - minimal
        self.prev_pinch = False
        self.pinch_events = []  # [(time, three_finger_mode), ...]
        self.last_action_time = 0
        self.prev_hand_pose = None
        self.last_win_time = 0

        # Perfoormance tracking
        self.frame_count = 0
        self.auto_calibration_frames = 0

        print("🚀 Akıllı Gesture Detector başlatıldı - Otomatik kalibrasyon aktif")

    def _load_config(self, config_path: str) -> Dict:
        """Konfigürasyon dosyasını yükle"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"settings": {"click_cooldown": 0.2}}

    def calibrate_hand(self, landmarks) -> bool:
        """Akıllı otomatik kalibrasyon"""
        if self.is_calibrated:
            return True

        # Otomatik kalibrasyon başlatılmamışsa başlat
        if not self.auto_calibrator.is_calibrating:
            self.auto_calibrator.start_calibration()

        # Kalibrasyon örneği ekle
        calibration_complete = self.auto_calibrator.add_calibration_sample(landmarks)

        if calibration_complete:
            # Kalibrasyon parametrelerini al
            params = self.auto_calibrator.get_calibration_parameters()

            if params['is_calibrated']:
                self.hand_size = params['hand_size']
                self.pinch_threshold = self.auto_calibrator.get_pinch_threshold()
                self.movement_threshold = self.auto_calibrator.get_movement_threshold()
                self.is_calibrated = True

                # Smart cursor'a hassasiyet ayarlarını aktar
                self.smart_cursor.sensitivity_x = params['sensitivity_multiplier']
                self.smart_cursor.sensitivity_y = params['sensitivity_multiplier']

                print("✅ Akıllı kalibrasyon tamamlandı!")
                print(f"   📏 El boyutu: {self.hand_size:.3f}")
                print(f"   🎯 Pinch eşiği: {self.pinch_threshold:.3f}")
                print(f"   📈 Hareket eşiği: {self.movement_threshold:.3f}")
                print(f"   ⚡ Hassasiyet: {params['sensitivity_multiplier']:.2f}")

                return True

        return False

    def _distance(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """İki nokta arası mesafe"""
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

    def _is_intentional_movement(self, movement_magnitude: float) -> bool:
        """Hareketin kasıtlı olup olmadığını kontrol et"""
        return movement_magnitude > self.movement_threshold

    def _is_precise_area(self, cursor_pos: Tuple[float, float]) -> bool:
        """Cursor hassas alanda mı? (menüler, butonlar vs.)"""
        # Bu basit implementasyon - geliştirilmesi gerekebilir
        x, y = cursor_pos
        # Ekran kenarları ve köşeler hassas kabul edilir
        return x < 100 or x > 1820 or y < 100 or y > 980

    def _count_extended_fingers(self, landmarks) -> int:
        """Uzatılmış parmak sayısı"""
        if not self.hand_size:
            return 0  # Kalibrasyon yapılmamış

        wrist = (landmarks[0].x, landmarks[0].y)
        finger_tips = [
            (landmarks[4].x, landmarks[4].y),   # Thumb
            (landmarks[8].x, landmarks[8].y),   # Index
            (landmarks[12].x, landmarks[12].y),  # Middle
            (landmarks[16].x, landmarks[16].y),  # Ring
            (landmarks[20].x, landmarks[20].y),  # Pinky
        ]

        extended = 0
        for tip in finger_tips:
            if self._distance(wrist, tip) > self.hand_size * 0.6:
                extended += 1

        return extended

    def detect_gesture(self, landmarks) -> Dict[str, Any]:
        """YENİ AKILLI GESTURE SİSTEMİ - Titreme önleyici ve otomatik optimize"""

        self.frame_count += 1

        # Otomatik kalibrasyon (ilk 90 frame)
        if not self.is_calibrated:
            if self.auto_calibration_frames < 90:  # 3 saniye @ 30fps
                self.auto_calibration_frames += 1
                self.calibrate_hand(landmarks)
                return {'type': 'calibration', 'action': None, 'confidence': 0.0, 'pinch_active': False}
            else:
                # Manuel kalibrasyon yap
                self.calibrate_hand(landmarks)

        current_time = time.time()

        # Ham pozisyonlar
        thumb = (landmarks[4].x, landmarks[4].y)
        index = (landmarks[8].x, landmarks[8].y)
        middle = (landmarks[12].x, landmarks[12].y)

        # Akıllı cursor pozisyonu hesapla (titreme filtreli)
        cursor_pos = self.smart_cursor.process_movement(
            index[0], index[1], 1920, 1080  # Varsayılan çözünürlük
        )

        # 1. PINCH DETECTION (dinamik eşik)
        pinch_distance = self._distance(thumb, index)
        is_pinch = pinch_distance < self.pinch_threshold

        # 2. DRAG DETECTION (3 parmak birlikte)
        middle_to_thumb = self._distance(middle, thumb)
        middle_to_index = self._distance(middle, index)
        is_drag_grip = (middle_to_thumb < self.pinch_threshold * 1.3 and
                        middle_to_index < self.pinch_threshold * 1.3 and
                        is_pinch)

        result = {
            'type': None,
            'action': None,
            'confidence': 0.0,
            'pinch_active': is_pinch,
            'drag_active': is_drag_grip,
            'stable': True,
            'cursor_pos': cursor_pos,  # Filtrelenmiş cursor pozisyonu
            'raw_pinch_distance': pinch_distance,
            'pinch_threshold': self.pinch_threshold
        }

        # 3. DRAG (TUTMA) İŞLEMLERİ - Geliştirilmiş
        if is_drag_grip and not getattr(self, 'prev_drag_grip', False):
            # Drag başladı - stabilite kontrolü
            print("✋ DRAG (Tutma) başladı - titreme korumalı")
            result.update({
                'type': 'drag',
                'action': 'drag_start',
                'confidence': 0.95,
                'stable': True
            })
            self.last_action_time = current_time

        elif not is_drag_grip and getattr(self, 'prev_drag_grip', False):
            # Drag bitti
            print("✋ DRAG (Tutma) bitti")
            result.update({
                'type': 'drag',
                'action': 'drag_end',
                'confidence': 0.95,
                'stable': True
            })
            self.last_action_time = current_time

        elif is_drag_grip:
            # Drag devam ediyor - yumuşak hareket
            result.update({
                'type': 'drag',
                'action': 'drag_move',
                'confidence': 0.95,
                'stable': True
            })

        # 4. CLICK İŞLEMLERİ - Geliştirilmiş titreme kontrolü
        elif is_pinch and not self.prev_pinch and not is_drag_grip:
            # Normal pinch başladı
            if self._is_intentional_movement(pinch_distance):
                print(f"📌 Kasıtlı click pinch başladı (mesafe: {pinch_distance:.3f})")

        elif not is_pinch and self.prev_pinch and not is_drag_grip:
            # Pinch bitti - click eventi

            # Gelişmiş cooldown kontrolü
            min_cooldown = 0.1 if self._is_precise_area(cursor_pos) else 0.15
            if current_time - self.last_action_time < min_cooldown:
                print("⏱️ Click çok hızlı - titreme koruması aktif")
                self.prev_pinch = is_pinch
                self.prev_drag_grip = is_drag_grip
                return result

            # Hareket büyüklüğü kontrolü
            if not self._is_intentional_movement(self.pinch_threshold - pinch_distance):
                print("🚫 Titreme algılandı - click iptal edildi")
                self.prev_pinch = is_pinch
                self.prev_drag_grip = is_drag_grip
                return result

            # Click eventi kaydet
            self.pinch_events.append((current_time, False))

            # Eski eventleri temizle (1.0 saniyeden eski)
            self.pinch_events = [e for e in self.pinch_events
                                 if current_time - e[0] < 1.0]

            print(f"🔢 Stabil click eventleri: {len(self.pinch_events)}")

            # CLICK BELİRLEME - Geliştirilmiş
            action = None
            confidence = 0.95

            # 1.0 saniye içinde 2+ click = SAĞ TIK
            if len(self.pinch_events) >= 2:
                action = "right_click"
                print(f"👍 SAĞ TIK algılandı ({len(self.pinch_events)} stabil click)")
                self.pinch_events = []  # Temizle

            # Tek click = SOL TIK
            else:
                action = "left_click"
                print("👆 SOL TIK algılandı (tek stabil click)")

            if action:
                result.update({
                    'type': 'click',
                    'action': action,
                    'confidence': confidence,
                    'stable': True
                })
                self.last_action_time = current_time

        # 5. WIN TUŞU + APP SEÇME SİSTEMİ - Değişiklik yok
        extended_fingers = self._count_extended_fingers(landmarks)
        current_pose = "fist" if extended_fingers <= 1 else ("open" if extended_fingers >= 4 else "partial")

        # Win tuşu mantığı
        if (self.prev_hand_pose == "fist" and current_pose == "open" and
                current_time - self.last_win_time > 1.0):

            # İlk açılma = Win menüsü aç
            if not getattr(self, 'win_menu_open', False):
                result.update({
                    'type': 'system',
                    'action': 'win_key',
                    'confidence': 0.9,
                    'stable': True
                })
                self.win_menu_open = True
                self.win_open_time = current_time
                print("✊→✋ WIN MENÜSÜ açıldı")

        elif (current_pose == "fist" and self.prev_hand_pose == "open" and
              getattr(self, 'win_menu_open', False)):

            # İkinci kapanma = App seç ve aç
            if current_time - getattr(self, 'win_open_time', 0) > 0.5:

                # El pozisyonuna göre app seçimi
                hand_center_x = (thumb[0] + index[0] + middle[0]) / 3
                app_selection = self._select_app_by_position(hand_center_x)

                result.update({
                    'type': 'system',
                    'action': 'open_app',
                    'confidence': 0.9,
                    'data': {'app': app_selection},
                    'stable': True
                })

                self.win_menu_open = False
                self.last_win_time = current_time
                print(f"✊ APP SEÇİLDİ: {app_selection}")

        # Win menüsü timeout (3 saniye)
        if (getattr(self, 'win_menu_open', False) and
                current_time - getattr(self, 'win_open_time', 0) > 3.0):
            self.win_menu_open = False
            print("⏰ Win menüsü timeout")

        # State güncellemeleri
        self.prev_pinch = is_pinch
        self.prev_drag_grip = is_drag_grip
        self.prev_hand_pose = current_pose

        return result

    def _select_app_by_position(self, hand_x: float) -> str:
        """El pozisyonuna göre uygulama seçimi"""
        # Ekranı 5 bölgeye ayır
        if hand_x < 0.2:
            return "firefox"  # Web browser
        elif hand_x < 0.4:
            return "code"  # VS Code
        elif hand_x < 0.6:
            return "nautilus"  # File manager
        elif hand_x < 0.8:
            return "gnome-terminal"  # Terminal
        else:
            return "gnome-calculator"  # Calculator

    def should_execute_action(self, gesture_type: str, action: str,
                              confidence: float = 0.0, stable: bool = False) -> bool:
        """Eylem yürütme onayı - basit"""
        return confidence >= 0.8  # Sadece güven kontrolü

    def get_calibration_status(self) -> Dict[str, Any]:
        """Kalibrasyon durumu"""
        auto_cal_params = self.auto_calibrator.get_calibration_parameters()
        cursor_stats = self.smart_cursor.get_stats()

        return {
            'is_calibrated': self.is_calibrated,
            'hand_size': self.hand_size,
            'pinch_threshold': self.pinch_threshold,
            'movement_threshold': self.movement_threshold,
            'auto_calibration': auto_cal_params,
            'cursor_stats': cursor_stats,
            'frames_processed': self.frame_count
        }

    def reset_calibration(self):
        """Kalibrasyon sıfırla"""
        self.is_calibrated = False
        self.hand_size = None
        self.pinch_events = []
        self.auto_calibration_frames = 0

        # Akıllı sistemleri sıfırla
        self.auto_calibrator = AutoCalibrator()
        self.smart_cursor.reset()

        print("🔄 Akıllı kalibrasyon sistemi sıfırlandı")

    def get_performance_stats(self) -> Dict[str, Any]:
        """Performans istatistikleri"""
        return {
            'total_frames': self.frame_count,
            'auto_calibration_frames': self.auto_calibration_frames,
            'calibration_complete': self.is_calibrated,
            'cursor_filter_stats': self.smart_cursor.get_stats()
        }
