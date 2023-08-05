var FileBaseEvents = Class.extend({
    init: function(owner) {
        this.owner = owner;
        this.menu = null;
    },

    dblClickFolder: function(event, data) {
        event.stopPropagation();
        event.preventDefault();
        this.owner.actions.openFolder(data);
    },

    rightClickFolder: function(event, node) {
        var _this = this;
        event.stopPropagation();
        event.preventDefault();
        var data = node.data().data;
        this.owner.selections.unselectAll();
        this.owner.selections.addSelection(data.path, node);
        var items = [_this.owner.menuitems.openFolder(data),
        _this.owner.menuitems.rename(data),
        _this.owner.menuitems.copy(data),
        _this.owner.menuitems.cut(data),
        _this.owner.menuitems.remove(data),
        _this.owner.menuitems.compress(data),
        _this.owner.menuitems.info(data)];
        var openCallback = Vispa.view.menuHandler.create("rightClickBkg", $('body'), items, {}, false, $('body'));
        var offset = 2;
        var position = {
            at: $.Helpers.strFormat('left+{0} top+{1}', event.pageX + offset, event.pageY + offset),
            my: 'left top',
            of: $('body')
        };
        openCallback(position);
    },

    dblClickFile: function(event, data) {
        event.stopPropagation();
        event.preventDefault();
        this.owner.actions.openFile(data);
    },

    rightClickFile: function(event, node) {
        var _this = this;
        event.stopPropagation();
        event.preventDefault();
        var data = node.data().data;
        this.owner.selections.unselectAll();
        this.owner.selections.addSelection(data.path, node);
        var items = [_this.owner.menuitems.openFile(data),
        _this.owner.menuitems.openWith(data),
        _this.owner.menuitems.rename(data),
        _this.owner.menuitems.copy(data),
        _this.owner.menuitems.cut(data),
        _this.owner.menuitems.remove(data),
        _this.owner.menuitems.download(data),
        _this.owner.menuitems.compress(data),
        _this.owner.menuitems.info(data)];
        var openCallback = Vispa.view.menuHandler.create("rightClickBkg", $('body'), items, {}, false, $('body'));
        var offset = 2;
        var position = {
            at: $.Helpers.strFormat('left+{0} top+{1}', event.pageX + offset, event.pageY + offset),
            my: 'left top',
            of: $('body')
        };
        openCallback(position);
    },

    clickBkg: function(event, data) {
        var _this = this;
        event.stopPropagation();
        event.preventDefault();

        var eventtype = event.which
        if (eventtype == 1) {
            _this.leftClickBkg(event, data);
        } else {
            _this.rightClickBkg(event, data);
        };
        this.owner.selections.unselectAll()
    },


    leftClickBkg: function(event, data) {
        event.stopPropagation();
        event.preventDefault();
        this.owner.selections.unselectAll();
    },

    rightClickBkg: function(event, data) {
        var _this = this;
        event.stopPropagation();
        event.preventDefault();

        var items = [_this.owner.menuitems.createFile(data),
        _this.owner.menuitems.createFolder(data),
        _this.owner.menuitems.paste(data, !this.owner.actions.pastebool),
        _this.owner.menuitems.info(data)];

        var openCallback = Vispa.view.menuHandler.create("rightClickBkg", $('body'), items, {}, false, $('body'));
        var offset = 2;
        var position = {
            at: $.Helpers.strFormat('left+{0} top+{1}', event.pageX + offset, event.pageY + offset),
            my: 'left top',
            of: $('body')
        };
        openCallback(position);
    },

    rightClickSelection: function(event, data) {
        var _this = this;
        event.stopPropagation();
        event.preventDefault();

        var items = [_this.owner.menuitems.copy(data),
        _this.owner.menuitems.cut(data),
        _this.owner.menuitems.remove(data),
        _this.owner.menuitems.compress(data),
        _this.owner.menuitems.info(data)];

        var openCallback = Vispa.view.menuHandler.create("rightClickBkg", $('body'), items, {}, false, $('body'));
        var offset = 2;
        var position = {
            at: $.Helpers.strFormat('left+{0} top+{1}', event.pageX + offset, event.pageY + offset),
            my: 'left top',
            of: $('body')
        };
        openCallback(position);
    }



});