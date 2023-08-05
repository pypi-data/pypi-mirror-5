var View = Class.extend({

    init: function(vispa, config) {
        Vispa = vispa;

        // attributes
        this.defaultConfig = {};
        this.config = $.Helpers.createConfig(config, this.defaultConfig);
    },

    startup: function() {
        this.setupMarkup();
        $('#login-name').focus();
        this.hideOverlay();
        return this;
    },

    setupMarkup: function() {
        var _this = this;
        // hide the 'forgot password' container?
        if(!Vispa.config.useForgot) {
            var selectors = '#login-forgot, #forgot-container, #forgot-container-header';
            $(selectors).remove();
        }
        // accordion
        $('#accordion').accordion({
            header: 'h3',
            animate: {easing: 'easeOutExpo', duration: 300},
            activate: function(event, ui) {
                var map = {
                    Login: '#login-name',
                    Register: '#register-name',
                    'Forgot password': '#forgot-name'
                };
                var selector = map[ui.newHeader.text()];
                if(selector) {
                    $(selector).focus();
                }
            }
        });
        // buttons
        $('#login-submit').button({
            icons: {primary: "ui-icon-check"}
        }).click(function() {
            Vispa.login();
        });
        $('#login-forgot').button({
            icons: {primary: "ui-icon-help"}
        }).click(function() {
            _this.showForgot();
        });
        $('#register-submit').button({
            icons: {primary: "ui-icon-pencil"}
        }).click(function() {
            Vispa.register();
        });
        $('#forgot-submit').button({
            icons: {primary: "ui-icon-mail-closed"}
        }).click(function() {
            Vispa.forgot();
        });
        // inputs
        var next = function(event, target) {
            var key = event.keyCode || event.which;
            if(key == 13) {
                if($.isFunction(target)) {
                    target();
                } else {
                    $(target).focus();
                }
            }
        };
        $('#login-name').keypress(function(event) {
            next(event, '#login-password');
        });
        $('#login-password').keypress(function(event) {
            next(event, function() {
                Vispa.login();
            });
        });
        $('#register-name').keypress(function(event) {
            next(event, '#register-mail-1');
        });
        $('#register-mail-1').keypress(function(event) {
            next(event, '#register-mail-2');
        });
        $('#register-mail-2').keypress(function(event) {
            next(event, '#register-password-1');
        });
        $('#register-password-1').keypress(function(event) {
            next(event, '#register-password-2');
        });
        $('#register-password-2').keypress(function(event) {
            next(event, function() {
                Vispa.register();
            });
        });
        $('#forgot-name').keypress(function(event) {
            next(event, function() {
                Vispa.forgot();
            });
        });
        return this;
    },

    showForgot: function() {
        $('#accordion').accordion('option', 'active', 2);
        return this;
    },

    hideOverlay: function(fx) {
        fx = $.extend(true, {
            duration: 50,
            easing: 'linear'
        }, fx);
        var dfd = $.Deferred();
        $('#startup-overlay').fadeOut(fx.duration, fx.easing, dfd.resolve);
        return dfd.promise();
    }
});