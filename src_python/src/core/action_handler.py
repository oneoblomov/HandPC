import pyautogui
import subprocess
import time
from typing import Dict, Any


class ActionHandler:
    """Geliştirilmiş gesture eylemlerini gerçekleştiren modul"""

    def __init__(self):
        self.is_disabled = False
        self.cursor_frozen = False
        self.drag_mode = False
        self.drag_start_pos = None
        self.safe_mode = True  # Guvenli mod (yanlişlikla eylemleri onler)

        # PyAutoGUI ayarlari - Fail-safe'i tamamen devre dişi birak
        pyautogui.FAILSAFE = False  # Fail-safe'i kapatiyoruz
        pyautogui.PAUSE = 0.01  # Çok kisa pause

        # Kendi guvenlik kontrolleri
        self.screen_width, self.screen_height = pyautogui.size()
        self.safe_margin = 50  # Daha buyuk guvenli mesafe (50 piksel)

        # Eylem geçmişi
        self.action_history = []
        self.last_action_time = {}

        # Guvenlik ayarlari
        self.min_action_interval = 0.3  # Minimum eylem arasi sure
        self.max_actions_per_second = 3
        self.recent_actions = []

    def enable_safe_mode(self, enabled: bool = True):
        """Guvenli modu etkinleştir/devre dişi birak"""
        self.safe_mode = enabled
        status = "etkinleştirildi" if enabled else "devre dişi birakildi"
        print(f"Guvenli mod {status}")

    def _is_action_safe(self, action: str) -> bool:
        """Eylemin guvenli olup olmadiğini kontrol et"""
        current_time = time.time()

        # Son 1 saniyedeki eylemleri temizle
        self.recent_actions = [t for t in self.recent_actions if current_time - t < 1.0]

        # Çok fazla eylem var mi?
        if len(self.recent_actions) >= self.max_actions_per_second:
            print(f"⚠ Çok fazla eylem algilandi, {action} bloklandi")
            return False

        # Minimum sure kontrolu
        if action in self.last_action_time:
            time_since_last = current_time - self.last_action_time[action]
            if time_since_last < self.min_action_interval:
                return False

        return True

    def _is_position_safe(self, x: float, y: float) -> bool:
        """Pozisyonun guvenli olup olmadiğini kontrol et (ekran kenarlarindan uzak)"""
        # Ekran kenarlarindan guvenli mesafede mi?
        if (x < self.safe_margin or x > self.screen_width - self.safe_margin or
                y < self.safe_margin or y > self.screen_height - self.safe_margin):
            print(f"⚠ Ekran kenarinda işlem engellendi (x:{x:.0f}, y:{y:.0f}) - margin:{self.safe_margin}")
            return False
        return True

    def _record_action(self, action: str, success: bool):
        """Eylem geçmişini kaydet"""
        current_time = time.time()
        self.last_action_time[action] = current_time

        if success:
            self.recent_actions.append(current_time)
            self.action_history.append({
                'action': action,
                'time': current_time,
                'success': success
            })

            # Geçmişi sinirla
            if len(self.action_history) > 100:
                self.action_history.pop(0)

    def execute_action(self, gesture_data: Dict[str, Any], cursor_pos: tuple) -> bool:
        """Algilanan gesture'a gore eylemi gerçekleştir - geliştirilmiş"""
        if self.is_disabled:
            return False

        action = gesture_data.get('action')
        confidence = gesture_data.get('confidence', 0.0)
        stable = gesture_data.get('stable', False)

        if not action:
            return False

        # Guvenlik kontrolleri
        if self.safe_mode and not self._is_action_safe(action):
            return False

        # Guven kontrolu
        if confidence < 0.7:  # Daha yuksek guven eşiği
            return False

        # Stabilite kontrolu
        if not stable and action in ['left_click', 'right_click', 'drag']:
            return False

        success = False

        try:
            # Fare kontrolu eylemleri
            if action == 'left_click':
                success = self._left_click_safe()
            elif action == 'right_click':
                success = self._right_click_safe()
            elif action == 'drag':
                success = self._handle_drag_safe(cursor_pos, gesture_data)
            elif action == 'drag_start':
                success = self._start_drag_safe(cursor_pos)
            elif action == 'drag_move':
                success = self._move_drag_safe(cursor_pos)
            elif action == 'drag_end':
                success = self._end_drag_safe()
            elif action == 'open_app':
                app_name = gesture_data.get('app', 'firefox')
                success = self._open_app_safe(app_name)

            # Kaydirma eylemleri (daha az sinirli)
            elif action in ['scroll_up', 'scroll_down']:
                success = self._scroll_safe(action)

            # Navigasyon eylemleri
            elif action in ['navigate_back', 'navigate_forward']:
                success = self._navigate_safe(action)

            # Zoom eylemleri - GEÇİCİ OLARAK DEVRE DIŞI
            elif action in ['zoom_in', 'zoom_out']:
                print(f"⚠ Zoom işlevi geçici olarak devre dişi: {action}")
                success = False

            # Sistem eylemleri (en guvenli)
            elif action == 'show_applications':
                success = self._show_applications_safe()
            elif action == 'win_key':
                success = self._win_key_safe()
            elif action == 'show_desktop':
                success = self._show_desktop_safe()
            elif action in ['workspace_left', 'workspace_right']:
                success = self._switch_workspace_safe(action)

            # Mod değiştirici eylemleri
            elif action == 'toggle_mode':
                success = self._toggle_disabled_mode()
            elif action == 'freeze_cursor':
                success = self._toggle_cursor_freeze()

        except Exception as e:
            print(f"Eylem gerçekleştirme hatasi ({action}): {e}")
            success = False

        # Eylemi kaydet
        self._record_action(action, success)

        if success and self.safe_mode:
            print(f"✓ Eylem gerçekleştirildi: {action} (guven: {confidence:.2f})")

        return success

    def _left_click_safe(self) -> bool:
        """Guvenli sol tiklama"""
        if not self.cursor_frozen:
            # Mevcut pozisyonu kontrol et
            current_pos = pyautogui.position()

            # Guvenli pozisyon kontrolu
            if not self._is_position_safe(current_pos[0], current_pos[1]):
                return False

            pyautogui.click()
            return True
        return False

    def _right_click_safe(self) -> bool:
        """Guvenli sağ tiklama"""
        if not self.cursor_frozen:
            # Mevcut pozisyonu kontrol et
            current_pos = pyautogui.position()

            # Guvenli pozisyon kontrolu
            if not self._is_position_safe(current_pos[0], current_pos[1]):
                return False

            pyautogui.click(button='right')
            return True
        return False

    def _handle_drag_safe(self, cursor_pos: tuple, gesture_data: Dict[str, Any]) -> bool:
        """Geliştirilmiş surukleme işlemi - yeni gesture sistemi için"""
        if self.cursor_frozen:
            return False

        # Yeni sistemde drag gesture'i tek seferde gelir
        action = gesture_data.get('action')
        if action == 'drag':
            if not self.drag_mode:
                # Surukleme başlat
                self.drag_mode = True
                self.drag_start_pos = cursor_pos
                pyautogui.mouseDown()
                print("🔄 Surukleme başlatildi")
                return True
            else:
                # Zaten surukleme modundaysa (guvenlik için)
                return False
        else:
            # Drag değilse ve drag modundaysak bitir
            if self.drag_mode:
                self.drag_mode = False
                pyautogui.mouseUp()
                print("✓ Surukleme tamamlandi")
                self.drag_start_pos = None
                return True
            return False

    def _end_drag_safe(self) -> bool:
        """Surukleme işlemini sonlandir"""
        if self.drag_mode:
            self.drag_mode = False
            pyautogui.mouseUp()
            print("✓ Surukleme sonlandirildi")
            self.drag_start_pos = None
            return True
        return False

    def _scroll_safe(self, direction: str) -> bool:
        """Guvenli kaydirma"""
        if self.cursor_frozen:
            return False

        scroll_amount = 2  # Daha az agresif
        if direction == 'scroll_up':
            pyautogui.scroll(scroll_amount)
        else:
            pyautogui.scroll(-scroll_amount)
        return True

    def _navigate_safe(self, direction: str) -> bool:
        """Guvenli navigasyon"""
        try:
            if direction == 'navigate_back':
                pyautogui.hotkey('alt', 'left')
            else:
                pyautogui.hotkey('alt', 'right')
            return True
        except Exception:
            return False

    def _zoom_safe(self, direction: str) -> bool:
        """Guvenli yakinlaştirma"""
        try:
            if direction == 'zoom_in':
                pyautogui.hotkey('ctrl', 'plus')
            else:
                pyautogui.hotkey('ctrl', 'minus')
            return True
        except Exception:
            return False

    def _show_applications_safe(self) -> bool:
        """Guvenli uygulama geçişi"""
        try:
            pyautogui.hotkey('super', 'tab')
            return True
        except Exception:
            try:
                pyautogui.hotkey('alt', 'tab')
                return True
            except Exception:
                return False

    def _win_key_safe(self) -> bool:
        """Guvenli Windows tuşu (uygulama listesi)"""
        try:
            # Windows/Meta tuşunu gonder
            pyautogui.press('win')
            return True
        except Exception:
            try:
                # Alternatif olarak Super tuşu
                pyautogui.press('super')
                return True
            except Exception:
                return False

    def _show_desktop_safe(self) -> bool:
        """Guvenli masaustu gosterimi"""
        try:
            pyautogui.hotkey('super', 'd')
            return True
        except Exception:
            try:
                pyautogui.hotkey('ctrl', 'alt', 'd')
                return True
            except Exception:
                return False

    def _switch_workspace_safe(self, direction: str) -> bool:
        """Guvenli çalişma alani değişimi"""
        try:
            if direction == 'workspace_left':
                pyautogui.hotkey('ctrl', 'alt', 'left')
            else:
                pyautogui.hotkey('ctrl', 'alt', 'right')
            return True
        except Exception:
            return False

    def _toggle_disabled_mode(self) -> bool:
        """Gesture kontrolunu geçici olarak devre dişi birak"""
        self.is_disabled = not self.is_disabled
        status = "devre dişi" if self.is_disabled else "etkin"
        print(f"🔄 Gesture kontrolu {status}")
        return True

    def _toggle_cursor_freeze(self) -> bool:
        """İmleci dondur/çoz"""
        self.cursor_frozen = not self.cursor_frozen
        status = "donduruldu" if self.cursor_frozen else "serbest"
        print(f"🔒 İmleç {status}")
        return True

    def move_cursor(self, x: float, y: float, pinch_active: bool = False, smoothing: float = 0.3) -> bool:
        """İmleci hareket ettir - SADECE pinch aktifken hareket eder"""
        if self.is_disabled or self.cursor_frozen:
            return False

        # SADECE baş parmak + işaret parmaği birleşik olduğunda hareket et
        if not pinch_active:
            return False

        try:
            current_x, current_y = pyautogui.position()
            screen_w, screen_h = pyautogui.size()

            # Koordinatlari duzgun çevir (0-1 normalized değerlerden piksel koordinatlarina)
            if x <= 1.0 and y <= 1.0:  # Normalized koordinatlar
                target_x = x * screen_w
                target_y = y * screen_h
            else:  # Zaten piksel koordinatlari
                target_x = x
                target_y = y

            # Smoothing uygula
            new_x = current_x + (target_x - current_x) * smoothing
            new_y = current_y + (target_y - current_y) * smoothing

            # Ekran sinirlari içinde tut ve guvenlik kontrolu
            new_x = max(self.safe_margin, min(new_x, screen_w - self.safe_margin))
            new_y = max(self.safe_margin, min(new_y, screen_h - self.safe_margin))

            # Pozisyon guvenli mi kontrol et
            if not self._is_position_safe(new_x, new_y):
                return False

            # Çok buyuk siçramalar engelle
            max_movement = 100  # piksel
            distance = ((new_x - current_x)**2 + (new_y - current_y)**2)**0.5

            if distance > max_movement:
                # Hareketi sinirla
                ratio = max_movement / distance
                new_x = current_x + (new_x - current_x) * ratio
                new_y = current_y + (new_y - current_y) * ratio

            pyautogui.moveTo(new_x, new_y, _pause=False)
            return True
        except Exception as e:
            print(f"İmleç hareket hatasi: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Mevcut durumu dondur"""
        return {
            'disabled': self.is_disabled,
            'cursor_frozen': self.cursor_frozen,
            'drag_mode': self.drag_mode,
            'safe_mode': self.safe_mode,
            'drag_start_pos': self.drag_start_pos,
            'recent_action_count': len(self.recent_actions),
            'last_actions': self.action_history[-5:] if self.action_history else []
        }

    def get_stats(self) -> Dict[str, Any]:
        """İstatistikleri dondur"""
        if not self.action_history:
            return {'total_actions': 0}

        action_counts = {}
        successful_actions = 0

        for action_record in self.action_history:
            action = action_record['action']
            action_counts[action] = action_counts.get(action, 0) + 1
            if action_record['success']:
                successful_actions += 1

        return {
            'total_actions': len(self.action_history),
            'successful_actions': successful_actions,
            'success_rate': successful_actions / len(self.action_history) * 100,
            'action_breakdown': action_counts,
            'recent_actions_per_minute': len(self.recent_actions) * 60
        }

    def _start_drag_safe(self, cursor_pos: tuple) -> bool:
        """Drag başlatma - guvenli"""
        try:
            if self.drag_mode:
                return True  # Zaten drag modunda

            # Pozisyon guvenli mi kontrol et
            if not self._is_position_safe(cursor_pos[0], cursor_pos[1]):
                return False

            self.drag_mode = True
            self.drag_start_pos = cursor_pos

            # Mouse tuşunu basili tut
            pyautogui.mouseDown()
            print(f"🔒 Drag başlatildi pozisyon: {cursor_pos}")
            return True

        except Exception as e:
            print(f"Drag başlatma hatasi: {e}")
            self.drag_mode = False
            return False

    def _move_drag_safe(self, cursor_pos: tuple) -> bool:
        """Drag hareket ettirme - guvenli"""
        try:
            if not self.drag_mode:
                return False

            # Drag sirasinda imleç hareketi
            x, y = cursor_pos
            screen_w, screen_h = pyautogui.size()

            # Koordinat kontrolu - normalized mi yoksa piksel mi?
            if x <= 1.0 and y <= 1.0:  # Normalized koordinatlar
                screen_x = int(x * screen_w)
                screen_y = int(y * screen_h)
            else:  # Zaten piksel koordinatlari
                screen_x = int(x)
                screen_y = int(y)

            # Guvenli sinirlari kontrol et - daha buyuk margin
            screen_x = max(self.safe_margin, min(screen_x, screen_w - self.safe_margin))
            screen_y = max(self.safe_margin, min(screen_y, screen_h - self.safe_margin))

            # Pozisyon guvenli mi kontrol et
            if not self._is_position_safe(screen_x, screen_y):
                print(f"⚠ Drag hareketi guvenli değil: x={screen_x}, y={screen_y}")
                return False

            # Mevcut pozisyondan çok uzaksa hareketi sinirla
            current_x, current_y = pyautogui.position()
            max_drag_distance = 200  # piksel
            distance = ((screen_x - current_x)**2 + (screen_y - current_y)**2)**0.5

            if distance > max_drag_distance:
                # Hareketi sinirla
                ratio = max_drag_distance / distance
                screen_x = current_x + int((screen_x - current_x) * ratio)
                screen_y = current_y + int((screen_y - current_y) * ratio)

            # Fareyi surukleyerek hareket ettir
            pyautogui.moveTo(screen_x, screen_y, _pause=False)
            return True

        except Exception as e:
            print(f"Drag hareket hatasi: {e}")
            return False

    def _open_app_safe(self, app_name: str) -> bool:
        """Uygulama açma - guvenli"""
        try:
            # Uygulama mapping
            app_commands = {
                'firefox': 'firefox',
                'code': 'code',
                'nautilus': 'nautilus',
                'gnome-terminal': 'gnome-terminal',
                'gnome-calculator': 'gnome-calculator'
            }

            command = app_commands.get(app_name, app_name)

            # Uygulamayi çaliştir
            subprocess.Popen([command],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)

            print(f"📱 Uygulama açildi: {app_name}")
            return True

        except Exception as e:
            print(f"Uygulama açma hatasi ({app_name}): {e}")
            return False
