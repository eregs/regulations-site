'use strict';

var $ = require('jquery');
var _ = require('underscore');
var Backbone = require('backbone');
Backbone.$ = $;

var ChildView = require('./main/child-view');
var CommentView = require('./comment-view');
var CommentEvents = require('../events/comment-events');

var PreambleView = ChildView.extend({
  el: '#content-wrapper',

  events: {
    'click .activate-write': 'write',
    'click .activate-read': 'read'
  },

  initialize: function() {
    ChildView.prototype.initialize.apply(this, arguments);
    this.$read = this.$el.find('#preamble-read');
    this.$write = this.$el.find('#preamble-write');
    this.commentView = new CommentView({el: this.$write.find('.comment-wrapper').get(0)});
    this.$write.hide();
  },

  read: function() {
    this.$write.hide();
    this.$read.show();
  },

  write: function(e) {
    var $target = $(e.target);
    var $parent = $target.closest('[data-permalink-section]').clone();
    $parent.find('.activate-write').remove();
    CommentEvents.trigger('comment:target', {
      section: $target.data('section'),
      $parent: $parent
    });
    this.$read.hide();
    this.$write.show();
  },

  render: function() {}
});

module.exports = PreambleView;
