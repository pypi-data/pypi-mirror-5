// Extension structure:
//      Extension -> Factory1 -> ContentInstance1
//                            -> ContentInstance2
//                            -> ...
//                            -> ContentInstanceN
//                -> Factory2 -> ...
//                -> ...      -> ...
//                -> FactoryN -> ...

// Underscore syntax:
//      '_' at the beginning of a member means that its value is already set (e.g. '_logger'),
//      whereas members without a '_' should can and/or should set by yourself (e.g. 'name')

// first, we create a Class (see http://ejohn.org/blog/simple-javascript-inheritance/ for more info)
// that inherits from 'ExtensionBase' and that will be our extesion main class
var DemoExtension = ExtensionBase.extend({

    init: function() {
        // call the super function (in this case, ExtensionBase.init)
        this._super();

        // set the name of this extension (should match the folder name of this extension in the
        // vispa/extensions folder)
        this.name = 'demo';

        // register the factories by creating an object, key -> factory instance
        this.factories = {
            full: new DemoFactory()
        };
    }
});

// define a factory by inheriting from 'ExtensionFactory', but since we want to have a 'full'
// factory (the content of 'full' factories are displayed in the center view wit maximum size)
// we inherit from a subclass called 'ExtensionFactoryFull'
var DemoFactory = ExtensionFactoryFull.extend({

    init: function() {
        // call the super function
        this._super();

        // store 'this' (the factory) as '_this' to use it in functions wherein 'this'points at the
        // functions caller
        var _this = this;

        // define a name for this factory
        this.name = 'Demo';

        // define the content constructor for this factory; note that factories are instantiated
        // once (in the Extension class) whereas instances from the content classes are created
        // dynamically
        this.constructor = DemoContent;

        // factories can define config objects that are kept in sync with the central database
        // per profile/user; the values of that config will be visible to each content instance
        this.defaultConfig = {
            backgroundColor: {
                descr: 'The background color of this extension',
                type: 'string',
                select: ['white', 'red', 'blue'],
                value: 'white'
            }
        };

        // menu entries as a list of objects containing 'label', 'icon', 'alt' and 'callback'
        // submenus are possible by using the 'children' key and the syntax as shown below
        // note the '_create' function in the callback of the first item
        // items of 'menuEntries' will be shown in the main menu
        this.menuEntries = [
            {
                label: 'new Demo ...',
                icon: 'ui-icon-plus',
                alt: 'some text',
                callback: function() {
                    // '_create' will create a new instance of 'constructor'
                    // the arguments will be shifted by 1 since the first constructor parameter
                    // is the config, e.g. in this case 'fooArg' will be the second and 'barArg'
                    // will be the third argument
                    _this._create('fooArg', 'barArg');
                }
            }, {
                label: 'Demo submenu',
                children: {
                    items: [{
                        label: 'Demo subitem',
                        callback: function() {
                            // code
                        }
                    }]
                }

            }
        ];

        // file handlers will listen to the opening of files with a specifig file extension, e.g.
        // the handler with the key 'txt' will listen to files like 'file.txt' ('/' => directories)
        // you can define a priority and a callback that will receive the path of the opened file
        this.fileHandlers = {
            txt: {
                priority: 1,
                callback: function(path) {
                    console.log('txt file Handler for', _this._id, path);
                }
            },
            '/': {
                priority: 10,
                callback: function(path) {
                    console.log('open path with', _this._id, path);
                }
            }
        };

        // url channel handlers will listen to url parameters, e.g. the example below will listen
        // to requests '<serveraddress>/?demochannel=a:b:c' where 'a', 'b' and 'c' will be the first
        // three parameters of the defined callback (the separator ':' is defined in the settings
        // of the extensionManager)
        this.urlChannelHandlers = {
            demochannel: {
                priority: 1,
                callback: function() {
                    console.log('url channel "demochannel" called and passed to', _this._key, arguments);
                }
            }
        };
    }
});

// define the content class that is used by 'DemoFactory'
// as mentioned above, instances of this class will be created dynamically on demand
var DemoContent = ExtensionContentFull.extend({

    init: function(config, path) {
        // call the super function and pass config which then will be usable as 'this._config'
        this._super(config);

        // store 'this'
        var _this = this;

        // store 'path' (which is the first parameters passed to '_create' of the factory)
        // according to the code above, its value will be 'fooArg'
        this.path = path;

        // same menu definition as showd in the extension/factory
        // items of 'menuEntries' will be shown in the extension menu
        this.menuEntries = [{
            label: 'My Id',
            icon: 'ui-icon-comment',
            callback: function() {
                $.Topic('msg.info').publish(_this._id);
            }
        }];
        this.nodes = {};
    },

    // the identifier should be a string that completely represents the current state of this
    // content instance; for the most extensions, this should be something like the 'path';
    // the extensionManager will use the method internally to identify the content or to update
    // the URL
    getIdentifier: function() {
        return this.path;
    },

    // this function is called when there were updates to the config; you should implement a handler
    // for each config entry (e.g. the background color in our example)
    applyConfig: function() {
        // backgroundColor
        $(this.nodes.content).css('background-color', this._config.backgroundColor);
        return this;
    },

    // the render function is called after the content has been set
    // 'node' is the main container (div) of the instance (and is also available via 'this._node')
    render: function(node) {
        this.nodes.content = $('<div />')
            .addClass('demo-full-body')
            .css('background-color', this._config.backgroundColor)
            .html($.Helpers.strFormat('Demo Content<br />Number: {0}<br />Workspace id: {1}', this._number, this._wid))
            .get(0);
        $(node).append(this.nodes.content);
        return this;
    }
});

// the passed callback in '$(callback)' is called when this script is loaded
$(function() {
    // register the Extension using jQuery Topic plugin
    $.Topic('extman.register').publish(DemoExtension);
});
