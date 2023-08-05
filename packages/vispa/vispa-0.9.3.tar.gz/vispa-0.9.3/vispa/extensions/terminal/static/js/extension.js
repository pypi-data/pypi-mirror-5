var TerminalExtension = ExtensionBase.extend({

	init : function(vispa) {
		this._super(vispa);
		var _this = this;

		this.name = 'terminal';

		this.factories = {
			full : new TerminalFactory(this._vispa)
		};
	}
});

var TerminalFactory = ExtensionFactoryFull.extend({

	init : function(vispa) {
		this._super(vispa);
		var _this = this;

		this.defaultConfig = {
			backgroundColor : {
				descr : 'The background color of this extension',
				select : [ 'white', 'red', 'blue' ],
				type : 'string',
				value : 'white'
			}
		};

		this.name = 'Terminal';
		this.constructor = TerminalContent;

		this.menuEntries = [ {
			label : 'new Terminal ...',
			icon : 'ui-icon-plus',
			callback : function() {
				_this._create();
			}
		} ];

	}
});

var TerminalContent = ExtensionContentFull.extend({

	init : function(vispa, config) {
		this._super(vispa, config);
		var _this = this;

		this.menuEntries = [ {
			label : 'My Id',
			icon : 'ui-icon-comment',
			callback : function() {
				$.Topic('msg.info').publish(_this._id);
			}
		} ];
	},

	getIdentifier : function() {
		return this.path;
	},

	render : function(node) {
		var _this = this;
		this.content = $('<div />').addClass('terminal-full-body')
		this.content.load(Vispa.urlHandler
				.dynamic('/extensions/terminal/static/html/content.html?'
						+ new Date().getTime()), function() {

			var terminal = this;
			var cmd = $(terminal).find(".terminal-command").addClass(
					'ui-widget');
			var sub = $(terminal).find(".terminal-submit").hide();
			var out = $(terminal).find(".terminal-output")
					.addClass('ui-widget');

			// send command when pressing enter
			cmd.keypress(function(event) {
				if (event.keyCode == 13) {
					sub.click();
				}
			});

			// create/open a new terminal session, returns id
			$.get(Vispa.urlHandler.dynamic('extensions/terminal/open'),
					{_wid: Vispa.workspaceManager.getWorkspace().id},
					function(terminalid) {

						// add on click action for submit button
						sub.click({
							terminalid : terminalid
						}, function(event) {
							// send command
							var command = encodeURI(cmd.val())
							$.get(Vispa.urlHandler
									.dynamic('extensions/terminal/command'), {
								_wid: Vispa.workspaceManager.getWorkspace().id,
								id : event.data.terminalid,
								command : command
							});
							cmd.val('');
						});

						// poll output
						var interval = setInterval(function() {
							$.get(Vispa.urlHandler
									.dynamic('extensions/terminal/output'), {
								_wid: Vispa.workspaceManager.getWorkspace().id,
								id : terminalid
							}, function(lines) {
								var output = $(terminal).find(
										".terminal-output")
								for ( var i = 0; i < lines.length; i++) {
									output.append("<div class='terminal-line'>"
											+ lines[i] + "</div");
								}

							});
						}, 500);

						// close remote terminal, clear polling
						_this.beforeClose = function() {
							$.get(Vispa.urlHandler
									.dynamic('extensions/terminal/close'), {
								id : terminalid
							});
							window.clearInterval(interval);
							return true;
						}
					});
		});
		$(node).append(this.content);
		return this;
	},

});

$(function() {
	// register the Extension
	$.Topic('extman.register').publish(TerminalExtension);
});