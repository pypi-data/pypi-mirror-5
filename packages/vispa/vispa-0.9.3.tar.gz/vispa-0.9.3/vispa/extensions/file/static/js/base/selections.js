var FileBaseSelections = Class.extend({
    init: function(owner) {
        this.owner = owner;
        // this.entries = new Array();
        this.entries = {};
        // var numberOfEntries = 0;
    },

    unselectAll: function() {
        var selectionBoxes = $('.file-selection-box');
        $.each(selectionBoxes,function(index, node) {$(".file-selection-checkbox",node).removeAttr('checked');});
        this.entries = {};
    }, 

    unselect: function  (path, node) {
        delete this.entries[path];
    },

    addSelection: function(path, node)
    {
        this.entries[path] = node;
    }
});