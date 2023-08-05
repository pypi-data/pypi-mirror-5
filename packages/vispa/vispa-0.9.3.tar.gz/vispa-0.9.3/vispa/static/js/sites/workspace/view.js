var View = Class.extend({

    init: function(config) {
        // attributes
        this.defaultConfig = {};
        this.config = $.extend(true, {}, this.defaultConfig, config);
    },

    startup: function() {
        this.setupMarkup();
        $('#ws-name').focus();
        this.hideOverlay();
        return this;
    },

    setupMarkup: function() {
        var _this = this;
        // hide add form?
        if (!Vispa.config.showAddForm) {
            $('#ws-add-container, #ws-add-container-header').remove();
        }
        // setup the selection content
        this.setupSelections();

        // accordion
        $('#accordion').accordion({
            header: 'h3',
            animate: {
                easing: 'easeOutExpo',
                duration: 300
            },
            activate: function(event, ui) {
                if (ui.newHeader.text() == 'Add Workspace') {
                    $('#ws-name').focus()
                }
            }
        });
        // buttons
        $('#ws-submit').button({
            icons: {
                primary: 'ui-icon-plusthick'
            }
        }).click(function() {
            Vispa.addWorkspace.apply(Vispa, arguments);
        });
        $('#ws-reset').button({
            icons: {
                primary: 'ui-icon-closethick'
            }
        }).click(function() {
            Vispa.reset.apply(Vispa, arguments);
        });
        $('#logout').button({
            icons: {
                primary: 'ui-icon-power'
            }
        }).click(function() {
            Vispa.logout.apply(Vispa, arguments);
        });
        // inputs
        var next = function(event, target) {
            var key = event.keyCode || event.which;
            if (key == 13) {
                if ($.isFunction(target)) {
                    target();
                } else {
                    $(target).focus();
                }
            }
        };
        $('#ws-name').keypress(function(event) {
            next(event, '#ws-host');
        });
        $('#ws-host').keypress(function(event) {
            next(event, '#ws-login');
        });
        $('#ws-login').keypress(function(event) {
            next(event, '#ws-key');
        });
        $('#ws-key').keypress(function(event) {
            next(event, '#ws-command');
        });
        $('#ws-command').keypress(function(event) {
            next(event, '#ws-basedir');
        });
        $('#ws-basedir').keypress(function(event) {
            next(event, function() {
                Vispa.addWorkspace.apply(Vispa, arguments);
            });
        });
        if (!$.Helpers.objectKeys(Vispa.workspaceData).length) {
            $('#accordion').accordion('option', 'active', 1);
        }
        return this;
    },

    setupSelections: function() {
        var container = $('#ws-select-container');
        $.each(Vispa.workspaceData, function(i, workspace) {
            var icon = workspace.user_id ? 'ui-icon-person' : 'ui-icon-star';
            var btn = $('<button />')
                .html(workspace.name)
                .attr('title', $.Helpers.strFormat('{0}: {1}', i, JSON.stringify(workspace)))
                .button({
                    icons: {
                        primary: icon
                    }
                }).click(function() {
                    Vispa.select(workspace.id, workspace.name);
                });
            container.append(btn);
        });
        return this;
    },

    hideOverlay: function(fx) {
        fx = $.extend(true, {
            duration: 50,
            easing: 'linear'
        }, fx);
        var dfd = $.Deferred();
        $('#startup-overlay').fadeOut(fx.duration, fx.easing, dfd.resolve);
        return dfd.promise();
    }
});