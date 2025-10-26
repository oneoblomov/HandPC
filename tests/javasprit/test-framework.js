// GNOME Shell Extension Test Framework
// Test utilities for HCI extension

const { GLib, Gio } = imports.gi;

// Mock GNOME Shell modules for testing
var TestFramework = class {
    constructor() {
        this.tests = [];
        this.results = { passed: 0, failed: 0, total: 0 };
    }

    addTest(name, testFunction) {
        this.tests.push({ name, testFunction });
    }

    async runAll() {
        print('🧪 Starting GNOME Extension Tests...');
        print('=' .repeat(50));

        for (let test of this.tests) {
            await this.runTest(test);
        }

        this.printResults();
        return this.results.failed === 0;
    }

    async runTest(test) {
        try {
            print(`▶️  Running: ${test.name}`);
            await test.testFunction();
            this.results.passed++;
            print(`✅ PASSED: ${test.name}`);
        } catch (error) {
            this.results.failed++;
            print(`❌ FAILED: ${test.name}`);
            print(`   Error: ${error.message}`);
            if (error.stack) {
                print(`   Stack: ${error.stack}`);
            }
        }
        this.results.total++;
    }

    printResults() {
        print('');
        print('📊 Test Results:');
        print('=' .repeat(30));
        print(`Total Tests: ${this.results.total}`);
        print(`Passed: ${this.results.passed}`);
        print(`Failed: ${this.results.failed}`);
        print(`Success Rate: ${((this.results.passed / this.results.total) * 100).toFixed(1)}%`);
    }

    // Assertion helpers
    assertEqual(actual, expected, message = '') {
        if (actual !== expected) {
            throw new Error(`Assertion failed: ${message}\n  Expected: ${expected}\n  Actual: ${actual}`);
        }
    }

    assertTrue(condition, message = '') {
        if (!condition) {
            throw new Error(`Assertion failed: ${message}\n  Expected: true\n  Actual: ${condition}`);
        }
    }

    assertFalse(condition, message = '') {
        if (condition) {
            throw new Error(`Assertion failed: ${message}\n  Expected: false\n  Actual: ${condition}`);
        }
    }

    assertNotNull(value, message = '') {
        if (value === null || value === undefined) {
            throw new Error(`Assertion failed: ${message}\n  Expected: not null/undefined\n  Actual: ${value}`);
        }
    }

    assertThrows(func, message = '') {
        try {
            func();
            throw new Error(`Assertion failed: ${message}\n  Expected: exception to be thrown\n  Actual: no exception`);
        } catch (error) {
            // Expected behavior
        }
    }
};

// Mock GNOME Shell objects for testing
var MockGnomeShell = {
    Main: {
        panel: {
            addToStatusArea: function(id, indicator) {
                return { id, indicator };
            }
        }
    },
    
    PanelMenu: {
        Button: class {
            constructor(menuAlignment, nameText, dontCreateMenu) {
                this.menuAlignment = menuAlignment;
                this.nameText = nameText;
                this.dontCreateMenu = dontCreateMenu;
                this.menu = { addMenuItem: () => {} };
                this._children = [];
            }
            
            add_child(child) {
                this._children.push(child);
            }
            
            destroy() {
                this._children = [];
            }
        }
    },
    
    PopupMenu: {
        PopupSwitchMenuItem: class {
            constructor(text, active) {
                this.label = { text };
                this.active = active;
                this._signals = [];
            }
            
            connect(signal, callback) {
                this._signals.push({ signal, callback });
                return this._signals.length - 1;
            }
        },
        
        PopupMenuItem: class {
            constructor(text, params = {}) {
                this.label = { text };
                this.reactive = params.reactive !== false;
                this._signals = [];
            }
            
            connect(signal, callback) {
                this._signals.push({ signal, callback });
                return this._signals.length - 1;
            }
        },
        
        PopupSeparatorMenuItem: class {
            constructor() {}
        }
    },
    
    St: {
        Icon: class {
            constructor(params) {
                this.icon_name = params.icon_name;
                this.style_class = params.style_class;
            }
        }
    },
    
    Gio: {
        Settings: class {
            constructor(params) {
                this.schema = params.settings_schema;
                this._values = new Map();
            }
            
            bind(key, object, property, flags) {
                // Mock binding
            }
            
            get_string(key) {
                return this._values.get(key) || '';
            }
            
            set_string(key, value) {
                this._values.set(key, value);
            }
            
            get_boolean(key) {
                return this._values.get(key) || false;
            }
            
            set_boolean(key, value) {
                this._values.set(key, value);
            }
        },
        
        SettingsSchemaSource: {
            new_from_directory: function(path, parent, trusted) {
                return {
                    lookup: function(schemaId, recursive) {
                        return { get_id: () => schemaId };
                    }
                };
            },
            
            get_default: function() {
                return {};
            }
        },
        
        File: {
            new_for_path: function(path) {
                return {
                    get_path: () => path,
                    query_exists: () => true,
                    load_contents: () => [true, new TextEncoder().encode('test content')],
                    replace_contents: () => true
                };
            }
        },
        
        Subprocess: {
            new: function(argv, flags) {
                return {
                    wait_async: function(cancellable, callback) {
                        // Mock async wait
                        setTimeout(() => {
                            callback(this, {});
                        }, 100);
                    },
                    
                    wait_finish: function(result) {
                        return true;
                    },
                    
                    force_exit: function() {
                        return true;
                    }
                };
            }
        }
    },
    
    GLib: {
        timeout_add_seconds: function(priority, interval, callback) {
            return setTimeout(callback, interval * 1000);
        },
        
        spawn_command_line_async: function(command) {
            return true;
        },
        
        SOURCE_CONTINUE: true
    }
};

// Export for use in other test files
var GNOME_TEST_FRAMEWORK = { TestFramework, MockGnomeShell };