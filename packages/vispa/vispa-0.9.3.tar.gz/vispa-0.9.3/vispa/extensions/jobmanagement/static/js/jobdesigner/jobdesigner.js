var JobDesigner = Class.extend({

	init : function(owner)
	{
	    // the owner is the extension content
	    this.owner = owner;
	    
	    // an ajax handler for this process extension
		this.ajax = new JobDesignerAjaxHandler(this);
	    
		// the datastore object (model)
		this.dataModelAvailableOptions = new DataModel(this);
		
	    // the view handler
	    this.view = new JobDesignerTabView(this);
	},

});