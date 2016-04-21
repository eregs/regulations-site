'use strict';
var _ = require('underscore');
var Backbone = require('backbone');
var MainView = require('./views/main/main-view');
var MainEvents = require('./events/main-events');
var BreakawayEvents = require('./events/breakaway-events');
require('backbone-query-parameters');

var RegsRouter;

if (typeof window.history.pushState === 'undefined') {
    RegsRouter = function() {
        this.start = function() {};
        this.navigate = function() {};
        this.hasPushState = false;
    };
}
else {
    RegsRouter = Backbone.Router.extend({
        routes: {
            'sxs/:section/:version': 'loadSxS',
            'search/:docType/:reg': 'loadSearchResults',
            'diff/:section/:baseVersion/:newerVersion': 'loadDiffSection',
            ':section/:version': 'loadSection',
            ':section': 'loadSection',
            'preamble/:docId': 'loadPreamble',
            'preamble/:docId/:section': 'loadPreamble'
        },

        loadSection: function(section) {
            var options = {id: section};

            // to scroll to paragraph if there is a hadh
            options.scrollToId = Backbone.history.getHash();

            // ask the view not to route, its not needed
            options.noRoute = true;

            MainEvents.trigger('section:open', section, options, 'reg-section');
        },

        loadPreamble: function(docId, section) {
            var parts = [docId];
            if (section) {
              parts.concat(section);
            }

            var options = {
              id: parts.join('-'),
              scrollToId: Backbone.history.getHash(),
              noRoute: true
            };

            MainEvents.trigger('section:open', section, options, 'preamble-section');
        },

        loadDiffSection: function(section, baseVersion, newerVersion, params) {
            var options = {};

            options.id = section;
            options.baseVersion = baseVersion;
            options.newerVersion = newerVersion;
            options.noRoute = true;
            options.fromVersion = params.from_version;

            MainEvents.trigger('diff:open', section, options, 'diff');
        },

        loadSxS: function(section, version, params) {
            BreakawayEvents.trigger('sxs:open', {
                regParagraph: section,
                docNumber: version,
                fromVersion: params.from_version
            });
        },

        loadSearchResults: function(docType, reg, params) {
            var config = {
                query: params.q,
                regVersion: params.regVersion,
                docType: docType
            };

            // if there is a page number for the query string
            if (typeof params.page !== 'undefined') {
                config.page = params.page;
            }

            MainEvents.trigger('search-results:open', null, config, 'search-results');
        },

        start: function() {
            var root = window.APP_PREFIX || '';

            Backbone.history.start({
                pushState: 'pushState' in window.history,
                silent: true,
                root: root
            });
        },

        hasPushState: true
    });
}

var router = new RegsRouter();
module.exports = router;
