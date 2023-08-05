var JobDesignerAjaxHandler = JobAjaxHandler.extend({

    init : function(owner) {
        this._super(owner);
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

    resetCommandLineDesigner : function(dfd) {
        var obj = {
            dataType : "json"
        };

        var data = {
            "data" : {
                extid : this.owner.owner._id,
                _wid: Vispa.workspaceManager.getWorkspace().id
            }
        };

        $.extend(obj, this.basicrequest("resetCommandLineDesigner", true), this.handling(dfd), data);

        return $.ajax(obj);
    },

    resetCommandLineDesigner : function(dfd) {
        var obj = {
            dataType : "json"
        };

        var data = {
            "data" : {
                extid : this.owner.owner._id,
                _wid: Vispa.workspaceManager.getWorkspace().id
            }
        };

        $.extend(obj, this.basicrequest("resetCommandLineDesigner", true), this.handling(dfd), data);

        return $.ajax(obj);
    },

    getTemplate : function(dfd) {
        var obj = {
        // traditional: true
        // dataType: "json"
        };

        var data = {
            "data" : {
                extid : this.owner.owner._id,
                _wid: Vispa.workspaceManager.getWorkspace().id
            }
        };
        $.extend(obj, this.basicrequest("loadjobdesignerview", false), this.handlingTemplate(dfd), data);
        return $.ajax(obj);
    },

    getParameterRange : function(script, dfd) {
        var obj = {
            dataType : "json"
        };

        var data = {
            "data" : {
                extid : this.owner.owner._id,
                _wid: Vispa.workspaceManager.getWorkspace().id,
                script : script
            }
        };

        $.extend(obj, this.basicrequest("getparameterrange", true), this.handling(dfd), data);

        return $.ajax(obj);
    },
    

    getStatus : function(script, dfd) {
        var obj = {
            dataType : "json"
        };

        var data = {
            "data" : {
                extid : this.owner.owner._id,
                _wid: Vispa.workspaceManager.getWorkspace().id
            }
        };

        $.extend(obj, this.basicrequest("getstatus", true), this.handling(dfd), data);

        return $.ajax(obj);
    },

    setJobDesignerCommand : function(command, dfd) {
        var obj = {
            dataType : "json"
        };

        var data = {
            "data" : {
                extid : this.owner.owner._id,
                _wid: Vispa.workspaceManager.getWorkspace().id,
                command : command
            }
        };

        $.extend(obj, this.basicrequest("setjobdesignercommand", false), this.handling(dfd), data);

        return $.ajax(obj);
    },

    getJobDesignerCommand : function(dfd) {
        var obj = {
            dataType : "json"
        };

        var data = {
            "data" : {
                extid : this.owner.owner._id,
                _wid: Vispa.workspaceManager.getWorkspace().id
            }
        };

        $.extend(obj, this.basicrequest("getjobdesignercommand", true), this.handling(dfd), data);

        return $.ajax(obj);
    },

    addParameterRange : function(name, active, values, script, dfd) {
        var obj = {
            dataType : "json",
            traditional : true
        };

        var data = {
            "data" : {
                extid : this.owner.owner._id,
                _wid: Vispa.workspaceManager.getWorkspace().id,
                name : name,
                active : active,
                values : values,
                script : script
            }
        };

        $.extend(obj, this.basicrequest("addparameterrange", true), this.handling(dfd), data);

        return $.ajax(obj);
    },

    getCommandLines : function(dfd) {
        var obj = {
            dataType : "json"
        };

        var data = {
            "data" : {
                extid : this.owner.owner._id,
                _wid: Vispa.workspaceManager.getWorkspace().id
            }
        };

        $.extend(obj, this.basicrequest("getcommandlines", true), this.handling(dfd), data);

        return $.ajax(obj);
    },

    getListOfOptions : function(dfd) {
        var obj = {
            dataType : "json"
        };

        var data = {
            "data" : {
                extid : this.owner.owner._id,
                _wid: Vispa.workspaceManager.getWorkspace().id
            }
        };

        $.extend(obj, this.basicrequest("getlistofoptions", true), this.handling(dfd), data);

        return $.ajax(obj);
    },

    getListOfParameterRanges : function(dfd) {
        var obj = {
            dataType : "json"
        };

        var data = {
            "data" : {
                extid : this.owner.owner._id,
                _wid: Vispa.workspaceManager.getWorkspace().id
            }
        };

        $.extend(obj, this.basicrequest("getlistofparameterranges", true), this.handling(dfd), data);

        return $.ajax(obj);
    },

    getListOfOptionDecorators : function(dfd, async) {

        var obj = {
            dataType : "json"
        };

        var data = {
            "data" : {
                extid : this.owner.owner._id,
                _wid: Vispa.workspaceManager.getWorkspace().id
            }
        };

        $.extend(obj, this.basicrequest("getlistofoptiondecorators", ((typeof async) == "undefined" ? true : async)), this.handling(dfd), data);

        return $.ajax(obj);
    },

    addOptionDecorator : function(name, script, dfd) {
        var obj = {
            dataType : "json"
        };

        var data = {
            "data" : {
                extid : this.owner.owner._id,
                _wid: Vispa.workspaceManager.getWorkspace().id,
                name : name,
                script : script
            }
        };

        $.extend(obj, this.basicrequest("addoptiondecorator", true), this.handling(dfd), data);

        return $.ajax(obj);
    },

    addOptionList : function(optionList, dfd) {
        var obj = {
            dataType : "json",
            traditional : "true"
        };

        var data = {
            "data" : {
                extid : this.owner.owner._id,
                _wid: Vispa.workspaceManager.getWorkspace().id,
                optionList : JSON.stringify(optionList)
            }
        };

        $.extend(obj, this.basicrequest("addoptionlist", true), this.handling(dfd), data);

        return $.ajax(obj);
    },

    addOption : function(name, optionString, active, value, group, decorator, dfd) {
        var obj = {
            dataType : "json"
        };

        var data = {
            "data" : {
                extid : this.owner.owner._id,
                _wid: Vispa.workspaceManager.getWorkspace().id,
                name : name,
                optionString : optionString,
                active : active,
                value : value,
                group : group,
                decorator : "default"
            }
        };

        $.extend(obj, this.basicrequest("addoption", true), this.handling(dfd), data);

        return $.ajax(obj);
    },

    modifyOption : function(newobj, dfd) {
        var obj = {
            dataType : "json",
            traditional : "true"
        };

        var data = {
            "data" : {
                extid : this.owner.owner._id,
                _wid: Vispa.workspaceManager.getWorkspace().id,
                name : newobj.name,
                newValues : JSON.stringify(newobj.values)
            }
        };

        $.extend(obj, this.basicrequest("modifyoption", true), this.handling(dfd), data);

        return $.ajax(obj);
    },

    loadJobFile : function(path, dfd) {
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

        $.extend(obj, this.basicrequest("loadjobfile", true), this.handling(dfd), data);

        return $.ajax(obj);
    },

    saveJobFile : function(path, dfd) {
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

        $.extend(obj, this.basicrequest("saveas", true), this.handling(dfd), data);

        return $.ajax(obj);
    },

    modifyParameterRange : function(newobj, dfd) {
        var obj = {
            dataType : "json",
            traditional : "true"
        };

        var data = {
            "data" : {
                extid : this.owner.owner._id,
                _wid: Vispa.workspaceManager.getWorkspace().id,
                name : newobj.name,
                newValues : JSON.stringify(newobj.values)
            }
        };

        $.extend(obj, this.basicrequest("modifyparameterrange", true), this.handling(dfd), data);

        return $.ajax(obj);
    },

    modifyOptionDecorator : function(newobj, dfd) {
        var obj = {
            dataType : "json",
            traditional : "true"
        };

        var data = {
            "data" : {
                extid : this.owner.owner._id,
                _wid: Vispa.workspaceManager.getWorkspace().id,
                name : newobj.name,
                newValues : JSON.stringify(newobj.values)
            }
        };

        $.extend(obj, this.basicrequest("modifyoptiondecorator", true), this.handling(dfd), data);

        return $.ajax(obj);
    },

    removeParameterRanges : function(parameterrangeslist, dfd) {
        var obj = {
            dataType : "json",
            traditional : "true"
        };

        var data = {
            "data" : {
                extid : this.owner.owner._id,
                _wid: Vispa.workspaceManager.getWorkspace().id,
                parameterrangeslist : JSON.stringify(parameterrangeslist)
            }
        };

        $.extend(obj, this.basicrequest("removeparameterranges", true), this.handling(dfd), data);

        return $.ajax(obj);
    },

    removeOptions : function(optionslist, dfd) {
        var obj = {
            dataType : "json",
            traditional : "true"
        };

        var data = {
            "data" : {
                extid : this.owner.owner._id,
                _wid: Vispa.workspaceManager.getWorkspace().id,
                optionslist : JSON.stringify(optionslist)
            }
        };

        $.extend(obj, this.basicrequest("removeoptions", true), this.handling(dfd), data);

        return $.ajax(obj);
    },

    removeOptionDecorators : function(decoratorslist, dfd) {
        var obj = {
            dataType : "json",
            traditional : "true"
        };

        var data = {
            "data" : {
                extid : this.owner.owner._id,
                _wid: Vispa.workspaceManager.getWorkspace().id,
                decoratorslist : JSON.stringify(decoratorslist)
            }
        };

        $.extend(obj, this.basicrequest("removeoptiondecorators", true), this.handling(dfd), data);

        return $.ajax(obj);
    }
});
