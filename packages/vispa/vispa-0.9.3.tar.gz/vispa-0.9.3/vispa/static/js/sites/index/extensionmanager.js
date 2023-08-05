var ExtensionManager = VispaModule.extend({

    init: function(config, extensionConfig) {
        this.defaultConfig = {
            reuseInstances: {
                descr: 'When creating a new instance, use an existing one if they have the same identifier (i.e. path, etc)?',
                type: 'boolean',
                value: true
            }
        };
        this._super('extensionManager', this.defaultConfig, config);

        // attributes
        this.preferenceSettings = {
            priority: 10
        };
        this.settings = {
            argSeparator: ':'
        };
        this.workflow = {
            urlChannelsFired: false
        };
        this.extensionConfig = extensionConfig;
        this.extensionStore = {};
        this.instances = {
            full: []
        };
        this.fileHandlers = {};
        this.urlChannelHandlers = {};

        // register the extension logger
        $.Logger('Extension');
    },

    startup: function() {
        this.applyConfig();
        this.setupTopics();

        this.logger.debug('Started');
        return this;
    },

    applyConfig: function() {
        // reuseInstances => dynamic
        return this;
    },

    getExtension: function(extension) {
        if (typeof(extension) == 'string') {
            if (this.extensionStore[extension]) {
                return this.extensionStore[extension];
            } else {
                return null;
            }
        } else {
            return extension;
        }
    },

    getFactory: function(factory, extension) {
        if (typeof(factory) == 'string') {
            extension = this.getExtension(extension);
            if (!extension) {
                return null;
            }
            return extension._getFactory(factory);
        } else {
            return factory;
        }
    },

    getInstance: function(instance) {
        if (typeof(instance) == 'string') {
            var obj = this.reverseId(instance);
            var factory = this.getFactory(obj.factoryKey, obj.extensionName);
            if (!factory) {
                return null;
            }
            return factory._instances[instance];
        } else {
            return instance;
        }
    },

    register: function(cls) {
        extension = new cls();

        if (!extension.name) {
            var msg = 'Tried to register an Extension without a name!';
            $.Topic('msg.error').publish(msg);
            return this;
        }

        if (this.extensionStore[extension.name]) {
            var msg = $.Helpers.strFormat("Extension '{0}' already registered!", extension.name);
            $.Topic('msg.error').publish(msg);
            return this;
        }

        this.extensionStore[extension.name] = extension;
        this.setupExtension(extension);
        this.logger.info($.Helpers.strFormat('Extension \'{0}\' added', extension.name));
        $.Topic('extenstion.added').publish(extension.name);
        return this;
    },

    setupExtension: function(extension) {
        var _this = this;

        // setup the logger
        extension.logger = $.Logger($.Helpers.strFormat('Extension.{0}', extension.name));

        // setup the main menu entries
        if (extension.menuEntries && extension.menuEntries.length) {
            $.Topic('menu.main.add').publish(extension.menuEntries, true);
        }

        // register the file handlers
        $.each(extension.fileHandlers, function(fileExt, handler) {
            _this.registerFileHandler(extension, fileExt, handler);
        });

        // register the url channel handlers
        $.each(extension.urlChannelHandlers, function(channel, handler) {
            _this.registerUrlChannelHandler(extension, channel, handler);
        });

        // setup each factory
        $.each(extension.factories, function(key, factory) {
            _this.setupFactory(extension, factory, key);
        });

        return this;
    },

    setupFactory: function(extension, factory, key) {
        var _this = this;
        // let the factory know about its extension (owner), name and key
        // 'name' is the place where to find this factory in its extension's 'factories' object
        // 'key' is something like '<extension_name>-<name>'
        factory._extension = extension;
        factory._key = key;
        factory._id = this.createId(extension, factory);

        // setup the logger
        factory._logger = $.Logger($.Helpers.strFormat('Extension.{0}.{1}', extension.name, factory.name));

        // add its preference variable
        factory._addPreferenceObservable();

        // setup the main menu entries
        if (factory.menuEntries && factory.menuEntries.length) {
            $.Topic('menu.main.add').publish(factory.menuEntries, true);
        }

        // register the file handlers
        $.each(factory.fileHandlers, function(fileExt, handlers) {
            _this.registerFileHandler(factory, fileExt, handlers);
        });

        // register the url channel handlers
        $.each(factory.urlChannelHandlers, function(channel, handler) {
            _this.registerUrlChannelHandler(factory, channel, handler);
        });

        // behavior depends on the factory type
        if (factory instanceof ExtensionFactoryFull) {
            // add an defaultConfig entry for the shorthand menu entries
            if (!factory.defaultConfig.droppedMenuEntries) {
                factory.defaultConfig.droppedMenuEntries = {
                    type: 'list',
                    value: [],
                    hidden: true
                };
            }
        }

        return this;
    },

    createInstance: function(extension, factory, number, byUrl, wid) {
        var args = $.makeArray(arguments);
        args.splice(0, 5);

        // the first arg is supposed to be the identifier
        // if it's set and there is aleady an instance of that factory
        // with that identifier, switch the view to that instance
        // but don't create a new one
        var identifier = args.length ? args[0] : null;
        if (identifier !== null && identifier !== undefined) {
            var targetInstance = null;
            $.each(factory._instances, function(i, instance) {
                var _identifier = instance.getIdentifier();
                if (_identifier == identifier) {
                    targetInstance = instance;
                    return false;
                }
            });
            if (targetInstance && this.config.reuseInstances) {
                var show = true;
                // don't show it if the current full instance has the same factory
                // and the same identifier
                var ci = this.getInstance(Vispa.extensionView.workflow.currentFullInstance);
                if (ci) {
                    if (ci._factory._id == targetInstance._factory._id && ci.getIdentifier() == identifier) {
                        show = false;
                    }
                }
                if (show) {
                    this.showInstance(targetInstance, byUrl);
                }
                return this;
            }
        }

        // max_instances reached?
        var max = factory.maxInstances;
        var count = $.Helpers.objectKeys(factory._instances).length;
        if (max && count >= max) {
            $.Topic('msg.error').publish('\'maxInstances\' reached!');
            return this;
        }

        // create an instance
        var config = this.extensionConfig[factory._id] = this.extensionConfig[factory._id] || {};
        config = $.Helpers.createConfig(config, factory.defaultConfig);
        var instance = this.constructorApply(factory.constructor, config, args);

        // before first
        var factoryHasProduced = factory._hasProduced;
        factory._hasProduced = true;
        if (!factoryHasProduced && instance.beforeFirst() === false) {
            return this;
        }

        // before open
        if (instance.beforeOpen() === false) {
            return this;
        }

        // store extension, factory and workspace id
        instance._extension = extension;
        instance._factory = factory;
        wid = wid || Vispa.workspaceManager.getWorkspace().id;
        instance._wid = wid;
        // tell the workspace manager to keep track of this instance
        Vispa.workspaceManager.addInstance(wid, instance);

        // update number
        number = this.makeNumber(factory, number);
        instance._number = number;

        // create a unique id
        var id = this.createId(extension, factory, number);
        instance._id = id;
        factory._instances[id] = instance;

        // setup the content
        this.setupInstance(instance);

        // call the render method
        instance.render(instance._node);

        // ready
        instance.ready();

        // switch to that instance content if its workspace is visible
        if (wid == Vispa.workspaceManager.getWorkspace().id) {
            this.showInstance(instance, byUrl);
        }

        // afterOpen
        instance.afterOpen();

        return this;
    },

    setupInstance: function(instance) {
        instance = this.getInstance(instance);
        if (!instance) {
            return this;
        }

        // setup the logger
        instance._logger = $.Logger($.Helpers.strFormat('Extension.{0}.{1}.{2}', instance._extension.name, instance._factory.name, instance._number));

        // behavior depends on the instance type
        // 'full' instance
        if (instance instanceof ExtensionContentFull) {
            // add the id to full instances
            this.instances.full.push(instance._id);

            // add the 'close' menu entry
            var items = [{
                label: 'Close',
                icon: 'ui-icon-close',
                callback: function() {
                    instance._close();
                }
            }];
            // add a separator?
            if (instance.menuEntries.length) {
                items.unshift({
                    separator: true
                });
            }
            instance.menuEntries = instance.menuEntries.concat(items);
            // make all menu entries draggable
            var addDragClass = function(entry) {
                if (entry.children && entry.children.items && entry.children.items.length) {
                    $.each(entry.children.items, function(i, item) {
                        addDragClass(item);
                    });
                } else {
                    if (entry.dragClass === undefined && !entry.separator) {
                        entry.dragClass = $.Helpers.strFormat('extension-{0}-menu-draggable', instance._id);
                    }
                }
            }
            $.each(instance.menuEntries, function(i, entry) {
                addDragClass(entry);
            });

            // add a $.Shortcuts object, named by the id
            instance._shortcuts = $.Shortcuts(instance._id);

            // create the view
            var showBadge = instance._wid == Vispa.workspaceManager.getWorkspace().id;
            var viewData = Vispa.extensionView.addFullInstance(instance, showBadge);

            // create the content code as _node for convenience
            instance._node = viewData.content;

            // store the view data in the instance
            instance._viewData = viewData;
        }
        return this;
    },

    removeInstance: function(instance) {
        instance = this.getInstance(instance);
        if (!instance) {
            return this;
        }
        // call before close
        if (instance.beforeClose() === false) {
            return this;
        }
        // remove it from the view
        // behavior depends on the instance type
        // 'full' instance
        if (instance instanceof ExtensionContentFull) {
            // is it visible?
            if (Vispa.extensionView.workflow.currentFullInstance == instance._id) {
                this.updateUrl();
            }

            // tell the workspace manager
            var state = {};
            state[instance._id] = null;
            Vispa.workspaceManager.updateState(state);

            // empty its shortcuts
            instance._shortcuts.disable().empty();
            Vispa.extensionView.removeFullInstance(instance);

            // remove the id from full instances
            var idx = $.inArray(instance._id, this.instances.full);
            if(idx >= 0) {
                this.instances.full.splice(idx, 1);
            }
        }
        // call after close
        instance.afterClose();
        // remove its data
        Vispa.workspaceManager.removeInstance(instance._wid, instance);
        delete instance._factory._instances[instance._id];
        delete instance;
        return this;
    },

    removeAllInstances: function() {
        this.removeAllFullInstances();
        return this;
    },

    removeAllFullInstances: function() {
        var _this = this;
        var ids = this.instances.full.concat();
        $.each(ids, function(i, id) {
            _this.removeInstance(id);
        });
        return this;
    },

    showInstance: function(instance, byUrl) {
        instance = this.getInstance(instance);
        if (instance instanceof ExtensionContentFull) {
            // already shown?
            if (Vispa.extensionView.workflow.currentFullInstance == instance._id) {
                return this;
            }
            // call before show
            if (instance.beforeShow() === false) {
                return this;
            }

            // handle a currentFullInstance
            var ci = this.getInstance(Vispa.extensionView.workflow.currentFullInstance);
            if (ci) {
                // call beforeHide
                if (ci.beforeHide() === false) {
                    return this;
                }
                // disable shortcuts
                ci._shortcuts.disable();
                // hide
                // 2. arg: fx, 3. arg: showWelcome
                Vispa.extensionView.hideFullInstance(ci, {
                    duration: 0
                }, false);
                // call afterHide
                ci.afterHide();
            }

            // update the url?
            if (!byUrl) {
                this.updateUrl(instance);
            }

            // update the preference handler data
            var obj = Vispa.preferenceHandler.observables['extensions'][instance._factory._id]
            // observable
            obj.config = instance._config;
            // apply callback
            obj.settings.apply = function() {
                return instance.applyConfig.apply(instance, arguments);
            }

            // enable the shortcuts object
            instance._shortcuts.enable();

            // update the view
            Vispa.extensionView.showFullInstance(instance, {
                duration: 0
            });

            // call onResize
            instance.onResize();

            // call afterShow
            instance.afterShow();

            // fetch messages for the context <instance._id>
            $.Topic('msg.fetch').publish(instance._id);
        }
        return this;
    },

    hideInstance: function(instance, byUrl) {
        instance = this.getInstance(instance);
        // behavior depends on the instance type
        if (!instance) {
            Vispa.extensionView.hideCurrentInstance(byUrl);
        } else if (instance instanceof ExtensionContentFull) {
            // visible now?
            if (Vispa.extensionView.workflow.currentFullInstance != instance._id) {
                return this;
            }
            // call beforeHide
            if (instance.beforeHide() === false) {
                return this;
            }
            // update the url?
            if (!byUrl) {
                this.updateUrl();
            }

            // disable shortcuts
            instance._shortcuts.disable();
            // hide
            // 2. arg: fx, 3. arg: showWelcome
            Vispa.extensionView.hideFullInstance(instance, null, true);
            // call afterHide
            instance.afterHide();
        }
        return this;
    },

    handleParameters: function(params) {
        var _this = this;
        if (!$.Helpers.objectKeys(params).length) {
            return this;
        }

        // procedure for each key-value pair:
        // 1. check if an extension can receive the key
        //      -> yes: step 2
        //      -> no: store the pair (rest), abort loop
        // 2. check if the target extension with the given number
        //    is already opened
        //      -> yes: forward the value to that instance
        //      -> no: create a new instance with the given number
        //             as the 'id part'.

        // first distinguish between parameter objects and a url in an object
        if ($.Helpers.objectKeys(params).length == 1 && params.url) {
            // cut until there's a '?'
            params = $.Helpers.getUrlParameters();
        }
        var rest = {};
        var hit = false;
        $.each(params, function(key, value) {
            if (!key) {
                return;
            }
            // try to analyse the key
            var obj = _this.reverseId(key);
            if (!obj) {
                rest[key] = value;
                return;
            }
            var extension = _this.extensionStore[obj.extensionName];
            if (!extension) {
                rest[key] = value;
                return;
            }
            var factory = extension.factories[obj.factoryKey];
            if (!factory) {
                rest[key] = value;
                return;
            }
            if (!obj.number && obj.number !== 0) {
                // create a new instance
                var args = [extension, factory, null, true, null].concat(_this.splitURLArgs(value));
                _this.createInstance.apply(_this, args);
            } else if (!factory._getInstance(key)) {
                var args = [extension, factory, obj.number, true, null].concat(_this.splitURLArgs(value));
                _this.createInstance.apply(_this, args);
            } else {
                console.log('pass', key, value);
                _this.showInstance(key, true);
            }
            hit = true;
        });
        if (!hit) {
            this.hideInstance(null, true);
        }
        // try to handle the unused parameters via url channels
        this.handleUrlChannels(rest);
        return this;
    },

    updateUrl: function(instance, fire) {
        instance = this.getInstance(instance);
        var url = '/';
        if (instance) {
            url = instance._getUrlParameters(true);
            // tell the workspace manager about that change
            Vispa.workspaceManager.updateState(instance._getUrlParameters());
        }
        // the third parameter is the 'fire' flag
        $.History().push(Vispa.urlHandler.dynamic(url), undefined, fire);
        return this;
    },

    handleUrlChannels: function(obj) {
        var _this = this;
        if (this.workflow.urlChannelsFired) {
            return this;
        }
        $.each(obj, function(channel, value) {
            var handler = _this.getDefaultUrlChannelHandler(channel);
            if (handler && handler.callback) {
                handler.callback.apply(null, _this.splitURLArgs(value));
            }
        });
        this.workflow.urlChannelsFired = true;
        return this;
    },

    registerFileHandler: function(owner, fileExtension, handler) {
        var obj = this.fileHandlers[fileExtension] = this.fileHandlers[fileExtension] || [];
        var data = $.extend({
            owner: owner
        }, handler);
        obj.push(data);
        return this;
    },

    getFileHandlers: function(fileExtension, sorted) {
        var handlers = this.fileHandlers[fileExtension];
        if (!handlers || sorted !== true) {
            return handlers || [];
        }
        return this.sortHandlers(handlers);
    },

    getDefaultFileHandler: function(fileExtension) {
        var handlers = this.getFileHandlers(fileExtension);
        var max, target;
        $.each(handlers, function(i, entry) {
            if ((!max && max !== 0) || entry.priority > max) {
                max = entry.priority;
                target = entry;
            }
        });
        return target;
    },

    registerUrlChannelHandler: function(owner, channel, handler) {
        var obj = this.urlChannelHandlers[channel] = this.urlChannelHandlers[channel] || [];
        var data = $.extend({
            owner: owner
        }, handler);
        obj.push(data);
        return this;
    },

    getUrlChannelHandlers: function(channel, sorted) {
        var handlers = this.urlChannelHandlers[channel];
        if (!handlers || sorted !== true) {
            return handlers || [];
        }
        return this.sortHandlers(handlers);
    },

    getDefaultUrlChannelHandler: function(channel) {
        var handlers = this.getUrlChannelHandlers(channel);
        var max, target;
        $.each(handlers, function(i, entry) {
            if ((!max && max !== 0) || entry.priority > max) {
                max = entry.priority;
                target = entry;
            }
        });
        return target;
    },

    sortHandlers: function(handlers) {
        var dummy = handlers.concat([]);
        var sortedHandlers = [];
        while (dummy.length) {
            var maxHandler = null;
            var idx = null;
            $.each(dummy, function(i, handler) {
                if (!maxHandler) {
                    maxHandler = handler;
                    idx = i;
                    return;
                }
                if (handler.priority > maxHandler.priority) {
                    maxHandler = handler;
                    idx = i;
                }
            });
            if (!maxHandler) {
                break;
            }
            sortedHandlers.push(maxHandler);
            dummy.splice(idx, 1);
        }
        return sortedHandlers;
    },

    constructorApply: function(cls, factory, a) {
        // we need this method since apply doesn't work for constructors
        if (!$.isArray(a) || !a.length) {
            return new cls(factory);
        }
        switch (a.length) {
            case 1:
                return new cls(factory, a[0]);
            case 2:
                return new cls(factory, a[0], a[1]);
            case 3:
                return new cls(factory, a[0], a[1], a[2]);
            case 4:
                return new cls(factory, a[0], a[1], a[2], a[3]);
            case 5:
                return new cls(factory, a[0], a[1], a[2], a[3], a[4]);
            case 6:
                return new cls(factory, a[0], a[1], a[2], a[3], a[4], a[5]);
            case 7:
                return new cls(factory, a[0], a[1], a[2], a[3], a[4], a[5], a[6]);
            case 8:
                return new cls(factory, a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7]);
            case 9:
                return new cls(factory, a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7], a[8]);
            case 10:
                return new cls(factory, a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7], a[8], a[9]);
            default:
                return new cls(factory, a);
        }
    },

    makeNumber: function(factory, number) {
        if (!number && number !== 0) {
            number = 0;
        }
        // taken?
        if ($.inArray(number, factory._numbers) >= 0) {
            // yes, so find a minimal, new one
            number = null;
            var max = Math.max.apply(Math, factory._numbers);
            for (var i = 0; i < max; ++i) {
                if ($.inArray(i, factory._numbers) < 0) {
                    number = i;
                    break;
                }
            }
            if (number === null) {
                number = max + 1;
            }
        }
        factory._numbers.push(number);
        return number;
    },

    createId: function(extension, factory, number) {
        if (number || number === 0) {
            return $.Helpers.strFormat('{0}-{1}-{2}', extension.name, factory._key, number);
        } else {
            return $.Helpers.strFormat('{0}-{1}', extension.name, factory._key);
        }
    },

    reverseId: function(id) {
        id = id || '';
        var parts = id.split('-');
        if (parts.length == 2) {
            return {
                extensionName: parts[0],
                factoryKey: parts[1]
            };
        } else if (parts.length == 3) {
            var number = parseInt(parts[2])
            return {
                extensionName: parts[0],
                factoryKey: parts[1],
                number: !isNaN(number) ? number : parts[2]
            };
        }
        return {};
    },

    joinURLArgs: function() {
        var args = $.makeArray(arguments);
        if (!args.length) {
            return null;
        }
        args = $.map(args, function(arg) {
            return String(arg);
        });
        return args.join(this.settings.argSeparator);
    },

    splitURLArgs: function(s) {
        if (!s) {
            return [];
        }
        return s.split(this.settings.argSeparator);
    },

    submitPreferences: function(section, name, obj) {
        var promise = $.ajax({
            url: Vispa.urlHandler.dynamic('ajax/setextensionpreference'),
            type: 'POST',
            data: {
                key: name,
                value: JSON.stringify(obj)
            }
        });
        return promise;
    },

    getPath: function(instance, method) {
        var name = instance;
        if (typeof(instance) != 'string') {
            name = instance._extension.name;
        }
        return Vispa.urlHandler.dynamic('extensions', name, method);
    },

    fetchMessages: function() {
        // current full instance
        $.Topic('msg.fetch').publish(Vispa.extensionView.workflow.currentFullInstance);
        return this;
    },

    setupTopics: function() {
        var _this = this;
        $.Topic('extman.register').subscribe(function() {
            return _this.register.apply(_this, arguments);
        });
        $.Topic('extman.cfg.submit').subscribe(function() {
            return _this.submitPreferences.apply(_this, arguments);
        });
        $.Topic('msg.pushed').subscribe(function() {
            return _this.fetchMessages.apply(_this, arguments);
        });
        return this;
    }
});


