var SelectableTable = Class.extend({

    init : function(args) {
        this.guid = (args.hasOwnProperty("guid") ? args.guid : guid());
        this.multiselect = (args.hasOwnProperty("multiselect") ? args.multiselect : false);
        this.columns = (args.hasOwnProperty("columns") ? args.columns : []);
        this.blindColumns = (args.hasOwnProperty("blindColumns") ? args.blindColumns : []);
        this.clickCallback = (args.hasOwnProperty("clickCallback") ? args.clickCallback : null);
        this.classes = (args.hasOwnProperty("classes") ? args.classes : "");
        this.bodyclasses = (args.hasOwnProperty("bodyclasses") ? args.bodyclasses : "");
        this.headclasses = (args.hasOwnProperty("headclasses") ? args.headclasses : "");
        this.treeTable= (args.hasOwnProperty("treeTable") ? args.treeTable : false);

        this.jid = "#" + this.guid;
        console.debug("DEBUG SelectableTable: Created SelectableTable with id '" + this.guid + "'");

        this.table = false;
        this.toogleSelect = false;
    },

    initializeTable : function(append) {
        if (!this.table)
            this.table = this.createTable();

        if (append) {
            if (append.length == 0)
                console.error("ERROR SelectableTable: Did not found object where table should be appended to ... parameter is appendTo='" + appendTo + "'");
            else
                $(append).append(this.table);
        } else
            console.error("ERROR SelectableTable: Did not found object where table should be appended to ... parameter is empty");

        if (this.treeTable)
        {
            $(this.jid).treeTable({
                indent : 15,
                clickableNodeNames : true,
                persist : false,
                persistStoreName : this.guid
            });
        }
        else
        {
            if (!$(this.jid).hasClass("tablesorter"))
            {
                $(this.jid).removeClass("mytablestyle");
                $(this.jid).addClass("tablesorter");
            }
            
            // Extend the themes to change any of the default class names ** NEW **
              $.extend($.tablesorter.themes.jui, {
                    // change default jQuery uitheme icons - find the full list of icons here: http://jqueryui.com/themeroller/ (hover over them for their name)
                    table      : 'ui-widget ui-widget-content ui-corner-all', // table classes
                    header     : 'ui-widget-header ui-corner-all ui-state-default', // header classes
                    footerRow  : '',
                    footerCells: '',
                    icons      : 'ui-icon', // icon class added to the <i> in the header
                    sortNone   : 'ui-icon-carat-2-n-s',
                    sortAsc    : 'ui-icon-carat-1-n',
                    sortDesc   : 'ui-icon-carat-1-s',
                    active     : 'ui-state-active', // applied when column is sorted
                    hover      : 'ui-state-hover',  // hover class
                    filterRow  : '',
                    even       : 'ui-widget-content', // odd row zebra striping
                    odd        : 'ui-widget-content'   // even row zebra striping //ui-state-default
                  });
      
            $(this.jid).tablesorter({
                theme : 'jui', // theme "jui" and "bootstrap" override the uitheme widget option in v2.7+
                headerTemplate : '{content} {icon}', // needed to add icon for jui theme
//                sortList: [[0,0]],
//              widgets : ['uitheme', 'zebra'],
                widgets : ['uitheme'],
                widgetOptions : {
                    // zebra striping class names - the uitheme widget adds the class names defined in
                    // $.tablesorter.themes to the zebra widget class names
                    zebra   : ["even", "odd"]

                    // set the uitheme widget to use the jQuery UI theme class names
                    // ** this is now optional, and will be overridden if the theme name exists in $.tablesorter.themes **
//                     uitheme : 'jui'
                  }
            });
        }
        
        this.postFillProcessing();

        return true;
    },

    postFillProcessing : function() {
        this.addTableHover();
        this.makeTableSelectable();
    },

    createTable : function() {
        var _this = this;

        var header = "<table class='" + this.classes + "' id='" + this.guid + "'>\
		  <thead class='" + this.headclasses + "'>\
	    <tr>";

        var columns = "";
        $.each(this.columns, function(index, column) {
            if (_this.blindColumns.indexOf(column) == -1)
                columns += "<th>";
            else
                columns += '<th style="display:none">';

            columns += column;
            columns += "</th>";
        });

        var footer = "</tr>\
			  </thead>\
			  <tbody class='" + this.bodyclasses + "'>\
			  </tbody>\
			</table>";

        this.table = header + columns + footer;

        return this.table;
    },

    // add hover to rows of table
    addTableHover : function() {
        // add hover to rows of decorator table
        $(this.jid).find('tbody tr').has(':not(th)').hover(function() {
            if (!$(this).hasClass("ui-state-hover"))
                $(this).addClass("ui-state-hover");
        }, function() {
            if (!this.selectedRow)
                $(this).removeClass("ui-state-hover");
        });
    },

    // make rows selectable
    makeTableSelectable : function() {
        var _this = this;
        $(this.jid).find('tbody tr').has(':not(th)').click(function(e) {
            if (!$(this).hasClass("parent")) {
                if (!this.selectedRow) {
                    if (!this.multiselect) {// deselect all other rows
                        $.each($(_this.jid).find('tbody tr').has(':not(th)'), function(index, element) {
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

            var obj = {};
            $.each(e.currentTarget.cells, function(index, element) {
                obj[_this.columns[index]] = element.textContent
            });

            _this.clickCallback(obj);
        });
    },

    clearRows : function() {
        $(this.jid + ' tr').not(function() {
            if ($(this).has('th').length) {
                return true;
            }
        }).remove();
    },

    toggleRows : function() {
        this.selectAllRows(!this.toogleSelect);
    },

    selectAllRows : function(state) {
        var select = typeof state == 'undefined' ? false : state;

        $.each($(this.jid).find('tbody tr').has(':not(th)'), function(index, element) {
            element.selectedRow = select;
            if (select) {
                if (!$(element).hasClass("ui-state-hover"))
                    $(element).addClass("ui-state-hover");
            } else
                $(element).removeClass("ui-state-hover");
        });
        this.toogleSelect = select;
    },

    getSelectedRows : function() {
        var _this = this;
        // var columns = (typeof column == 'undefined' ? [] : columns);
        var returnValues = [];

        var selectedRows = $(this.jid).find('tr').has(':not(th)').filter(function(index) {
            return (this.selectedRow == true);
        });

        $.each(selectedRows, function() {
            var obj = {};
            $.each(this.cells, function(index, element) {
                obj[_this.columns[index]] = element.textContent
            });

            returnValues.push(obj);
        });

        return returnValues;
    },

    addRows : function(rows, resort) {
        
        var _this = this;

        var resort = typeof resort !== 'undefined' ? resort : true;

        $.each(rows, function(indexrow, element) {
            var row = '<tr>';
            $.each(_this.columns, function(indexcolumn, column) {
                if (_this.blindColumns.indexOf(column) == -1)
                    row += '<td>' + element[column] + '</td>';
                else
                    row += '<td style="display:none">' + element[column] + '</td>';
            });
            row += '</tr>';
            
            //FIXME: bug in tablesorter
            //$(_this.jid).find('tbody').append($(row)).trigger('addRows', [ $(row), resort]);
            $(_this.jid).find('tbody').append($(row)).trigger('update');

        });

      this.postFillProcessing();
    }
});