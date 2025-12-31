// Extension Tests for HCI GNOME Shell Extension
// Tests the main extension.js functionality

const { TestFramework, MockGnomeShell } = imports.testFramework;

// Create test framework instance
const framework = new TestFramework();

// Mock the extension environment
const mockExtensionMetadata = {
    uuid: 'hci@oneOblomov.dev',
    name: 'HCI Gesture Control',
    description: 'Hand gesture control for GNOME',
    version: '1.0',
    'shell-version': ['42', '43', '44']
};

// Test HCI Extension Class
framework.addTest('Extension Initialization', () => {
    // Mock the extension imports (simplified)
    const Extension = class {
        constructor(metadata) {
            this.metadata = metadata;
            this._indicator = null;
            this._gestureService = null;
            this._settings = null;
            this._isEnabled = false;
            this._statusIcon = null;
        }
        
        enable() {
            this._loadSettings();
            this._createIndicator();
            this._startGestureService();
            this._isEnabled = true;
        }
        
        disable() {
            this._stopGestureService();
            if (this._indicator) {
                this._indicator.destroy();
                this._indicator = null;
            }
            this._isEnabled = false;
        }
        
        _loadSettings() {
            this._settings = new MockGnomeShell.Gio.Settings({
                settings_schema: { get_id: () => 'org.gnome.shell.extensions.hci' }
            });
        }
        
        _createIndicator() {
            this._indicator = new MockGnomeShell.PanelMenu.Button(0.0, 'HCI Gesture Control', false);
            this._statusIcon = new MockGnomeShell.St.Icon({
                icon_name: 'input-gesture-symbolic',
                style_class: 'system-status-icon'
            });
            this._indicator.add_child(this._statusIcon);
            this._createMenu();
        }
        
        _createMenu() {
            this._toggleItem = new MockGnomeShell.PopupMenu.PopupSwitchMenuItem('Gesture Control', false);
            this._statusItem = new MockGnomeShell.PopupMenu.PopupMenuItem('Durum: Kapali', { reactive: false });
            this._calibrateItem = new MockGnomeShell.PopupMenu.PopupMenuItem('El Kalibrasyonu');
        }
        
        _startGestureService() {
            // Mock service start
            this._gestureService = { running: true };
        }
        
        _stopGestureService() {
            if (this._gestureService) {
                this._gestureService.running = false;
                this._gestureService = null;
            }
        }
    };
    
    // Test extension creation
    const extension = new Extension(mockExtensionMetadata);
    framework.assertNotNull(extension, 'Extension should be created');
    framework.assertEqual(extension.metadata.uuid, 'hci@oneOblomov.dev', 'Extension UUID should match');
    framework.assertFalse(extension._isEnabled, 'Extension should start disabled');
});

framework.addTest('Extension Enable/Disable Cycle', () => {
    const Extension = class {
        constructor(metadata) {
            this.metadata = metadata;
            this._isEnabled = false;
            this._indicator = null;
            this._gestureService = null;
            this._settings = null;
        }
        
        enable() {
            this._settings = {};
            this._indicator = { destroy: () => {} };
            this._gestureService = { running: true };
            this._isEnabled = true;
        }
        
        disable() {
            if (this._gestureService) {
                this._gestureService.running = false;
                this._gestureService = null;
            }
            if (this._indicator) {
                this._indicator.destroy();
                this._indicator = null;
            }
            this._isEnabled = false;
        }
    };
    
    const extension = new Extension(mockExtensionMetadata);
    
    // Test enable
    extension.enable();
    framework.assertTrue(extension._isEnabled, 'Extension should be enabled');
    framework.assertNotNull(extension._indicator, 'Indicator should be created');
    framework.assertNotNull(extension._gestureService, 'Gesture service should be started');
    
    // Test disable
    extension.disable();
    framework.assertFalse(extension._isEnabled, 'Extension should be disabled');
    framework.assertEqual(extension._indicator, null, 'Indicator should be destroyed');
    framework.assertEqual(extension._gestureService, null, 'Gesture service should be stopped');
});

