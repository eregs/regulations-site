'use strict';

var Backbone = require('backbone');
var MainEvents = require('./events/main-events');
var BreakawayEvents = require('./events/breakaway-events');
require('backbone-query-parameters');

var RegsRouter;

if (typeof window.history.pushState === 'undefined') {
  RegsRouter = function router() {
    this.start = function start() {};
    this.navigate = function navigate() {};
    this.hasPushState = false;
  };
} else {
  RegsRouter = Backbone.Router.extend({
    routes: {
      'sxs/:section/:version': 'loadSxS',
      'search/:docType/:reg': 'loadSearchResults',
      'diff/:section/:baseVersion/:newerVersion': 'loadDiffSection',
      ':section/:version': 'loadSection',
      ':section': 'loadSection',
      'preamble/:docId/:section': 'loadPreamble',
      'preamble/:docId/cfr_changes/:section': 'loadCfrChanges',
    },

    loadSection: function loadSection(section) {
      this.openSection(section, 'reg-section');
    },

    loadPreamble: function loadPreamble(docId, section) {
      var parts = [docId, 'preamble', docId, section];
      this.openSection(parts.join('-'), 'preamble-section');
    },

    loadCfrChanges: function loadCfrChanges(docId, section) {
      var parts = [docId, 'cfr', section];
      this.openSection(parts.join('-'), 'preamble-section');
    },

    openSection: function openSection(id, type) {
      var options = {
        id: id,
        scrollToId: Backbone.history.getHash(),
        noRoute: true,
      };
      MainEvents.trigger('section:open', id, options, type);
    },

    loadDiffSection: function loadDiffSection(section, baseVersion, newerVersion, params) {
      var options = {};

      options.id = section;
      options.baseVersion = baseVersion;
      options.newerVersion = newerVersion;
      options.noRoute = true;
      options.fromVersion = params.from_version;

      MainEvents.trigger('diff:open', section, options, 'diff');
    },

    loadSxS: function loadSxS(section, version, params) {
      BreakawayEvents.trigger('sxs:open', {
        regParagraph: section,
        docNumber: version,
        fromVersion: params.from_version,
      });
    },

    loadSearchResults: function loadSearchResults(docType, reg, params) {
      var config = {
        query: params.q,
        regVersion: params.regVersion,
        docType: docType,
      };

            // if there is a page number for the query string
      if (typeof params.page !== 'undefined') {
        config.page = params.page;
      }

      MainEvents.trigger('search-results:open', null, config, 'search-results');
    },

    start: function start() {
      var root = window.APP_PREFIX || '';

      Backbone.history.start({
        pushState: 'pushState' in window.history,
        silent: true,
        root: root,
      });
    },

    hasPushState: true,
  });
}

var router = new RegsRouter();
module.exports = router;
