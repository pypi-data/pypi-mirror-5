var View = VispaModule.extend({

    init: function(config) {
        this.defaultConfig = {};
        this._super("view", config);

        // attributes
        this.settings = {};
        this.workflow = {};
        this.nodes = {};
    },

    startup: function() {
        this.setupMarkup();
        this.logger.debug("Started");
        return this;
    },

    applyConfig: function() {
        return this;
    },

    getTemplate: function(path) {
        var request = {
            url: Vispa.urlHandler.dynamic("ajax/gettemplate"),
            type: 'POST',
            data: {path: path}
        };
        return $.ajax(request);
    },

    setupMarkup: function() {
        var promise = this.getTemplate("bootstrap/workspace_group.html");
        $.when(promise).then(function(response) {
            var wsGroup = $(".subheader-workspaces").html(response).children().first();
            console.log(wsGroup);
        });
        return this;
    }
});