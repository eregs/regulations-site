'use strict';

var $ = require('jquery');
var _ = require('underscore');
var Backbone = require('backbone');
Backbone.$ = $;

var CommentEvents = require('../events/comment-events');
var MainEvents = require('../events/main-events');
var DrawerEvents = require('../events/drawer-events');

module.exports = Backbone.CommentTocView = Backbone.View.extend({
  events: {
    'click .comment-toc-edit': 'editComment',
    'click .comment-toc-clear': 'clearComment'
  },

  initialize: function(options) {
    this.docNumber = this.$el.data('doc-number');
    this.prefix = 'comment:' + this.docNumber;
    this.template = _.template($('#comment-toc-template').html());

    this.render();
  },

  render: function() {
    var html = this.template({comments: this.parseComments()});
    this.$el.html(html);
  },

  parseComments: function() {
    return _.chain(_.keys(window.localStorage))
      .filter(function(key) {
        return key.indexOf(this.prefix) === 0;
      }.bind(this))
      .map(function(key) {
        var payload = JSON.parse(window.localStorage.getItem(key));
        var section = key.replace('comment:', '');
        payload.section = section;
        return payload;
      }.bind(this))
      .value();
  },

  editComment: function(e) {
    var section = $(e.target)
      .closest('.comment-toc-item')
      .data('comment-section');
    var options = {mode: 'write', section: section};
    DrawerEvents.trigger('section:open', section);
    MainEvents.trigger('section:open', section, options, 'preamble-section');
  },

  clearComment: function(e) {
    var section = $(e.target)
      .closest('.comment-toc-item')
      .data('comment-section');
    // TODO(jmcarp) Push storage ops to model
    window.localStorage.removeItem('comment:' + section);
    CommentEvents.trigger('comment:update', section);
    this.render();
  }
});
