var FileSelectorView = FileBaseView.extend({

    init: function(owner) {
        this._super(owner);
    },

    setMainContainer: function() {
        var maindiv = this._super();
        
        var bottomdiv = $('<div />');
        this.addButtons(bottomdiv);
        maindiv.append(bottomdiv);

        return maindiv;
    },

    addButtons: function(node) {
        var _this = this;

        // The select button
        var select = $('<div/>', {
            text: "Select",
            title: "Select",
            alt: "Select"
        })
            .button()
            .click(function(event) {
            event.stopPropagation();
            $.each(_this.owner.selections.entries, function(path, node) {
                _this.owner.workflow.selection.push(path);
            });
            if (_this.owner.workflow.selection.length != 0) {
                if (_this.owner.workflow.multimode) {
                    _this.owner.workflow.callback(_this.owner.workflow.selection);
                } else {
                    _this.owner.workflow.callback(_this.owner.workflow.selection[0]);
                };
                _this.owner.instance._close();
            };
        })
            .addClass("file-selector-button");

        // The close button
        var close = $('<div/>', {
            text: "Close",
            title: "Close",
            alt: "Close"
        })
            .button()
            .click(function(event) {
            event.stopPropagation();
            _this.owner.instance._close();
        })
            .addClass("file-selector-button");

        // Append the buttons to the node
        node.append(select);
        node.append(close);
    }
});
