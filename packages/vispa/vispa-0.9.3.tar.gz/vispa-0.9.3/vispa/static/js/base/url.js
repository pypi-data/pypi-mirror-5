var UrlHandler = Class.extend({

    init: function(config) {
        // attributes
        this.settings = {};
        this.defaultConfig = {
            staticBase: {
                type: 'string',
                value: '/'
            },
            dynamicBase: {
                type: 'string',
                value: '/'
            }
        };
        this.workflow = {
            urlParametersHandled: false,
            wrappedCallback: null
        };
        this.config = $.Helpers.createConfig(config, this.defaultConfig);
    },

    startup: function() {
        return this;
    },

    dynamic: function() {
        var args = $.makeArray(arguments);
        var url = $.Helpers.strBounds(this.config.dynamicBase, null, false);
        $.each(args, function(i, arg) {
            url += $.Helpers.strBounds(arg, true, i == args.length-1 ? null : false);
        });
        return encodeURI(url);
    },

    static: function() {
        var args = $.makeArray(arguments);
        var url = $.Helpers.strBounds(this.config.staticBase, null, false);
        $.each(args, function(i, arg) {
            url += $.Helpers.strBounds(arg, true, i == args.length-1 ? null : false);
        });
        return url;
    },

    wrappHistory: function(callback) {
        // store it
        this.workflow.wrappedCallback = callback;
        // use callback as a handler for the history plugin
        $.History(callback);
        return this;
    }
});