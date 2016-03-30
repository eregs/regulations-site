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

    CommentEvents.on('writeSectionComment', this.writeComment, this);
  },

  readProposal: function() {
    this.$readTab.addClass('active-mode');
    this.$writeTab.removeClass('active-mode');

    CommentEvents.trigger('readProposal');
  },

  writeComment: function() {
    this.$writeTab.addClass('active-mode');
    this.$readTab.removeClass('active-mode');
  }

});

module.exports = PreambleHeadView;
