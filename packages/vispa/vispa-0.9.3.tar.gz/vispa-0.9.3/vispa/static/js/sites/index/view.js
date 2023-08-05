var View = VispaModule.extend({

    init: function(config) {
        this.defaultConfig = {
            sidebarAlignment: {
                descr: 'The alignment of the sidebar',
                select: ['left', 'right'],
                type: 'string',
                value: 'left'
            },
            sidebarWidth: {
                descr: 'The width of the sidebar.',
                range: [0, Infinity],
                type: 'integer',
                value: 0
            },
            headerHeight: {
                descr: 'The height of the header',
                range: [0, Infinity],
                type: 'integer',
                value: 75
            }
        };
        this._super('view', this.defaultConfig, config);

        // attributes
        this.preferenceSettings = {priority: 12, entryOrder: ['sidebarAlignment', 'sidebarWidth', 'headerHeight']};
        this.settings = {
            headerMinHeight: 60,
            headerMaxHeight: 120,
            headerCollapseHeight: -1,//40
            headerCollapsedHeight: 30,
            sidebarMediumWidth: 150,
            sidebarMinWidth: 60,
            sidebarCollapseWidth: 30,
            sidebarCollapsedWidth: 0,
            sidebarSwipeMinOffsetFraction: 0.4,
            sidebarSwipeMaxDuration: 1000,
            sidebarSwipeFx: {
                duration: 0,
                easing: 'linear'
            },
            contentSwipeMinOffsetFraction: 0.3,
            contentSwipeMaxStartFraction: 0.2,
            safetyDelay: 50,
            holdDelay: 750,
            menuWidth: 180,
        };
        this.workflow = {
            headerCollapsed: false,
            headerResizing: false,
            sidebarCollapsed: false,
            sidebarResizing: false,
            sidebarMoving: false,
            lastHeaderHeight: null,
            lastSidebarWidth: null,
            lastWindowHeight: null,
            lastWindowWidth: null,
            welcomeIsVisible: true,
            contentIsVisible: false
        };
        this.nodes = {
            loader: null
        };

        // members
        this.menuHandler = new MenuHandler();
    },

    startup: function() {
        this.setupLayout();
        this.setupMenus();
        this.addPaletteCommands();
        this.applyConfig();
        this.setupTopics();
        this.hideOverlay();

        this.logger.debug('Started');
        return this;
    },

    applyConfig: function() {
        // sidebarAlignment
        this.updateLayout(this.config.sidebarAlignment);
        // sidebarWidth
        this.resizeSidebar(this.config.sidebarWidth);
        // headerHeight
        this.resizeHeader(this.config.headerHeight);
        return this;
    },

    setupLayout: function() {
        var _this = this;
        // set the resizable objects
        $('#header').resizable({
            handles: 's',
            resize: function() {
                _this.resizeHeader($(this).height());
            },
            start: function() {
                _this.workflow.headerResizing = true;
            },
            stop: function() {
                _this.resizeHeader($(this).height());
                window.setTimeout(function() {
                    _this.workflow.headerResizing = false;
                    $.Topic('prefs.update').publish('vispa', _this.name);
                }, _this.workflow.safetyDelay);
            }
        });
        $('.ui-resizable-s').css({
            height: 10,
            cursor: 'row-resize'
        });
        $('#sidebar').resizable({
            handles: 'e, w',
            resize: function() {
                _this.resizeSidebar($('#sidebar').width());
            },
            start: function() {
                _this.workflow.sidebarResizing = true;
            },
            stop: function() {
                _this.resizeSidebar($('#sidebar').width());
                window.setTimeout(function() {
                    _this.workflow.sidebarResizing = false;
                    $.Topic('prefs.update').publish('vispa', _this.name);
                }, _this.workflow.safetyDelay);
            }
        });
        $('.ui-resizable-w, .ui-resizable-e').css({
            width: 10,
            cursor: 'col-resize'
        });

        $(window).resize(function() {
            _this.onResize();
        });
        this.onResize();

        // touch gestures
        if($.Helpers.hasTouch()) {
            //this.bindTouchGestures();
        }

        // setup the loader
        this.nodes.loader = this.makeLoader('#body-wrapper');

        return this;
    },

    onResize: function() {
        var height = $(window).height();
        var width = $(window).width();
        var changed = this.workflow.lastWindowWidth != width || this.workflow.lastWindowHeight != height;
        if(changed) {
            this.updateLayout(this.config.sidebarAlignment);
            Vispa.extensionView.onResize();
            this.checkHeaderShadows();
            this.workflow.lastWindowHeight = height;
            this.workflow.lastWindowWidth = width;
        }
        return this;
    },

    bindTouchGestures: function() {
        var _this = this;
        $('#sidebar').on('scroll', function(event) {
            //$(this).scrollLeft( 0 );
        });
        $('#sidebar').on('swipeone', function(event, data) {
            // hide the sidebar when swipe direction is 'e->w'
            var abort = _this.workflow.sidebarCollapsed || _this.workflow.sidebarMoving || _this.workflow.sidebarResizing || !data;
            if(abort) {
                return;
            }
            if(data.duration > _this.settings.sidebarSwipeMaxDuration) {
                return;
            }
            var hDirection = data.description.split(':')[2];
            var isHorizontal = Math.abs(data.delta[0].lastX) > Math.abs(data.delta[0].lastY);
            if(hDirection != _this.config.sidebarAlignment || !isHorizontal) {
                return;
            }
            var offset = $('#sidebar').width() * _this.settings.sidebarSwipeMinOffsetFraction;
            if(data.delta[0].moved <= offset) {
                return;
            }
            _this.toggleSidebar(_this.settings.sidebarSwipeFx);
        });
        $('#content').on('swipeone', function(event, data) {
            var abort = !_this.workflow.sidebarCollapsed || _this.workflow.sidebarMoving || !data;
            if(abort) {
                return;
            }
            if(data.duration > _this.settings.sidebarSwipeMaxDuration) {
                return;
            }
            var hDirection = data.description.split(':')[2];
            var isHorizontal = Math.abs(data.delta[0].lastX) > Math.abs(data.delta[0].lastY);
            if(hDirection == _this.config.sidebarAlignment || !isHorizontal) {
                return;
            }
            var evtX = data.originalEvent.changedTouches ? data.originalEvent.changedTouches[0].clientX : data.originalEvent.clientX;
            var start, startCheck;
            if(_this.config.sidebarAlignment == 'left') {
                start = $('#content').width() * _this.settings.contentSwipeMaxStartFraction;
                startCheck = evtX - data.delta[0].moved < start;
            } else {
                start = $('#content').width() * (1 - _this.settings.contentSwipeMaxStartFraction);
                startCheck = evtX + data.delta[0].moved > start;
            }
            var offset = $('#content').width() * _this.settings.contentSwipeMinOffsetFraction;
            if(data.delta[0].moved < offset || !startCheck) {
                return;
            }
            _this.toggleSidebar(_this.settings.sidebarSwipeFx);
        });
        return this;
    },

    updateLayout: function(sidebarAlignment) {
        sidebarAlignment = sidebarAlignment || this.config.sidebarAlignment;
        var sidebarWidth = $('#sidebar').width();
        var windowWidth = $(window).width();
        switch(sidebarAlignment) {
            case 'left':
                $('#sidebar').css('right', '').css({
                    left: 0
                });
                $('#content').css('width', '').css({
                    left: sidebarWidth,
                    right: 0
                });
                $('#sidebar > .ui-resizable-w').hide();
                $('#sidebar > .ui-resizable-e').show();
                break;
            case 'right':
                $('#sidebar').css('left', '').css({
                    right: 0
                });
                $('#content').css('width', '').css({
                    left: 0,
                    right: sidebarWidth
                });
                $('#sidebar > .ui-resizable-e').hide();
                $('#sidebar > .ui-resizable-w').show();
                break;
            default:
                return this;
        }
        $('#sidebar, #content').height('100%');
        $('#header').width('100%');
        this.config.sidebarAlignment = sidebarAlignment;
        return this;
    },

    resizeHeader: function(height) {
        if(height < this.settings.headerCollapseHeight) {
            height = this.settings.headerCollapsedHeight;
            this.workflow.headerCollapsed = true;
        } else {
            if(height <= this.settings.headerMinHeight) {
                height = this.settings.headerMinHeight;
            } else if(height >= this.settings.headerMaxHeight) {
                height = this.settings.headerMaxHeight;
            }
            this.workflow.headerCollapsed = false;
        }
        $('#header').height(height);
        $('#sidebar').height('100%');
        $('#center').css('top', height);
        if(this.workflow.lastHeaderHeight != height) {
            this.resizeHeaderContent(height);
            Vispa.extensionView.onResize();
            this.checkHeaderShadows();
            this.workflow.lastHeaderHeight = height;
            this.config.headerHeight = height;
        }
        return this;
    },

    resizeHeaderContent: function(height) {
        Vispa.extensionView.resizeBadges(height);

        // collapsed header? => handle menu buttons
        var cl = this.workflow.headerCollapsed;
        $.each(['main', 'ws'], function(i, name) {
            $($.Helpers.strFormat('#menu-button-outer-{0}', name))
            .toggleClass('menu-button-outer', !cl)
            .toggleClass('menu-button-outer-small', cl);
            $($.Helpers.strFormat('#menu-button-{0}', name))
            .toggleClass($.Helpers.strFormat('menu-button-image-{0}', name), !cl)
            .toggleClass($.Helpers.strFormat('menu-button-image-{0}-small', name), cl);
        });

        // position the menu icons
        var mainBtn = $('#menu-button-outer-main');
        mainBtn.css({
            top: ($('#header-right').height() - mainBtn.height())*0.5,
            left: ($('#header-right').width() - mainBtn.width())*0.5
        });
        var wsBtn = $('#menu-button-outer-ws');
        wsBtn.css({
            top: ($('#header-left').height() - wsBtn.height())*0.5,
            left: ($('#header-left').width() - wsBtn.width())*0.5
        });

        // position the workspace label
        var wsLabel = $('#header-left-label');
        var top = (mainBtn.position().top - $.Helpers.pxToInt(wsLabel.css('font-size'))) * 0.5;
        $('#header-left-label').css('top', top + 3);//3 => font size conversion offsets
        return this;
    },

    toggleHeader: function() {
        if(this.workflow.headerCollapsed) {
            var height = $('#header').data('tmpHeight') || config.headerHeight;
            $('#header').removeData('tmpHeight');
            this.resizeHeader(height);
        } else {
            $('#header').data('tmpHeight', $('#header').height());
            this.resizeHeader(0);
        }
        return this;
    },

    resizeSidebar: function(width, fx) {
        var _this = this;
        if(this.workflow.sidebarMoving) {
            return;
        }
        if(width <= this.settings.sidebarCollapseWidth) {
            width = this.settings.sidebarCollapsedWidth;
        } else if(width <= this.settings.sidebarMinWidth) {
            width = this.settings.sidebarMinWidth;
        }
        fx = $.extend(true, {
            duration: 0,
            easing: 'easeOutExpo'
        }, fx);
        var dfd = $.Deferred();
        var resolve;
        if(fx.duration > 0) {
            resolve = function() {
                _this.workflow.sidebarCollapsed = width == _this.settings.sidebarCollapsedWidth;
                _this.workflow.sidebarMoving = false;
                dfd.resolve();
            };
            this.workflow.sidebarMoving = true;
        } else {
            resolve = dfd.resolve;
            this.workflow.sidebarMoving = false;
            this.workflow.sidebarCollapsed = width == this.settings.sidebarCollapsedWidth;
        }
        var windowWidth = $(window).width();
        switch(this.config.sidebarAlignment) {
            case 'left':
                $('#sidebar').css({left: 0, right: ''}).animate({
                    width: width
                }, fx.duration, fx.easing);
                $('#content').css('right', 0).animate({
                    left: width,
                    width: windowWidth - width
                }, fx.duration, fx.easing, resolve);
                break;
            case 'right':
                $('#sidebar').css({right: 0, left: ''}).animate({
                    width: width
                }, fx.duration, fx.easing);
                $('#content').css('left', 0).animate({
                    right: width,
                    width: windowWidth - width
                }, fx.duration, fx.easing, resolve);
                break;
            default:
                resolve();
                return dfd.promise();
        }
        if(this.workflow.lastSidebarWidth != width) {
            this.resizeSidebarContent(width, fx);
            Vispa.extensionView.onResize();
            this.workflow.lastSidebarWidth = width;
            this.config.sidebarWidth = width;
        }
        return dfd.promise();
    },

    resizeSidebarContent: function(width, fx) {
        // pass
        return this;
    },

    toggleSidebar: function(fx) {
        var _this = this;
        if(this.workflow.sidebarMoving) {
            return;
        }
        var width;
        if(this.workflow.sidebarCollapsed) {
            width = $('#sidebar').data('tmpWidth') || this.config.sidebarWidth || this.settings.sidebarMediumWidth;
            $('#sidebar').removeData('tmpWidth');
        } else {
            $('#sidebar').data('tmpWidth', $('#sidebar').width());
            width = this.settings.sidebarCollapsedWidth;
        }
        return this.resizeSidebar(width, fx);
    },

    collapseAll: function(fx) {
        // header
        if(!this.workflow.headerCollapsed) {
            $('#header').data('tmpHeight', $('#header').height());
            this.resizeHeader(0);
        }
        // sidebar
        if(!this.workflow.sidebarMoving && !this.workflow.sidebarCollapsed) {
            $('#sidebar').data('tmpWidth', $('#sidebar').width());
            this.resizeSidebar(0, fx);
        }
        return this;
    },

    expandAll: function(fx) {
        // header
        if(this.workflow.headerCollapsed) {
            var height = $('#header').data('tmpHeight') || this.config.headerHeight;
            $('#header').removeData('tmpHeight');
            this.resizeHeader(height);
        }
        // sidebar
        if(!this.workflow.sidebarMoving && this.workflow.sidebarCollapsed) {
            var width = $('#sidebar').data('tmpWidth') || this.config.sidebarWidth;
            $('#sidebar').removeData('tmpWidth');
            return this.resizeSidebar(width, fx);
        }
        return this;
    },

    checkHeaderShadows: function() {
        var headerWidth = $('#header-center').width(),
            contentWidth = 0;
        $.each(Vispa.extensionView.badges(), function(i, badge) {
            contentWidth += $(badge).width();
            contentWidth += $.Helpers.pxToInt($(badge).css('margin-left')) + $.Helpers.pxToInt($(badge).css('margin-right'));
        });
        // left shadow
        if($('#extension-badges').scrollLeft()) {
            if ($('#header-left-shadow').css('display') == 'none') {
                $('#header-left-shadow').fadeIn(200);
            }
        } else {
            if ($('#header-left-shadow').css('display') != 'none') {
                $('#header-left-shadow').fadeOut(200);
            }
        }
        // right shadow
        // the -1 fixes scaling bugs
        if(contentWidth - $('#extension-badges').scrollLeft()-1 > headerWidth) {
            if ($('#header-right-shadow').css('display') == 'none') {
                $('#header-right-shadow').fadeIn(200);
            }
        } else {
            if ($('#header-right-shadow').css('display') != 'none') {
                $('#header-right-shadow').fadeOut(200);
            }
        }
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
    },

    hideWelcome: function(fx) {
        if(!this.workflow.welcomeIsVisible) {
            return this;
        }
        fx = $.extend(true, {duration: 50, easing: 'linear'}, fx);
        $('#content-welcome').fadeOut(fx.duration, fx.easing);
        this.workflow.welcomeIsVisible = false;
        return this;
    },

    showWelcome: function(fx) {
        if(this.workflow.welcomeIsVisible) {
            return this;
        }
        fx = $.extend(true, {duration: 50, easing: 'linear'}, fx);
        //$('#content-main').fadeOut(fx.duration, fx.easing);
        $('#content-welcome').fadeIn(fx.duration, fx.easing);
        this.workflow.welcomeIsVisible = true;
        return this;
    },

    hideContent: function(fx) {
        if(!this.workflow.contentIsVisible) {
            return this;
        }
        fx = $.extend(true, {duration: 50, easing: 'linear'}, fx);
        $('#content-body').fadeOut(fx.duration, fx.easing);
        this.workflow.contentIsVisible = false;
        return this;
    },

    showContent: function(fx) {
        if(this.workflow.contentIsVisible) {
            return this;
        }
        fx = $.extend(true, {duration: 50, easing: 'linear'}, fx);
        $('#content-body').fadeIn(fx.duration, fx.easing);
        this.workflow.contentIsVisible = true;
        return this;
    },

    toggleDisplay: function(fx) {
        this.workflow.welcomeIsVisible ? this.hideWelcome(fx) : this.showWelcome(fx);
        this.workflow.contentIsVisible ? this.hideContent(fx) : this.showContent(fx);
        return this;
    },

    hideFrames: function() {
        Vispa.commandPalette.hide();
        Vispa.preferenceView.hide();
        return self;
    },

    makeLoader: function(target) {
        var loaderImg = $('<img />').attr('src', Vispa.urlHandler.dynamic('static/img/maingui/loader2.gif'));
        var loaderText = $('<span />').html('Loading<br /><br />');
        var loaderInner = $('<div />')
            .addClass('loader-inner')
            .append(loaderText, loaderImg);
        var loader = $('<div />')
            .addClass('loader-outer ui-widget-overlay')
            .append(loaderInner);
        if (target) {
            loader.appendTo(target);
        }
        return loader.get(0);
    },

    setupMenus: function() {
        var mainItems = Vispa.menuItems('main');
        var mainPosition = {
            at: 'right bottom',
            my: 'right top'
        };
        this.menuHandler.create('menu-main', '#menu-button-main', mainItems, mainPosition);

        var wsItems = Vispa.menuItems('ws');
        var wsPosition = {
            at: 'left bottom',
            my: 'left top'
        };
        this.menuHandler.create('menu-ws', '#menu-button-ws', wsItems, wsPosition);
        return self;
    },

    addPaletteCommands: function() {
        var _this = this;
        Vispa.commandPalette.add('view', {
            key: 'Sidebar: toggle',
            callback: function() {
                var promise = _this.toggleSidebar({
                    duration: 250,
                    easing: 'easeOutExpo'
                });
                $.when(promise).then(function() {
                    $.Topic('prefs.update').publish('vispa', _this.name);
                });
            }
        }).add('view', {
            key: 'Sidebar: left',
            callback: function() {
                _this.updateLayout('left');
                $.Topic('prefs.update').publish('vispa', _this.name);
            }
        }).add('view', {
            key: 'Sidebar: right',
            callback: function() {
                _this.updateLayout('right');
                $.Topic('prefs.update').publish('vispa', _this.name);
            }
        }).add('view', {
            key: 'Content: hide all',
            callback: function() {
                Vispa.extensionManager.hideInstance();
            }
        }).enableContext('view');
        return this;
    },

    setupTopics: function() {
        var _this = this;
        var mainMenuAdd = function() {
            var args = $.makeArray(arguments);
            args.unshift('#menu-main');
            _this.menuHandler.add.apply(_this.menuHandler, args);
        };
        $.Topic('menu.main.add').subscribe(function() {
            return mainMenuAdd.apply(_this, arguments);
        });

        var wsMenuAdd = function() {
            var args = $.makeArray(arguments);
            args.unshift('#menu-ws');
            _this.menuHandler.add.apply(_this.menuHandler, args);
        };
        $.Topic('menu.ws.add').subscribe(function() {
            return wsMenuAdd.apply(_this, arguments);
        });

        var wsMenuModify = function() {
            var args = $.makeArray(arguments);
            args.unshift('#menu-ws');
            _this.menuHandler.modify.apply(_this.menuHandler, args);
        };
        $.Topic('menu.ws.modify').subscribe(function() {
            return wsMenuModify.apply(_this, arguments);
        });

        var wsMenuRemove = function() {
            var args = $.makeArray(arguments);
            args.unshift('#menu-ws');
            _this.menuHandler.remove.apply(_this.menuHandler, args);
        };
        $.Topic('menu.ws.remove').subscribe(function() {
            return wsMenuRemove.apply(_this, arguments);
        });
        return this;
    }
});