// Extension Base class
var ExtensionBase = Class.extend({

    init: function() {

        // the name of the extension should match the folder name in vispa/extensions/
        // and is used for id creation
        this.name = null;

        // the map/object for storing factories
        // their keys are used for id creation
        this.factories = {};

        // menu entries for the main menu
        // an item may look like: { label: 'new ...', icon: 'ui-icon-plus', callback: function(){} }
        // submenus can be added by using the entry: children: { id: <submenuid>, items: [] }
        this.menuEntries = [];

        // file handlers
        // e.g.: { txt: { priority: 5, callback: function(){} } }
        //       will listen to txt files with priority 5
        this.fileHandlers = {};

        // url channel handlers
        // e.g.: { channelA: { priority: 3, callback: function(){} } }
        //       will listen to urls like 'localhost/?cannelA=<somevalue>' with priority 3
        this.urlChannelHandlers = {};

        // the logger object for this extension
        // e.g.: this.logger.debug(<logmessage>), this.logger.level('info'), this.logger.en/disable()
        this._logger = null;
    },

    _getFactory: function(key) {
        return this.factories[key];
    },

    _countFactories: function() {
        return $.Helpers.objectKeys(this.factories).length;
    },

    _countInstances: function() {
        var n = 0;
        $.each(this.factories, function(key, factory) {
            n += factory._countInstances();
        });
        return n;
    }
});


