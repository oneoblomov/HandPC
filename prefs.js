import { ExtensionPreferences } from 'resource:///org/gnome/Shell/Extensions/js/extensions/prefs.js';
import Adw from 'gi://Adw';
import Gio from 'gi://Gio';
import Gtk from 'gi://Gtk';

export default class HCIPreferences extends ExtensionPreferences {
    fillPreferencesWindow(window) {
        const settings = this.getSettings('org.gnome.shell.extensions.hci');
    
    // Ana sayfa
    const page = new Adw.PreferencesPage({
        title: 'HCI Ayarları',
        icon_name: 'input-gesture-symbolic',
    });
    window.add(page);
    
    // Ana ayarlar grubu
    const mainGroup = new Adw.PreferencesGroup({
        title: 'Ana Ayarlar',
        description: 'Temel gesture kontrol ayarları',
    });
    page.add(mainGroup);
    
    // Tutorial modu
    const tutorialRow = new Adw.SwitchRow({
        title: 'Tutorial Modu',
        subtitle: 'Güvenli test modu (gerçek eylemler çalıştırılmaz)',
    });
    mainGroup.add(tutorialRow);
    settings.bind('tutorial-mode', tutorialRow, 'active', Gio.SettingsBindFlags.DEFAULT);
    
    // Güvenli mod
    const safeModeRow = new Adw.SwitchRow({
        title: 'Güvenli Mod',
        subtitle: 'İstenmeyen eylemleri önler',
    });
    mainGroup.add(safeModeRow);
    settings.bind('safe-mode', safeModeRow, 'active', Gio.SettingsBindFlags.DEFAULT);
    
    // Otomatik kalibrasyon
    const autoCalibrateRow = new Adw.SwitchRow({
        title: 'Otomatik Kalibrasyon',
        subtitle: 'Başlangıçta otomatik el kalibrasyonu',
    });
    mainGroup.add(autoCalibrateRow);
    settings.bind('auto-calibrate', autoCalibrateRow, 'active', Gio.SettingsBindFlags.DEFAULT);
    
    // Hassasiyet ayarları grubu
    const sensitivityGroup = new Adw.PreferencesGroup({
        title: 'Hassasiyet Ayarları',
        description: 'Gesture algılama hassasiyeti',
    });
    page.add(sensitivityGroup);
    
    // Cursor yumuşaklığı
    const smoothingRow = new Adw.SpinRow({
        title: 'İmleç Yumuşaklığı',
        subtitle: 'Yüksek değer = daha yumuşak hareket',
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
        subtitle: 'Düşük değer = daha hassas',
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
    
    // Minimum güven
    const confidenceRow = new Adw.SpinRow({
        title: 'Minimum Güven Seviyesi',
        subtitle: 'Gesture algılama için minimum güven',
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
    
    // Güvenlik ayarları grubu
    const securityGroup = new Adw.PreferencesGroup({
        title: 'Güvenlik Ayarları',
        description: 'İstenmeyen eylemleri önleme',
    });
    page.add(securityGroup);
    
    // Click bekleme süresi
    const cooldownRow = new Adw.SpinRow({
        title: 'Click Bekleme Süresi',
        subtitle: 'Clickler arası minimum süre (saniye)',
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
    
    // Maksimum eylem sayısı
    const maxActionsRow = new Adw.SpinRow({
        title: 'Saniye Başı Max Eylem',
        subtitle: 'Saniyede maksimum eylem sayısı',
        adjustment: new Gtk.Adjustment({
            lower: 1,
            upper: 10,
            step_increment: 1,
            page_increment: 1,
        }),
    });
    securityGroup.add(maxActionsRow);
    settings.bind('max-actions-per-second', maxActionsRow, 'value', Gio.SettingsBindFlags.DEFAULT);
    
    // Ekran kenarı mesafesi
    const marginRow = new Adw.SpinRow({
        title: 'Ekran Kenarı Mesafesi',
        subtitle: 'Ekran kenarlarından güvenli mesafe (piksel)',
        adjustment: new Gtk.Adjustment({
            lower: 10,
            upper: 200,
            step_increment: 10,
            page_increment: 10,
        }),
    });
    securityGroup.add(marginRow);
    settings.bind('screen-edge-margin', marginRow, 'value', Gio.SettingsBindFlags.DEFAULT);
    
    // Kamera ayarları grubu
    const cameraGroup = new Adw.PreferencesGroup({
        title: 'Kamera Ayarları',
        description: 'Kamera cihazı ayarları',
    });
    page.add(cameraGroup);
    
    // Kamera indeksi
    const cameraIndexRow = new Adw.SpinRow({
        title: 'Kamera Cihazı',
        subtitle: 'Kullanılacak kamera cihazı (0 = varsayılan)',
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
        subtitle: 'Saniyedeki frame sayısı',
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
        subtitle: 'Önemli olaylar için masaüstü bildirimleri',
    });
    otherGroup.add(notificationsRow);
    settings.bind('show-notifications', notificationsRow, 'active', Gio.SettingsBindFlags.DEFAULT);
    
    // Log seviyesi
    const logLevelRow = new Adw.ComboRow({
        title: 'Log Seviyesi',
        subtitle: 'Kayıt tutma detay seviyesi',
        model: new Gtk.StringList(),
    });
    
    ['DEBUG', 'INFO', 'WARNING', 'ERROR'].forEach(level => {
        logLevelRow.model.append(level);
    });
    
    otherGroup.add(logLevelRow);
    settings.bind('log-level', logLevelRow, 'selected', Gio.SettingsBindFlags.DEFAULT);
    }
}
