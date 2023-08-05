var Symbolview = Class.extend({
    init: function(owner) {
        this.owner = owner;
        this.fileContentContainer = null;
        this.type = "Symbolview"
        this.template = null;
    },

    render: function() {
        var _this = this;
        var symbol = Vispa.urlHandler.dynamic("/extensions/file/static/html/symbol.html?" + new Date().getTime());
        $.ajax({
            url: symbol,
            type: 'GET',
            async: false,
            success: function(response) {
                _this.owner.view.fileContentContainer.html(response);
                _this.template = response;
            }
        })
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
        $(".file-view-symbol", this.fileContentContainer).render(data.filelist);

        // Get the objects and append the data to them
        $(".file-view-symbol", this.fileContentContainer).children().each(function(i, child) {
            _this.owner.view.setupDataActions($(child), data.filelist[i], _this.owner);
            _this.owner.view.setupSymbols($(child), data.filelist[i], -1, "30%");

        });

        $(".file-view-symbol", this.fileContentContainer).isotope({
            itemSelector: ".symbol-item",
            // layoutMode: 'fitRows',
            layoutMode: 'cellsByRow',
            getSortData: {
                name: function($elem) {
                    return $elem.find('.file-view-symbol-name').text();
                }, 

                type: function ($elem) {
                    return $elem.data("data").type;
                }
            },
            sortBy: 'type, name',
            sortAscending: true
        })/*.isotope('reLayout')*/;

        var selectors = $(".file-selection-p");
        if (this.owner.workflow.selectmode) {
            selectors.css("visibility", "visible");
        };
    }
});