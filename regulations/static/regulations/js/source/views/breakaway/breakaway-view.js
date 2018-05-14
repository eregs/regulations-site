

const $ = require('jquery');
const _ = require('underscore');
const Backbone = require('backbone');
const SxS = require('./sxs-view');
const Router = require('../../router');
const BreakawayEvents = require('../../events/breakaway-events');
const MainEvents = require('../../events/main-events');
const SidebarEvents = require('../../events/sidebar-events');

Backbone.$ = $;

const BreakawayView = Backbone.View.extend({
  childViews: {},

  initialize: function initialize() {
    this.listenTo(BreakawayEvents, 'sxs:open', this.openSxS);
  },

  openSxS: function openSxS(initialContext) {
    const context = $.extend({}, initialContext);
    context.url = `${context.regParagraph}/${context.docNumber}?from_version=${context.fromVersion}`;

    this.childViews.sxs = new SxS(context);

    if (Router.hasPushState) {
      Router.navigate(`sxs/${context.url}`);
    }

    MainEvents.trigger('breakaway:open', _.bind(this.removeChild, this));
    SidebarEvents.trigger('breakaway:open');
  },

  removeChild: function removeChild() {
    this.childViews.sxs.remove();
    delete (this.childViews.sxs);
  },
});

const breakaway = new BreakawayView();
module.exports = breakaway;
