"""
Gelişmiş yumuşatma ve filtreleme sistemi
El hareketlerindeki titremeleri minimize eder ve daha hassas kontrol sağlar
"""

import numpy as np
import math
from typing import Tuple, List, Optional, Dict, Any
from collections import deque
import time


class AdaptiveFilter:
    """El hareketlerine uyum sağlayan akıllı filtre"""
    
    def __init__(self, window_size: int = 5):
        self.window_size = window_size
        self.position_history = deque(maxlen=window_size)
        self.velocity_history = deque(maxlen=window_size)
        self.last_position = None
        self.last_time = None
        
    def add_position(self, x: float, y: float) -> Tuple[float, float]:
        """Yeni pozisyon ekle ve filtrelenmiş pozisyon döndür"""
        current_time = time.time()
        
        if self.last_position is not None and self.last_time is not None:
            # Hız hesapla
            dt = current_time - self.last_time
            if dt > 0:
                vx = (x - self.last_position[0]) / dt
                vy = (y - self.last_position[1]) / dt
                self.velocity_history.append((vx, vy))
        
        self.position_history.append((x, y))
        self.last_position = (x, y)
        self.last_time = current_time
        
        # Adaptif filtreleme
        return self._adaptive_smooth()
    
    def _adaptive_smooth(self) -> Tuple[float, float]:
        """Hıza göre adaptif yumuşatma"""
        if len(self.position_history) < 2:
            return self.position_history[-1] if self.position_history else (0, 0)
        
        # Ortalama hız hesapla
        avg_velocity = 0.0
        if self.velocity_history:
            velocities = [math.sqrt(vx*vx + vy*vy) for vx, vy in self.velocity_history]
            avg_velocity = sum(velocities) / len(velocities)
        
        # Hıza göre filtreleme katsayısı
        if avg_velocity < 50:  # Yavaş hareket - daha fazla filtreleme
            weights = [0.1, 0.2, 0.3, 0.4][:len(self.position_history)]
        elif avg_velocity < 200:  # Orta hız
            weights = [0.2, 0.3, 0.5][:len(self.position_history)]
        else:  # Hızlı hareket - az filtreleme
            weights = [0.4, 0.6][:len(self.position_history)]
        
        # Ağırlıklı ortalama
        total_weight = sum(weights)
        if total_weight == 0:
            return self.position_history[-1]
        
        weights = [w/total_weight for w in weights]
        
        filtered_x = sum(pos[0] * w for pos, w in zip(list(self.position_history)[-len(weights):], weights))
        filtered_y = sum(pos[1] * w for pos, w in zip(list(self.position_history)[-len(weights):], weights))
        
        return (filtered_x, filtered_y)


class KalmanFilter:
    """El takibi için Kalman filtresi"""
    
    def __init__(self):
        # State: [x, y, vx, vy]
        self.state = np.array([0.0, 0.0, 0.0, 0.0])
        self.P = np.eye(4) * 1000  # Covariance
        self.Q = np.eye(4) * 0.1   # Process noise
        self.R = np.eye(2) * 10    # Measurement noise
        self.dt = 1/30  # 30 FPS varsayımı
        
        # State transition matrix
        self.F = np.array([
            [1, 0, self.dt, 0],
            [0, 1, 0, self.dt],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
        
        # Measurement matrix
        self.H = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0]
        ])
        
        self.initialized = False
    
    def update(self, x: float, y: float) -> Tuple[float, float]:
        """Yeni ölçümle filtreyi güncelle"""
        measurement = np.array([x, y])
        
        if not self.initialized:
            self.state[:2] = measurement
            self.initialized = True
            return (x, y)
        
        # Predict
        self.state = self.F @ self.state
        self.P = self.F @ self.P @ self.F.T + self.Q
        
        # Update
        y_residual = measurement - self.H @ self.state
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)
        
        self.state = self.state + K @ y_residual
        self.P = (np.eye(4) - K @ self.H) @ self.P
        
        return (self.state[0], self.state[1])
    
    def reset(self):
        """Filtreyi sıfırla"""
        self.initialized = False
        self.P = np.eye(4) * 1000


