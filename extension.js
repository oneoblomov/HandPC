import { Extension } from 'resource:///org/gnome/shell/extensions/extension.js';
import GObject from 'gi://GObject';
import St from 'gi://St';
import GLib from 'gi://GLib';

import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import * as PanelMenu from 'resource:///org/gnome/shell/ui/panelMenu.js';
import * as PopupMenu from 'resource:///org/gnome/shell/ui/popupMenu.js';

// Ayarlarla entegre HCI Gesture Control Extension
const HCIIndicator = GObject.registerClass(
class HCIIndicator extends PanelMenu.Button {
    _init(extension) {
        super._init(0.0, 'HCI Gesture Control');
        
        this._extension = extension;
        this._settings = extension.getSettings();
        this._currentProcess = null;

        this._icon = new St.Icon({
            icon_name: 'input-touchpad-symbolic',
            style_class: 'system-status-icon'
        });
        this.add_child(this._icon);

        this._buildMenu();
        this._connectSettings();
        log('HCI: Ayarlarla entegre extension başlatıldı');
    }

    _connectSettings() {
        // Ayar değişikliklerini dinle
        this._settingsConnections = [];
        
        const keys = [
            'tutorial-mode', 'safe-mode', 'auto-calibrate', 
            'smoothing-factor', 'camera-index', 'confidence-minimum'
        ];
        
        keys.forEach(key => {
            const connection = this._settings.connect(`changed::${key}`, () => {
                log(`HCI: Ayar değişti: ${key} = ${this._getSettingValue(key)}`);
                this._onSettingsChanged();
            });
            this._settingsConnections.push(connection);
        });
    }

    _getSettingValue(key) {
        try {
            if (key.includes('mode') || key.includes('auto-calibrate')) {
                return this._settings.get_boolean(key);
            } else if (key.includes('factor') || key.includes('threshold') || key.includes('confidence') || key.includes('cooldown')) {
                return this._settings.get_double(key);
            } else if (key.includes('index') || key.includes('fps') || key.includes('actions') || key.includes('margin')) {
                return this._settings.get_int(key);
            } else {
                return this._settings.get_string(key);
            }
        } catch (e) {
            log(`HCI: Ayar okuma hatasi ${key}: ${e}`);
            return null;
        }
    }

    _onSettingsChanged() {
        // Eğer servis çalişiyorsa, yeniden başlat
        if (this._currentProcess) {
            log('HCI: Ayarlar değişti, servis yeniden başlatiliyor...');
            this._showNotification('Yeniden Başlatılıyor', 'Ayar değişikliği nedeniyle servis yeniden başlatılıyor');
            this._stopService(() => {
                // Kisa bir bekleme sonrasi yeniden başlat
                GLib.timeout_add(GLib.PRIORITY_DEFAULT, 1000, () => {
                    this._runLocalScript();
                    return false;
                });
            });
        }
    }

    _stopService(callback) {
        if (this._currentProcess) {
            try {
                // Python process'ini nazikçe sonlandir
                const killCommand = `pkill -f "python3.*main.py"`;
                GLib.spawn_command_line_async(killCommand);
                
                this._currentProcess = null;
                log('HCI: Servis durduruldu');
                
                if (callback) {
                    GLib.timeout_add(GLib.PRIORITY_DEFAULT, 500, () => {
                        callback();
                        return false;
                    });
                }
            } catch (e) {
                logError(e, 'HCI: Servis durdurma hatasi');
            }
        } else if (callback) {
            callback();
        }
    }

    _buildMenu() {
        try {
            log('HCI: Building menu...');
            
            // Durum gostergesi - dinamik olarak guncellenecek
            this._statusItem = new PopupMenu.PopupMenuItem(this._getStatusText(), { reactive: false });
            this.menu.addMenuItem(this._statusItem);

            this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());

            // Ana çaliştirma butonu
            this._runItem = new PopupMenu.PopupMenuItem('Gesture Servisini Başlat');
            this._runItem.connect('activate', () => {
                log('HCI: Run button clicked!');
                try {
                    this._runLocalScript();
                } catch (e) {
                    logError(e, 'HCI: Menu item activation failed');
                    this._showNotification('Hata', 'Menü eylemi başarısız');
                }
            });
            this.menu.addMenuItem(this._runItem);
            
            // Durdurma butonu
            this._stopItem = new PopupMenu.PopupMenuItem('Servisi Durdur');
            this._stopItem.connect('activate', () => {
                log('HCI: Stop button clicked!');
                this._stopService(() => {
                    this._showNotification('Durduruldu', 'Gesture servisi durduruldu');
                    this._updateMenuState();
                });
            });
            this.menu.addMenuItem(this._stopItem);
            
            this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());
            
            // Ayarlar onizlemesi
            this._settingsPreviewItem = new PopupMenu.PopupMenuItem(this._getSettingsPreview(), { reactive: false });
            this.menu.addMenuItem(this._settingsPreviewItem);
            
            this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());
            
            // Sistem durumu kontrol butonu
            this._statusCheckItem = new PopupMenu.PopupMenuItem('📊 Sistem Durumu');
            this._statusCheckItem.connect('activate', () => {
                log('HCI: Status check button clicked!');
                try {
                    this._checkSystemStatus();
                } catch (e) {
                    logError(e, 'HCI: Status check failed');
                }
            });
            this.menu.addMenuItem(this._statusCheckItem);
            
            // Test bildirim butonu (debug)
            this._testItem = new PopupMenu.PopupMenuItem('Test Bildirim');
            this._testItem.connect('activate', () => {
                log('HCI: Test notification button clicked!');
                this._showNotification('🧪 Test', 'Bu bir test bildirimidir');
            });
            this.menu.addMenuItem(this._testItem);
            
            this._updateMenuState();
            log('HCI: Menu built successfully');
        } catch (e) {
            logError(e, 'HCI: Menu building failed');
        }
    }

    _updateMenuState() {
        // Menu oğelerinin durumunu guncelle
        const isRunning = this._currentProcess !== null;
        
        if (this._runItem) {
            this._runItem.label.text = isRunning ? 'Yeniden Başlat' : 'Gesture Servisini Başlat';
        }

        if (this._stopItem) {
            this._stopItem.setSensitive(isRunning);
        }

        if (this._statusItem) {
            this._statusItem.label.text = this._getStatusText();
        }

        if (this._settingsPreviewItem) {
            this._settingsPreviewItem.label.text = this._getSettingsPreview();
        }
    }

    _getStatusText() {
        const isRunning = this._currentProcess !== null;
        const tutorialMode = this._getSettingValue('tutorial-mode');
        const safeMode = this._getSettingValue('safe-mode');
        
        let status = isRunning ? 'Çalişiyor' : 'Durdu';
        if (tutorialMode) status += ' (Tutorial)';
        if (safeMode) status += ' (Guvenli)';
        
        return status;
    }

    _getSettingsPreview() {
        try {
            const tutorial = this._getSettingValue('tutorial-mode') ? 'ON' : 'OFF';
            const safe = this._getSettingValue('safe-mode') ? 'ON' : 'OFF';
            const smoothing = this._getSettingValue('smoothing-factor')?.toFixed(1) || '0.3';
            const camera = this._getSettingValue('camera-index') || 0;
            
            return `Tutorial:${tutorial} Safe:${safe} Smooth:${smoothing} Cam:${camera}`;
        } catch (e) {
            return 'Ayarlar yuklenemedi';
        }
    }

    _runLocalScript() {
        try {
            // once mevcut sureci durdur
            this._stopService();
            
            // Get the script path
            const extensionDir = GLib.build_filenamev([GLib.get_home_dir(), '.local', 'share', 'gnome-shell', 'extensions', 'hci@oneOblomov.dev']);
            const scriptPath = GLib.build_filenamev([extensionDir, 'src_python', 'run.sh']);
            
            // Check if script exists first
            if (!GLib.file_test(scriptPath, GLib.FileTest.EXISTS)) {
                throw new Error('run.sh script not found');
            }
            
            if (!GLib.file_test(scriptPath, GLib.FileTest.IS_EXECUTABLE)) {
                throw new Error('run.sh script is not executable');
            }
            
            // Ayarlari environment variables olarak hazirla
            const envVars = this._prepareEnvironmentVariables();
            
            // Environment variables'lari string olarak birleştir
            let envString = '';
            for (const [key, value] of Object.entries(envVars)) {
                envString += `export ${key}="${value}"; `;
            }
            
            // Command with environment variables
            const command = `cd "${extensionDir}/src_python" && ${envString} nohup bash run.sh > /dev/null 2>&1 &`;
            
            log(`HCI: Executing command with settings: ${command}`);
            log(`HCI: Environment vars: ${JSON.stringify(envVars)}`);
            
            // Execute the command (spawn_command_line_async runs asynchronously and does not return a tuple)
            try {
                GLib.spawn_command_line_async(`bash -c '${command}'`);

                // The script uses nohup and backgrounds itself, so we can't reliably obtain a PID here.
                // Mark the service as running and update UI accordingly.
                this._currentProcess = true;
                this._showNotification('Başlatıldı', 'Gesture hizmeti ayarlarla başlatıldı');
                this._updateMenuState();
                log(`HCI: Gesture service start command executed`);

                // 2 saniye sonra durum guncellemesi
                GLib.timeout_add(GLib.PRIORITY_DEFAULT, 2000, () => {
                    this._updateMenuState();
                    return false;
                });
            } catch (e) {
                throw new Error('Failed to execute start command: ' + e.message);
            }
            
        } catch (e) {
            logError(e, 'HCI: runLocalScript failed');
            this._showNotification('[X] Hata', `Gesture hizmeti başlatilamadi: ${e.message}`);
        }
    }

    _prepareEnvironmentVariables() {
        const vars = {};
        
        try {
            // Boolean ayarlar
            vars['HCI_TUTORIAL_MODE'] = this._getSettingValue('tutorial-mode') ? 'true' : 'false';
            vars['HCI_SAFE_MODE'] = this._getSettingValue('safe-mode') ? 'true' : 'false';
            vars['HCI_AUTO_CALIBRATE'] = this._getSettingValue('auto-calibrate') ? 'true' : 'false';
            vars['HCI_SHOW_NOTIFICATIONS'] = this._getSettingValue('show-notifications') ? 'true' : 'false';
            
            // Numeric ayarlar
            vars['HCI_SMOOTHING_FACTOR'] = String(this._getSettingValue('smoothing-factor') || 0.3);
            vars['HCI_PINCH_THRESHOLD'] = String(this._getSettingValue('pinch-threshold') || 0.05);
            vars['HCI_CONFIDENCE_MINIMUM'] = String(this._getSettingValue('confidence-minimum') || 0.7);
            vars['HCI_CLICK_COOLDOWN'] = String(this._getSettingValue('click-cooldown') || 0.3);
            vars['HCI_CAMERA_INDEX'] = String(this._getSettingValue('camera-index') || 0);
            vars['HCI_CAMERA_FPS'] = String(this._getSettingValue('camera-fps') || 30);
            vars['HCI_MAX_ACTIONS_PER_SECOND'] = String(this._getSettingValue('max-actions-per-second') || 3);
            vars['HCI_SCREEN_EDGE_MARGIN'] = String(this._getSettingValue('screen-edge-margin') || 50);
            
            // String ayarlar
            vars['HCI_LOG_LEVEL'] = this._getSettingValue('log-level') || 'INFO';
            
            log(`HCI: Prepared environment variables: ${JSON.stringify(vars)}`);
        } catch (e) {
            logError(e, 'HCI: Error preparing environment variables');
        }
        
        return vars;
    }

    _showNotification(title, message) {
        // Simple and reliable notification using notify-send
        log(`HCI Notification - ${title}: ${message}`);
        try {
            const command = `notify-send "${title}" "${message}" --icon=input-touchpad-symbolic --app-name="HCI Gesture Control"`;
            GLib.spawn_command_line_async(command);
            log(`HCI: Notification sent via notify-send`);
        } catch (error) {
            log(`HCI: Notification error: ${error.message}`);
        }
    }

    _checkSystemStatus() {
        try {
            const extensionDir = GLib.build_filenamev([GLib.get_home_dir(), '.local', 'share', 'gnome-shell', 'extensions', 'hci@oneOblomov.dev']);
            const scriptPath = GLib.build_filenamev([extensionDir, 'src_python', 'run.sh']);
            const pythonPath = GLib.build_filenamev([extensionDir, 'src_python', 'src', 'main.py']);
            
            // Check if files exist
            let statusMessage = 'Sistem Durumu:\n';
            
            if (GLib.file_test(scriptPath, GLib.FileTest.EXISTS)) {
                statusMessage += 'run.sh bulundu\n';
                if (GLib.file_test(scriptPath, GLib.FileTest.IS_EXECUTABLE)) {
                    statusMessage += 'run.sh çaliştirilabilir\n';
                } else {
                    statusMessage += 'run.sh çaliştirilabilir değil\n';
                }
            } else {
                statusMessage += 'run.sh bulunamadi\n';
            }
            
            if (GLib.file_test(pythonPath, GLib.FileTest.EXISTS)) {
                statusMessage += 'main.py bulundu\n';
            } else {
                statusMessage += 'main.py bulunamadi\n';
            }
            
            // Check environment
            const display = GLib.getenv('DISPLAY');
            if (display) {
                statusMessage += `[✓] DISPLAY: ${display}\n`;
            } else {
                statusMessage += '[X] DISPLAY değişkeni yok\n';
            }
            
            this._showNotification('Sistem Durumu', statusMessage);
            log(`HCI: System status checked: ${statusMessage}`);
            
        } catch (e) {
            logError(e, 'HCI: System status check failed');
            this._showNotification('Hata', 'Sistem durumu kontrol edilemedi');
        }
    }

    destroy() {
        try {
            log('HCI: Indicator destroying...');
            
            // Settings bağlantilarini temizle
            if (this._settingsConnections) {
                this._settingsConnections.forEach(connection => {
                    this._settings.disconnect(connection);
                });
                this._settingsConnections = [];
            }
            
            // Çalişan servisi durdur
            this._stopService();
            
            super.destroy();
            log('HCI: Indicator destroyed successfully');
        } catch (e) {
            logError(e, 'HCI: Indicator destruction failed');
        }
    }
});

export default class HCIExtension extends Extension {
    enable() {
        try {
            log('HCI: Extension enabling...');
            this._indicator = new HCIIndicator(this);
            Main.panel.addToStatusArea('hci-gesture-control', this._indicator);
            log('HCI: Extension enabled successfully');
        } catch (e) {
            logError(e, 'HCI: Extension enable failed');
        }
    }

    disable() {
        try {
            log('HCI: Extension disabling...');
            if (this._indicator) {
                this._indicator.destroy();
                this._indicator = null;
                log('HCI: Extension disabled successfully');
            }
        } catch (e) {
            logError(e, 'HCI: Extension disable failed');
        }
    }
}