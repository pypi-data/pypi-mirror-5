var _bus = {
    websocket: null,
    settings: {
        address: null,
        onopen: function(event) {
        },
        onclose: function(event) {
        },
        onmessage: function(event) {
            var data = $.parseJSON(event.data.replace(/\'/g, '"'));
            if (data.topic && _bus.topics[data.topic]) {
                Bus(data.topic).publish(data);
            }
        },
        onerror: function() {
        },
        onmessageFallback: function(event) {
            var msgs = $.parseJSON(event.data.replace(/\'/g, '"'));
            $.each(msgs, function(i, msg) {
                var evt = {
                    data: msg
                };
                _bus.settings.onmessage(evt);
            });
        }
    },
    setup: function(_settings) {
        this.websocket = WappSocket(_settings.address, _settings);
    },
    topics: {}
};


var Bus = function(id) {

    // configure and startup if id is an object
    if ($.isPlainObject(id)) {
        _bus.settings = $.Helpers.extend(id, _bus.settings)
        _bus.setup(id);
        return Bus;
    }

    var self = id && _bus.topics[id];

    if (!self) {

        var _callbacks = $.Callbacks(),

        _enabled = true,

        publish = function() {
            if (_enabled) {
                _callbacks.fire.apply(_callbacks, arguments);
            }
            return self;
        },

        subscribe = function(callback) {
            _callbacks.add(callback.fire || callback);
            return self;
        },

        send = function(msg) {
            if (_bus.websocket) {
                if($.isPlainObject(msg)) {
                    msg = JSON.stringify(msg);
                }
                _bus.websocket.send(msg);
            }
            return self;
        },

        enable = function() {
            _enabled = true;
            return self;
        },

        disable = function() {
            _enabled = false;
            return self;
        },

        enabled = function() {
            return _enabled;
        },

        empty = function() {
            _callbacks = $.Callbacks();
            return self;
        },

        remove = function() {
            if (id) {
                delete _bus.topics[id];
            }
        },

        callbacks = function() {
            return _callbacks;
        };

        self = {
            publish: publish,
            subscribe: subscribe,
            send: send,
            enable: enable,
            disable: disable,
            enabled: enabled,
            empty: empty,
            remove: remove,
            callbacks: callbacks
        };

        if (id) {
            _bus.topics[id] = self;
        }
    }

    return self;
};