var FileSelectorActions = FileBaseActions.extend({

    init: function(owner) {
        this._super(owner);
        this.owner = owner;
    },

    // This is not really an open File method but a select file method
    openFile: function(data) {
        this.owner.workflow.selection.push(data.path)
        if (this.owner.workflow.multimode) {
            this.owner.workflow.callback(this.owner.workflow.selection);
        } else {
            this.owner.workflow.callback(this.owner.workflow.selection[0]);
        };
        this.owner.instance._close();
    },
});