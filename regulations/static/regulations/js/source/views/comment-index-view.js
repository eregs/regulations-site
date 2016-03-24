'use strict';

var $ = require('jquery');
var _ = require('underscore');
var Backbone = require('backbone');
Backbone.$ = $;

var CommentEvents = require('../events/comment-events');
var MainEvents = require('../events/main-events');
var DrawerEvents = require('../events/drawer-events');

function getSection(elm) {
  return $(elm)
    .closest('.comment-index-item')
    .data('comment-section');
}

module.exports = Backbone.CommentIndexView = Backbone.View.extend({
  events: {
    'click .comment-index-edit': 'editComment',
    'click .comment-index-clear': 'clearComment'
  },

  initialize: function(options) {
    this.docNumber = this.$el.data('doc-number');
    this.prefix = 'comment:' + this.docNumber;
    this.template = _.template($('#comment-index-template').html());
    this.$index = this.$el.find('.comment-index-items');

    this.render();
  },

  render: function() {
    var html = this.template({comments: this.parseComments()});
    this.$index.html(html);
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
    var section = getSection(e.target);
    var options = {mode: 'write', section: section};
    DrawerEvents.trigger('section:open', section);
    MainEvents.trigger('section:open', section, options, 'preamble-section');
  },

  clearComment: function(e) {
    var section = getSection(e.target);
    // TODO(jmcarp) Push storage ops to model
    window.localStorage.removeItem('comment:' + section);
    CommentEvents.trigger('comment:update', section);
    this.render();
  }
});
