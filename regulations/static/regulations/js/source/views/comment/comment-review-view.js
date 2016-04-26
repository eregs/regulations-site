'use strict';

var $ = require('jquery');
var URI = require('urijs');
var _ = require('underscore');
var Backbone = require('backbone');
Backbone.$ = $;

var MainEvents = require('../../events/main-events');
var PreambleHeadView = require('../header/preamble-head-view');
var CommentEvents = require('../../events/comment-events');
var comments = require('../../collections/comment-collection');

var CommentReviewView = Backbone.View.extend({
  events: {
    'click .edit-comment': 'editComment',
    'click .preview-button': 'preview',
    'change .agree': 'toggleSubmit'
  },

  initialize: function(options) {
    Backbone.View.prototype.setElement.call(this, '#' + options.id);

    this.$content = this.$el.find('.comment-review-items');

    this.docId = this.$el.data('doc-id');
    this.template = _.template($('#comment-template').html());

    this.previewLoading = false;

    this.listenTo(CommentEvents, 'read:proposal', this.handleRead);

    this.render();
  },

  findElms: function() {
    this.$form = this.$el.find('form');
  },

  handleRead: function() {
    var section = this.docId + '-preamble-' + this.docId + '-I';
    var options = {id: section, section: section, mode: 'read'};

    $('#content-body').removeClass('comment-review-wrapper');

    MainEvents.trigger('section:open', section, options, 'preamble-section');
  },

  editComment: function(e) {
    var section = $(e.target).closest('li').data('section');
    var options = {id: section, section: section, mode: 'write'};

    $('#content-body').removeClass('comment-review-wrapper');

    MainEvents.trigger('section:open', section, options, 'preamble-section');
    CommentEvents.trigger('comment:writeTabOpen');
  },

  render: function() {
    var commentData = comments.toJSON({docId: this.docId});
    var html = this.template({
      comments: commentData,
      previewLoading: this.previewLoading
    });

    this.$content.html(html);
    this.findElms();

    this.$form.find('[name="comments"]').val(JSON.stringify(commentData));

    this.preambleHeadView = new PreambleHeadView();
    CommentEvents.trigger('comment:writeTabOpen');
  },

  preview: function() {
    var $xhr = $.ajax({
      type: 'POST',
      url: window.APP_PREFIX + 'comments/preview',
      data: JSON.stringify({
        assembled_comment: comments.toJSON({docId: this.docId})
      }),
      contentType: 'application/json',
      dataType: 'json'
    });
    $xhr.then(this.previewSuccess.bind(this));
    this.previewLoading = true;
    this.render();
  },

  previewSuccess: function(resp) {
    window.location = resp.url;
    this.previewLoading = false;
    this.render();
  },

  toggleSubmit: function() {
    $('.submit-button').prop('disabled', function(i, v) { return !v; });
  }
});

module.exports = CommentReviewView;
