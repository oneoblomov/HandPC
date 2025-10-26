#!/usr/bin/env python3
"""
Gesture Control - Basit Örnek Kullanım
Minimal gesture control örneği
"""

import sys
import os

# src klasörünü path'e ekle
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def simple_example():
    """Basit gesture control örneği"""
    print("🎯 Basit Gesture Control Örneği")
    print("=" * 40)
    
    try:
        import cv2
        import mediapipe as mp
        from src.core.gesture_detector import GestureDetector
        from src.core.action_handler import ActionHandler
        
        # Kamera başlat
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Kamera açılamadı!")
            return
        
        # Gesture sistemi başlat
        detector = GestureDetector("../config/gesture_map.json")
        handler = ActionHandler()
        handler.enable_safe_mode(True)  # Güvenli mod
        
        # MediaPipe hands
        mp_hands = mp.solutions.hands # type: ignore
        mp_drawing = mp.solutions.drawing_utils # type: ignore
        
        print("✅ Sistem hazır! 'q' ile çıkış")
        print("🤚 Gesture'ları deneyebilirsiniz (güvenli modda)")
        
        with mp_hands.Hands(max_num_hands=1,
                           min_detection_confidence=0.7,
                           min_tracking_confidence=0.7) as hands:
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame = cv2.flip(frame, 1)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb)
                
                if results.multi_hand_landmarks:
                    landmarks = results.multi_hand_landmarks[0]
                    
                    # Gesture algıla
                    gesture_info = detector.detect_gesture(landmarks.landmark)
                    
                    # Görsel geri bildirim
                    if gesture_info.get('action'):
                        action = gesture_info['action']
                        confidence = gesture_info.get('confidence', 0)
                        cv2.putText(frame, f"Gesture: {action} ({confidence:.2f})", 
                                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                                   0.7, (0, 255, 0), 2)
                        print(f"🎯 Algılanan: {action} (güven: {confidence:.2f})")
                    
                    # El çizimi
                    mp_drawing.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)
                
                # Yardım metni
                cv2.putText(frame, "Basit Gesture Control", (10, frame.shape[0] - 50),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(frame, "q: Cikis", (10, frame.shape[0] - 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                cv2.imshow('Basit Gesture Control', frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        
        cap.release()
        cv2.destroyAllWindows()
        print("👋 Örnek tamamlandı!")
        
    except ImportError as e:
        print(f"❌ Modül hatası: {e}")
        print("Gerekli paketleri yükleyin: python setup.py")
    except Exception as e:
        print(f"❌ Hata: {e}")

if __name__ == '__main__':
    simple_example()
