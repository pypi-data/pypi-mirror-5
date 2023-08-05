var Vispa = Class.extend({

    init: function(config, workspaceData) {
        // attributes
        this.defaultConfig = {
            requestedPath: '/',
            showAddForm: true,
            view: {},
            messenger: {},
            urlHandler: {}
        };
        this.settings = {
            redirectDelay: 1000
        };
        this.workflow = {
            connecting: false,
            selecting: false
        };
        this.config = $.extend(true, {}, this.defaultConfig, config);
        // members
        this.view = new View(this.config.view);
        this.messenger = new Messenger(this.config.messenger);
        this.urlHandler = new UrlHandler(this.config.urlHandler);

        this.workspaceData = workspaceData;
    },

    startup: function() {
        this.messenger.startup();
        this.urlHandler.startup();
        this.view.startup();
        return this;
    },

    addWorkspace: function() {
        var _this = this;
        if (this.workflow.connecting) {
            return this;
        }
        var keys = ['name', 'host', 'login', 'key', 'command', 'basedir'];
        var data = {};
        $.each(keys, function(i, key) {
            data[key] = $('#ws-' + key).val() || null;
        });
        var relevant = ['name', 'host'];
        for (var i = 0; i < relevant.length; ++i) {
            if (!data[relevant[i]]) {
                $('#ws-' + relevant[i]).focus();
                $.Topic('msg.notify').publish({
                    text: $.Helpers.strFormat('please enter a \'{0}\'', relevant[i]),
                    icon: 'ui-icon-pencil'
                });
                return this;
            }
        }
        // try to add the workspace
        this.workflow.connecting = true;
        var promise = $.ajax({
            url: this.urlHandler.dynamic('/ajax/addworkspace'),
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data)
        });
        // notification
        var obj = $.Topic('msg.notify').publishBack({
            text: $.Helpers.strFormat('connecting to \'{0}\'...', data.host),
            icon: 'ui-icon-refresh',
            duration: 0
        })[0];
        // action, when request is done
        $.when(promise).then(function(response) {
            if (!response.success) {
                obj.update({
                    text: 'connection refused',
                    icon: 'ui-icon-alert'
                });
                $.Topic('msg.error').publish(response.msg, function() {
                    $('#ws-name').focus();
                });
                _this.workflow.connecting = false;
            } else {
                obj.update({
                    text: 'connection established',
                    icon: 'ui-icon-transferthick-e-w'
                });
                window.setTimeout(function() {
                    $.Helpers.redirect(_this.urlHandler.dynamic(_this.config.requestedPath));
                }, _this.settings.redirectDelay);
            }
        });
        return this;
    },

    reset: function() {
        var keys = ['name', 'host', 'login', 'key', 'command', 'directory'];
        $.each(keys, function(i, key) {
            $('#ws-' + key).val('');
        });
        $('#ws-name').focus();
        return this;
    },

    select: function(wid, name) {
        var _this = this;
        if (this.workflow.selecting) {
            return this;
        }
        this.workflow.selecting = true;
        var promise = $.ajax({
            url: this.urlHandler.dynamic('/ajax/connectworkspace'),
            type: 'POST',
            data: {
                wid: wid,
                preload: false,
                state: false
            }
        });
        // notification
        var obj = $.Topic('msg.notify').publishBack({
            text: $.Helpers.strFormat('connecting to workspace \'{0}\'...', name),
            icon: 'ui-icon-refresh',
            duration: 0
        })[0];
        // action, when request is done
        $.when(promise).then(function(response) {
            if (response.success) {
                obj.update({
                    text: 'connection established',
                    icon: 'ui-icon-transferthick-e-w'
                });
                window.setTimeout(function() {
                    $.Helpers.redirect(_this.urlHandler.dynamic(_this.config.requestedPath));
                }, 1000);
            } else {
                obj.update({
                    text: 'connection refused',
                    icon: 'ui-icon-alert'
                });
                $.Topic('msg.error').publish(response.msg);
                _this.workflow.connecting = false;
            }
        });
        return this;
    },

    logout: function() {
        $.Helpers.redirect(this.urlHandler.dynamic('/logout'));
        return this;
    }
});