# Gesture Control - Kullanim Kilavuzu

## Hizli Başlangiç

### 1. Sistemi Başlatin

```bash
python gesture_control.py
```

### 2. İlk Kalibrasyonu Bekleyin

- Sistem otomatik olarak elinizi kalibre edecek
- Elinizi kameranin onunde sabit tutun
- "✓ El kalibrasyonu tamamlandi" mesajini bekleyin

### 3. Tutorial Modu ile Test Edin

- `t` tuşuna basarak tutorial modunu açin
- Bu modda eylemler gerçekleşmez, sadece algilanir
- Gesture'lari guvenle deneyebilirsiniz

## 🤚 Gesture Rehberi

### [✓] Temel Gesture'lar (Kolay)

- **👆 Sol Tiklama**: Thumb+Index parmaği birleştirin (pinch)
- **🖱️ Sağ Tiklama**: Thumb+Index+Middle parmaği birleştirin
- **🔄 Surukleme**: Pinch'i 0.7+ saniye tutun

### ⚠️ İleri Seviye Gesture'lar (Deneyimli)

- **📜 Kaydirma**: İki parmak (index+middle) yukari/aşaği hareket
- **🔙 Geri/İleri**: İki parmak sola/sağa hareket
- **🏠 Masaustu**: Beş parmak aşaği hareket
- **📱 Uygulamalar**: Beş parmak yukari hareket

### 🛡️ Guvenlik Gesture'lari

- **✊ Yumruk**: Sistemi geçici devre dişi birak
- **✋ Açik Avuç**: İmleci dondur

## Ayarlar ve Kontroller

### Klavye Kisayollari

| Tuş     | Fonksiyon                         |
| ------- | --------------------------------- |
| `q`     | Çikiş                             |
| `c`     | El kalibrasyonu başlat            |
| `t`     | Tutorial modu aç/kapa             |
| `s`     | Guvenli mod aç/kapa               |
| `f`     | İmleci dondur/çoz                 |
| `d`     | Gesture kontrolu devre dişi/etkin |
| `h`     | Yardimi goster/gizle              |
| `SPACE` | Sistemi duraklat                  |

### Gorsel Gostergeler

- 🟢 **Yeşil Nokta**: Gerçek fare pozisyonu
- 🔵 **Mavi Nokta**: İşaret parmaği pozisyonu
- 🔴 **Kirmizi Nokta**: Hedef pozisyon
- **Confidence**: Gesture guven seviyesi (0.0-1.0)
- **Kararli**: Gesture'in stabil olup olmadiği
- **Kasitli**: Hareketin kasitli olup olmadiği

## Kullanim İpuçlari

### [✓] Doğru Kullanim

1. **Yavaş ve Kasitli Hareketler**: Ani hareketlerden kaçinin
2. **Kalibrasyon**: İlk kullanimda mutlaka kalibre edin
3. **Tutorial Modu**: Yeni gesture'lari once tutorial modunda deneyin
4. **Guvenli Mod**: Kritik çalişmalarda guvenli modu açik tutun
5. **Dinlenme**: Uzun kullanimda ara verin

### [X] Yaygin Hatalar

- **Çok Hizli Hareket**: Sistem algilamayabilir
- **Kalibrasyon Yapmama**: Hatali algilamalara neden olur
- **Kotu Işik**: El algilama zorlaşir
- **Çok Yakin/Uzak**: Optimal mesafe 50-80 cm
- **Arka Plan Karişikliği**: Duz arka plan tercih edin

## 🔧 Sorun Giderme

### Problem: El Algilanmiyor

- **Çozum 1**: Işiği artirin
- **Çozum 2**: Kamerayi temizleyin
- **Çozum 3**: Mesafeyi ayarlayin (50-80 cm)
- **Çozum 4**: Arka plani duzgunleştirin

### Problem: Gesture Algilanmiyor

- **Çozum 1**: `c` ile yeniden kalibre edin
- **Çozum 2**: Daha yavaş hareket edin
- **Çozum 3**: Tutorial modunda test edin
- **Çozum 4**: Guven seviyesini kontrol edin

### Problem: İstenmeyen Tiklamalar

- **Çozum 1**: Guvenli modu açin (`s`)
- **Çozum 2**: Cooldown suresini artirin
- **Çozum 3**: İmleci dondurarak test edin (`f`)
- **Çozum 4**: Sistemi duraklayin (`SPACE`)

### Problem: Performans Duşuk

- **Çozum 1**: Diğer uygulamalari kapatin
- **Çozum 2**: Kamera çozunurluğunu duşurun
- **Çozum 3**: Debug modunu kapatin
- **Çozum 4**: Python environment'i optimize edin

## 📊 Sistem Gereksinimleri

### Minimum

- Python 3.7+
- OpenCV 4.0+
- MediaPipe 0.8+
- PyAutoGUI 0.9+
- 4GB RAM
- Webcam

### onerilen

- Python 3.9+
- 8GB RAM
- 1080p Webcam
- İyi aydinlatma
- Duz arka plan

## ⚡ Performans Optimizasyonu

### Ayarlar Dosyasi (gesture_map.json)

```json
{
  "settings": {
    "smoothing": 0.3, // Hareket yumuşakliği (0.1-0.5)
    "click_cooldown": 0.8, // Tiklama arasi sure (0.5-2.0)
    "stability_required": true, // Kararlilik gerekli mi
    "confidence_minimum": 0.8 // Minimum guven seviyesi
  }
}
```

### Hassasiyet Ayarlari

- **Yuksek Hassasiyet**: `smoothing: 0.1`, `confidence_minimum: 0.6`
- **Dengeli**: `smoothing: 0.3`, `confidence_minimum: 0.8`
- **Guvenli**: `smoothing: 0.5`, `confidence_minimum: 0.9`

## 🆘 Acil Durum

### Sistem Dondu?

1. `SPACE` tuşu ile duraklatin
2. `d` tuşu ile devre dişi birakin
3. `q` tuşu ile çikin
4. Terminal'den `Ctrl+C`

### Fare Kontrolu Kaybolduysa

1. **Yumruk** yaparak devre dişi birakin
2. `f` tuşu ile imleci dondurun
3. Fiziksel fareyi kullanin
4. Sistemi yeniden başlatin

## 📞 Destek

### Log Dosyalari

Sistem hatalari terminal çiktisinda gorunur.

### Test Araçlari

```bash
python test_gesture.py config      # Konfigurasyon test
python test_gesture.py interactive # Interaktif test
python test_gesture.py performance # Performans test
```

### İstatistikler

Oturum sonunda detayli istatistikler gosterilir.

---

**💡 İpucu**: En iyi deneyim için sabirli olun ve sistemi oğrenmeye zaman ayirin!
