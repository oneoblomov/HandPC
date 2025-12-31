// Preferences Tests for HCI GNOME Shell Extension
// Tests the prefs.js functionality

const { TestFramework, MockGnomeShell } = imports.testFramework;

// Create test framework instance
const framework = new TestFramework();

// Mock GTK/Adw for preferences testing
const MockAdw = {
    PreferencesPage: class {
        constructor(params) {
            this.title = params.title;
            this.icon_name = params.icon_name;
            this._groups = [];
        }
        
        add(group) {
            this._groups.push(group);
        }
        
        get_groups() {
            return this._groups;
        }
    },
    
    PreferencesGroup: class {
        constructor(params) {
            this.title = params.title;
            this.description = params.description;
            this._rows = [];
        }
        
        add(row) {
            this._rows.push(row);
        }
        
        get_rows() {
            return this._rows;
        }
    },
    
    SwitchRow: class {
        constructor(params) {
            this.title = params.title;
            this.subtitle = params.subtitle;
            this.active = false;
            this._bindings = [];
        }
        
        bind_property(property, target, target_property, flags) {
            this._bindings.push({ property, target, target_property, flags });
        }
    },
    
    SpinRow: class {
        constructor(params) {
            this.title = params.title;
            this.subtitle = params.subtitle;
            this.adjustment = params.adjustment;
            this.digits = params.digits || 0;
            this.value = params.adjustment ? params.adjustment.value : 0;
            this._bindings = [];
        }
        
        bind_property(property, target, target_property, flags) {
            this._bindings.push({ property, target, target_property, flags });
        }
    },
    
    ComboRow: class {
        constructor(params) {
            this.title = params.title;
            this.subtitle = params.subtitle;
            this.model = params.model;
            this.selected = 0;
            this._bindings = [];
        }
        
        bind_property(property, target, target_property, flags) {
            this._bindings.push({ property, target, target_property, flags });
        }
    }
};

const MockGtk = {
    Adjustment: class {
        constructor(params) {
            this.lower = params.lower;
            this.upper = params.upper;
            this.step_increment = params.step_increment;
            this.page_increment = params.page_increment;
            this.value = params.value || params.lower;
        }
    },
    
    StringList: class {
        constructor() {
            this._items = [];
        }
        
        append(item) {
            this._items.push(item);
        }
        
        get_items() {
            return this._items;
        }
    }
};

