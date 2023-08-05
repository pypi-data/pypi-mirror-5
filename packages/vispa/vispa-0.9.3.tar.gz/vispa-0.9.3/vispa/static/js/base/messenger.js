// (global) log levels
window.logLevels = {
    all: 0,
    trace: 2,
    debug: 4,
    info: 6,
    warn: 8,
    error: 10,
    fatal: 12,
    off: 20
};

var Messenger = Class.extend({

    init: function(config) {
        // attributes
        this.defaultConfig = {
            notificationDuration: {
                descr: 'The duration a notification is shown',
                range: [0, 20000],
                type: 'integer',
                value: 5000
            },
            notificationMode: {
                descr: 'The alignment of notifications',
                select: ['left', 'right'],
                type: 'string',
                value: 'left'
            },
            logLevel: {
                descr: 'The log level',
                select: ['all', 'trace', 'debug', 'info', 'warn', 'error', 'fatal', 'off'],
                type: 'string',
                value: 'info'
            }
        };
        this.settings = {
            defaultContext: 'global',
            defaultTarget: '#body-wrapper',
            defaultType: 'info',
            notificationFx: {duration: 50, easing: 'linear'}
        };
        this.workflow = {};
        this.config = $.Helpers.createConfig(config, this.defaultConfig);
        this.stacks = {};
    },

    startup: function() {
        this.setupMarkup();
        this.setupTopics();
        this.applyConfig();
        return this;
    },

    applyConfig: function() {
        // notificatioDuration => dynamic
        // notificationMode
        this.updateNotificationMode();
        // logLevel => dynamic
        // showLogLevels => dynamic
        return this;
    },

    setupMarkup: function() {
        var inner = $('<div />')
            .attr('id', 'notifications')
            .addClass('ui-state-default notifications');
        var wrapper = $('<div />')
            .attr('id', 'notifications-wrapper')
            .addClass('notifications-wrapper')
            .append(inner);
        $('<div />')
            .attr('id', 'notifications-outer')
            .addClass('notifications-outer')
            .append(wrapper)
            .appendTo('body');
        return this;
    },

    push: function(data, callback) {
        // default context
        data.context = data.context || this.settings.defaultContext;
        // default target
        data.appendTo = data.appendTo || this.settings.defaultTarget;
        // create the message with a specific handler
        var dialog = this.createDialog(data.type, data);
        // store it
        this.stacks[data.context] = this.stacks[data.context] || [];
        this.stacks[data.context].push(dialog);
        if (data.autoFetch || data.context == this.settings.defaultContext) {
            this.fetch(data.context);
        }
        if ($.isFunction(callback)) {
            callback();
        }
        // call the msgPushTopic
        $.Topic('msg.pushed').publish(data);
        return this;
    },

    fetch: function(context, n) {
        context = context || this.settings.defaultContext;
        if (!this.stacks[context]) {
            return this;
        }
        var trash = [];
        $.each(this.stacks[context], function(i, dialog) {
            if (!n || i < n) {
                $(dialog).dialog('open');
                // focus an input?
                var data = $(dialog).data('data');
                if(data && data.input) {
                    window.setTimeout(function() {
                        $(data.input).focus();
                    }, 0);
                }
                trash.push(i);
            }
        });
        this.stacks[context] = $.grep(this.stacks[context], function(dialog, i) {
            return $.inArray(i, trash) == -1;
        });
        return this;
    },

    count: function(context) {
        context = context || this.settings.defaultContext;
        if (!this.stacks[context]) {
            return 0;
        }
        return this.stacks[context].length;
    },

    template: function(data) {
        // create the title span
        var icon = $('<span />');
        if(data.icon) {
            icon.addClass('ui-icon ' + data.icon).css({
                float: 'left',
                margin: '0px 7px 0px 0px'
            });
        }
        var text = $('<span />').html(data.title);
        data.title = $('<span />').append(icon, text);
        // create the contents
        var content = $('<p />');
        if (typeof(data.content) == 'string') {
            data.content = $('<span />').html(data.content)[0]
        }
        content.append(data.content);
        // create the dialog
        var dialog = $('<div />')
            .append(content)
            .dialog(data).get(0);
        // reverse storage
        data.dialog = dialog;
        $(dialog).data('data', data);
        return dialog;
    },

    createDialog: function(type, data) {
        switch(type.toLowerCase()) {
            case 'error':
                return this.createError(data);
            case 'confirm':
                return this.createConfirm(data);
            case 'prompt':
                return this.createPrompt(data);
            case 'info':
            default:
                return this.createInfo(data);
        }
    },

    createInfo: function(data) {
        var defaultData = {
            title: 'Info',
            content: '',
            autoOpen: false,
            modal: true,
            draggable: false,
            resizable: false,
            icon: 'ui-icon-info',
            buttons: [{
                text: 'Close',
                icons: {primary: 'ui-icon-close'},
                click: function() {
                    $(this).dialog('close');
                    if($.isFunction(data.callback)) {
                        data.callback();
                    }
                }
            }]
        };
        data = $.extend(true, {}, defaultData, data);
        return this.template(data);
    },

    createError: function(data) {
        var defaultData = {
            title: 'Error',
            content: '',
            autoOpen: false,
            modal: true,
            draggable: false,
            resizable: false,
            icon: 'ui-icon-alert',
            buttons: [{
                text: 'Close',
                icons: {primary: 'ui-icon-close'},
                click: function() {
                    $(this).dialog('close');
                    if($.isFunction(data.callback)) {
                        data.callback();
                    }
                }
            }]
        };
        data = $.extend(true, {}, defaultData, data);
        return this.template(data);
    },

    createConfirm: function(data) {
        var defaultData = {
            title: 'Confirmation',
            content: '',
            autoOpen: false,
            modal: true,
            draggable: false,
            resizable: false,
            icon: 'ui-icon-check',
            callback: function(){},
            buttons: [{
                text: 'Cancel',
                icons: {primary: 'ui-icon-close'},
                click: function() {
                    $(this).dialog('close');
                }
            }, {
                text: 'Confirm',
                icons: {primary: 'ui-icon-check'},
                click: function() {
                    if($.isFunction(data.callback)) {
                        data.callback(true);
                    }
                    $(this).dialog('close');
                }
            }]
        };
        data = $.extend(true, {}, defaultData, data);
        return this.template(data);
    },

    createPrompt: function(data) {
        var defaultData = {
            title: 'Please Enter',
            content: '',
            text: '',
            preselection: '',
            input: null,
            autoOpen: false,
            modal: true,
            draggable: false,
            resizable: false,
            icon: 'ui-icon-pencil',
            callback: function(){},
            buttons: [{
                text: 'Cancel',
                icons: {primary: 'ui-icon-close'},
                click: function() {
                    $(this).dialog('close');
                },
            }, {
                text: 'Ok',
                icons: {primary: 'ui-icon-check'},
                click: function() {
                    if($.isFunction(data.callback)) {
                        var value;
                        if(data.input) {
                            value = $(data.input).val();
                        }
                        data.callback(value);
                    }
                    $(this).dialog('close');
                }
            }]
        };
        data = $.extend(true, {}, defaultData, data);
        if(!data.content) {
            data.content = $('<div />');
            $('<div />').html(data.text).appendTo(data.content);
            data.input = $('<input />').css({
                width: 268,
                'margin-top': 8
            }).val(data.preselection)
            .appendTo(data.content)
            .on('keypress', function(event) {
                var key = event.keyCode || event.which;
                if(key == 13) {
                    if($.isFunction(data.callback)) {
                        data.callback($(this).val());
                    }
                    $(data.dialog).dialog('close');
                }
            })[0];
        }
        return this.template(data);
    },

    info: function(data) {
        var defaultData = {
            type: 'info',
            content: 'Info',
            callback: function(){}
        };
        if(typeof(data) == 'string') {
            data = {content: data};
        }
        this.push($.extend(true, defaultData, data));
        return this;
    },

    error: function(data) {
        var defaultData = {
            type: 'error',
            content: 'Error',
            callback: function(){}
        };
        if(typeof(data) == 'string') {
            data = {content: data};
        }
        this.push($.extend(true, defaultData, data));
        return this;
    },

    confirm: function(data) {
        var defaultData = {
            type: 'confirm',
            content: 'Confirm',
            callback: function(){}
        };
        if(typeof(data) == 'string') {
            data = {content: data};
        }
        this.push($.extend(true, defaultData, data));
        return this;
    },

    prompt: function(data) {
        var defaultData = {
            type: 'prompt',
            text: 'Prompt',
            callback: function(){},
            preselection: null
        }
        if(typeof(data) == 'string') {
            data = {text: data};
        }
        this.push($.extend(true, defaultData, data));
        return this;
    },

    notify: function(data) {
        var _this = this;
        // data manipulation
        var defaultData = {
            text: '',
            duration: null,
            fx: this.settings.notificationFx,
            icon: null
        };
        if($.isPlainObject(data)) {
            data = $.extend(true, {}, defaultData, data);
        } else {
            data = $.extend({}, defaultData, {text: data});
        }
        if(!data.duration && data.duration !== 0) {
            data.duration = this.config.notificationDuration;
        }
        if(data.icon) {
            data.text = this.iconSpan(data.icon) + data.text;
        }
        // create the note
        var note = $('<div />')
        .addClass('note')
        .html(data.text)
        .hide();
        // show the notifications box?
        if(!$('#notifications').children().length) {
            $('#notifications-outer').fadeIn(0);
        }
        note.appendTo('#notifications')
        .fadeIn(data.fx.duration, data.fx.delay);
        // define the deferred hiding function
        var dfd = $.Deferred();
        dfd.done(function() {
            note.fadeOut(data.fx.duration, data.fx.easing, function() {
                if($('#notifications').children().length == 1) {
                    $('#notifications-outer').fadeOut(0);
                }
                note.remove();
            });
        });
        var timeout;
        // define the returned update function
        var update = function(newData) {
            if(dfd.state() == 'resolved') {
                return _this.notify(newData);
            }
            if(timeout) {
                window.clearTimeout(timeout);
            }
            if(!$.isPlainObject(newData)) {
                newData = {text: newData};
            } else if(!newData.text) {
                newData.text = data.text;
            }
            var duration;
            if(newData.duration) {
                duration = newData.duration;
            } else if(!newData.duration && newData.duration !== 0) {
                if(data.duration !== 0) {
                    duration = data.duration;
                } else {
                    duration = _this.config.notificationDuration;
                }
            }
            if(duration) {
                timeout = window.setTimeout(dfd.resolve, duration);
            }
            if(newData.icon) {
                newData.text = _this.iconSpan(newData.icon) + newData.text;
            }
            note.html(newData.text);
        };
        if(data.duration) {
            timeout = window.setTimeout(dfd.resolve, data.duration);
        }
        return {
            note: note,
            dfd: dfd,
            update: update
        };
    },

    log: function(level, data) {
        var levelString;
        if(typeof(level) == 'string') {
            levelString = level;
            level = logLevels[level];
            level = level || logLevels.info;
        } else {
            $.each(logLevels, function(key, value) {
                if(!levelString && level == value) {
                    levelString = key;
                }
            });
        }
        var lvl = this.config.logLevel;
        if(typeof(lvl) == 'string') {
            lvl = logLevels[lvl];
            lvl = lvl || logLevels.info;
        }
        if(level < lvl) {
            return {update: function(){}};
        }
        return this.notify(data);
    },

    updateNotificationMode: function() {
        switch(this.config.notificationMode) {
            case 'left':
                $('#notifications-outer').css({
                    left: 0,
                    right: ''
                });
                $('#notifications-wrapper').css({
                    'border-width': '1px 1px 0px 0px',
                    'border-radius': '0px 3px 0px 0px'
                });
                break;
            case 'right':
                $('#notifications-outer').css({
                    left: '',
                    right: 0
                });
                $('#notifications-wrapper').css({
                    'border-width': '1px 0px 0px 1px',
                    'border-radius': '3px 0px 0px 0px'
                });
                break;
            default:
                break;
        }
        return this;
    },

    iconSpan: function(icon) {
        var format = '<span class="ui-icon {0} note-icon"></span>';
        return $.Helpers.strFormat(format, icon);
    },

    setupTopics: function() {
        var _this = this;
        $.Topic('msg').subscribe(function() {
            return _this.push.apply(_this, arguments);
        });
        $.Topic('msg.fetch').subscribe(function() {
            return _this.fetch.apply(_this, arguments);
        });
        $.Topic('msg.info').subscribe(function() {
            return _this.info.apply(_this, arguments);
        });
        $.Topic('msg.error').subscribe(function() {
            return _this.error.apply(_this, arguments);
        });
        $.Topic('msg.confirm').subscribe(function() {
            return _this.confirm.apply(_this, arguments);
        });
        $.Topic('msg.prompt').subscribe(function() {
            return _this.prompt.apply(_this, arguments);
        });
        $.Topic('msg.notify').subscribe(function() {
            return _this.notify.apply(_this, arguments);
        });
        $.Topic('msg.log').subscribe(function() {
            return _this.log.apply(_this, arguments);
        });
        return this;
    }
});