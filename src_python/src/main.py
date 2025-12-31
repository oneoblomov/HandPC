import cv2
import mediapipe as mp
import pyautogui
import time
import math
import json
import os
import argparse
from typing import Optional, Dict, Any

from core.gesture_detector import GestureDetector
from core.action_handler import ActionHandler

mp_hands = mp.solutions.hands  # type: ignore
mp_drawing = mp.solutions.drawing_utils  # type: ignore

try:
    SCREEN_W, SCREEN_H = pyautogui.size()
except Exception as e:
    SCREEN_W, SCREEN_H = 0, 0
    print(f"[WARN] pyautogui.size() failed: {e}")


class GestureControlSystem:
    """Ana gesture kontrol sistemi"""

    def __init__(self, config_path: str = "config/gesture_map.json", settings_override: Optional[Dict] = None):
        # Environment variables'dan ayarları al (oncelik: env vars > settings_override > config file > defaults)
        self.settings = self._load_settings_from_env(settings_override)

        self.detector = GestureDetector(config_path)
        self.action_handler = ActionHandler()

        # Config dosyasini da yukle (eski uyumluluk için)
        self.config = self._load_config(config_path)

        # Mevcut durumu takip etmek için
        self.prev_cursor_x = 0.0
        self.prev_cursor_y = 0.0
        self.last_gesture_time = 0.0

        # Ayarlari yukle - environment'dan gelen ayarlari kullan
        self.smoothing = self.settings.get('smoothing_factor', 0.3)
        self.sensitivity = self.settings.get('sensitivity', {})

        # Kullanici dostu ozellikler - environment'dan alinan ayarlar
        self.show_help = True
        self.calibration_countdown = 0
        self.tutorial_mode = self.settings.get('tutorial_mode', False)
        self.debug_mode = self.settings.get('debug_mode', False)

        # Guvenlik ayarlari
        self.safe_mode = self.settings.get('safe_mode', True)
        self.auto_calibrate = self.settings.get('auto_calibrate', True)

        # Kamera ayarlari
        self.camera_index = self.settings.get('camera_index', 0)
        self.camera_fps = self.settings.get('camera_fps', 30)

        # Hassasiyet ayarlari
        self.pinch_threshold = self.settings.get('pinch_threshold', 0.05)
        self.confidence_minimum = self.settings.get('confidence_minimum', 0.7)
        self.click_cooldown = self.settings.get('click_cooldown', 0.3)

        # İstatistikler
        self.frame_count = 0
        self.gesture_count = 0
        self.successful_actions = 0

        # Ayarlari uygula
        self._apply_settings()

    def _load_settings_from_env(self, settings_override: Optional[Dict] = None) -> Dict:
        """Environment variables'dan ayarlari yukle"""
        settings = {}

        # once varsayilan değerleri ayarla
        defaults = {
            'tutorial_mode': False,
            'safe_mode': True,
            'auto_calibrate': True,
            'smoothing_factor': 0.3,
            'pinch_threshold': 0.05,
            'confidence_minimum': 0.7,
            'click_cooldown': 0.3,
            'camera_index': 0,
            'camera_fps': 30,
            'max_actions_per_second': 3,
            'screen_edge_margin': 50,
            'show_notifications': True,
            'log_level': 'INFO',
            'debug_mode': False,
            'sensitivity': {'movement': 1.0, 'pinch_detection': 1.0}
        }

        # Environment variables'i kontrol et
        env_mappings = {
            'HCI_TUTORIAL_MODE': ('tutorial_mode', bool),
            'HCI_SAFE_MODE': ('safe_mode', bool),
            'HCI_AUTO_CALIBRATE': ('auto_calibrate', bool),
            'HCI_SMOOTHING_FACTOR': ('smoothing_factor', float),
            'HCI_PINCH_THRESHOLD': ('pinch_threshold', float),
            'HCI_CONFIDENCE_MINIMUM': ('confidence_minimum', float),
            'HCI_CLICK_COOLDOWN': ('click_cooldown', float),
            'HCI_CAMERA_INDEX': ('camera_index', int),
            'HCI_CAMERA_FPS': ('camera_fps', int),
            'HCI_MAX_ACTIONS_PER_SECOND': ('max_actions_per_second', int),
            'HCI_SCREEN_EDGE_MARGIN': ('screen_edge_margin', int),
            'HCI_SHOW_NOTIFICATIONS': ('show_notifications', bool),
            'HCI_LOG_LEVEL': ('log_level', str),
            'HCI_DEBUG_MODE': ('debug_mode', bool),
        }

        for env_var, (setting_key, value_type) in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                try:
                    if value_type == bool:
                        defaults[setting_key] = env_value.lower() in ('true', '1', 'yes', 'on')
                    elif value_type == int:
                        defaults[setting_key] = int(env_value)
                    elif value_type == float:
                        defaults[setting_key] = float(env_value)
                    else:
                        defaults[setting_key] = env_value
                    print(f"Environment variable {env_var} = {defaults[setting_key]}")
                except (ValueError, TypeError) as e:
                    print(f"Environment variable {env_var} geçersiz değer: {env_value} ({e})")

        return defaults

    def _apply_settings(self):
        """Ayarlari ilgili bileşenlere uygula"""
        # Tutorial modunu etkinleştir
        if self.tutorial_mode:
            self.enable_tutorial_mode()

        # Guvenli modu ayarla
        self.action_handler.enable_safe_mode(self.safe_mode)

        # Debug modu
        if self.debug_mode:
            print("Debug modu etkinleştirildi")

        # Log seviyesi
        if self.settings.get('log_level') == 'DEBUG':
            self.debug_mode = True

        print("Ayarlar yuklendi:")
        print(f"   Tutorial modu: {self.tutorial_mode}")
        print(f"   Guvenli mod: {self.safe_mode}")
        print(f"   Otomatik kalibrasyon: {self.auto_calibrate}")
        print(f"   Smoothing: {self.smoothing}")
        print(f"   Kamera: {self.camera_index} @ {self.camera_fps}fps")
        print(f"   Guven seviyesi: {self.confidence_minimum}")

    def get_settings(self) -> Dict:
        """Mevcut ayarlari dondur"""
        return self.settings.copy()

    def _load_config(self, config_path: str) -> Dict:
        """Konfigurasyon dosyasini yukle"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Konfigurasyon dosyasi bulunamadi: {config_path}")
            return {"settings": {"smoothing": 0.3}}

    def start_calibration(self):
        """Kalibrasyon surecini başlat"""
        print("\nEl kalibrasyonu başlatiliyor...")
        print("Lutfen elinizi kameranin onunde doğal pozisyonda tutun")
        print("3 saniye içinde kalibrasyon başlayacak...")
        self.calibration_countdown = 90  # 3 saniye x 30 FPS
        self.detector.reset_calibration()

    def enable_tutorial_mode(self):
        """Tutorial modunu etkinleştir"""
        self.tutorial_mode = True
        print("\nTutorial modu etkinleştirildi")
        print("Gesture'lari deneyip nasil çaliştiğini gorebilirsiniz")
        print("Gerçek eylemler çaliştirilmayacak")
        self.action_handler.enable_safe_mode(True)

    def _calculate_cursor_position(self, landmarks) -> tuple:
        """İşaret parmağindan cursor pozisyonunu hesapla - akilli filtreleme"""
        index_finger = landmarks[8]

        # Ham koordinatlar
        raw_x = index_finger.x
        raw_y = index_finger.y

        # Gesture detector'dan filtrelenmiş pozisyonu al
        gesture_info = self.detector.detect_gesture(landmarks)

        if 'cursor_pos' in gesture_info:
            return gesture_info['cursor_pos']

        # Fallback - manuel hesaplama
        screen_x = raw_x * (SCREEN_W or 1920)
        screen_y = raw_y * (SCREEN_H or 1080)

        # Basit yumuşatma (legacy)
        smoothing_factor = self.smoothing
        new_x = self.prev_cursor_x + (screen_x - self.prev_cursor_x) * smoothing_factor
        new_y = self.prev_cursor_y + (screen_y - self.prev_cursor_y) * smoothing_factor

        self.prev_cursor_x, self.prev_cursor_y = new_x, new_y
        return (new_x, new_y)

    def _draw_calibration_overlay(self, frame):
        """Kalibrasyon için overlay çiz"""
        h, w, _ = frame.shape

        if self.calibration_countdown > 0:
            # Geri sayim goster
            countdown_sec = self.calibration_countdown // 30
            cv2.putText(frame, f"Kalibrasyon: {countdown_sec + 1}",
                        (w // 2 - 100, h // 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)

            # Hedef alan çiz
            center_x, center_y = w // 2, h // 2
            cv2.rectangle(frame, (center_x - 100, center_y - 100),
                          (center_x + 100, center_y + 100), (0, 255, 255), 2)
            cv2.putText(frame, "Elinizi burada tutun",
                        (center_x - 80, center_y + 130), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    def _draw_visual_feedback(self, frame, landmarks, cursor_pos: tuple, gesture_info: Dict):
        """Gelişmiş gorsel geri bildirim - akilli sistem bilgileri"""
        h, w, _ = frame.shape

        # Kalibrasyon overlay'i
        if self.calibration_countdown > 0:
            self._draw_calibration_overlay(frame)
            return

        # El landmark'larini çiz
        if mp_drawing and mp_hands:
            mp_drawing.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)

        # İşaret parmaği pozisyonu (mavi)
        index_finger = landmarks.landmark[8]
        cam_x, cam_y = int(index_finger.x * w), int(index_finger.y * h)
        cv2.circle(frame, (cam_x, cam_y), 8, (255, 0, 0), -1)

        # Filtrelenmiş cursor pozisyonu (yeşil)
        if 'cursor_pos' in gesture_info:
            filter_x, filter_y = gesture_info['cursor_pos']
            vis_filter_x = int((filter_x / (SCREEN_W or w)) * w)
            vis_filter_y = int((filter_y / (SCREEN_H or h)) * h)
            cv2.circle(frame, (vis_filter_x, vis_filter_y), 6, (0, 255, 0), -1)

        # Gesture durumunu goster
        status_y = 30

        # Kalibrasyon durumu - geliştirilmiş
        cal_status = self.detector.get_calibration_status()
        if cal_status['is_calibrated']:
            cv2.putText(frame, f"✓ Akilli kalibrasyon (boyut: {cal_status.get('hand_size', 0):.3f})", (10, status_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        else:
            progress = (cal_status.get('frames_processed', 0) / 90) * 100
            cv2.putText(frame, f"⏳ Otomatik kalibrasyon: {progress:.0f}%", (10, status_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        status_y += 20

        # Pinch durumu - detayli
        if gesture_info.get('pinch_active', False):
            pinch_dist = gesture_info.get('raw_pinch_distance', 0)
            pinch_thresh = gesture_info.get('pinch_threshold', 0)
            cv2.putText(frame, f"Pinch aktif ({pinch_dist:.3f} < {pinch_thresh:.3f})", (10, status_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
            status_y += 20

        # Mevcut gesture
        if gesture_info.get('action'):
            confidence = gesture_info.get('confidence', 0)
            stable = "OK" if gesture_info.get('stable', False) else "NO"

            action_text = f"Gesture: {gesture_info['action']} ({confidence:.2f})"
            cv2.putText(frame, action_text, (10, status_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
            status_y += 20

        # Sistem durumu
        system_status = self.action_handler.get_status()
        if system_status['disabled']:
            cv2.putText(frame, "DEVRE DIŞI", (10, status_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            status_y += 30

        if system_status['safe_mode']:
            cv2.putText(frame, "GUVENLI MOD", (10, status_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            status_y += 25

        if system_status['cursor_frozen']:
            cv2.putText(frame, "İMLEÇ DONDURULDU", (10, status_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
            status_y += 25

        if system_status['drag_mode']:
            cv2.putText(frame, "SuRuKLEME MODU", (10, status_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            status_y += 25

        # Tutorial modu
        if self.tutorial_mode:
            cv2.putText(frame, "TUTORIAL MODU - Eylemler çaliştirilmiyor",
                        (10, status_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
            status_y += 20

        # Performans istatistikleri (debug modu)
        if self.debug_mode:
            perf_stats = self.detector.get_performance_stats()
            cv2.putText(frame, f"İşlenen frame: {perf_stats['total_frames']}",
                        (10, h - 80), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

            cursor_stats = perf_stats.get('cursor_filter_stats', {})
            if cursor_stats.get('total_movements', 0) > 0:
                filter_rate = cursor_stats.get('filter_rate', 0) * 100
                cv2.putText(frame, f"Filtreleme orani: {filter_rate:.1f}%",
                            (10, h - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

        # Yardim metni
        if self.show_help:
            help_y = h - 40
            cv2.putText(frame, 'q: çik | c: kalibre et | h: yardimi gizle | t: tutorial | s: guvenli mod',
                        (10, help_y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            help_y += 15
            cv2.putText(frame, 'f: imleç dondur | d: devre dişi | SPACE: durakla | `: debug',
                        (10, help_y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

    def process_frame(self, frame, landmarks) -> Dict[str, Any]:
        """Bir frame'i işle ve gesture algila - optimize edilmiş"""
        self.frame_count += 1

        # Kalibrasyon geri sayimi (legacy)
        if self.calibration_countdown > 0:
            self.calibration_countdown -= 1
            if self.calibration_countdown == 0:
                print("Manuel kalibrasyon başlatiliyor...")
                self.detector.calibrate_hand(landmarks.landmark)

        # Gesture algila (bu işlem cursor pozisyonunu da hesaplar)
        gesture_info = self.detector.detect_gesture(landmarks.landmark)

        # Filtrelenmiş cursor pozisyonunu al
        cursor_pos = gesture_info.get('cursor_pos', (0, 0))

        # İmleci hareket ettir - SADECE pinch aktifken VE akilli filtreleme ile
        pinch_active = gesture_info.get('pinch_active', False)
        if pinch_active and gesture_info.get('type') != 'calibration':
            self.action_handler.move_cursor(cursor_pos[0], cursor_pos[1], pinch_active, 1.0)

        # Gesture eylemini gerçekleştir
        if gesture_info['action'] and gesture_info.get('type') != 'calibration':
            self.gesture_count += 1

            # Tutorial modunda gerçek eylemleri çaliştirma
            if not self.tutorial_mode:
                should_execute = self.detector.should_execute_action(
                    gesture_info['type'],
                    gesture_info['action'],
                    gesture_info.get('confidence', 0),
                    gesture_info.get('stable', False)
                )

                if should_execute:
                    success = self.action_handler.execute_action(gesture_info, cursor_pos)
                    if success:
                        self.successful_actions += 1
                        self.last_gesture_time = time.time()
            else:
                # Tutorial modunda sadece bilgi goster
                confidence = gesture_info.get('confidence', 0)
                stable = "OK" if gesture_info.get('stable', False) else "NO"
                print(f"Tutorial: {gesture_info['action']} (guven: {confidence:.2f}, stabil: {stable})")

        # Gorsel geri bildirim
        self._draw_visual_feedback(frame, landmarks, cursor_pos, gesture_info)

        return gesture_info

    def handle_keyboard_input(self, key: int) -> bool:
        """Klavye girişlerini işle"""
        if key == ord('q'):
            return False  # Çik
        elif key == ord('c'):
            self.start_calibration()
        elif key == ord('h'):
            self.show_help = not self.show_help
            print(f"Yardim {'gosteriliyor' if self.show_help else 'gizlendi'}")
        elif key == ord('t'):
            self.tutorial_mode = not self.tutorial_mode
            if self.tutorial_mode:
                self.enable_tutorial_mode()
            else:
                print("Tutorial modu kapatildi")
                self.action_handler.enable_safe_mode(True)
        elif key == ord('s'):
            current_safe = self.action_handler.safe_mode
            self.action_handler.enable_safe_mode(not current_safe)
        elif key == ord('f'):
            self.action_handler._toggle_cursor_freeze()
        elif key == ord('d'):
            self.action_handler._toggle_disabled_mode()
        elif key == ord(' '):  # SPACE - durakla
            input("Sistem duraklatildi. Devam etmek için Enter'a basin...")
        elif key == ord('`'):  # Backtick - debug mode
            self.debug_mode = not self.debug_mode
            print(f"Debug modu {'etkin' if self.debug_mode else 'kapali'}")

        return True

    def get_session_stats(self) -> Dict[str, Any]:
        """Oturum istatistiklerini dondur"""
        action_stats = self.action_handler.get_stats()
        return {
            'frames_processed': self.frame_count,
            'gestures_detected': self.gesture_count,
            'successful_actions': self.successful_actions,
            'action_stats': action_stats,
            'calibrated': self.detector.is_calibrated,
            'tutorial_mode': self.tutorial_mode
        }


