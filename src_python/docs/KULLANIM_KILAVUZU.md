# 🎯 Gesture Control - Kullanım Kılavuzu

## 🚀 Hızlı Başlangıç

### 1. Sistemi Başlatın

```bash
python gesture_control.py
```

### 2. İlk Kalibrasyonu Bekleyin

- Sistem otomatik olarak elinizi kalibre edecek
- Elinizi kameranın önünde sabit tutun
- "✓ El kalibrasyonu tamamlandı" mesajını bekleyin

### 3. Tutorial Modu ile Test Edin

- `t` tuşuna basarak tutorial modunu açın
- Bu modda eylemler gerçekleşmez, sadece algılanır
- Gesture'ları güvenle deneyebilirsiniz

## 🤚 Gesture Rehberi

### ✅ Temel Gesture'lar (Kolay)

- **👆 Sol Tıklama**: Thumb+Index parmağı birleştirin (pinch)
- **🖱️ Sağ Tıklama**: Thumb+Index+Middle parmağı birleştirin
- **🔄 Sürükleme**: Pinch'i 0.7+ saniye tutun

### ⚠️ İleri Seviye Gesture'lar (Deneyimli)

- **📜 Kaydırma**: İki parmak (index+middle) yukarı/aşağı hareket
- **🔙 Geri/İleri**: İki parmak sola/sağa hareket
- **🏠 Masaüstü**: Beş parmak aşağı hareket
- **📱 Uygulamalar**: Beş parmak yukarı hareket

### 🛡️ Güvenlik Gesture'ları

- **✊ Yumruk**: Sistemi geçici devre dışı bırak
- **✋ Açık Avuç**: İmleci dondur

## ⚙️ Ayarlar ve Kontroller

### Klavye Kısayolları

| Tuş | Fonksiyon |
|-----|-----------|
| `q` | Çıkış |
| `c` | El kalibrasyonu başlat |
| `t` | Tutorial modu aç/kapa |
| `s` | Güvenli mod aç/kapa |
| `f` | İmleci dondur/çöz |
| `d` | Gesture kontrolü devre dışı/etkin |
| `h` | Yardımı göster/gizle |
| `SPACE` | Sistemi duraklat |

### Görsel Göstergeler

- 🟢 **Yeşil Nokta**: Gerçek fare pozisyonu
- 🔵 **Mavi Nokta**: İşaret parmağı pozisyonu
- 🔴 **Kırmızı Nokta**: Hedef pozisyon
- **Confidence**: Gesture güven seviyesi (0.0-1.0)
- **Kararlı**: Gesture'ın stabil olup olmadığı
- **Kasıtlı**: Hareketin kasıtlı olup olmadığı

## 🎯 Kullanım İpuçları

### ✅ Doğru Kullanım

1. **Yavaş ve Kasıtlı Hareketler**: Ani hareketlerden kaçının
2. **Kalibrasyon**: İlk kullanımda mutlaka kalibre edin
3. **Tutorial Modu**: Yeni gesture'ları önce tutorial modunda deneyin
4. **Güvenli Mod**: Kritik çalışmalarda güvenli modu açık tutun
5. **Dinlenme**: Uzun kullanımda ara verin

### ❌ Yaygın Hatalar

- **Çok Hızlı Hareket**: Sistem algılamayabilir
- **Kalibrasyon Yapmama**: Hatalı algılamalara neden olur
- **Kötü Işık**: El algılama zorlaşır
- **Çok Yakın/Uzak**: Optimal mesafe 50-80 cm
- **Arka Plan Karışıklığı**: Düz arka plan tercih edin

## 🔧 Sorun Giderme

### Problem: El Algılanmıyor

- **Çözüm 1**: Işığı artırın
- **Çözüm 2**: Kamerayı temizleyin
- **Çözüm 3**: Mesafeyi ayarlayın (50-80 cm)
- **Çözüm 4**: Arka planı düzgünleştirin

### Problem: Gesture Algılanmıyor

- **Çözüm 1**: `c` ile yeniden kalibre edin
- **Çözüm 2**: Daha yavaş hareket edin
- **Çözüm 3**: Tutorial modunda test edin
- **Çözüm 4**: Güven seviyesini kontrol edin

### Problem: İstenmeyen Tıklamalar

- **Çözüm 1**: Güvenli modu açın (`s`)
- **Çözüm 2**: Cooldown süresini artırın
- **Çözüm 3**: İmleci dondurarak test edin (`f`)
- **Çözüm 4**: Sistemi duraklayın (`SPACE`)

### Problem: Performans Düşük

- **Çözüm 1**: Diğer uygulamaları kapatın
- **Çözüm 2**: Kamera çözünürlüğünü düşürün
- **Çözüm 3**: Debug modunu kapatın
- **Çözüm 4**: Python environment'ı optimize edin

## 📊 Sistem Gereksinimleri

### Minimum

- Python 3.7+
- OpenCV 4.0+
- MediaPipe 0.8+
- PyAutoGUI 0.9+
- 4GB RAM
- Webcam

### Önerilen

- Python 3.9+
- 8GB RAM
- 1080p Webcam
- İyi aydınlatma
- Düz arka plan

## ⚡ Performans Optimizasyonu

### Ayarlar Dosyası (gesture_map.json)

```json
{
  "settings": {
    "smoothing": 0.3,          // Hareket yumuşaklığı (0.1-0.5)
    "click_cooldown": 0.8,     // Tıklama arası süre (0.5-2.0)
    "stability_required": true, // Kararlılık gerekli mi
    "confidence_minimum": 0.8   // Minimum güven seviyesi
  }
}
```

### Hassasiyet Ayarları

- **Yüksek Hassasiyet**: `smoothing: 0.1`, `confidence_minimum: 0.6`
- **Dengeli**: `smoothing: 0.3`, `confidence_minimum: 0.8`
- **Güvenli**: `smoothing: 0.5`, `confidence_minimum: 0.9`

## 🆘 Acil Durum

### Sistem Dondu?

1. `SPACE` tuşu ile duraklatın
2. `d` tuşu ile devre dışı bırakın
3. `q` tuşu ile çıkın
4. Terminal'den `Ctrl+C`

### Fare Kontrolü Kaybolduysa

1. **Yumruk** yaparak devre dışı bırakın
2. `f` tuşu ile imleci dondurun
3. Fiziksel fareyi kullanın
4. Sistemi yeniden başlatın

## 📞 Destek

### Log Dosyaları

Sistem hataları terminal çıktısında görünür.

### Test Araçları

```bash
python test_gesture.py config      # Konfigürasyon test
python test_gesture.py interactive # Interaktif test
python test_gesture.py performance # Performans test
```

### İstatistikler

Oturum sonunda detaylı istatistikler gösterilir.

---
**💡 İpucu**: En iyi deneyim için sabırlı olun ve sistemi öğrenmeye zaman ayırın!
