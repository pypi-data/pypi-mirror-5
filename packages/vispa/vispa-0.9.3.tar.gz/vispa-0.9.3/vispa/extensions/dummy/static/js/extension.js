var DummyExtension = ExtensionBase.extend({

    init: function() {
        this._super();
        var _this = this;

        this.name = 'dummy';

        this.factories = {
            full: new DummyFactory()
        };
    }
});

var DummyFactory = ExtensionFactoryFull.extend({

    init: function() {
        this._super();
        var _this = this;

        this.defaultConfig = {
            backgroundColor: {
                descr: 'The background color of this extension',
                type: 'string',
                select: ['white', 'red', 'blue'],
                value: 'white'
            }
        };

        this.name = 'Dummy';
        this.constructor = DummyContent;

        this.menuEntries = [{
            label: 'new Dummy ...',
            icon: 'ui-icon-plus',
            callback: function() {
                _this._create('~/user/vispa/analyses/ttH.txt');
            }
        }];

        this.fileHandlers = {
            txt: {
                priority: 1,
                callback: function() {
                    console.log('txt file Handler for', _this._id, arguments);
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

var DummyContent = ExtensionContentFull.extend({

    init: function(config, path) {
        this._super(config);
        var _this = this;
        this.path = path;

        this.menuEntries = [{
            label: 'My Id',
            icon: 'ui-icon-comment',
            callback: function() {
                $.Topic('msg.info').publish(_this._id);
            }
        }];
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

    render: function(node) {
        this.nodes.content = $('<div />')
            .addClass('dummy-full-body')
            .css('background-color', this._config.backgroundColor)
            .html($.Helpers.strFormat('Dummy Content<br />Number: {0}<br />Workspace id: {1}', this._number, this._wid))
            .get(0);
        $(node).append(this.nodes.content);
        return this;
    }
});

$(function() {
    // register the Extension
    $.Topic('extman.register').publish(DummyExtension);
});