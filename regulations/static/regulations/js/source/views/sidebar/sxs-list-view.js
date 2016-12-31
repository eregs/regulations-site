

const $ = require('jquery');
const _ = require('underscore');
const Backbone = require('backbone');
const Router = require('../../router');
const BreakawayEvents = require('../../events/breakaway-events');
const GAEvents = require('../../events/ga-events');

Backbone.$ = $;

const SxSListView = Backbone.View.extend({
  el: '#sxs-list',

  events: {
    'click .sxs-link': 'openSxS',
  },

  initialize: function initialize() {
    this.render = _.bind(this.render, this);

        // if the browser doesn't support pushState, don't
        // trigger click events for links
    if (Router.hasPushState === false) {
      this.events = {};
    }
  },

  openSxS: function openSxS(e) {
    e.preventDefault();

    const $sxsLink = $(e.target);
    const id = $sxsLink.data('sxs-paragraph-id');
    const docNumber = $sxsLink.data('doc-number');
    const version = $('section[data-base-version]').data('base-version');

    BreakawayEvents.trigger('sxs:open', {
      regParagraph: id,
      docNumber,
      fromVersion: version,
    });

    GAEvents.trigger('sxs:open', {
      id,
      docNumber,
      regVersion: version,
      type: 'sxs',
    });
  },

  render: function render(html) {
    const $html = $(html);
    const list = $html.find('#sxs-list').html();
    this.$el.html(list);
  },
});

module.exports = SxSListView;
