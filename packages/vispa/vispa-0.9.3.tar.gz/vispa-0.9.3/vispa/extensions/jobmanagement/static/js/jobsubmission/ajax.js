var JobSubmissionAjaxHandler = JobAjaxHandler.extend({

    init : function(owner) {
        this._super(owner);
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
        $.extend(obj, this.basicrequest("loadjobsubmissionview", false), this.handlingTemplate(dfd), data);
        return $.ajax(obj);
    },

    /*
     * getAvailableBatchManager : function() { var template = ""; var obj = {
     * handleAs : "text", content : {extid : this.owner._id}, onLoad :
     * function(result) { template = result; } };
     * this.basicRequest("getAvailableBatchManager", obj); return template; },
     */

    getAvailableBatchManager : function(dfd) {
        var obj = {
            dataType : "json"
        };

        var data = {
            "data" : {
                _wid: Vispa.workspaceManager.getWorkspace().id
            }
        };

        $.extend(obj, this.basicrequest("getAvailableBatchManager", true), this.handling(dfd), data);

        return $.ajax(obj);
    },

    getBatchManagerConfiguration : function(batchmanager) {
        var obj = {
        // traditional: true
        // dataType: "json"
        };

        var data = {
            "data" : {
                extid : this.owner.owner._id,
                _wid: Vispa.workspaceManager.getWorkspace().id,
                batchmanager : batchmanager
            }
        };
        $.extend(obj, this.basicrequest("getBatchManagerConfiguration", false), this.handlingTemplate(null), data);
        return $.ajax(obj);
    },

    /*
     * this.getBatchManagerConfiguration : function(batchmanager) { var template =
     * ""; var obj = { handleAs : "text", content : {extid :
     * this.owner.owner._id, batchmanager:batchmanager}, onLoad :
     * function(result) { template = result; } };
     * this.basicRequest("getBatchManagerConfiguration", obj); return template; },
     */

    runJobs : function(joblist, dfd) {
        var obj = {
            traditional : true,
            dataType : "json"
        };

        var data = {
            "data" : {
                _wid: Vispa.workspaceManager.getWorkspace().id,
                joblist : JSON.stringify(joblist)                
            }
        };
        $.extend(obj, this.basicrequest("runJobs", true), this.handling(dfd), data);

        return $.ajax(obj);
    }

});