var Vispa = Class.extend({

    init: function(config, extensionConfig, workspaceData) {
        // register a logger
        this.logger = $.Logger("Vispa");

        // attributes
        this.defaultConfig = {
            urlHandler: {},
            view: {}
        };
        this.config = $.extend(true, {}, this.defaultConfig, config);
        this.settings = {};
        this.workflow = {};

        // members
        this.view = new View(this.config.view);
        this.urlHandler = new UrlHandler(this.config.urlHandler);
    },

    startup: function() {
        var _this = this;
        this.logger.debug("Started");

        // setup all components
        this.urlHandler.startup();
        this.view.startup();

        // wrapp the history when everything is done and call it
        this.urlHandler.wrappHistory(function() {
            _this.handleUrlParameters.apply(_this, arguments);
        });

        $.Shortcuts("global").enable();
        this.setupTopics();

        return this;
    },

    applyConfig: function() {
        // urlHandler => static
        // view
        this.view.applyConfig();
        return this;
    },

    logout: function() {
        $.Helpers.redirect(this.urlHandler.dynamic("/logout"));
        return this;
    },

    handleUrlParameters: function(params) {
        return this;
    },

    useSlimScroll: function() {
        return false;
    },

    updateTitle: function(title) {
        $("title").html(title);
        return this;
    },

    setupTopics: function() {
        return this;
    }
});


var VispaModule = Class.extend({

    init: function(name, config) {
        this.name = name;
        this.defaultConfig = this.defaultConfig || {};
        this.config = $.Helpers.createConfig(config, this.defaultConfig);
        this.logger = $.Logger($.Helpers.strCapitalize(name));
    },

    startup: function() {
        return this;
    },

    applyConfig: function() {
        return this;
    }
});