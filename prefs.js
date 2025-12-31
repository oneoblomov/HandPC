import { ExtensionPreferences } from 'resource:///org/gnome/Shell/Extensions/js/extensions/prefs.js';
import Adw from 'gi://Adw';
import Gio from 'gi://Gio';
import Gtk from 'gi://Gtk';

export default class HCIPreferences extends ExtensionPreferences {
    fillPreferencesWindow(window) {
        const settings = this.getSettings('org.gnome.shell.extensions.hci');
    
    // Ana sayfa
    const page = new Adw.PreferencesPage({
        title: 'HCI Ayarlari',
        icon_name: 'input-gesture-symbolic',
    });
    window.add(page);
    
    // Ana ayarlar grubu
    const mainGroup = new Adw.PreferencesGroup({
        title: 'Ana Ayarlar',
        description: 'Temel gesture kontrol ayarlari',
    });
    page.add(mainGroup);
    
    // Tutorial modu
    const tutorialRow = new Adw.SwitchRow({
        title: 'Tutorial Modu',
        subtitle: 'Guvenli test modu (gerçek eylemler çaliştirilmaz)',
    });
    mainGroup.add(tutorialRow);
    settings.bind('tutorial-mode', tutorialRow, 'active', Gio.SettingsBindFlags.DEFAULT);
    
    // Guvenli mod
    const safeModeRow = new Adw.SwitchRow({
        title: 'Guvenli Mod',
        subtitle: 'İstenmeyen eylemleri onler',
    });
    mainGroup.add(safeModeRow);
    settings.bind('safe-mode', safeModeRow, 'active', Gio.SettingsBindFlags.DEFAULT);
    
    // Otomatik kalibrasyon
    const autoCalibrateRow = new Adw.SwitchRow({
        title: 'Otomatik Kalibrasyon',
        subtitle: 'Başlangiçta otomatik el kalibrasyonu',
    });
    mainGroup.add(autoCalibrateRow);
    settings.bind('auto-calibrate', autoCalibrateRow, 'active', Gio.SettingsBindFlags.DEFAULT);
    
    // Hassasiyet ayarlari grubu
    const sensitivityGroup = new Adw.PreferencesGroup({
        title: 'Hassasiyet Ayarlari',
        description: 'Gesture algilama hassasiyeti',
    });
    page.add(sensitivityGroup);
    
    // Cursor yumuşakliği
    const smoothingRow = new Adw.SpinRow({
        title: 'İmleç Yumuşakliği',
        subtitle: 'Yuksek değer = daha yumuşak hareket',
        adjustment: new Gtk.Adjustment({
            lower: 0.1,
            upper: 0.9,
            step_increment: 0.1,
            page_increment: 0.1,
        }),
        digits: 1,
    });
    sensitivityGroup.add(smoothingRow);
    settings.bind('smoothing-factor', smoothingRow, 'value', Gio.SettingsBindFlags.DEFAULT);
    
    // Pinch hassasiyeti
    const pinchRow = new Adw.SpinRow({
        title: 'Pinch Hassasiyeti',
        subtitle: 'Duşuk değer = daha hassas',
        adjustment: new Gtk.Adjustment({
            lower: 0.01,
            upper: 0.2,
            step_increment: 0.01,
            page_increment: 0.01,
        }),
        digits: 2,
    });
    sensitivityGroup.add(pinchRow);
    settings.bind('pinch-threshold', pinchRow, 'value', Gio.SettingsBindFlags.DEFAULT);
    
    // Minimum guven
    const confidenceRow = new Adw.SpinRow({
        title: 'Minimum Guven Seviyesi',
        subtitle: 'Gesture algilama için minimum guven',
        adjustment: new Gtk.Adjustment({
            lower: 0.5,
            upper: 0.95,
            step_increment: 0.05,
            page_increment: 0.05,
        }),
        digits: 2,
    });
    sensitivityGroup.add(confidenceRow);
    settings.bind('confidence-minimum', confidenceRow, 'value', Gio.SettingsBindFlags.DEFAULT);
    
    // Guvenlik ayarlari grubu
    const securityGroup = new Adw.PreferencesGroup({
        title: 'Guvenlik Ayarlari',
        description: 'İstenmeyen eylemleri onleme',
    });
    page.add(securityGroup);
    
    // Click bekleme suresi
    const cooldownRow = new Adw.SpinRow({
        title: 'Click Bekleme Suresi',
        subtitle: 'Clickler arasi minimum sure (saniye)',
        adjustment: new Gtk.Adjustment({
            lower: 0.1,
            upper: 2.0,
            step_increment: 0.1,
            page_increment: 0.1,
        }),
        digits: 1,
    });
    securityGroup.add(cooldownRow);
    settings.bind('click-cooldown', cooldownRow, 'value', Gio.SettingsBindFlags.DEFAULT);
    
    // Maksimum eylem sayisi
    const maxActionsRow = new Adw.SpinRow({
        title: 'Saniye Başi Max Eylem',
        subtitle: 'Saniyede maksimum eylem sayisi',
        adjustment: new Gtk.Adjustment({
            lower: 1,
            upper: 10,
            step_increment: 1,
            page_increment: 1,
        }),
    });
    securityGroup.add(maxActionsRow);
    settings.bind('max-actions-per-second', maxActionsRow, 'value', Gio.SettingsBindFlags.DEFAULT);
    
    // Ekran kenari mesafesi
    const marginRow = new Adw.SpinRow({
        title: 'Ekran Kenari Mesafesi',
        subtitle: 'Ekran kenarlarindan guvenli mesafe (piksel)',
        adjustment: new Gtk.Adjustment({
            lower: 10,
            upper: 200,
            step_increment: 10,
            page_increment: 10,
        }),
    });
    securityGroup.add(marginRow);
    settings.bind('screen-edge-margin', marginRow, 'value', Gio.SettingsBindFlags.DEFAULT);
    
    // Kamera ayarlari grubu
    const cameraGroup = new Adw.PreferencesGroup({
        title: 'Kamera Ayarlari',
        description: 'Kamera cihazi ayarlari',
    });
    page.add(cameraGroup);
    
    // Kamera indeksi
    const cameraIndexRow = new Adw.SpinRow({
        title: 'Kamera Cihazi',
        subtitle: 'Kullanilacak kamera cihazi (0 = varsayilan)',
        adjustment: new Gtk.Adjustment({
            lower: 0,
            upper: 10,
            step_increment: 1,
            page_increment: 1,
        }),
    });
    cameraGroup.add(cameraIndexRow);
    settings.bind('camera-index', cameraIndexRow, 'value', Gio.SettingsBindFlags.DEFAULT);
    
    // Kamera FPS
    const fpsRow = new Adw.SpinRow({
        title: 'Kamera FPS',
        subtitle: 'Saniyedeki frame sayisi',
        adjustment: new Gtk.Adjustment({
            lower: 15,
            upper: 60,
            step_increment: 5,
            page_increment: 5,
        }),
    });
    cameraGroup.add(fpsRow);
    settings.bind('camera-fps', fpsRow, 'value', Gio.SettingsBindFlags.DEFAULT);
    
    // Diğer ayarlar grubu
    const otherGroup = new Adw.PreferencesGroup({
        title: 'Diğer Ayarlar',
        description: 'Çeşitli ek ayarlar',
    });
    page.add(otherGroup);
    
    // Bildirimler
    const notificationsRow = new Adw.SwitchRow({
        title: 'Bildirimler',
        subtitle: 'onemli olaylar için masaustu bildirimleri',
    });
    otherGroup.add(notificationsRow);
    settings.bind('show-notifications', notificationsRow, 'active', Gio.SettingsBindFlags.DEFAULT);
    
    // Log seviyesi
    const logLevelRow = new Adw.ComboRow({
        title: 'Log Seviyesi',
        subtitle: 'Kayit tutma detay seviyesi',
        model: new Gtk.StringList(),
    });
    
    ['DEBUG', 'INFO', 'WARNING', 'ERROR'].forEach(level => {
        logLevelRow.model.append(level);
    });
    
    otherGroup.add(logLevelRow);
    settings.bind('log-level', logLevelRow, 'selected', Gio.SettingsBindFlags.DEFAULT);
    }
}
