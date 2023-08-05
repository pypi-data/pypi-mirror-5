var CommandPalette = VispaModule.extend({

    init: function(config) {
        this.defaultConfig = {
            autoSuggest: {
                descr: 'Show suggestions when the search field is empty?',
                type: 'boolean',
                value: true
            }
        };
        this._super('commandPalette', this.defaultConfig, config);

        // attributes
        this.preferenceSettings = {priority: 6};
        this.settings = {
            shortcut: 'ctrl+shift+p',
            headerOffset: 50,
            modal: true
        };
        this.workflow = {
            isOpen: false,
            enabledContexts: []
        };
        this.nodes = {
            dialog: null,
            input: null
        };
        this.commands = {};
    },

    startup: function() {
        this.setupMarkup();
        this.applyConfig();
        this.setupShortcuts();

        this.logger.debug('Started');
        return this;
    },

    applyConfig: function() {
        // autoSuggest
        $(this.nodes.input).autocomplete('option', 'minLength', this.config.autoSuggest ? 0 : 1);
        return this;
    },

    setupMarkup: function() {
        var _this = this;
        var icon = $('<span />')
            .addClass('ui-icon ui-icon-carat-1-e')
            .css({
                float: 'left',
                margin: '0px 7px 0px 0px'
            });
        var text = $('<span />').html('Command Palette');
        this.nodes.dialog = $('<div />')
            .attr('id', 'commandpalette-dialog')
            .appendTo('body')
            .dialog({
                autoOpen: false,
                resizable: false,
                draggable: false,
                modal: this.settings.modal,
                position: ['center', 'center'],
                height: 90,
                width: 300,
                title: $('<span />').append(icon, text),
                open: function() {
                    _this.workflow.isOpen = true;
                },
                close: function() {
                    _this.workflow.isOpen = false;
                }
            }).get(0);
        this.nodes.input = $('<input />')
            .css({
                width: 220,
                'margin-top': 8,
                float: 'left'
            }).autocomplete({
                delay: 0,
                source: function() {
                    _this.suggestions.apply(_this, arguments);
                },
                select: function(event, data) {
                    var callback = _this.getCallback($(this).val(data.item.value).val());
                    if(callback) {
                        _this.toggle();
                        callback();
                    }
                    event.preventDefault();
                }
            }).keydown(function(event) {
                // enter key
                if(event.keyCode == 13) {
                    var callback = _this.getCallback($(this).val());
                    if(callback) {
                        _this.toggle();
                        callback();
                    }
                }
            }).bind('keydown', this.settings.shortcut, function() {
                _this.toggle();
            }).appendTo(this.nodes.dialog)[0];
        // the button
        var btn = $('<button />').html('Go')
        .css({
            margin: '1px 0px 0px 12px',
            float: 'left'
        }).click(function() {
            var callback = _this.getCallback($(_this.nodes.input).val());
            if(callback) {
                _this.toggle();
                callback();
            }
        }).button({
            text: false,
            icons: {
                primary: 'ui-icon-arrowreturnthick-1-e'
            }
        }).appendTo(this.nodes.dialog);
        return this;
    },

    suggestions: function(request, response) {
        var _this = this;
        var hitMap = {};
        var hitList = [];
        var words = $.trim(request.term.toLowerCase()).split(' ');
        // an intuitive search algorithm
        $.each(this.commands, function(context, entries) {
            if($.inArray(context, _this.workflow.enabledContexts) == -1) {
                return;
            }
            $.each(entries, function(i, entry) {
                var hits = 0;
                $.each(words, function(j, word) {
                    if(words.length > 1 && !word) {
                        return;
                    }
                    if(entry.key.toLowerCase().indexOf(word) > -1) {
                        hits++;
                    }
                });
                if(hits) {
                    hitMap[hits] = hitMap[hits] || [];
                    hitMap[hits].push(entry.key);
                    if($.inArray(hits, hitList) == -1) {
                        hitList.push(hits);
                    }
                }
            });
        });
        var suggestions = [];
        $.each(hitList.sort(), function(i, hits) {
            suggestions = $.merge(hitMap[hits], suggestions);
        });
        response(suggestions);
        return this;
    },

    show: function() {
        var _this = this;
        if(this.workflow.isOpen) {
            return this;
        }
        var empty = true;
        $.each(this.commands, function(context, entries) {
            if (empty && $.inArray(context, _this.workflow.enabledContexts) > -1 && entries.length) {
                empty = false;
            }
        });
        if (empty) {
            return this;
        }
        Vispa.view.hideFrames();
        var position = ['center', $('#header').height() + this.settings.headerOffset];
        $(this.nodes.dialog).dialog('option', 'position', position).dialog('close').dialog('open');
        window.setTimeout(function() {
            if(_this.config.autoSuggest) {
                $(_this.nodes.input).autocomplete('search');
            }
            $(_this.nodes.input).focus();
        }, 0);
        return this;
    },

    hide: function() {
        if(!this.workflow.isOpen) {
            return this;
        }
        $(this.nodes.input).val('').blur().autocomplete('close');
        $(this.nodes.dialog).dialog('close');
        return this;
    },

    toggle: function() {
        this.workflow.isOpen ? this.hide() : this.show();
        return this;
    },

    enableContext: function(context) {
        if($.inArray(context, this.workflow.enabledContexts) == -1) {
            this.workflow.enabledContexts.push(context);
        }
        return this;
    },

    disableContext: function(context) {
        var idx = $.inArray(context, this.workflow.enabledContexts);
        if(idx > -1) {
            this.workflow.enabledContexts.splice(idx, 1);
        }
        return this;
    },

    add: function(context, entry) {
        var _this = this;
        // set default values
        this.commands[context] = this.commands[context] || [];
        entry.description = entry.description || '';
        // add the new entry
        var length = this.commands[context].length;
        var canPush = !length || entry.key > this.commands[context][length - 1].key;
        if(canPush) {
            this.commands[context].push(entry);
            return this;
        }
        if(entry.key < this.commands[context][0].key) {
            this.commands[context].unshift(entry);
            return this;
        }
        var done = false;
        $.each(this.commands[context], function(i, dummyEntry) {
            if(!done && entry.key < dummyEntry.key) {
                _this.commands[context].splice(i, 0, entry);
                done = true;
            }
        });
        return this;
    },

    remove: function(context, key) {
        var _this = this;
        if(!key) {
            this.commands[context] = [];
        } else {
            var done = false;
            $.each(this.commands[context], function(i, entry) {
                if(!done && key && entry.key == key) {
                    _this.commands[context].splice(i, 1);
                    done = true;
                }
            });
        }
        return this;
    },

    getCallback: function(key) {
        var _this = this;
        var callback;
        $.each(this.commands, function(context, entries) {
            if($.inArray(context, _this.workflow.enabledContexts) == -1) {
                return;
            }
            $.each(entries, function(i, entry) {
                if(key && entry.key.toLowerCase() == key.toLowerCase()) {
                    callback = entry.callback;
                }
            });
        });
        return callback;
    },

    setupShortcuts: function() {
        var _this = this;
        // register the shortcut for 'toggle' to 'global'
        $.Shortcuts('global').add(this.settings.shortcut, function() {
            _this.toggle();
        });
        return this;
    }
});