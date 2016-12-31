

const $ = require('jquery');
const Backbone = require('backbone');
const Router = require('../../router');
const SxSModel = require('../../models/sxs-model');
const BreakawayEvents = require('../../events/breakaway-events');

Backbone.$ = $;

const SxSView = Backbone.View.extend({
  el: '#breakaway-view',

  events: {
    'click .sxs-back-button': 'remove',
    'click .footnote-jump-link': 'footnoteHighlight',
    'click .return-link': 'removeHighlight',
  },

  initialize: function initialize(options) {
    this.options = options;

      // visibly open the SxS panel immediately
    this.$el.addClass('open-sxs');

      // give it a state of `progress` until content loads
    this.changeState('inprogress');

    SxSModel.get(this.options.url, {}).then((resp) => {
      this.$el.html(resp);
    }).fail(() => {
      this.$el.html('<div class="error"><span class="cf-icon cf-icon-error icon-warning"></span>Due to a network error, we were unable to retrieve the requested information.</div>');
    }).always(() => {
      this.changeState('completed');
    });

    this.listenTo(BreakawayEvents, 'sxs:close', this.remove);

      // if the browser doesn't support pushState, don't
      // trigger click events for links
    if (Router.hasPushState === false) {
      this.events = {};
    }
  },

  changeState: function changeState(state) {
        // if a previous state exists remove the class before updating
    this.$el.removeClass(this.loadingState);
    this.loadingState = state;
    this.$el.addClass(state);
  },

  footnoteHighlight: function footnoteHighlight(e) {
    const target = $(e.target).attr('href');
        // remove existing highlight
    this.removeHighlight();
        // highlight the selected footnote
    $(`.footnotes ${target}`).toggleClass('highlight');
  },

  removeHighlight: function removeHighlight() {
    $('.footnotes li').removeClass('highlight');
  },

  remove: function remove(e) {
    if (typeof e !== 'undefined') {
      e.preventDefault();
      window.history.back();
    }

    this.$el.removeClass('open-sxs');
    this.$el.html('');
    this.stopListening();
    this.$el.off();
    return this;
  },
});

module.exports = SxSView;
