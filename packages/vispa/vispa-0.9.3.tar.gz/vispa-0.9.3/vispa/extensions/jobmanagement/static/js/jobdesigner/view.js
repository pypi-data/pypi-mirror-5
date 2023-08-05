var JobDesignerTabView = Class
        .extend({

            init : function(owner) {
                // store the owner
                this.owner = owner;
                this.dataTableAvailableOptions = false;
            },
            
            initialize : function(args) {
                console.debug("DEBUG JobDesignerTabView: initialize for '"+this.owner.owner._id+"'");
               var _this = this;
                              
               var reset = true; //default
               if (typeof(args) != "undefined")
               {
                   if (typeof(args.resetCommandLineDesigner) != "undefined")
                       reset = args.resetCommandLineDesigner;
               }
               
               if (reset)
                   _this.reset();
               else
                   _this.initializeOptionList(args);
            },
            
            initializeOptionList : function(args)
            {
                var _this = this;
                
                if (typeof(args) != "undefined")
                {
                    if (typeof(args.command) != "undefined")
                    {
                         var dfdCommand = jQuery.Deferred();
                                 
                         dfdCommand.done(function(commandargs){_this.refreshView(commandargs);});         
                         _this.owner.ajax.setJobDesignerCommand(args.command, dfdCommand);
                     }
                    
                    if (args.optionList)
                    {
                        var dfdOptionList = jQuery.Deferred();
                        dfdOptionList.done(function(optionlistargs){_this.refreshView(optionlistargs);});
                        _this.owner.ajax.addOptionList(args.optionList, dfdOptionList);
                    }
                }
            },
            
            reset : function()
            {
                var _this = this;
                
                var dfd = jQuery.Deferred();
                dfd.done(function(args) {
                    _this.initializeOptionList(args);
                    
                    // refresh the view
                    var dfdStatus = jQuery.Deferred();
                    dfdStatus.done(function(args) {
                        _this.refreshView(args);
                    });
                    _this.owner.ajax.getStatus(dfdStatus);
                });
                this.owner.ajax.resetCommandLineDesigner(dfd);
            },

            getSimpleIconButton : function(iconlist, classes, mytitle) {

                var title = "";

                if (mytitle)
                    title = mytitle;

                if (iconlist.length > 1) {
                    var button = $("<button class='" + classes + "' title='" + title + "'>").button({
                        icons : {
                            primary : iconlist[0],
                            secondary : iconlist[1]
                        }
                    });
                } else {
                    var button = $("<button class='" + classes + "' title='" + title + "'>").button({
                        icons : {
                            primary : iconlist[0]
                        }
                    });
                }

                return button;
            },

            startup : function() {
                var _this = this;

                /*
                 * this.dataTableAvailableOptions = new SelectableTable({
                 * columns:["Options", "Active", "Default values", "Command-line<br>option
                 * flag", "Range"], multiselect:false, classes:"mytablestyle
                 * fixedtable", headclasses:"ui-widget ui-widget-header",
                 * bodyclasses:"ui-widget ui-widget-content",
                 * clickCallback:function(args){_this.clickRow(args,
                 * "AvailableOptions")} });
                 */

                var header = ""
                var body = "";
                $.when(_this.owner.ajax.getTemplate()).done(function(args) {
                    body += args;
                });

                var footer = '\
        	';
                var content = "";

                content += header;
                content += body;
                content += footer;

                return content;
            },

            clickRow : function(args, index) {
                if (index == "AvailableOptions") {

                }

            },

            ready : function() {

                var _this = this;

                // $("#"+this.owner.owner._id+"-jobdesigner-parameterranges").dialog();
                // $("#"+this.owner.owner._id+"-jobdesigner-decorators").dialog();
                // $("#"+this.owner.owner._id+"-jobdesigner-availableoptions").dialog();

                $(".column" + "." + this.owner.owner._id).sortable({
                    connectWith : ".column"
                });

                $(".portlet")
                        .addClass("ui-widget ui-widget-content ui-helper-clearfix ui-corner-all")
                        .find("." + this.owner.owner._id + ".portlet-header")
                        .addClass("ui-widget-header ui-corner-all")
                        .prepend("<span class='ui-icon ui-icon-minusthick'></span>")
                        .end()
                        .find("." + this.owner.owner._id + ".portlet-headeradddelete")
                        .addClass("ui-widget-header ui-corner-all")
                        .prepend("<span class='ui-icon ui-icon-minusthick' style='float:right'></span>")
                        .append(
                                "<div class='jobmanagement forceinline ui-hide-label no-field-separator' data-role='fieldcontain' data-type='horizontal' ><fieldset class='AdditionalIcons jobmanagement ui-hide-label no-field-separator' data-mini='true' data-role='controlgroup' data-type='horizontal'><span class='ui-icon ui-icon-circle-plus floatleft' title='Add'></span><span class='ui-icon ui-icon-circle-minus floatleft' title='Delete'></span><span class='ui-icon ui-icon-pencil floatleft' title='Modify'></span></fieldset></div>")
                        .end().find("." + this.owner.owner._id + ".portlet-content");

                var bt_openFolder = this.getSimpleIconButton([ "ui-icon-folder-open" ], "floatleft", "Create a new parameter range using the file browser"); // ,
                // "ui-icon-document"
                var bt_add = this.getSimpleIconButton([ "ui-icon-circle-plus" ], "floatleft", "Add");
                var bt_delete = this.getSimpleIconButton([ "ui-icon-circle-minus" ], "floatleft", "Delete");
                var bt_modify = this.getSimpleIconButton([ "ui-icon-pencil" ], "floatleft", "Modify");
                var bt_toggleActive = this.getSimpleIconButton([ "ui-icon-check" ], "floatleft", "Show or hide active options");
                var bt_toggleActive = "<span class='ui-icon ui-icon-check floatleft' title='Show or hide active options'></span>";

                var bt_openFolder = "<span class='ui-icon ui-icon-folder-open floatleft' title='Create a new parameter range using the file browser'></span>";

                // bt_openFolder.appendTo($("#"+this.owner.owner._id+"-jobdesigner-parameterrangesHeader").find('.AdditionalIcons'));
                $("#" + this.owner.owner._id + "-jobdesigner-parameterrangesHeader").find('.AdditionalIcons').append(bt_openFolder);

                $("#" + this.owner.owner._id + "-jobdesigner-availableoptionsHeader").find('.AdditionalIcons').append(bt_toggleActive);

                // bt_openFolder.click(function() {
                $(".portlet-headeradddelete .ui-icon-folder-open").click(function() {

                    var openFunc = function(paths) {
                        var pr = {
                            name : "InputFiles",
                            active : true,
                            values : paths,
                            script : ""
                        };

                        var dfd = jQuery.Deferred();
                        dfd.done(function(args) {
                            _this.refreshView(args);
                        });
                        _this.owner.ajax.addParameterRange(pr.name, pr.active, pr.values, pr.script, dfd);
                    };
                    // folderMode
                    var params = {
                        path: "~", 
                        callback : openFunc,
                        multimode : true,
                        titleText : "Select files or folders that should be added to a new parameter range"
                    };
                    
                    $.Topic("ext.file.selector").publish(params);
                });

                // toggle active options
                $(".portlet-headeradddelete .ui-icon-check").click(
                        function() {

                            var should_hide = !($(this).hasClass("togglehide"));

                            if (should_hide)
                                $(this).addClass("togglehide");
                            else
                                $(this).removeClass("togglehide");

                            var not_selected_rows = $("#" + _this.owner.owner._id + "-jobdesigner-availableoptionsTable").find('tbody').find('tr').has(
                                    ':not(th)').filter(function(index) {
                                if (!$(this).hasClass("parent")) {
                                    if (this.cells.length > 1 && this.cells[1].children.length > 0 && this.cells[1].children[0].type == "checkbox") {
                                        return !($(this.cells[1].children[0]).is(':checked'));
                                    }
                                }
                                return false;
                            });

                            $.each(not_selected_rows, function(indexrow, row) {
                                if (should_hide)
                                    $(row).addClass("hiddenrow");
                                else
                                    $(row).removeClass("hiddenrow");
                            });
                        });

                // connect the minus icon to minimize the portlet
                $("." + this.owner.owner._id + ".portlet-header .ui-icon-minusthick").click(function() {
                    $(this).toggleClass("ui-icon-minusthick").toggleClass("ui-icon-plusthick");
                    $(this).parents(".portlet:first").find(".portlet-content").toggle();
                });

                // connect the dialog buttons
                $("#" + this.owner.owner._id + "-jobdesigner-dialog-parameterranges-evaluateScriptButton").button();
                $("#" + this.owner.owner._id + "-jobdesigner-dialog-parameterranges-evaluateScriptButton").click(function() {
                    var dfd = jQuery.Deferred();
                    dfd.done(function(args) {
                        var newValues = args;

                        // check whether the last script execution was
                        // successfull
                        if (!newValues.scriptStatus) {
                            // $("#"+_this.owner.owner._id+"-jobdesigner-dialog-parameterranges-valuespreview").text("");
                            $("#" + _this.owner.owner._id + "-jobdesigner-dialog-parameterranges-valuespreview").css("background-color", "red");
                            $("#" + _this.owner.owner._id + "-jobdesigner-dialog-parameterranges-valuespreview").text("ERROR");
                        } else {
                            $("#" + _this.owner.owner._id + "-jobdesigner-dialog-parameterranges-valuespreview").css("background-color", "");
                            // update the preview values text
                            $("#" + _this.owner.owner._id + "-jobdesigner-dialog-parameterranges-valuespreview").text(newValues.valueslist);
                        }

                    });

                    _this.owner.ajax.getParameterRange($("#" + _this.owner.owner._id + "-jobdesigner-dialog-parameterranges-script").val(), dfd);
                });

                $("#" + this.owner.owner._id + "-jobdesigner-dialog-parameterranges-saveScriptButton").button();
                $("#" + this.owner.owner._id + "-jobdesigner-dialog-parameterranges-saveScriptButton").click(function() {
                    _this.saveText("#" + _this.owner.owner._id + "-jobdesigner-dialog-parameterranges-script");
                });

                $("#" + this.owner.owner._id + "-jobdesigner-dialog-parameterranges-loadScriptButton").button();
                $("#" + this.owner.owner._id + "-jobdesigner-dialog-parameterranges-loadScriptButton").click(function() {
                    _this.loadText("#" + _this.owner.owner._id + "-jobdesigner-dialog-parameterranges-script");
                });

                $("#" + this.owner.owner._id + "-jobdesigner-dialog-decorators-saveScriptButton").button();
                $("#" + this.owner.owner._id + "-jobdesigner-dialog-decorators-saveScriptButton").click(function() {
                    _this.saveText("#" + _this.owner.owner._id + "-jobdesigner-dialog-decorators-script");
                });

                $("#" + this.owner.owner._id + "-jobdesigner-dialog-decorators-loadScriptButton").button();
                $("#" + this.owner.owner._id + "-jobdesigner-dialog-decorators-loadScriptButton").click(function() {
                    _this.loadText("#" + _this.owner.owner._id + "-jobdesigner-dialog-decorators-script");
                });

                // connect the minus icon to minimize the portlet
                $("." + this.owner.owner._id + ".portlet-headeradddelete .ui-icon-minusthick").click(function() {
                    $(this).toggleClass("ui-icon-minusthick").toggleClass("ui-icon-plusthick");
                    $(this).parents(".portlet:first").find(".portlet-content").toggle();
                });

                $(".column").disableSelection();

                // Widgets
                // Command
                $("#" + this.owner.owner._id + "-jobdesigner-commandButton").button();
                $("#" + this.owner.owner._id + "-jobdesigner-commandButton").click(function() {
                    var dfd = jQuery.Deferred();
                    dfd.done(function(args) {
                        _this.refreshView(args);
                    });
                    _this.owner.ajax.setJobDesignerCommand($("#" + _this.owner.owner._id + "-jobdesigner-commandText").val(), dfd);
                });

                $("#" + this.owner.owner._id + "-jobdesigner-commandContent").click(function() {
                    $("#" + _this.owner.owner._id + "-jobdesigner-commandText").focus();
                });

                // Available options

                // dialog to add a new option to the available options
                // connect the circle plus icon
                $("#" + this.owner.owner._id + "-jobdesigner-availableoptionsHeader .ui-icon-circle-plus").click(
                        function() {
                            $("#" + _this.owner.owner._id + "-jobdesigner-dialog-addnewoption").dialog(
                                    {
                                        resizable : true,
                                        height : 500,
                                        width : "30%",
                                        modal : true,
                                        buttons : {
                                            "Add" : function() {
                                                var dfd = jQuery.Deferred();
                                                dfd.done(function(args) {
                                                    _this.refreshView(args);
                                                });
                                                var decorator = "";
                                                _this.owner.ajax.addOption($("#" + _this.owner.owner._id + "-jobdesigner-dialog-addnewoption-name").val(), $(
                                                        "#" + _this.owner.owner._id + "-jobdesigner-dialog-addnewoption-optionstring").val(), $(
                                                        "#" + _this.owner.owner._id + "-jobdesigner-dialog-addnewoption-active").is(':checked'), $(
                                                        "#" + _this.owner.owner._id + "-jobdesigner-dialog-addnewoption-value").val(), $(
                                                        "#" + _this.owner.owner._id + "-jobdesigner-dialog-addnewoption-group").val(), decorator, dfd);
                                                $(this).dialog("close");
                                            },
                                            Cancel : function() {
                                                $(this).dialog("close");
                                            }
                                        },
                                        close : function(event, ui) {
                                            _this.clearAvailableOptionsDialog();
                                        }
                                    });
                        });

                // connect the circle minus icon
                $("#" + this.owner.owner._id + "-jobdesigner-availableoptionsHeader .ui-icon-circle-minus").click(function() {
                    // $("#"+_this.owner.owner._id+"-jobdesigner-availableoptionsContent").dynatree("getActiveNode").remove();

                    var selected = _this.getFirstColumnValuesOfSelectedRows("#" + _this.owner.owner._id + "-jobdesigner-availableoptionsTable");

                    if (selected.length > 0) {
                        var dfd = jQuery.Deferred();
                        dfd.done(function(args) {
                            _this.refreshView(args);
                        });

                        _this.owner.ajax.removeOptions(selected, dfd);
                    }

                });

                // connect the pencil icon (modify)
                $("#" + this.owner.owner._id + "-jobdesigner-availableoptionsHeader .ui-icon-pencil").click(function() {

                    var selected = _this.getColumnValuesOfSelectedRows("#" + _this.owner.owner._id + "-jobdesigner-availableoptionsTable");

                    if (selected.length > 0) {
                        var currentElement = selected[0];

                        _this.clearAvailableOptionsDialog();

                        $("#" + _this.owner.owner._id + "-jobdesigner-dialog-addnewoption-name").val(currentElement["Option"]);
                        $("#" + _this.owner.owner._id + "-jobdesigner-dialog-addnewoption-optionstring").val(currentElement["Command-lineoption flag"]);
                        $("#" + _this.owner.owner._id + "-jobdesigner-dialog-addnewoption-active").prop('checked', currentElement["Active"]);
                        $("#" + _this.owner.owner._id + "-jobdesigner-dialog-addnewoption-value").val(currentElement["Default values"]);
                        // $("#"+_this.owner.owner._id+"-jobdesigner-dialog-addnewoption-group").val(currentElement["Default
                        // values"]);

                        // create the modify dialog
                        $("#" + _this.owner.owner._id + "-jobdesigner-dialog-addnewoption").dialog({
                            title : "Modify an option",
                            resizable : true,
                            height : 500,
                            width : "30%",
                            modal : true,
                            buttons : {
                                "Modify" : function() {
                                    var dfd = jQuery.Deferred();
                                    dfd.done(function(args) {
                                        _this.refreshView(args);
                                    });

                                    // do not use the return array from split()
                                    // directly as it makes it easier to handle
                                    // conversion or user input errors...
                                    var newValues = [ {
                                        "key" : "optionString",
                                        "value" : $("#" + _this.owner.owner._id + "-jobdesigner-dialog-addnewoption-optionstring").val()
                                    }, {
                                        "key" : "active",
                                        "value" : $("#" + _this.owner.owner._id + "-jobdesigner-dialog-addnewoption-active").is(":checked")
                                    }, {
                                        "key" : "value",
                                        "value" : $("#" + _this.owner.owner._id + "-jobdesigner-dialog-addnewoption-value").val()
                                    },
                                    // {"key":"group",
                                    // "value":$("#"+_this.owner.owner._id+"-jobdesigner-dialog-addnewoption-group").val()},

                                    // important: last step is to rename the
                                    // option itself ...
                                    {
                                        "key" : "name",
                                        "value" : $("#" + _this.owner.owner._id + "-jobdesigner-dialog-addnewoption-name").val()
                                    } ];

                                    _this.owner.ajax.modifyOption({
                                        name : currentElement["Option"],
                                        values : newValues
                                    }, dfd);

                                    $(this).dialog("close");
                                },
                                Cancel : function() {
                                    $(this).dialog("close");
                                }
                            },
                            close : function(event, ui) {
                                _this.clearAvailableOptionsDialog();
                            }
                        });

                        // var dfd = jQuery.Deferred();
                        // dfd.done(function(args){_this.refreshView(args);});

                        // _this.owner.ajax.removeParameterRanges(selected,
                        // dfd);
                    }
                });

                // Parameter ranges

                var dfd = jQuery.Deferred();
                dfd.done(function(args) {
                    _this.refreshView(args);
                });
                _this.owner.ajax.getListOfParameterRanges(dfd);

                // connect the circle plus icon
                $("#" + this.owner.owner._id + "-jobdesigner-parameterrangesHeader .ui-icon-circle-plus").click(
                        function() {
                            // create the dialog
                            $("#" + _this.owner.owner._id + "-jobdesigner-dialog-parameterranges").dialog(
                                    {
                                        title : "Add a parameter range",
                                        resizable : true,
                                        height : 500,
                                        width : "30%",
                                        modal : false,
                                        buttons : {
                                            "Add" : function() {
                                                var dfd = jQuery.Deferred();
                                                dfd.done(function(args) {
                                                    _this.refreshView(args);
                                                });

                                                // do not use the return array
                                                // from split() directly as it
                                                // makes it easier to handle
                                                // conversion or user input
                                                // errors...
                                                var values = [];
                                                $.each($("#" + _this.owner.owner._id + "-jobdesigner-dialog-parameterranges-values").val()
                                                        .replace(/,\s+/g, ",").split(","), function() {
                                                    values.push(this);
                                                });

                                                var pr = {
                                                    name : $("#" + _this.owner.owner._id + "-jobdesigner-dialog-parameterranges-name").val(),
                                                    active : $("#" + _this.owner.owner._id + "-jobdesigner-dialog-parameterranges-active").is(":checked"),
                                                    values : values,
                                                    script : $("#" + _this.owner.owner._id + "-jobdesigner-dialog-parameterranges-script").val()
                                                };

                                                var dfd2 = jQuery.Deferred();
                                                dfd2.done(function(args) {
                                                    _this.refreshView(args);
                                                });

                                                _this.owner.ajax.addParameterRange(pr.name, pr.active, pr.values, pr.script, dfd2);

                                                $(this).dialog("close");
                                            },
                                            Cancel : function() {
                                                $(this).dialog("close");
                                            }
                                        },
                                        close : function(event, ui) {
                                            _this.clearParameterRangeDialog();
                                        }
                                    });
                        });

                // connect the circle minus icon
                $("#" + this.owner.owner._id + "-jobdesigner-parameterrangesHeader .ui-icon-circle-minus").click(function() {

                    var selected = _this.getFirstColumnValuesOfSelectedRows("#" + _this.owner.owner._id + "-jobdesigner-ParameterRangesTable");

                    if (selected.length > 0) {
                        var dfd = jQuery.Deferred();
                        dfd.done(function(args) {
                            _this.refreshView(args);
                        });

                        _this.owner.ajax.removeParameterRanges(selected, dfd);
                    }
                });

                // connect the pencil icon (modify)
                $("#" + this.owner.owner._id + "-jobdesigner-parameterrangesHeader .ui-icon-pencil").click(
                        function() {

                            var selected = _this.getColumnValuesOfSelectedRows("#" + _this.owner.owner._id + "-jobdesigner-ParameterRangesTable");

                            if (selected.length > 0) {
                                var currentElement = selected[0];

                                _this.clearParameterRangeDialog();

                                $("#" + _this.owner.owner._id + "-jobdesigner-dialog-parameterranges-active").prop('checked', currentElement["Active"]);

                                $("#" + _this.owner.owner._id + "-jobdesigner-dialog-parameterranges-name").val(currentElement["Name"]);
                                $("#" + _this.owner.owner._id + "-jobdesigner-dialog-parameterranges-values").val(currentElement["Values"]);
                                $("#" + _this.owner.owner._id + "-jobdesigner-dialog-parameterranges-script").val(currentElement["Script"]);

                                // create the modify dialog
                                $("#" + _this.owner.owner._id + "-jobdesigner-dialog-parameterranges").dialog(
                                        {
                                            title : "Modify a parameter range",
                                            resizable : true,
                                            height : 500,
                                            width : "30%",
                                            modal : false,
                                            buttons : {
                                                "Modify" : function() {
                                                    var dfd = jQuery.Deferred();
                                                    dfd.done(function(args) {
                                                        _this.refreshView(args);
                                                    });

                                                    // do not use the return
                                                    // array from split()
                                                    // directly as it makes it
                                                    // easier to handle
                                                    // conversion or user input
                                                    // errors...
                                                    var values = [];
                                                    $.each($("#" + _this.owner.owner._id + "-jobdesigner-dialog-parameterranges-values").val().replace(/,\s+/g,
                                                            ",").split(","), function() {
                                                        values.push(this);
                                                    });

                                                    var newValues = [ {
                                                        "key" : "active",
                                                        "value" : $("#" + _this.owner.owner._id + "-jobdesigner-dialog-parameterranges-active").is(":checked")
                                                    }, {
                                                        "key" : "values",
                                                        "value" : values
                                                    }, {
                                                        "key" : "script",
                                                        "value" : $("#" + _this.owner.owner._id + "-jobdesigner-dialog-parameterranges-script").val()
                                                    },
                                                    // important: last step is
                                                    // to rename the parameter
                                                    // range ...
                                                    {
                                                        "key" : "name",
                                                        "value" : $("#" + _this.owner.owner._id + "-jobdesigner-dialog-parameterranges-name").val()
                                                    }, ];

                                                    _this.owner.ajax.modifyParameterRange({
                                                        name : currentElement["Name"],
                                                        values : newValues
                                                    }, dfd);

                                                    $(this).dialog("close");
                                                },
                                                Cancel : function() {
                                                    $(this).dialog("close");
                                                }
                                            },
                                            close : function(event, ui) {
                                                _this.clearParameterRangeDialog();
                                            }
                                        });

                                // var dfd = jQuery.Deferred();
                                // dfd.done(function(args){_this.refreshView(args);});

                                // _this.owner.ajax.removeParameterRanges(selected,
                                // dfd);
                            }
                        });

                // connect the icons to steer the add parameter range expert
                // view
                $("#" + this.owner.owner._id + "-jobdesigner-dialog-parameterranges-ExpertViewToggle").click(function() {
                    $(_this).toggleClass("ui-icon-plusthick").toggleClass("ui-icon-minusthick");

                    $.each($(".jobdesigner-dialog-parameterrangesExpertView"), function() {
                        if (this.style.display == "")
                            this.style.display = "none";
                        else
                            this.style.display = "";
                    });
                });

                // Option decorators
                var dfd = jQuery.Deferred();
                dfd.done(function(args) {
                    _this.refreshView(args);
                });

                this.owner.ajax.getListOfOptionDecorators(dfd);

                // connect the circle plus icon

                $("#" + this.owner.owner._id + "-jobdesigner-decoratorsHeader .ui-icon-circle-plus").click(
                        function() {
                            // initialize the dialog

                            _this.updateOptionDecoratorDialog("select");

                            // create the dialog
                            $("#" + _this.owner.owner._id + "-jobdesigner-dialog-decorators").dialog(
                                    {
                                        resizable : true,
                                        height : 500,
                                        width : "30%",
                                        modal : false,
                                        buttons : {
                                            "Add" : function() {
                                                var dfd = jQuery.Deferred();
                                                dfd.done(function(args) {
                                                    _this.refreshView(args);
                                                });
                                                var values = []; // FIXME:
                                                // Currently
                                                // not
                                                // implemented
                                                // in view
                                                _this.owner.ajax.addOptionDecorator($("#" + _this.owner.owner._id + "-jobdesigner-dialog-decorators-name")
                                                        .val(), $("#" + _this.owner.owner._id + "-jobdesigner-dialog-decorators-script").val(), dfd);

                                                $(this).dialog("close");
                                            },
                                            Cancel : function() {
                                                $(this).dialog("close");
                                            }
                                        },
                                        close : function(event, ui) {
                                            _this.clearOptionDecoratorDialog();
                                        }
                                    });
                        });

                // and connect the selectbox within the dialog
                $("#" + this.owner.owner._id + "-jobdesigner-dialog-decorators-parameterrangeSelect").change(function() {
                    console.log("changed selectbox");
                    if ($(this).val() != "default") {
                        var textbox = $("#" + _this.owner.owner._id + "-jobdesigner-dialog-decorators-script");
                        textbox.text(textbox.text() + "\n" + ("return valueDict['" + $(this).val() + "']"));
                    }
                });

                // connect the circle minus icon
                $("#" + this.owner.owner._id + "-jobdesigner-decoratorsHeader .ui-icon-circle-minus").click(function() {

                    var selected = _this.getFirstColumnValuesOfSelectedRows("#" + _this.owner.owner._id + "-jobdesigner-decoratorsTable");

                    if (selected.length > 0) {
                        var dfd = jQuery.Deferred();
                        dfd.done(function(args) {
                            _this.refreshView(args);
                        });

                        _this.owner.ajax.removeOptionDecorators(selected, dfd);
                    }
                });

                // connect the pencil icon (modify)
                $("#" + this.owner.owner._id + "-jobdesigner-decoratorsHeader .ui-icon-pencil").click(function() {

                    var selected = _this.getColumnValuesOfSelectedRows("#" + _this.owner.owner._id + "-jobdesigner-decoratorsTable");

                    if (selected.length > 0) {
                        var currentElement = selected[0];

                        _this.updateOptionDecoratorDialog("select");

                        // _this.owner.ajax.addOptionDecorator($("#"+_this.owner.owner._id+"-jobdesigner-dialog-decorators-name").val(),
                        // $("#"+_this.owner.owner._id+"-jobdesigner-dialog-decorators-script").val(),
                        // dfd);
                        $("#" + _this.owner.owner._id + "-jobdesigner-dialog-decorators-name").val(currentElement["Name"]);
                        // $("#"+_this.owner.owner._id+"-jobdesigner-dialog-parameterranges-values").val(currentElement["Values"]);
                        // $("#"+_this.owner.owner._id+"-jobdesigner-dialog-parameterranges-script").val(currentElement["Script"]);

                        // create the modify dialog
                        $("#" + _this.owner.owner._id + "-jobdesigner-dialog-decorators").dialog({
                            title : "Modify a variant of a parameter range",
                            resizable : true,
                            height : 500,
                            width : "30%",
                            modal : false,
                            buttons : {
                                "Modify" : function() {
                                    var dfd = jQuery.Deferred();
                                    dfd.done(function(args) {
                                        _this.refreshView(args);
                                    });

                                    // do not use the return array from split()
                                    // directly as it makes it easier to handle
                                    // conversion or user input errors...
                                    /*
                                     * var values = [];
                                     * $.each($("#"+_this.owner.owner._id+"-jobdesigner-dialog-decorators-values").val().replace(/,\s+/g,
                                     * ",").split(","), function(){
                                     * values.push(this); });
                                     */

                                    var newValues = [
                                    // {"key":"active",
                                    // "value":$("#"+_this.owner.owner._id+"-jobdesigner-dialog-parameterranges-active").is(":checked")},
                                    // {"key":"values", "value":values},
                                    // {"key":"script",
                                    // "value":$("#"+_this.owner.owner._id+"-jobdesigner-dialog-parameterranges-script").val()},
                                    // important: last step is to rename the
                                    // parameter range ...
                                    {
                                        "key" : "name",
                                        "value" : $("#" + _this.owner.owner._id + "-jobdesigner-dialog-decorators-name").val()
                                    }, ];

                                    _this.owner.ajax.modifyOptionDecorator({
                                        name : currentElement["Name"],
                                        values : newValues
                                    }, dfd);

                                    $(this).dialog("close");
                                },
                                Cancel : function() {
                                    $(this).dialog("close");
                                }
                            },
                            close : function(event, ui) {
                                _this.clearOptionDecoratorDialog();
                            }
                        });

                        // var dfd = jQuery.Deferred();
                        // dfd.done(function(args){_this.refreshView(args);});

                        // _this.owner.ajax.removeParameterRanges(selected,
                        // dfd);
                    }
                });

                // Active options

                // parameter ranges table
                /*
                 * $("#"+this.owner.owner._id+"-jobdesigner-ParameterRangesTable").tablesorter({
                 * widthFixed: true, widgets : ['zebra'] });
                 */

                // decorator table
                /*
                 * $("#"+this.owner.owner._id+"-jobdesigner-decoratorsTable").tablesorter({
                 * widthFixed: true, widgets : ['zebra'] });
                 */

                // $("#"+this.owner.owner._id+"-jobdesigner-availableoptionsTable").treeTable();
                this.initializeAvailableoptionsTable("#" + this.owner.owner._id + "-jobdesigner-availableoptionsTable");

                // Configure draggable nodes
                $("#" + this.owner.owner._id + "-jobdesigner-availableoptionsTable .file, " + "#" + this.owner.owner._id + "-availableoptionsTable .folder")
                        .draggable({
                            helper : "clone",
                            opacity : .75,
                            refreshPositions : true, // Performance?
                            revert : "invalid",
                            revertDuration : 300,
                            scroll : true
                        });

                $("#" + this.owner.owner._id + "-jobdesigner-availableoptionsTable .folder").each(function() {
                    $($(this).parents("tr")[0]).droppable({
                        accept : ".file, .folder",
                        drop : function(e, ui) {
                            $($(ui.draggable).parents("tr")[0]).appendBranchTo(this);
                        },
                        hoverClass : "accept",
                        over : function(e, ui) {
                            if (this.id != $(ui.draggable.parents("tr")[0]).id && !$(this).is(".expanded")) {
                                $(this).expand();
                            }
                        }
                    });
                });

                // Make visible that a row is clicked
                $("#" + this.owner.owner._id + "-jobdesigner-availableoptionsTable tbody tr").mousedown(function() {
                    $("tr.selected").removeClass("selected"); // Deselect
                    // currently
                    // selected rows
                    $(this).addClass("selected");
                });

                // Make sure row is selected when span is clicked
                $("#" + this.owner.owner._id + "-jobdesigner-availableoptionsTable tbody tr span").mousedown(function() {
                    $($(this).parents("tr")[0]).trigger("mousedown");
                });

                // initialization of available options
                var dfd = jQuery.Deferred();
                dfd.done(function(args) {
                    _this.refreshView(args);
                });

                this.owner.ajax.getListOfOptions(dfd);

                $("#" + this.owner.owner._id + "-submitButton").button({});
                $("#" + this.owner.owner._id + "-submitButton").click(function(event) {
                    var dfd = jQuery.Deferred();
                    dfd.done(function(args) {
                        var outputPath = "";
                        var pxlrun_arguments = "";

                        var jobs = [];
                        $.each(args.commandLines, function() {
                            jobs.push({
                                command : this,
                                arguments : [ pxlrun_arguments ],
                                outputPath : outputPath
                            });
                        });

                        var tabExtension_instance = Vispa.extensionManager.createInstance('jobmanagement', 'jobSubmissionTab', {
                            dfd : dfd,
                            jobs : jobs
                        });
                        // tabExtension_instance.show();
                    });
                    _this.owner.ajax.getCommandLines(dfd);

                });

                $("#" + this.owner.owner._id + "-cancelButton").button();
                $("#" + this.owner.owner._id + "-cancelButton").click(function(event) {
                    alert("clicked");
                });

                $("#" + this.owner.owner._id + "-resetButton").button();
                $("#" + this.owner.owner._id + "-resetButton").click(function(event) {
                    alert("clicked");
                });

                // some dummy settings
                $("#" + _this.owner.owner._id + "-jobdesigner-commandText").click(function() {
                    // $("#"+this.owner.owner._id+"-jobdesigner-commandText").blur();
                    $(this).focus();
                    // $('#'+this.owner.owner._id+'-jobdesigner-body').focus();
                });

                var dfd = jQuery.Deferred();
                dfd.done(function(args) {
                    _this.refreshView(args);
                });
                this.owner.ajax.getJobDesignerCommand(dfd);
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

            refreshView : function(args) {

                var _this = this;

                console.log("<-- begin refreshView:");

                if (!args) {
                    console.log("refreshView w/o args");
                    return false;
                } else {
                    console.log("<-- begin refreshView arguments:");
                    console.log(args);
                    console.log("end refreshView arguments -->");
                }

                // update the command input text field
                if (args.command) {
                    console.log("update command text field");
                    $("#" + this.owner.owner._id + "-jobdesigner-commandText").val(args.command);
                }

                if (args.parameterRangeList) {
                    console.log("update parameter range list table");
                    // clear all rows from existing table
                    $('#' + this.owner.owner._id + '-jobdesigner-ParameterRangesTable tr').not(function() {
                        if ($(this).has('th').length) {
                            return true
                        }
                    }).remove();

                    $.each(args.parameterRangeList, function() {
                        // and add all other rows
                        // <td title="'
                        // +this.script.replace(/(\r\n|\n|\r)/gm,"\n" )+
                        // '">'+this.script.replace(/(\r\n|\n|\r)/gm,
                        // "<br>")+'</td>\
                        var row = '<tr>\
    	 			<td>' + this.name + '</td>\
    	 			<td style="overflow: hidden; text-overflow: ellipsis;" title="'
                                + this.values + '">' + this.values + '</td>\
    	 			<td title="' + this.script + '">' + this.script + '</td>\
    	 			<td>'
                                + '<input type="checkbox" class="jobdesigner-ParameterRangesTableCheckbox" value="' + this.name + '" '
                                + ((this.active == true || this.active == "true" || this.active == "True") ? "checked='checked'" : "") + '>' + '</input>'
                                + '</td>\
    	 			</tr>', $row = $(row), resort = true;

                        $('#' + _this.owner.owner._id + '-jobdesigner-ParameterRangesTable').find('tbody').append($row).trigger('addRows', [ $row, resort ]);
                    });

                    // re-bind the checkboxes
                    $(".jobdesigner-ParameterRangesTableCheckbox").change(function(event) {
                        event.preventDefault();

                        var dfd = jQuery.Deferred();
                        dfd.done(function(args) {
                            _this.refreshView(args);
                        });

                        _this.owner.ajax.modifyParameterRange({
                            name : event.currentTarget.value,
                            values : [ {
                                "key" : "active",
                                "value" : event.currentTarget.checked
                            } ]
                        }, dfd);
                    });

                    this.addTableHover("#" + this.owner.owner._id + "-jobdesigner-ParameterRangesTable");
                    this.makeTableSelectable("#" + this.owner.owner._id + "-jobdesigner-ParameterRangesTable");
                }

                if (args.numJobs) {
                    console.log("update total number of jobs");
                    $("#" + this.owner.owner._id + "-jobdesigner-parameterrangesnumjobs").text("Total number of jobs: " + args.numJobs);
                }

                if (args.optionDecoratorList) {
                    console.log("update option decorator list table");
                    // clear all rows from existing table
                    $('#' + this.owner.owner._id + '-jobdesigner-decoratorsTable tr').not(function() {
                        if ($(this).has('th').length) {
                            return true
                        }
                    }).remove();

                    $.each(args.optionDecoratorList, function() {

                        // and add all other rows
                        var row = '<tr>\
    	 			<td>' + this.name + '</td>\
    	 			</tr>', $row = $(row), resort = true;

                        $('#' + _this.owner.owner._id + '-jobdesigner-decoratorsTable').find('tbody').append($row).trigger('addRows', [ $row, resort ]);
                    });

                    // add hover to rows of decorator table
                    this.addTableHover("#" + this.owner.owner._id + "-jobdesigner-decoratorsTable");

                    // make rows of parameter ranges table selectable
                    this.makeTableSelectable("#" + this.owner.owner._id + "-jobdesigner-decoratorsTable");
                }

                if (args.optionList) {
                    console.log("update option list tree");

                    // list of option decorators is needed to create the
                    // <select> within the tree. Re-get the list if not existing
                    var optionDecoratorNames = [];

                    if ((typeof args.optionDecoratorList) == "undefined") {
                        var dfd = jQuery.Deferred();
                        dfd.done(function(arguments) {
                            args.optionDecoratorList = arguments.optionDecoratorList;
                        });

                        this.owner.ajax.getListOfOptionDecorators(dfd, false);
                    }

                    $.each(args.optionDecoratorList, function(key, decorator) {
                        optionDecoratorNames.push(decorator.name);
                    });

                    // clear all elements from existing table
                    $("#" + this.owner.owner._id + "-jobdesigner-availableoptionsContent").find("tbody tr").remove().end();

                    var children = [];

                    // sort list of available folders
                    var full_optionList = [];
                    $.each(args.optionList, function(key, module) {
                        full_optionList.push(module);
                    });

                    full_optionList.sort(this.sortFolderAlphabetically);

                    // now fill all folders
                    $.each(full_optionList, function(key, module) {
                        if (module.length > 1) {
                            console.log("found multiple option elements");

                            var folder_children = [];
                            module.sort(this.sortChildrenAlphabetically);

                            $.each(module, function(key, option) {
                                folder_children.push({
                                    title : option.name,
                                    defaultValue : option.value,
                                    availableDecorators : optionDecoratorNames,
                                    decorator : option.decorator,
                                    isFolder : false,
                                    group : option.group,
                                    icon : false,
                                    optionString : option.optionString,
                                    select : option.active
                                });
                            });

                            children.push({
                                title : module[0].group,
                                isFolder : true,
                                key : module[0].group,
                                children : folder_children,
                                select : false
                            });
                        } else if (module.length > 0) {
                            console.log("found one option element");

                            var new_option = {
                                title : module[0].name,
                                isFolder : false,
                                group : module[0].group,
                                defaultValue : module[0].value,
                                availableDecorators : optionDecoratorNames,
                                decorator : module[0].decorator,
                                icon : false,
                                optionString : module[0].optionString,
                                select : module[0].active
                            };

                            if (module[0].group == "" || !module[0].group) {
                                children.push(new_option);
                            } else {
                                children.push({
                                    title : new_option.group,
                                    isFolder : true,
                                    key : new_option.group,
                                    children : [ new_option ],
                                    select : false
                                });
                            }
                        } else {
                            console.log("empty list of option elements");
                        }
                    });

                    var rows = this.getAvailableOptionsTableRows(children);
                    $.each(rows, function(index, current_row) {
                        $("#" + _this.owner.owner._id + "-jobdesigner-availableoptionsTable").find('tbody').append(current_row);
                    });
                    this.initializeAvailableoptionsTable("#" + this.owner.owner._id + "-jobdesigner-availableoptionsTable");

                    // $("#"+this.owner.owner._id+"-jobdesigner-availableoptionsContent").dynatree("getRoot").addChild(children);

                }

                console.log("end refreshView -->");
            },

            getAvailableOptionsTableRows : function(children, mother) {

                var new_mother = false;
                if (mother)
                    new_mother = mother;

                var _this = this;
                var rows = [];

                $.each(children, function(index, element) {

                    if (!element.isFolder) {
                        console.log("noFolder");

                        rows.push(_this.makeAvailableOptionsTableSingleRow(element, new_mother));
                    } else {
                        console.log("Folder");

                        rows.push(_this.makeAvailableOptionsTableSingleRow(element, new_mother));
                        var further_children = _this.getAvailableOptionsTableRows(element.children, element.title);
                        $.each(_this.getAvailableOptionsTableRows(element.children, element.title), function(index, folderchild) {
                            rows.push(folderchild);
                        });
                    }
                });

                return rows;
            },

            makeAvailableOptionsTableSingleRow : function(element, motherParameter) {
                var row = '';

                element.rowID = (element.title).replace('.', '').replace('#' + this.owner.owner._id + '-', '').replace('/', '').replace(/\s+/g, '');

                var availableDecorators = "";
                $.each((element.availableDecorators ? element.availableDecorators : []), function() {
                    availableDecorators += '<option value="' + this + '">';
                    availableDecorators += this;
                    availableDecorators += '</option>';
                });

                var mother = "";
                if (motherParameter)
                    mother = motherParameter.replace('.', '').replace('#' + this.owner.owner._id + '-', '').replace('/', '').replace(/\s+/g, '');

                if (mother != "")
                    row += '<tr id="node-' + element.rowID + '" class="child-of-node-' + mother + '">';
                else
                    row += '<tr id="node-' + element.rowID + '">';

                if (element.isFolder)
                    row += '<td><span class="folder">' + element.title + '</span></td>';
                else
                    row += '<td><span class="file">' + element.title + '</span></td>';

                if (element.select && !element.isFolder && element.select != "false")
                    row += '<td><input type="checkbox" class="availableOptionsCheckbox" checked="checked" name="' + element.title + '"></input></td>';
                else if (!element.isFolder)
                    row += '<td><input type="checkbox" class="availableOptionsCheckbox" name="' + element.title + '"></input></td>';
                else
                    row += "<td></td>";

                row += '<td>' + (element.defaultValue ? element.defaultValue : '') + '</td>';

                if (element.optionString)
                    row += "<td>" + element.optionString + "</td>";
                else
                    row += "<td></td>";

                //&& element.select
                if (!element.isFolder)
                {
                    if (availableDecorators != "")
                        row += "<td>" + "<select class='availableOptionsSelect' id='availableOptionsSelect" + element.rowID + "' name='" + element.title + "'>"
                                + availableDecorators + "</select></td>";
                    else if (availableDecorators == "") {
                        availableDecorators = '<option value="">add a parameter range</option>';
                        row += "<td>" + "<select class='availableOptionsSelect' id='availableOptionsSelect" + element.rowID + "' name='" + element.title + "'>"
                                + availableDecorators + "</select></td>";
                    }
                }
                else
                    row += "<td></td>";

                row += '</tr>';

                return row;
            },

            initializeAvailableoptionsTable : function(id) {
                var _this = this;

                $(id).treeTable({
                    indent : 15,
                    clickableNodeNames : true,
                    persist : true,
                    persistStoreName : "VISPAavailableOptionsTreeTable"
                });

                $(".availableOptionsSelect").hover(function() {
                    this.focus();
                });
                
                // connect the selectionmenus
                $(".availableOptionsSelect").change(function() {
                    var name = this.name;
                    var decoratorname = $(this).val();

                    var dfd = jQuery.Deferred();
                    dfd.done(function(args) {
                        _this.refreshView(args);
                    });

                    var newValues = [ {
                        "key" : "decorator",
                        "value" : decoratorname
                    } ];

                    _this.owner.ajax.modifyOption({
                        name : name,
                        values : newValues
                    }, dfd);
                });

                // connect the active checkboxes
                $(".availableOptionsCheckbox").change(function() {
                    console.log("changed");
                    var name = this.name;

                    var dfd = jQuery.Deferred();
                    dfd.done(function(args) {
                        _this.refreshView(args);
                    });

                    var newValues = [ {
                        "key" : "active",
                        "value" : $(this).is(':checked')
                    } ];

                    _this.owner.ajax.modifyOption({
                        name : name,
                        values : newValues
                    }, dfd);
                });

                this.addTableHover(id);
                this.makeTableSelectable(id);
            },

            // add hover to rows of parameter ranges table
            addTableHover : function(tableid) {
                // add hover to rows of decorator table
                $(tableid).find('tbody tr').has(':not(th)').hover(function() {
                    if (!$(this).hasClass("parent")) {
                        if (!$(this).hasClass("ui-state-hover"))
                            $(this).addClass("ui-state-hover");
                    }
                }, function() {
                    if (!$(this).hasClass("parent")) {
                        if (!this.selectedRow)
                            $(this).removeClass("ui-state-hover");
                    }
                });
            },

            // make rows of parameter ranges table selectable
            makeTableSelectable : function(tableid) {
                var multiselect = false;
                
                var _this = this;
                $(tableid).find('tbody tr').has(':not(th)').click(function(e) {
                    if (!$(this).hasClass("parent")) {
                        if (!this.selectedRow) {
                            if (!multiselect) {// deselect all other rows
                                $.each($(tableid).find('tbody tr').has(':not(th)'), function(index, element) {
                                    element.selectedRow = false;
                                    $(element).removeClass("ui-state-hover");
                                });
                            }

                            this.selectedRow = true;
                            $(this).mouseenter();
                        } else {
                            this.selectedRow = false;
                            $(this).mouseleave();
                        }
                    }
                });
            },

            getFirstColumnValuesOfSelectedRows : function(tableid) {
                var children = [];

                var selectedRows = $(tableid).find('tr').has(':not(th)').filter(function(index) {
                    return (this.selectedRow == true);
                });

                $.each(selectedRows, function() {
                    children.push(this.cells[0].textContent);
                });

                return children;
            },

            getPathToXML : function(id) {
                var xml = "";

                var tableid = "#" + this.owner.owner._id + "-jobdesigner-availableoptionsTable";
                var rows = $(tableid).find('tr').has(':not(th)').filter(function(index) {
                    return (this.cells[0].textContent == id);
                });

                if (rows.length > 0)
                    xml = rows[0].cells[0].textContent;

                return xml;
            },

            getColumnValuesOfSelectedRows : function(tableid) {
                var rows = [];
                var headers = [];

                $.each($(tableid).find('th'), function(index, element) {
                    headers.push(element.textContent);
                });

                // console.log(headers);

                var selectedRows = $(tableid).find('tr').has(':not(th)').filter(function(index) {
                    return (this.selectedRow == true);
                });

                $.each(selectedRows, function(indexrow, row) {
                    var current_row = {};
                    $.each(headers, function(indexheader, header) {
                        current_row[header] = row.cells[indexheader].textContent;

                        // test if there are any checkboxes
                        if (current_row[header] == "" && row.cells[indexheader].children.length > 0 && row.cells[indexheader].children[0].type == "checkbox") {
                            current_row[header] = row.cells[indexheader].children[0].checked;
                        }
                    });

                    rows.push(current_row);
                });

                return rows;
            },

            sortChildrenAlphabetically : function(a, b) {
                if (a.name < b.name) {
                    return -1;
                }

                if (a.name > b.name) {
                    return 1;
                }

                return 1;
            },

            sortFolderAlphabetically : function(a, b) {
                if (a.length == 0 && b.length > 0) {
                    return -1;
                } else if (b.length == 0 && a.length > 0) {
                    return 1;
                }
                if (a.length == 1 && b.length > 1) {
                    return -1;
                } else if (b.length == 1 && a.length > 1) {
                    return 1;
                } else if (b.length == 1 && a.length == 1) {
                    if (a[0].name < b[0].name) {
                        return -1;
                    }

                    if (a[0].name > b[0].name) {
                        return 1;
                    }
                } else if (b.length > 1 && a.length > 1) {
                    if (a[0].group < b[0].group) {
                        return -1;
                    }

                    if (a[0].group > b[0].group) {
                        return 1;
                    }
                } else {
                    console.log("Error .. should not happen ... while sorting list of folders ... trying to sort the following elements:");
                    console.log(a);
                    console.log(b);
                }

                return 1;
            },

            clearParameterRangeDialog : function() {
                $("#" + this.owner.owner._id + "-jobdesigner-dialog-parameterranges-name").val("");
                $("#" + this.owner.owner._id + "-jobdesigner-dialog-parameterranges-active").prop('checked', true);
                $("#" + this.owner.owner._id + "-jobdesigner-dialog-parameterranges-valuespreview").text("");
                $("#" + this.owner.owner._id + "-jobdesigner-dialog-parameterranges-script").val("");
                $("#" + this.owner.owner._id + "-jobdesigner-dialog-parameterranges-values").val("");
            },

            clearOptionDecoratorDialog : function() {
                $("#" + this.owner.owner._id + "-jobdesigner-dialog-decorators-name").val("");
                $("#" + this.owner.owner._id + "-jobdesigner-dialog-decorators-script").val("");
                $('#' + this.owner.owner._id + '-jobdesigner-dialog-decorators-parameterrangeSelect').find('option').remove().end();

                $('#' + this.owner.owner._id + '-jobdesigner-dialog-decorators-parameterrangeSelect').append(
                        '<option value="default">Select parameter range to insert return statement</option>');
                $("#" + this.owner.owner._id + "-jobdesigner-dialog-decorators-parameterrangeSelect").val(
                        $("#" + this.owner.owner._id + "-jobdesigner-dialog-decorators-parameterrangeSelect option:first").val());

            },

            updateOptionDecoratorDialog : function(id) {
                var _this = this;

                if (id == "select") {
                    var existing_decorator = []

                    $.each($('#' + this.owner.owner._id + '-jobdesigner-dialog-decorators-parameterrangeSelect').find('option'), function() {
                        existing_decorator.push(this.textContent);
                    });

                    var dfd = jQuery.Deferred();
                    dfd.done(function(args) {
                        var returnValues = args;

                        var parameterRanges = returnValues.parameterRangeList;

                        if (returnValues)
                            parameterRanges = returnValues.parameterRangeList;
                        else
                            parameterRanges = {};

                        // list of all parameter range names
                        var parameterRangeList = [];

                        $.each(parameterRanges, function() {
                            parameterRangeList.push(this.name);
                        });

                        parameterRangeList.sort();

                        $.each(parameterRangeList, function(index, element) {
                            if ($.inArray(element, existing_decorator) == -1) {
                                $("#" + _this.owner.owner._id + "-jobdesigner-dialog-decorators-parameterrangeSelect").append(
                                        "<option value='" + element + "'>" + element + "</option>");
                                existing_decorator.push(element);
                            }
                        });

                    });
                    this.owner.ajax.getListOfParameterRanges(dfd);
                }
            },

            clearAvailableOptionsDialog : function() {
                $("#" + this.owner.owner._id + "-jobdesigner-dialog-addnewoption-group").val("");
                $("#" + this.owner.owner._id + "-jobdesigner-dialog-addnewoption-name").val("");
                $("#" + this.owner.owner._id + "-jobdesigner-dialog-addnewoption-value").val("");
                $("#" + this.owner.owner._id + "-jobdesigner-dialog-addnewoption-optionstring").val("");
                $("#" + this.owner.owner._id + "-jobdesigner-dialog-addnewoption-active").prop('checked', true);
            }
        });