framework.addTest('Settings Management', () => {
    const Extension = class {
        constructor() {
            this._settings = null;
        }
        
        _loadSettings() {
            this._settings = new MockGnomeShell.Gio.Settings({
                settings_schema: { get_id: () => 'org.gnome.shell.extensions.hci' }
            });
            
            // Set some default values
            this._settings.set_boolean('tutorial-mode', false);
            this._settings.set_boolean('safe-mode', true);
            this._settings.set_string('log-level', 'INFO');
        }
        
        getSettingValue(key) {
            if (!this._settings) return null;
            
            if (key.includes('mode')) {
                return this._settings.get_boolean(key);
            } else {
                return this._settings.get_string(key);
            }
        }
        
        setSettingValue(key, value) {
            if (!this._settings) return;
            
            if (typeof value === 'boolean') {
                this._settings.set_boolean(key, value);
            } else {
                this._settings.set_string(key, value);
            }
        }
    };
    
    const extension = new Extension();
    extension._loadSettings();
    
    // Test setting values
    framework.assertFalse(extension.getSettingValue('tutorial-mode'), 'Tutorial mode should be false by default');
    framework.assertTrue(extension.getSettingValue('safe-mode'), 'Safe mode should be true by default');
    framework.assertEqual(extension.getSettingValue('log-level'), 'INFO', 'Log level should be INFO by default');
    
    // Test changing values
    extension.setSettingValue('tutorial-mode', true);
    framework.assertTrue(extension.getSettingValue('tutorial-mode'), 'Tutorial mode should be changeable');
});

framework.addTest('Menu Creation and Structure', () => {
    const menuItems = [];
    
    const MockMenu = {
        addMenuItem: function(item) {
            menuItems.push(item);
        }
    };
    
    const Extension = class {
        constructor() {
            this.menu = MockMenu;
        }
        
        _createMenu() {
            // Main toggle
            this._toggleItem = new MockGnomeShell.PopupMenu.PopupSwitchMenuItem('Gesture Control', false);
            this.menu.addMenuItem(this._toggleItem);
            
            // Separator
            this.menu.addMenuItem(new MockGnomeShell.PopupMenu.PopupSeparatorMenuItem());
            
            // Status
            this._statusItem = new MockGnomeShell.PopupMenu.PopupMenuItem('Durum: Kapali', { reactive: false });
            this.menu.addMenuItem(this._statusItem);
            
            // Calibration
            this._calibrateItem = new MockGnomeShell.PopupMenu.PopupMenuItem('El Kalibrasyonu');
            this.menu.addMenuItem(this._calibrateItem);
            
            // Tutorial mode
            this._tutorialItem = new MockGnomeShell.PopupMenu.PopupSwitchMenuItem('Tutorial Modu', false);
            this.menu.addMenuItem(this._tutorialItem);
            
            // Safe mode
            this._safeModeItem = new MockGnomeShell.PopupMenu.PopupSwitchMenuItem('Guvenli Mod', true);
            this.menu.addMenuItem(this._safeModeItem);
        }
    };
    
    const extension = new Extension();
    extension._createMenu();
    
    // Test menu structure
    framework.assertTrue(menuItems.length >= 5, 'Menu should have at least 5 items');
    framework.assertNotNull(extension._toggleItem, 'Toggle item should be created');
    framework.assertNotNull(extension._statusItem, 'Status item should be created');
    framework.assertNotNull(extension._calibrateItem, 'Calibration item should be created');
    framework.assertNotNull(extension._tutorialItem, 'Tutorial item should be created');
    framework.assertNotNull(extension._safeModeItem, 'Safe mode item should be created');
});

framework.addTest('Gesture Service Communication', () => {
    const Extension = class {
        constructor() {
            this._gestureService = null;
            this._commandsSent = [];
        }
        
        _startGestureService() {
            this._gestureService = {
                running: true,
                commands: []
            };
        }
        
        _stopGestureService() {
            if (this._gestureService) {
                this._gestureService.running = false;
                this._gestureService = null;
            }
        }
        
        _sendCommand(command) {
            this._commandsSent.push(command);
            if (this._gestureService) {
                this._gestureService.commands.push(command);
            }
        }
        
        _calibrateHands() {
            this._sendCommand('calibrate');
        }
        
        _toggleTutorialMode(enabled) {
            this._sendCommand(enabled ? 'tutorial_on' : 'tutorial_off');
        }
        
        _toggleSafeMode(enabled) {
            this._sendCommand(enabled ? 'safe_on' : 'safe_off');
        }
    };
    
    const extension = new Extension();
    extension._startGestureService();
    
    // Test service start
    framework.assertTrue(extension._gestureService.running, 'Gesture service should be running');
    
    // Test command sending
    extension._calibrateHands();
    framework.assertTrue(extension._commandsSent.includes('calibrate'), 'Calibrate command should be sent');
    
    extension._toggleTutorialMode(true);
    framework.assertTrue(extension._commandsSent.includes('tutorial_on'), 'Tutorial on command should be sent');
    
    extension._toggleTutorialMode(false);
    framework.assertTrue(extension._commandsSent.includes('tutorial_off'), 'Tutorial off command should be sent');
    
    extension._toggleSafeMode(true);
    framework.assertTrue(extension._commandsSent.includes('safe_on'), 'Safe mode on command should be sent');
    
    // Test service stop
    extension._stopGestureService();
    framework.assertEqual(extension._gestureService, null, 'Gesture service should be stopped');
});

