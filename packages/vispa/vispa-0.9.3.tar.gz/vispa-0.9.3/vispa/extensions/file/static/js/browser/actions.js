var FileBrowserActions = FileBaseActions.extend({

    init: function(owner) {
        this._super(owner);
        this.owner = owner;
    },

    openFolder: function(data) {
        this.owner.workflow.path = data.path;
        this.owner.updateView();
        Vispa.pathBar.setValue(data.path);
    }
});