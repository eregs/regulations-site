'use strict';

var $ = require('jquery');
var _ = require('underscore');
var Backbone = require('backbone');
Backbone.$ = $;

var CommentView = Backbone.View.extend({
  events: {
    'click .toggle': 'toggle',
    'submit form': 'submit'
  },

  initialize: function() {
    this.$content = this.$el.find('.comment');
    this.$toggle = this.$el.find('.toggle');
    this.$comment = this.$el.find('textarea');
    this.section = this.$el.data('section');

    this.$content.hide();

    this.key = 'comment:' + this.section;

    this.load();
  },

  render: function() {},

  toggle: function() {

    this.$content.fadeToggle();

    if (this.$content.is(':visible')) {
      $('html, body').animate({
        scrollTop: this.$comment.offset().top
      }, 2000);
    }

  },

  submit: function(e) {
    e.preventDefault();
    window.localStorage.setItem(
      this.key,
      JSON.stringify({
        comment: this.$comment.val()
      })
    );
  },

  load: function() {
    var payload = JSON.parse(window.localStorage.getItem(this.key) || '{}');
    if (payload.comment) {
      this.$comment.val(payload.comment);
    }
  }
});

module.exports = CommentView;
