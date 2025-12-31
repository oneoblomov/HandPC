# Evrensel Kontrol Şemasi (kodla uyumlu, oneri)

Bu dokuman, `gesture_detector.py` ve `action_handler.py` içindeki mevcut mantiğa uygun, açik ve guvenli bir hareket şemasi sunar.

## Temel prensipler

- Basit ve tekrarlanabilir: sik kullanilan eylemler tek başparmak+işaret kombinasyonuna (pinch) atanir.
- Guvenlik on planda: ekran kenari marginleri, eylem hiz sinirlamalari ve stabilite kontrolleri uygulanir.
- Moduler: guçlu eylemler drag veya çok parmak kombinasyonlari ile ayrilir.

onerilen ve kodla ortuşen haritalama

### Tek parmak (başparmak + işaret = pinch)

- Pinch (kisa kapan-aç): sol tiklama (`left_click`).
- İki hizli pinch (1s içinde): sağ tiklama (`right_click`).
- Pinch hold + hareket: surukle (drag_start, drag_move, drag_end). (Detect: pinch + orta parmak ile guçlu tutma -> drag)
- Pinch ile imleç kontrolu: pinch aktifken `move_cursor(x,y, pinch_active=True)` ile imleç taşinir.

### uç-parmak / drag-grip

- Pinch + orta parmak sikişi (drag grip): `drag_start`, `drag_move`, `drag_end` olaylari uretilir ve `action_handler` suruklemeyi guvenli şekilde uygular.

### İki parmak

- İki parmak yukari/aşaği: kaydirma (`scroll_up` / `scroll_down`).
- İki parmak sola/sağa: gezinme (`navigate_back` / `navigate_forward`).

### El pozlari — sistem eylemleri

- Kapali yumruk → açik el (fist → open): `win_key` — sistem uygulama menusunu açar.
- Win menusu açikken belirli el x konumuna gore uygulama seç: `open_app` (or: `firefox`, `code`, `nautilus`, `gnome-terminal`, `gnome-calculator`).

### Çok parmak (beş parmak gibi) — oneri

- Beş parmak yukari: uygulama değiştirici (`show_applications`).
- Beş parmak aşaği: masaustunu goster / tum pencereleri kuçult (`show_desktop`).
- Beş parmak sola/sağa: çalişma alani değiştirme (`workspace_left` / `workspace_right`).

### Diğer yararli eylemler

- `toggle_mode`: gesture kontrolunu etkin/devre dişi birak (guvenlik/kalibrasyon sirasinda).
- `freeze_cursor`: imleci dondur/çoz (kazara hareketleri onlemek için).

## Guvenlik & davraniş notlari

- `gesture_detector` tarafinda confidence ve stabilite ataniyor; `action_handler.execute_action` ek olarak confidence >= 0.7, stable gereksinimi ve safe_mode kontrolleri uyguluyor.
- `move_cursor` sadece `pinch_active=True` iken hareket eder.
- Ekran kenari için `safe_margin` (varsayilan 50px) dişina eylemler genelde engellenir.
- Çok hizli ardişik eylemler `max_actions_per_second` ile engellenir.

## Uyumluluk onerileri

- Eğer başka bir hareket ekleyecekseniz, hem `gesture_detector.detect_gesture` içinde action ismini ve confidence/stable alanlarini ekleyin hem de `action_handler.execute_action` içinde o action'a karşilik gelen guvenli uygulamayi (orn. `_my_action_safe`) yazin.

Ek: Bu şema, mevcut kod davranişiyla uyumludur; dilerseniz ben bunu README'a veya extension metadata'sina da yansitacak kuçuk bir duzenleme yapabilirim.
