var CodeEditor = Class.extend({

    init: function(instance, path) {
        this.instance = instance;

        this.workflow = {
            path: path,
            content: content,
            mTime: null,
            modified: false
        };

        this.ace = null;
    },

    ready: function() {
        var _this = this;
        // initialize ace
        this.ace = ace.edit(this.instance.nodes.aceNode);

        // load the content
        var promise = this.load();

        // the next steps are proceeded deferred
        $.when(promise).then(function() {
            // what happens on change? => set modified
            _this.ace.on('change', function() {
                var hasChanges = _this.ace.getValue() != _this.workflow.content;
                var doUpdateBadge = false;
                if (hasChanges != _this.workflow.modified) {
                    // change the badge title
                    doUpdateBadge = true;
                }
                _this.workflow.modified = hasChanges;
                if (doUpdateBadge) {
                    _this.instance._updateBadge();
                }
            });

        });
        // setup shortcuts
        this.setupShortcuts();

        return this;
    },

    load: function(path) {
        path = path || this.workflow.path;
        var _this = this;
        var promise = $.ajax({
            type: 'POST',
            url: this.instance._getPath('getcontent'),
            data: {
                _wid: this.instance._wid,
                path: path
            }
        });
        this.instance._setLoading(true);

        $.when(promise).then(function(response) {
            if (response.success) {
                _this.ace.getSession().setMode($.Helpers.strFormat('ace/mode/{0}', _this.getAceMode(path)));
                _this.ace.setValue(response.content);
                //_this.ace.focus();
                _this.ace.gotoLine(1);
                _this.ace.gotoPageUp();
                // store content and mtime
                _this.workflow.content = response.content;
                _this.workflow.mTime = response.mtime;
                _this.workflow.modified = false;
                // update the badge
                _this.instance._updateBadge();
            } else {
                $.Topic('msg.error').publish(response.msg);
            }
            _this.instance._setLoading(false);
        });
        return promise;
    },

    save: function() {
        var _this = this;
        if (!this.workflow.modified) {
            return this;
        }
        var content = this.ace.getValue();
        if (content == this.workflow.content) {
            this.workflow.modified = false;
            this.instance._updateBadge();
            $.Topic('msg.log').publish('info', {
                text: 'Saved',
                icon: 'ui-icon-check'
            });
            return this;
        }

        // there was a real change so tell the server
        var promise = $.ajax({
            type: 'POST',
            url: this.instance._getPath('savecontent'),
            data: {
                _wid: this.instance._wid,
                path: this.workflow.path,
                content: content
            }
        });
        var msgObject = $.Topic('msg.log').publishBack('info', {
            text: 'Saving',
            icon: 'ui-icon-refresh'
        })[0];

        $.when(promise).then(function(response) {
            if (response.success) {
                _this.workflow.content = content;
                _this.workflow.mTime = response.mtime;
                _this.workflow.modified = false;
                _this.instance._updateBadge();
                msgObject.update({
                    text: 'Saved',
                    icon: 'ui-icon-check'
                });
            } else {
                $.Topic('msg.error').publish(response.msg);
                msgObject.update({
                    text: 'Saving failed',
                    icon: 'ui-icon-alert'
                });
            }
        });
        return this;
    },

    checkMTime: function() {
        // only check, when mTime is set
        if (!this.workflow.mTime) {
            return this;
        }
        var _this = this;
        var promise = $.ajax({
            type: 'POST',
            url: this.instance._getPath('checkmtime'),
            data: {
                _wid: this.instance._wid,
                path: this.workflow.path,
                mtime: this.workflow.mTime
            }
        });

        $.when(promise).then(function(response) {
            if (response.success) {
                if (!response.check) {
                    _this.load();
                    // TODO: show dialog?
                }
            } else {
                $.Topic('msg.error').publish(response.msg);
            }
        });
    },

    setupShortcuts: function() {
        var _this = this;
        this.instance._shortcuts.add('ctrl+s', function() {
            _this.save();
        });
        // we need to add them to the ace instance as well
        // since ace catches all shortcuts by itself
        var cmds = [{
            bindKey: 'ctrl+s',
            exec: function() {
                _this.save();
            }
        },
        // the next commands are hardcoded and defined by the vispa gui
        // preferenceView.toggle
        {
            bindKey: Vispa.preferenceView.settings.shortcut,
            exec: function() {
                Vispa.preferenceView.toggle();
            }
        },
        // commandPalette.toggle
        {
            bindKey: Vispa.commandPalette.settings.shortcut,
            exec: function() {
                Vispa.commandPalette.toggle();
            }
        },
        // workspaceManager.openConfigure
        {
            bindKey: Vispa.workspaceManager.settings.openShortcut,
            exec: function() {
                Vispa.workspaceManager.openConfigure();
            }
        },
        // extensionView.goToFullInstance
        {
            bindKey: Vispa.extensionView.settings.shortcuts.shiftLeft,
            exec: function() {
                Vispa.extensionView.goToFullInstance(false);
            }
        }, {
            bindKey: Vispa.extensionView.settings.shortcuts.shiftRight,
            exec: function() {
                Vispa.extensionView.goToFullInstance(true);
            }
        }];
        // dynamically add the extensionView.goToFullInstance commands
        $.each([1, 2, 3, 4, 5, 6, 7, 8, 9], function(i, key) {
            cmds.push({
                bindKey: $.Helpers.strFormat(Vispa.extensionView.settings.shortcuts.shiftTemplate, key),
                exec: function() {
                    Vispa.extensionView.goToFullInstance(key);
                }
            });
        });
        this.ace.commands.addCommands(cmds);
        // other ace related shortcuts:
        // https://github.com/ajaxorg/ace/wiki/Default-Keyboard-Shortcuts

        return this;
    },

    getAceMode: function(path) {
        var ext = $.Helpers.strExtension(path);
        if (!ext) {
            return 'python';
        }
        switch (ext.toLowerCase()) {
            case 'c':
            case 'cpp':
            case 'h':
                return 'c_cpp';
            case 'xml':
                return 'xml';
            case 'js':
                return 'javascript';
            case 'css':
                return 'css';
            case 'sh':
                return 'sh';
            case 'txt':
                return 'text';
            case 'py':
            default:
                return 'python';
        }
    }
});