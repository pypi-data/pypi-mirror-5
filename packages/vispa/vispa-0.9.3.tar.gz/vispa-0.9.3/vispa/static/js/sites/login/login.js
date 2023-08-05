var Vispa = Class.extend({

    init: function(config) {
        // attributes
        this.defaultConfig = {
            requestedPath: '/',
            useForgot: false,
            view: {},
            messenger: {},
            urlHandler: {}
        };
        this.config = $.extend(true, {}, this.defaultConfig, config);
        // members
        this.view = new View(this.config.view);
        this.messenger = new Messenger(this.config.messenger);
        this.urlHandler = new UrlHandler(this.config.urlHandler);
    },

    startup: function() {
        this.messenger.startup();
        this.urlHandler.startup();
        this.view.startup();
        return this;
    },

    login: function() {
        var me = this;
        var user = $('#login-name').val();
        var pass = $('#login-password').val();
        if(!user) {
            $('#login-name').focus();
            return this;
        }
        if(!pass) {
            $('#login-password').focus();
            return this;
        }
        pass = $.sha256(pass);
        var promise = $.ajax({
            type: 'POST',
            url: this.urlHandler.dynamic('/ajax/login'),
            data: {username: user, password: pass}
        });
        $.when(promise).then(function(response) {
            if(!response.success) {
                $.Topic('msg.error').publish(response.msg, function() {
                    $('#login-name').focus();
                });
            } else {
                $.Helpers.redirect(me.urlHandler.dynamic(me.config.requestedPath));
            }
        }).fail(function(request, status, msg) {
            $.Topic('msg.error').publish($.Helpers.strFormat('{0}: {1}', request.status, msg));
        });
        return this;
    },

    register: function() {
        var me = this;
        var user = $('#register-name').val();
        var pass1 = $('#register-password-1').val();
        var pass2 = $('#register-password-2').val();
        var mail1 = $('#register-mail-1').val();
        var mail2 = $('#register-mail-2').val();
        if(!user) {
            $('#register-name').focus();
            return this;
        }
        if(!pass1) {
            $('#register-password-1').focus();
            return this;
        }
        if(!pass2) {
            $('#register-password-2').focus();
            return this;
        }
        if(!mail1) {
            $('#register-mail-1').focus();
            return this;
        }
        if(!mail2) {
            $('#register-mail-2').focus();
            return this;
        }
        if(mail1 != mail2) {
            $.Topic('msg.error').publish('Your mail addresses do not match!', function() {
                $('#register-mail-1').focus();
            });
            return this;
        }
        if(pass1.length < 8) {
            $.Topic('msg.error').publish('The minimal password length is 8!', function() {
                $('#register-password-1').focus();
            });
            return this;
        }
        if(pass1 != pass2) {
            var msg = 'Your passwords do not match!';
            $.Topic('msg.error').publish(msg, function() {
                $('#register-password-1').focus();
            });
            return this;
        }
        pass = $.sha256(pass1);
        var promise = $.ajax({
            type: 'POST',
            url: this.urlHandler.dynamic('/ajax/register'),
            data: {username: user, email: mail1, password: pass}
        });
        $.when(promise).then(function(response) {
            if(!response.success) {
                $.Topic('msg.error').publish(response.msg, function() {
                    $('#register-name').focus();
                });
            } else {
                $.Helpers.redirect(me.urlHandler.dynamic('/'));
            }
        }).fail(function(request, status, msg) {
            $.Topic('msg.error').publish($.Helpers.strFormat('{0}: {1}', request.status, msg));
        });
        return this;
    },

    forgot: function() {
        if(!this.config.userForgot) {
            return this;
        }
        var user = $('#forgot-name').val();
        if(!user) {
            $('#forgot-name').focus();
            return this;
        }
        var promise = $.ajax({
            type: 'POST',
            url: this.urlHandler.dynamic('/ajax/forgot'),
            data: {username: user}
        });
        $.when(promise).then(function(response) {
            $.Topic('msg.notify').publish({text: response.msg, icon: 'ui-icon-mail-closed'});
            $('#accordion').accordion('option', 'active', 0);
        }).fail(function(request, status, msg) {
            $.Topic('msg.error').publish($.Helpers.strFormat('{0}: {1}', request.status, msg));
        });
        return this;
    }
});