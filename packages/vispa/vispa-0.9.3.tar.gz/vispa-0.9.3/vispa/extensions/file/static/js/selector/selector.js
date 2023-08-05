// The fileselector will be available by publishing to the Topic:
// 
// function test(a) {console.log(a);};
// $.Topic("ext.file.selector").publish({path: "/", multimode: true, callback: test})

var FileSelector = FileBase.extend({

    init: function(instance, obj) {
        // get the path
        var path = obj.path === undefined ? "~" : obj.path;

        // Define a default callback if no callback is defined
        var defCallback = function() {
            alert("No callback")
        };
        var callback = obj.callback === undefined ? defCallback : obj.callback;

        var multimode = obj.multimode === undefined ? true : obj.multimode;


        // use urlHandler.dynamic as urlFormatter
        var formatter = function(path) {
            return Vispa.urlHandler.dynamic(path);
        }

        this._super(path, formatter);

        this.instance = instance;
        this.view = new FileSelectorView(this);
        this.actions = new FileSelectorActions(this);

        var selection = new Array();
        $.extend(true, this.workflow, {
            callback: callback, 
            multimode: multimode,
            selection: selection
        })

        this.workflow.selectmode = true;
    },

    getContent: function() {
        var content = this.create();
        return content;
    }

})