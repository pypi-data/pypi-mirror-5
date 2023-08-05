var JobDashboardView = Class.extend({

    init : function(owner) {
        // this._super();

        // store a reference to this object (needed for callback functions or
        // any change of "this" scope in jquery methods, e.g. $.each()...)
        var _this = this;

        // store the owner
        this.owner = owner;

        this.dataTable = false;
        this.buttonSet = false;

        this.started = false;
    },

    /*
     * afterCloseDashboard: function() { dojo.publish("removePolling", [
     * "JobDashboard"]); },
     */

    clickRow : function(args) {
        var _this = this;

        if (args.Jobid) {
            $("#" + this.owner.owner._id + "-JobDetailedViewTable-jobid").text(args.Jobid);
            $("#" + this.owner.owner._id + "-JobDetailedViewTable-command").text(args.Command);

            var dfd = jQuery.Deferred();
            dfd.done(function(args) {
                var data = args.data;

                if (typeof data !== "undefined") {
                    if (!data.stdout)
                        data.stdout = "Job stdout not found";

                    if (!data.stderr)
                        data.stderr = "Job stderr not found";

                    _this.updateDetailedView({
                        stdout : data.stdout,
                        stderr : data.stderr
                    });
                }
            });
            this.owner.ajax.getJobDetails(args.Jobid, dfd);
        }
    },

    startup : function() {
        var _this = this;
        this.dataTable = new SelectableTable({
            columns : [ "Jobid", "Command", "Status", "Creation Time", "Finished Time", "Runtime" ],
            blindColumns : [ "Jobid" ],
            multiselect : true,
            //classes : "mytablestyle fixedtable",
            //classes : "fixedtable",
            //headclasses : "ui-widget ui-widget-header",
            //bodyclasses : "ui-widget ui-widget-content",
            clickCallback : function(args) {
                _this.clickRow(args)
            }
        });

        // add callback functions
        this.owner.addCallback("update", function(args) {
            _this.updateView(args)
        });

        this.buttonSet = {
            "selectall" : new SimpleButton({
                iconlist : [ "ui-icon-check" ],
                title : "Select all",
                tooltip : "Select/Unselect all jobs",
                clickCallback : function(args) {
                    _this.buttonClickCallback(args)
                },
                identifier : "selectall"
            }),
            "reload" : new SimpleButton({
                iconlist : [ "ui-icon-arrowrefresh-1-s" ],
                title : "Reload",
                tooltip : "Reload the data table",
                clickCallback : function(args) {
                    _this.buttonClickCallback(args)
                },
                identifier : "reload"
            }),
            "remove" : new SimpleButton({
                iconlist : [ "ui-icon-trash" ],
                title : "Remove",
                tooltip : "Remove the selected jobs",
                clickCallback : function(args) {
                    _this.buttonClickCallback(args)
                },
                identifier : "remove"
            }),
            "stop" : new SimpleButton({
                iconlist : [ "ui-icon-stop" ],
                title : "Stop",
                tooltip : "Stop the selected jobs",
                clickCallback : function(args) {
                    _this.buttonClickCallback(args)
                },
                identifier : "stop"
            }),
            "restart" : new SimpleButton({
                iconlist : [ "ui-icon-triangle-e" ],
                title : "Restart",
                tooltip : "Restart the selected jobs",
                clickCallback : function(args) {
                    _this.buttonClickCallback(args)
                },
                identifier : "restart"
            })
        };

        var content = "";
        var footer = "";
        var header = "";

        content += header;
        var dfd = $.when(this.owner.ajax.getTemplate()).done(function(args) {
            content += args;
        });
        content += footer;

        this.started = true;

        // dojo.publish("addPolling", [ "JobDashboard",
        // function(){self.refresh();}]);
        return content;
    },

    // callback function for polling
    refresh : function() {
        var _this = this;

        var dfd = jQuery.Deferred();

        dfd.done(function(args) {
            _this.refreshDataModel(args);
        });
        this.owner.ajax.getJobData(dfd);
    },

    refreshDataModel : function(args) {
        console.debug("DEBUG Dashboard: refreshDataModel");

        if (typeof (args) == "undefined") {
            console.error("ERROR Dashboard refreshDataModel: Couldn't refresh data model, got empty arguments!");
        }

        if (args.data) {
            if (args.data.length > 0) {
                this.owner.dataModel.replaceData(jQuery.makeArray(args.data), "jobid");
            }
        }
    },

    updateView : function(args) {
        console.debug("DEBUG Dashboard: updateView");

        this.updateTable();
    },

    updateDetailedView : function(args) {
        console.debug("DEBUG Dashboard: updateDetailedView");
        if (args.stdout) {
            $("#" + this.owner.owner._id + "-JobDetailedViewTable-stdout").text(args.stdout);
        }

        if (args.stderr) {
            $("#" + this.owner.owner._id + "-JobDetailedViewTable-stderr").text(args.stderr);
        }
    },

    updateTable : function() {
        console.debug("DEBUG Dashboard: updateTable");

        this.dataTable.clearRows();

        var data = this.owner.dataModel.getData();
        if (((typeof data) !== 'undefined') && data.length > 0) {
            var rows = [];

            $.each(data, function(index, element) {
                rows.push({
                    "Jobid" : (typeof element.jobid == 'undefined' ? "" : element.jobid),
                    "Command" : (typeof element.command == 'undefined' ? "" : element.command),
                    "Status" : (typeof element.status == 'undefined' ? "" : element.status),
                    "Creation Time" : (typeof element.submissiontime == 'undefined' ? "" : element.submissiontime),
                    "Finished Time" : (typeof element.finishedtime == 'undefined' ? "" : element.finishedtime),
                    "Runtime" : (typeof element.runtime == 'undefined' ? "" : element.runtime)
                });
            });
            this.dataTable.addRows(rows, false);

        }

    },

    loadData : function() {
        var dfd = jQuery.Deferred();
        dfd.done(function(args) {
            _this.loadDataView(args);
        });
        this.owner.ajax.getJobData(dfd);
    },

    buttonClickCallback : function(args) {
        if (args.data.identifier) {
            switch (args.data.identifier) {
            case "selectall":
                this.dataTable.toggleRows();
                break;
            case "reload":
                this.refresh();
                break;
            case "remove":
                var joblist = this.dataTable.getSelectedRows();
                if (confirm("Do you really want to remove the chosen " + (joblist.length == 1 ? "Job?" : String(joblist.length) + " Jobs?"))) {
                    var jobids = [];

                    $.each(joblist, function(index, element) {
                        jobids.push(element.Jobid);
                    });

                    this.owner.ajax.removeJobs(jobids);

                    this.refresh();
                }
                break;
            case "stop":
                var joblist = this.dataTable.getSelectedRows();
                /*
                 * if (confirm("Do you really want to stop the chosen " +
                 * (joblist.length == 1 ? "Job?" : String(joblist.length)+ "
                 * Jobs?"))) { var jobids = [];
                 * 
                 * $.each(joblist, function(index, element) {
                 * jobids.push(element.Jobid); });
                 * 
                 * this.owner.ajax.stopJobs(jobids);
                 * 
                 * this.refresh(); }
                 */
                var testJobs = [ {
                    "status" : "Finished Normally",
                    "finishedtime" : "2013-02-14 16:52:52",
                    "jobid" : "69915d07-3ccf-442c-831c-73275c4599ad",
                    "command" : "pxlrun -p /user/klingebiel/vispa-webLOCAL/var/data/user/123456/cms_z_short/cms_z_short.xml",
                    "submissiontime" : "2013-02-14 16:52:50",
                    "runtime" : "0:00:02"
                }, {
                    "status" : "Finished Normally",
                    "finishedtime" : "2013-02-14 16:52:57",
                    "jobid" : "9247f204-74a4-4db8-a635-c9dee6e1e6e4",
                    "command" : "pxlrun -p /user/klingebiel/vispa-webLOCAL/var/data/user/123456/cms_z_short/cms_z_short.xml",
                    "submissiontime" : "2013-02-14 16:52:54",
                    "runtime" : "0:00:03"
                }, {
                    "status" : "Finished Normally",
                    "finishedtime" : "2013-02-14 16:52:52",
                    "jobid" : "69915d07-3ccf-442c-831c-73275c4599bd",
                    "command" : "pxlrun -p /user/klingebiel/vispa-webLOCAL/var/data/user/123456/cms_z_short/cms_z_short.xml",
                    "submissiontime" : "2013-02-14 16:52:50",
                    "runtime" : "0:00:02"
                }, {
                    "status" : "Finished Normally",
                    "finishedtime" : "2013-02-14 16:52:57",
                    "jobid" : "9247f204-74a4-4db8-a635-c9dee6e1e6f4",
                    "command" : "pxlrun -p /user/klingebiel/vispa-webLOCAL/var/data/user/123456/cms_z_short/cms_z_short.xml",
                    "submissiontime" : "2013-02-14 16:52:54",
                    "runtime" : "0:00:03"
                }, {
                    "status" : "Finished Normally",
                    "finishedtime" : "2013-02-14 16:52:52",
                    "jobid" : "69915d07-3ccf-442c-831c-73275c4599cd",
                    "command" : "pxlrun -p /user/klingebiel/vispa-webLOCAL/var/data/user/123456/cms_z_short/cms_z_short.xml",
                    "submissiontime" : "2013-02-14 16:52:50",
                    "runtime" : "0:00:02"
                }, {
                    "status" : "Finished Normally",
                    "finishedtime" : "2013-02-14 16:52:57",
                    "jobid" : "9247f204-74a4-4db8-a635-c9dee6e1e6g4",
                    "command" : "pxlrun -p /user/klingebiel/vispa-webLOCAL/var/data/user/123456/cms_z_short/cms_z_short.xml",
                    "submissiontime" : "2013-02-14 16:52:54",
                    "runtime" : "0:00:03"
                } ];
                this.owner.dataModel.replaceData($.makeArray(testJobs), "jobid");

                break;
            case "restart":
                var joblist = this.dataTable.getSelectedRows();
                if (confirm("Do you really want to restart the chosen " + (joblist.length == 1 ? "Job?" : String(joblist.length) + " Jobs?"))) {
                    var jobids = [];

                    $.each(joblist, function(index, element) {
                        jobids.push(element.Jobid);
                    });

                    this.owner.ajax.restartJobs(jobids);

                    this.refresh();
                }
                break;
            default:

                break;
            }
        }
    },

    ready : function() {
        var _this = this;

        if (!this.started)
            this.startup();

        /*
         * $( ".column" ).sortable({ connectWith: ".column" });
         */

        $(".column").disableSelection();

        $(".portlet").addClass("ui-widget ui-widget-content ui-helper-clearfix ui-corner-all").find(".portlet-header").addClass(
                "ui-widget-header ui-corner-all").prepend("<span class='ui-icon ui-icon-minusthick'></span>").end()

        // connect the minus icon to minimize the portlet
        $(".portlet-header .ui-icon-minusthick").click(function() {
            $(this).toggleClass("ui-icon-minusthick").toggleClass("ui-icon-plusthick");
            $(this).parents(".portlet:first").find(".portlet-content").toggle();
        });

        this.dataTable.initializeTable($("#" + this.owner.owner._id + "-tableDataContent"));

        // initialize all buttons
        $.each(this.buttonSet, function(key, value) {
            value.initializeButton($("#" + _this.owner.owner._id + "-buttonContent"));
        });

    }
});