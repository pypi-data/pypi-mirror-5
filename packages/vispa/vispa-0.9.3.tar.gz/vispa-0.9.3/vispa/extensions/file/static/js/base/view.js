var FileBaseView = Class.extend({

    init: function(owner) {
        this.owner = owner;
        this.fileContentContainer = null;
    },

    setMainContainer: function() {
        var _this = this;

        var maindiv = $('<div />').addClass("file-maindiv");

        var fileMainTemplate = Vispa.urlHandler.dynamic("/extensions/file/static/html/main.html?" + new Date().getTime());
        $.ajax({
            url: fileMainTemplate,
            type: 'GET',
            async: false,
            success: function(response) {
                maindiv.html(response);
            }
        })

        // console.log(maindiv);

        this.fileContentContainer = $('.file-content', maindiv);

        this.fileContentContainer.on('click', function(e) {
            _this.owner.events.leftClickBkg(e, this.fileContentContainer);
        });
        this.fileContentContainer.bind("contextmenu", function(e) {
            _this.owner.events.rightClickBkg(e, this.fileContentContainer);
        });

        return maindiv;
    },

    // Method needed for all views for appending the data to the views and 
    // for making the items correctly clickable
    setupDataActions: function(node, data /* = data.filelist*/ , owner) {
        var _this = this;
        node.data("data", data);
        node.data("selected", false)
        // get the selection <p>
        var selectp = $(".file-selection-p", node);
        // var selectbox = $('.file-selection-box', selectp)
        var selectbox = $(":checkbox", selectp)
        // selectp.on('click', function(event) {
        //     event.stopPropagation();
        //     // Here this is the <p></p>
        //     selectbox.change(function(event) {
        //         event.stopPropagation();
        //         if (selectbox.is(":checked")) {
        //             owner.selections.addSelection(data.path, node);
        //             node.data().selected = true;
        //         } else {
        //             owner.selections.unselect(data.path);
        //         };
        //     });
        // })

        node.on('click', function(event) {
            if (_this.owner.workflow.selectmode) {
                event.stopPropagation();
                if (selectbox.is(":checked")) {
                    selectbox.removeAttr("checked");
                    owner.selections.unselect(data.path.toString());
                } else {
                    node.data().selected = true;
                    selectbox.attr('checked', true);
                    owner.selections.addSelection(data.path.toString(), node);
                };
            } else {

                if (data.type == "f") {
                    owner.events.dblClickFile(event, data);
                } else {
                    owner.events.dblClickFolder(event, data);
                };
            };
        });
        node.bind("contextmenu", function(event) {
            if (node.data().selected == true) {
                owner.events.rightClickSelection(event, node);
            } else {
                if (data.type == "f") {
                    owner.events.rightClickFile(event, node);
                } else {
                    owner.events.rightClickFolder(event, node);
                };
            };
        });
    },

    setupSymbols: function(node, data /* = data.filelist*/ , width /*as string*/ , heigth /*as string*/ ) {
        var imgUrl = "/extensions/file/static/img/"
        var src = null;
        var availableIcons = ["c", "cpp", "default", "folder", "h", "jpeg", "jpg", "pdf", "png", "pxlio", "py", "root", "txt", "xml", "zip"]
        var type = data.type;
        if (type == "d") {
            src = Vispa.urlHandler.dynamic(imgUrl + "folder.png");
        } else {
            var extension = $.Helpers.strExtension(data.name);
            if (availableIcons.indexOf(extension) > 0) {
                src = Vispa.urlHandler.dynamic(imgUrl + extension + ".png");
            } else {
                src = Vispa.urlHandler.dynamic(imgUrl + "default.png");
            };
        };
        $("img", node).attr("src", src);
        if (width == -1) {
            $("img", node).attr("heigth", heigth);
        } else {
            $("img", node).attr("width", width);
        }
    }


});