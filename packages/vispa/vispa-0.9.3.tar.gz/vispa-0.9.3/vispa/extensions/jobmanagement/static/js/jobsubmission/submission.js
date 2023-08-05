var JobSubmission = Class.extend({

    init : function(owner) {
        // the owner is the extension content
        this.owner = owner;

        // an ajax handler for this process extension
        this.ajax = new JobSubmissionAjaxHandler(this);

        // the view handler
        this.view = new JobSubmissionTabView(this);
    }
});