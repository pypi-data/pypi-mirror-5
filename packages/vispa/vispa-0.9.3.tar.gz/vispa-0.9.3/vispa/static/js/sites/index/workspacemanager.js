var WorkspaceManager = VispaModule.extend({

    init: function(config, workspaceData) {
        this.defaultConfig = {
            connectionTimeout: {
                descr: 'Maximum time (in ms) for establishing a workspace connection.',
                type: 'integer',
                value: 10000
            },
            nRetry: {
                descr: 'Number of tries for establishing a workspace connection. 0 means infinit.',
                type: 'integer',
                select: [0, 1, 2, 3, 4, 5],
                value: 2
            }
        };
        this._super('workspaceManager', this.defaultConfig, config);

        // attributes
        this.preferenceSettings = {
            priority: 9
        };
        this.settings = {
            openShortcut: 'ctrl+w'
        };
        this.workflow = {};
        this.workspaces = workspaceData;
        this.extensionInstances = {};
        this.state = {};
        this.workspaceConfigDefaults = {
            name: {
                type: 'string',
                value: ''
            },
            host: {
                type: 'string',
                value: ''
            },
            login: {
                type: 'string',
                value: ''
            },
            key: {
                type: 'string',
                value: ''
            },
            basedir: {
                type: 'string',
                value: ''
            },
            command: {
                type: 'string',
                value: ''
            }
        };
    },

    startup: function() {
        this.setupObservables();
        this.setupWorkspaceMenu();
        this.setupTopics();
        this.setupShortcuts();
        this.connect();

        this.logger.debug('Started');
        return this;
    },

    applyConfig: function() {
        // useLast -> dynamic
        return this;
    },

    addWorkspaceObservable: function(workspace) {
        var _this = this;
        if (!workspace.user_id) {
            return;
        }
        var btn = {
            label: 'Delete',
            icons: {
                primary: 'ui-icon-close'
            },
            click: function() {
                _this.deleteWorkspace(workspace);
            }
        };
        var settings = {
            title: workspace.name,
            type: 'ask',
            priority: 0,
            submit: 'ws.submit',
            apply: 'ws.apply',
            capitalizeTitle: false,
            entryOrder: ['name', 'host', 'login', 'key', 'basedir', 'command'],
            buttons: [btn]
        };
        Vispa.preferenceHandler.setupObservable('workspaces', workspace.id, workspace, this.workspaceConfigDefaults, settings);
        return this;
    },

    setupObservables: function() {
        var _this = this;
        $.each(this.workspaces.all, function(key, obj) {
            _this.addWorkspaceObservable(obj);
        });
        return this;
    },

    updateObservables: function() {
        var _this = this;
        $.each(Vispa.preferenceHandler.observables['workspaces'], function(id) {
            _this.updateObservable('workspaces', id);
        });
        return this;
    },

    updateObservable: function(section, id) {
        var obj = Vispa.preferenceHandler.observables[section][id]
        // update the title
        obj.settings.title = obj.config.name;
        return this;
    },

    setWorkspaces: function(connected, workspaces) {
        var _this = this;
        if (connected) {
            this.workspaces.connected = connected;
        }
        if (workspaces) {
            if (!$.isArray(workspaces)) {
                workspaces = [workspaces];
            }
            $.each(workspaces, function(i, workspace) {
                _this.workspaces.all[workspace.id] = workspace;
            });
        }
        return this;
    },

    getWorkspace: function(wid) {
        if (!wid) {
            return this.getWorkspace(this.workspaces.connected[0]);
        }
        var target;
        $.each(this.workspaces.all, function(name, workspace) {
            if (!target && workspace.id == wid) {
                target = workspace;
            }
        });
        return target;
    },

    addWorkspaceMenuEntry: function(workspace) {
        var _this = this;
        var entry = {
            label: workspace.name,
            icon: workspace.user_id ? 'ui-icon-person' : 'ui-icon-star',
            callback: function() {
                if (_this.getWorkspace().id != workspace.id) {
                    _this.setWorkspaces([workspace.id]);
                    _this.connect();
                }
            }
        };
        $.Topic('menu.ws.add').publish(entry, true);
        return this;
    },

    setupWorkspaceMenu: function() {
        var _this = this;
        $.each(this.workspaces.all, function(id, workspace) {
            _this.addWorkspaceMenuEntry(workspace);
        });
        return this;
    },

    showAddWorkspace: function() {
        var _this = this;
        var callback = function(name) {
            _this.addWorkspace(name);
        };
        $.Topic('msg.prompt').publish({
            text: 'Enter a unique name for the new Workspace:',
            title: 'Add a Workspace',
            icon: 'ui-icon-plus',
            callback: callback
        });
        return this;
    },

    addWorkspace: function(name) {
        var _this = this;
        // tell the server
        var promise = $.ajax({
            url: Vispa.urlHandler.dynamic('/ajax/addworkspace'),
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                name: name
            })
        });

        $.when(promise).then(function(response) {
            if (response.success) {
                _this.setWorkspaces(null, response.data);
                _this.addWorkspaceObservable(response.data);
                _this.addWorkspaceMenuEntry(response.data);
                _this.openConfigure(response.data);
            } else {
                $.Topic('msg.error').publish(response.msg);
            }
        });
        return this;
    },

    deleteWorkspace: function(workspace) {
        var _this = this;
        if (!workspace.user_id) {
            return this;
        }
        var promise = $.ajax({
            url: Vispa.urlHandler.dynamic('/ajax/deleteworkspace'),
            type: 'POST',
            data: {
                wid: workspace.id
            }
        });

        $.when(promise).then(function(response) {
            if (response.success) {
                // if was_selected is true, reload the page
                if (response.was_selected) {
                    $.Helpers.redirect(Vispa.urlHandler.dynamic('/'));
                } else {
                    // remove the preference observable
                    Vispa.preferenceHandler.removeObservable('workspaces', workspace.id);
                    Vispa.preferenceView.updateContent();

                    // remove the menu entry
                    $.Topic('menu.ws.remove').publish(workspace.name);
                }
            } else {
                $.Topic('msg.error').publish(response.msg);
            }
        });
        return this;
    },

    submitWorkspaceData: function(section, name, obj) {
        var promise = $.ajax({
            url: Vispa.urlHandler.dynamic('ajax/setworkspacedata'),
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(obj)
        });
        return promise;
    },

    applyWorkspaceData: function(section, name, newObj, oldObj) {
        var _this = this;

        // 1. have there been changes to the current workspace?
        // change the label of the menu entry
        $.Topic('menu.ws.modify').publish(oldObj.name, newObj.name);
        // update the label of the selected workspace
        var workspace = this.getWorkspace();
        if (String(workspace.id) == String(name)) {
            $('#header-left-label').html(newObj.name);
        }

        // 2. update the preferenceView so new names are applied
        this.updateObservable(section, name);
        Vispa.preferenceView.updateContent();

        return this;
    },

    connect: function(nTry) {
        var _this = this;
        nTry = nTry || 1;
        var workspace = this.getWorkspace();

        Vispa.setLoading(true);
        var msg = $.Helpers.strFormat('connecting to \'{0}\' ...', workspace.name);
        var obj = $.Topic('msg.log').publishBack('info', {
            text: msg,
            icon: 'ui-icon-refresh'
        })[0];
        var promise = $.ajax({
            url: Vispa.urlHandler.dynamic('/ajax/connectworkspace'),
            type: 'POST',
            data: {
                wid: workspace.id
            }
        });

        $.when(promise).then(function(response) {
            if (response.success) {
                obj.update({
                    text: $.Helpers.strFormat('connected to \'{0}\'', workspace.name),
                    icon: 'ui-icon-transferthick-e-w'
                });
                // set the workspace label
                $('#header-left-label').html(workspace.name);
                // set the pathbar base dir
                Vispa.pathBar.setValue(workspace.basedir);
                // close all full instances
                Vispa.extensionManager.removeAllFullInstances();
                // set the state
                _this.state = response.data;
                // apply the state
                Vispa.extensionManager.handleParameters(_this.state);
                // call the wrapped history callback
                Vispa.urlHandler.workflow.wrappedCallback();
                Vispa.setLoading(false);
            } else {
                var callback = function() {
                    $.Helpers.redirect(Vispa.urlHandler.dynamic('/resetworkspace'));
                };
                var msg = $.Helpers.strFormat('{0}<br />You will be redirected in 3 seconds...', response.msg);
                $.Topic('msg.error').publish({content: msg, callback: callback});
                obj.update({
                    text: $.Helpers.strFormat('\'{0}\' rejected connection', workspace.name),
                    icon: 'ui-icon-alert'
                });
                window.setTimeout(callback, 3000);
            }
        });

        // check timeout
        window.setTimeout(function() {
            if (promise.state() != 'resolved') {
                promise.abort();
                if (_this.config.nRetry && nTry >= _this.config.nRetry) {
                    // redirect
                    $.Helpers.redirect(Vispa.urlHandler.dynamic('/resetworkspace'));
                } else {
                    // retry
                    _this.connect(nTry + 1);
                }
            }
        }, this.config.connectionTimeout);

        return this;
    },

    openConfigure: function(workspace) {
        // create a new startkey based on the name of the selected workspace
        var id = workspace ? workspace.id : null;
        var key = $.Helpers.strFormat('workspaces.{0}', id || this.getWorkspace().id);
        Vispa.preferenceView.toggle(key);
        return this;
    },

    updateState: function(obj) {
        var _this = this;
        // update the state object
        $.each(obj, function(id, identifier) {
            if (identifier === null || identifier === undefined) {
                // the instance is closed
                delete _this.state[id];
            } else {
                // the instance had an update
                _this.state[id] = identifier;
            }
        });
        // tell the server
        $.post(Vispa.urlHandler.dynamic('/ajax/updateworkspacestate'), {
            wid: this.getWorkspace().id,
            state: JSON.stringify(obj)
        });
        return this;
    },

    addInstance: function(wid, instance) {
        this.extensionInstances[wid] = this.extensionInstances[wid] || [];
        this.extensionInstances[wid].push(instance);
        return this;
    },

    removeInstance: function(wid, instance) {
        if (this.extensionInstances[wid]) {
            this.extensionInstances[wid] = $.grep(this.extensionInstances[wid], function(_instance, i) {
                return _instance != instance;
            });
        }
        return this;
    },

    setupTopics: function() {
        var _this = this;
        $.Topic('ws.apply').subscribe(function() {
            return _this.applyWorkspaceData.apply(_this, arguments);
        });
        $.Topic('ws.submit').subscribe(function() {
            return _this.submitWorkspaceData.apply(_this, arguments);
        });
        return this;
    },

    setupShortcuts: function() {
        var _this = this;
        // register the shortcut for 'toggle' to 'global'
        $.Shortcuts('global').add(this.settings.openShortcut, function() {
            _this.openConfigure();
        });
    },
});