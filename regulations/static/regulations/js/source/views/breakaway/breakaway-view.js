'use strict';
var $ = require('jquery');
var _ = require('underscore');
var Backbone = require('backbone');
var SxS = require('./sxs-view');
var Router = require('../../router');
var BreakawayEvents = require('../../events/breakaway-events');
var MainEvents = require('../../events/main-events');
var SidebarEvents = require('../../events/sidebar-events');

Backbone.$ = $;

var BreakawayView = Backbone.View.extend({
  childViews: {},

  initialize: function initialize() {
    this.listenTo(BreakawayEvents, 'sxs:open', this.openSxS);
  },

  openSxS: function openSxS(context) {
    context.url = context.regParagraph + '/' + context.docNumber + '?from_version=' + context.fromVersion;

    this.childViews.sxs = new SxS(context);

    if (Router.hasPushState) {
      Router.navigate('sxs/' + context.url);
    }

    MainEvents.trigger('breakaway:open', _.bind(this.removeChild, this));
    SidebarEvents.trigger('breakaway:open');
  },

  removeChild: function removeChild() {
    this.childViews.sxs.remove();
    delete(this.childViews.sxs);
  },
});

var breakaway = new BreakawayView();
module.exports = breakaway;
