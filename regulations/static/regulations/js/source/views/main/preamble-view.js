'use strict';

var $ = require('jquery');
var _ = require('underscore');
var Backbone = require('backbone');
Backbone.$ = $;

var ChildView = require('./child-view');
var CommentView = require('../comment/comment-view');
var CommentIndexView = require('../comment/comment-index-view');
var CommentEvents = require('../../events/comment-events');

var PreambleView = ChildView.extend({
  el: '#content-wrapper',

  events: {
    'click .activate-write': 'handleWrite',
    'click .activate-read': 'handleRead'
  },

  initialize: function(options) {
    this.options = options;
    this.id = options.id;
    this.url = 'preamble/' + this.id.split('-').join('/');
    if (!options.render) {
      this.render();
    }
    ChildView.prototype.initialize.apply(this, arguments);
  },

  handleRead: function() {
    this.$write.hide();
    this.$read.show();
  },

  handleWrite: function(e) {
    var $target = $(e.target);
    this.write(
      $target.data('section'),
      $target.closest('[data-permalink-section]')
    );
  },

  write: function(section, $parent) {
    $parent = $parent.clone();
    $parent.find('.activate-write').remove();
    CommentEvents.trigger('comment:target', {
      section: section,
      $parent: $parent
    });
    this.$read.hide();
    this.$write.show();
  },

  render: function() {
    ChildView.prototype.render.apply(this, arguments);
    this.$read = this.$el.find('#preamble-read');
    this.$write = this.$el.find('#preamble-write');
    var section = this.$read.closest('section').attr('id');
    var docId = section.split('-')[0];
    this.commentView = new CommentView({
      el: this.$write.find('.comment-wrapper'),
      section: section
    });
    this.commentIndex = new CommentIndexView({
      el: this.$write.find('.comment-index'),
      docId: docId
    });

    if (this.options.mode === 'write') {
      var $parent = $('#' + this.options.section).find('[data-permalink-section]');
      this.write(this.options.section, $parent);
    } else {
      this.handleRead();
    }
  },

  remove: function() {
    this.commentView.remove();
    this.commentIndex.remove();
    Backbone.View.prototype.remove.call(this);
  }
});

module.exports = PreambleView;