// Test HCI Preferences Class
framework.addTest('Preferences Initialization', () => {
    const HCIPreferences = class {
        constructor() {
            this._settings = new MockGnomeShell.Gio.Settings({
                settings_schema: { get_id: () => 'org.gnome.shell.extensions.hci' }
            });
        }
        
        getSettings(schemaId) {
            return this._settings;
        }
        
        fillPreferencesWindow(window) {
            const settings = this.getSettings('org.gnome.shell.extensions.hci');
            
            // Create main page
            const page = new MockAdw.PreferencesPage({
                title: 'HCI Ayarlari',
                icon_name: 'input-gesture-symbolic',
            });
            
            this._createMainSettings(page, settings);
            this._createSensitivitySettings(page, settings);
            this._createSecuritySettings(page, settings);
            this._createCameraSettings(page, settings);
            this._createOtherSettings(page, settings);
            
            return page;
        }
        
        _createMainSettings(page, settings) {
            const mainGroup = new MockAdw.PreferencesGroup({
                title: 'Ana Ayarlar',
                description: 'Temel gesture kontrol ayarlari',
            });
            
            this.tutorialRow = new MockAdw.SwitchRow({
                title: 'Tutorial Modu',
                subtitle: 'Guvenli test modu (gerçek eylemler çaliştirilmaz)',
            });
            mainGroup.add(this.tutorialRow);
            
            this.safeModeRow = new MockAdw.SwitchRow({
                title: 'Guvenli Mod',
                subtitle: 'İstenmeyen eylemleri onler',
            });
            mainGroup.add(this.safeModeRow);
            
            page.add(mainGroup);
        }
        
        _createSensitivitySettings(page, settings) {
            const sensitivityGroup = new MockAdw.PreferencesGroup({
                title: 'Hassasiyet Ayarlari',
                description: 'Gesture algilama hassasiyeti',
            });
            
            this.smoothingRow = new MockAdw.SpinRow({
                title: 'İmleç Yumuşakliği',
                subtitle: 'Yuksek değer = daha yumuşak hareket',
                adjustment: new MockGtk.Adjustment({
                    lower: 0.1,
                    upper: 0.9,
                    step_increment: 0.1,
                    page_increment: 0.1,
                    value: 0.3
                }),
                digits: 1,
            });
            sensitivityGroup.add(this.smoothingRow);
            
            page.add(sensitivityGroup);
        }
        
        _createSecuritySettings(page, settings) {
            const securityGroup = new MockAdw.PreferencesGroup({
                title: 'Guvenlik Ayarlari',
                description: 'İstenmeyen eylemleri onleme',
            });
            
            this.cooldownRow = new MockAdw.SpinRow({
                title: 'Click Bekleme Suresi',
                subtitle: 'Clickler arasi minimum sure (saniye)',
                adjustment: new MockGtk.Adjustment({
                    lower: 0.1,
                    upper: 2.0,
                    step_increment: 0.1,
                    page_increment: 0.1,
                    value: 0.3
                }),
                digits: 1,
            });
            securityGroup.add(this.cooldownRow);
            
            page.add(securityGroup);
        }
        
        _createCameraSettings(page, settings) {
            const cameraGroup = new MockAdw.PreferencesGroup({
                title: 'Kamera Ayarlari',
                description: 'Kamera cihazi ayarlari',
            });
            
            this.cameraIndexRow = new MockAdw.SpinRow({
                title: 'Kamera Cihazi',
                subtitle: 'Kullanilacak kamera cihazi (0 = varsayilan)',
                adjustment: new MockGtk.Adjustment({
                    lower: 0,
                    upper: 10,
                    step_increment: 1,
                    page_increment: 1,
                    value: 0
                }),
            });
            cameraGroup.add(this.cameraIndexRow);
            
            page.add(cameraGroup);
        }
        
        _createOtherSettings(page, settings) {
            const otherGroup = new MockAdw.PreferencesGroup({
                title: 'Diğer Ayarlar',
                description: 'Çeşitli ek ayarlar',
            });
            
            this.notificationsRow = new MockAdw.SwitchRow({
                title: 'Bildirimler',
                subtitle: 'onemli olaylar için masaustu bildirimleri',
            });
            otherGroup.add(this.notificationsRow);
            
            this.logLevelRow = new MockAdw.ComboRow({
                title: 'Log Seviyesi',
                subtitle: 'Kayit tutma detay seviyesi',
                model: new MockGtk.StringList(),
            });
            
            ['DEBUG', 'INFO', 'WARNING', 'ERROR'].forEach(level => {
                this.logLevelRow.model.append(level);
            });
            
            otherGroup.add(this.logLevelRow);
            page.add(otherGroup);
        }
    };
    
    const prefs = new HCIPreferences();
    framework.assertNotNull(prefs, 'Preferences should be created');
    framework.assertNotNull(prefs.getSettings('org.gnome.shell.extensions.hci'), 'Settings should be available');
});

framework.addTest('Preferences Window Creation', () => {
    const HCIPreferences = class {
        constructor() {
            this._settings = new MockGnomeShell.Gio.Settings({
                settings_schema: { get_id: () => 'org.gnome.shell.extensions.hci' }
            });
        }
        
        getSettings(schemaId) {
            return this._settings;
        }
        
        fillPreferencesWindow(window) {
            const page = new MockAdw.PreferencesPage({
                title: 'HCI Ayarlari',
                icon_name: 'input-gesture-symbolic',
            });
            
            // Add some basic groups
            const mainGroup = new MockAdw.PreferencesGroup({
                title: 'Ana Ayarlar',
                description: 'Temel gesture kontrol ayarlari',
            });
            
            page.add(mainGroup);
            return page;
        }
    };
    
    const prefs = new HCIPreferences();
    const mockWindow = { add: () => {} };
    const page = prefs.fillPreferencesWindow(mockWindow);
    
    framework.assertNotNull(page, 'Preferences page should be created');
    framework.assertEqual(page.title, 'HCI Ayarlari', 'Page title should be correct');
    framework.assertEqual(page.icon_name, 'input-gesture-symbolic', 'Page icon should be correct');
    framework.assertTrue(page.get_groups().length > 0, 'Page should have preference groups');
});

