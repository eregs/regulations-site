'use strict';
var $ = require('jquery');
var _ = require('underscore');
var Backbone = require('backbone');
var TOCView = require('./toc-view');
var HistoryView = require('./history-view');
var SearchView = require('./search-view');
var DrawerTabs = require('./drawer-tabs-view');
var DrawerEvents = require('../../events/drawer-events');
Backbone.$ = $;

var DrawerView = Backbone.View.extend({
    el: '#menu',

    initialize: function(options) {
        this.listenTo(DrawerEvents, 'pane:change', this.setActivePane);
        this.listenTo(DrawerEvents, 'pane:init', this.setActivePane);

        this.$label = $('.toc-type');
        this.$children = $('.toc-container');

        this.childViews = {};
        this.childViews['table-of-contents'] = new TOCView();
        this.childViews['timeline'] = new HistoryView();
        this.childViews['search'] = new SearchView();
        this.childViews['drawer-tabs'] = new DrawerTabs({forceOpen: options.forceOpen});

        var $tocSecondary = $('#table-of-contents-secondary');
        if ($tocSecondary.length) {
          this.childViews['table-of-contents-secondary'] = new TOCView({el: $tocSecondary});
        }

        this.setActivePane('table-of-contents');
    },

    // page types are more diverse and are named differently for
    // semantic reasons, so we need to associate page types
    // with the drawer panes they should be associated with
    pageTypeMap: {
        'diff': 'timeline',
        'reg-section': 'table-of-contents',
        'error': 'table-of-contents',
        'search-results': 'search',
    },

    // activeId = page type or child view type
    setActivePane: function(activeId) {
        if (typeof this.childViews[activeId] === 'undefined') {
            activeId = this.pageTypeMap[activeId];
        }

        // hide the content of all drawer sections
        this.$children.addClass('hidden');

        // remove the 'hidden' class from the active drawer section
        this.childViews[activeId].$el.removeClass('hidden');
    },

});

module.exports = DrawerView;
