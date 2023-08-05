var PreferenceView = VispaModule.extend({

    init: function(config) {
        this.defaultConfig = {
            toggleSections: {
                descr: 'Hide unused sections?',
                type: 'boolean',
                value: true
            }
        };
        this._super('preferenceView', this.defaultConfig, config);

        // attributes
        this.preferenceSettings = {priority: 4};
        this.settings = {
            shortcut: 'ctrl+p',
            dialogHeight: 360,
            dialogWidth: 650,
            sidebarWidth: 199,// value from the css class
            contentWidth: 429,// value from the css class
            keySeparator: '.',
            startKey: 'vispa.view',
            sectionToggleFx: {duration: 100, easing: 'easeOutExpo'}
        };
        this.workflow = {
            isOpen: false,
            loaderIsVisible: false,
            currentKey: null,
            openSections: []
        };
        this.nodes = {
            dialog: null,
            loader: null,
            entriesBoxes: {},
            entryLinks: {},
            headers: {},
            content: {}
        };
    },

    startup: function() {
        this.setupMarkup();
        this.setupShortcuts();

        this.logger.debug('Started');
        return this;
    },

    applyConfig: function() {
        // toggleSections -> dynamic
        return this;
    },

    setupMarkup: function() {
        var _this = this;
        // the title
        var title = $('<span />');
        var icon = $('<span />')
            .addClass('ui-icon ui-icon-gear')
            .css({
                float: 'left',
                margin: '0px 7px 0px 0px'
            }).appendTo(title);
        var text = $('<span />')
            .html('Preferences')
            .appendTo(title);
        // the dialog
        this.nodes.dialog = $('<div />')
            .css('overflow', 'hidden')
            .appendTo('body')
            .dialog({
                title: title,
                height: this.settings.dialogHeight + 112,// 112 -> header and footer
                width: this.settings.dialogWidth,
                autoOpen: false,
                draggable: false,
                resizable: false,
                modal: true,
                closeOnEscape: true,
                buttons: [{
                    text: 'Close',
                    click: function() {
                        $(this).dialog('close');
                    }
                }],
                open: function() {
                    // set the dialogs content
                    _this.updateContent();
                    _this.workflow.isOpen = true;
                },
                close: function() {
                    _this.workflow.isOpen = false;
                }
            }).get(0);
        return this;
    },

    show: function(key) {
        if (this.workflow.isOpen) {
            return this;
        }
        Vispa.view.hideFrames();
        // set the new key
        if (key) {
            this.workflow.currentKey = key;
        }
        // and show it
        $(this.nodes.dialog).dialog('open');
        return this;
    },

    hide: function() {
        if (!this.workflow.isOpen) {
            return this;
        }
        $(this.nodes.dialog).dialog('close');
        return this;
    },

    toggle: function(key) {
        this.workflow.isOpen ? this.hide() : this.show(key);
        return this;
    },

    setupLoader: function() {
        // setup only once
        if(this.nodes.loader) {
            return this;
        }
        this.nodes.loader = $('<div />')
            .addClass('preference-loader ui-widget-overlay')
            .appendTo($(this.nodes.dialog).parent());
        $('<img />')
            .attr('src', Vispa.urlHandler.dynamic('static/img/maingui/loader2.gif'))
            .addClass('preference-loader-inner')
            .appendTo(this.nodes.loader);
        return this;
    },

    showLoader: function() {
        if (this.workflow.loaderIsVisible) {
            return this;
        }
        $(this.nodes.loader).show();
        this.workflow.loaderIsVisible = true;
        return this;
    },

    hideLoader: function() {
        if (!this.workflow.loaderIsVisible) {
            return this;
        }
        $(this.nodes.loader).hide();
        this.workflow.loaderIsVisible = false;
        return this;
    },

    removeContent: function() {
        $(this.nodes.dialog).empty();
        this.nodes.entriesBoxes = {};
        this.nodes.headers = {};
        this.nodes.content = {};
        this.workflow.openSections = [];
        return this;
    },

    updateContent: function() {
        var _this = this;
        this.removeContent();

        var outer = $('<div />').addClass('preference-outer');
        var inner = $('<div />')
            .addClass('preference-inner')
            .appendTo(outer);
        var leftBox = $('<div />')
            .addClass('preference-left')
            .appendTo(inner);
        var rightBox = $('<div />')
            .addClass('preference-right')
            .appendTo(inner);

        var startKey = this.workflow.currentKey || this.settings.startKey;

        $.each(Vispa.preferenceHandler.workflow.sectionOrder, function(i, section) {
            var observables = Vispa.preferenceHandler.observables[section];
            if (!observables) {
                return;
            }
            // create a box for each section
            var sectionBox = _this.createSectionBox(section, leftBox);
            // create the section header
            var sectionHeader = _this.createSectionHeader(section, sectionBox);
            $(sectionHeader).click(function() {
                _this.toggleSection(section);
            });
            _this.nodes.headers[section] = sectionHeader;
            // create a box that contains each entry link
            var entriesBox = _this.createEntriesBox(sectionBox);
            _this.nodes.entriesBoxes[section] = entriesBox;
            if (!_this.config.toggleSections) {
                _this.openSection(section, {duration: 0});
            }

            var entryOrder = Vispa.preferenceHandler.workflow.entryOrders[section];
            $.each(entryOrder, function(j, name) {
                var obj = observables[name];
                // hidden observable or config unset?
                if (obj.settings.hidden || !obj.config || !$.Helpers.objectKeys(obj.config).length) {
                    return;
                }
                // any visible entries?
                var empty = true;
                $.each(obj.defaultConfig, function(key, map) {
                    if (!map.hidden) {
                        empty = false;
                        return false;
                    }
                });
                if (empty) {
                    return;
                }

                // create a link for each entry
                var title = obj.settings.title;
                if (obj.settings.capitalizeTitle) {
                    title = $.Helpers.strCapitalize(title);
                }
                var titleActions = obj.settings.titleActions;
                var entryLink = _this.createEntryLink(section, title, titleActions, entriesBox, j != entryOrder.length-1);
                // create the content for each entry
                var entryContent = _this.createEntryContent(section, name, obj, rightBox);
                // create a unique key for storage reasons
                var key = _this.createKey(section, name);
                _this.nodes.content[key] = entryContent;
                _this.nodes.entryLinks[key] = entryLink;
                // click event for the entryLink
                $(entryLink)
                    .click(function() {
                        _this.switchEntry(key);
                    });
            });
            // remove the last child of entriesBox if it is a separator
            var lastChild = $(entriesBox).children().last();
            if (lastChild && lastChild.hasClass('preference-separator')) {
                lastChild.remove();
            }
        });

        if (Vispa.useSlimScroll()) {
            leftBox
                .slimScroll({
                    height: '100%',
                    width: this.settings.sidebarWidth,
                    wrapperClass: 'preference-left'
                }).parent()
                .css('position', 'absolute');
        }

        $(this.nodes.dialog).append(outer);
        this.setupLoader();

        // select the startKey
        this.switchEntry(startKey);

        return this;
    },

    createSectionBox: function(section, target) {
        var box = $('<div />')
            .addClass('preference-section-box')
            .appendTo(target);
        return box.get(0);
    },

    createSectionHeader: function(section, target) {
        // the header
        var icon = $('<span />')
            .addClass('ui-icon ui-icon-triangle-1-e')
            .css({
                float: 'left',
                margin: '2px 3px 0px 0px'
            });
        var header = $('<div />')
            .append(icon, $.Helpers.strCapitalize(section))
            .addClass('preference-header')
            .appendTo(target);
        return header.get(0);
    },

    createEntriesBox: function(target) {
        var box = $('<div />')
            .addClass('preference-entries-box')
            .appendTo(target);
        return box.get(0);
    },

    createEntryLink: function(section, title, titleActions, target, separator) {
        var titleActionsOuter = $('<div />')
            .addClass('preference-element-actions')
            .append(titleActions);
        var linkTitle = $('<div />')
            .addClass('preference-element-title')
            .append(title);
        var clear = $('<div />').css('clear', 'both');
        var link = $('<div />')
            .append(linkTitle, titleActionsOuter, clear)
            .addClass('preference-element');
        var entry = $('<a />', {href: 'javascript:void(0)'})
            .append(link)
            .css('cursor', 'pointer')
            .appendTo(target);
        if (separator || separator === undefined) {
            this.createSeparator(target);
        }
        return entry.get(0);
    },

    createSeparator: function(target) {
        var separator = $('<div />')
            .addClass('preference-separator')
            .appendTo(target);
        return separator.get(0);
    },

    createKey: function(section, name) {
        return $.Helpers.strFormat('{0}{1}{2}', section, this.settings.keySeparator, name);
    },

    reverseKey: function(key) {
        if (!key) {
            return null;
        }
        var parts = key.split(this.settings.keySeparator);
        return {
            section: parts[0],
            name: parts[1]
        };
    },

    openSection: function(section, fx) {
        var _this = this;
        fx = $.extend(true, {}, this.settings.sectionToggleFx, fx);
        var idx = $.inArray(section, this.workflow.openSections);
        if (idx >= 0) {
            // the section is already open
            return this;
        }
        // the section is hidden, open it and if toggleSections is true,
        // hide all other open sections
        if (this.config.toggleSections) {
            $.each(this.workflow.openSections, function(i, _section) {
                _this.closeSection(_section, fx);
            });
        }
        $(this.nodes.entriesBoxes[section]).slideDown(fx.duration, fx.easing);
        // change the header icon
        $(this.nodes.headers[section])
            .children()
            .first()
            .toggleClass('ui-icon-triangle-1-e', false)
            .toggleClass('ui-icon-triangle-1-s', true);
        this.workflow.openSections.push(section);
        return this;
    },

    closeSection: function(section, fx) {
        fx = $.extend(true, {}, this.settings.sectionToggleFx, fx);
        var idx = $.inArray(section, this.workflow.openSections);
        if (idx < 0) {
            // the section is already closed
            return this;
        }
        // the section is open, close it
        $(this.nodes.entriesBoxes[section]).slideUp(fx.duration, fx.easing);
        // change the header icon
        $(this.nodes.headers[section])
            .children()
            .first()
            .toggleClass('ui-icon-triangle-1-s', false)
            .toggleClass('ui-icon-triangle-1-e', true);
        this.workflow.openSections.splice(idx, 1);
        return this;
    },

    toggleSection: function(section, fx) {
        var idx = $.inArray(section, this.workflow.openSections);
        idx < 0 ? this.openSection(section, fx) : this.closeSection(section, fx);
        return this;
    },

    switchEntry: function(key) {
        if (this.workflow.currentKey) {
            // hide the current content
            $(this.nodes.content[this.workflow.currentKey]).hide();
            // unhighlight the entryLink
            $(this.nodes.entryLinks[this.workflow.currentKey])
                .children().first()
                .children().first()
                .toggleClass('preference-element-selected', false);
        }
        if (!key) {
            return this;
        }
        // toggle sections?
        this.openSection(this.reverseKey(key).section);
        // show the new content
        $(this.nodes.content[key]).show();
        // entryLink highlight
        $(this.nodes.entryLinks[key])
            .children().first()
            .children().first()
            .toggleClass('preference-element-selected', true);
        this.workflow.currentKey = key;

        return this;
    },

    setupShortcuts: function() {
        var _this = this;
        // register the shortcut for 'toggle' to 'global'
        $.Shortcuts('global').add(this.settings.shortcut, function() {
            _this.toggle();
        });
    },

    createEntryContent: function(section, name, obj, target) {
        var _this = this;
        var box = $('<div />')
            .addClass('preference-content')
            .appendTo(target);
        var head = $('<div />')
            .addClass('preference-content-header')
            .appendTo(box);
        var innerContent = $('<div />')
            .addClass('preference-content-inner')
            .appendTo(box);
        var footer = $('<div />')
            .addClass('preference-content-footer')
            .appendTo(box);
        $('<span />')
            .addClass('ui-icon ' + obj.settings.icon)
            .css({
                float: 'left',
                margin: '2px 5px 0px 0px'
            }).appendTo(head);
        head.append(obj.settings.title);
        // description?
        if (obj.settings.description) {
            var descriptionContainer = $('<div />').addClass('preference-content-description ui-state-highlight ui-corner-all');
            var icon = $('<span />').addClass('ui-icon ui-icon-info');
            $('<div />')
                .css('float', 'left')
                .append(icon)
                .appendTo(descriptionContainer);
            $('<div >')
                .addClass('preference-content-description-text')
                .append(obj.settings.description)
                .appendTo(descriptionContainer);
            $('<div />')
                .css('clear', 'both')
                .appendTo(descriptionContainer);
            descriptionContainer.appendTo(innerContent);
        }
        // the data container
        var dataContainer = $('<div />')
            .addClass('preferece-content-data')
            .appendTo(innerContent);
        // config present?
        if (!obj.config || !$.Helpers.objectKeys(obj.config).length) {
            dataContainer.html('<i>empty</i>');
            return box.get(0);
        }
        // define the looping function that is called for each data entry
        var entries = [];
        var loop = function(key) {
            if (!key || !obj.defaultConfig[key]) {
                return;
            }
            var filter = obj.settings.entryFilter;
            var hidden = obj.defaultConfig[key].hidden
                || ($.isArray(filter) && $.inArray(key, filter) >= 0);
            if (hidden) {
                return;
            }
            var entry = _this.createDataEntry(section, name, obj, key, dataContainer);
            if (entry) {
                entries.push(entry);
            }
        };
        // is the an entryOrder for this object?
        var order = obj.settings.entryOrder
        if ($.isArray(order) && order.length) {
            // are there missing entries in the order?
            var missing = $.grep($.Helpers.objectKeys(obj.config), function(key) {
                return $.inArray(key, order) < 0;
            });
            $.each(order.concat(missing), function(i, key) {
                loop(key);
            });
        } else {
            $.each(obj.config, loop);
        }

        // the save button
        $('<button />')
            .html('Save')
            .addClass('preference-content-footer-button-right')
            .button({
                icons: {
                    primary: 'ui-icon-disk'
                }
            }).appendTo(footer)
            .click(function() {
                // change icon
                $(this).button('option', 'icons', {primary: 'ui-icon-refresh'}).button('disable');
                var dfd = _this.save(section, name, obj, entries);
                var btn = this;
                $.when(dfd).always(function() {
                    // the button may not exists at this time anymore
                    try {
                        $(btn).button('option', 'icons', {primary: 'ui-icon-disk'}).button('enable');
                    } catch(e) {}
                });
            });
        // the reset default button
        $('<button />')
            .html('Reset to defaults')
            .addClass('preference-content-footer-button-right')
            .button({
                icons: {
                    primary: 'ui-icon-arrowreturnthick-1-w'
                }
            }).appendTo(footer)
            .click(function() {
                $.each(entries, function(i, entry) {
                    $(entry).data('manipulator').setDefault();
                });
            });
        // own buttons
        $.each(obj.settings.buttons, function(i, btn) {
            btn.click = btn.click || function() {};
            $('<button />')
                .button(btn)
                .click(btn.click)
                .addClass('preference-content-footer-button-left')
                .appendTo(footer);
        });

        // slimscroll?
        if (Vispa.useSlimScroll()) {
            innerContent
                .slimScroll({
                    height: '100%',
                    width: this.settings.contentWidth,
                    wrapperClass: 'preference-content-inner'
                }).parent()
                .css('position', 'absolute');
        }
        return box.get(0);
    },

    createDataEntry: function(section, name, obj, key, target) {
        if (!obj.defaultConfig[key]) {
            return null;
        }
        var entry = $('<div />')
            .addClass('preference-content-data-entry')
            .appendTo(target);
        var typeSpan = $('<span />')
            .addClass('preference-content-data-type')
            .html($.Helpers.strFormat('  ({0})', $.Helpers.strCapitalize(obj.defaultConfig[key].type)));
        var keySpan = $('<span />')
            .addClass('preference-content-data-key')
            .html(key);
        var defaultSpan = $('<span />')
            .addClass('preference-content-data-default')
            .html('set default');
        var title = $('<div />')
            .addClass('preference-content-data-title')
            .append("&bull;", keySpan, typeSpan, defaultSpan)
            .appendTo(entry);
        // description and/or range?
        var hasRange = $.isArray(obj.defaultConfig[key].range) && obj.defaultConfig[key].range.length == 2;
        var showDescr = obj.defaultConfig[key].descr || hasRange;
        if (showDescr) {
            var descr;
            if (obj.defaultConfig[key].descr) {
                descr = obj.defaultConfig[key].descr;
            }
            if (hasRange) {
                var rangeText = '<b>Range</b>: {0} to {1}.';
                rangeText = $.Helpers.strFormat(rangeText, obj.defaultConfig[key].range[0], obj.defaultConfig[key].range[1]);
                if (descr) {
                    var connector = '. ';
                    if ($.Helpers.strEnds(obj.defaultConfig[key].descr, '.') || $.Helpers.strEnds(obj.defaultConfig[key].descr, '!') || $.Helpers.strEnds(obj.defaultConfig[key].descr, '?')) {
                        connector = ' ';
                    }
                    descr += connector + rangeText;
                } else {
                    descr = rangeText;
                }
            }
            var descriptionContainer = $('<div />').addClass('preference-content-data-description');
            var icon = $('<span />').addClass('ui-icon ui-icon-comment');
            $('<div />')
                .css('float', 'left')
                .append(icon)
                .appendTo(descriptionContainer);
            $('<div >')
                .addClass('preference-content-data-description-text')
                .append(descr)
                .appendTo(descriptionContainer);
            $('<div />')
                .css('clear', 'both')
                .appendTo(descriptionContainer);
            descriptionContainer.appendTo(entry);
        }
        var manipulator = this.createDataManipulator(section, name, obj, key);
        var content = $('<div >')
            .addClass('preference-content-data-manipulator')
            .append(manipulator)
            .appendTo(entry);
        defaultSpan.click(function() {
            manipulator.setDefault();
        });
        // store the manipulator directly in the entry
        entry.data('manipulator', manipulator);
        entry.data('key', key);
        return entry.get(0);
    },

    createDataManipulator: function(section, name, obj, key) {
        switch(obj.defaultConfig[key].type.toLowerCase()) {
            case 'string':
            case 'str':
                return this.createStringManipulator(section, name, obj, key);
            case 'integer':
            case 'int':
                return this.createIntegerManipulator(section, name, obj, key);
            case 'float':
                return this.createNumberFieldManipulator(section, name, obj, key);
            case 'boolean':
            case 'bool':
                return this.createBooleanManipulator(section, name, obj, key);
            case 'list':
                return this.createListManipulator(section, name, obj, key);
            case 'object':
            case 'obj':
                return this.createObjectManipulator(section, name, obj, key);
            default:
                return obj.config[key];
        }
    },

    createSelectionManipulator: function(section, name, obj, key) {
        var manipulator = $('<div />');
        var select = $('<select />')
            .addClass('preference-content-data-select')
            .appendTo(manipulator);
        var hit = false;
        $.each(obj.defaultConfig[key].select, function(i, value) {
            var option = $('<option />')
                .html(value)
                .appendTo(select);
            if (value == obj.config[key]) {
                option.attr('selected', 'selected');
                hit = true;
            }
        });
        if (!hit) {
            var tmpl = 'SelectionManipulator \'{0}.{1}.{2}\' tried to select a value (\'{3}\') which isn\'t selectable';
            this.logger.warn($.Helpers.strFormat(tmpl, section, name, key, obj.config[key]));
        }
        // attach manipulator methods
        manipulator.get(0).getValue = function() {
            return manipulator.find(":selected").text();
        };
        manipulator.get(0).setValue = function(value) {
            $.each(select.children(), function(i, child) {
                if ($(child).html() == value) {
                    $(child).attr('selected', 'selected');
                }
            });
        };
        manipulator.get(0).setDefault = function() {
            var defaultValue = obj.defaultConfig[key].value;
            this.setValue(defaultValue);
        }
        return manipulator.get(0);
    },

    createStringManipulator: function(section, name, obj, key) {
        if (obj.defaultConfig[key].select && $.isArray(obj.defaultConfig[key].select) && obj.defaultConfig[key].select.length) {
            // selection box!
            return this.createSelectionManipulator(section, name, obj, key);
        } else {
            // normal text field
            return this.createStringFieldManipulator(section, name, obj, key);
        }
    },

    createStringFieldManipulator: function(section, name, obj, key) {
        var manipulator = $('<div />');
        var field = $('<input />')
            .attr('type', 'text')
            .addClass('preference-content-data-text')
            .appendTo(manipulator)
            .val(obj.config[key])
            .keypress(function(event) {
                if (event.keyCode == 13) {
                    field.blur();
                }
            });
        // attach manipulator methods
        manipulator.get(0).getValue = function() {
            return field.val();
        };
        manipulator.get(0).setValue = function(value) {
            field.val(value);
        };
        manipulator.get(0).setDefault = function() {
            var defaultValue = obj.defaultConfig[key].value;
            this.setValue(defaultValue);
        }
        return manipulator.get(0);
    },

    createIntegerManipulator: function(section, name, obj, key) {
        // 'select' is prioritised over 'range'
        if (obj.defaultConfig[key].select && $.isArray(obj.defaultConfig[key].select) && obj.defaultConfig[key].select.length) {
            // selection box!
            return this.createSelectionManipulator(section, name, obj, key);
        } else {
            // normal text field
            return this.createNumberFieldManipulator(section, name, obj, key);
        }
    },

    createNumberFieldManipulator: function(section, name, obj, key) {
        var manipulator = $('<div />');
        var field = $('<input />')
            .attr('type', 'text')
            .addClass('preference-content-data-text')
            .appendTo(manipulator)
            .val(obj.config[key])
            .keypress(function(event) {
                if (event.keyCode == 13) {
                    field.blur();
                }
            });
        // attach manipulator methods
        manipulator.get(0).getValue = function() {
            return field.val();
        };
        manipulator.get(0).setValue = function(value) {
            field.val(value);
        };
        manipulator.get(0).setDefault = function() {
            var defaultValue = obj.defaultConfig[key].value;
            this.setValue(defaultValue);
        }
        return manipulator.get(0);
    },

    createBooleanManipulator: function(section, name, obj, key) {
        var radioName = $.Helpers.strFormat('{0}-{1}-{2}', section, name, key);
        var yesId = $.Helpers.strFormat('{0}-{1}', radioName, 'yes');
        var noId = $.Helpers.strFormat('{0}-{1}', radioName, 'no');
        // markup
        var manipulator = $('<div />');
        var set = $('<div />');
        var yes = $('<input />')
            .attr({
                id: yesId,
                type: 'radio',
                name: radioName,
                checked: 'checked'
            }).appendTo(set);
        $('<label />')
            .attr('for', yesId)
            .html('True')
            .appendTo(set);
        var no = $('<input />')
            .attr({
                id: noId,
                type: 'radio',
                name: radioName,
                checked: 'checked'
            }).appendTo(set);
        $('<label />')
            .attr('for', noId)
            .html('False')
            .appendTo(set);
        // set value
        if (obj.config[key]) {
            no.removeAttr('checked');
        } else {
            yes.removeAttr('checked');
        }
        $(set).buttonset().appendTo(manipulator);
        // attach manipulator methods
        manipulator.get(0).getValue = function() {
            return yes.get(0).checked;
        };
        manipulator.get(0).setValue = function(value) {
            var target = value ? yes : no;
            target.trigger('click');
        };
        manipulator.get(0).setDefault = function() {
            var defaultValue = obj.defaultConfig[key].value;
            this.setValue(defaultValue);
        }
        return manipulator.get(0);
    },

    createListManipulator: function(section, name, obj, key) {
        var value = $.Helpers.strFormat('{0}', obj.config[key]).replace(/\,/g, ', ');
        var manipulator = $('<div />');
        var field = $('<input />')
            .attr('type', 'text')
            .addClass('preference-content-data-text')
            .appendTo(manipulator)
            .val(value)
            .keypress(function(event) {
                if (event.keyCode == 13) {
                    field.blur();
                }
            });
        // attach manipulator methods
        manipulator.get(0).getValue = function() {
            return field.val();
        };
        manipulator.get(0).setValue = function(value) {
            if (typeof(value) != 'string') {
                value = $.Helpers.strFormat('{0}', value).replace(/\,/g, ', ');
            }
            field.val(value);
        };
        manipulator.get(0).setDefault = function() {
            var defaultValue = obj.defaultConfig[key].value;
            this.setValue(defaultValue);
        }
        return manipulator.get(0);
    },

    createObjectManipulator: function(section, name, obj, key) {
        var value = JSON.stringify(obj.config[key]);
        var manipulator = $('<div />');
        var field = $('<input />')
            .attr('type', 'text')
            .addClass('preference-content-data-text')
            .appendTo(manipulator)
            .val(value)
            .keypress(function(event) {
                if (event.keyCode == 13) {
                    field.blur();
                }
            });
        // attach manipulator methods
        manipulator.get(0).getValue = function() {
            return field.val();
        };
        manipulator.get(0).setValue = function(value) {
            if (typeof(value) != 'string') {
                value = JSON.stringify(value);
            }
            field.val(value);
        };
        manipulator.get(0).setDefault = function() {
            var defaultValue = obj.defaultConfig[key].value;
            this.setValue(defaultValue);
        }
        return manipulator.get(0);
    },

    save: function(section, name, obj, entries) {
        var _this = this;
        var newData = $.extend(true, {}, obj.config);
        $.each(entries, function(i, entry) {
            var key = $(entry).data('key');
            var value = $(entry).data('manipulator').getValue();
            newData[key] = value;
        });
        // show the loader
        this.showLoader();
        var dfd = Vispa.preferenceHandler.commit(section, name, newData);
        dfd.always(function() {
            // hide the loader
            _this.hideLoader();
        });
        return dfd;
    }
});