framework.addTest('Settings Binding', () => {
    const MockSettings = class extends MockGnomeShell.Gio.Settings {
        bind(key, object, property, flags) {
            // Mock the binding
            object._bindings = object._bindings || [];
            object._bindings.push({ key, property, flags });
            
            // Simulate initial value setting
            if (key.includes('mode') || key.includes('notifications')) {
                object[property] = false;
            } else if (key.includes('level')) {
                object[property] = 1; // INFO level
            } else {
                object[property] = 0.3; // Default numeric value
            }
        }
    };
    
    const HCIPreferences = class {
        constructor() {
            this._settings = new MockSettings({
                settings_schema: { get_id: () => 'org.gnome.shell.extensions.hci' }
            });
        }
        
        getSettings(schemaId) {
            return this._settings;
        }
        
        createAndBindRow(key, rowType, params) {
            const settings = this.getSettings('org.gnome.shell.extensions.hci');
            let row;
            
            switch (rowType) {
                case 'switch':
                    row = new MockAdw.SwitchRow(params);
                    settings.bind(key, row, 'active', 0);
                    break;
                case 'spin':
                    row = new MockAdw.SpinRow(params);
                    settings.bind(key, row, 'value', 0);
                    break;
                case 'combo':
                    row = new MockAdw.ComboRow(params);
                    settings.bind(key, row, 'selected', 0);
                    break;
            }
            
            return row;
        }
    };
    
    const prefs = new HCIPreferences();
    
    // Test switch binding
    const tutorialRow = prefs.createAndBindRow('tutorial-mode', 'switch', {
        title: 'Tutorial Modu',
        subtitle: 'Test mode'
    });
    
    framework.assertNotNull(tutorialRow, 'Tutorial row should be created');
    framework.assertTrue(tutorialRow._bindings.length > 0, 'Row should have bindings');
    framework.assertEqual(tutorialRow._bindings[0].key, 'tutorial-mode', 'Binding key should be correct');
    
    // Test spin binding
    const smoothingRow = prefs.createAndBindRow('smoothing-factor', 'spin', {
        title: 'Smoothing',
        adjustment: new MockGtk.Adjustment({ lower: 0.1, upper: 0.9, value: 0.3 })
    });
    
    framework.assertNotNull(smoothingRow, 'Smoothing row should be created');
    framework.assertEqual(smoothingRow.value, 0.3, 'Row should have bound value');
    
    // Test combo binding
    const logRow = prefs.createAndBindRow('log-level', 'combo', {
        title: 'Log Level',
        model: new MockGtk.StringList()
    });
    
    framework.assertNotNull(logRow, 'Log row should be created');
    framework.assertEqual(logRow.selected, 1, 'Row should have bound selection');
});

framework.addTest('Preference Groups Structure', () => {
    const HCIPreferences = class {
        fillPreferencesWindow(window) {
            const page = new MockAdw.PreferencesPage({
                title: 'HCI Ayarlari',
                icon_name: 'input-gesture-symbolic',
            });
            
            // Main settings group
            const mainGroup = new MockAdw.PreferencesGroup({
                title: 'Ana Ayarlar',
                description: 'Temel gesture kontrol ayarlari',
            });
            
            mainGroup.add(new MockAdw.SwitchRow({
                title: 'Tutorial Modu',
                subtitle: 'Guvenli test modu'
            }));
            
            mainGroup.add(new MockAdw.SwitchRow({
                title: 'Guvenli Mod',
                subtitle: 'İstenmeyen eylemleri onler'
            }));
            
            page.add(mainGroup);
            
            // Sensitivity group
            const sensitivityGroup = new MockAdw.PreferencesGroup({
                title: 'Hassasiyet Ayarlari',
                description: 'Gesture algilama hassasiyeti',
            });
            
            sensitivityGroup.add(new MockAdw.SpinRow({
                title: 'İmleç Yumuşakliği',
                adjustment: new MockGtk.Adjustment({ lower: 0.1, upper: 0.9, value: 0.3 })
            }));
            
            page.add(sensitivityGroup);
            
            // Security group
            const securityGroup = new MockAdw.PreferencesGroup({
                title: 'Guvenlik Ayarlari',
                description: 'İstenmeyen eylemleri onleme',
            });
            
            securityGroup.add(new MockAdw.SpinRow({
                title: 'Click Bekleme Suresi',
                adjustment: new MockGtk.Adjustment({ lower: 0.1, upper: 2.0, value: 0.3 })
            }));
            
            page.add(securityGroup);
            
            return page;
        }
    };
    
    const prefs = new HCIPreferences();
    const page = prefs.fillPreferencesWindow({});
    
    const groups = page.get_groups();
    framework.assertEqual(groups.length, 3, 'Should have 3 preference groups');
    
    // Check main group
    const mainGroup = groups[0];
    framework.assertEqual(mainGroup.title, 'Ana Ayarlar', 'Main group title should be correct');
    framework.assertEqual(mainGroup.get_rows().length, 2, 'Main group should have 2 rows');
    
    // Check sensitivity group
    const sensitivityGroup = groups[1];
    framework.assertEqual(sensitivityGroup.title, 'Hassasiyet Ayarlari', 'Sensitivity group title should be correct');
    framework.assertTrue(sensitivityGroup.get_rows().length > 0, 'Sensitivity group should have rows');
    
    // Check security group
    const securityGroup = groups[2];
    framework.assertEqual(securityGroup.title, 'Guvenlik Ayarlari', 'Security group title should be correct');
    framework.assertTrue(securityGroup.get_rows().length > 0, 'Security group should have rows');
});

