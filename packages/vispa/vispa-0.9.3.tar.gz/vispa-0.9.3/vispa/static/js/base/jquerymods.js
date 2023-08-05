(function($) {

    // jQuery Core

    // jQuery Callbacks
    var core_rnotwhite = /\S+/g;
    var optionsCache = {};
    function createOptions( options ) {
        var object = optionsCache[ options ] = {};
        jQuery.each( options.match( core_rnotwhite ) || [], function( _, flag ) {
            object[ flag ] = true;
        });
        return object;
    }
    jQuery.Callbacks = function( options ) {

        // Convert options from String-formatted to Object-formatted if needed
        // (we check in cache first)
        options = typeof options === "string" ?
            ( optionsCache[ options ] || createOptions( options ) ) :
            jQuery.extend( {}, options );

        var // Flag to know if list is currently firing
            firing,
            // Last fire value (for non-forgettable lists)
            memory,
            // Flag to know if list was already fired
            fired,
            // End of the loop when firing
            firingLength,
            // Index of currently firing callback (modified by remove if needed)
            firingIndex,
            // First callback to fire (used internally by add and fireWith)
            firingStart,
            // Actual callback list
            list = [],
            // Stack of fire calls for repeatable lists
            stack = !options.once && [],
            // Fire callbacks
            fire = function( data ) {
                memory = options.memory && data;
                fired = true;
                firingIndex = firingStart || 0;
                firingStart = 0;
                firingLength = list.length;
                firing = true;
                for ( ; list && firingIndex < firingLength; firingIndex++ ) {
                    if ( list[ firingIndex ].apply( data[ 0 ], data[ 1 ] ) === false && options.stopOnFalse ) {
                        memory = false; // To prevent further calls using add
                        break;
                    }
                }
                firing = false;
                if ( list ) {
                    if ( stack ) {
                        if ( stack.length ) {
                            fire( stack.shift() );
                        }
                    } else if ( memory ) {
                        list = [];
                    } else {
                        self.disable();
                    }
                }
            },
            // Modification:
            // add fireBack
            fireBack = function( data ) {
                memory = options.memory && data;
                fired = true;
                firingIndex = firingStart || 0;
                firingStart = 0;
                firingLength = list.length;
                firing = true;
                var results = [];
                for ( ; list && firingIndex < firingLength; firingIndex++ ) {
                    var result = list[ firingIndex ].apply( data[ 0 ], data[ 1 ] );
                    results.push( result );
                    if ( result === false && options.stopOnFalse ) {
                        memory = false; // To prevent further calls using add
                        break;
                    }
                }
                firing = false;
                if ( list ) {
                    if ( stack ) {
                        if ( stack.length ) {
                            fire( stack.shift() );
                        }
                    } else if ( memory ) {
                        list = [];
                    } else {
                        self.disable();
                    }
                }
                return results;
            },
            // Actual Callbacks object
            self = {
                // Add a callback or a collection of callbacks to the list
                add: function() {
                    if ( list ) {
                        // First, we save the current length
                        var start = list.length;
                        (function add( args ) {
                            jQuery.each( args, function( _, arg ) {
                                var type = jQuery.type( arg );
                                if ( type === "function" ) {
                                    if ( !options.unique || !self.has( arg ) ) {
                                        list.push( arg );
                                    }
                                } else if ( arg && arg.length && type !== "string" ) {
                                    // Inspect recursively
                                    add( arg );
                                }
                            });
                        })( arguments );
                        // Do we need to add the callbacks to the
                        // current firing batch?
                        if ( firing ) {
                            firingLength = list.length;
                        // With memory, if we're not firing then
                        // we should call right away
                        } else if ( memory ) {
                            firingStart = start;
                            fire( memory );
                        }
                    }
                    return this;
                },
                // Remove a callback from the list
                remove: function() {
                    if ( list ) {
                        jQuery.each( arguments, function( _, arg ) {
                            var index;
                            while( ( index = jQuery.inArray( arg, list, index ) ) > -1 ) {
                                list.splice( index, 1 );
                                // Handle firing indexes
                                if ( firing ) {
                                    if ( index <= firingLength ) {
                                        firingLength--;
                                    }
                                    if ( index <= firingIndex ) {
                                        firingIndex--;
                                    }
                                }
                            }
                        });
                    }
                    return this;
                },
                // Check if a given callback is in the list.
                // If no argument is given, return whether or not list has callbacks attached.
                has: function( fn ) {
                    return fn ? jQuery.inArray( fn, list ) > -1 : !!( list && list.length );
                },
                // Remove all callbacks from the list
                empty: function() {
                    list = [];
                    return this;
                },
                // Have the list do nothing anymore
                disable: function() {
                    list = stack = memory = undefined;
                    return this;
                },
                // Is it disabled?
                disabled: function() {
                    return !list;
                },
                // Lock the list in its current state
                lock: function() {
                    stack = undefined;
                    if ( !memory ) {
                        self.disable();
                    }
                    return this;
                },
                // Is it locked?
                locked: function() {
                    return !stack;
                },
                // Call all callbacks with the given context and arguments
                fireWith: function( context, args ) {
                    args = args || [];
                    args = [ context, args.slice ? args.slice() : args ];
                    if ( list && ( !fired || stack ) ) {
                        if ( firing ) {
                            stack.push( args );
                        } else {
                            fire( args );
                        }
                    }
                    return this;
                },
                // Call all the callbacks with the given arguments
                fire: function() {
                    self.fireWith( this, arguments );
                    return this;
                },
                // To know if the callbacks have already been called at least once
                fired: function() {
                    return !!fired;
                },
                // Modification:
                // add fireWithBack and fireBack
                fireWithBack: function( context, args ) {
                    args = args || [];
                    args = [ context, args.slice ? args.slice() : args ];
                    var result;
                    if ( list && ( !fired || stack ) ) {
                        if ( firing ) {
                            stack.push( args );
                        } else {
                            result = fireBack( args );
                        }
                    }
                    return result;
                },
                fireBack: function() {
                    return self.fireWithBack( this, arguments );
                }
            };

        return self;
    };


    // jQuery UI

    // dialog
    if ($.ui.dialog) {
        $.extend($.ui.dialog.prototype, {
            _oldTitle: $.ui.dialog.prototype._title,
            _title: function( title ) {
                if ( !this.options.title ) {
                    title.html("&#160;");
                }
                // modification: use html() instead of text()
                title.html( this.options.title );
            }
        });
    }

    // menu
    if ($.ui.menu) {
        $.extend($.ui.menu.prototype, {
            _oldCreate: $.ui.menu.prototype._create,
            _create: function() {
                this.activeMenu = this.element;
                // flag used to prevent firing of the click handler
                // as the event bubbles up through nested menus
                this.mouseHandled = false;
                this.element
                    .uniqueId()
                    .addClass( "ui-menu ui-widget ui-widget-content ui-corner-all" )
                    .toggleClass( "ui-menu-icons", !!this.element.find( ".ui-icon" ).length )
                    .attr({
                        role: this.options.role,
                        tabIndex: 0
                    })
                    // need to catch all clicks on disabled menu
                    // not possible through _on
                    .bind( "click" + this.eventNamespace, $.proxy(function( event ) {
                        if ( this.options.disabled ) {
                            event.preventDefault();
                        }
                    }, this ));

                if ( this.options.disabled ) {
                    this.element
                        .addClass( "ui-state-disabled" )
                        .attr( "aria-disabled", "true" );
                }

                this._on({
                    // Prevent focus from sticking to links inside menu after clicking
                    // them (focus should always stay on UL during navigation).
                    "mousedown .ui-menu-item > a": function( event ) {
                        event.preventDefault();
                    },
                    "click .ui-state-disabled > a": function( event ) {
                        event.preventDefault();
                    },
                    "click .ui-menu-item:has(a)": function( event ) {
                        var target = $( event.target ).closest( ".ui-menu-item" );

                        // Modification:
                        // don't require this.mouseHandled to be false
                        //if ( !this.mouseHandled && target.not( ".ui-state-disabled" ).length ) {
                        if ( target.not( ".ui-state-disabled" ).length ) {

                            // Modification: comment the mouseHandled state change and the select call
                            // this.mouseHandled = true;
                            // this.select( event );

                            // Open submenu on click
                            if ( target.has( ".ui-menu" ).length ) {
                                this.expand( event );
                                // Modification:
                                // stop event propagation
                                event.stopPropagation();
                            } else if ( !this.element.is( ":focus" ) ) {
                                // Modification:
                                // call the select method now
                                this.select( event );

                                // Redirect focus to the menu
                                this.element.trigger( "focus", [ true ] );

                                // If the active item is on the top level, let it stay active.
                                // Otherwise, blur the active item since it is no longer visible.
                                if ( this.active && this.active.parents( ".ui-menu" ).length === 1 ) {
                                    clearTimeout( this.timer );
                                }
                            }
                        }
                    },
                    "mouseenter .ui-menu-item": function( event ) {
                        var target = $( event.currentTarget );
                        // Remove ui-state-active class from siblings of the newly focused menu item
                        // to avoid a jump caused by adjacent elements both having a class with a border
                        target.siblings().children( ".ui-state-active" ).removeClass( "ui-state-active" );
                        this.focus( event, target );
                    },
                    mouseleave: "collapseAll",
                    "mouseleave .ui-menu": "collapseAll",
                    focus: function( event, keepActiveItem ) {
                        // If there's already an active item, keep it active
                        // If not, activate the first item
                        var item = this.active || this.element.children( ".ui-menu-item" ).eq( 0 );

                        if ( !keepActiveItem ) {
                            this.focus( event, item );
                        }
                    },
                    blur: function( event ) {
                        this._delay(function() {
                            if ( !$.contains( this.element[0], this.document[0].activeElement ) ) {
                                this.collapseAll( event );
                            }
                        });
                    },
                    keydown: "_keydown"
                });

                this.refresh();

                // Clicks outside of a menu collapse any open menus
                this._on( this.document, {
                    click: function( event ) {
                        // Modification:
                        // stop here
                        return;

                        if ( !$( event.target ).closest( ".ui-menu" ).length ) {
                            this.collapseAll( event );
                        }

                        // Reset the mouseHandled flag
                        this.mouseHandled = false;
                    }
                });
            }
        });
    }
})(jQuery)