var Vispa = Class.extend({

    init: function(config, extensionConfig, workspaceData) {
        // register a logger
        this.logger = $.Logger('Vispa');

        // attributes
        this.settings = {};
        this.defaultConfig = {
            userName: null,
            workspaceId: null,
            addWorkspaces: null,
            profileId: null,
            view: {},
            extensionView: {},
            extensionManager: {},
            commandPalette: {},
            urlHandler: {},
            messenger: {},
            preferenceHandler: {},
            preferenceView: {},
            workspaceManager: {},
            pathBar: {},
            bus: {}
        };
        this.workflow = {
            urlParametersHandled: false
        };
        this.config = $.extend(true, {}, this.defaultConfig, config);

        // members
        this.view = new View(this.config.view);
        this.extensionView = new ExtensionView(this.config.extensionView);
        this.extensionManager = new ExtensionManager(this.config.extensionManager, extensionConfig);
        this.commandPalette = new CommandPalette(this.config.commandPalette);
        this.urlHandler = new UrlHandler(this.config.urlHandler);
        this.workspaceManager = new WorkspaceManager(this.config.workspaceManager, workspaceData);
        this.messenger = new Messenger(this.config.messenger);
        this.preferenceHandler = new PreferenceHandler(this.config.preferenceHandler);
        this.preferenceView = new PreferenceView(this.config.preferenceView);
        this.pathBar = new PathBar(this.config.pathBar);
        this.bus = Bus(this.config.bus);
    },

    startup: function() {
        var _this = this;

        this.logger.debug('Started');

        // setup all components
        this.preferenceView.startup();
        this.preferenceHandler.startup();
        this.messenger.startup();
        this.urlHandler.startup();
        this.commandPalette.startup();
        this.extensionManager.startup();
        this.extensionView.startup();
        this.pathBar.startup();
        this.view.startup();
        this.workspaceManager.startup();

        // setup the preference management
        this.addPreferenceObservables();
        // change the section order in the preferenceHandler
        this.preferenceHandler.setSectionOrder(['vispa', 'workspaces', 'extensions']);

        this.setupTopics();
        this.addPaletteCommands();
        // enable global shortcuts
        $.Shortcuts('global').enable();

        // wrapp the history when everything is done and call it
        this.urlHandler.wrappHistory(function() {
            _this.handleUrlParameters.apply(_this, arguments);
        });
        // the callback is called once when the workspace is connected

        if (!this.config.devMode) {
            $(window).on('beforeunload', function() {
                return 'You are about to leave Vispa.';
            });
        }

        return this;
    },

    applyConfig: function() {
        // userName => static
        // commandPalette
        this.commandPalette.applyConfig();
        // messenger
        this.messenger.applyConfig();
        // bus => static
        // extensionManager
        this.extensionManager.applyConfig();
        // url => static
        // view
        this.view.applyConfig();
        // extensionView
        this.extensionView.applyConfig();
        // preferenceView
        this.preferenceView.applyConfig();
        // preferenceHandler
        this.preferenceHandler.applyConfig();
        // workspaceManager
        this.workspaceManager.applyConfig();
        // notify
        //$.Topic('msg.log').publish('debug', {text: 'config applied', icon: 'ui-icon-plus'});
        return this;
    },

    menuItems: function(selection) {
        var _this = this;
        if (selection == 'main') {
            return [{
                separator: true
            }, {
                label: 'Hide all',
                alt: 'Hide all',
                icon: 'ui-icon-circle-minus',
                callback: function() {
                    _this.extensionManager.hideInstance();
                }
            }, {
                label: 'Preferences',
                alt: $.Helpers.strFormat('Preferences ({0})', _this.preferenceView.settings.shortcut),
                icon: 'ui-icon-gear',
                callback: function() {
                    _this.preferenceView.show();
                }
            }, {
                label: 'Command Palette ...',
                alt: $.Helpers.strFormat('Command Palette ({0})', _this.commandPalette.settings.shortcut),
                icon: 'ui-icon-star',
                callback: function() {
                    _this.commandPalette.show();
                }
            }, {
                separator: true
            }, {
                label: 'Logout',
                icon: 'ui-icon-power',
                callback: function() {
                    _this.logout();
                }
            }, {
                separator: true
            }, {
                label: $.Helpers.strFormat('<span class="logged-in-name">Logged-in as {0}<span>', this.config.userName),
                icon: 'ui-icon-person',
                disabled: true
            }];
        } else if (selection == 'ws' || selection == 'workspace') {
            return [{
                separator: true
            }, {
                label: 'Add new Workspace',
                disabled: !this.config.addWorkspaces,
                icon: 'ui-icon-plus',
                callback: function() {
                    _this.workspaceManager.showAddWorkspace();
                }
            }, {
                label: 'Configure Workspaces',
                alt: $.Helpers.strFormat('Command Palette ({0})', _this.workspaceManager.settings.openShortcut),
                icon: 'ui-icon-gear',
                callback: function() {
                    _this.workspaceManager.openConfigure();
                }
            }];
        }
    },

    addPaletteCommands: function() {
        var _this = this;
        this.commandPalette.add('vispa', {
            key: 'Vispa: logout',
            callback: function() {
                _this.logout();
            }
        }).add('vispa', {
            key: 'Vispa: preferences',
            callback: function() {
                _this.preferenceView.show();
            }
        }).enableContext('vispa');
        return this;
    },

    logout: function() {
        $.Helpers.redirect(this.urlHandler.dynamic('/logout'));
        return this;
    },

    handleUrlParameters: function(params) {
        if (!params || !params.url || $.Helpers.strStarts(params.url, '?')) {
            params = $.Helpers.getUrlParameters(params ? params.url : null);
        }
        if (!this.workflow.urlParametersHandled) {
            this.workflow.urlParametersHandled = true;
            // no global url operations yet, pass all to the ExtMan
            // plan: add global url channels with callbacks to listen to, once!
        }
        this.extensionManager.handleParameters(params);
        return this;
    },

    useSlimScroll: function() {
        // the slimScroll plugin is only used for
        // platform <-> browser combinations that natively
        // don't have 'smart' scroll bars
        var use = false;
        if (!$.Helpers.hasTouch()) {
            use |= $.device.win();
            use |= $.device.linux();
            use |= $.device.mac() && !$.browser.chrome && !$.browser.safari;
        }
        return use;
    },

    updateTitle: function(id) {
        var obj = this.extensionManager.reverseId(id);
        var format = '',
            title = 'Vispa',
            ext = '',
            conf = '';
        if (obj.extensionName) {
            format += ' - {0}';
            ext = $.Helpers.strCapitalize(obj.extensionName);
            if (obj.configName) {
                format += ' {1}';
                conf = $.Helpers.strCapitalize(obj.configName);
                if (obj.number || obj.number === 0) {
                    format += ' {2}';
                }
            }
            title += $.Helpers.strFormat(format, ext, conf, obj.number);
        }
        $('title').html(title);
        return this;
    },

    addPreferenceObservables: function() {
        var _this = this;
        var objs = [this.commandPalette, this.view, this.extensionView, this.extensionManager, this.preferenceHandler, this.preferenceView, this.pathBar, this.workspaceManager];
        $.each(objs, function(i, obj) {
            obj.addPreferenceObservable();
        });
        // the messenger observable has to added by hand
        var settings = {
            title: 'Messenger',
            type: 'set',
            priority: 2,
            entryOrder: ['logLevel', 'notificationMode', 'notificationDuration'],
            submit: 'vispa.cfg.submit',
            apply: function() {
                return _this.messenger.applyConfig.apply(_this.messenger, arguments);
            }
        };
        this.preferenceHandler.setupObservable('vispa', 'messenger', this.messenger.config, this.messenger.defaultConfig, settings);
        return this;
    },

    submitPreferences: function(section, name, obj) {
        var promise = $.ajax({
            url: this.urlHandler.dynamic('ajax/setvispapreference'),
            type: 'POST',
            data: {
                section: name,
                value: JSON.stringify(obj)
            }
        });
        return promise;
    },

    pathExists: function(path, type, wid) {
        var promise = $.ajax({
            url: this.urlHandler.dynamic('ajax/fs/exists'),
            type: 'POST',
            data: {
                _wid: wid || Vispa.workspaceManager.getWorkspace().id,
                path: path,
                type: type || null
            }
        });
        return promise;
    },

    // sets the content to loading mode or ends it
    setLoading: function(state) {
        if (state) {
            $(this.view.nodes.loader).css('display', 'table');
        } else {
            $(this.view.nodes.loader).hide();
        }
        return this;
    },

    setupTopics: function() {
        var _this = this;
        $.Topic('vispa.cfg.apply').subscribe(function() {
            return _this.applyConfig.apply(_this, arguments);
        });
        $.Topic('vispa.cfg.submit').subscribe(function() {
            return _this.submitPreferences.apply(_this, arguments);
        });
        return self;
    }
});

var VispaModule = Class.extend({

    init: function(name, defaultConfig, config) {
        this.name = name;
        this.config = $.Helpers.createConfig(config, this.defaultConfig);
        this.preferenceSettings = {};
        this.logger = $.Logger($.Helpers.strCapitalize(name));
    },

    startup: function() {
        return this;
    },

    applyConfig: function() {
        return this;
    },

    addPreferenceObservable: function() {
        var _this = this;
        var settings = $.extend(true, {
            title: $.Helpers.strCapitalize(this.name),
            type: 'set',
            priority: 0,
            submit: 'vispa.cfg.submit',
            apply: function() {
                return _this.applyConfig.apply(_this, arguments);
            }
        }, this.preferenceSettings);

        Vispa.preferenceHandler.setupObservable('vispa', this.name, this.config, this.defaultConfig, settings);
        return this;
    }
});