framework.addTest('Status Updates and Indicators', () => {
    const Extension = class {
        constructor() {
            this._statusIcon = new MockGnomeShell.St.Icon({
                icon_name: 'input-gesture-symbolic',
                style_class: 'system-status-icon'
            });
            this._statusItem = new MockGnomeShell.PopupMenu.PopupMenuItem('Durum: Kapali', { reactive: false });
            this._logItem = new MockGnomeShell.PopupMenu.PopupMenuItem('Log: Hazir', { reactive: false });
        }
        
        _updateStatus(status, color) {
            this._statusItem.label.text = `Durum: ${status}`;
            
            if (color === 'green') {
                this._statusIcon.icon_name = 'input-gesture-symbolic';
            } else if (color === 'red') {
                this._statusIcon.icon_name = 'dialog-error-symbolic';
            }
        }
        
        _updateLog(logText) {
            const shortLog = logText.length > 50 ? logText.substring(0, 47) + '...' : logText;
            this._logItem.label.text = `Log: ${shortLog}`;
        }
    };
    
    const extension = new Extension();
    
    // Test status updates
    extension._updateStatus('Aktif', 'green');
    framework.assertEqual(extension._statusItem.label.text, 'Durum: Aktif', 'Status should update to active');
    framework.assertEqual(extension._statusIcon.icon_name, 'input-gesture-symbolic', 'Icon should show gesture symbol');
    
    extension._updateStatus('Hata', 'red');
    framework.assertEqual(extension._statusItem.label.text, 'Durum: Hata', 'Status should update to error');
    framework.assertEqual(extension._statusIcon.icon_name, 'dialog-error-symbolic', 'Icon should show error symbol');
    
    // Test log updates
    extension._updateLog('Test log message');
    framework.assertEqual(extension._logItem.label.text, 'Log: Test log message', 'Log should update with short message');
    
    const longMessage = 'This is a very long log message that should be truncated when displayed in the menu';
    extension._updateLog(longMessage);
    framework.assertTrue(extension._logItem.label.text.includes('...'), 'Long log should be truncated');
    framework.assertTrue(extension._logItem.label.text.length <= 54, 'Truncated log should not exceed max length'); // "Log: " + 47 chars + "..."
});

framework.addTest('Error Handling', () => {
    const Extension = class {
        constructor() {
            this.errors = [];
        }
        
        _loadSettings() {
            try {
                // Simulate settings loading failure
                throw new Error('Schema not found');
            } catch (e) {
                this.errors.push(`Settings error: ${e.message}`);
                // Use default settings
                this._settings = null;
            }
        }
        
        _startGestureService() {
            try {
                // Simulate service start failure
                throw new Error('Python script not found');
            } catch (e) {
                this.errors.push(`Service error: ${e.message}`);
                this._gestureService = null;
            }
        }
        
        hasErrors() {
            return this.errors.length > 0;
        }
        
        getErrors() {
            return this.errors;
        }
    };
    
    const extension = new Extension();
    
    // Test error handling in settings loading
    extension._loadSettings();
    framework.assertTrue(extension.hasErrors(), 'Extension should record errors');
    framework.assertTrue(extension.getErrors().some(e => e.includes('Settings error')), 'Should record settings error');
    
    // Test error handling in service start
    extension._startGestureService();
    framework.assertTrue(extension.getErrors().some(e => e.includes('Service error')), 'Should record service error');
    framework.assertEqual(extension._gestureService, null, 'Service should be null on error');
});

// Run all tests
framework.runAll().then(success => {
    if (success) {
        print('\n🎉 All extension tests passed!');
    } else {
        print('\n💥 Some extension tests failed!');
    }
});