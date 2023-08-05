var JobDashboard = Class.extend({

    init : function(owner) {

        // the owner is the extension content
        this.owner = owner;

        // an ajax handler for this process extension
        this.ajax = new JobDashboardAjaxHandler(this);

        // the view handler
        this.view = new JobDashboardView(this);

        // the datastore object (model)
        this.dataModel = new DataModel(this);

        // store callback methods
        this.callbacks = {
            "update" : []
        };
    },

    addCallback : function(id, callback) {
        if (!(id in this.callbacks)) {
            this.callbacks[id] = [];
        }

        this.callbacks[id].push(callback);
    },

    removeCallback : function(id, callback) {
        if (id in this.callbacks) {
            $.each(this.callbacks[id], function(key, callbacklist) {
                var list_index = callbacklist.indexOf(callback);
                if (list_index != -1) {
                    callbacklist.remove(list_index);
                    return true;
                }
            });
        }
        return false;
    },

    fireCallback : function(id) {
        console.debug("DEBUG Dashboard: fireCallback with id=" + id);

        $.each(this.callbacks, function(currentid, callbacklist) {
            if (currentid == id) {
                $.each(callbacklist, function(index, callback) {
                    callback();
                });
            }
        });
    }
});