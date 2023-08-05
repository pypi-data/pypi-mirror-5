var FileBaseActions = Class.extend({
    init: function(owner) {
        this.owner = owner;
        this.pastebool = false;
        this.removebool = false;
        this.entries = {};
    },

    openFolder: function(data) {;
        this.owner.workflow.path = data.path;
        this.owner.updateView();
    },

    openFile: function(data) {
        var ext = $.Helpers.strExtension(data.name);
        console.log(ext);
        var path = data.path;

        var handlers = Vispa.extensionManager.getFileHandlers(ext, true);

        if (handlers.length == 0) {
            alert("Can not open File, because no Extension has been defined.")
        } else {
            handlers[0].callback(path);
        };
    },

    rename: function(data) {
        var _this = this;
        var type = data.type;
        var name = data.name;
        var newName = prompt("Enter a new name", name)
        if (newName == name || newName == null || newName == "") {
            return
        };

        if (type == "d") {
            $.ajax({
                url: this.owner.urlFormatter('ajax/fs/renamefolder'),
                type: 'POST',
                data: {
                    _wid: Vispa.workspaceManager.getWorkspace().id,
                    path: data.path,
                    name: newName
                },
                success: function(response) {
                    if (response.success) {
                        _this.owner.updateView();
                    } else {
                        $.Topic('msg.error').publish(response.msg);
                    }
                }
            });
        } else {
            $.ajax({
                url: this.owner.urlFormatter('ajax/fs/renamefile'),
                type: 'POST',
                data: {
                    _wid: Vispa.workspaceManager.getWorkspace().id,
                    path: data.path,
                    name: newName
                },
                success: function(response) {
                    if (response.success) {
                        _this.owner.updateView();
                    } else {
                        $.Topic('msg.error').publish(response.msg);
                    }
                }
            });
        };
    },

    copy: function(data) {
        this.pastebool = true;
        this.entries = this.owner.selections.entries;
    },

    cut: function(data) {
        this.pastebool = true;
        this.entries = this.owner.selections.entries;
        this.removebool = true;
    },

    paste: function(data) {
        var _this = this;
        var paths = new Array();
        $.each(this.entries, function(path, node) {
            paths.push(path);
        });
        $.ajax({
            url: this.owner.urlFormatter('ajax/fs/paste'),
            type: 'GET',
            data: {
                _wid: Vispa.workspaceManager.getWorkspace().id,
                path: this.owner.workflow.path,
                paths: JSON.stringify(paths),
                cut: this.removebool
            },
            success: function(response) {
                if (response.success) {
                    _this.owner.updateView();
                } else {
                    $.Topic('msg.error').publish(response.msg);
                }
            }
        });
        if (this.removebool) {this.entries = {}};
    },

    remove: function(data) {
        var _this = this;
        this.entries = this.owner.selections.entries;
        console.log("remove");
        console.log(this.entries);
        $.each(this.entries, function(path, node) {
            console.log(path);
            $.ajax({
                url: _this.owner.urlFormatter('ajax/fs/remove'),
                type: 'POST',
                data: {
                    _wid: Vispa.workspaceManager.getWorkspace().id,
                    path: path,
                },
                success: function(response) {
                    if (response.success) {
                        _this.owner.updateView();
                    } else {
                        $.Topic('msg.error').publish(response.msg);
                    }
                }
            });
        });
        this.entries = {}
        },

        download: function(data) {
            console.log("download");
        },

        compress: function(data) {
            var _this = this;

            var newName = prompt("Enter a name for the zip-file", name)
            if (newName == name || newName == null || newName == "") {
                return
            };

            var paths = new Array();
            $.each(this.owner.selections.entries, function(i, entry) {
                paths.push(entry.data.path);
            });

            $.ajax({
                url: this.owner.urlFormatter('ajax/fs/compress'),
                type: 'GET',
                data: {
                    _wid: Vispa.workspaceManager.getWorkspace().id,
                    path: this.owner.workflow.path,
                    paths: JSON.stringify(paths),
                    name: newName
                },
                success: function(response) {
                    if (response.success) {
                        _this.owner.updateView();
                    } else {
                        $.Topic('msg.error').publish(response.msg);
                    }
                }
            });
        },

        info: function(data) {
            console.log("info");
        },

        createFile: function(data) {
            var _this = this;
            var newName = prompt("Enter name for new file:", name)
            if (newName == null || newName == "") {
                return
            };
            $.ajax({
                url: this.owner.urlFormatter('ajax/fs/createfile'),
                type: 'POST',
                data: {
                    _wid: Vispa.workspaceManager.getWorkspace().id,
                    path: _this.owner.workflow.path,
                    name: newName
                },
                success: function(response) {
                    if (response.success) {
                        _this.owner.updateView();
                    } else {
                        $.Topic('msg.error').publish(response.msg);
                    }
                }
            });
        },

        createFolder: function(data) {
            var _this = this;
            var newName = prompt("Enter name for new directory:", name)
            if (newName == null || newName == "") {
                return
            };
            $.ajax({
                url: this.owner.urlFormatter('ajax/fs/createfolder'),
                type: 'POST',
                data: {
                    _wid: Vispa.workspaceManager.getWorkspace().id,
                    path: this.owner.workflow.path,
                    name: newName
                },
                success: function(response) {
                    if (response.success) {
                        _this.owner.updateView();
                    } else {
                        $.Topic('msg.error').publish(response.msg);
                    }
                }
            });
        },

        select: function(data, node) {

        }
    });