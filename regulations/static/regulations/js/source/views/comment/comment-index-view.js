'use strict';

var $ = require('jquery');
var _ = require('underscore');
var Backbone = require('backbone');
Backbone.$ = $;

var MainEvents = require('../../events/main-events');
var DrawerEvents = require('../../events/drawer-events');
var CommentEvents = require('../../events/comment-events');
var comments = require('../../collections/comment-collection');

function getSection(elm) {
  return $(elm)
    .closest('[data-comment-section]')
    .data('comment-section');
}

module.exports = Backbone.CommentIndexView = Backbone.View.extend({
  events: {
    'click .comment-index-edit': 'editComment',
    'click .comment-index-clear': 'clearComment'
  },

  initialize: function(options) {
    this.template = _.template($('#comment-index-template').html());
    this.$index = this.$el.find('.comment-index-items');
    this.$commentIndexReview = this.$el.find('.comment-index-review');

    this.listenTo(comments, 'add remove', this.render);

    this.render();
  },

  render: function() {
    var commentData = comments.toJSON();
    var html = this.template({comments: commentData});
    this.$index.html(html);

    if (commentData.length) {
      this.$commentIndexReview.show();
    } else {
      this.$commentIndexReview.hide();
    }
  },

  editComment: function(e) {
    var section = getSection(e.target);
    var options = {mode: 'write', section: section};
    DrawerEvents.trigger('section:open', section);
    MainEvents.trigger('section:open', section, options, 'preamble-section');
  },

  clearComment: function(e) {
    var section = getSection(e.target);
    var comment = comments.get(section);
    if (comment) {
      comment.destroy();
    }
  }
});
