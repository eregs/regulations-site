'use strict';

var $ = require('jquery');
var _ = require('underscore');
var Backbone = require('backbone');
Backbone.$ = $;

var MainEvents = require('../../events/main-events');
var DrawerEvents = require('../../events/drawer-events');
var CommentEvents = require('../../events/comment-events');
var comments = require('../../collections/comment-collection');

function getOptions(elm) {
  var $elm = $(elm).closest('.comment-index-item');
  return {
    section: $elm.data('comment-section'),
    tocId: $elm.data('comment-toc-section'),
    label: $elm.data('comment-label'),
  };
}

module.exports = Backbone.CommentIndexView = Backbone.View.extend({
  events: {
    'click .comment-index-edit': 'editComment',
    'click .comment-index-clear': 'clearComment',
  },

  initialize: function initialize(options) {
    this.docId = options.docId;
    this.template = _.template($('#comment-index-template').html());
    this.$index = this.$el.find('.comment-index-items');
    this.$commentIndexReview = this.$el.find('.comment-index-review');

    this.listenTo(comments, 'add remove', this.render);

    this.render();
  },

  render: function render() {
    var commentData = comments.toJSON({docId: this.docId});

    var html = this.template({comments: commentData});
    this.$index.html(html);

    if (commentData.length) {
      this.$commentIndexReview.show();
    } else {
      this.$commentIndexReview.hide();
    }
  },

  editComment: function editComment(e) {
    var options = _.extend({mode: 'write'}, getOptions(e.target));
    var type = options.section.split('-')[1];
    DrawerEvents.trigger('section:open', options.tocId);
    DrawerEvents.trigger('pane:change', type === 'preamble' ? 'table-of-contents' : 'table-of-contents-secondary');
    MainEvents.trigger('section:open', options.section, options, 'preamble-section');
    CommentEvents.trigger('comment:writeTabOpen');
  },

  clearComment: function clearComment(e) {
    var options = getOptions(e.target);
    var comment = comments.get(options.section);
    if (comment) {
      comment.destroy();
    }
  },
});
