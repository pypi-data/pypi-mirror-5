var FileBase = Class.extend({

    init: function(path, urlFormatter) {
        // components
        this.view = new FileBaseView(this);
        // this.ajax = new FileBaseAjaxHandler(this);
        this.events = new FileBaseEvents(this);
        this.actions = new FileBaseActions(this);
        this.selections = new FileBaseSelections(this);
        this.menuitems = new FileBaseMenuItems(this);

        // store the formatter
        this.urlFormatter = urlFormatter || function(path) {
            return path
        };

        // the workflow object may be extended
        this.workflow = {
            path: path,
            parentpath: "",
            currentView: null,
            data: null,
            selectmode: false
        };
    },

    create: function() {
        var mainContainer = this.view.setMainContainer();
        $(document)[0].oncontextmenu = function() {
            return false;
        };

        this.changeView(Symbolview);
        // this.changeView(Tableview);

        return mainContainer;
    },

    changeView: function(viewConstructor) {
        var newView = new viewConstructor(this);

        if (this.currentView != null && newView.type == this.currentView.type) return null;

        this.currentView = newView;

        // add the view to the center pane of the main container
        var viewContainer = this.currentView.render();
        this.updateView();

    },

    updateView: function() {
        var _this = this;
        this.selections.unselectAll();

        $.ajax({
            url: this.urlFormatter('ajax/fs/filelist'),
            type: 'POST',
            data: {
                _wid: Vispa.workspaceManager.getWorkspace().id,
                path: this.workflow.path
            },
            success: function(response) {
                if (response.success) {
                    _this.workflow.data = response.data;
                    _this.currentView.setContent(response.data);
                } else {
                    $.Topic('msg.error').publish(response.msg);
                }
            }
        });

    }
});