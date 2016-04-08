/**
 * preamble-head-view.js
 *
 * This view specifically handles Preamble actions in the
 * Sub View Header, notably click actions of the read/write tabs.
 *
 */

'use strict';

var $ = require('jquery');
var _ = require('underscore');
var Backbone = require('backbone');
Backbone.$ = $;

var CommentEvents = require('../../events/comment-events');

var PreambleHeadView = Backbone.View.extend({
  el: '.preamble-header',

  events: {
    'click .read-proposal': 'readProposal',
    'click .write-comment': 'writeComment'
  },

  initialize: function() {

    this.$readTab = this.$el.find('.read-proposal');
    this.$writeTab = this.$el.find('.write-comment');

    this.listenTo(CommentEvents, 'comment:readTabOpen', this.readTabOpen);
    this.listenTo(CommentEvents, 'comment:writeTabOpen', this.writeTabOpen);
  },

  readTabOpen: function () {
    this.$readTab.addClass('active-mode');
    this.$writeTab.removeClass('active-mode');
  },

  readProposal: function() {
    // yeah... need a better way to manage this. - xtine
    if ($('#preamble-write').is(':visible') || $('#comment-review').length) {
      this.readTabOpen();

      CommentEvents.trigger('read:proposal');
    }
  },

  writeTabOpen: function() {
    this.$writeTab.addClass('active-mode');
    this.$readTab.removeClass('active-mode');
  },

  writeComment: function() {
    if ($('#preamble-read').is(':visible')) {
      this.writeTabOpen();

      CommentEvents.trigger('comment:write');
    }
  }
});

module.exports = PreambleHeadView;
