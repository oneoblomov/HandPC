# Evrensel Kontrol Şeması (kodla uyumlu, öneri)

Bu doküman, `gesture_detector.py` ve `action_handler.py` içindeki mevcut mantığa uygun, açık ve güvenli bir hareket şeması sunar.

## Temel prensipler

- Basit ve tekrarlanabilir: sık kullanılan eylemler tek başparmak+işaret kombinasyonuna (pinch) atanır.
- Güvenlik ön planda: ekran kenarı marginleri, eylem hız sınırlamaları ve stabilite kontrolleri uygulanır.
- Modüler: güçlü eylemler drag veya çok parmak kombinasyonları ile ayrılır.

Önerilen ve kodla örtüşen haritalama

### Tek parmak (başparmak + işaret = pinch)

- Pinch (kısa kapan-aç): sol tıklama (`left_click`).
- İki hızlı pinch (1s içinde): sağ tıklama (`right_click`).
- Pinch hold + hareket: sürükle (drag_start, drag_move, drag_end). (Detect: pinch + orta parmak ile güçlü tutma -> drag)
- Pinch ile imleç kontrolü: pinch aktifken `move_cursor(x,y, pinch_active=True)` ile imleç taşınır.

### Üç-parmak / drag-grip

- Pinch + orta parmak sıkışı (drag grip): `drag_start`, `drag_move`, `drag_end` olayları üretilir ve `action_handler` sürüklemeyi güvenli şekilde uygular.

### İki parmak

- İki parmak yukarı/aşağı: kaydırma (`scroll_up` / `scroll_down`).
- İki parmak sola/sağa: gezinme (`navigate_back` / `navigate_forward`).

### El pozları — sistem eylemleri

- Kapalı yumruk → açık el (fist → open): `win_key` — sistem uygulama menüsünü açar.
- Win menüsü açıkken belirli el x konumuna göre uygulama seç: `open_app` (ör: `firefox`, `code`, `nautilus`, `gnome-terminal`, `gnome-calculator`).

### Çok parmak (beş parmak gibi) — öneri

- Beş parmak yukarı: uygulama değiştirici (`show_applications`).
- Beş parmak aşağı: masaüstünü göster / tüm pencereleri küçült (`show_desktop`).
- Beş parmak sola/sağa: çalışma alanı değiştirme (`workspace_left` / `workspace_right`).

### Diğer yararlı eylemler

- `toggle_mode`: gesture kontrolünü etkin/devre dışı bırak (güvenlik/kalibrasyon sırasında).
- `freeze_cursor`: imleci dondur/çöz (kazara hareketleri önlemek için).

## Güvenlik & davranış notları

- `gesture_detector` tarafında confidence ve stabilite atanıyor; `action_handler.execute_action` ek olarak confidence >= 0.7, stable gereksinimi ve safe_mode kontrolleri uyguluyor.
- `move_cursor` sadece `pinch_active=True` iken hareket eder.
- Ekran kenarı için `safe_margin` (varsayılan 50px) dışına eylemler genelde engellenir.
- Çok hızlı ardışık eylemler `max_actions_per_second` ile engellenir.

## Uyumluluk önerileri

- Eğer başka bir hareket ekleyecekseniz, hem `gesture_detector.detect_gesture` içinde action ismini ve confidence/stable alanlarını ekleyin hem de `action_handler.execute_action` içinde o action'a karşılık gelen güvenli uygulamayı (örn. `_my_action_safe`) yazın.

Ek: Bu şema, mevcut kod davranışıyla uyumludur; dilerseniz ben bunu README'a veya extension metadata'sına da yansıtacak küçük bir düzenleme yapabilirim.
