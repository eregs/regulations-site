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
    this.$content = this.$el.find('.content');
    this.$comment = this.$el.find('textarea');
    this.section = this.$el.data('section');
    this.key = 'comment:' + this.section;

    this.load();
    this.toggle();
  },

  render: function() {},

  toggle: function() {
    if (this.$content.is(':visible')) {
      this.$content.hide();
    } else {
      this.$content.show();
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