class JitterReduction:
    """Titreme azaltma sistemi"""
    
    def __init__(self, threshold: float = 2.0):
        self.threshold = threshold
        self.last_position = None
        self.stable_position = None
        self.stable_count = 0
        self.min_stable_frames = 3
    
    def filter_position(self, x: float, y: float) -> Tuple[float, float]:
        """Küçük titremeleri filtrele"""
        if self.last_position is None:
            self.last_position = (x, y)
            self.stable_position = (x, y)
            return (x, y)
        
        # Hareket mesafesi
        distance = math.sqrt((x - self.last_position[0])**2 + (y - self.last_position[1])**2)
        
        if distance < self.threshold:
            # Küçük hareket - titreme olabilir
            self.stable_count += 1
            if self.stable_count >= self.min_stable_frames:
                # Yeterince stabil, pozisyonu güncelle
                self.stable_position = (x, y)
                self.last_position = (x, y)
                return (x, y)
            else:
                # Henüz stabil değil, eski pozisyonu kullan
                return self.stable_position if self.stable_position is not None else (x, y)
        else:
            # Büyük hareket - gerçek hareket
            self.stable_count = 0
            self.stable_position = (x, y)
            self.last_position = (x, y)
            return (x, y)


class SmartCursor:
    """Akıllı cursor kontrolü - titreme önleyici ve hassasiyet optimizasyonu"""
    
    def __init__(self):
        self.adaptive_filter = AdaptiveFilter()
        self.kalman_filter = KalmanFilter()
        self.jitter_reducer = JitterReduction()
        
        # Hassasiyet ayarları
        self.sensitivity_x = 1.0
        self.sensitivity_y = 1.0
        self.acceleration_factor = 1.2
        self.deceleration_factor = 0.8
        
        # Alan bölgeleri
        self.precision_zones = []  # Hassas çalışma alanları
        self.dead_zone_radius = 3  # Merkez dead zone
        
        # İstatistikler
        self.movement_stats = {
            'total_movements': 0,
            'filtered_movements': 0,
            'precision_movements': 0
        }
    
    def add_precision_zone(self, x: float, y: float, width: float, height: float):
        """Hassas çalışma alanı ekle (ör. menü, buton bölgeleri)"""
        self.precision_zones.append({
            'x': x, 'y': y, 'width': width, 'height': height
        })
    
    def is_in_precision_zone(self, x: float, y: float) -> bool:
        """Pozisyon hassas bölgede mi?"""
        for zone in self.precision_zones:
            if (zone['x'] <= x <= zone['x'] + zone['width'] and
                zone['y'] <= y <= zone['y'] + zone['height']):
                return True
        return False
    
    def process_movement(self, raw_x: float, raw_y: float, screen_width: int, screen_height: int) -> Tuple[float, float]:
        """Ham koordinatları işle ve optimize edilmiş cursor pozisyonu döndür"""
        self.movement_stats['total_movements'] += 1
        
        # 1. Kalman filtresi ile temel filtreleme
        filtered_x, filtered_y = self.kalman_filter.update(raw_x, raw_y)
        
        # 2. Adaptif filtreleme
        adaptive_x, adaptive_y = self.adaptive_filter.add_position(filtered_x, filtered_y)
        
        # 3. Titreme azaltma
        final_x, final_y = self.jitter_reducer.filter_position(adaptive_x, adaptive_y)
        
        # 4. Ekran koordinatlarına çevir
        screen_x = final_x * screen_width
        screen_y = final_y * screen_height
        
        # 5. Hassasiyet ayarları
        if self.is_in_precision_zone(screen_x, screen_y):
            # Hassas bölgede - yavaşlat
            screen_x *= self.deceleration_factor
            screen_y *= self.deceleration_factor
            self.movement_stats['precision_movements'] += 1
        else:
            # Normal bölgede - hassasiyet uygula
            screen_x *= self.sensitivity_x
            screen_y *= self.sensitivity_y
        
        # 6. Ekran sınırları kontrolü
        screen_x = max(0, min(screen_width - 1, screen_x))
        screen_y = max(0, min(screen_height - 1, screen_y))
        
        return (screen_x, screen_y)
    
    def calibrate_sensitivity(self, user_movements: List[Tuple[float, float, float, float]]):
        """Kullanıcı hareketlerine göre hassasiyeti kalibre et
        user_movements: [(raw_x, raw_y, expected_x, expected_y), ...]
        """
        if len(user_movements) < 5:
            return
        
        x_ratios = []
        y_ratios = []
        
        for raw_x, raw_y, exp_x, exp_y in user_movements:
            if raw_x != 0:
                x_ratios.append(exp_x / raw_x)
            if raw_y != 0:
                y_ratios.append(exp_y / raw_y)
        
        if x_ratios:
            self.sensitivity_x = sum(x_ratios) / len(x_ratios)
        if y_ratios:
            self.sensitivity_y = sum(y_ratios) / len(y_ratios)
        
        print(f"Hassasiyet kalibre edildi: X={self.sensitivity_x:.2f}, Y={self.sensitivity_y:.2f}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Filtreleme istatistikleri"""
        total = self.movement_stats['total_movements']
        if total == 0:
            return self.movement_stats
        
        return {
            **self.movement_stats,
            'filter_rate': self.movement_stats['filtered_movements'] / total,
            'precision_rate': self.movement_stats['precision_movements'] / total
        }
    
    def reset(self):
        """Tüm filtreleri sıfırla"""
        self.adaptive_filter = AdaptiveFilter()
        self.kalman_filter = KalmanFilter()
        self.jitter_reducer = JitterReduction()
        self.movement_stats = {
            'total_movements': 0,
            'filtered_movements': 0,
            'precision_movements': 0
        }


class AutoCalibrator:
    """Otomatik el kalibrasyonu sistemi"""
    
    def __init__(self):
        self.calibration_data = []
        self.is_calibrating = False
        self.calibration_start_time = None
        self.calibration_duration = 3.0  # 3 saniye
        
        # Kalibrasyon sonuçları
        self.hand_size = None
        self.movement_range = None
        self.natural_rest_position = None
        self.sensitivity_multiplier = 1.0
        
    def start_calibration(self):
        """Otomatik kalibrasyonu başlat"""
        print("🎯 Otomatik kalibrasyon başlatıldı...")
        print("3 saniye boyunca elinizi doğal şekilde hareket ettirin")
        
        self.is_calibrating = True
        self.calibration_start_time = time.time()
        self.calibration_data = []
    
    def add_calibration_sample(self, landmarks) -> bool:
        """Kalibrasyon örneği ekle. True döndürürse kalibrasyon tamamlandı."""
        if not self.is_calibrating or self.calibration_start_time is None:
            return False
        
        current_time = time.time()
        elapsed = current_time - self.calibration_start_time
        
        # Kalibrasyon süresi doldu mu?
        if elapsed >= self.calibration_duration:
            self._process_calibration_data()
            self.is_calibrating = False
            return True
        
        # Örnek ekle
        hand_data = self._extract_hand_features(landmarks)
        self.calibration_data.append(hand_data)
        
        # İlerleme göster
        progress = (elapsed / self.calibration_duration) * 100
        if len(self.calibration_data) % 10 == 0:  # Her 10 frame'de bir göster
            print(f"Kalibrasyon ilerlemesi: {progress:.0f}%")
        
        return False
    
    def _extract_hand_features(self, landmarks) -> Dict:
        """El özelliklerini çıkar"""
        # Temel noktalar
        wrist = (landmarks[0].x, landmarks[0].y)
        thumb_tip = (landmarks[4].x, landmarks[4].y)
        index_tip = (landmarks[8].x, landmarks[8].y)
        middle_tip = (landmarks[12].x, landmarks[12].y)
        ring_tip = (landmarks[16].x, landmarks[16].y)
        pinky_tip = (landmarks[20].x, landmarks[20].y)
        
        # El boyutu (bilek-orta parmak)
        hand_size = math.sqrt((middle_tip[0] - wrist[0])**2 + (middle_tip[1] - wrist[1])**2)
        
        # El merkezi
        palm_center = (
            (wrist[0] + thumb_tip[0] + index_tip[0] + middle_tip[0] + ring_tip[0] + pinky_tip[0]) / 6,
            (wrist[1] + thumb_tip[1] + index_tip[1] + middle_tip[1] + ring_tip[1] + pinky_tip[1]) / 6
        )
        
        return {
            'hand_size': hand_size,
            'palm_center': palm_center,
            'wrist': wrist,
            'fingertips': [thumb_tip, index_tip, middle_tip, ring_tip, pinky_tip],
            'timestamp': time.time()
        }
    
    def _process_calibration_data(self):
        """Kalibrasyon verilerini işle ve parametreleri hesapla"""
        if len(self.calibration_data) < 30:  # En az 1 saniye veri
            print("❌ Yetersiz kalibrasyon verisi. Yeniden deneyin.")
            return
        
        # El boyutu ortalaması
        hand_sizes = [data['hand_size'] for data in self.calibration_data]
        self.hand_size = sum(hand_sizes) / len(hand_sizes)
        
        # Hareket aralığı
        palm_centers = [data['palm_center'] for data in self.calibration_data]
        x_coords = [center[0] for center in palm_centers]
        y_coords = [center[1] for center in palm_centers]
        
        self.movement_range = {
            'x_min': min(x_coords),
            'x_max': max(x_coords),
            'y_min': min(y_coords),
            'y_max': max(y_coords),
            'x_range': max(x_coords) - min(x_coords),
            'y_range': max(y_coords) - min(y_coords)
        }
        
        # Doğal dinlenme pozisyonu (ortalama)
        self.natural_rest_position = (
            sum(x_coords) / len(x_coords),
            sum(y_coords) / len(y_coords)
        )
        
        # Hassasiyet çarpanı (hareket aralığına göre)
        avg_range = (self.movement_range['x_range'] + self.movement_range['y_range']) / 2
        if avg_range > 0.3:  # Geniş hareket
            self.sensitivity_multiplier = 0.8
        elif avg_range < 0.1:  # Dar hareket
            self.sensitivity_multiplier = 1.5
        else:
            self.sensitivity_multiplier = 1.0
        
        print("✅ Otomatik kalibrasyon tamamlandı!")
        print(f"   El boyutu: {self.hand_size:.3f}")
        print(f"   Hareket aralığı: {avg_range:.3f}")
        print(f"   Hassasiyet çarpanı: {self.sensitivity_multiplier:.2f}")
        print(f"   Dinlenme pozisyonu: ({self.natural_rest_position[0]:.3f}, {self.natural_rest_position[1]:.3f})")
    
    def get_calibration_parameters(self) -> Dict[str, Any]:
        """Kalibrasyon parametrelerini döndür"""
        return {
            'hand_size': self.hand_size,
            'movement_range': self.movement_range,
            'natural_rest_position': self.natural_rest_position,
            'sensitivity_multiplier': self.sensitivity_multiplier,
            'is_calibrated': self.hand_size is not None
        }
    
    def get_pinch_threshold(self) -> float:
        """El boyutuna göre pinch eşiği"""
        if self.hand_size is None:
            return 0.05  # Varsayılan
        return self.hand_size * 0.12  # El boyutunun %12'si
    
    def get_movement_threshold(self) -> float:
        """El boyutuna göre hareket eşiği"""
        if self.hand_size is None:
            return 0.02  # Varsayılan
        return self.hand_size * 0.08  # El boyutunun %8'i
