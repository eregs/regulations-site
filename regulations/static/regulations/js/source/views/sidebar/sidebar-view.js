'use strict';
var $ = require('jquery');
var _ = require('underscore');
var Backbone = require('backbone');
var RegModel = require('../../models/reg-model');
var SxSList = require('./sxs-list-view');
var SidebarModel = require('../../models/sidebar-model');
var DefinitionModel = require('../../models/definition-model');
var Breakaway = require('../breakaway/breakaway-view');
var SidebarEvents = require('../../events/sidebar-events');
var Definition = require('./definition-view');
var MetaModel = require('../../models/meta-model');
var MainEvents = require('../../events/main-events');
var Helpers = require('../../helpers.js');

Backbone.$ = $;

var SidebarView = Backbone.View.extend({
    el: '#sidebar-content',

    events: {
        'click .expandable': 'toggleExpandable'
    },

    initialize: function() {
        var cache;
        this.openRegFolders = _.bind(this.openRegFolders, this);
        this.externalEvents = SidebarEvents;
        this.listenTo(this.externalEvents, 'update', this.updateChildViews);
        this.listenTo(this.externalEvents, 'definition:open', this.openDefinition);
        this.listenTo(this.externalEvents, 'definition:close', this.closeDefinition);
        this.listenTo(this.externalEvents, 'section:loading', this.loading);
        this.listenTo(this.externalEvents, 'section:error', this.loaded);
        this.listenTo(this.externalEvents, 'breakaway:open', this.hideChildren);

        this.childViews = {'sxs': new SxSList()};
        this.definitionModel = DefinitionModel;
        this.model = SidebarModel;
        /* Cache the initial sidebar */
        this.$el.find('[data-cache-key=sidebar]').each(function(idx, el) {
            var $el = $(el);
            SidebarModel.set($el.data('cache-value'), $el.html());
        });
    },

    openDefinition: function(config) {
        var createDefView = function(cb, success, res) {
            var errorMsg;

            if (success) {
                this.childViews.definition.render(res);
            }
            else {
                errorMsg = 'We tried to load that definition, but something went wrong. ';
                errorMsg += '<a href="#" class="update-definition inactive internal" data-definition="' + this.childViews.definition.id + '">Try again?</a>';

                this.childViews.definition.renderError(errorMsg);
            }
        }.bind(this);

        this.childViews.definition = new Definition({
            id: config.id,
            term: config.term
        });

        config.cb = config.cb || null;

        this.definitionModel.get(config.id, _.partial(createDefView, config.cb));
    },

    closeDefinition: function() {
        if (typeof this.childViews.definition !== 'undefined') {
            this.childViews.definition.remove();
        }
    },

    updateChildViews: function(context) {
        var $definition = $definition || this.$el.find('#definition'); // eslint-disable-line no-use-before-define
        switch (context.type) {
            case 'reg-section':
                this.model.get(context.id, this.openRegFolders);
                MainEvents.trigger('definition:carriedOver');

                // definition container is hidden when SxS opens
                if ($definition.is(':hidden')) {
                    $definition.show();
                }

                break;
            case 'search':
                this.removeChildren();
                this.loaded();
                break;
            case 'diff':
                this.loaded();
                break;
            default:
                this.removeChildren();
                this.loaded();
        }

        this.removeLandingSidebar();
    },

    /* AJAX retrieved a sidebar. Replace the relevant portions of the
     * existing sidebar */
    openRegFolders: function(success, html) {
        // remove all except definition
        this.removeChildren('definition');

        this.$el.find('[data-cache-key=sidebar]').remove();
        this.$el.append(html);

        // new views to bind to new html
        this.childViews.sxs = new SxSList();
        this.loaded();
    },

    removeLandingSidebar: function() {
        $('.landing-sidebar').hide();
    },

    insertDefinition: function(el) {
        this.closeExpandables();

        if (this.$el.definition.length === 0) {
            // if the page was loaded on the landing, search or 404 page,
            // it won't have the content sidebar template
            this.$el.prepend('<section id="definition"></section>');
            this.$el.definition = this.$el.find('#definition');
        }

        this.$el.definition.html(el);
    },

    closeExpandables: function() {
        this.$el.find('.expandable').each(function(i, folder) {
            var $folder = $(folder);
            if ($folder.hasClass('open')) {
                this.toggleExpandable($folder);
            }
        }.bind(this));
    },

    toggleExpandable: function(e) {
      var $expandable;

        if (typeof e.stopPropagation !== 'undefined') {
            e.stopPropagation();
            $expandable = $(e.currentTarget);
        }
        else {
            $expandable = e;
        }
        Helpers.toggleExpandable($expandable, 400);
    },

    removeChildren: function(except) {
        var k;
        for (k in this.childViews) {
            if (this.childViews.hasOwnProperty(k)) {
                if (!except || except !== k) {
                    this.childViews[k].remove();
                }
            }
        }
        /* Also remove any components of the sidebar which don't have a
         * Backbone view */
        this.$el.find('.regs-meta').remove();
    },

    loading: function() {
        this.$el.addClass('loading');
    },

    loaded: function() {
        this.$el.removeClass('loading');
    },

    // when breakaway view loads
    hideChildren: function() {
        this.loading();
    }
});

module.exports = SidebarView;
