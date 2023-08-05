var FileExtension = ExtensionBase.extend({

    init: function() {
        this._super();
        var _this = this;

        this.name = "file";

        this.factories = {
            browser: new FileBrowserFactory(),
            selector: new FileSelectorFactory()
        };
    }
});


var FileBrowserFactory = ExtensionFactoryFull.extend({

    init: function() {
        this._super();
        var _this = this;

        this.defaultConfig = {
            droppedMenuEntries: {
                type: "list",
                hidden: true,
                value: ["Tableview", "Symbolview", "Toggle SelectionMode", "Refresh", "Folder up"]
            }
        };

        this.name = "FileBrowser";
        this.constructor = FileBrowserContent;

        this.menuEntries = [{
            label: "open FileBrowser",
            icon: "ui-icon-folder-open",
            callback: function() {
                _this._create("~/");
            }
        }];

        this.fileHandlers = {
            "/": {
                priority: 1,
                callback: function(path) {
                    _this._create(path);
                }
            }
        };
    }
});

var FileBrowserContent = ExtensionContentFull.extend({

    init: function(config, path) {
        var _this = this;
        this._super(config);

        var viewSubMenu = [{
            label: "Tableview",
            icon: "ui-icon-calculator",
            callback: function() {
                _this.browser.changeView(Tableview);
            }
        }, {
            label: "Symbolview",
            icon: "ui-icon-image",
            callback: function() {
                _this.browser.changeView(Symbolview);
            }
        }];

        this.menuEntries = [{
            label: "Folder up",
            icon: "ui-icon-arrowreturnthick-1-w",
            callback: function() {
                _this.browser.workflow.path = _this.browser.workflow.parentpath;
                _this.browser.updateView();
                Vispa.pathBar.setValue(_this.browser.workflow.path);
            }
        }, {
            label: "Set View",
            children: {
                id: null,
                items: viewSubMenu
            }
        }, {
            label: "Toggle SelectionMode",
            icon: "ui-icon-star",
            callback: function() {
                var selectors = $(".file-selection-p");
                if (selectors.css("visibility") == "visible") {
                    selectors.css("visibility", "hidden")
                    _this.browser.workflow.selectmode = false;
                } else {
                    selectors.css("visibility", "visible");
                    _this.browser.workflow.selectmode = true;
                };
            }
        }, {
            label: "Refresh",
            icon: "ui-icon-refresh",
            callback: function() {
                _this.browser.updateView();
            }
        }];

        this.browser = new FileBrowser(this, path);
    },

    getIdentifier: function() {
        return this.browser.workflow.path;
    },

    render: function(node) {
        $(node).append(this.browser.getContent());
        return this;
    },

    getTitle: function() {
        return this.browser.workflow.path;
    }
});


var FileSelectorFactory = ExtensionFactoryFull.extend({

    init: function() {
        var _this = this;
        this._super();

        this.defaultConfig = {
            droppedMenuEntries: {
                type: "list",
                hidden: true,
                value: ["Tableview", "Symbolview", "Toggle SelectionMode", "Refresh", "Folder up"]
            }
        };
        this.name = "FileSelector";
        this.constructor = FileSelectorContent;

        $.Topic("ext.file.selector").subscribe(function() {
            _this._create.apply(_this, arguments);
        });
    }
});

var FileSelectorContent = ExtensionContentFull.extend({

    init: function(config, data) {
        var _this = this;
        this._super(config);

        this.workflow = {
            initialData: data
        };

        var viewSubMenu = [{
            label: "Tableview",
            icon: "ui-icon-calculator",
            callback: function() {
                _this.selector.changeView(Tableview);
            }
        }, {
            label: "Symbolview",
            icon: "ui-icon-image",
            callback: function() {
                _this.selector.changeView(Symbolview);
            }
        }];

        this.menuEntries = [{
            label: "Folder up",
            icon: "ui-icon-arrowreturnthick-1-w",
            callback: function() {
                _this.selector.workflow.path = _this.selector.workflow.parentpath;
                _this.selector.updateView();
                Vispa.pathBar.setValue(_this.selector.workflow.path);
            }
        }, {
            label: "Set View",
            children: {
                id: null,
                items: viewSubMenu
            }
        }, {
            label: "Toggle SelectionMode",
            icon: "ui-icon-star",
            callback: function() {
                var selectors = $(".file-selection-p");
                if (selectors.css("visibility") == "visible") {
                    selectors.css("visibility", "hidden")
                    _this.selector.workflow.selectmode = false;
                } else {
                    selectors.css("visibility", "visible");
                    _this.selector.workflow.selectmode = true;
                };
            }
        }, {
            label: "Refresh",
            icon: "ui-icon-refresh",
            callback: function() {
                _this.selector.updateView();
            }
        }];

        this.selector = new FileSelector(this, this.workflow.initialData);
    },

    render: function(node) {
        $(node).append(this.selector.getContent());
        // $(node).append(this.workflow.initialData.path);
        return this;
    },

    getTitle: function() {
        return this._factory.name;
    }
});


$(function() {
    // register the Extension
    $.Topic("extman.register").publish(FileExtension);
});