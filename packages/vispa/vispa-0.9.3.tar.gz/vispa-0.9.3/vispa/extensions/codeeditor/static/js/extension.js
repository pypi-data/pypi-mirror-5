var CodeEditorExtension = ExtensionBase.extend({

    init: function() {
        this._super();
        var _this = this;

        this.name = 'codeeditor';

        this.factories = {
            full: new CodeEditorFullFactory()
        };
    }
});

var CodeEditorFullFactory = ExtensionFactoryFull.extend({

    init: function() {
        this._super();
        var _this = this;

        this.defaultConfig = {
            theme: {
                descr: 'The Ace theme',
                type: 'string',
                select: ['chrome', 'eclipse', 'monokai', 'textmate', 'xcode'],
                value: 'textmate'
            },
            fontSize: {
                descr: 'The editor\'s font size',
                type: 'integer',
                select: [8, 10, 12, 13, 14, 16, 18, 20],
                value: 12
            },
            showInvisibles: {
                descr: 'Show invisible characters?',
                type: 'boolean',
                value: false
            },
            indentationGuides: {
                descr: 'Show indentation guides?',
                type: 'boolean',
                value: true
            },
            ruler: {
                descr: 'The position of the rulter. 0 means \'no ruler\'.',
                type: 'integer',
                select: [0, 60, 80, 100, 120, 140, 180],
                value: 80
            }
        };
        this.preferenceSettings = {
            entryOrder: ['theme', 'fontSize', 'ruler', 'showInvisibles', 'indentationGuides']
        };

        this.name = 'CodeEditor';
        this.constructor = CodeEditorFullContent;

        this.fileHandlers = {}
        var fileExtensions = ['txt', 'py', 'c', 'cc', 'cpp', 'h', 'hh', 'xml', 'js', 'css', 'sh']
        $.each(fileExtensions, function(i, ext) {
            _this.fileHandlers[ext] = {
                priority: 1,
                callback: function(path) {
                    _this._create(path);
                }
            }
        });
    }
});

var CodeEditorFullContent = ExtensionContentFull.extend({

    init: function(config, path) {
        this._super(config);
        var _this = this;

        this.menuEntries = [
            {
                label: 'Save',
                icon: 'ui-icon-disk',
                callback: function() {
                    _this.editor.save();
                }
            }
        ];

        this.nodes = {
            aceNode: null
        };

        this.editor = new CodeEditor(this, path);
    },

    applyConfig: function() {
        // theme
        this.editor.ace.setTheme($.Helpers.strFormat('ace/theme/{0}', this._config.theme));
        // fontSize
        this.editor.ace.setFontSize(this._config.fontSize);
        // showInvisibles
        this.editor.ace.setShowInvisibles(this._config.showInvisibles);
        // indentationGuides
        this.editor.ace.setDisplayIndentGuides(this._config.indentationGuides);
        // ruler
        this.editor.ace.setShowPrintMargin( !! this._config.ruler);
        this.editor.ace.setPrintMarginColumn(this._config.ruler);
        return this;
    },

    getIdentifier: function() {
        return this.editor.workflow.path;
    },

    getTitle: function() {
        var title = this.editor.workflow.path.split('/').pop();
        if (this.editor.workflow.modified) {
            title = '&bull;' + title;
        }
        return title;
    },

    render: function(node) {
        this.nodes.aceNode = $('<div />')
            .addClass('codeeditor-ace-instance')
            .css('position', 'absolute')
            .get(0);
        $(node).append(this.nodes.aceNode);
        return this;
    },

    ready: function() {
        this.editor.ready();
        this.applyConfig();
        return this;
    },

    afterShow: function() {
        this.editor.checkMTime();
        return this;
    }
});

$(function() {
    // register the Extension
    $.Topic('extman.register').publish(CodeEditorExtension);
});