

const $ = require('jquery');
const Backbone = require('backbone');
const Router = require('../../router');
const MainEvents = require('../../events/main-events');

Backbone.$ = $;

const SectionFooterView = Backbone.View.extend({
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
    const $target = $(e.currentTarget);
    const sectionId = $target.data('linked-section');
    const pageType = $target.data('page-type') || 'reg-section';

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