// ExtensionFactory Base class
var ExtensionFactoryBase = Class.extend({

    init: function() {

        // a config object that is the default for each content
        // produced by this factory
        // the structure should match the preferenceHandler requirements
        this.defaultConfig = {};
        // additional settings for the object that is passed to the preferenceHandler
        this.preferenceSettings = {};

        // a reference to the (owning) extension
        this._extension = null;
        // the key of this factory in the extension's content attribute
        this._key = null;
        // the id of this factory, basically '<extensionName>-<key>'
        this._id = null;

        // used numbers of instances of this factory
        this._numbers = [],
        // a map/object for storing content instances
        // the keys are the ids if the content instances
        this._instances = {};
        // has this factory produced at least once?
        this._hasProduced = false;
        // a reference to the content class this factory will
        // produces instances of
        this.constructor = null;

        // the maximium number of instances this factory
        // should hold at the same time
        this.maxInstances = 0;
        // an additional, optional name for this factory
        // that may be used by instances
        this.name = 'FactoryName';
        // menu entries for the main menu (usage: see ExtensionBase)
        this.menuEntries = [];
        // file handlers (usage: see ExtensionBase)
        this.fileHandlers = {};
        // url channel handlers (usage: see ExtensionBase)
        this.urlChannelHandlers = {};
        // the logger object for this factory (usage: see ExtensionBase)
        this._logger = null;
    },

    // creates a content instance
    // all arguments passed to this function are passed to the content instance's init function
    _create: function() {
        var args = $.makeArray(arguments);
        args = [this._extension, this, null, false, null].concat(args);
        Vispa.extensionManager.createInstance.apply(Vispa.extensionManager, args);
        return this;
    },

    // adds a preference observable to the preferenceHandler based on defaultConfig
    _addPreferenceObservable: function() {
        var _this = this;
        var settings = $.extend(true, {
            title: $.Helpers.strCapitalize(this.name),
            type: 'set',
            priority: 0,
            submit: 'extman.cfg.submit',
            apply: null
        }, this.preferenceSettings);
        // create a dummy config, that holds an config object, that is
        // exptected by the preferenceHandler and contains the data of the defaultObject
        // and the config received from the server
        var dummyConfig = $.Helpers.createConfig(Vispa.extensionManager.extensionConfig[this._id], this.defaultConfig);
        // tell the extensionManager that the config of this factory changed
        // by syncing the references to the config object: preferenceHandler <-> extensionManager
        Vispa.extensionManager.extensionConfig[this._id] = dummyConfig;
        Vispa.preferenceHandler.setupObservable('extensions', this._id, dummyConfig, this.defaultConfig, settings);
        return this;
    },

    // returns the content instance of this factory with a specific id 
    _getInstance: function(id) {
        return this._instances[id];
    },

    // counts the number of currently hold content instances
    _countInstances: function() {
        return $.Helpers.objectKeys(this._instances).length;
    }
});


