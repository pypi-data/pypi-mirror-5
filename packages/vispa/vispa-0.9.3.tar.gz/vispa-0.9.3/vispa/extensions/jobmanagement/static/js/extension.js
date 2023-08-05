var JobmanagementExtension = ExtensionBase.extend({

    init : function() {
        this._super();
        var _this = this;

        this.name = 'jobmanagement';

        this.factories = {
            jobdashboard : new JobDashboardFactory(),
            jobdesigner : new JobDesignerFactory(),
            jobsubmission : new JobSubmissionFactory()
        };
    }
});

var JobDashboardFactory = ExtensionFactoryFull.extend({

    init : function() {
        this._super();
        var _this = this;

        this.name = 'JobDashboard';
        this.constructor = JobDashboardContent;

        this.defaultConfig = {
            backgroundColor : {
                descr : 'The background color of this extension',
                select : [ 'white', 'red', 'blue' ],
                type : 'string',
                value : 'white'
            }
        };

        this.menuEntries = [ {
            label : 'new JobDashboard',
            icon : 'ui-icon-plus',
            callback : function() {
                _this._create();
            }
        } ];

        /*
         * this.fileHandlers = { txt: { priority: 1, callback: function() {
         * console.log('txt file Handler for', _this._id, arguments); } } };
         */

        /*
         * this.urlChannelHandlers = { dummyUrlChannel1: { priority: 1,
         * callback: function() { console.log('url channel "dummyUrlChannel1"
         * called, and passed to', _this._id, arguments); } } };
         */

    }
});

var JobDashboardContent = ExtensionContentFull.extend({

    init : function(config, path) {
        this._super(config);
        var _this = this;

        this.path = path;

        // attributes
        this.nodes = {};

        // the dashboard object (view, ajax requests, datamodel,...)
        this.dashboard = new JobDashboard(this);

        /*
         * this.menuEntries = [ { label: 'My Id', icon: 'ui-icon-comment',
         * callback: function() { $.Topic('msg.info').publish(_this._id); } } ];
         */
    },

    applyConfig : function() {
        // backgroundColor
        // $(this.nodes.content).css('background-color',
        // this._config.backgroundColor);
        return this;
    },

    render : function(node) {
        $(node).append(this.dashboard.view.startup());
        return this;

        /*
         * this.nodes.content = $('<div />')
         * .addClass('Jobmanagement-jobdashboard-body') .css('background-color',
         * this._config.backgroundColor) .html($.Helpers.strFormat('Jobdashboard
         * Content<br />Number: {0}', this._number)) .get(0); return
         * this.nodes.content;
         */
    },

    ready : function() {
        this._super();
        this.dashboard.view.ready();
        this._setLoading(false);
    }
});

var JobSubmissionFactory = ExtensionFactoryFull.extend({

    init : function() {
        this._super();
        var _this = this;

        this.name = 'JobSubmission';
        this.constructor = JobSubmissionContent;

        this.menuEntries = [ {
            label : 'new JobSubmission',
            icon : 'ui-icon-plus',
            callback : function() {
                _this._create();
            }
        } ];
    }
});

var JobSubmissionContent = ExtensionContentFull.extend({

    init : function(config, args) {
        this._super(config);
        var _this = this;
        
        // deferred object
        //this.dfd = args.dfd;

        // dictionary with jobs
        // this.jobs= args.jobs;

        // attributes
        this.nodes = {};
        
        this.args = args;

        // the submission object (view, ajax requests, datamodel,...)
        this.submission = new JobSubmission(this);
    },

    applyConfig : function() {
        return this;
    },

    render : function(node) {
        $(node).append(this.submission.view.startup());
        return this;
    },

    ready : function() {
        this.submission.view.initialize(this.args);
        this.submission.view.ready();
        this._setLoading(false);
    }
});

var JobDesignerFactory = ExtensionFactoryFull.extend({

    init : function() {
        this._super();
        var _this = this;

        this.name = 'JobDesigner';
        this.constructor = JobDesignerContent;

        this.menuEntries = [ {
            label : 'new JobDesigner',
            icon : 'ui-icon-plus',
            callback : function() {
                _this._create();
            }
        } ];
    }
});

