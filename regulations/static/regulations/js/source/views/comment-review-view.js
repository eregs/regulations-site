'use strict';

var $ = require('jquery');
var _ = require('underscore');
var Backbone = require('backbone');
Backbone.$ = $;

var CommentView = require('./comment-view');

var CommentReviewView = Backbone.View.extend({
  events: {
  },

  initialize: function(options) {
    Backbone.View.prototype.setElement.call(this, '#' + options.id);
    this.template = $('#comment-template').html();
    this.$content = this.$el.find('#comment');

    this.showComments();
  },

  showComments: function() {
    this.comments = _.chain(_.keys(window.localStorage))
      .filter(function(key) {
        return key.indexOf('comment:') === 0;
      })
      .map(function(key) {
        var section = key.replace('comment:', '');
        var $elm = $(_.template(this.template)({section: section}));
        $elm.appendTo(this.$content);
        return new CommentView({el: $elm});
      }.bind(this))
      .value();
  },

  render: function() {}
});

module.exports = CommentReviewView;
