'use strict';

var $ = require('jquery');
var _ = require('underscore');
var Backbone = require('backbone');
Backbone.$ = $;

var CommentView = require('./comment-view');
var CommentEvents = require('../../events/comment-events');

var CommentReviewView = Backbone.View.extend({
  events: {
    'click .preview-button': 'preview',
    'click .submit-button': 'submit'
  },

  initialize: function(options) {
    Backbone.View.prototype.setElement.call(this, '#' + options.id);

    this.$content = this.$el.find('#comment');
    this.$previewContent = this.$el.find('.preview-content');
    this.$previewButton = this.$el.find('.preview-button');
    this.$submitButton = this.$el.find('.submit-button');
    this.$status = this.$el.find('.status');

    this.template = _.template($('#comment-template').html());
    this.docNumber = this.$el.data('doc-number');
    this.prefix = 'comment:' + this.docNumber;

    this.listenTo(CommentEvents, 'comment:clear', this.clearComment);
    this.listenTo(CommentEvents, 'comment:clear', this.previewMode);
    this.listenTo(CommentEvents, 'comment:save', this.previewMode);

    this.showComments();
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

  render: function() {},

  showComments: function() {
    this.comments = _.chain(_.keys(window.localStorage))
      .filter(function(key) {
        return key.indexOf(this.prefix) === 0;
      }.bind(this))
      .map(function(key) {
        var payload = JSON.parse(window.localStorage.getItem(key));
        var section = key.replace('comment:', '');
        var $elm = $(this.template({
          // TODO(jmcarp) Handle non-preamble sources
          url: ['', 'preamble'].concat(section.split('-')).join('/'),
          section: section,
          title: section
        }));
        $elm.appendTo(this.$content);
        return new CommentView({
          el: $elm,
          section: section
        });
      }.bind(this))
      .value();

    this.checkForComments();
  },

  clearComment: function(section) {
    var index = _.findIndex(this.comments, function(comment) {
      return comment.section === section;
    });

    if (index !== -1) {
      var target = this.comments.splice(index, 1);
      target[0].remove();
      this.checkForComments();
    }
  },

  checkForComments: function() {
    if (!this.comments.length) {
      $('#comment').html('<p>There are no comments to review or submit.</p>');
      $('#comment-confirm').remove();
    }
  },

  serialize: function() {
    return {
      // TODO(jmcarp) Pass regs.gov document ID
      // doc_number: this.docNumber,
      sections: _.chain(_.keys(window.localStorage))
        .filter(function(key) {
          return key.indexOf(this.prefix) === 0;
        }.bind(this))
        .map(function(key) {
          return JSON.parse(window.localStorage.getItem(key));
        })
        .value()
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
    this.$status.text('Comment submitted').fadeIn();
  },

  submitError: function() {
    // TODO(jmcarp) Figure out desired behavior
  }
});

module.exports = CommentReviewView;
