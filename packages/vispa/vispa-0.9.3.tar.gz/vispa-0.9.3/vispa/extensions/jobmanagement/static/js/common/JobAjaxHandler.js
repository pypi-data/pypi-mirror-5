var JobAjaxHandler = Class.extend({

    init : function(owner) {
        // store the owner
        this.owner = owner;
    },

    readFile : function(path, dfd) {
        var obj = {
            dataType : "json"
        };

        var data = {
            "data" : {
                extid : this.owner.owner._id,
                _wid: Vispa.workspaceManager.getWorkspace().id,
                path : path
            }
        };

        $.extend(obj, this.basicrequest("readfile", true), this.handling(dfd), data);

        return $.ajax(obj);
    },

    saveFile : function(path, content, dfd) {
        var obj = {
            dataType : "json",
        };

        var data = {
            "data" : {
                extid : this.owner.owner._id,
                _wid: Vispa.workspaceManager.getWorkspace().id,
                path : path,
                content : JSON.stringify(content)
            }
        };

        $.extend(obj, this.basicrequest("savefile", true), data);

        return $.ajax(obj);
    },

    basicrequest : function(controllermethod, async) {
        var _this = this;

        // default is true
        var basicrequest = {
            type : 'POST',
            url : Vispa.extensionManager.getPath(this.owner.owner, controllermethod),
            // url:
            // Vispa.extensionManager.getAjaxPath(_this.owner.owner._config._ext.name,
            // controllermethod),
            async : (typeof async == 'undefined' ? true : async)
        };
        return basicrequest;
    },

    handling : function(dfd) {
        var _this = this;
        var handling = {
            success : function(result, textStatus, jqXHR) {
                if (!result.success) {
                    // dojo.publish("createTabError",
                    // [_this.owner.owner._config._ext.name,
                    // _this.owner.owner._config._key, _this.owner.owner._id,
                    // result.msg]);
                    $.Topic('msg.error').publish(result.msg, function() {
                        // $('#register-name').focus();
                    });
                } else {
                    if (dfd)
                        dfd.resolve(result);
                }
            },
            error : function(jqXHR, textStatus, errorThrown) {
                // dojo.publish("createTabError",
                // [_this.owner.owner._config._ext.name,
                // _this.owner.owner._config._key, _this.owner.owner._id,
                // textStatus]);

                $.Topic('msg.error').publish(textStatus, function() {
                    // $('#register-name').focus();
                });
            }
        };

        return handling;
    },

    handlingTemplate : function(dfd) {
        var _this = this;

        var handling = {
            success : function(result, textStatus, jqXHR) {
                if (dfd)
                    dfd.resolve(result);
            },
            error : function(jqXHR, textStatus, errorThrown) {
                // dojo.publish("createTabError",
                // [_this.owner.owner._config._ext.name,
                // _this.owner.owner._config._key, _this.owner.owner._id,
                // textStatus]);

                $.Topic('msg.error').publish(textStatus, function() {
                    // $('#register-name').focus();
                });
            }
        };

        return handling;
    }
});
