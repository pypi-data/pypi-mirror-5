var DataModel = Class.extend({
    // class caches the data

    init : function(owner) {
        // store the owner
        this.owner = owner;

        // stores the data .. list of associative arrays
        var data = $.makeArray([]);
    },

    addData : function(datalist) {
        var _this = this;

        $.each(datalist, function(index, dataset) {
            _this.data.push(dataset);
        });

        this.owner.fireCallback("update");
    },

    removeData : function(dataidlist, idkey) {
        var _this = this;
        var id = (typeof (idkey) == "undefined" ? "id" : idkey);

        $.each(dataidlist, function(index, dataid) {
            _this.data = $.grep(_this.data, function(value) {
                return value[id] != dataid;
            });
        });

        self.owner.fireCallback("update");
    },

    findData : function(dataid, idkey) {
        var _this = this;
        var id = (typeof (idkey) == "undefined" ? "id" : idkey);

        return ($.grep(_this.data, function(value) {
            return value[id] != dataid;
        }));
    },

    hasData : function(dataid, idkey) {
        var id = (typeof (idkey) == "undefined" ? "id" : idkey);

        return this.findData(dataid, id).length;
        // flat arrays: (jQuery.inArray(jobid, self.datra) != -1);
    },

    getData : function() {
        return this.data;
    },

    replaceData : function(data, idkey) {
        if (typeof (idkey) == "undefined") {
            console.debug("INFO DataModel: Using standard id 'id' as passed by the data ... ");
        } else {
            console.debug("INFO DataModel: Setting id '" + idkey + "' as id ... ");

            $.each(data, function(index, dataset) {
                if (typeof (dataset[idkey]) == "undefined") {
                    console.error("ERROR: Did not found key '" + idkey + "' for object:");
                } else {
                    dataset.id = dataset[idkey];
                }
            });
        }
        this.data = $.makeArray(data);
        this.owner.fireCallback("update");
    },

    updateData : function(datasets) {
        var _this = this;

        $.each(datasets, function(index, dataset) {
            var old_id = dataset.id;
            var new_data = dataset;

            var found = false;
            if (_this.hasData(old_id)) {
                $.each(_this.data, function(index, item) {
                    if (item.id == id) {
                        _this.data[index] = new_data;
                        found = true;
                    }
                });
            }
        });

        this.owner.fireCallback("update");
    },

    update : function() {
        this.owner.fireCallback("update");
    }
});
