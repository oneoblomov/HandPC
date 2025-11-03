# HCI (Hand Control Interface) - GNOME Shell Extension

[![CI](https://github.com/oneoblomov/HandPC/workflows/HCI%20Extension%20CI/CD%20Pipeline/badge.svg)](https://github.com/oneoblomov/HandPC/actions)
[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![GNOME Shell 45](https://img.shields.io/badge/GNOME%20Shell-45-orange.svg)](https://wiki.gnome.org/)
[![GNOME Shell 46](https://img.shields.io/badge/GNOME%20Shell-46-orange.svg)](https://wiki.gnome.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

El hareketleri ile bilgisayar kontrolü için GNOME Shell eklentisi. MediaPipe tabanlı gesture recognition kullanarak fare ve klavye işlemlerini el hareketleri ile gerçekleştirmenizi sağlar.

## 🎯 Özellikler

### ✨ Ana Özellikler

- **El Gesture Kontrolü**: MediaPipe ile gelişmiş el algılama
- **Modüler Yapı**: Temiz ve sürdürülebilir kod
- **GNOME Entegrasyonu**: Üst bar'da tam entegrasyon
- **Güvenli Mod**: İstenmeyen eylemleri önler
- **Tutorial Modu**: Güvenli öğrenme ortamı

### 🤚 Desteklenen Gestureler

- **👆 Pinch**: İmleç hareketi (baş + işaret parmağı)
- **👆➡️👆 Tek Pinch**: Sol click
- **👆➡️👆➡️👆 Çift Pinch**: Sağ click
- **✋ Üç Parmak**: Sürükleme (drag & drop)
- **✊➡️✋ Yumruk→Açık**: Win tuşu/Uygulama menüsü

### 🛡️ Güvenlik Özellikleri

- Ekran kenarı koruması
- Eylem sıklığı sınırlaması
- Minimum güven seviyesi kontrolü
- Tutorial modu ile güvenli test

## 📦 Kurulum

### Gereksinimler

```bash
# Python bağımlılıkları
pip install opencv-python mediapipe pyautogui

# Sistem gereksinimleri
sudo apt install python3-opencv python3-pip glib-2.0-dev
```

### Eklenti Kurulumu

1. Eklenti dosyalarını doğru konuma kopyalayın
2. Şemaları derleyin:

```bash
cd ~/.local/share/gnome-shell/extensions/hci@oneOblomov.dev/schemas
glib-compile-schemas .
```

3. GNOME Shell'i yeniden başlatın: `Alt+F2` → `r` → `Enter`
4. Extensions uygulamasından eklentiyi etkinleştirin

## 🚀 Kullanım

### İlk Başlatma

1. Üst bar'daki HCI ikonuna tıklayın
2. "Gesture Control" anahtarını açın
3. Otomatik kalibrasyon tamamlanmasını bekleyin
4. Tutorial modu ile güvenle test edin

### Panel Menüsü

- **🔄 Gesture Control**: Ana açma/kapama
- **📚 Tutorial Modu**: Güvenli test modu
- **🛡️ Güvenli Mod**: Koruma sistemi
- **🎯 El Kalibrasyonu**: Manuel kalibrasyon
- **📊 İstatistikler**: Kullanım verileri
- **📝 Log**: Anlık durum bilgisi

### Gesture Kullanımı

1. **İmleç Hareketi**: Baş ve işaret parmağınızı birleştirin (pinch), hareket ettirin
2. **Sol Click**: Pinch yapıp bırakın
3. **Sağ Click**: Hızlı iki kez pinch yapın
4. **Sürükleme**: Üç parmağınızı birleştirin, hareket ettirin
5. **Win Menüsü**: Yumruğunuzu açık ele çevirin

## ⚙️ Ayarlar

### Ana Ayarlar

- **Tutorial Modu**: Güvenli test ortamı
- **Güvenli Mod**: İstenmeyen eylem koruması
- **Otomatik Kalibrasyon**: Başlangıç kalibrasyonu

### Hassasiyet

- **İmleç Yumuşaklığı**: Hareket pürüzsüzlüğü (0.1-0.9)
- **Pinch Hassasiyeti**: Algılama eşiği (0.01-0.2)
- **Minimum Güven**: Gesture güven seviyesi (0.5-0.95)

### Güvenlik

- **Click Bekleme**: Clickler arası süre (0.1-2.0s)
- **Max Eylem/Saniye**: Hız sınırı (1-10)
- **Ekran Kenarı Mesafesi**: Güvenli alan (10-200px)

### Kamera

- **Kamera Cihazı**: Kullanılacak kamera (0-10)
- **FPS**: Frame hızı (15-60)

## 🐛 Sorun Giderme

### Kamera Açılmıyor

```bash
# Kamera erişim kontrolü
ls /dev/video*

# Python test
python3 -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"
```

### MediaPipe Hatası

```bash
# MediaPipe yeniden kurulum
pip uninstall mediapipe
pip install mediapipe
```

### PyAutoGUI Sorunu

```bash
# X11 için
export DISPLAY=:0

# Wayland için (sınırlı destek)
sudo apt install python3-xlib
```

### Eklenti Logları

```bash
# GNOME Shell logları
journalctl -f -o cat /usr/bin/gnome-shell

# HCI logları
tail -f ~/.local/share/gnome-shell/extensions/hci@oneOblomov.dev/logs/hci.log
```

## 📁 Dosya Yapısı

```
hci@oneOblomov.dev/
├── metadata.json          # Eklenti metadata
├── extension.js          # Ana GNOME JS kodu
├── prefs.js             # Ayarlar sayfası
├── gesture_service.py   # Python gesture servisi
├── gesture_core.py      # Modüler gesture algılama
├── schemas/             # GSettings şeması
│   ├── *.gschema.xml
│   └── gschemas.compiled
├── logs/               # Log dosyaları
└── commands/          # Komut dosyaları
```

## 🔧 Geliştirme

### Debug Modu

```bash
# Extension logları
journalctl -f -o cat /usr/bin/gnome-shell | grep HCI

# Python servisi debug
python3 gesture_service.py /path/to/extension
```

### Yeni Gesture Ekleme

1. `gesture_core.py` içinde `detect_gesture()` fonksiyonunu düzenleyin
2. `ActionHandler` sınıfına yeni eylem ekleyin
3. Ayarlar şemasını güncelleyin

### Test

```bash
# Eklenti test
busctl --user call org.gnome.Shell /org/gnome/Shell org.gnome.Shell Eval s 'Extension.reloadExtension("hci@oneOblomov.dev")'

# Python test
python3 -c "from gesture_core import GestureDetector; print('OK')"
```

## 🎯 Gelecek Özellikler

- [ ] Çoklu el desteği
- [ ] Özel gesture tanımlama
- [ ] Ses komut entegrasyonu
- [ ] Wayland tam desteği
- [ ] Uygulama bazlı gesture profilleri

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun
3. Değişikliklerinizi commit edin
4. Pull request gönderin

## 📄 Lisans

MIT License - Özgürce kullanabilir ve geliştirebilirsiniz.

## 🆘 Destek

- **Issues**: GitHub repository
- **Wiki**: Detaylı dokümantasyon
- **Discussions**: Topluluk desteği

---

**⚠️ Uyarı**: Bu eklenti henüz geliştirme aşamasındadır. Tutorial modu ile güvenle test edin.
