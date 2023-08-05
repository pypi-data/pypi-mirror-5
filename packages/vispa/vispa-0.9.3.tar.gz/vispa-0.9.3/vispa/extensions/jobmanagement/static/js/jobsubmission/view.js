var JobSubmissionTabView = Class.extend({

    init : function(owner) {
        // store the owner
        this.owner = owner;

        this.started = false;
        this.batchManagerSelector = false;
    },

    initialize : function(args) {
        console.debug("DEBUG JobSubmissionTabView: initialize for '"+this.owner.owner._id+"'");
        
       var _this = this;
       
       if (typeof(args) != "undefined")
       {
           if (typeof(args.jobs) != "undefined")
           {
                if (args.jobs) {
                  console.log(("#" + this.owner.owner._id + "-JobPreviewText"));
                  console.log($("#" + this.owner.owner._id + "-JobPreviewText"));
                  
                    $("#" + this.owner.owner._id + "-JobPreviewText").val(_this.getJobPreviewTextFromJobs(args.jobs));
                } else
                    $("#" + this.owner.owner._id + "-JobPreviewText").html("/insert/full/path");
           }
       }
    },

    startup : function() {
        var content = "";
        var footer = "";
        var header = "";

        content += header;
        var dfd = $.when(this.owner.ajax.getTemplate()).done(function(args) {
            content += args;
        });
        content += footer;

        this.started = true;

        return content;
    },

    changeBatchManagerSelectorCallback : function(args) {
        // get the current selection
        var selectedManager = $(this.batchManagerSelector.jid).val();

        // load the job configuration template
        var jobConfigurationHTMLPage = "";

        $.when(this.owner.ajax.getBatchManagerConfiguration(selectedManager)).done(function(args) {
            jobConfigurationHTMLPage += args;
        });

        $("#" + this.owner.owner._id + "-BatchSystemConfiguration").html(jobConfigurationHTMLPage);
        $("#" + this.owner.owner._id + "-BatchSystemConfigurationHeader").html("Batchsystem configuration: Active is " + selectedManager);

        // hide all descriptions
        this.batchManagerSelector.hideAllDescriptions();

        // show explanation of current selection
        this.batchManagerSelector.showDescription(selectedManager);

        // destroy and recreate accordion to fix some layout bugs
        $("#" + this.owner.owner._id + "-bmbody").accordion('destroy').accordion({
            collapsible : true,
            heightStyle : "content"
        });
    },

    ready : function() {
        var _this = this;

        this.batchManagerSelector = new BatchManagerSelector({
            description : false,
            changeCallback : function(args) {
                _this.changeBatchManagerSelectorCallback(args)
            }
        });

        var dfd = jQuery.Deferred();
        dfd.done(function(args) {
            if (args) {
                _this.batchManagerSelector.setOptions(args.data);
                _this.batchManagerSelector.initialize("#" + _this.owner.owner._id + "-header");

                // initial setting of BM configuration
                $("#" + _this.owner.owner._id + "-BatchSystemConfigurationHeader").html(
                        "Batchsystem configuration: Active is " + $(_this.batchManagerSelector.jid).val());

                var jobConfigurationHTMLPage = "";
                $.when(_this.owner.ajax.getBatchManagerConfiguration($(_this.batchManagerSelector.jid).val())).done(function(args) {
                    jobConfigurationHTMLPage += args;
                });

                $("#" + _this.owner.owner._id + "-BatchSystemConfiguration").html(jobConfigurationHTMLPage);

                _this.batchManagerSelector.showDescription($(_this.batchManagerSelector.jid).val());
            }
        });
        this.owner.ajax.getAvailableBatchManager(dfd);

        // connect the body (jquery ui with type 'accordian')
        $("#" + this.owner.owner._id + "-bmbody").accordion({
            collapsible : true,
            heightStyle : "content"
        });

        $("textarea#" + this.owner.owner._id + "-JobPreviewTextArea").click(function() {
            $("textarea#" + _this.owner.owner._id + "-JobPreviewTextArea").blur();
            // $(this).focus();
            $('#bmbody').focus();
        });

        // job configuration
        // $("#"+this.owner.owner._id+"-BatchSystemConfiguration").load("CondorBatchManagerConfiguration.html",
        // {'selectedBatchManager': "Condor"});

        // PreExecutionScript
        $("textarea#" + this.owner.owner._id + "-PreExecutionScriptText").click(function() {
            $("textarea#" + _this.owner.owner._id + "-PreExecutionScriptText").blur();
            $(this).focus();
        });

        $("#" + this.owner.owner._id + "-savePreExecutionScriptButton").button({});
        $("#" + this.owner.owner._id + "-savePreExecutionScriptButton").click(function(event) {
            _this.saveText("textarea#" + _this.owner.owner._id + "-PreExecutionScriptText");
        });

        $("#" + this.owner.owner._id + "-loadPreExecutionScriptButton").button({});
        $("#" + this.owner.owner._id + "-loadPreExecutionScriptButton").click(function(event) {
            _this.loadText("textarea#" + _this.owner.owner._id + "-PreExecutionScriptText");
        });

        $("#" + this.owner.owner._id + "-resetPreExecutionScriptButton").button({});
        $("#" + this.owner.owner._id + "-resetPreExecutionScriptButton").click(function(event) {
            $("textarea#" + _this.owner.owner._id + "-PreExecutionScriptText").val("");
        });

        // PostExecutionScript
        $("textarea#" + this.owner.owner._id + "-PostExecutionScriptText").click(function() {
            $("textarea#" + _this.owner.owner._id + "-PostExecutionScriptText").blur();
            $(this).focus();
        });

        $("#" + this.owner.owner._id + "-savePostExecutionScriptButton").button({});
        $("#" + this.owner.owner._id + "-savePostExecutionScriptButton").click(function(event) {
            _this.saveText("textarea#" + _this.owner.owner._id + "-PostExecutionScriptText");
        });

        $("#" + this.owner.owner._id + "-loadPostExecutionScriptButton").button({});
        $("#" + this.owner.owner._id + "-loadPostExecutionScriptButton").click(function(event) {
            _this.loadText("textarea#" + _this.owner.owner._id + "-PostExecutionScriptText");
        });

        $("#" + this.owner.owner._id + "-resetPostExecutionScriptButton").button({});
        $("#" + this.owner.owner._id + "-resetPostExecutionScriptButton").click(function(event) {
            $("textarea#" + _this.owner.owner._id + "-PostExecutionScriptText").val("");
        });

        // connect the footer
        $("#" + this.owner.owner._id + "-submitButton").button({});
        $("#" + this.owner.owner._id + "-submitButton").click(function(event) {

            var lines = $('#' + _this.owner.owner._id + '-JobPreviewText').val().split('\n');

            var jobs = [];

            $.each(lines, function() {
                if (this.length > 0) {
                    jobs.push({
                        "command" : this,
                        "manager" : $(_this.batchManagerSelector.jid).val(),
                        "preExecutionScriptText" : $("textarea#" + _this.owner.owner._id + "-PreExecutionScriptText").val(),
                        "postExecutionScriptText" : $("textarea#" + _this.owner.owner._id + "-PostExecutionScriptText").val(),
                        "outputPath" : ""
                    });
                }
            });

            var dfd = null;
            _this.owner.ajax.runJobs(jobs, dfd);
        });

        $("#" + this.owner.owner._id + "-cancelButton").button();
        $("#" + this.owner.owner._id + "-cancelButton").click(function(event) {
            alert("clicked");
        });

        // some dummy or initial settings
        $("textarea#" + this.owner.owner._id + "-JobPreviewTextArea").each(function() {
            $(this).attr('readonly', 'readonly');
        });
    },

    loadText : function(textareaJID) {
        var _this = this;
        var openFunc = function(path) {
            var dfd = jQuery.Deferred();
            dfd.done(function(args) {
                $(textareaJID).val(args.content);
            });
            _this.owner.ajax.readFile(path[0], dfd);
        };

        var params = {
            path: "~",
            callback : openFunc,
            multimode : false,
            titleText : "Select a file with a script"
        };
        $.Topic("ext.file.selector").publish(params);

    },

    saveText : function(textareaJID) {
        var _this = this;

        var openFunc = function(path) {
            var dfd = jQuery.Deferred();
            dfd.done(function(args) {
                // do nothing
            });
            _this.owner.ajax.saveFile(path[0], $(textareaJID).val(), dfd);
        };

        var params = {
            path: "~",
            callback : openFunc,
            multimode : false,
            titleText : "Select a file to save the script"
        };
        $.Topic("ext.file.selector").publish(params);
        
    },

    getJobPreviewTextFromJobs : function(jobs) {
        var value = "";
        // {dfd:dfd, jobs:{"AnalysisDesignerJob":{command: "pxlrun -p",
        // arguments: [pxlrun_arguments], outputPath:
        // this.workflow.outputPath}}}

        $.each(jobs, function(index, job) {
            value += "" + job.command;
            $.each(job.arguments, function(index, argument) {
                value += " " + argument;
            });
            value += "\n";
        });
        return value;
    }

});