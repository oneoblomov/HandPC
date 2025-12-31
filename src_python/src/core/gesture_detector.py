import math
import time
from typing import Dict, Tuple, Any
import json

# Import sorununu çozmek için absolute import kullan
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from utils.smoothing_filters import AutoCalibrator, SmartCursor
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
    from smoothing_filters import AutoCalibrator, SmartCursor


class GestureDetector:
    """ULTRA OPTİMİZE GESTİCR DETECTOR - Akilli filtreleme ve otomatik kalibrasyon"""

    def __init__(self, config_path: str = "config/gesture_map.json"):
        self.config = self._load_config(config_path)

        # Yeni akilli sistemler
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

        print("Akilli Gesture Detector başlatildi - Otomatik kalibrasyon aktif")

    def _load_config(self, config_path: str) -> Dict:
        """Konfigurasyon dosyasini yukle"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"settings": {"click_cooldown": 0.2}}

    def calibrate_hand(self, landmarks) -> bool:
        """Akilli otomatik kalibrasyon"""
        if self.is_calibrated:
            return True

        # Otomatik kalibrasyon başlatilmamişsa başlat
        if not self.auto_calibrator.is_calibrating:
            self.auto_calibrator.start_calibration()

        # Kalibrasyon orneği ekle
        calibration_complete = self.auto_calibrator.add_calibration_sample(landmarks)

        if calibration_complete:
            # Kalibrasyon parametrelerini al
            params = self.auto_calibrator.get_calibration_parameters()

            if params['is_calibrated']:
                self.hand_size = params['hand_size']
                self.pinch_threshold = self.auto_calibrator.get_pinch_threshold()
                self.movement_threshold = self.auto_calibrator.get_movement_threshold()
                self.is_calibrated = True

                # Smart cursor'a hassasiyet ayarlarini aktar
                self.smart_cursor.sensitivity_x = params['sensitivity_multiplier']
                self.smart_cursor.sensitivity_y = params['sensitivity_multiplier']

                print("[✓] Akilli kalibrasyon tamamlandi!")
                print(f"   El boyutu: {self.hand_size:.3f}")
                print(f"   Pinch eşiği: {self.pinch_threshold:.3f}")
                print(f"   Hareket eşiği: {self.movement_threshold:.3f}")
                print(f"   ⚡ Hassasiyet: {params['sensitivity_multiplier']:.2f}")

                return True

        return False

    def _distance(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """İki nokta arasi mesafe"""
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

    def _is_intentional_movement(self, movement_magnitude: float) -> bool:
        """Hareketin kasitli olup olmadiğini kontrol et"""
        return movement_magnitude > self.movement_threshold

    def _is_precise_area(self, cursor_pos: Tuple[float, float]) -> bool:
        """Cursor hassas alanda mi? (menuler, butonlar vs.)"""
        # Bu basit implementasyon - geliştirilmesi gerekebilir
        x, y = cursor_pos
        # Ekran kenarlari ve koşeler hassas kabul edilir
        return x < 100 or x > 1820 or y < 100 or y > 980

    def _count_extended_fingers(self, landmarks) -> int:
        """Uzatilmiş parmak sayisi"""
        if not self.hand_size:
            return 0  # Kalibrasyon yapilmamiş

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
        """YENİ AKILLI GESTURE SİSTEMİ - Titreme onleyici ve otomatik optimize"""

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

        # Akilli cursor pozisyonu hesapla (titreme filtreli)
        cursor_pos = self.smart_cursor.process_movement(
            index[0], index[1], 1920, 1080  # Varsayilan çozunurluk
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
            # Drag başladi - stabilite kontrolu
            print("✋ DRAG (Tutma) başladi - titreme korumali")
            result.update({
                'type': 'drag',
                'action': 'drag_start',
                'confidence': 0.95,
                'stable': True
            })
            self.last_action_time = current_time

        elif not is_drag_grip and getattr(self, 'prev_drag_grip', False):
            # Drag bitti
            print("DRAG (Tutma) bitti")
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

        # 4. CLICK İŞLEMLERİ - Geliştirilmiş titreme kontrolu
        elif is_pinch and not self.prev_pinch and not is_drag_grip:
            # Normal pinch başladi - başlangiç değerlerini kaydet
            self.pinch_start_distance = pinch_distance
            self.pinch_start_time = current_time
            if self._is_intentional_movement(pinch_distance):
                print(f"Kasitli click pinch başladi (mesafe: {pinch_distance:.3f})")

        elif not is_pinch and self.prev_pinch and not is_drag_grip:
            # Pinch bitti - click eventi

            # Gelişmiş cooldown kontrolu
            min_cooldown = 0.1 if self._is_precise_area(cursor_pos) else 0.15
            if current_time - self.last_action_time < min_cooldown:
                print("⏱️ Click çok hizli - titreme korumasi aktif")
                self.prev_pinch = is_pinch
                self.prev_drag_grip = is_drag_grip
                return result

            # Titreme kontrolu - pinch açilma mesafesi
            is_valid_click = True
            if hasattr(self, 'pinch_start_distance'):
                # Pinch açilma mesafesi kontrolu
                open_distance = pinch_distance - self.pinch_start_distance
                if abs(open_distance) < self.movement_threshold:
                    print(f"Titreme algilandi - click iptal edildi (açilma: {open_distance:.3f})")
                    is_valid_click = False
            else:
                # Fallback - basit mesafe kontrolu
                if pinch_distance < self.pinch_threshold + self.movement_threshold:
                    print("Titreme algilandi - click iptal edildi (fallback)")
                    is_valid_click = False

            if not is_valid_click:
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
                print(f"SAĞ TIK algilandi ({len(self.pinch_events)} stabil click)")
                self.pinch_events = []  # Temizle

            # Tek click = SOL TIK
            else:
                action = "left_click"
                print("SOL TIK algilandi (tek stabil click)")

            if action:
                result.update({
                    'type': 'click',
                    'action': action,
                    'confidence': confidence,
                    'stable': True
                })
                self.last_action_time = current_time

        # 5. WIN TUŞU + APP SEÇME SİSTEMİ - Win menusu aç ve fare imleci konumlandir
        extended_fingers = self._count_extended_fingers(landmarks)
        current_pose = "fist" if extended_fingers <= 1 else ("open" if extended_fingers >= 4 else "partial")

        # Win tuşu mantiği
        if (self.prev_hand_pose == "fist" and current_pose == "open" and
                current_time - self.last_win_time > 1.0):

            # İlk açilma = Win menusu aç ve fare imleci konumlandir
            if not getattr(self, 'win_menu_open', False):
                # Elin orta kismina gore fare imleci konumlandir
                hand_center_x = (thumb[0] + index[0] + middle[0]) / 3
                hand_center_y = (thumb[1] + index[1] + middle[1]) / 3

                # Win menusu için cursor pozisyonunu guncelle
                win_cursor_pos = self.smart_cursor.process_movement(
                    hand_center_x, hand_center_y, 1920, 1080
                )

                result.update({
                    'type': 'system',
                    'action': 'win_key',
                    'confidence': 0.9,
                    'stable': True,
                    'cursor_pos': win_cursor_pos  # Win menusunde imleç konumlandir
                })
                self.win_menu_open = True
                self.win_open_time = current_time
                print("WIN MENuSu açildi - fare imleci konumlandirildi")

        elif (current_pose == "fist" and self.prev_hand_pose == "open" and
              getattr(self, 'win_menu_open', False)):

            # İkinci kapanma = Sol tiklama ile uygulama seç
            if current_time - getattr(self, 'win_open_time', 0) > 0.5:
                result.update({
                    'type': 'click',
                    'action': 'left_click',
                    'confidence': 0.9,
                    'stable': True
                })

                self.win_menu_open = False
                self.last_win_time = current_time
                print("SOL TIKLAMA - uygulama seçildi")

        # Win menusu timeout (3 saniye)
        if (getattr(self, 'win_menu_open', False) and
                current_time - getattr(self, 'win_open_time', 0) > 3.0):
            self.win_menu_open = False
            print("Win menusu timeout")

        # State guncellemeleri
        self.prev_pinch = is_pinch
        self.prev_drag_grip = is_drag_grip
        self.prev_hand_pose = current_pose

        return result

    def _select_app_by_position(self, hand_x: float) -> str:
        """El pozisyonuna gore uygulama seçimi"""
        # Ekrani 5 bolgeye ayir
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
        """Eylem yurutme onayi - basit"""
        return confidence >= 0.8  # Sadece guven kontrolu

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
        """Kalibrasyon sifirla"""
        self.is_calibrated = False
        self.hand_size = None
        self.pinch_events = []
        self.auto_calibration_frames = 0

        # Akilli sistemleri sifirla
        self.auto_calibrator = AutoCalibrator()
        self.smart_cursor.reset()

        print(" Akilli kalibrasyon sistemi sifirlandi")

    def get_performance_stats(self) -> Dict[str, Any]:
        """Performans istatistikleri"""
        return {
            'total_frames': self.frame_count,
            'auto_calibration_frames': self.auto_calibration_frames,
            'calibration_complete': self.is_calibrated,
            'cursor_filter_stats': self.smart_cursor.get_stats()
        }