var JobDesignerContent = ExtensionContentFull.extend({

    init : function(config, args) {
        this._super(config);
        var _this = this;
        
        this.args = args;

        /*
         * example arguments
         args = {command:"pxlun", 
                 optionList:optionList, 
                 resetCommandLineDesigner:true}
                 
                 default is resetCommandLineDesigner = true!
        
        
        ---- optionList -----
        
		var optionList = [];

		//add default options
		optionList.push([{
			name: "Analysis XML file",
			group: "pxlrun",
			optionString: '',
			value: "myAnalysis.xml",
			decorator: '',
			active:true
		},
		{
            name: "Analysis XML file2",
            group: "pxlrun",
            optionString: '',
            value: "myAnalysis2.xml",
            decorator: '',
		}
		]);

		this.args = {"optionList": optionList};
         */
        
        // attributes
        this.nodes = {};

        // the designer object (view, ajax requests, datamodel,...)
        this.jobdesigner = new JobDesigner(this);

        this.menuEntries = [ {
            label : 'Load',
            icon : 'ui-icon-folder-open',
            callback : function() {
             //$.Topic('msg.info').publish(_this._id);
                // if (!this.get("disabled")) self.loadFile();
            },
            disabled : false
        }, {
            label : 'Save',
            icon : 'ui-icon-disk',
            callback : function() {
                // $.Topic('msg.info').publish(_this._id);
                // if (!this.get("disabled")) self.saveFile();
            },
            disabled : true
        }, {
            label : 'Save as ...',
            icon : 'ui-icon-disk',
            callback : function() {
                // $.Topic('msg.info').publish(_this._id);
                // self.saveFileAs();
            },
            disabled : true
        }, {
            label : 'Refresh options from xml file ...',
            icon : 'ui-icon-arrowrefresh-1-w',
            callback : function() {
                // $.Topic('msg.info').publish(_this._id);
                // self.refreshFromXmlFile();
            },
            disabled : true
        }, {
            label : 'Reset Designer',
            icon : 'ui-icon-cancel',
            callback : function() {
                // $.Topic('msg.info').publish(_this._id);
                // self.refreshFromXmlFile();
                _this.jobdesigner.view.reset();
            },
            disabled : false
        } ];
        
    },

    applyConfig : function() {
        return this;
    },

    render : function(node) {
        $(node).append(this.jobdesigner.view.startup());
        return this;

    },

    ready : function() {
        var _this = this;
        this.jobdesigner.view.ready();
        this.jobdesigner.view.initialize(this.args);
        this._setLoading(false);

        /*
         * var dfd = jQuery.Deferred(); dfd.done(function(args){
         * this.jobdesigner.view.ready();
         * 
         * if (args.command) { var dfd = jQuery.Deferred();
         * 
         * dfd.done(function(args){_this.jobdesigner.view.refreshView(args);});
         * this.jobdesigner.ajax.setJobDesignerCommand(args.command, dfd); }
         * 
         * if (args.optionList) {
         * 
         * var dfd = jQuery.Deferred();
         * //dfd.done(function(args){_this.jobdesigner.view.refreshView(self.jobdesigner.ajax.getListOfOptions());});
         * dfd.done(function(args){_this.jobdesigner.view.refreshView(args);});
         * this.jobdesigner.ajax.addOptionList(args.optionList, dfd); } });
         * 
         * this.jobdesigner.ajax.resetCommandLineDesigner(dfd);
         */
    },

    refreshFromXmlFile : function() {
        var _this = this;
        $("#" + this._id + "-jobdesigner-dialog-refreshFromXmlFile").dialog({
            resizable : false,
            height : 100,
            width : 250,
            modal : true,
            create : function(event, ui) {

                $(event.target.parentNode).find(".ui-dialog-buttonpane").css({
                    "border" : "none",
                    "float" : "center",
                    "margin-left" : "auto",
                    "margin-right" : "auto"
                });
            },
            buttons : {
                "Yes" : function() {
                    var overwrite = true;
                    var path_to_xml = _this.jobdesigner.view.getPathToXML("Analysis XML file");

                    $(this).dialog("close");
                },
                "No" : function() {
                    var overwrite = false;
                    var path_to_xml = _this.jobdesigner.view.getPathToXML("Analysis XML file");

                    $(this).dialog("close");
                },
                Cancel : function() {
                    $(this).dialog("close");
                }
            }
        });
    },

    loadFile : function() {
        var _this = this;
        var openFunc = function(path) {

            var dfd = jQuery.Deferred();
            dfd.done(function(args) {
                this.jobdesigner.view.refreshView(args);
                this.path = path[0];
                this.enableSaveButton();
            });
            this.jobdesigner.ajax.loadJobFile(path[0], dfd);
        };

        var params = {
            path: "~",
            callback : openFunc,
            filter : {
                reverse : true,
                extensions : [ "job" ]
            },
            multimode : false,
            titleText : "Select files or folders that should be added to a new parameter range"
        };
                
        $.Topic("ext.file.selector").publish(params);

    },

    /*
     * enableSaveButton = function(){
     * Vispa.view.menus.getItem("toolbar-extmenu-content",
     * "Save").set("disabled", false); },
     */

    saveFile : function() {
        var _this = this;

        var dfd = jQuery.Deferred();
        dfd.done(function(args) {
            _this.jobdesigner.view.refreshView(args);
            _this.enableSaveButton();
        });
        this.jobdesigner.ajax.saveJobFile(this.path, dfd);
    },

    saveFileAs : function() {
        var _this = this

        var openFunc = function(path) {
            this.path = path[0];
            this.saveFile();
        };

        var params = {
            path: "~",
            callback : openFunc,
            filter : {
                reverse : true,
                extensions : [ "job" ]
            },
            creationMode : true,
            multimode : false,
            titleText : "Save *.job file"
        };
        $.Topic("ext.file.selector").publish(params);        
        
    }

});

$(function() {
    // register the Extension
    $.Topic('extman.register').publish(JobmanagementExtension);
});
