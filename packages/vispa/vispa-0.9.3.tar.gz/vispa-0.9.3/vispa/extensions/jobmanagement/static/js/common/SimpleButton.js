var SimpleButton = Class.extend({

    init : function(args) {
        this.iconlist = (args.hasOwnProperty("iconlist") ? args.iconlist : []);
        this.classes = (args.hasOwnProperty("classes") ? args.classes : []);
        this.title = (args.hasOwnProperty("title") ? args.title : "");
        this.tooltip = (args.hasOwnProperty("tooltip") ? args.tooltip : "");
        this.guid = (args.hasOwnProperty("guid") ? args.guid : guid());
        this.jid = "#" + this.guid;
        this.identifier = (args.hasOwnProperty("identifier") ? args.identifier : false);
        this.clickCallback = (args.hasOwnProperty("clickCallback") ? args.clickCallback : null);

        console.debug("DEBUG SimpleButton: Created Button with id '" + this.guid + "'");

        this.button = false;
    },

    initializeButton : function(append) {
        var _this = this;

        if (!this.button)
            this.button = this.createButton();

        if (append) {
            if (append.length == 0)
                console.error("ERROR SimpleButton: Did not found object where button should be appended to ... parameter is appendTo='" + appendTo + "'");
            else
                $(append).append(this.button);
        } else
            console.error("ERROR SimpleButton: Did not found object where button should be appended to ... parameter is empty");

        if (this.iconlist.length > 1) {
            $(this.jid).button({
                icons : {
                    primary : this.iconlist[0],
                    secondary : this.iconlist[1]
                }
            });
        } else if (this.iconlist.length == 1) {
            $(this.jid).button({
                icons : {
                    primary : this.iconlist[0]
                }
            });
        } else {
            $(this.jid).button();
        }

        $.each(this.classes, function(index, currentClass) {
            $(_this.jid).addClass(currentClass);
        });

        this.postFillProcessing();

        return true;
    },

    postFillProcessing : function() {
        if (this.clickCallback)
            this.connectButtonClick(this.clickCallback);
    },

    createButton : function() {
        this.button = "<button title='" + this.tooltip + "' id='" + this.guid + "'>" + this.title + "</button>";
        return this.button;
    },

    connectButtonClick : function(callback) {
        if (this.button) {
            $(this.jid).click({
                identifier : this.identifier
            }, callback);
        }
    }
});