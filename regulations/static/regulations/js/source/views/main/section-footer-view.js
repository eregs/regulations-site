'use strict';
var $ = require('jquery');
var _ = require('underscore');
var Backbone = require('backbone');
var Router = require('../../router');
var MainEvents = require('../../events/main-events');

Backbone.$ = $;

var SectionFooterView = Backbone.View.extend({
  events: {
    'click .navigation-link': 'sendNavEvent',
  },

  initialize: function initialize() {
        // if the browser doesn't support pushState, don't
        // trigger click events for links
    if (Router.hasPushState === false || $('#table-of-contents').hasClass('diff-toc')) {
      this.events = {};
    }
  },

  sendNavEvent: function sendNavEvent(e) {
    var $target = $(e.currentTarget);
    var sectionId = $target.data('linked-section');
    var pageType = $target.data('page-type') || 'reg-section';

    if (sectionId) {
      e.preventDefault();
      MainEvents.trigger('section:open', sectionId, {}, pageType);
    }
  },

  remove: function render() {
    this.stopListening();
    return this;
  },
});

module.exports = SectionFooterView;
