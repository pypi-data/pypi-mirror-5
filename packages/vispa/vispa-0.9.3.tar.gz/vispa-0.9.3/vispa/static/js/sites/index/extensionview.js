var ExtensionView = VispaModule.extend({

    init: function(config) {
        this.defaultConfig = {};
        this._super('extensionView', this.defaultConfig, config);

        // attributes
        this.settings = {
            badgeMargin: {
                top: 6,
                right: 3,
                bottom: 1,
                left: 3
            },
            badgeTitleHeight: 24,
            collapsedBadgeWidth: 45,
            badgeRatio: 4./3.,
            draggableDistance: 20,
            contentSwitchFx: {duration: 50, easing: 'linear'},
            shortcuts: {
                shiftLeft: 'ctrl+shift+left',
                shiftRight: 'ctrl+shift+right',
                shiftTemplate: 'ctrl+shift+{0}'
            }
        };
        this.workflow = {
            currentFullInstance: null
        };
        this.nodes = {
            menuContainer: null
        };
        this.instances = {};
    },

    startup: function() {
        this.setupMarkup();
        this.applyConfig();
        this.setupShortcuts();

        this.logger.debug('Started');
        return this;
    },

    setupMarkup: function() {
        var _this = this;

        // setup the badge container
        var resizePlaceholder = function() {
            var height = $('#extension-badges').height() - (_this.settings.badgeMargin.top + _this.settings.badgeMargin.bottom);
            $('.extension-badge-placeholder').css({
                width: _this.config.badgeRatio * height,
                height: height
            });
        };
        $('#extension-badges')
            .scroll(function() {
                Vispa.view.checkHeaderShadows();
                $(this).scrollTop(0);
            }).sortable({
                axis: 'x',
                distance: this.settings.draggableDistance,
                cursor: 'move',
                opacity: 0.75,
                forcePlaceholderSize: true,
                handle: '.extension-badge-top',
                start: function(event, ui) {
                    $(ui.item).data('isDragged', true);
                    resizePlaceholder.apply(null, arguments);
                },
                sort: function() {
                    $(this).scrollTop(0);
                },
                stop: function(event, ui) {
                    $(ui.item).data('isDragged', false);
                    event.originalEvent.stopPropagation();
                    event.originalEvent.preventDefault();
                }
            }).disableSelection();
        this.setupBadgeMenu();

        // setup the menu container
        this.nodes.menuContainer = $('<div />')
            .addClass('extension-menu-container')
            .appendTo('#content-header-right')
            .get(0);

        this.setupScrolling();
        return this;
    },

    setupScrolling: function() {
        if(!Vispa.useSlimScroll()) {
            return this;
        }
        $('#extension-badges')
            .slimScrollHorizontal({
                height: '100%',
                width: '100%',
                position: 'bottom',
                distance: '2px',
                wheelStep: 10,
                wrapperClass: 'extension-badges'
            }).parent()
            .css('position', 'absolute');
        return self;
    },

    onResize: function() {
        this.resizeCurrentFullInstance();
        return this;
    },

    addBadge: function(instance) {
        var _this = this;
        var badge = this.makeBadge(instance);
        $(badge).appendTo('#extension-badges');

        // create a menu for each badge
        var menuId = $.Helpers.strFormat('{0}-menu', badge.id);
        var items = instance.menuEntries;
        var openCallback = Vispa.view.menuHandler.create(menuId, badge, items, {}, false, $('body'));
        var showMenu = function(event) {
            var badgeWidth = $(badge).width();
            var offset = $.Helpers.hasTouch() ? 10 : -10;
            var position = {
                at: $.Helpers.strFormat('left+{0} top+{1}', event.pageX + offset, event.pageY + offset),
                my: 'left top',
                of: $('body')
            };
            openCallback(position);
            event.stopPropagation();
            event.preventDefault();
        };
        $(badge)
            .click(function() {
                if(_this.workflow.currentFullInstance != instance._id) {
                    Vispa.extensionManager.showInstance(instance);
                }
            }).on('contextmenu', showMenu);
        // simulate a hold event for touch devices
        if($.Helpers.hasTouch()) {
            var doShow = true;
            $($(badge).data('sortHandle'))
                .on('vmousedown', function(event) {
                    // the extension header menu requires vmousedown
                    // so tell this event as well that a badge was clicked before
                    event.originalEvent.usedForBadgeMenu = true;
                }).on('mousedown', function(event) {
                    event.originalEvent.usedForBadgeMenu = true;
                    window.setTimeout(function() {
                        if(doShow && !$(badge).data('isDragged')) {
                            showMenu(event);
                        }
                        doShow = true;
                    }, Vispa.view.settings.holdDelay);
                }).on('mouseup', function() {
                    doShow = false;
                    window.setTimeout(function() {
                        doShow = true;
                    }, Vispa.view.settings.holdDelay);
                });
            $(badge).on('vmousedown', function(event) {
                // same reason as above (sortHandle vmousedown)
                event.originalEvent.usedForBadgeScrolling = true;
            });
        }

        Vispa.view.checkHeaderShadows();
        return badge;
    },

    makeBadge: function(instance) {
        var _this = this;
        var badgeId = $.Helpers.strFormat('{0}-badge', instance._id);
        var title = instance.getTitle();

        var height = $('#extension-badges').height() - (this.settings.badgeMargin.top + this.settings.badgeMargin.bottom);
        var width = this.settings.badgeRatio * ( height - this.settings.badgeTitleHeight );
        var badge = $('<div />')
            .attr({
                id: badgeId,
                alt: instance.getIdentifier(),
                title: instance.getIdentifier()
            }).addClass('extension-badge')
            .css({
                height: height,
                width: width
            });

        var top = $('<div />')
            .addClass('extension-badge-top')
            .appendTo(badge);
        var bottom = $('<div />')
            .addClass('extension-badge-bottom')
            .appendTo(badge);
        var topWrapper = $('<div />')
            .addClass('extension-badge-top-wrapper')
            .appendTo(top);
        var bottomWrapper = $('<div />')
            .addClass('extension-badge-bottom-wrapper')
            .appendTo(bottom);
        var labelOuter = $('<div />')
            .addClass('extension-badge-label-outer')
            .appendTo(bottomWrapper);
        var label = $('<div />')
            .addClass('extension-badge-label')
            .appendTo(labelOuter)
            .html(title)
            .css(this.badgeFontStyle(height));

        var select = function() {
            topWrapper.toggleClass('extension-badge-top-wrapper-selected', true);
            label.toggleClass('extension-badge-label-selected', true);
        };
        var diselect = function() {
            topWrapper.toggleClass('extension-badge-top-wrapper-selected', false);
            label.toggleClass('extension-badge-label-selected', false);
        };
        var remove = function() {
            // empty the menu
            var selector = $.Helpers.strFormat('#{0}-menu', $(badge).attr('id'));
            Vispa.view.menuHandler.empty(selector);
            // remove
            $(badge).remove();
        };
        var update = function(title, alt) {
            var height = $('#extension-badges').height() - (_this.settings.badgeMargin.top + _this.settings.badgeMargin.bottom);
            label
                .html(title)
                .css(_this.badgeFontStyle(height));
            badge.attr({
                alt: alt,
                title: alt
            });
        };
        var hide = function() {
            badge.hide();
        };
        var show = function() {
            badge.show().css('display', 'inline-block');
        };
        badge.data('sortHandle', top);
        badge.data('select', select);
        badge.data('diselect', diselect);
        badge.data('remove', remove);
        badge.data('update', update);
        badge.data('hide', hide);
        badge.data('show', show);
        badge.data('instanceId', instance._id);
        return badge.get(0);
    },

    resizeBadges: function(height) {
        var _this = this;
        var badges = this.badges();
        if(!badges.length) {
            return self;
        }
        // collapsed?
        if(Vispa.view.workflow.headerCollapsed) {
            $.each(badges, function(i, badge) {
                $(badge).toggleClass('extension-badge', false).toggleClass('extension-badge-collapsed', true).css({
                    height: height,
                    width: _this.settings.collapsedBadgeWidth
                });
            });
            return self;
        }
        height -= this.settings.badgeMargin.top + this.settings.badgeMargin.bottom;
        $.each(badges, function(i, badge) {
            $(badge).toggleClass('extension-badge', true).toggleClass('extension-badge-collapsed', false).css({
                height: height,
                width: _this.settings.badgeRatio * (height - _this.settings.badgeTitleHeight)
            });
        });
        return this;
    },

    badgeFontStyle: function(height) {
        return {//TODO
            'font-size': 11
        };
    },

    setupBadgeMenu: function() {
        var _this = this;
        var items = [
            {
                label: 'Close all Extensions',
                icon: 'ui-icon-close',
                callback: function() {
                    Vispa.extensionManager.removeAllFullInstances();
                }
            }
        ];
        var position = {};
        var openCallback = Vispa.view.menuHandler.create('badge-menu', '#header', items, position, false, $('body'));
        var showMenu = function(event) {
            // define a better position that depends on the event data
            var offset = $.Helpers.hasTouch() ? 10 : -10;
            position = {
                at: 'left top',
                my: $.Helpers.strFormat('left+{0} top+{1}', event.pageX+offset, event.pageY+offset),
                of: $('body')
            };
            openCallback(position);
            event.stopPropagation();
            event.preventDefault();
        }
        $('#extension-badges').on('contextmenu', showMenu);

        // simulate a hold event for touch devices
        if($.Helpers.hasTouch()) {
            var doShow = true;
            // store if vmousedown has fired since jQMobile seems
            // to be buggy at this point
            var vFired = false;
            $('#extension-badges')
                .on('vmousedown', function(event) {
                    if(vFired) {
                        return;
                    }
                    if(!event.originalEvent.usedForBadgeScrolling) {
                        // this enabled scrolling for badges
                        // and disabled touch/hold selection
                        event.preventDefault();
                    }
                    vFired = true;
                    window.setTimeout(function() {
                        vFired = false;
                        if(doShow && !event.originalEvent.usedForBadgeMenu) {
                            showMenu(event);
                        }
                        doShow = true;
                    }, Vispa.view.settings.holdDelay);
                }).on('vmouseup', function() {
                    doShow = false;
                    window.setTimeout(function() {
                        doShow = true;
                    }, Vispa.view.settings.holdDelay);
                });
        }
        return this;
    },

    badges: function() {
        return $('#extension-badges').children();
    },

    addExtensionMenu: function(instance) {
        // the menu box
        var menuBox = $('<div />')
            .addClass('extension-menu-box')
            .appendTo(this.nodes.menuContainer);

        // the button
        var textSpan = $('<span />').html('Menu');
        var icon = $('<span />')
            .addClass('ui-icon ui-icon-triangle-1-s')
            .css({
                float: 'right',
                'margin-right': 4,
            });
        var menuBtnInner = $('<div />')
            .addClass('extension-menu-button-inner')
            .append(textSpan, icon);
        var menuBtn = $('<div />')
            .addClass('extension-menu-button ui-state-default ui-corner-all')
            .attr('title', 'Extension Menu')
            .hover(function() {
                $(this).toggleClass('ui-state-hover', true);
            }, function() {
                $(this).toggleClass('ui-state-hover', false);
            }).append(menuBtnInner)
            .appendTo(menuBox);
        // create the UI
        var menuId = $.Helpers.strFormat('{0}-extension-menu', instance._id);
        var items = instance.menuEntries;
        var openCallback = Vispa.view.menuHandler.create(menuId, menuBtn, items, {}, false, $('body'));
        menuBtn.click(openCallback);

        // the drop zone
        var dropZone = this.makeDropZone(instance);
        menuBox.append(dropZone);

        return menuBox.get(0);
    },

    makeDropZone: function(instance) {
        var _this = this;
        var items = instance.menuEntries;
        var dropZone;
        // show used dropzone?
        var styleDropZone = function() {
            var hasChildren = !!$(dropZone).children().length;
            $(dropZone).toggleClass('extension-menu-dropzone-used', hasChildren);
        };
        // uniqueness function
        var hasItem = function(item) {
            var hit = false;
            $.each($(dropZone).children(), function(i, child) {
                var childItem = $(child).data('menuItem');
                if(childItem.label == item.label) {
                    hit = true;
                    return false;
                }
            });
            return hit;
        };
        // the adding function
        var addItem = function(item, byDrag) {
            // is the item already in the drop zone?
            if(hasItem(item)) {
                return false;
            }

            // markup
            var ico = '';
            if(item.icon) {
                ico = $('<span />')
                    .addClass('ui-icon ' + item.icon)
                    .css({
                        float: 'left',
                        'margin-right': 4,
                    });
            }
            var text = $('<span />').html(item.label);
            // the inner container
            var btnInner = $('<div />')
                .addClass('extension-menu-shorthand-button-inner')
                .append(ico, text);
            // the button
            var btn = $('<div />')
                .addClass('extension-menu-shorthand-button ui-state-default ui-corner-all')
                .hover(function() {
                    $(this).toggleClass('ui-state-hover', true);
                }, function() {
                    $(this).toggleClass('ui-state-hover', false);
                }).click(function() {
                    item.callback();
                }).data('menuItem', item)
                .append(btnInner)
                .appendTo(dropZone);
            // style the drop zone
            styleDropZone();

            // tell the config?
            if(byDrag && $.inArray(item.label, instance._config.droppedMenuEntries) < 0) {
                instance._config.droppedMenuEntries.push(item.label);
                // update
                $.Topic('prefs.update').publish('extensions', instance._factory._id);
            }
        };
        // the removing function
        var removeItem = function(draggable) {
            var label = draggable.data('menuItem').label;
            // remove the ui
            draggable.remove();
            // style the drop zone
            styleDropZone();
            // tell the server
            var idx = $.inArray(label, instance._config.droppedMenuEntries);
            if(idx >= 0) {
                instance._config.droppedMenuEntries.splice(idx, 1);
                // update
                $.Topic('prefs.update').publish('extensions', instance._factory._id);
            }
        };
        dropZone = $('<div />')
            .addClass('extension-menu-dropzone')
            .attr('title', 'Menu Dropzone')
            .droppable({
                accept: function(draggable) {
                    // check the class
                    var acceptClass = $.Helpers.strFormat('extension-{0}-menu-draggable', instance._id);
                    var hasClass = draggable.hasClass(acceptClass);
                    if(!hasClass) {
                        return false;
                    }
                    // check uniqueness
                    if(hasItem(draggable.data('menuItem'))) {
                        return false;
                    }
                    return true;
                },
                activeClass: 'extension-menu-box-active',
                hoverClass: 'extension-menu-box-hover',
                drop: function(event, ui) {
                    if(ui.draggable) {
                        var item = ui.draggable.data('menuItem');
                        addItem(item, true);
                    }
                }
            }).sortable({
                axis: 'x',
                distance: _this.settings.draggableDistance,
                cursor: 'move',
                opacity: 0.75,
                forcePlaceholderSize: true,
                start: function(event, ui) {
                    ui.item.toggleClass('extension-menu-shorthand-button-keepable', true);
                },
                sort: function(event, ui) {
                    var headerHeight = Vispa.view.workflow.lastHeaderHeight;
                    var contentHeaderHeight = $('#content-header').height();
                    var deletable = event.clientY > headerHeight + 3 * contentHeaderHeight;
                    ui.item.toggleClass('extension-menu-shorthand-button-deletable', deletable);
                },
                stop: function(event, ui) {
                    ui.item.toggleClass('extension-menu-shorthand-button-deletable', false);
                    ui.item.toggleClass('extension-menu-shorthand-button-keepable', false);
                    // remove?
                    var headerHeight = Vispa.view.workflow.lastHeaderHeight;
                    var contentHeaderHeight = $('#content-header').height();
                    var deletable = event.clientY > headerHeight + 3 * contentHeaderHeight;
                    if(deletable) {
                        removeItem(ui.item);
                        return;
                    }
                    // get the new order and snyc it with the config
                    // if there is more than one child
                    var children = $(dropZone).children();
                    if(children.length < 2) {
                        return;
                    }
                    var labels = [];
                    $.each(children, function(i, child) {
                        labels.push($(child).data('menuItem').label);
                    });
                    instance._config.droppedMenuEntries = labels;
                    // update
                    $.Topic('prefs.update').publish('extensions', instance._factory._id);
                }
            });

        // add already dragged menu entries
        var deepItems = {};
        var targetItems = items.concat();
        while (targetItems.length) {
            var item = targetItems.pop();
            if (item.children && item.children.items && $.isArray(item.children.items)) {
                targetItems = targetItems.concat(item.children.items);
            }
            if (item.label && !item.children && !deepItems[item.label]) {
                deepItems[item.label] = item;
            }
        }

        $.each(instance._config.droppedMenuEntries, function(i, label) {
            if (deepItems[label]) {
                addItem(deepItems[label]);
                delete deepItems[label];
            }
        });

        return dropZone.get(0);
    },

    addFullInstance: function(instance, showBadge) {
        if (this.instances[instance._id]) {
            return this;
        }
        // setup the view for that instance
        var data = this.setupFullInstance(instance, showBadge);

        return this.instances[instance._id] = $.extend(true, {
            instance: instance
        }, data);
    },

    setupFullInstance: function(instance, showBadge) {
        var contentId = $.Helpers.strFormat('{0}-content', instance._id);
        var content = $('<div />')
            .attr('id', contentId)
            .addClass('extension-content')
            .appendTo('#content-body')
            .get(0);
        var badge = this.addBadge(instance);
        var menu = this.addExtensionMenu(instance);
        var loader = Vispa.view.makeLoader(content);

        // show the badge?
        if (showBadge) {
            $(badge).data('show')();
        }

        return {
            content: content,
            badge: badge,
            menu: menu,
            loader: loader
        };
    },

    showFullInstance: function(instance, fx) {
        fx = $.extend(true, this.settings.contentSwitchFx, fx);
        Vispa.view.hideWelcome(fx);
        Vispa.view.showContent(fx);

        var data = this.instances[instance._id];
        $(data.content).fadeIn(fx.duration, fx.easing);
        this.workflow.currentFullInstance = instance._id;
        Vispa.updateTitle(instance._id);
        // select the badge
        $(data.badge).data('select')();
        // show the menu
        $(data.menu).show();
        // update the pathbar
        var value = instance.getIdentifier();
        Vispa.pathBar.setValue(value).show();
        return this;
    },

    hideFullInstance: function(instance, fx, showWelcome) {
        fx = $.extend(true, this.settings.contentSwitchFx, fx);
        if(this.workflow.currentFullInstance != instance._id) {
            return this;
        }
        if(showWelcome || showWelcome === undefined) {
            Vispa.view.hideContent(fx);
            Vispa.view.showWelcome(fx);
        }

        var data = this.instances[instance._id];
        $(data.content).fadeOut(fx.duration, fx.easing);
        this.workflow.currentFullInstance = null;
        Vispa.updateTitle();
        // disselect the badge
        $(data.badge).data('diselect')();
        // hide the menu
        $(data.menu).hide();
        // reset the pathbar
        Vispa.pathBar.setValue();
        return this;
    },

    hideCurrentFullInstance: function(byUrl) {
        var ci = this.workflow.currentFullInstance;
        if(ci) {
            Vispa.extensionManager.hideInstance(ci, byUrl);
        }
        return this;
    },

    switchFullInstance: function(instance, fx) {
        if(this.workflow.currentFullInstance == instance._id) {
            return this;
        }
        this.hideCurrentFullInstance(fx, false);
        this.showFullInstance(instance, fx);
        return this;
    },

    removeFullInstance: function(instance, fx) {
        fx = $.extend(true, this.settings.contentSwitchFx, fx);
        this.hideFullInstance(instance, fx);
        var data = this.instances[instance._id];
        // remove the content
        $(data.content).remove();
        // remove the badge
        $(data.badge).data('remove')();
        delete this.instances[instance._id];
        return this;
    },

    hideCurrentInstance: function(byUrl) {
        //TODO: check full and frame instances
        this.hideCurrentFullInstance(byUrl);
        return this;
    },

    goToFullInstance: function(next) {
        var badges = this.badges();
        if(!badges.length) {
            return this;
        }
        var instanceIds = [];
        $.each(badges, function(i, badge) {
            instanceIds.push($(badge).data('instanceId'));
        });
        var newInstanceId;
        if(typeof(next) == 'number') {
            // no action, when there is no instance at the target position
            if(next > instanceIds.length) {
                return this;
            }
            newInstanceId = instanceIds[next-1];
        } else {
            if(!this.workflow.currentFullInstance) {
                // no instance selected, go to the first/last one
                newInstanceId = next ? instanceIds[instanceIds.length-1] : instanceIds[0];
            } else {
                // no action, when the current instance is the most right/left one
                var idx = $.inArray(this.workflow.currentFullInstance, instanceIds);
                if(next) {
                    if(idx == instanceIds.length-1) {
                        return this;
                    } else {
                        newInstanceId = instanceIds[idx+1];
                    }
                } else {
                    if(idx == 0) {
                        return this;
                    } else {
                        newInstanceId = instanceIds[idx-1];
                    }
                }
            }
        }
        // switch the instance
        Vispa.extensionManager.showInstance(newInstanceId);
        return this;
    },

    resizeCurrentFullInstance: function() {
        if(!this.workflow.currentFullInstance) {
            return this;
        }
        var ci = Vispa.extensionManager.getInstance(this.workflow.currentFullInstance);
        if(ci) {
            ci.onResize();
        }
        return this;
    },

    setupShortcuts: function() {
        var _this = this;
        // register the shortcuts for full instance shifting
        $.Shortcuts('global').add(this.settings.shortcuts.shiftLeft, function() {
            _this.goToFullInstance(false);
        });
        $.Shortcuts('global').add(this.settings.shortcuts.shiftRight, function() {
            _this.goToFullInstance(true);
        });
        // register shortcuts for jumping to a full instance
        $.each([1, 2, 3, 4, 5, 6, 7, 8, 9], function(i, key) {
            $.Shortcuts('global').add($.Helpers.strFormat(_this.settings.shortcuts.shiftTemplate, key), function() {
                _this.goToFullInstance(key);
            });
        });
        return this;
    }
});