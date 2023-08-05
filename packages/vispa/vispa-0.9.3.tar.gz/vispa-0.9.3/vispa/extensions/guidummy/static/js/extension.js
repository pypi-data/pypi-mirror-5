var GuiDummyExtension = ExtensionBase.extend({

    init: function(vispa) {
        this._super(vispa);
        var _this = this;

        this.name = 'guidummy';

        this.factories = {
            full: new GuiDummyFactory(this._vispa)
        };
    }
});

var GuiDummyFactory = ExtensionFactoryFull.extend({

    init: function(vispa) {
        this._super(vispa);
        var _this = this;

        this.defaultConfig = {
            backgroundColor: {
                descr: 'The background color of this extension',
                select: ['white', 'red', 'blue'],
                type: 'string',
                value: 'white'
            }
        };

        this.name = 'GuiDummy';
        this.constructor = GuiDummyContent;

        this.menuEntries = [
            {
                label: 'new GuiDummy ...',
                icon: 'ui-icon-plus',
                callback: function() {
                    _this._create('~/user/vispa/analyses/ttH.txt');
                }
            }
        ];

        this.fileHandlers = {
            png: {
                priority: 1,
                callback: function() {
                    callback: function(path) {
                        _this._create(path);
                    }
                }
            },
            '/': {
                priority: 10,
                callback: function() {
                    console.log('open path with', _this._id, arguments);
                }
            }
        };

        this.urlChannelHandlers = {
            dummyUrlChannel1: {
                priority: 1,
                callback: function() {
                    console.log('url channel "dummyUrlChannel1" called, and passed to', _this._key, arguments);
                }
            }
        };
    }
});

var GuiDummyContent = ExtensionContentFull.extend({

    init: function(vispa, config, path) {
        this._super(vispa, config);
        var _this = this;
        this.path = path;

        this.menuEntries = [
            {
                label: 'My Id',
                icon: 'ui-icon-comment',
                callback: function() {
                    $.Topic('msg.info').publish(_this._id);
                }
            }
        ];
        this.nodes = {};
    },

    getIdentifier: function() {
        return this.path;
    },

    applyConfig: function() {
        // backgroundColor
        $(this.nodes.content).css('background-color', this._config.backgroundColor);
        return this;
    },

    getContent: function() {
        return this.nodes.content = $('<div />')
            .addClass('dummy-full-body')
            .css('background-color', this._config.backgroundColor)
            .html($.Helpers.strFormat('<img src="extensions/guidummy/{0}', this._number))
            .get(0);
    }
});

$(function() {
    // register the Extension
    $.Topic('extman.register').publish(GuiDummyExtension);
});