def _dist(a, b):
    """Backward compatibility için"""
    return math.hypot(a[0] - b[0], a[1] - b[1])


def run(camera_index=0, settings_override: Optional[Dict] = None):
    """Ana çaliştirma fonksiyonu - kullanici dostu versiyon"""

    # MediaPipe kontrolu
    if not mp_hands or not mp_drawing:
        print("[X] MediaPipe bulunamadi. 'pip install mediapipe' komutunu çaliştirin.")
        return

    # Settings override varsa kullan, yoksa camera_index parametresini kullan
    if settings_override is None:
        settings_override = {}

    # Camera index'i ayarlardan al veya parametre olarak kullan
    final_camera_index = settings_override.get('camera_index', camera_index)

    cap = cv2.VideoCapture(final_camera_index)
    if not cap.isOpened():
        print(f"Kamera açilamadi (index: {final_camera_index}).")
        return

    # Ensure window is created from main thread and use a resizable window
    try:
        cv2.namedWindow('Gesture Control - Kullanici Dostu Versiyon', cv2.WINDOW_NORMAL)
        # On some platforms OpenCV/Qt can complain about threads; startWindowThread helps
        cv2.startWindowThread()
    except Exception:
        # non-fatal, continue
        pass

    # Moduler sistemi başlat - ayarlarla birlikte
    gesture_system = GestureControlSystem(settings_override=settings_override)

    # MediaPipe hands modeli - ayarlardan guven seviyesi al
    confidence_level = gesture_system.confidence_minimum

    with mp_hands.Hands(max_num_hands=1,
                        min_detection_confidence=confidence_level,
                        min_tracking_confidence=confidence_level) as hands:

        # Otomatik kalibrasyon oner - ayarlardan kontrol et
        if gesture_system.auto_calibrate:
            print("\nOtomatik kalibrasyon başlatiliyor...")
            gesture_system.start_calibration()
        else:
            print("\nOtomatik kalibrasyon devre dişi. 'c' tuşu ile manuel kalibrasyon yapabilirsiniz.")

        frame_count = 0
        start_time = time.time()
        target_fps = gesture_system.camera_fps

        while True:
            ok, frame = cap.read()
            if not ok:
                print("Kamera verisi alinamadi")
                break

            # Aynayi çevir
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # El algilama
            results = hands.process(rgb)

            if results.multi_hand_landmarks:
                for landmarks in results.multi_hand_landmarks:
                    # Frame'i işle ve gesture algila
                    gesture_info = gesture_system.process_frame(frame, landmarks)
            else:
                # El algilanmadiğinda bilgi goster
                h, w, _ = frame.shape
                cv2.putText(frame, "El algilanmadi - Elinizi kameranin onune getirin",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

                # Kalibrasyon durumunda yardim goster
                if gesture_system.calibration_countdown > 0:
                    gesture_system._draw_calibration_overlay(frame)

            # FPS hesapla ve goster
            frame_count += 1
            if frame_count % 30 == 0:  # Her 30 frame'de bir guncelle
                elapsed = time.time() - start_time
                fps = frame_count / elapsed
                cv2.putText(frame, f"FPS: {fps:.1f}", (frame.shape[1] - 100, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            # Frame'i goster
            cv2.imshow('Gesture Control - Kullanici Dostu Versiyon', frame)

            # Klavye girişi kontrolu
            key = cv2.waitKey(1) & 0xFF
            if not gesture_system.handle_keyboard_input(key):
                break

    # Kapaniş istatistikleri
    cap.release()
    cv2.destroyAllWindows()

# Eski run fonksiyonu için backward compatibility


def run_legacy(camera_index=0):
    """Eski basit implementasyon (backward compatibility)"""

    # MediaPipe kontrolu
    if not mp_hands or not mp_drawing:
        print("[X] MediaPipe bulunamadi. 'pip install mediapipe' komutunu çaliştirin.")
        return

    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print("Kamera açilamadi.")
        return

    prev_x = prev_y = 0.0
    last_click = 0.0

    # Sabit değerler
    SMOOTH = 0.2
    CLICK_DIST = 0.05
    CLICK_COOLDOWN = 0.6

    with mp_hands.Hands(max_num_hands=1,
                        min_detection_confidence=0.6,
                        min_tracking_confidence=0.6) as hands:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = hands.process(rgb)

            if res.multi_hand_landmarks:
                lm = res.multi_hand_landmarks[0].landmark
                idx = (lm[8].x, lm[8].y)
                thumb = (lm[4].x, lm[4].y)
                mid = (lm[12].x, lm[12].y)

                # normalize -> ekran piksel koordinatina çevir
                sx = idx[0] * (SCREEN_W or w)
                sy = idx[1] * (SCREEN_H or h)

                # yumuşak geçiş
                cur_x = prev_x + (sx - prev_x) * SMOOTH
                cur_y = prev_y + (sy - prev_y) * SMOOTH

                try:
                    pyautogui.moveTo(cur_x, cur_y, _pause=False)
                except Exception:
                    # pyautogui/ortam sorunu olabilir; devam et
                    pass

                prev_x, prev_y = cur_x, cur_y

                # gorsel geri bildirim
                cam_x, cam_y = int(idx[0] * w), int(idx[1] * h)
                vis_x = int((cur_x / (SCREEN_W or w)) * w)
                vis_y = int((cur_y / (SCREEN_H or h)) * h)
                cv2.circle(frame, (cam_x, cam_y), 6, (255, 0, 0), -1)   # kamera uzayi
                cv2.circle(frame, (vis_x, vis_y), 6, (0, 0, 255), -1)   # hedef (sistem koordinati projeksiyonu)
                # gerçek fare pozisyonunu da goster (yeşil) — debug amaçli
                try:
                    mx, my = pyautogui.position()
                    if SCREEN_W and SCREEN_H:
                        fmx = int(mx / SCREEN_W * w)
                        fmy = int(my / SCREEN_H * h)
                    else:
                        # SCREEN size bilinmiyorsa, gosterimi hedef noktasina yaklaştir
                        fmx, fmy = vis_x, vis_y
                    cv2.circle(frame, (fmx, fmy), 6, (0, 255, 0), -1)
                    cv2.putText(frame, f'mouse={mx},{my}', (10, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                except Exception:
                    pass

                now = time.time()
                if _dist(idx, thumb) < CLICK_DIST and (now - last_click) > CLICK_COOLDOWN:
                    try:
                        pyautogui.click()
                    except Exception:
                        pass
                    last_click = now

                if _dist(idx, mid) < CLICK_DIST and (now - last_click) > CLICK_COOLDOWN:
                    try:
                        pyautogui.click(button='right')
                    except Exception:
                        pass
                    last_click = now

                if mp_drawing and mp_hands:
                    mp_drawing.draw_landmarks(frame, res.multi_hand_landmarks[0], mp_hands.HAND_CONNECTIONS)

            cv2.putText(frame, 'q: quit', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow('Gesture Control', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()


def parse_args():
    """Komut satiri argumanlarini parse et"""
    parser = argparse.ArgumentParser(description='HCI Gesture Control System')

    # Ana modlar
    parser.add_argument('--legacy', action='store_true', help='Eski basit sistemi kullan')
    parser.add_argument('--camera-index', type=int, default=0, help='Kamera cihaz numarasi (varsayilan: 0)')

    # Ayar parametreleri
    parser.add_argument('--tutorial-mode', action='store_true', help='Tutorial modunu etkinleştir')
    parser.add_argument('--safe-mode', action='store_true', default=True, help='Guvenli modu etkinleştir')
    parser.add_argument('--no-safe-mode', action='store_true', help='Guvenli modu devre dişi birak')
    parser.add_argument('--auto-calibrate', action='store_true', default=True, help='Otomatik kalibrasyonu etkinleştir')
    parser.add_argument('--no-auto-calibrate', action='store_true', help='Otomatik kalibrasyonu devre dişi birak')
    parser.add_argument('--debug', action='store_true', help='Debug modunu etkinleştir')

    # Hassasiyet ayarlari
    parser.add_argument('--smoothing', type=float, default=0.3, help='Cursor yumuşakliği (0.1-0.9)')
    parser.add_argument('--pinch-threshold', type=float, default=0.05, help='Pinch algilama eşiği')
    parser.add_argument('--confidence', type=float, default=0.7, help='Minimum guven seviyesi')
    parser.add_argument('--click-cooldown', type=float, default=0.3, help='Tiklama arasi bekleme suresi')

    # Kamera ayarlari
    parser.add_argument('--fps', type=int, default=30, help='Kamera FPS (15-60)')

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    if args.legacy:
        print("Legacy mode ile başlatiliyor...")
        run_legacy(args.camera_index)
    else:
        # Ayarlari hazirla
        settings_override = {
            'camera_index': args.camera_index,
            'camera_fps': args.fps,
            'tutorial_mode': args.tutorial_mode,
            'safe_mode': args.safe_mode and not args.no_safe_mode,
            'auto_calibrate': args.auto_calibrate and not args.no_auto_calibrate,
            'debug_mode': args.debug,
            'smoothing_factor': args.smoothing,
            'pinch_threshold': args.pinch_threshold,
            'confidence_minimum': args.confidence,
            'click_cooldown': args.click_cooldown,
        }

        print("HCI Gesture Control başlatiliyor...")
        print(f"Ayarlar: Tutorial={args.tutorial_mode}, Safe={settings_override['safe_mode']}, Auto-cal={settings_override['auto_calibrate']}")
        print(f"Kamera: {args.camera_index} @ {args.fps}fps")
        print(f"Hassasiyet: smoothing={args.smoothing}, confidence={args.confidence}")

        # Varsayilan olarak moduler sistemi çaliştir
        run(settings_override=settings_override)
