var MenuHandler = Class.extend({

    init: function() {
        this.menus = [];
        this.defaultItem = {
            label: '',
            separator: false,
            icon: null,
            alt: null,
            callback: function() {},
            formatter: null,
            dragClass: null,
            children: {
                id: null,
                items: []
            }
        };
    },

    create: function(id, trigger, items, position, bind, target) {
        var _this = this;
        // define the basic position
        var defaultPosition = {
            my: 'left top',
            at: 'left bottom',
            of: $(trigger)
        };
        position = $.extend(defaultPosition, position);
        var menu;
        // define the global menu overlay
        var overlay = $('<div />')
            .addClass('menu-overlay')
            .appendTo('body')
            .mousedown(function() {
                $(this).hide();
                menu.hide();
            });
        // define the opening callback
        var openCallback = function(_position) {
            var pos = $.extend(true, {}, position, _position);
            if(menu.css('display') == 'none') {
                _this.hideAll();
                overlay.show();
                menu.show().position(pos).menu('refresh').focus().css('z-index', 1010);
                menu.one('click', function() {
                    menu.hide();
                    overlay.hide();
                });
            } else {
                menu.hide();
            }
            return false;
        };
        // bind the opening callback it to the trigger?
        if(bind || bind === undefined) {
            $(trigger).click(openCallback);
        }
        // create the node and ad to behind the trigger
        menu = $('<ul />')
            .attr('id', id)
            .appendTo(target || $(trigger).parent())
            .hide()
            .data('menuOverlay', overlay);
        this.add(menu, items, false, false);
        menu.menu();
        this.menus.push(menu.get(0));
        return openCallback;
    },

    hideAll: function() {
        $.each(this.menus, function(i, menu) {
            if(menu) {
                $(menu).hide();
            }
        });
        return this;
    },

    add: function(selector, items, prepend, doRefresh) {
        var _this = this;
        if(!$.isArray(items)) {
            items = [items];
        }
        var menu = $(selector);
        $.each(items, function(i, item) {
            var li = _this.parseItem(item);
            if(prepend) {
                menu.prepend(li);
            } else {
                menu.append(li);
            }
        });
        if(doRefresh || doRefresh === undefined) {
            this.refresh(selector);
        }
        return this;
    },

    remove: function(selector, items, subSelector) {
        subSelector = subSelector || selector;
        if(!$.isArray(items)) {
            items = [items];
        }
        $.each(items, function(i, item) {
            $.each($(subSelector).children(), function(j, li) {
                var a = $(li).find('a')[0];
                var target = $.isPlainObject(item) ? item.label : item;
                if(a && target && $.Helpers.strEnds($(a).html(), '</span>' + target)) {
                    $(li).remove();
                }
            });
        });
        this.refresh(selector);
        return this;
    },

    modify: function(selector, item, newItem, subSelector) {
        if (!$.isPlainObject(newItem)) {
            newItem = {
                label: newItem
            };
        }
        subSelector = subSelector || selector;
        $.each($(subSelector).children(), function(i, li) {
            var a = $(li).find('a')[0];
            var target = $.isPlainObject(item) ? item.label : item;
            if(a && target && $.Helpers.strEnds($(a).html(), '</span>' + target)) {
                // replace the label
                var expr = /(.*\<\/span\>).*/;
                var matches = expr.exec($(a).html());
                $(a).html(matches[1] + newItem.label);
                // replace the icon
                if (newItem.icon) {
                    expr = /(.*ui\-icon\s).*(\"\sstyle.*)/;
                    matches = expr.exec($(a).html());
                    $(a).html(matches[1] + newItem.icon + matches[2]);
                }
            }
        });
        this.refresh(selector);
        return this;
    },

    empty: function(selector) {
        $(selector).empty();
        this.refresh(selector);
        return this;
    },

    refresh: function(selector) {
        $(selector).menu('refresh');
        return this;
    },

    parseItem: function(item) {
        var _this = this;
        item = $.extend(true, {}, this.defaultItem, item);
        if (item.separator) {
            return $('<hr>').get(0);
        }
        var li = $('<li>');

        if(item.disabled) {
            li.addClass('ui-state-disabled');
        } else {
            if(item.dragClass) {
                li
                    .addClass(item.dragClass)
                    .draggable({
                        distance: 20,
                        helper: 'clone'
                    }).data('menuItem', item);
            }
        }
        var a = $('<a>').css('cursor', 'pointer');
        var aLabel = '';
        if(item.icon) {
            var style = 'margin-top:1px;';
            aLabel += $.Helpers.strFormat('<span class="ui-icon {0}" style="{1}"></span>', item.icon, style);
        }
        aLabel += item.label;
        a.html(aLabel);
        // stylize the link
        if(item.alt) {
            a.attr({alt: item.alt, title: item.alt});
        }
        if(item.formatter && $.isFunction(item.formatter)) {
            a = item.formatter(a);
        }
        li.append(a);
        if(item.children && item.children.items && item.children.items.length) {
            var ul = $('<ul />');
            if(item.children.id) {
                ul.attr('id', item.children.id)
            }
            $.each(item.children.items, function(i, elem) {
                ul.append(_this.parseItem(elem));
            });
            li.append(ul);
        } else if (item.callback && $.isFunction(item.callback)) {
            a.click(item.callback);
        }
        return li[0];
    }
});