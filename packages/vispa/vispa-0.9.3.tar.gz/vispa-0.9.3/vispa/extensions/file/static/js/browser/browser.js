var FileBrowser = FileBase.extend({

    init: function(instance, path) {
        // use urlHandler.dynamic as urlFormatter
        var formatter = function(_path) {
            return Vispa.urlHandler.dynamic(_path);
        }
        this._super(path, formatter);
        this.instance = instance;

        this.view = new FileBrowserView(this);
        this.actions = new FileBrowserActions(this);
    },

    getContent: function() {
        var content = this.create();
        return content;
    },

    updateView: function() {
        Vispa.extensionManager.updateUrl(this.instance);
        this._super();
    }
});