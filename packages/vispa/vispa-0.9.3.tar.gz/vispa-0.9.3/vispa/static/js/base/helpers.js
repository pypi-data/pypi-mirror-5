/*
 * Useful helper functions and parameters
 */

$.Helpers = {

    // infinity (int)
    infinity: 9007199254740992,

    // redirects to 'url' and use 'formatter' to eventually format
    // 'url' prior to that
    redirect: function(url, formatter) {
        url = url || '/';
        if($.isFunction(formatter)) {
            url = formatter(url);
        }
        window.location.href = url;
        return this;
    },

    // changes the directory of the url without reloading
    // the page, e.g. localhost/app to localhost/register
    // one can use '../' as well
    changeUrl: function(s) {
        history.pushState(null, '', encodeURI(s));
        return this;
    },

    // return the search parameters of the location in a  map
    getUrlParameters: function(search) {
        // catch paths (beginning with '/')
        if(search && this.strStarts(search, '/')) {
            return {};
        }
        search = search || window.location.search;
        // cut the '?' at the beginning
        search = this.strBounds(search, false, null, '?');
        var params = {};
        if(!search) {
            return params;
        }
        $.each(search.split('&'), function(i, pair) {
            if(!pair) {
                return;
            }
            var parts = pair.split('=');
            params[parts[0]] = parts[1];
        });
        return params;
    },

    formatUrlParameters: function(params, qmark) {
        var paramList = [];
        var _this = this;
        $.each(params, function(key, value) {
            if(!key) {
                return;
            }
            var tmpl;
            if(value === null || value === undefined) {
                tmpl = '{0}';
            } else {
                tmpl = '{0}={1}';
            }
            paramList.push(_this.strFormat(tmpl, key, value));
        });
        if(!paramList.length) {
            return null;
        }
        var s = qmark || qmark === undefined ? '?{0}' : '{0}';
        return this.strFormat(s, paramList.join('&'));
    },

    // retrieve the path of a js file
    scriptPath: function(scriptName) {
        var path = null;
        $('script').each(function(i, script) {
            if(script.src.substr(-1 * scriptName.length) == scriptName) {
                path = script.src.split('?')[0].split('/').slice(0, -1).join('/') + '/';
                // break $.each
                return false;
            }
        });
        return path;
    },

    loadContent: function(url, requestData) {
        requestData = $.extend({
            url: url,
            type: "GET",
            async: false,
            data: {},
            contentKey: null
        }, requestData);
        var promise = $.ajax(requestData);
        if (requestData.async) {
            return promise;
        }
        var content;
        $.when(promise).then(function(response) {
            content = requestData.contentKey ? response[requestData.contentKey] : response;
        });
        return content;
    },

    hasTouch: function() {
        return $.support.touch;
    },

    isScrollable: function(node) {
        return node.scrollHeight > $(node).height();
    },

    // searches an 'event' for a keyboard 'key' and calls a 'callback' on success
    keyCallback: function(event, key, callback) {
        var target = window.Event ? event.which : event.keyCode;
        if(target && target == key && $.isFunction(callback)) {
            callback();
        }
        return this;
    },

    // shortcut for 'keyCallback' with enter key (13) pressed
    enterKeyCallback: function(event, callback) {
        this.keyCallback(event, 13, callback);
        return this;
    },

    // handles the click on a specified object and distinguishes between
    // multiple clicks (such as single, double, triple) dependent
    // on the number of functions passed in the arguments
    // args: map{unique name w/o spaces, delay, callback, event}, function1, function2, ..., functionN
    clickCallback: function() {
        var args = arguments;

        // arguments and default values
        var map = {
            // the delay between the clicks
            delay: 300,
            // a callback that is fired eitherway
            callback: null,
            // the actual event
            event: null
        };
        $.extend(map, args[0]);

        var ccs = this.clickCallbackStorage;
        // action
        ccs[map.id] = (ccs[map.id] + 1 || 1);

        if(ccs[map.id] == 1) {
            var _this = this;
            window.setTimeout(function() {
                if(ccs[map.id] <= args.length - 1) {
                    args[ccs[map.id]](map.event);
                }

                delete ccs[map.id];
                _this.call(map.callback);
            }, map.delay);
        }
        return this;
    },

    // a storage map used be the function above
    clickCallbackStorage: {},

    // this function loads an array of js scripts recursively
    // and calls a callback function when everything is loaded
    loadJs: function(scripts, callback, async) {
        async = async == undefined ? true : async;
        scripts = typeof(scripts) == 'string' ? [scripts] : scripts;

        $.each(scripts, function(i, script) {
            // let $ load the script via ajax
            $.ajax({
                url: script,
                dataType: 'script',
                async: async
            }).fail(function(request, name, error) {
                throw error;
            });
        });
        $.isFunction() && callback();
        return this;
    },

    // this function loads an array of css scripts recursively
    // and calls a callback function when everything is loaded
    loadCss: function(scripts, callback) {
        scripts = typeof(scripts) == 'string' ? [scripts] : scripts;
        $.each(scripts, function(i, script) {
            var csslink = document.createElement('link');
            $(csslink).attr({
                type: 'text/css',
                rel: 'stylesheet',
                href: script
            });
            $('head')[0].appendChild(csslink);
        });
        $.isFunction() && callback();
        return this;
    },

    // check if a value is an integer
    isInt: function(n) {
        return typeof(n) == 'number' && n % 1 == 0;
    },

    // converts an integer 'i' into a string value in pixel
    intToPx: function(i) {
        return String(i) + 'px';
    },

    // convertes a string value in pixel 's' into an integer
    pxToInt: function(s) {
        return parseInt(s, 10);
    },

    // convertes a string value in percent 's' into an integer
    percentToInt: function(s) {
        return parseInt(s, 10);
    },

    // converts an integer 'i' into a string value in percent
    intToPercent: function(i) {
        return String(i) + '%';
    },

    // converts degree into radians
    degToRad: function(f) {
        return f * Math.PI / 180.0;
    },

    // converts radians into degree
    radToDeg: function(f) {
        return f * 180.0 / Math.PI;
    },

    // converts a string 's' into a domnode
    stringToElement: function(s) {
        return $('<div></div>').html(s).children();
    },

    // converts a domnode 'node' into a string
    elementToString: function(node) {
        var div = document.createElement('div');
        // use a deep cloned node
        $(div).append(node.cloneNode(true));
        return $(div).html();
    },

    // extends 'target' with values from objects (passed as arguments)
    // but does not overwrite existing values (like $.extend)
    extend: function(target) {
        if(!target) {
            return target;
        }
        var args = $.makeArray(arguments);
        args.shift();
        var me = this;
        $.each(args, function(i, obj) {
            $.each(obj, function(key, value) {
                var write = target[key] === undefined
                    || target[key] === null
                    || ($.isPlainObject(target[key]) && !me.objectKeys(target[key]).length);
                if(write) {
                    target[key] = value;
                }
            });
        });
        return target;
    },

    createConfig: function(target) {
        if(!$.isPlainObject(target)) {
            target = {};
        }
        var args = $.makeArray(arguments);
        args.shift();
        var me = this;
        $.each(args, function(i, obj) {
            $.each(obj, function(key, value) {
                // the key is the name of the config entry/object
                // catch name exceptions
                if(key.toLowerCase() == 'structure') {
                    return;
                }
                // value my be an object itself
                var newValue = value;
                if($.isPlainObject(value)) {
                    if(value.value === undefined) {
                        return;
                    }
                    newValue = value.value;
                }
                // value set?
                var set = value !== undefined && value !== null;
                if(!set) {
                    return;
                }
                // target set?
                var write = target[key] === undefined
                    || target[key] === null
                    || ($.isPlainObject(target[key]) && !me.objectKeys(target[key]).length);
                if(!write) {
                    return;
                }
                target[key] = newValue;
            });
        });
        return target;
    },

    // returns the keys of an object 'obj' in a list/array
    objectKeys: function(obj) {
        return $.map(obj, function(value, key) {
            return key;
        });
    },

    // switches keys and values (strings and/or integers only)
    // of an object 'obj' and returns a new one
    switchObject: function(obj) {
        var newObj = {};
        $.each(obj, function(key, value) {
            newObj[value] = key;
        });
        return newObj;
    },

    argCheck: function(obj, keys, caller, msg) {
        // no keys to check?
        if(!keys || keys == []) {
            return true;
        }

        // convert string to array
        if(typeof(keys) == 'string') {
            keys = [keys];
        }

        // prepare the error message
        if(!msg) {
            msg = ': Following keys were missing';
            if(caller == null) {
                msg += ': ';
            } else {
                msg += this.strFormat(" while calling '{0}': ", caller);
            }
        }

        // key check
        var objKeys = this.objectKeys(obj),
            missing = [];
        for(var i = 0; i < keys.length; ++i) {
            if(objKeys.indexOf(keys[i]) == -1) {
                missing.push(this.strFormat("'{0}'", keys[i]));
            }
        }

        // result
        if(missing.length == 0) {
            return true;
        } else {
            throw msg + missing.join(', ');
            return false;
        }
    },

    // converts a number 'f' into a byte string (e.g. 256623 => 256.6 kB)
    bytesToString: function(f) {
        var prefixes = {
            Bytes: 0,
            kB: 3,
            MB: 6,
            GB: 9,
            TB: 12
        };

        // try to parse as float
        try {
            f = parseFloat(f);
        } catch(e) {
            return f;
        }

        var target = 'Bytes';
        $.each(prefixes, function(prefix, value) {
            if(f / parseFloat(Math.pow(10, value)) >= 1.0) {
                target = prefix;
            }
        });

        // return the formatted string
        return this.strFormat('{0} {1}', Math.round((f / parseFloat(Math.pow(10, prefixes[target]))) * 100) / 100, target);
    },

    // returns the first argument that is not null
    getFirstSetValue: function() {
        var value;
        $.each(arguments, function(i, arg) {
            if(arg) {
                value = arg;
                // break $.each
                return false;
            }
        });
        return value;
    },

    // checks whether the file 'url' exists ('async') and uses error ('onError') or success ('onSuccess') callbacks
    validURL: function(url, onSuccess, onError, async) {
        async = async == undefined ? false : async;
        $.ajax({
            url: url,
            type: 'HEAD',
            async: async
        }).done(onSuccess).fail(onError);
        return this;
    },

    // calculates the width of text
    textWidth: function(text, css) {
        css = css || {};
        var span = $('<span />')
            .append(text)
            .css(css)
            .css('opacity', 0)
            .appendTo('body');
        var width = span.width();
        span.remove();
        return width;
    },

    /* String operations*/
    strFormat: function(s) {
        var i = arguments.length;
        while (i--) {
            s = s.replace(new RegExp('\\{' + (i-1) + '\\}', 'gm'), String(arguments[i]));
        }
        return s;
    },

    strEnds: function(s, sub) {
        return s.substr(-1 * sub.length) == sub;
    },

    strStarts: function(s, sub) {
        return s.substr(0, sub.length) == sub;
    },

    strClean: function(s, selection) {
        selection = selection || 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-_';
        selection = $.isArray(selection) ? selection.join('') : selection;
        var clean = true;
        $.each(s.split(''), function(i, c) {
            if(selection.indexOf(c) == -1) {
                clean = false;
                // break $.each
                return false;
            }
        });
        return clean;
    },

    strExtension: function(s) {
        var parts = s.split('/');
        if (!parts.length) {
            return null;
        }
        s = parts.pop();

        parts = s.split('.');
        if(parts.length < 2) {
            return null;
        }
        return parts.pop();
    },

    strCutExtension: function(s) {
        var parts = s.split('.');
        if(parts.length === 1) {
            return s;
        }
        parts.pop();
        return parts.join('.');
    },

    strCapitalize: function(s) {
        return s.substring(0, 1).toUpperCase() + s.substring(1);
    },

    strEscapeHTML: function(s) {
        return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    },

    strCount: function(s, sub) {
        if(!s) {
            return 0;
        }
        var i = 0,
            copy = s,
            idx = s.indexOf(sub);
        while(idx != -1) {
            i++;
            copy = copy.substring(0, idx) + copy.substring(idx + sub.length);
            idx = copy.indexOf(sub);
        }
        return i;
    },

    strBounds: function(s, leading, trailing, leadingSub, trailingSub) {
        leadingSub = leadingSub || '/';
        trailingSub = trailingSub || leadingSub;
        if(!this.strStarts(s, leadingSub)) {
            s = leading === true ? (leadingSub + s) : s;
        } else {
            s = leading === false ? s.substr(leadingSub.length) : s;
        }
        if(!this.strEnds(s, trailingSub)) {
            s = trailing === true ? (s + trailingSub) : s;
        } else {
            s = trailing === false ? s.substr(0, s.length - trailingSub.length) : s;
        }
        return s;
    },

    joinPath: function() {
        var me = this;
        var args = $.makeArray(arguments);
        var parts = [];
        $.each(args, function(i, arg) {
            var part = me.strBounds(arg, !i ? null : false, i == args.length-1 ? null : false);
            parts.push(part);
        });
        return parts.join('/').replace(/\/\/\//g, '/').replace(/\/\//g, '/');
    },

    // removes all classes from obj that match pattern
    removeClass: function(selector, pattern) {
        var jQNode = $(selector);
        var classes = jQNode.attr('class').replace(/\s+/g, ' ');
        $.each(classes.split(' '), function(i, cls) {
            if(cls.match(pattern)) {
                jQNode.removeClass(cls);
            }
        });
        return jQNode.get(0);
    },

    s4: function() {
        return Math.floor((1 + Math.random()) * 0x10000)
             .toString(16)
            .substring(1);
    },

    guid: function() {
      return this.s4() + this.s4() + '-' + this.s4() + '-' + this.s4() + '-' + this.s4() + '-' + this.s4() + this.s4() + this.s4();
    }
};