var Tableview = Class.extend({
    init: function(owner) {
        this.owner = owner;
        this.mainContainer = null;
        this.type = "Tableview"
        this.template = null;
    },

    render: function() {
        var _this = this;
        var table = Vispa.urlHandler.dynamic("/extensions/file/static/html/table.html?" + new Date().getTime());
        $.ajax({
            url: table,
            type: 'GET',
            async: false,
            success: function(response) {
                _this.owner.view.fileContentContainer.html(response);
                _this.template = response;
            }
        });
    },

    setContent: function(data) {
        var _this = this;
        this.data = data;

        // Get the container
        this.fileContentContainer = _this.owner.view.fileContentContainer;
        this.owner.view.fileContentContainer.empty();
        this.owner.view.fileContentContainer.html(this.template);

        // Set the right path
        this.owner.workflow.parentpath = data.parentpath;

        // render the content
        $(".files-table", this.fileContentContainer).render(data.filelist);

        // Get the objects and append the data to them
        $(".files-table", this.fileContentContainer).children().each(function(i, child) {
            _this.owner.view.setupDataActions($(child), data.filelist[i], _this.owner);
            _this.owner.view.setupSymbols($(child), data.filelist[i], "20px", -1);
        });

        // Make the table sortable with a certain theme
        $(".tablesorter", _this.owner.view.fileContentContainer).tablesorter(
        /*{
            theme: "blue"
        }*/
        {
            theme: 'jui', // theme "jui" and "bootstrap" override the uitheme widget option in v2.7+
            headerTemplate: '{content} {icon}', // needed to add icon for jui theme
            sortList: [
                [2, 0],
                [0, 0]
            ],
            widgets: ['uitheme'],
        });

        var selectors = $(".file-selection-p");
        if (this.owner.workflow.selectmode) {
            selectors.css("visibility", "visible");
        };

    }

});