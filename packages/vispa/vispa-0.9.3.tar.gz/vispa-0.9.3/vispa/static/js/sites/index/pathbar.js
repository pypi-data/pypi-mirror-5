var PathBar = VispaModule.extend({

    init: function(config) {
        this.defaultConfig = {
            nSuggestions: {
                descr: 'The number of received suggestions',
                type: 'integer',
                select: [1, 5, 10, 20, 30, 40, 50],
                value: 10
            },
            appendHiddenFiles: {
                descr: 'Move hidden files to the end?',
                type: 'boolean',
                value: true
            }
        };
        this._super('pathBar', this.defaultConfig, config);

        // attributes
        this.preferenceSettings = {
            priority: 8,
            entryOrder: ['nSuggestions']
        };
        this.settings = {
            shortcut: 'ctrl+shift+g',
            checkDelay: 1000,
            feedbackDelay: 200,
            defaultValue: '~/'
        };
        this.workflow = {
            mode: 'display',
            checkTimeout: null,
            isGettingSuggestion: false,
            autocompleteVisible: false,
            fileExtensions: []
        };
        this.nodes = {
            bar: null,
            display: null,
            input: null,
            inputNode: null,
            inputLoader: null
        };
    },

    startup: function() {
        this.setupMarkup();
        this.setupTopics();
        this.setValue();
        this.logger.debug('Started');

        return this;
    },

    applyConfig: function() {
        // nSuggestions => dynamic
        return this;
    },

    updateFileExtensions: function() {
        this.workflow.fileExtensions = $.Helpers.objectKeys(Vispa.extensionManager.fileHandlers);
        return false;
    },

    setupMarkup: function() {
        var _this = this;
        // the display
        var menuBox = $('<div />')
            .addClass('extension-menu-box')
            .appendTo(this.nodes.menuContainer);

        // the button
        var textSpan = $('<span />').html('Go to');
        var icon = $('<span />')
            .addClass('ui-icon ui-icon-triangle-1-e')
            .css({
            float: 'right',
            'margin-right': 0,
        });
        var goBtnInner = $('<div />')
            .addClass('pathbar-display-button-inner')
            .append(textSpan, icon);
        var goBtn = $('<div />')
            .addClass('pathbar-display-button ui-state-default ui-corner-all')
            .attr('title', 'Go to')
            .hover(function() {
            $(this).toggleClass('ui-state-hover', true);
        }, function() {
            $(this).toggleClass('ui-state-hover', false);
        }).append(goBtnInner);
        var displayText = $('<span />')
            .addClass('pathbar-display-text');
        var displayInner = $('<span />')
            .addClass('pathbar-display-inner')
            .append(goBtn, displayText);
        var displayWrapper = $('<div />')
            .addClass('pathbar-display-wrapper')
            .append(displayInner);
        this.nodes.display = $('<div />')
            .addClass('pathbar-display')
            .append(displayWrapper)
            .get(0);

        // the input
        this.nodes.inputLoader = $('<span />')
            .addClass('pathbar-input-loader-inner');
        var loader = $('<div />')
            .addClass('pathbar-input-loader')
            .append(this.nodes.inputLoader);
        this.nodes.inputNode = $('<input />')
            .attr('type', 'text')
            .addClass('pathbar-input-input')
            .get(0);
        var inputOuter = $('<div />')
            .addClass('pathbar-input-outer')
            .append(this.nodes.inputNode);
        this.nodes.input = $('<div />')
            .addClass('pathbar-input')
            .append(loader, inputOuter)
            .get(0);

        // the main bar
        this.nodes.bar = $('<div />')
            .addClass('pathbar-content')
            .append(this.nodes.display, this.nodes.input)
            .appendTo('#content-header-left')
            .get(0);

        // events
        var bindHide = function() {
            $(document).one('click', function(event) {
                var hide = !$(_this.nodes.bar).find(event.target).length;
                hide ? _this.showDisplay() : bindHide();
            });
        };
        $(this.nodes.display).click(function(event) {
            _this.showInput();
            event.stopPropagation();
            bindHide();
        });
        // up: 38, down: 40, left: 37, right: 39, tab: 9, enter: 13
        $(this.nodes.inputNode)
            .keydown(function(event) {
            if (event.keyCode == 13) {
                // enter key action
                if (_this.workflow.autocompleteVisible) {
                    _this.workflow.autocompleteVisible = false;
                } else {
                    _this.commit(this.value);
                }
            } else if (event.keyCode == 9) {
                // tab key action
                event.preventDefault();
                _this.suggest(this.value);
            } else if (event.keyCode != 38 && event.keyCode != 40) {
                // clear the check timeout
                window.clearTimeout(_this.workflow.checkTimeout);
                _this.destroyAutoComplete();
            }
        }).keyup(function(event) {
            if (_this.workflow.autocompleteVisible || $.inArray(event.keyCode, [37, 38, 39, 40, 9, 13]) < 0) {
                _this.check(this.value);
            }
        });

        return this;
    },

    destroyAutoComplete: function() {
        try {
            $(this.nodes.inputNode).autocomplete('destroy');
        } catch (err) {}
        this.workflow.autocompleteVisible = false;
        return this;
    },

    setLoader: function(value, flag) {
        // value:
        //      undefined   -> empty
        //      null        -> loader gif
        //      false       -> cross
        //      string      -> file banner
        var content;
        if (value === undefined) {
            content = '';
        } else if (value === null) {
            content = $('<img />')
                .attr('src', Vispa.urlHandler.static('img/maingui/loader3.gif'))
                .css('margin-top', 5);
        } else if (value === false) {
            content = this.makeFileBanner('?');
        } else if (typeof(value) == 'string') {
            content = this.makeFileBanner(value, flag);
        } else {
            return this;
        }
        // set the content
        $(this.nodes.inputLoader)
            .empty()
            .append(content);
        return this;
    },

    makeFileBanner: function(fileExtension, flag) {
        var banner = $('<span />')
            .addClass('pathbar-input-loader-filelabel')
            .html(fileExtension);
        if (flag === true) {
            banner.addClass('pathbar-input-loader-filelabel-true');
        } else if (flag === false) {
            banner.addClass('pathbar-input-loader-filelabel-false');
        }
        return banner.get(0);
    },

    show: function() {
        $(this.nodes.bar).show();
        return this;
    },

    hide: function() {
        $(this.nodes.bar).hide();
        return this;
    },

    showInput: function() {
        if (this.workflow.mode == 'input') {
            return this;
        }
        this.workflow.mode = 'input';
        $(this.nodes.display).hide();
        $(this.nodes.input)
            .show()
            .find('.pathbar-input-input');
        // sync values
        var value = $(this.nodes.display)
            .find('.pathbar-display-text')
            .html();
        $(this.nodes.input)
            .find('.pathbar-input-input')
            //.val('')
            .focus()
            //.val(value);
        // check once, immediate
        this.check(value, true);
        return this;
    },

    showDisplay: function() {
        if (this.workflow.mode == 'display') {
            return this;
        }
        this.workflow.mode = 'display';
        $(this.nodes.input).hide();
        $(this.nodes.display).show();
        this.nodes.inputNode.blur();
        this.setLoader();
        return this;
    },

    setValue: function(value) {
        value = value || Vispa.workspaceManager.getWorkspace().basedir || this.settings.defaultValue;
        // set the display value
        $(this.nodes.display)
            .find('.pathbar-display-text')
            .html(value)
            .attr('title', value);
        // set the input value
        $(this.nodes.input)
            .find('.pathbar-input-input')
            .val(value);
        return this;
    },

    check: function(path, immediate) {
        var _this = this;

        // timeout set?
        if (this.workflow.checkTimeout) {
            // clear it
            window.clearTimeout(this.workflow.checkTimeout);
        }

        // set a new timeout
        this.workflow.checkTimeout = window.setTimeout(function() {
            _this.setLoader(null);
            // check if the path exists
            var promise = Vispa.pathExists(path);
            // there has to be a minimum delay to see that
            // something changed/was loaded
            var dfd = $.Deferred();
            window.setTimeout(dfd.resolve, _this.settings.feedbackDelay);
            $.when(promise, dfd.promise()).then(function(response) {
                response = response[0];
                var hit = false;
                if (response.success) {
                    if (response.type == 'f') {
                        // get the file extension
                        var ext = $.Helpers.strExtension(path);
                        if (ext) {
                            hit = true;
                            ext = ext.toLowerCase();
                            // extension accepted?
                            var idx = $.inArray(ext, _this.workflow.fileExtensions);
                            _this.setLoader(ext, idx >= 0);
                        }
                    } else if (response.type == 'd') {
                        hit = true;
                        // is there a handler for '/'?
                        var idx = $.inArray('/', _this.workflow.fileExtensions);
                        _this.setLoader('dir', idx >= 0);
                    }
                }
                if (!hit) {
                    _this.setLoader(false);
                }
            });
        }, immediate ? 0 : this.settings.checkDelay);
        return this;
    },

    suggest: function(path) {
        var _this = this;
        if (this.workflow.isGettingSuggestion) {
            return this;
        }
        this.workflow.isGettingSuggestion = true;
        var promise = $.ajax({
            url: Vispa.urlHandler.dynamic('ajax/fs/getsuggestions'),
            type: 'POST',
            data: {
                _wid: Vispa.workspaceManager.getWorkspace().id,
                path: path,
                length: this.config.nSuggestions,
                'append_hidden': this.config.appendHiddenFiles
            }
        });
        $.when(promise).then(function(response) {
            if (promise.success) {
                if (!response.suggestions) {
                    // nothing should happen
                } else if (response.suggestions.length == 1) {
                    $(_this.nodes.inputNode).val(response.suggestions[0]);
                    _this.check(response.suggestions[0], true);
                } else if (response.suggestions.length > 1) {
                    $(_this.nodes.inputNode)
                        .autocomplete({
                            delay: 0,
                            minLength: 0,
                            source: response.suggestions,
                            select: function(event) {
                                _this.check(_this.nodes.inputNode.value);
                                event.stopPropagation();
                            },
                            open: function() {
                                var me = this;
                                _this.workflow.autocompleteVisible = true;
                                // vary the width
                                // jQuery UI calls 'open' even when the widget
                                // is not started yet, so use try-catch to avoid these cases
                                try {
                                    var maxWidth = 0;
                                    var offset = 20;
                                    var menu = $(this).autocomplete('widget');
                                    menu.children().each(function(i, item) {
                                        var a = $(item).children().first();
                                        maxWidth = Math.max(maxWidth, $.Helpers.textWidth(a.html()));
                                    });
                                    menu.width(maxWidth + offset);
                                } catch (e) {}
                            },
                            close: function() {
                                _this.workflow.autocompleteVisible = false;
                            },
                            _renderItem: function(ul, item) {
                                var regexp = new RegExp('^' + this.term);
                                var label = item.label.replace(regexp, $.Helpers.strFormat('<b>{0}</b>', this.term));
                                return $('<li>')
                                    .append($('<a>').html(label))
                                    .appendTo(ul);
                            }
                        });
                    $(_this.nodes.inputNode).autocomplete('search');
                } else {
                    _this.check(path);
                }
            }
            _this.workflow.isGettingSuggestion = false;
        });
        return this;
    },

    commit: function(path) {
        var _this = this;
        // does it exist? it may be a file or a folder
        var promise = Vispa.pathExists(path);
        $.when(promise).then(function(response) {
            if (response.success) {
                // file or folder
                var ext;
                if (response.type == 'f') {
                    ext = $.Helpers.strExtension(path);
                    if (!ext) {
                        return;
                    }
                } else if (response.type == 'd') {
                    ext = '/';
                }
                // is there a handler?
                var handlers = Vispa.extensionManager.getFileHandlers(ext, true);
                if (handlers.length == 1) {
                    _this.showDisplay();
                    handlers[0].callback(path);
                } else if (handlers.length > 1) {
                    var names = [];
                    var map = {};
                    $.each(handlers, function(i, handler) {
                        var name = 'unknown';
                        if (handler.owner instanceof ExtensionBase) {
                            name = $.Helpers.strFormat('<b>{0}</b> <i>(Extension)</i>', handler.owner.name);
                        } else if (handler.owner instanceof ExtensionFactoryBase) {
                            name = $.Helpers.strFormat('<b>{0}</b> <i>(Factory)</i>', handler.owner.name);
                        }
                        names.push(name);
                        map[name] = handler;
                    });
                    _this.destroyAutoComplete();
                    $(_this.nodes.inputNode)
                        .autocomplete({
                            delay: 0,
                            minLength: 0,
                            source: function(request, response) {
                                // set names as source array
                                response(names);
                            },
                            select: function(event, ui) {
                                var name = ui.item.value;
                                event.preventDefault();
                                if (map[name]) {
                                    _this.showDisplay();
                                    map[name].callback(path);
                                }
                            },
                            focus: function(event) {
                                // don't change the value of the input
                                event.preventDefault();
                            },
                            open: function() {
                                _this.workflow.autocompleteVisible = true;
                            },
                            close: function() {
                                _this.workflow.autocompleteVisible = false;
                            }
                        });
                    $(_this.nodes.inputNode).autocomplete('search');
                }
            }
        });
        return this;
    },

    setupTopics: function() {
        var _this = this;
        $.Topic('extenstion.added').subscribe(function() {
            _this.updateFileExtensions();
        });
        return this;
    }
});