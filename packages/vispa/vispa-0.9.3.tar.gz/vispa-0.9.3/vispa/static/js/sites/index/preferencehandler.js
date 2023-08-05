var PreferenceHandler = VispaModule.extend({

    init: function(config) {
        this.defaultConfig = {};
        this._super('preferenceHandler', this.defaultConfig, config);

        // attributes
        this.settings = {};
        this.workflow = {
            sectionOrder: [],
            entryOrders: {}
        };
        this.observables = {};
    },

    startup: function() {
        this.setupTopics();

        this.logger.debug('Started');
        return this;
    },

    applyConfig: function() {
        return this;
    },

    setupObservable: function(section, name, _config, _defaultConfig, _settings) {
        // section already present?
        var obs = this.observables[section] = this.observables[section] || {};
        // name already in use in this section
        if(obs[name]) {
            var msg = $.Helpers.strFormat("Observable '<b>{0}</b>' has already been set in section '<b>{1}</b>'!", name, section);
            $.Topic('msg.error').publish(msg);
            return;
        }
        var defaultSettings = {
            // entry title
            title: name,
            // either 'set' or 'ask'
            type: null,
            // the order-priority inside the section
            priority: 0,
            // a client-side pre-check function, that may return an error message or simply false
            // return true to propagate the changes
            // basic type checks are performed by default regarding the data in the defaultConfig
            check: function(obj){return true;},
            // the topic or function to be called when the changes should be submitted to the server
            // a jQuery.promise object is expected to be returned
            submit: null,
            // the topic or function to be called after changes took place
            apply: null,
            // names of entries that should not appear (however, they will be submitted)
            entryFilter: [],
            // names of entries on a list to create an order
            entryOrder: [],
            // text above the entries
            description: null,
            // jquery ui icon class for the icon in the header
            icon: 'ui-icon-wrench',
            // is this observable hidden?
            hidden: false,
            // capitalize the title?
            capitalizeTitle: true,
            // a container with arbitrary content, displayed with right-align in the title link
            titleActions: null,
            // additional buttons,
            buttons: []
        };
        obs[name] = {
            config: _config,
            defaultConfig: _defaultConfig,
            settings: $.extend(true, {}, defaultSettings, _settings)
        };

        // loop through defaultConfig and add 'hidden' configs to the entryFilter
        $.each(_defaultConfig, function(key, value) {
            if(value.hidden && $.inArray(key, obs[name].settings.entryFilter) < 0) {
                obs[name].settings.entryFilter.push(key);
            }
        });
        // set the entry order for this section
        var order = this.workflow.entryOrders[section] = this.workflow.entryOrders[section] || [];
        var hit = false;
        $.each(order, function(i, _name) {
            if(!hit && obs[name].settings.priority > obs[_name].settings.priority) {
                order.splice(i, 0, name);
                hit = true;
            }
        });
        if(!hit) {
            order.push(name);
        }
        // append the section to the section order
        if($.inArray(section, this.workflow.sectionOrder) < 0) {
            this.workflow.sectionOrder.push(section);
        }
        return this;
    },

    getObservable: function(section, name) {
        return this.observables[section][name];
    },

    removeObservable: function(section, name) {
        // delete the main entry
        delete this.observables[section][name];
        // delete the name from the entry orders
        var entryOrders = this.workflow.entryOrders[section];
        var idx = $.inArray(name, entryOrders);
        if (idx >= 0) {
            entryOrders.splice(idx, 1);
        }
        return this;
    },

    setSectionOrder: function(order) {
        if(order) {
            this.workflow.sectionOrder = order;
        }
        return this;
    },

    commit: function(section, name, obj, callback) {
        // behavior is type-dependent
        var type = this.getObservable(section, name).settings.type.toLowerCase();
        if(type == 'set') {
            return this.commitSet(section, name, obj, callback);
        } else if(type == 'ask') {
            return this.commitAsk(section, name, obj, callback);
        }
        var dfd = $.Deferred();
        dfd.reject();
        return dfd;
    },

    commitSet: function(section, name, obj, callback) {
        var dfd = $.Deferred();
        // perform the check first
        if(!this.check(section, name, obj)) {
            dfd.reject();
            return dfd;
        }
        var observable = this.getObservable(section, name);
        // just tell the server
        var submitFunc = observable.settings.submit;
        var isTopic = false;
        if(typeof(submitFunc) == 'string') {
            submitFunc = $.Topic(submitFunc).publishBack;
            isTopic = true;
        }
        // only tell the server when submitFunc is a function
        if($.isFunction(submitFunc)) {
            // handle notifications
            var logMsg = $.Helpers.strFormat('pushing \'{0}\' config ...', observable.settings.title);
            var logObj = $.Topic('msg.log').publishBack('info', {text: logMsg, icon: 'ui-icon-refresh'})[0]; 
            var promise = submitFunc(section, name, obj);
            if(isTopic) {
                promise = promise[0];
            }
            $.when(promise).then(function(response) {
                if(!response.success) {
                    logObj.update({
                        text: response.msg || $.Helpers.strFormat('\'{0}\' config push failed', observable.settings.title),
                        icon: 'ui-icon-alert'
                    });
                } else {
                    logObj.update({
                        text: $.Helpers.strFormat('\'{0}\' config pushed', observable.settings.title),
                        icon: 'ui-icon-arrowthickstop-1-n'
                    });
                }
            });
        }
        // copy the old data
        var old = $.extend(true, {}, observable.config);
        // perform the data change
        $.extend(true, observable.config, obj);
        // callback
        if($.isFunction(callback)) {
            callback();
        }
        // apply changes
        var applyFunc = observable.settings.apply;
        if(typeof(applyFunc) == 'string') {
            applyFunc = $.Topic(applyFunc).publish;
        }
        if($.isFunction(applyFunc)) {
            applyFunc(section, name, observable.config, old);
        }
        dfd.resolve();
        return dfd;
    },

    commitAsk: function(section, name, obj, callback) {
        var _this = this;
        var dfd = $.Deferred();
        // perform the check first
        // the check function also converts the values of obj
        if(!this.check(section, name, obj)) {
            dfd.reject();
            return dfd;
        }
        var observable = this.getObservable(section, name);
        // tell the server and wait for permission
        var submitFunc = observable.settings.submit;
        var isTopic = false;
        if(typeof(submitFunc) == 'string') {
            submitFunc = $.Topic(submitFunc).publishBack;
            isTopic = true;
        }
        // abort if submitFunc is not a function
        if(!$.isFunction(submitFunc)) {
            dfd.reject();
            return dfd;
        }
        // handle notifications
        var logMsg = $.Helpers.strFormat('pushing \'{0}\' config ...', observable.settings.title);
        var logObj = $.Topic('msg.log').publishBack('info', {text: logMsg, icon: 'ui-icon-refresh'})[0];
        var promise = submitFunc(section, name, obj);
        if(isTopic) {
            promise = promise[0];
        }
        $.when(promise).then(function(response) {
            if(!response.success) {
                var errorMsg = $.Helpers.strFormat('The server rejected the changes for \'<b>{0}</b>\' in section \'<b>{1}</b>\'!', observable.settings.title, section);
                $.Topic('msg.error').publish(response.msg || errorMsg);
                logObj.update({
                    text: $.Helpers.strFormat('\'{0}\' config push failed', observable.settings.title),
                    icon: 'ui-icon-alert'
                });
                dfd.reject();
            } else {
                // copy the old data
                var old = $.extend(true, {}, observable.config);
                // perform the data change
                $.extend(true, observable.config, obj);
                // callback
                if($.isFunction(callback)) {
                    callback();
                }
                // apply changes
                var applyFunc = observable.settings.apply;
                if(typeof(applyFunc) == 'string') {
                    applyFunc = $.Topic(applyFunc).publish;
                }
                if($.isFunction(applyFunc)) {
                    applyFunc(section, name, observable.config, old);
                }
                logObj.update({
                    text: $.Helpers.strFormat('\'{0}\' config pushed', observable.settings.title),
                    icon: 'ui-icon-arrowthickstop-1-n'
                });
                dfd.resolve();
            }
        });
        return dfd;
    },

    update: function(section, name) {
        var obj = this.getObservable(section, name).config;
        return this.commit(section, name, obj);
    },

    check: function(section, name, obj) {
        var _this = this;
        // check the range and type of the values first
        // according to the entries in the defaultObj
        var clean = true;
        var observable = this.getObservable(section, name);
        $.each(obj, function(key, value) {
            if(clean === true) {
                var _defaultConfig = observable.defaultConfig[key];
                if(!_defaultConfig) {
                    clean == $.Helpers.strFormat('Empty defaultConfig for key \'{0}\'', key);
                    return false;
                }
                var newValue;
                var tmpl = 'The value \'<b>{0}</b>\' with key \'<b>{1}</b>\' and type \'<b>{2}</b>\' for \'<b>{3}</b>\' in section \'<b>{4}</b>\' is invalid!';
                switch(_defaultConfig.type.toLowerCase()) {
                    case 'string':
                    case 'str':
                        newValue = _this.parseString(value, _defaultConfig);
                        if(newValue === undefined) {
                            clean = $.Helpers.strFormat(tmpl, value, 'string', key, name, section);
                        } else {
                            obj[key] = newValue;
                        }
                        break;
                    case 'integer':
                    case 'int':
                        newValue = _this.parseInteger(value, _defaultConfig);
                        if(newValue === undefined) {
                            clean = $.Helpers.strFormat(tmpl, value, 'integer', key, name, section);
                        } else {
                            obj[key] = newValue;
                        }
                        break;
                    case 'float':
                        newValue = _this.parseFloat(value, _defaultConfig);
                        if(newValue === undefined) {
                            clean = $.Helpers.strFormat(tmpl, value, 'float', key, name, section);
                        } else {
                            obj[key] = newValue;
                        }
                        break;
                    case 'boolean':
                    case 'bool':
                        newValue = _this.parseBoolean(value, _defaultConfig);
                        if(newValue === undefined) {
                            clean = $.Helpers.strFormat(tmpl, value, 'boolean', key, name, section);
                        } else {
                            obj[key] = newValue;
                        }
                        break;
                    case 'list':
                        newValue = _this.parseList(value, _defaultConfig);
                        if(newValue === undefined) {
                            clean = $.Helpers.strFormat(tmpl, value, 'list', key, name, section);
                        } else {
                            obj[key] = newValue;
                        }
                        break;
                    case 'object':
                    case 'obj':
                        newValue = _this.parseObject(value, _defaultConfig);
                        if(newValue === undefined) {
                            clean = $.Helpers.strFormat(tmpl, value, 'object', key, name, section);
                        } else {
                            obj[key] = newValue;
                        }
                        break;
                    default:
                        clean = $.Helpers.strFormat('Unknown preference type: \'{0}\'', _defaultConfig.type);
                        break;
                }
            }
        });
        if(clean !== true) {
            $.Topic('msg.error').publish(clean);
            return false;
        }
        // check with the given callback
        var response = observable.settings.check(obj);
        if (response !== true) {
            var defaultMsg = $.Helpers.strFormat('The check for \'<b>{0}</b>\' in section \'<b>{1}</b>\' failed!', name, section);
            var msg = reponse !== false ? response : defaultMsg;
            $.Topic('msg.error').publish(msg);
            return false;
        }
        return true;
    },

    parseString: function(value, _defaultConfig) {
        // check value
        value = String(value);
        // check range, which is a list of possible values
        if(_defaultConfig.range && _defaultConfig.range.length) {
            if($.inArray(value, _defaultConfig.range) < 0) {
                return undefined;
            }
        }
        return value;
    },

    parseInteger: function(value, _defaultConfig) {
        // check value
        value = parseInt(value);
        if(isNaN(value)) {
            return undefined;
        }
        // check range, which is a real range, given in a list with two values
        if(_defaultConfig.range && _defaultConfig.range.length == 2) {
            if(value < _defaultConfig.range[0] || value > _defaultConfig.range[1]) {
                return undefined;
            }
        }
        return value;
    },

    parseFloat: function(value, _defaultConfig) {
         // check value
        value = parseFloat(value);
        if(isNaN(value)) {
            return undefined;
        }
        // check range, which is a real range, given in a list with two values
        if(_defaultConfig.range && _defaultConfig.range.length == 2) {
            if(value < _defaultConfig.range[0] || value > _defaultConfig.range[1]) {
                return undefined;
            }
        }
        return value;
    },

    parseBoolean: function(value, _defaultConfig) {
        // check value, no range
        value = String(value).toLowerCase();
        if(value == 'true') {
            return true;
        } else if(value == 'false') {
            return false;
        }
        return undefined;
    },

    parseList: function(value, _defaultConfig) {
        value = $.Helpers.strBounds(String(value), false, false, '[', ']');
        var list = [];
        $.each(value.split(','), function(i, part) {
            list.push($.trim(String(part)));
        });
        return list;
    },

    parseObject: function(value, _defaultConfig) {
        value = $.parseJSON(String(value));
        return value;
    },

    setupTopics: function() {
        var _this = this;
        $.Topic('prefs.update').subscribe(function() {
            return _this.update.apply(_this, arguments);
        });
        return this;
    }
});