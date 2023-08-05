var WappSocket = function(url, _settings) {

    var self,

    settings = {
        autoReconnect: false,//TODO
        fallback: true,
        fallbackSendUrl: url ? url.replace('ws:', 'http:').replace('wss:', 'https:') : url,
        fallbackSendMethod: 'POST',
        fallbackSendAsync: true,
        fallbackPollUrl: url ? url.replace('ws:', 'http:').replace('wss:', 'https:') : url,
        fallbackPollMethod: 'POST',
        fallbackPollAsync: true,
        fallbackPollDelay: 3000,
        fallbackPollParams: {},
        forceFallback: false,
        onopen: function(){},
        onclose: function(){},
        onmessage: function(){},
        onerror: function(){},
        onopenFallback: null,
        oncloseFallback: null,
        onmessageFallback: null,
        onerrorFallback: null
    },

    ws;

    $.extend(true, settings, _settings);

    if (window.WebSocket && !settings.forceFallback) {
        ws = new WebSocket(url);
        ws.onopen = settings.onopen;
        ws.onclose = settings.onclose;
        ws.onmessage = settings.onmessage;
        ws.onerror = settings.onerror;
    } else if (settings.fallback) {
        var interval,

        statusMap = {
            'CONNECTING': 0, 
            'CONNECTED': 1,
            'CLOSING': 2,
            'CLOSED': 3
        },

        status = statusMap['CLOSED'],

        send = function(data) {
            if (!settings.fallbackSendUrl) {
                return;
            }
            if ($.isPlainObject(data)) {
                data = $.parseJSON(data.replace(/\'/g, '"'));
            }
            $.ajax({
                url: settings.fallbackSendUrl,
                type: settings.fallbackSendMethod,
                async: settings.fallbackSendAsync,
                data: data
            });
        },

        poll = function() {
            ws.readyState = statusMap['CONNECTING'];
            var onMessage = function(text) {
                var event = {data: text};
                ws.onmessage(event);
            };
            var onError = function(data, status, msg) {
                var event = {};
                ws.onerror(event);
            };
            var onOpen = function() {
                if (ws.readyState != statusMap['CONNECTED']) {
                    ws.readyState = statusMap['CONNECTED'];
                    var event = {};
                    ws.onopen(event);
                }
            };
            var onClose = function(data, status, msg) {
                if (ws.readyState != statusMap['CLOSED']) {
                    ws.readyState = statusMap['CLOSING'];
                    window.clearInterval(interval);
                    interval = null;
                    ws.readyState = statusMap['CLOSED'];
                    var event = {reason: msg};
                    ws.onclose(event);
                }
            };
            var callback = function() {
                $.ajax({
                    url: settings.fallbackPollUrl,
                    type: settings.fallbackPollMethod,
                    async: settings.fallbackPollAsync,
                    dataType: 'text',
                    contentType : 'application/x-www-form-urlencoded; charset=utf-8',
                    data: settings.fallbackPollParams,
                    success: function(data) {
                        onOpen.apply(null, arguments);
                        if (data != '') {
                            onMessage.apply(null, arguments);
                        }
                    },
                    error: function(data, status, msg) {
                        onError.apply(null, arguments);
                        onClose.apply(null, arguments);
                    }
                });
            };
            callback();
            interval = window.setInterval(callback, settings.fallbackPollDelay);
        };

        ws = {
            send: send,
            onopen: settings.onopenFallback || settings.onopen,
            onclose: settings.oncloseFallback || settings.onclose,
            onmessage: settings.onmessageFallback || settings.onmessage,
            onerror: settings.onerrorFallback || settings.onerror,
            readyState: status
        };

        poll();
    }

    return ws;
};