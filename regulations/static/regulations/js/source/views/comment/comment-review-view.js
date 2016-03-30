'use strict';

var $ = require('jquery');
var _ = require('underscore');
var Backbone = require('backbone');
Backbone.$ = $;

var CommentView = require('./comment-view');
var comments = require('../../collections/comment-collection');

var CommentReviewView = Backbone.View.extend({
  events: {
    'click .preview-button': 'preview',
    'click .submit-button': 'submit',
    'click .back-to-comment' : 'back'
  },

  initialize: function(options) {
    Backbone.View.prototype.setElement.call(this, '#' + options.id);

    this.$content = this.$el.find('#comment');
    this.$previewContent = this.$el.find('.preview-content');
    this.$previewButton = this.$el.find('.preview-button');
    this.$submitButton = this.$el.find('.submit-button');
    this.$status = this.$el.find('.status');

    this.docId = this.$el.data('doc-id');
    this.template = _.template($('#comment-template').html());

    this.listenTo(comments, 'destroy', this.clearComment);
    this.listenTo(comments, 'destroy', this.previewMode);
    this.listenTo(comments, 'update', this.previewMode);

    this.render();
    this.previewMode();
  },

  previewMode: function() {
    this.$previewButton.show();
    this.$previewContent.hide();
    this.$submitButton.hide();
  },

  submitMode: function() {
    this.$previewButton.hide();
    this.$previewContent.show();
    this.$submitButton.show();
  },

  render: function() {
    var models = comments.toJSON({docId: this.docId});
    this.commentViews = models.map(function(comment) {
      var $elm = $(this.template({
        // TODO(jmcarp) Handle non-preamble sources
        url: ['', 'preamble'].concat(comment.id.split('-')).join('/'),
        section: comment.id,
        title: comment.label
      }));
      $elm.appendTo(this.$content);
      return new CommentView({
        el: $elm,
        section: comment.id,
        label: comment.label
      });
    }.bind(this));

    this.checkForComments();
  },

  clearComment: function(section) {
    var index = _.findIndex(this.commentViews, function(comment) {
      return comment.model.id === section.id;
    });

    if (index !== -1) {
      var target = this.commentViews.splice(index, 1);
      target[0].remove();
      target[0].$el.remove();
      this.checkForComments();
    }
  },

  checkForComments: function() {
    if (!this.commentViews.length) {
      $('#comment').html('<p>There are no comments to review or submit.</p>');
      $('#comment-confirm').remove();
    }
  },

  serialize: function() {
    return {
      sections: comments.toJSON({docId: this.docId})
    };
  },

  preview: function() {
    var prefix = window.APP_PREFIX || '/';
    var $xhr = $.ajax({
      type: 'POST',
      url: prefix + 'comments/preview',
      data: JSON.stringify(this.serialize()),
      contentType: 'application/json'
    });
    $xhr.then(this.previewSuccess.bind(this));
  },

  previewSuccess: function(resp) {
    this.$previewContent.text(resp);
    this.submitMode();
  },

  back: function() {
    window.history.back();
  },

  submit: function() {
    var prefix = window.APP_PREFIX || '/';
    var $xhr = $.ajax({
      type: 'POST',
      url: prefix + 'comments/comment',
      data: JSON.stringify(this.serialize()),
      contentType: 'application/json',
      dataType: 'json'
    });
    $xhr.done(this.submitSuccess.bind(this));
    $xhr.fail(this.submitError.bind(this));
  },

  submitSuccess: function(resp) {
    this.$status.text('Comment processing').fadeIn();
    this.poll(resp.metadata_url);
  },

  submitError: function() {
    // TODO(jmcarp) Figure out desired behavior
  },

  poll: function(url) {
    this.interval = window.setInterval(
      function() {
        $.getJSON(url).then(function(resp) {
          window.clearInterval(this.interval);
          this.setTrackingNumber(resp.trackingNumber);
        }.bind(this));
      }.bind(this),
      5000
    );
  },

  setTrackingNumber: function(number) {
    this.$status.html(
      '<div>Comment submitted</div>' +
      '<div>Tracking number: ' +
        '<a href="http://www.regulations.gov/#!searchResults;rpp=25;po=0;s=' + number + '">' + number + '</a>' +
      '</div>'
    );
  }
});

module.exports = CommentReviewView;