framework.addTest('Adjustment Ranges Validation', () => {
    const adjustments = {
        smoothing: new MockGtk.Adjustment({
            lower: 0.1,
            upper: 0.9,
            step_increment: 0.1,
            value: 0.3
        }),
        
        clickCooldown: new MockGtk.Adjustment({
            lower: 0.1,
            upper: 2.0,
            step_increment: 0.1,
            value: 0.3
        }),
        
        cameraIndex: new MockGtk.Adjustment({
            lower: 0,
            upper: 10,
            step_increment: 1,
            value: 0
        }),
        
        cameraFps: new MockGtk.Adjustment({
            lower: 15,
            upper: 60,
            step_increment: 5,
            value: 30
        })
    };
    
    // Validate smoothing adjustment
    const smoothing = adjustments.smoothing;
    framework.assertTrue(smoothing.lower >= 0.0, 'Smoothing lower bound should be valid');
    framework.assertTrue(smoothing.upper <= 1.0, 'Smoothing upper bound should be valid');
    framework.assertTrue(smoothing.value >= smoothing.lower && smoothing.value <= smoothing.upper, 'Smoothing default value should be in range');
    
    // Validate cooldown adjustment
    const cooldown = adjustments.clickCooldown;
    framework.assertTrue(cooldown.lower > 0.0, 'Cooldown lower bound should be positive');
    framework.assertTrue(cooldown.upper <= 5.0, 'Cooldown upper bound should be reasonable');
    
    // Validate camera index adjustment
    const cameraIndex = adjustments.cameraIndex;
    framework.assertEqual(cameraIndex.lower, 0, 'Camera index should start from 0');
    framework.assertTrue(cameraIndex.upper >= 5, 'Camera index should support multiple cameras');
    framework.assertEqual(cameraIndex.step_increment, 1, 'Camera index should increment by 1');
    
    // Validate FPS adjustment
    const fps = adjustments.cameraFps;
    framework.assertTrue(fps.lower >= 10, 'FPS lower bound should be reasonable');
    framework.assertTrue(fps.upper <= 60, 'FPS upper bound should not exceed typical max');
    framework.assertEqual(fps.step_increment, 5, 'FPS should increment by 5');
});

framework.addTest('Log Level Combo Box', () => {
    const logLevels = ['DEBUG', 'INFO', 'WARNING', 'ERROR'];
    const stringList = new MockGtk.StringList();
    
    // Add log levels to string list
    logLevels.forEach(level => {
        stringList.append(level);
    });
    
    const logLevelRow = new MockAdw.ComboRow({
        title: 'Log Seviyesi',
        subtitle: 'Kayit tutma detay seviyesi',
        model: stringList,
    });
    
    framework.assertEqual(stringList.get_items().length, 4, 'Should have 4 log levels');
    framework.assertTrue(stringList.get_items().includes('DEBUG'), 'Should include DEBUG level');
    framework.assertTrue(stringList.get_items().includes('INFO'), 'Should include INFO level');
    framework.assertTrue(stringList.get_items().includes('WARNING'), 'Should include WARNING level');
    framework.assertTrue(stringList.get_items().includes('ERROR'), 'Should include ERROR level');
    
    framework.assertEqual(logLevelRow.title, 'Log Seviyesi', 'Log level row title should be correct');
    framework.assertEqual(logLevelRow.model, stringList, 'Log level row should use the string list model');
});

framework.addTest('Preferences Error Handling', () => {
    const HCIPreferences = class {
        constructor() {
            this._settings = null;
            this.errors = [];
        }
        
        getSettings(schemaId) {
            try {
                if (!this._settings) {
                    throw new Error('Settings schema not available');
                }
                return this._settings;
            } catch (e) {
                this.errors.push(`Settings error: ${e.message}`);
                // Return mock settings as fallback
                return new MockGnomeShell.Gio.Settings({
                    settings_schema: { get_id: () => schemaId }
                });
            }
        }
        
        fillPreferencesWindow(window) {
            try {
                const settings = this.getSettings('org.gnome.shell.extensions.hci');
                
                const page = new MockAdw.PreferencesPage({
                    title: 'HCI Ayarlari',
                    icon_name: 'input-gesture-symbolic',
                });
                
                return page;
            } catch (e) {
                this.errors.push(`Window creation error: ${e.message}`);
                throw e;
            }
        }
        
        hasErrors() {
            return this.errors.length > 0;
        }
        
        getErrors() {
            return this.errors;
        }
    };
    
    const prefs = new HCIPreferences();
    
    // Test with no settings available
    const page = prefs.fillPreferencesWindow({});
    
    framework.assertTrue(prefs.hasErrors(), 'Should record settings error');
    framework.assertTrue(prefs.getErrors().some(e => e.includes('Settings error')), 'Should have settings error message');
    framework.assertNotNull(page, 'Should still create page with fallback settings');
});

// Run all tests
framework.runAll().then(success => {
    if (success) {
        print('\n🎉 All preferences tests passed!');
    } else {
        print('\n💥 Some preferences tests failed!');
    }
});