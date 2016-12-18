

var $ = require('jquery');
var _ = require('underscore');
var Backbone = require('backbone');
var Router = require('../../router');
var BreakawayEvents = require('../../events/breakaway-events');
var GAEvents = require('../../events/ga-events');

Backbone.$ = $;

var SxSListView = Backbone.View.extend({
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

    var $sxsLink = $(e.target);
    var id = $sxsLink.data('sxs-paragraph-id');
    var docNumber = $sxsLink.data('doc-number');
    var version = $('section[data-base-version]').data('base-version');

    BreakawayEvents.trigger('sxs:open', {
      regParagraph: id,
      docNumber: docNumber,
      fromVersion: version,
    });

    GAEvents.trigger('sxs:open', {
      id: id,
      docNumber: docNumber,
      regVersion: version,
      type: 'sxs',
    });
  },

  render: function render(html) {
    var $html = $(html);
    var list = $html.find('#sxs-list').html();
    this.$el.html(list);
  },
});

module.exports = SxSListView;