// ExtensionContent Base class
var ExtensionContentBase = Class.extend({

    // there might be additional arguments
    init: function(config) {

        // a reference to the (owning) extension
        this._extension = null;
        // a reference to the (owning) factory
        this._factory = null;
        // the id of this instance, basically '<extensionName>-<factoryKey>-<number>'
        this._id = null;
        // the id of the workspace this instance was opened in/belongs to
        this._wid
        // the number of this content instance that is used for id creation
        this._number = null;
        // the config object representing the current preferences for this instance/factory
        this._config = config;
        // view data of this content instance: { content: DOMNode, loader: DOMNode, ... }
        this._viewData = null;
        // the logger object for this factory (usage: see ExtensionBase)
        this._logger = null;
    },

    // closes this instance
    _close: function() {
        Vispa.extensionManager.removeInstance(this);
        return this;
    },

    // creates an object: id -> current identifier
    // the output can url formatted
    _getUrlParameters: function(format, qmark) {
        var obj = {};
        obj[this._id] = this.getIdentifier();
        if (format) {
            obj = $.Helpers.formatUrlParameters(obj, qmark);
        }
        return obj;
    },

    // creates an ajax or static path for this instance
    _getPath: function(method) {
        return Vispa.urlHandler.dynamic('extensions', this._extension.name, method);
    },

    // sets the content to loading mode or ends it
    _setLoading: function(state) {
        if (this._viewData && this._viewData.content) {
            if (state) {
                $(this._viewData.loader).css('display', 'table');
            } else {
                $(this._viewData.loader).hide();
            }
        }
        return this;
    },

    // applies the current config
    applyConfig: function() {
        return this;
    },

    // return the current identifier
    getIdentifier: function() {
        return null;
    },

    // return the current title
    // default: use the factory's name
    getTitle: function() {
        return this._factory.name;
    },

    // returns a value for a given url channel
    // (used when creating urls with a generator)
    getUrlChannelValue: function(channel) {
        return null;
    },

    // called before creation, when this is the first content instance
    // return false -> prevent creation
    beforeFirst: function() {
        return true;
    },

    // called right before this content instance is opened
    // return false -> prevent opening
    beforeOpen: function() {
        return true;
    },

    // called after this content instance is opened
    afterOpen: function() {},

    // called before this content instance is closed
    // return false -> prevent closing
    beforeClose: function() {
        return true;
    },

    // called after this content instance is closed
    afterClose: function() {},

    // called when the content of this instance is parsed the first time
    ready: function() {
        this._setLoading(false);
        return this;
    },

    // this method should render the the instance's content into the _node
    render: function(node) {
        return this;
    }
});


