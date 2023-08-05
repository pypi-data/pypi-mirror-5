var FileBaseMenuItems = Class.extend({
    init: function(owner) {
        this.owner = owner;

    },

    openFolder: function(data) {
        var _this = this;
        var item = {
            label: 'Open',
            alt: 'Open',
            icon: 'ui-icon-folder-open',
            callback: function() {
                _this.owner.actions.openFolder(data);
            }
        };
        return item;
    },

    openFile: function(data) {
        var _this = this;
        return {
            label: 'Open',
            alt: 'Open',
            icon: 'ui-icon-document-b',
            callback: function() {
                _this.owner.actions.openFile(data);
            }
        };
    },

    openWith: function(data) {
        var _this = this;
        var ext = $.Helpers.strExtension(data.name);

        // get all the handlers for putting them into the submenu (children)
        var children = [];
        var handlers = Vispa.extensionManager.getFileHandlers(ext, true);
        var name = null;
        $.each(handlers, function(i, handler) {
            name = $.Helpers.strFormat(handler.owner.name);
            children.push({
                label: name,
                alt: name,
                icon: "",
                callback: function() {
                    // This is not following the usual concept
                    // But for this single line there is no sense in 
                    // implementing a function actions.js
                    handler.callback(data.path);

                }
            });
        });

        return {
            label: 'Open ...',
            alt: 'Open ...',
            icon: '',
            children: {
                id: null,
                items: children
            }
        };
    },

    rename: function(data) {
        var _this = this;
        return {
            label: 'Rename',
            alt: 'Rename',
            icon: 'ui-icon-pencil',
            callback: function() {
                _this.owner.actions.rename(data);
            }
        };
    },

    copy: function(data) {
        var _this = this;
        return {
            label: 'Copy',
            alt: 'Copy',
            icon: 'ui-icon-copy',
            callback: function() {
                _this.owner.actions.copy(data);
            }
        };
    },

    cut: function(data) {
        var _this = this;
        return {
            label: 'Cut',
            alt: 'Cut',
            icon: 'ui-icon-scissors',
            callback: function() {
                _this.owner.actions.cut();
            }
        };
    },

    paste: function(data, active) {
        active = active === undefined ? false : active;
        var _this = this;
        return {
            label: 'Paste',
            alt: 'Paste',
            icon: 'ui-icon-eject',
            disabled: active,
            callback: function() {
                _this.owner.actions.paste(data);
            }
        };
    },

    remove: function(data) {
        var _this = this;
        return {
            label: 'Remove',
            alt: 'Remove',
            icon: 'ui-icon-trash',
            callback: function() {
                _this.owner.actions.remove(data);
            }
        };
    },

    download: function(data) {
        var _this = this;
        return {
            label: 'Download',
            alt: 'Download',
            icon: 'ui-icon-arrowthick-1-s',
            callback: function() {
                _this.owner.actions.download(data);
            }
        };
    },

    compress: function(data) {
        var _this = this;
        return {
            label: 'Compress...',
            alt: 'Compress...',
            icon: 'ui-icon-suitcase',
            callback: function() {
                _this.owner.actions.compress(data);
            }
        };
    },

    info: function(data) {
        var _this = this;
        return {
            label: 'Info',
            alt: 'Info',
            icon: 'ui-icon-info',
            callback: function() {
                _this.owner.actions.info(data);
            }
        };
    },

    createFile: function(data) {
        var _this = this;
        return {
            label: 'Create File',
            alt: 'Create File',
            icon: 'ui-icon-document',
            callback: function() {
                _this.owner.actions.createFile(data);
            }
        };
    },

    createFolder: function(data) {
        var _this = this;
        return {
            label: 'Create Folder',
            alt: 'Create Folder',
            icon: 'ui-icon-folder-collapsed',
            callback: function() {
                _this.owner.actions.createFolder(data);
            }
        };
    }
});