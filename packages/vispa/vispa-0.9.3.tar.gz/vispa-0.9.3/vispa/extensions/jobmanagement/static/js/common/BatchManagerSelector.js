var BatchManagerSelector = Class
        .extend({

            init : function(args) {
                this.options = (args.hasOwnProperty("options") ? args.options : []);
                this.description = (args.hasOwnProperty("description") ? args.description : false);

                this.guid = (args.hasOwnProperty("guid") ? args.guid : guid());
                this.jid = "#" + this.guid;

                this.identifier = (args.hasOwnProperty("identifier") ? args.identifier : "BatchManagerSelector");
                this.changeCallback = (args.hasOwnProperty("changeCallback") ? args.changeCallback : null);

                console.debug("DEBUG BatchManagerSelector: Created BatchManagerSelector with id '" + this.guid + "'");
                this.batchManagerSelector = false;
            },

            initialize : function(append) // options = [{"name":"foo",
            // "description":""}]
            {
                var _this = this;
                // console.log(this.options);
                if (!this.batchManagerSelector)
                    this.batchManagerSelector = this.create();

                if (append) {
                    if (append.length == 0)
                        console
                                .error("ERROR BatchManagerSelector: Did not found object where batchmanager selector div should be appended to ... parameter is appendTo='"
                                        + appendTo + "'");
                    else {
                        $(append).append(this.batchManagerSelector);

                        // append options
                        var myoptions = "";
                        $.each(this.options, function(index, option) {
                            var name = (option.hasOwnProperty("name") ? option.name : "");
                            myoptions += "<option value=" + name + ">" + name + "</option>";
                        });

                        $(this.jid).append(myoptions);

                        $(this.jid).selectBoxIt({
                            theme : "jqueryui"
                        });

                        // append descriptions
                        if (this.description) {
                            var descriptions = "";

                            $.each(this.options, function(index, option) {
                                descriptions += "<div id=" + _this.jid + "-" + option.name + "-DESCRIPTION>";
                                descriptions += option.description;
                                descriptions += "</div>";
                            });
                            $(descriptions).insertAfter(this.jid + "SelectBoxItContainer");

                            // initially hide all descriptions
                            this.hideAllDescriptions();
                        }

                    }
                } else
                    console
                            .error("ERROR BatchManagerSelector: Did not found object where batchmanager selector div should be appended to ... parameter is empty");

                this.postFillProcessing();

                return true;
            },

            hideAllDescriptions : function() {
                var _this = this;

                $('div').filter(function() {
                    return this.id.match(_this.guid + ".*?-DESCRIPTION");
                }).hide();
            },

            showDescription : function(option) {
                var _this = this;

                $('div').filter(function() {
                    return this.id.match(_this.guid + ".*?-" + option + "-DESCRIPTION");
                }).show();
            },

            setOptions : function(options) {
                this.options = options;
            },

            getOptions : function() {
                return this.options;
            },

            postFillProcessing : function() {
                if (this.changeCallback)
                    this.connectChange(this.changeCallback);
            },

            create : function() {
                this.batchManagerSelector = "";

                this.batchManagerSelector += '<div id="' + this.guid + 'DIV">';
                this.batchManagerSelector += '<select id="' + this.guid + '">';

                this.batchManagerSelector += '</select>';
                this.batchManagerSelector += '</div>';

                return this.batchManagerSelector;
            },

            connectChange : function(callback) {
                if (this.batchManagerSelector) {
                    $(this.jid).change({
                        identifier : this.identifier
                    }, callback);
                }
            }

        });