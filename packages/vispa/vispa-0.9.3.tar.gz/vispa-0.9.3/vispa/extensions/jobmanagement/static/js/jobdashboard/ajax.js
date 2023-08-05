var JobDashboardAjaxHandler = JobAjaxHandler.extend({

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
        $.extend(obj, this.basicrequest("loadjobdashboardview", false), this.handlingTemplate(dfd), data);

        return $.ajax(obj);
    },

    restartJobs : function(jobids) {
        var obj = {
            traditional : true,
            dataType : "json"
        };

        var data = {
            "data" : {
                jobids : JSON.stringify(jobids),
                _wid: Vispa.workspaceManager.getWorkspace().id
            }
        };
        $.extend(obj, this.basicrequest("restartJobs", false), this.handling(), data);

        return $.ajax(obj);
    },

    stopJobs : function(jobids) {
        var obj = {
            traditional : true,
            dataType : "json"
        };

        var data = {
            "data" : {
                _wid: Vispa.workspaceManager.getWorkspace().id,
                jobids : JSON.stringify(jobids)                
            }
        };
        $.extend(obj, this.basicrequest("stopJobs", false), this.handling(), data);

        return $.ajax(obj);
    },

    removeJobs : function(jobids) {
        var obj = {
            traditional : true,
            dataType : "json"
        };

        var data = {
            "data" : {
                _wid: Vispa.workspaceManager.getWorkspace().id,
                jobids : JSON.stringify(jobids)
            }
        };
        $.extend(obj, this.basicrequest("removeJobs", false), this.handling(), data);

        return $.ajax(obj);
    },

    getJobCommand : function(jobid) {
        var obj = {};

        var data = {
            "data" : {
                _wid: Vispa.workspaceManager.getWorkspace().id,
                jobid : jobid
            }
        };
        $.extend(obj, this.basicrequest("getJobCommand", false), this.handling(), data);

        return $.ajax(obj);
    },

    getJobDetails : function(jobid, dfd) {
        var obj = {};

        var data = {
            "data" : {
                _wid: Vispa.workspaceManager.getWorkspace().id,
                jobid : jobid
            }
        };

        $.extend(obj, this.basicrequest("getJobDetails"), this.handling(dfd), data);

        return $.ajax(obj);
    },

    getJobData : function(dfd) {
        var obj = {
            dataType : "json"
        };

        var data = {
            "data" : {
                _wid: Vispa.workspaceManager.getWorkspace().id
                }
        };

        $.extend(obj, this.basicrequest("getJobData"), this.handling(dfd), data);
        console.debug("DEBUG GetJobData:" + obj);
        return $.ajax(obj);
    },

    getBatchManagerAvailability : function(jobid, dfd) {
        var obj = {
            datatype : "json"
        };

        var data = {
            "data" : {
                _wid: Vispa.workspaceManager.getWorkspace().id
                }
        };

        $.extend(obj, this.basicrequest("isBatchManagerAvailable"), this.handling(), data);

        return $.ajax(obj);
    }
});