// ExtensionFactory Base class for 'full' window instances
var ExtensionFactoryFull = ExtensionFactoryBase.extend({

    init: function() {
        // call the super-init
        this._super();

        // TODO
    }
});


// ExtensionContent Base class for 'full' window instances
var ExtensionContentFull = ExtensionContentBase.extend({

    // there might be additional arguments
    init: function(config) {
        // call the super init
        this._super(config);

        // the shortcut handler for this full content instance
        // usage: this._shortcuts.subscribe('ctrl+f', function(){});
        this._shortcuts = null;
        // menu entries for the extension menu (usage: see ExtensionBase)
        this.menuEntries = [];
    },

    // updates the badge fot this full content based on the value
    // returned by 'getTitle'
    _updateBadge: function() {
        $(this._viewData.badge).data('update')(this.getTitle(), this.getIdentifier());
        return this;
    },

    // called before this full content instance is shown
    // return false -> prevent showing
    beforeShow: function() {
        return true;
    },

    // called after this full content instance is shown
    afterShow: function() {},

    // called before this full content instance is hidden
    // return false -> prevent hiding
    beforeHide: function() {
        return true;
    },

    // called after this full content instance is hidden
    afterHide: function() {},

    // called when the window is resized or the size of a
    // component that resizes this content is changed
    onResize: function() {}
});