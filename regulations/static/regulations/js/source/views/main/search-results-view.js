'use strict';
var $ = require('jquery');
var URI = require('urijs');
var _ = require('underscore');
var Backbone = require('backbone');
var SearchModel = require('../../models/search-model.js');
var Router = require('../../router');
var HeaderEvents = require('../../events/header-events');
var MainEvents = require('../../events/main-events');
var DrawerEvents = require('../../events/drawer-events');
var ChildView = require('./child-view');
Backbone.$ = $;

var SearchResultsView = ChildView.extend({
    events: {
        'click .search-nav a': 'paginate',
        'click h3 .internal': 'openResult'
    },

    initialize: function(options) {
        this.options = options;
        this.query = this.options.query;
        // the TOC may link to a different reg version than this.options.resultsRegVersion
        // because the user can select a different version to pull search results from
        this.resultsRegVersion = this.options.regVersion;
        this.page = parseInt(this.options.page, 10) || 0;
        this.title = 'Search of ' + this.options.docId + ' for ' + this.query + ' | eRegulations';

        // if the browser doesn't support pushState, don't
        // trigger click events for links
        if (Router.hasPushState === false) {
            this.events = {};
        }

        DrawerEvents.trigger('pane:change', 'search');

        // if the site wasn't loaded on the search results page
        if (this.options.render) {
            this.url = 'search/' + this.model.assembleSearchURL(this.options);
            ChildView.prototype.initialize.apply(this, arguments);
        } else {
            this.options.docType = this.$el.data('doc-type');
        }
    },

    setElement: function() {
        Backbone.View.prototype.setElement.call(this, '#content-wrapper.search-results');
    },

    render: function() {
        var $results = this.$el.find('#result-count');

        // if the results were ajaxed in, update header
        if ($results.text().length > 0) {
            HeaderEvents.trigger('search-results:open', $results.text());
            $results.remove();
        }

        if (Router.hasPushState) {
            if (typeof this.options.id !== 'undefined') {
                Router.navigate(this.url);
            }
        }
    },

    paginate: function(e) {
        e.preventDefault();

        var options = {
          query: this.options.query,
          docType: this.options.docType,
          regVersion: this.options.regVersion,
          page: this.page + ($(e.target).hasClass('previous') ? -1 : 1)
        };

        MainEvents.trigger('search-results:open', null, options, 'search-results');
    },

    openResult: function(e) {
        // TOC version retains the version the reg was loaded on whereas the content base section
        // changes to match the search results
        // page should reload if the TOC version doesn't match the searched version
        if (!this.resultsRegVersion || this.resultsRegVersion === $('nav#toc').attr('data-toc-version')) {
            e.preventDefault();
            var $resultLink = $(e.target);
            var pageType = this.options.docType === 'cfr' ? 'reg-section' : 'preamble-section';
            var options = {
              regVersion: $resultLink.data('linked-version'),
              scrollToId: $resultLink.data('linked-subsection')
            };

            DrawerEvents.trigger('pane:change', 'table-of-contents');
            MainEvents.trigger('section:open', $resultLink.data('linked-section'), options, pageType);
        }
    }
});

module.exports = SearchResultsView;
