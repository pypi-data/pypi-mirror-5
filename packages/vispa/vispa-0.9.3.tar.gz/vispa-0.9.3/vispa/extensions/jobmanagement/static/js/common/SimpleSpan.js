var SimpleSpan = Class.extend({

    /*
     * <th style="background-color: white;"><label
     * for="${extid}-JobDetailedViewTable-jobid">JobID:</label></th> <td><span
     * id="${extid}-JobDetailedViewTable-jobid"></span></td>
     */

    init : function(args) {
        this.label = (args.hasOwnProperty("label") ? label : false);
        this.labeltext = (args.hasOwnProperty("labeltext") ? args.iconlist : "");
        this.rowStyle = (args.hasOwnProperty("rowStyle") ? args.rowStyle : false);
        this.text = (args.hasOwnProperty("text") ? args.iconlist : "");
        this.tooltip = (args.hasOwnProperty("tooltip") ? args.tooltip : "");

        this.guid = (args.hasOwnProperty("guid") ? args.guid : guid());
        this.jid = "#" + this.guid;

        this.identifier = (args.hasOwnProperty("identifier") ? args.identifier : false);
        this.clickCallback = (args.hasOwnProperty("clickCallback") ? args.clickCallback : null);

        console.debug("DEBUG SimpleSpan: Created Span with id '" + this.guid + "'");

        this.span = false;
    },

    initializeSpan : function(append) {
        if (!this.span)
            this.span = this.createSpan();

        if (append) {
            if (append.length == 0)
                console.error("ERROR SimpleSpan: Did not found object where span should be appended to ... parameter is appendTo='" + appendTo + "'");
            else
                $(append).append(this.span);
        } else
            console.error("ERROR SimpleSpan: Did not found object where span should be appended to ... parameter is empty");

        this.postFillProcessing();

        return true;
    },

    postFillProcessing : function() {
        if (this.clickCallback)
            this.connectSpanClick(this.clickCallback);
    },

    createSpan : function() {

        var th = "";
        if (this.label)
            th = "<label for='" + this.guid + "'>" + this.labeltext + "</label>";
        var td = "<span title='" + this.tooltip + "' id='" + this.guid + "'>" + this.text + "</span>";

        if (this.rowStyle) {
            this.span = "";
            this.span += "<th>" + th + "</th>";
            this.span += "<td>" + td + "</td>";
        } else {
            this.span = th + td;
        }

        return this.span;
    },

    connectSpanClick : function(callback) {
        if (this.span) {
            $(this.jid).click({
                identifier : this.identifier
            }, callback);
        }
    }

});